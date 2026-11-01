# Sesión: 2026-11-01 · Pau/Codex · Preparación EXP-01…07

## Inicio

- Pau autoriza comenzar matriz y revisión de EXP-03/04 para la tarjeta de los siete experimentos finales.
- Fetch confirma `origin/main` en `0d9d1b9`, PR #18 integrada. Rama aislada `docs/final-experiments-audit`, checkout limpio.
- Notion inaccesible en consulta previa (404); exportación vigente indicada por usuario y definiciones históricas del documento base TFM. No se modificó Notion ni se enviaron mensajes a Alexander.

## Cierre — SESSION END STATUS

- Matriz: `docs/experiments/final-experiments-matrix.md`. Inventario: `experiments/final/preparation-audit.json`.
- Revisados siete EXP, scripts y artefactos existentes. EXP-03: 20 certificados, 8 anomalías históricas; fechas FUTURE_DATE ya pasadas, omisión de errores y cobertura incompleta. EXP-04: CSV ausente del checkout, agregado con unidades mezcladas y necesidad de revisar corte temporal entre activos.
- Comprobaciones estáticas: manifiesto/20 PDFs/reportes coinciden en nombres y recuentos, 60 instrumentos/120 pronósticos históricos; SHA-256 de 29 archivos; diff y enlaces relativos. No se ejecutan experimentos ni tests de aplicación porque solo se entrega auditoría documental.
- Preparación implementada y comprobada; no protocolo/dataset final congelados ni validación final.
- Preparado para commit/push/PR de documentación; consultar la rama para revisión. No fusionar sin revisión del compañero.
- Siguiente paso: reconciliar criterios, preparar runner EXP-03 con reloj/control de fallos y EXP-04 con hash/métricas por familia-horizonte; después congelar y ejecutar en entorno aislado.
