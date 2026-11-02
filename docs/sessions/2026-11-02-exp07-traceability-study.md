# Sesión: 2026-11-02 · Pau/Codex · EXP-07

## Inicio

- Pau autoriza «hacemos 6 y 7 nosotros» mientras Alexander revisa; EXP-06 ya tiene PR #26. No se han enviado mensajes ni fusionado ramas.
- Fuente: exportación Notion confirmada por Pau y matriz de preparación PR #19. Notion directo no disponible; no actualizado.
- `origin/main` comprobado con fetch en `0d9d1b9`; worktree nuevo y limpio, rama `feature/exp07-traceability-study` independiente de EXP-06 y otras PR.
- Objetivo: guion de certificado vigente/trazabilidad, baseline manual comparable, registro y análisis verificable. No inventar resultados ni participantes.

## Cierre — SESSION END STATUS

- Implementado protocolo versionado, templates CSV/JSON vacíos, analizador stdlib, CI y guía en `docs/experiments/exp07-traceability-study.md`.
- Diseño propuesto exploratorio con seis personas, dos órdenes AB/BA y variantes distintas; tiempos CERT/TRACE limitados a 180/300 segundos. Equivalencia del baseline y clave revisada antes de la muestra.
- Analizador conserva roster y denominadores, fallos, ayudas, ausentes y exclusiones de pares; no sobrescribe informes, no interpreta datos vacíos como éxito y no decide aceptación académica.
- Evidencia TESTED del software: 22 controles pasan en Python 3.12 local y 3.11 Docker. Filas de tests sintéticas, temporales, etiquetadas; no se versiona ningún resultado de participantes. `git diff --check` correcto. No suite de aplicación: producción no cambia.
- No realizado: preparación de dataset A/B y baseline final, verificación en UI, reclutamiento, consentimiento y recogida humana; dependen del dataset aprobado y de personas reales. No se declara EXP-07 VALIDATED.
- Rama preparada para commit/push/PR; consultar PR de esta rama para revisión. Ninguna PR se integra automáticamente. Dependencias de producción sin cambios.
- Notion pendiente: «EXP-07 protocolo, plantillas y analizador preparados y comprobados; falta baseline final, piloto y muestra humana. Tarjeta global EXP-01…07 sigue en curso».
- Siguiente paso: revisar protocolo/criterios, congelar equivalencia y clave de respuesta, ejecutar piloto separado y sesiones reales; analizar los registros originales preservando fallos y ausencias.
