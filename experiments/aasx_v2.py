"""Explicit BaSyx 1.4/AAS v2 <-> standard AASX bridge, tool-only SDK."""
from copy import deepcopy
from decimal import Decimal
import io
import json
from pathlib import Path
from urllib.parse import quote, urlsplit

NAMES = {'Nameplate','OperationalState','CalibrationHistory','DocumentProvenance'}


class RoundtripError(ValueError):
    pass


def validate_base(value):
    parsed=urlsplit(value)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise RoundtripError('Use an explicit HTTP(S) BaSyx base without credentials/query')
    return value.rstrip('/')


def identifier(item):
    value=item['identification']
    return value['idType'], value['id']


def ref(identifier_, type_):
    return {'keys':[{'type':type_,'local':True,'idType':identifier_[0],'value':identifier_[1]}]}


def last_reference(value, expected_type):
    keys=value['keys']
    if not keys or keys[-1]['type']!=expected_type:
        raise RoundtripError('Invalid reference target type')
    return keys[-1]['idType'],keys[-1]['value']


def fetch(session,base,aas_id):
    root=base+'/shells/'+quote(aas_id,safe='')+'/aas'
    shell=session.get(root,timeout=10);shell.raise_for_status()
    subs=session.get(root+'/submodels',timeout=10);subs.raise_for_status()
    return {'shell':shell.json(),'submodels':subs.json()}


def normalize_source(snapshot):
    shell=deepcopy(snapshot['shell']);subs=deepcopy(snapshot['submodels'])
    if not isinstance(subs,list) or {sm['idShort'] for sm in subs}!=NAMES or len(subs)!=4:
        raise RoundtripError('Exactly the four MVP submodels are required')
    asset={k:v for k,v in shell['asset'].items() if k!='keys'}
    asset['modelType']={'name':'Asset'}
    if last_reference(shell['asset'],'Asset')!=identifier(asset):
        raise RoundtripError('Embedded asset and reference disagree')
    expected={identifier(sm) for sm in subs}
    refs=[last_reference(value,'Submodel') for value in shell['submodels']]
    if set(refs)!=expected or len(refs)!=len(expected):
        raise RoundtripError('Submodel references are incomplete, duplicated or dangling')
    shell['asset']=ref(identifier(asset),'Asset')
    # BaSyx REST compound paths become globally resolvable AAS v2 references.
    shell['submodels']=[ref(value,'Submodel') for value in sorted(expected)]
    shell['modelType']={'name':'AssetAdministrationShell'}
    for sm in subs:
        sm.pop('parent',None)  # REST containment is not an extra canonical identity.
        sm['modelType']={'name':'Submodel'}
    return {'assetAdministrationShells':[shell],'assets':[asset],'submodels':subs,'conceptDescriptions':[]}


def critical_snapshot(environment):
    shells,assets,subs=environment['assetAdministrationShells'],environment['assets'],environment['submodels']
    if len(shells)!=1 or len(assets)!=1 or len(subs)!=4 or {sm['idShort'] for sm in subs}!=NAMES:
        raise RoundtripError('Unexpected object counts or submodel scope')
    shell,asset=shells[0],assets[0]
    asset_ref=last_reference(shell['asset'],'Asset')
    refs=[last_reference(value,'Submodel') for value in shell['submodels']]
    if asset_ref!=identifier(asset) or set(refs)!={identifier(sm) for sm in subs} or len(refs)!=4:
        raise RoundtripError('Unresolvable or duplicated identity references')
    result={'shell/id':list(identifier(shell)),'shell/idShort':shell['idShort'],
            'shell/assetReference':list(asset_ref),'shell/submodelReferences':sorted([list(value) for value in refs]),
            'asset/id':list(identifier(asset)),'asset/idShort':asset['idShort'],'asset/kind':asset['kind']}
    def elements(values,path):
        names=[value['idShort'] for value in values]
        if len(names)!=len(set(names)):raise RoundtripError('Duplicate idShort in element namespace')
        result[path+'/children']=sorted(names)
        for value in values:
            key=path+'/'+value['idShort'];kind=value['modelType']['name'];result[key+'/modelType']=kind
            if kind=='SubmodelElementCollection': elements(value['value'],key)
            elif kind=='Property':
                value_type=value['valueType'];result[key+'/valueType']=value_type
                if value_type=='double':
                    number=Decimal(str(value['value']))
                    if not number.is_finite():raise RoundtripError('Non-finite property')
                    result[key+'/value']=str(number.normalize())
                elif value_type=='string':result[key+'/value']=str(value['value'])
                else:raise RoundtripError('Unsupported property datatype; do not silently drop it')
            else:raise RoundtripError('Unsupported element model type')
    for sm in subs:
        path='submodels/'+sm['idShort']
        result[path+'/id']=list(identifier(sm))
        result[path+'/semanticId']=sm['semanticId']
        elements(sm['submodelElements'],path)
    return result


def compare(expected,actual):
    missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
    changed=sorted(key for key in expected.keys() & actual.keys() if expected[key]!=actual[key])
    preserved=sum(key in actual and expected[key]==actual[key] for key in expected)
    return {'result':'PASS' if not missing and not extra and not changed else 'FAIL',
            'expected_critical_entries':len(expected),'preserved':preserved,
            'preserved_fraction':preserved/len(expected) if expected else None,
            'missing':missing,'extra':extra,'changed':changed}


def export_package(environment,path):
    from basyx.aas.adapter import json as adapter,aasx
    from basyx.aas import model
    store=adapter.read_aas_json_file(io.StringIO(json.dumps(environment)),failsafe=False)
    # Validate normalization before writing, not only read-vs-write against itself.
    normalized=io.StringIO();adapter.write_aas_json_file(normalized,store)
    normalized=json.loads(normalized.getvalue())
    check=compare(critical_snapshot(environment),critical_snapshot(normalized))
    if check['result']!='PASS':raise RoundtripError('SDK JSON normalization lost critical fields')
    aas_identifier=next(obj.identification for obj in store if isinstance(obj,model.AssetAdministrationShell))
    with Path(path).open('xb') as stream:
        with aasx.AASXWriter(stream) as writer:
            writer.write_aas(aas_identifier,
                             store,aasx.DictSupplementaryFileContainer(),write_json=True)
    return check


def read_package(path):
    from basyx.aas.adapter import json as adapter,aasx
    from basyx.aas import model
    store=model.DictObjectStore()
    with aasx.AASXReader(path) as reader:reader.read_into(store,aasx.DictSupplementaryFileContainer())
    result=io.StringIO();adapter.write_aas_json_file(result,store)
    environment=json.loads(result.getvalue())
    critical_snapshot(environment)  # Reject a partially parsed/incomplete package.
    return environment


def require_empty(session,base):
    response=session.get(base+'/shells',timeout=10);response.raise_for_status()
    if response.json()!=[]:raise RoundtripError('Repository is not empty; no reset or overwrite is performed')


def import_environment(session,base,environment):
    critical_snapshot(environment)
    shell=deepcopy(environment['assetAdministrationShells'][0]);asset=deepcopy(environment['assets'][0])
    asset.pop('modelType',None);shell['asset']=asset;shell['submodels']=[]
    root=base+'/shells/'+quote(shell['identification']['id'],safe='')
    response=session.put(root,json=shell,timeout=10);response.raise_for_status()
    for sm in environment['submodels']:
        response=session.put(root+'/aas/submodels/'+quote(sm['idShort'],safe=''),json=sm,timeout=10)
        response.raise_for_status()
