# Sesión: 2026-11-02 · Pau/Codex · Abrir original TD-01

## Inicio

- Pau autoriza «hagámoslo»: apertura del PDF desde pasaporte/revisión, descarga por ID y comprobación hash/errores.
- Base `origin/main` comprobada con fetch: `823a4bb`; rama/worktree nuevo `feature/document-original`, limpio. Independiente de PR #28 (plan/deuda); no se integra su documentación como dependencia.
- Leídas instrucciones y último cierre. Coordinación: archivos de API/UI de documentos; sin mensajes externos a Alexander. Notion no modificado.

## Cierre — SESSION END STATUS

- Endpoint original por ID con contención RAW y hash de los mismos bytes servidos, cabeceras/nombre seguros, errores 404/409; lectura sin materialización ni cambios de estado.
- Nueva vista React con PDF nativo, descarga y hash, navegación contextual y errores; acciones separadas en ficha y enlace desde documento cargado. Sin cambios de esquema/dependencias.
- TESTED: 282 backend/BI pasan en Docker/Python 3.11/PostgreSQL 17, 12 nuevos; build Node 20/Vite correcto. Siete controles Chromium con servicios reales y RAW compartido; PDF renderizado inspeccionado y descarga comparada por SHA; móvil/errores sin JS errors.
- Permisos de fixtures sintéticos inicialmente impidieron controles negativos; ajustados solo para esos archivos y restaurados después, no política de producción. Avisos Requests/Starlette anteriores persisten.
- Contrato/evidencia en `docs/architecture/document-original.md` y JSON. No streaming/range ni nuevo modelo de autenticación; requiere RAW disponible dentro de raíz configurada. TD-02/03/04 siguen pendientes.
- `git diff --check` y enlaces locales correctos; preparado commit/push/PR, sin merge automático. TD-01 implementado/probado pero pendiente revisión/integración; se enlazará desde registro de PR #28 sin declararlo cerrado.
- Recursos aislados se retiran al finalizar; servicios habituales preservados. No experimento final ni estudio humano, tampoco edición de Notion.
- Siguiente paso: revisar/integrar; después transición validación→materialización y estados en UI.
