"""Read the exact RAW bytes for a document without exposing filesystem paths."""
import hashlib
import hmac
from pathlib import Path
import re
from urllib.parse import quote

from fastapi import HTTPException, Response


def original_response(document, raw_directory, download=False):
    unavailable = 'El archivo original no está disponible. Revisa su conservación en el almacenamiento RAW.'
    try:
        root = Path(raw_directory).resolve(strict=True)
        path = Path(document.file_path).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise HTTPException(404, unavailable)
        # Hash and serve the same bytes, rather than reopening after verification.
        contents = path.read_bytes()
    except (OSError, RuntimeError, TypeError, ValueError):
        raise HTTPException(404, unavailable) from None

    digest = hashlib.sha256(contents).hexdigest()
    expected = str(document.sha256_hash or '').lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or not hmac.compare_digest(digest, expected):
        raise HTTPException(409, 'El original no coincide con su hash registrado. No se ha servido el archivo; revisa su integridad.')

    filename = str(document.original_filename or f'documento-{document.id}').replace('\\', '/').rsplit('/', 1)[-1]
    filename = ''.join(char for char in filename if char >= ' ' and char != '\x7f') or f'documento-{document.id}'
    is_pdf = contents.startswith(b'%PDF-')
    disposition = 'attachment' if download or not is_pdf else 'inline'
    return Response(contents, media_type='application/pdf' if is_pdf else 'application/octet-stream', headers={
        'Content-Disposition': f"{disposition}; filename*=UTF-8''{quote(filename, safe='')}",
        'X-Content-SHA256': digest,
        'ETag': f'"{digest}"',
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
    })
