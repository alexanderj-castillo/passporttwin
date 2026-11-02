from datetime import datetime
import hashlib

import pytest
from app.models.document import Document
from tests.test_analytics_snapshots import setup


def record(db,name,instrument=None,status='RECEIVED'):
    doc=Document(original_filename=name,file_path='/internal/not-exposed.pdf',
        sha256_hash=hashlib.sha256(name.encode()).hexdigest(),processing_status=status,
        instrument_unit_id=instrument.id if instrument else None,uploaded_at=datetime(2026,1,1))
    db.add(doc);db.flush();return doc


def test_list_includes_unlinked_documents_without_raw_paths(setup):
    client,db,instrument=setup
    one=record(db,'LIST-only-unlinked.pdf',status='REVIEW_REQUIRED')
    two=record(db,'LIST-only-linked.pdf',instrument)
    result=client.get('/api/v1/documents?q=LIST-only-').json()
    assert {row['id'] for row in result['items']}=={one.id,two.id}
    rows={row['id']:row for row in result['items']}
    assert rows[one.id]['instrument_serial'] is None
    assert rows[two.id]['instrument_public_id']==str(instrument.public_id)
    assert all('file_path' not in row and 'storage_path' not in row for row in result['items'])


def test_search_matches_filename_serial_and_location_case_insensitively(setup):
    client,db,instrument=setup
    instrument.location='Unique Search Laboratory';db.flush()
    doc=record(db,'Search Certificado.pdf',instrument)
    for query in ('certificado',instrument.serial_number.lower(),'unique search laboratory'):
        assert any(row['id']==doc.id for row in client.get('/api/v1/documents',params={'q':query}).json()['items'])


def test_search_treats_like_wildcards_as_literals(setup):
    client,db,instrument=setup
    doc=record(db,'Literal%_Only.pdf')
    record(db,'LiteralXXOnly.pdf')
    rows=client.get('/api/v1/documents',params={'q':'%_Only'}).json()['items']
    assert [row['id'] for row in rows]==[doc.id]


def test_review_filter_and_stable_pagination(setup):
    client,db,instrument=setup
    docs=[record(db,f'PAGE-doc-{n}.pdf',status='REVIEW_REQUIRED' if n%2 else 'ACCEPTED') for n in range(4)]
    first=client.get('/api/v1/documents?q=PAGE-doc-&limit=2').json()
    second=client.get('/api/v1/documents?q=PAGE-doc-&limit=2&offset=2').json()
    assert first['has_more'] is True and second['has_more'] is False
    assert [row['id'] for row in first['items']+second['items']]==[d.id for d in reversed(docs)]
    review=client.get('/api/v1/documents?q=PAGE-doc-&review_only=true').json()['items']
    assert {row['id'] for row in review}=={d.id for d in docs if d.processing_status=='REVIEW_REQUIRED'}


@pytest.mark.parametrize('params',[{'limit':0},{'limit':101},{'offset':-1},{'q':'x'*201}])
def test_invalid_page_limits_are_rejected(setup,params):
    client,db,instrument=setup
    assert client.get('/api/v1/documents',params=params).status_code==422
