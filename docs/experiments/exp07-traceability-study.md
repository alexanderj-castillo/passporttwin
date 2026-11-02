# EXP-07 · Certificado vigente y trazabilidad frente a carpeta/tabla

Estado: protocolo y analizador preparados, **sin participantes ni resultados humanos**. Los tests del analizador usan filas sintéticas temporales; no constituyen un estudio. El alcance procede de la matriz EXP-01…07 de PR #19 y de la exportación Notion confirmada por Pau. Este documento no actualiza Notion.

## Pregunta y diseño prefijado

¿Con qué éxito y tiempo se recuperan un certificado vigente y su evidencia de corrección/aceptación en PassportTwin frente a carpeta y tabla manual? Dos tareas de solo consulta, sin modificar el estado entre participantes. No se mide aquí extracción, matching, deriva ni validez del Health Score.

Se propone una muestra exploratoria de **seis participantes, tres por grupo**, por conveniencia; no es un cálculo de potencia ni permite generalizar. Registrar roles y experiencia previa en el cuaderno de sesión. Mantener el roster incluso si una persona abandona; no sustituir fallos por ensayos nuevos. Si solo participan desarrolladores, declararlo como evaluación interna con sesgo de familiaridad. Un recorrido hecho por Codex sin personas será únicamente comprobación técnica.

| Grupo | Periodo 1 | Periodo 2 |
| --- | --- | --- |
| AB | Carpeta/tabla, variante A | PassportTwin, variante B |
| BA | PassportTwin, variante A | Carpeta/tabla, variante B |

Asignar alternativamente AB/BA al reclutar, antes de conocer resultados; documentar desviaciones. Cada periodo contiene CERT y después TRACE, sobre activos diferentes. Las variantes deben tener igual número de instrumentos/documentos, misma profundidad de historial, distractores y ambigüedad, con identificadores y respuestas diferentes. Este diseño equilibra método/periodo; no elimina por completo aprendizaje ni diferencias entre variantes. No reutilizar el mismo activo del calentamiento.

No se fija un umbral de aceptación del producto a partir de esta preparación. El análisis es descriptivo: tasas de éxito, errores y ayudas por tarea/método; mediana de diferencias emparejadas de tiempo. Prefijar y aprobar cualquier criterio formal antes de la recogida, versionando el protocolo y su hash. No ajustar tareas/criterios después de ver resultados.

## Preparar datos y baseline antes del primer participante

1. Usar una copia desechable del dataset congelado y anotar fecha de referencia, commit completo, versiones, máquina, red, navegador y URLs en el cuaderno referenciado por `environment_ref`. Evitar que venza un certificado o cambie el reloj entre periodos; si la UI depende del día actual, completar los ensayos ese día o preparar el entorno con la fecha acordada y documentarlo.
2. Preparar A y B con un certificado anterior y uno vigente aceptados, documentos distractores pendientes/rechazados, y al menos una corrección documentada seguida de aceptación para el activo de TRACE. No basta ejecutar `tools/dev.py demo`: puede conservar correcciones previas y no garantiza esos eventos equivalentes. Preparar estos casos en el entorno desechable y verificar sus auditorías antes de congelar.
3. Para cada variante, crear una carpeta `certificates/` con copias de los mismos archivos RAW que puede abrir el usuario en PassportTwin y una `instruments.csv` con serial, ubicación, document_ref, filename, estado, calibration_date, next_due_date y SHA-256. Crear `audit.csv` con document_ref, action, created_at, source, actor, before y after (JSON dentro de celda CSV). Exportar esos datos del mismo estado canónico; no reconstruirlos de memoria. Actor ausente queda vacío en ambos métodos. Si la UI no permite acceder al archivo o a un campo, resolverlo antes del estudio o declarar la tarea no disponible en ambos métodos.
4. El baseline permite explorador de archivos, visor PDF y lector habitual de CSV, con búsqueda/ordenación ordinarias. PassportTwin permite su buscador, pasaporte, documentos y auditoría. Mantener ambos preparados, con sesión iniciada, sin abrir la respuesta. Sin API, SQL, scripts ni ayuda del desarrollador durante la tarea. Los datos y las posibilidades de consulta deben ser equivalentes; registrar cualquier diferencia residual.
5. Un evaluador distinto del implementador revisa ambos entornos y prepara una clave privada para CERT y TRACE en A/B. CERT: activo, documento aceptado más reciente cuya calibración ≤ referencia ≤ vencimiento, nombre de archivo, fechas, hash; si no hay vigente, respuesta explícita y prueba. Resolver empates/ambigüedades antes del ensayo. TRACE: documento y eventos exactos, fechas, origen, campo, antes y después; no inferir actores inexistentes. Guardar junto a cada respuesta sus fuentes canónicas.
6. Crear manifiestos ordenados con ruta relativa y SHA-256 de todos los archivos del dataset, baseline y exportación de snapshot UI/API para cada variante. Calcular SHA-256 de cada manifiesto y anotarlo en `session.json`; guardar los manifiestos y archivos originales fuera de Git. Hash de la clave y de `experiments/exp07/protocol.json` también obligatorio. El analizador comprueba formato/coincidencia del protocolo; una persona debe contrastar los demás hashes con los artefactos reales. No llamar «congelado» a un hash inventado.

