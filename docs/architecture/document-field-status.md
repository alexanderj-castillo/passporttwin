# Estados comprobables por campo · TD-03 / UI-03

Entrega apilada sobre PR #30. Las reglas documentales y la materialización siguen siendo fases diferentes. Un documento ACCEPTED no demuestra que cada campo tenga una comprobación individual registrada ni que exista calibración canónica.

## Estados

| Estado persistido | Significado en esta fase |
| --- | --- |
| VALIDATED | Se aplicó y superó una regla documental sobre este campo; no certifica metrología ni exactitud industrial. |
| REVIEW_REQUIRED | Falló una regla que afecta al campo, o está vacío siendo obligatorio. |
| NOT_EVALUATED | No hay regla aplicable o faltan condiciones para comprobarlo. Incluye error/tolerancia en esta fase, campos desconocidos y unidad sin instrumento/unidad canónica resolubles. |
| EVIDENCE | Candidatas de serie o texto limpio: evidencia conservada, no un valor editable validado. Texto completo sigue oculto en la edición. |
| STAGING | Comprobación no vigente/registrada; exige validar antes de incorporar desde UI. |

Las etiquetas históricas ACCEPTED por campo se conservan en base, pero la UI las presenta como «Sin comprobación vigente registrada», igual que STAGING, sin inferir VALIDATED por el estado documental. Las filas antiguas no se migran ni repintan masivamente. Nuevos fixtures demo parten de STAGING; su creación no finge ejecutar reglas.

## Qué se comprueba

- Serie: matching y ambigüedad.
- Fecha de calibración: presencia, fecha futura y relación con vencimiento cuando aplica.
- Próximo vencimiento: solo con ambos valores disponibles; orden respecto a calibración.
- Unidad: compatibilidad dimensional solo si hay instrumento y unidad canónica. No se afirma conversión de unidades.
- Rango: coherencia de límites cuando está presente.

Una regla de unidad/rango fallida no marca fechas o serie como fallidas si sus propias comprobaciones se superaron. Tampoco se marcan error/tolerancia como comprobados porque se acepte el documento: R-TOL-01 ocurre al incorporar, con otro alcance. No se añaden reglas nuevas ni se corrige aquí el manejo existente de fechas mal formadas o valores numéricos no válidos.

## Persistencia y correcciones

`process` aplica estados a las filas extraídas después del resultado real del motor y registra DOCUMENT_PROCESSED con reglas/estados. `revalidate` persiste estados y amplía su evento existente con antes/después. Los estados auditados incluyen ID y nombre, para conservar significado si un reprocesado sustituye filas.

Guardar una corrección invalida todos los campos que pueden depender del documento, exige revalidación y conserva RAW. La respuesta PATCH añade `field_validation`; la UI actualiza esos estados sin sobreescribir borradores de otros campos. Un valor modificado localmente se identifica como «Cambio sin guardar» hasta guardar. EVIDENCE continúa de solo lectura y los campos sin regla siguen NOT_EVALUATED.

GET no revalida ni modifica históricos. La UI bloquea incorporar mientras haya STAGING/ACCEPTED histórico, aunque el documento esté ACCEPTED; después de una validación explícita puede habilitarlo si el contrato de incorporación también lo permite. El endpoint `/accept` conserva su compatibilidad anterior con estados documentales: esta entrega no impone una migración de estados por campo a todos los consumidores API.

## Evidencia y límites

[Resumen técnico](../verification/document-field-status-2026-11-02.json): 301 backend/BI correctos en Docker/Python 3.11/PostgreSQL 17 (nueve nuevos), build frontend Node 20 correcto. Tras añadir nombres a los estados auditados pasan otros 13 controles focales del contrato/correcciones; no se presenta como una segunda suite completa.

Siete controles de navegador con API/PostgreSQL/RAW reales sintéticos: histórico sin validación inferida, borradores conservados al guardar otro campo, checks reales frente a campos no evaluados, persistencia en recarga, invalidación y fecha futura en revisión, móvil 390 px y rehabilitación tras validar sin incorporar automáticamente. Los seis controles principales monitorizan y no detectan errores JS; el adicional comprueba elegibilidad.

No cambia el esquema ni dependencias ni corrige TD-04 (`Serial Number:`). No reinterpreta retroactivamente una calibración canónica o una auditoría antigua. La cobertura de reglas sigue siendo limitada y debe declararse en EXP-01/03 y defensa. No se realiza estudio humano ni validación académica final.
