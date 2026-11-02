"""EXP-06: project projection -> fresh BaSyx -> real AASX -> SDK -> fresh BaSyx."""
import argparse
from datetime import date,datetime,timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from types import SimpleNamespace as N
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from aasx_v2 import (RoundtripError,validate_base,fetch,normalize_source,critical_snapshot,
                     compare,export_package,read_package,require_empty,import_environment)
FIXTURE=ROOT/'experiments/fixtures/exp06-aasx.json'


class ComparisonFailure(RoundtripError):
    def __init__(self, message, report):
        super().__init__(message)
        self.report = report


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(commit=None):
    if commit is not None and not re.fullmatch('[0-9a-fA-F]{40}',commit):raise RoundtripError('Full code commit required')
    try:
        found=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
        dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],text=True,stderr=subprocess.DEVNULL).strip())
    except (OSError,subprocess.CalledProcessError):
        if not commit:raise RoundtripError('Git unavailable: supply --code-commit from host') from None
        return {'commit':commit,'working_tree_dirty':None,'source':'caller_supplied_not_verified'}
    if commit and commit!=found:raise RoundtripError('Commit differs from checkout')
    return {'commit':found,'working_tree_dirty':dirty,'source':'git_checkout'}


def project_fixture(session,base,fixture):
    sys.path.insert(0,str(ROOT/'backend'))
    from app.services import aas_builder
    # Route the real builder's writes to the explicitly provided empty test source.
    # No mocked HTTP response: session.put talks to actual BaSyx.
    with patch.object(aas_builder,'BASYX_AAS_URL',base),patch.object(aas_builder.requests,'put',session.put):
        for item in fixture['instruments']:
            instrument=N(**{k:v for k,v in item.items() if k not in ('calibrations','documents','magnitude')})
            instrument.installed_at=date.fromisoformat(item['installed_at']) if item['installed_at'] else None
            calibrations=[N(**{**event,'calibration_date':date.fromisoformat(event['calibration_date']),
                               'next_due_date':date.fromisoformat(event['next_due_date']),
                               'created_at':datetime.fromisoformat(event['created_at'])}) for event in item['calibrations']]
            docs=[N(**{**document,'uploaded_at':datetime.fromisoformat(document['uploaded_at'])}) for document in item['documents']]
            results=[aas_builder.AASBuilder.sync_shell_and_nameplate(instrument,N(magnitude=item['magnitude'])),
                     aas_builder.AASBuilder.sync_calibration_submodel(instrument,calibrations),
                     aas_builder.AASBuilder.sync_document_provenance(instrument,docs),
                     aas_builder.AASBuilder.sync_operational_state(instrument)]
            if not all(results):raise RoundtripError('Project AAS projection failed')


def run(source,target,directory,commit=None):
    import requests
    source,target=validate_base(source),validate_base(target)
    if source==target:raise RoundtripError('Source and target must be distinct empty repositories')
    fixture=json.loads(FIXTURE.read_text())
    if fixture['version']!='exp06_aas2_preparation_v1':raise RoundtripError('Unsupported fixture')
    serials=[item['serial_number'].replace('-','_') for item in fixture['instruments']]
    if len(serials)!=len(set(serials)):raise RoundtripError('Colliding AAS identities in fixture')
    for item in fixture['instruments']:
        for document in item['documents']:
            if not re.fullmatch('[a-f0-9]{64}',document['sha256_hash']):raise RoundtripError('Invalid synthetic document hash')
    report={'experiment':'EXP-06','scope':'Controlled synthetic technical round-trip, not final validation',
            'criterion':'100% of declared critical entries preserved at every checked boundary',
            'git':identity(commit),'python':platform.python_version(),
            'fixture_sha256':sha(FIXTURE),'source_url':source,'target_url':target,
            'sdk_packages':{name:version(name) for name in ('basyx-python-sdk','pyecma376-2','lxml','requests')},
            'normalization':'BaSyx embedded asset -> separate AAS v2 asset; compound submodel references -> global references to same identifiers; REST parent removed',
            'cases':[]}
    session=requests.Session();session.trust_env=False
    require_empty(session,source);require_empty(session,target)
    project_fixture(session,source,fixture)
    require_empty(session,target)  # Also rejects aliases of the source and concurrent population.
    for item in fixture['instruments']:
        aas_id='AAS_'+item['serial_number'].replace('-','_')
        original=fetch(session,source,aas_id)
        environment=normalize_source(original)
        expected=critical_snapshot(environment)
        package=directory/(aas_id+'.aasx')
        sdk_check=export_package(environment,package)
        restored=read_package(package)
        package_check=compare(expected,critical_snapshot(restored))
        if package_check['result']!='PASS':
            report['cases'].append({'aas_id':aas_id,'sdk_normalization':sdk_check,'aasx_read':package_check})
            raise ComparisonFailure('AASX read lost critical fields; target not written',report)
        import_environment(session,target,restored)
        received=normalize_source(fetch(session,target,aas_id))
        target_check=compare(expected,critical_snapshot(received))
        record={'aas_id':aas_id,'sdk_normalization':sdk_check,'aasx_read':package_check,'target_read':target_check,
                'source_critical_sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest(),
                'package_file':package.name,'package_sha256':sha(package),
                'calibration_events':len(item['calibrations']),'accepted_document_references':len(item['documents'])}
        report['cases'].append(record)
        if target_check['result']!='PASS':raise ComparisonFailure('Target repository changed critical data',report)
    report.update(execution_status='COMPLETE',roundtrip_result='PASS',calculated_at=datetime.now(timezone.utc).isoformat(),
                  source_sha256={name:sha(ROOT/name) for name in ('experiments/run_aasx_exp06.py','experiments/aasx_v2.py','backend/app/services/aas_builder.py','experiments/aasx/requirements.txt')})
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-url',required=True);parser.add_argument('--target-url',required=True)
    parser.add_argument('--run-dir',type=Path,required=True);parser.add_argument('--code-commit')
    args=parser.parse_args()
    try:args.run_dir.mkdir(parents=True,exist_ok=False)
    except FileExistsError:parser.error('Run directory exists; no artifacts or repositories are reset')
    try:report=run(args.source_url,args.target_url,args.run_dir,args.code_commit)
    except Exception as exc:
        report={**getattr(exc,'report',{}),'experiment':'EXP-06','execution_status':'FAILED','roundtrip_result':'NOT_PASSED',
                'error_type':type(exc).__name__,'error':str(exc) if isinstance(exc,RoundtripError) else 'Round-trip failed; inspect isolated servers/tool environment',
                'scope':'Failed technical run; partial artifacts retained, no success claimed'}
    with (args.run_dir/'report.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    print(f"{report['execution_status']}: {args.run_dir/'report.json'}")
    return 0 if report['execution_status']=='COMPLETE' else 2


if __name__=='__main__':raise SystemExit(main())
