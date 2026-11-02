from copy import deepcopy
from datetime import date
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as N
from unittest.mock import patch
import zipfile
import xml.etree.ElementTree as ET

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'experiments'),str(ROOT/'backend')]
import aasx_v2 as bridge
from app.services import aas_builder


def snapshot():
    calls=[]
    def put(url,json,**kwargs):
        calls.append((url,deepcopy(json)))
        return N(status_code=201)
    inst=N(serial_number='EXP06-UNIT',manufacturer='Café',model='M1',lifecycle_state='operational',
           criticality='HIGH',location='Lab',installed_at=date(2024,1,1))
    event=N(id=1,calibration_date=date(2025,1,1),next_due_date=date(2026,1,1),error_value=-.0125,tolerance=.1,result='pass',created_at=None)
    doc=N(id=1,original_filename='synthetic.pdf',source_type='PDF_CERTIFICATE',sha256_hash='ab'*32,processing_status='ACCEPTED',uploaded_at=None)
    with patch.object(aas_builder.requests,'put',side_effect=put):
        assert aas_builder.AASBuilder.sync_shell_and_nameplate(inst,N(magnitude='Pressure'))
        assert aas_builder.AASBuilder.sync_operational_state(inst)
        assert aas_builder.AASBuilder.sync_calibration_submodel(inst,[event])
        assert aas_builder.AASBuilder.sync_document_provenance(inst,[doc])
    shell=calls[0][1];subs=[payload for _,payload in calls[1:]]
    shell['asset'].update(bridge.ref(bridge.identifier(shell['asset']),'Asset'))
    shell['submodels']=[bridge.ref(bridge.identifier(sm),'Submodel') for sm in subs]
    return {'shell':shell,'submodels':subs}


def test_real_aasx_opc_and_sdk_roundtrip_preserve_all_declared_entries(tmp_path):
    environment=bridge.normalize_source(snapshot())
    expected=bridge.critical_snapshot(environment)
    path=tmp_path/'passport.aasx'
    assert bridge.export_package(environment,path)['result']=='PASS'
    with zipfile.ZipFile(path) as package:
        assert '[Content_Types].xml' in package.namelist()
        relationships=ET.fromstring(package.read('_rels/.rels'))
        assert any(element.attrib['Type'].endswith('/aasx-origin') for element in relationships)
        assert any(name.endswith('.aas.json') for name in package.namelist())
    restored=bridge.read_package(path)
    result=bridge.compare(expected,bridge.critical_snapshot(restored))
    assert result['result']=='PASS' and result['preserved_fraction']==1
    with pytest.raises(FileExistsError):bridge.export_package(environment,path)


def test_missing_or_changed_critical_property_cannot_pass():
    environment=bridge.normalize_source(snapshot())
    expected=bridge.critical_snapshot(environment)
    mutated=deepcopy(environment)
    nameplate=next(sm for sm in mutated['submodels'] if sm['idShort']=='Nameplate')
    nameplate['submodelElements'].pop()
    result=bridge.compare(expected,bridge.critical_snapshot(mutated))
    assert result['result']=='FAIL' and result['missing']
    changed=deepcopy(expected);key=next(k for k in changed if k.endswith('/Sha256/value'))
    changed[key]='cd'*32
    assert bridge.compare(expected,changed)['changed']==[key]


def test_numeric_lexical_equivalence_preserves_value_but_not_nearby_numbers():
    environment=bridge.normalize_source(snapshot());expected=bridge.critical_snapshot(environment)
    calibration=next(sm for sm in environment['submodels'] if sm['idShort']=='CalibrationHistory')
    value=next(element for element in calibration['submodelElements'][0]['value'] if element['idShort']=='ErrorValue')
    value['value']='-0.0125000'
    assert bridge.compare(expected,bridge.critical_snapshot(environment))['result']=='PASS'
    value['value']='-0.0125000000000001'
    assert bridge.compare(expected,bridge.critical_snapshot(environment))['result']=='FAIL'


@pytest.mark.parametrize('mutation',['missing_submodel','dangling_reference','duplicate_reference'])
def test_invalid_reference_graph_is_rejected(mutation):
    source=snapshot()
    if mutation=='missing_submodel':source['submodels'].pop()
    elif mutation=='dangling_reference':source['shell']['submodels'][0]['keys'][-1]['value']='missing'
    else:source['shell']['submodels'].append(deepcopy(source['shell']['submodels'][0]))
    with pytest.raises(bridge.RoundtripError):bridge.normalize_source(source)


def test_unknown_element_type_is_not_silently_dropped():
    environment=bridge.normalize_source(snapshot())
    environment['submodels'][0]['submodelElements'][0]['modelType']['name']='UnknownType'
    with pytest.raises(bridge.RoundtripError):bridge.critical_snapshot(environment)


def test_json_zip_is_not_accepted_as_aasx(tmp_path):
    path=tmp_path/'fake.aasx'
    with zipfile.ZipFile(path,'w') as package:package.writestr('passport.json','{}')
    with pytest.raises((KeyError,ValueError,IndexError)):bridge.read_package(path)


def test_nonempty_repository_is_rejected_without_writes():
    class Session:
        def get(self,*args,**kwargs):return N(raise_for_status=lambda:None,json=lambda:[{'existing':'aas'}])
        def put(self,*args,**kwargs):raise AssertionError('No writes before emptiness guard')
    with pytest.raises(bridge.RoundtripError):bridge.require_empty(Session(),'http://test/aasServer')


def test_empty_submodels_roundtrip(tmp_path):
    environment=normalize_source(snapshot())
    for sm in environment['submodels']:
        if sm['idShort'] in ('CalibrationHistory','DocumentProvenance'):
            sm['submodelElements']=[]
    expected=critical_snapshot(environment)
    path=tmp_path/'empty.aasx'
    assert export_package(environment,path)['result']=='PASS'
    assert compare(expected,critical_snapshot(read_package(path)))['result']=='PASS'
