# Etiqueta completa Serial Number · TD-04 / DOC-01

Un PDF digital con `Serial Number: PT-A` se interpretaba como serie `Number`. Si el catálogo contenía ese serial, podía vincularse al activo equivocado; sin él, se enviaba a revisión por matching fallido. El cambio consume la etiqueta completa antes del valor y evita que el patrón corto `Serial` vuelva a interpretar `Number` como identidad.

Se mantienen `Serial:`, `S/N:` y `Número de Serie`, con espacios/tabulaciones horizontales y mayúsculas/minúsculas en etiquetas. Se conserva el valor y su alfabeto anterior (letras ASCII, dígitos, guion y subrayado), sin normalizar la serie ni cambiar matching exacto. Un límite de palabra evita capturar `NotSerial:` como etiqueta.

Etiqueta y valor se reconocen en la misma línea. Los separadores ya no consumen saltos de línea: `Serial Number:` vacío seguido de `Calibration Date:` no crea una identidad `Number`/`Calibration`. Valores únicamente en la línea siguiente quedan sin extraer y requieren revisión; es una restricción deliberada para evitar consumir otra etiqueta. No se afirma soporte de cualquier formato, OCR ni documentos escaneados.

La deduplicación y política de ambigüedad no cambian: varias identidades distintas → serie sin elegir, candidatas conservadas, revisión obligatoria. La misma serie repetida con etiquetas distintas no crea una ambigüedad artificial. No se reprocesan documentos antiguos ni se mueven calibraciones materializadas.

## Evidencia del 02/11/2026

[Resumen](../verification/serial-label-2026-11-02.json). Antes de corregir: 14 fallos y cinco controles correctos en 19 casos focales. Después: 19/19 correctos. Cuatro PDFs digitales reales generados/subidos/procesados por la API con PostgreSQL real verifican serie única, repetida, ambigua y ausente, incluyendo un instrumento llamado `Number` en el catálogo para detectar vínculo equivocado.

Suite de esta rama independiente desde main: **293 backend/BI pasan**, Python 3.11/PostgreSQL 17 en Docker. Composición local de PR #29/#30/#31 más este cambio: **324 pasan** en `test/document-ui-and-label`, sin conflictos funcionales ni merge de main. Son suites con bases distintas, no recuentos que se deban sumar. Commits, árbol y hashes registrados en el JSON.

No se repite build/estudio de navegador porque no cambia frontend. Las pruebas API usan PDFs digitales sintéticos y datos controlados; son regresiones conocidas de desarrollo. Falta evaluación final independiente para generalizar extracción/matching. Se conservan datasets e informes experimentales anteriores; no se recalifican retrospectivamente.
