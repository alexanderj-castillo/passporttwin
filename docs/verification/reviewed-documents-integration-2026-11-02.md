# Propagación de PR revisadas a main · 02/11/2026

Pau comunica «aceptados». Se comprueban metadatos GitHub, refs y presencia de código, sin asumir que toda PR fusionada está en main.

| PR | Fusión observada | Presencia en main `0f4f3ac` antes de esta entrega |
| --- | --- | --- |
| #28 | main, `81ed08e` | Plan/deuda presentes |
| #29 | main, `9f34501` | Original documental presente |
| #30 | feature/document-original, `6b72797` | Materialización ausente |
| #31 | feature/document-materialization, `9ad3f20` | Estados por campo ausentes |
| #32 | main, `0f4f3ac` | Corrección de etiqueta presente |

La fusión de #30 ocurrió en una rama que ya se había trasladado a main; #31 se fusionó en la rama de #30. Sus estados `merged=true` no propagaron esos nuevos commits automáticamente a main. Se comprobó ausencia de servicios/tests y acciones UI de incorporación/estados en el árbol de main.

## Candidato

Rama `test/integrate-reviewed-documents` desde main `0f4f3ac27ed04577078318eb1ffef3d6d4111605`, merge local no conflictivo de `origin/feature/document-materialization` `9ad3f200b901744fe77fa4e7e747d71003fe6081`, commit funcional candidato `0b17361a8b18473f40580736af839da2d8d8bf93`. Se conserva el historial revisado; no se modifica main ni se reabre/modifica una PR anterior.

No hay diferencias en `backend/`, `frontend/` y `bi/` frente a la composición ya comprobada `2f6615e464588789451131c63b1750c2116df549`. Esta entrega solo traslada funcionalidad previamente revisada y actualiza seguimiento de deuda/backlog.

## Comprobaciones nuevas

- **324 backend/BI correctos**, Docker/Python 3.11/PostgreSQL 17 desechable; `python -m pytest tests /repo/bi/tests -q -p no:cacheprovider --tb=short` con fuentes del candidato montadas en lectura.
- **Build frontend correcto**, Node 20/Vite 5.4.21; fuentes del candidato con dependencias de imagen existente, no instalación limpia.
- `git diff --exit-code 2f6615e HEAD -- backend frontend bi` sin diferencias funcionales antes de añadir documentación de seguimiento.
- `git diff --check` y enlaces de documentación comprobados.

Los avisos previos de Requests/Starlette persisten. No se repite navegador ni estudio humano: no hay cambios funcionales respecto a la composición previa; sus informes conservan commits/fechas originales. No se declara ejecutado el conjunto final EXP-01…07 ni se valida académicamente el producto por esta integración.

## Estado y continuación

TD-01/04 integrados en main; TD-02/03 incluidos en candidato probado, **pendientes de fusionar esta PR hacia main**. Actualizar su estado solo cuando ese merge se observe. Notion no modificado. Después de integrar, confirmar presencia/ancestría y avanzar en navegación/diseño visual sobre la base completa; no repetir suites ya verdes sin cambios o incidencias que lo justifiquen.
