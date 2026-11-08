# Sesión: 2026-11-08 · Pau/Codex · Recuperación de proyección AAS al incorporar

- Rama: fix/recuperar-proyeccion-aas desde main 8ee67a2. Entorno Compose aislado ptwin-ensayo.
- Reproducción previa: instrumento sintético sin shell, incorporación con ERROR de proyección y una calibración canónica. El sync manual reconstruyó la proyección sin duplicar la calibración.
- Cambio: si falla la proyección dinámica y BaSyx confirma por HTTP 404 que el shell no existe, se reconstruyen shell y Nameplate y se repite la proyección dinámica una vez. La calibración ya está guardada antes de contactar con BaSyx.
- Pruebas: pytest tests/test_document_materialization.py -q en Docker, 11 correctas y dos avisos de dependencias. Sintaxis y git diff --check correctos.
- BaSyx real: PTWIN-DEMO-SANO pasó de shell 404 a SYNCED, con cuatro submodelos y la calibración 32 registrada una sola vez. Segundo intento de incorporación: 409.
- Caída real: con BaSyx detenido, PTWIN-DEMO-VENCIDO pasó de 8 a 9 calibraciones y registró AAS_SYNC_FAILED. Tras el arranque, POST /sync pasó de ERROR a SYNCED y reconstruyó los cuatro submodelos. El historial siguió en 9 y la calibración 33 aparece una vez.
- Pendientes: push, PR y revisión. Esta corrección cubre el caso de shell ausente y la recuperación manual tras caída. La persistencia de BaSyx y la política general de recuperación siguen siendo trabajo separado.