La preparación del baseline no está automatizada por este kit: depende del dataset final aprobado y de comprobar equivalencia en la UI. No empezar la muestra si esta preparación está incompleta. Un piloto separado (excluido y documentado) comprueba claridad y accesibilidad; cualquier cambio posterior requiere nueva versión antes de la muestra.

## Guion del observador

- Obtener consentimiento para observación y, si se acuerda, grabación. Usar pseudónimos; conservar identidades y consentimiento aparte, sin subirlos a Git. Registrar experiencia de uso y rol. El participante puede parar; contabilizarlo como `aborted` con motivo, sin penalizarlo personalmente.
- Calentamiento no medido de dos minutos por método sobre otro activo. Explicar herramientas disponibles y dar instrucciones idénticas. Reiniciar la vista/carpeta a su punto inicial antes de cada tarea; cerrar resultados del calentamiento y del periodo anterior. Mantener el mismo equipo y visor.
- Leer el prompt CERT/TRACE de `protocol.json`, sustituyendo activo/documento de la variante según la clave. La persona confirma que entiende. Iniciar cronómetro monotónico al decir «empieza», con interfaz inicial lista y prompt visible. Incluir navegación, lectura, búsqueda y espera de la aplicación en el tiempo.
- Detener al entregar la primera respuesta final, al abandonar o al límite (CERT 180 s; TRACE 300 s). Una respuesta final equivocada termina como `incorrect`; no dar intentos adicionales. El observador verifica después contra la clave sin contar ese tiempo. Ante límite, `timeout` y tiempo igual al límite. Ante fallo de infraestructura, `aborted` y motivo; no borrar esa fila ni repetirla como si no hubiera ocurrido.
- Registrar errores observables (activo/archivo equivocado o afirmación incorrecta) y ayudas de contenido/navegación; una aclaración neutral del prompt no cuenta como ayuda, pero se anota. Toda ayuda se describe. Un éxito asistido sigue siendo éxito observado, pero se excluye del análisis primario de tiempos emparejados.
- Guardar una evidencia por tarea (respuesta entregada y localización del archivo/evento, captura o nota detallada del observador), junto con referencia de observador. Un enlace a la página inicial sin respuesta no demuestra éxito. Conservar errores y respuestas fallidas. El analizador exige referencias, no verifica su contenido.

## Registro y análisis

Copiar los tres templates de `experiments/exp07/` a un directorio privado de resultados. Los CSV solo tienen cabeceras: no hay participantes prellenados. Completar `session-template.json` sin dejar campos vacíos y renombrarlo a `session.json`. Los hashes identifican manifiestos reales; `app_commit` identifica la versión UI/backend probada, no el commit del analizador.

Una fila por participante/tarea/método, sin reintentos. `period` y `variant` deben seguir su grupo. `verified` usa `true`/`false` literal; `success` exige verificación. Tiempos positivos en segundos con punto decimal, `errors`/`assists` enteros no negativos. Para CSV con comas o saltos de línea en notas, usar comillas CSV. Guardar datos UTF-8. Referencias locales a evidencias, sin credenciales. El roster permite informar también las tareas que no se han registrado.

Comando en una sola línea, válido también en PowerShell desde raíz:

```sh
python experiments/analyze_exp07.py --participants results/exp07/participants.csv --observations results/exp07/observations.csv --session results/exp07/session.json --output results/exp07/report-01.json
```

El informe requiere ruta nueva y no sobrescribe resultados. Sale 0 solo con todas las observaciones previstas; `INCOMPLETE`/`NO_DATA` escriben informe y salen 2. Datos inválidos salen 2 sin informe nuevo. `COMPLETE_OBSERVATIONS` significa cobertura del roster, **no** aprobación del producto ni validación académica. Incluso una muestra pequeña completa puede estar muy sesgada.

Por cada celda tarea/método se informan previstos, observados, ausentes, cuatro estados, éxitos sin ayuda, errores y ayudas. La tasa de éxito usa observados y muestra su denominador; los ausentes siguen visibles. La mediana de éxitos es condicional, no sustituye a los fallos. El tiempo emparejado solo usa mismo participante/tarea con éxito verificado sin ayuda en ambos métodos. Se informa quién se excluye por ausencia, fallo o ayuda y cuántos pares quedan. Ahorro = manual − PassportTwin; porcentaje por par = ahorro/manual × 100. Se conservan valores negativos. Sin pares, métricas `null`, nunca cero inventado. Los timeouts no se convierten en tiempos de éxito ni se usa su límite como duración real de finalización.

Interpretar conjuntamente éxito y tiempo: menos segundos con más fallos no demuestra mejora. Presentar resultados por tarea, grupo/orden, rol y familiaridad en el informe final con sus limitaciones; el JSON conserva tiempos por par pero no ajusta efectos de aprendizaje ni realiza inferencia estadística. No fijar conclusiones con dos desarrolladores ni mezclar piloto y muestra final.

## Evidencia disponible y pendiente

El kit tiene controles de cálculos emparejados, fallos/ayudas/ausencias, valores inválidos, orden/variante, verificación, hashes, CSV vacío y no sobrescritura. No se ha ejecutado estudio con personas, generado baseline final, comprobado un dataset A/B en UI ni decidido criterio de aceptación académico. Esos pasos siguen pendientes; la tarjeta global EXP-01…07 no se cierra con esta PR.
