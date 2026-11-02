"""Original retrieval exercises real HTTP/DB and exact on-disk RAW bytes."""
import hashlib
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.api import documents
from app.database.session import engine, get_db
from app.main import app
from app.models.document import Document


@pytest.fixture
def original(tmp_path, monkeypatch):
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode='create_savepoint')
    monkeypatch.setattr(documents, 'STORAGE_RAW_DIR', str(tmp_path))
    content = b'%PDF-1.4\nsynthetic original bytes\n%%EOF\n'
    path = tmp_path / 'stored.pdf'
    path.write_bytes(content)
    doc = Document(original_filename='Certificado presión.pdf', file_path=str(path),
                   sha256_hash=hashlib.sha256(content).hexdigest(), processing_status='REVIEW_REQUIRED')
    db.add(doc); db.flush()
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: db
    try:
        yield SimpleNamespace(client=TestClient(app), db=db, doc=doc, path=path, content=content, root=tmp_path)
    finally:
        app.dependency_overrides.clear(); app.dependency_overrides.update(previous)
        db.close(); transaction.rollback(); connection.close()


@pytest.mark.parametrize('status', ['RECEIVED', 'REVIEW_REQUIRED', 'ACCEPTED'])
def test_pdf_original_is_exact_and_available_independent_of_review_status(original, status):
    o = original
    o.doc.processing_status = status; o.db.flush()
    response = o.client.get(f'/api/v1/documents/{o.doc.id}/original', headers={'Origin': 'http://localhost:5173'})
    assert response.status_code == 200
    assert response.content == o.content
    assert response.headers['content-type'] == 'application/pdf'
    assert response.headers['content-disposition'].startswith('inline;')
    assert unquote(response.headers['content-disposition'].split("UTF-8''")[1]) == o.doc.original_filename
    assert response.headers['x-content-sha256'] == hashlib.sha256(response.content).hexdigest()
    assert 'Content-Disposition' in response.headers['access-control-expose-headers']
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert o.doc.processing_status == status  # Read does not accept/materialize.


def test_download_attachment_preserves_bytes(original):
    response = original.client.get(f'/api/v1/documents/{original.doc.id}/original?download=true')
    assert response.status_code == 200 and response.content == original.content
    assert response.headers['content-disposition'].startswith('attachment;')


def test_missing_document_or_file_gives_path_free_404(original):
    o = original
    assert o.client.get('/api/v1/documents/2147483647/original').status_code == 404
    o.path.unlink()
    response = o.client.get(f'/api/v1/documents/{o.doc.id}/original')
    assert response.status_code == 404
    assert str(o.root) not in response.text
    assert 'no está disponible' in response.json()['detail']


def test_tampered_file_is_never_returned(original):
    o = original
    o.path.write_bytes(b'tampered secret bytes')
    response = o.client.get(f'/api/v1/documents/{o.doc.id}/original')
    assert response.status_code == 409
    assert b'tampered secret bytes' not in response.content
    assert str(o.path) not in response.text


@pytest.mark.parametrize('symlink', [False, True])
def test_database_path_cannot_serve_outside_raw(original, tmp_path_factory, symlink):
    o = original
    outside = tmp_path_factory.mktemp('outside') / 'private.pdf'
    outside.write_bytes(o.content)
    if symlink:
        o.path.unlink(); o.path.symlink_to(outside)
    else:
        o.doc.file_path = str(outside); o.db.flush()
    response = o.client.get(f'/api/v1/documents/{o.doc.id}/original')
    assert response.status_code == 404
    assert o.content not in response.content and str(outside) not in response.text


def test_nested_demo_raw_path_is_supported(original):
    o = original
    nested = o.root / 'demo' / 'original.pdf'
    nested.parent.mkdir(); o.path.rename(nested)
    o.doc.file_path = str(nested); o.db.flush()
    assert o.client.get(f'/api/v1/documents/{o.doc.id}/original').content == o.content


def test_non_pdf_is_downloaded_and_filename_cannot_inject_headers(original):
    o = original
    content = b'<html><script>alert(1)</script></html>'
    o.path.write_bytes(content)
    o.doc.sha256_hash = hashlib.sha256(content).hexdigest()
    o.doc.original_filename = '..\\folder\\fake.pdf\r\nX-Injected: yes'
    o.db.flush()
    response = o.client.get(f'/api/v1/documents/{o.doc.id}/original')
    assert response.status_code == 200 and response.content == content
    assert response.headers['content-type'] == 'application/octet-stream'
    assert response.headers['content-disposition'].startswith('attachment;')
    assert 'x-injected' not in response.headers
    assert '\r' not in response.headers['content-disposition'] and '\n' not in response.headers['content-disposition']
    assert 'folder' not in response.headers['content-disposition']


@pytest.mark.parametrize('stored_hash', ['not-a-hash', 'é' * 64])
def test_malformed_recorded_hash_is_integrity_error_not_server_error(original, stored_hash):
    original.doc.sha256_hash = stored_hash; original.db.flush()
    response = original.client.get(f'/api/v1/documents/{original.doc.id}/original')
    assert response.status_code == 409
    assert original.content not in response.content
