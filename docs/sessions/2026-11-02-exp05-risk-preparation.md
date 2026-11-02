# Sesión: 2026-11-02 · Pau/Codex · Preparación EXP-05

## Inicio

- Pau autoriza revisar evidencia de riesgo y preparar EXP-05 sin reutilizar pruebas como validación final independiente.
- Base remota `0d9d1b9`; rama `feature/exp05-risk-evaluation`. No se modifica el núcleo de riesgo, política de mantenimiento, protocolo previo o informes históricos.

## Cierre — SESSION END STATUS

- Nuevo prepare/evaluate con paquete reproducible, semilla histórica conocida y controles de abstención/mantenimiento. Umbral 0,5 candidato, sin umbrales nuevos de aceptación final.
- Dos enfoques reales, métricas 30/60/90, baselines de estado/gaussiano, cobertura y razones; comparaciones pareadas y comparación entre enfoques solo en fechas comunes.
- Tests de fuga temporal y postmantenimiento, nulos/cero, métricas y errores. 180 backend+BI iniciales, 17 focales finales y 270 en composición de PR #19–24 + esta entrega, sin conflictos.
- Dos paquetes finales offline idénticos. CLI: 126 casos/378 fechas por enfoque; núcleo 342 puntuados+36 abstenciones, política 333+45. Conserva escenarios adversos, incluida cobertura 0 % ante cambio brusco en este pequeño paquete.
- Manifiesto y resumen con hashes versionados; 756 filas completas conservadas localmente/regenerables, no como datos finales en Git. Código cotejado con commit; imagen/Python registrados.
- PostgreSQL/red desechables de tests retirados al cerrar; los servicios del equipo se conservan. CLI de riesgo no usa red ni DB. No se editó Notion ni se enviaron mensajes externos.
- Rama de pruebas `test/ambiguity-pending-prs` actualizada para reproducción de la composición; no main ni aprobación de PR.
- Preparado para commit/push/PR, revisión de Alexander antes de integrar. Preparación implementada/probada; no experimento final ni cierre de los siete EXP.
- Siguiente paso: EXP-06/AASX y guion EXP-07; acordar/fijar protocolo final y muestra independiente para todo el paquete antes de ejecución final.
