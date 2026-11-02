# Sesión: 2026-11-02 · Pau/Codex · TD-03 estados por campo

## Inicio

- «ok» de Pau tras proponer como siguiente bloque TD-03. Base comprobada main `823a4bb`; PR #29/#30 pendientes. Rama apilada `feature/document-field-status` desde #30 `fa5ebe0`, base PR `feature/document-materialization`.
- Leídas instrucciones y cierre anterior. Alcance estados verificables, invalidación de checks y presentación; no cambios de extractor ni reglas nuevas. Sin mensajes externos/Notion.

## Cierre — SESSION END STATUS

- Estados persistidos por reglas aplicadas, revisión específica, no evaluado, evidencia y staging invalidado; process/revalidate auditados. No se pinta todo verde por ACCEPTED.
- PATCH invalida checks dependientes y devuelve estados; UI conserva otros borradores y distingue sin guardar. Histórico ACCEPTED/STAGING no se revalida por lectura; incorporación UI requiere registrar checks. Nuevos fixtures demo no fingen validación por campo.
- TESTED: 301 backend/BI correctos en Docker/Python 3.11/PostgreSQL 17, nueve nuevos; build Node 20. Tras añadir nombres a estados auditados, 13 controles focales correctos. Siete controles navegador, seis con captura de errores JS sin detectar errores y séptimo de elegibilidad histórica. Móvil 390 px sin overflow.
- Se detectó durante preparación que seed_demo escribía ACCEPTED/REVIEW_REQUIRED en campos según documento, no STAGING; se ajustan nuevos fixtures y se conservan filas históricas como tales. No backfill ni alteración RAW.
- Contrato/alcance en `docs/architecture/document-field-status.md` y JSON. Sin dependencias/esquema. `git diff --check` y enlaces locales comprobados; avisos previos de dependencias persisten.
- Preparado commit/push/PR apilada; integrar #29 → #30 → esta rama, sin merge automático. TD-03 implementado/probado pendiente revisión/integración; actualizar registro PR #28 sin declarar cierre.
- Servicios desechables se retiran al finalizar, manteniendo habituales. No experimento final ni estudio humano. Siguiente bloque: TD-04, ampliar etiqueta Serial Number sin modificar política de ambigüedad.
