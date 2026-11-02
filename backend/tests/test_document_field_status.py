import io
import json
import pytest

from app.models.calibration import AuditLog, CalibrationEvent
from app.models.document import ExtractedField
from tests.test_analytics_snapshots import setup
from tests.test_document_materialization import certificate
from app.api import documents
from reportlab.pdfgen import canvas


def states(client, doc):
    return {f['field_name']: f['validation_status'] for f in client.get(f'/api/v1/documents/{doc.id}/fields').json()['fields']}


def add_field(db, doc, name, value):
    field=ExtractedField(document_id=doc.id,field_name=name,raw_value=value,normalized_value=value,validation_status='STAGING')
    db.add(field);db.flush();return field


def test_revalidation_marks_only_actual_documentary_checks(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    response=client.post(f'/api/v1/documents/{doc.id}/revalidate')
    assert response.status_code==200
    assert states(client,doc)=={'serial_number':'VALIDATED','calibration_date':'VALIDATED','next_due_date':'VALIDATED',
                               'error_value':'NOT_EVALUATED','tolerance':'NOT_EVALUATED'}
    assert db.query(CalibrationEvent).filter(CalibrationEvent.instrument_unit_id==instrument.id).count()==0
    audit=db.query(AuditLog).filter(AuditLog.action=='DOCUMENT_REVALIDATED',AuditLog.entity_id==doc.id).one()
    assert all(f['validation_status']=='STAGING' for f in audit.details['before']['field_validation'])
    assert len(audit.details['after']['field_validation'])==5


def test_failed_unit_and_range_do_not_invalidate_independent_fields(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    add_field(db,doc,'unit','°C');add_field(db,doc,'operating_range','10-0 bar')
    response=client.post(f'/api/v1/documents/{doc.id}/revalidate').json()
    assert response['processing_status']=='REVIEW_REQUIRED'
    result=states(client,doc)
    assert result['unit']==result['operating_range']=='REVIEW_REQUIRED'
    assert result['serial_number']==result['calibration_date']=='VALIDATED'


def test_unit_compatibility_and_range_checks_are_recorded_when_applicable(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    add_field(db,doc,'unit','kPa');add_field(db,doc,'operating_range','0-10 kPa')
    assert client.post(f'/api/v1/documents/{doc.id}/revalidate').status_code==200
    result=states(client,doc)
    assert result['unit']==result['operating_range']=='VALIDATED'


def test_unit_is_not_checked_without_matching_instrument(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    serial=db.query(ExtractedField).filter(ExtractedField.document_id==doc.id,ExtractedField.field_name=='serial_number').one()
    serial.normalized_value='UNKNOWN-FIELD-STATUS';add_field(db,doc,'unit','bar');db.flush()
    assert client.post(f'/api/v1/documents/{doc.id}/revalidate').status_code==200
    result=states(client,doc)
    assert result['serial_number']=='REVIEW_REQUIRED' and result['unit']=='NOT_EVALUATED'
    assert result['calibration_date']=='VALIDATED'


def test_correction_invalidates_all_dependent_checks_preserving_raw(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    client.post(f'/api/v1/documents/{doc.id}/revalidate')
    field=db.query(ExtractedField).filter(ExtractedField.document_id==doc.id,ExtractedField.field_name=='error_value').one()
    raw=field.raw_value
    response=client.patch(f'/api/v1/documents/{doc.id}/fields/{field.id}',json={'normalized_value':'0.03'})
    assert response.status_code==200 and response.json()['field_validation']
    result=states(client,doc)
    assert result['serial_number']==result['calibration_date']==result['next_due_date']=='STAGING'
    assert result['error_value']=='NOT_EVALUATED'
    assert field.raw_value==raw
    assert client.post(f'/api/v1/documents/{doc.id}/accept').status_code==400


def test_serial_candidates_are_read_only_evidence_not_validated_values(setup):
    client,db,instrument=setup;doc=certificate(db,instrument)
    evidence=add_field(db,doc,'serial_candidates',json.dumps([instrument.serial_number,'ANOTHER-SERIAL']))
    assert client.post(f'/api/v1/documents/{doc.id}/revalidate').json()['processing_status']=='ACCEPTED'
    assert states(client,doc)['serial_candidates']=='EVIDENCE'
    assert client.patch(f'/api/v1/documents/{doc.id}/fields/{evidence.id}',json={'normalized_value':'[]'}).status_code==400


@pytest.mark.parametrize("legacy_status", ["STAGING", "ACCEPTED"])
def test_legacy_accepted_document_is_not_relabelled_by_reading(setup, legacy_status):
    client,db,instrument=setup;doc=certificate(db,instrument)
    for field in db.query(ExtractedField).filter(ExtractedField.document_id==doc.id).all(): field.validation_status=legacy_status
    db.flush()
    assert set(states(client,doc).values())=={legacy_status}
    assert doc.processing_status=='ACCEPTED'


def test_real_pdf_processing_persists_checks_and_keeps_full_text_hidden(setup,tmp_path,monkeypatch):
    client,db,instrument=setup
    monkeypatch.setattr(documents,'STORAGE_RAW_DIR',str(tmp_path))
    stream=io.BytesIO();pdf=canvas.Canvas(stream,invariant=1)
    for i,line in enumerate([f'Serial: {instrument.serial_number}','Calibration Date: 2026-01-01','Due Date: 2027-01-01','Max Error: 0.02','Tolerance: 0.1']):pdf.drawString(40,780-i*22,line)
    pdf.save()
    upload=client.post('/api/v1/documents/upload',files={'file':('field-status.pdf',stream.getvalue(),'application/pdf')})
    assert upload.status_code==201;did=upload.json()['document_id']
    process=client.post(f'/api/v1/documents/{did}/process?extractor=deterministic')
    assert process.status_code==200
    response=client.get(f'/api/v1/documents/{did}/fields').json()
    result={f['field_name']:f['validation_status'] for f in response['fields']}
    assert result['serial_number']=='VALIDATED' and result['error_value']=='NOT_EVALUATED'
    assert '__full_text__' not in result
    hidden=db.query(ExtractedField).filter(ExtractedField.document_id==did,ExtractedField.field_name=='__full_text__').one()
    assert hidden.validation_status=='EVIDENCE'
    assert db.query(AuditLog).filter(AuditLog.action=='DOCUMENT_PROCESSED',AuditLog.entity_id==did).count()==1
