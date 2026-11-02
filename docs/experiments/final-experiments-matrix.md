# Preparación de EXP-01 a EXP-07 — 01/11/2026

Estado: **inventario y revisión previa**, no ejecución final ni protocolo congelado.
Base inspeccionada: `main` en `0d9d1b9` (PR #18 integrada).

## Fuentes y límites

- Tarjeta de la exportación Notion confirmada por Pau: «Ejecutar los 7 experimentos finales (EXP-01 a EXP-07) sobre dataset congelado», Critical, Both; pide semilla, commit, versión y separación temporal sin fuga. La consulta directa al backlog devolvió 404: no se ha actualizado Notion.
- Los nombres, preguntas y métricas de los siete EXP proceden del documento inicial `PassportTwin_Documento_Base_TFM_v1.0.docx`, sección 21. Es contexto histórico, no una confirmación de que el protocolo siga aprobado sin cambios. La exportación del backlog confirma EXP-03/reglas y EXP-06/AASX.
- Código y artefactos integrados prevalecen para describir disponibilidad. Los resultados anteriores se conservan como evidencia histórica.
- [Inventario con hashes](../../experiments/final/preparation-audit.json): 29 archivos inspeccionados, 20 certificados y manifiesto; consistencia de recuentos históricos comprobada. Estos hashes identifican evidencia revisada, **no congelan el dataset final**.

## Matriz de trabajo

Los criterios pendientes deben fijarse antes de la ejecución final. No se deducen umbrales de resultados ya observados ni se inventan participantes o mediciones.

| EXP | Pregunta y métricas de referencia | Evidencia disponible | Preparación pendiente / criterio |
| --- | --- | --- | --- |
| EXP-01 Extracción | Campos clave correctos; accuracy/F1 por campo y porcentaje de correcciones; referencia manual/reglas simples | PDFs con ground truth, extractor PDF y pipeline | Runner por campo, normalización de comparación prefijada, campos ausentes/errores contabilizados, baseline operativo; definir muestra y umbral de aceptación |
| EXP-02 Matching | Documento asociado al activo correcto; accuracy, REVIEW_REQUIRED y falsos matches; baseline serial exacto | Matching determinista por serial en validación documental | Catálogo congelado y casos limpios, desconocidos y ambiguos; ground truth independiente. Si implementación y baseline son el mismo método, declararlo; no atribuir una mejora inexistente |
| EXP-03 Reglas | Precision/recall/F1 **por regla**; anomalías inyectadas | `benchmark_rules_exp03.py`, 20 PDFs y `results_exp03.json`: 8 TP, 12 TN, 0 FP/FN históricos | Control del reloj; ampliar cobertura a unidades/rango/duplicados y aceptación fuera de tolerancia; no omitir errores de ejecución; informe por regla y tamaño final prefijado |
| EXP-04 Deriva | B0 persistencia, B1 familia, M1 lineal; MAE/RMSE por horizonte | Generador, benchmark y resultados históricos: 60 instrumentos, 480 registros declarados, 6 train/2 test, 120 predicciones, horizontes 90/180 días | Regenerar e identificar dataset; métricas por familia/horizonte y normalizadas por tolerancia; revisar cortes temporales entre activos; vincular benchmark y servicio productivo; prefijar criterio comparativo |
| EXP-05 Riesgo | Salida de tolerancia 30/60/90; precision/recall/F1 y Brier probabilístico, baseline último error | Evaluación OLS sintética con protocolo previo, Brier/ECE/cobertura y escenarios adversos; política postmantenimiento disponible | Reconciliar protocolo final con evaluación existente; definir umbral de clasificación, abstenciones y política postmantenimiento; no llamar independiente a un test ya usado para ajustar. Conservar resultados adversos |
| EXP-06 AAS | Round-trip AASX; porcentaje de campos críticos preservados y pass/fail | Sincronización AAS y pruebas de submodelos; tarjeta específica de exportación/importación | No se localizó runner AASX en backend/tests inspeccionados. Implementar/identificar exportador-importador, lista explícita de campos críticos, verificación tras importación y aislamiento de BaSyx; AAS JSON no equivale a AASX |
| EXP-07 Trazabilidad/UI | Recuperar certificado vigente y evidencia; éxito y tiempo de tarea frente a carpeta/tabla manual | UI, auditoría y comprobaciones funcionales; ensayo local de Pau con Metabase | Guion, tareas, baseline y reglas de tiempo/éxito; registrar participantes/roles si existen, aprendizaje y orden. Sin participantes, informar recorrido técnico, no estudio de usabilidad |

## Revisión detallada de EXP-03

1. **Reloj:** `cert_002.pdf` y `cert_010.pdf` están etiquetados FUTURE_DATE con fecha `2026-10-31`. El motor compara con `datetime.utcnow().date()`: el 01/11 ya no son futuros. El generador usa `date.today()` y los PDFs no fijan metadatos deterministas. Semilla 42 sola no reproduce los mismos bytes ni la semántica temporal.
2. **Cobertura:** manifiesto de 20: 10 NONE, 3 SERIAL_MISMATCH, 2 FUTURE_DATE, 3 INVALID_DUE_DATE y 2 OUT_OF_TOLERANCE. No hay casos dedicados a unidad/rango/duplicados. R-TOL-01 se evalúa durante aceptación, no en la clasificación de extracción del benchmark.
3. **Métricas:** matriz global y coincidencia exacta de conjuntos de reglas, sin precision/recall por regla. `precision`/`recall` usan 1 si su denominador es cero; la ejecución final debe declarar casos no definidos y soportes.
4. **Integridad:** PDF ausente, error de subida o procesamiento provoca `continue`; puede publicar métricas sobre una muestra parcial sin fallar el proceso. Reutiliza IDs tras un 409 y reprocesa documentos: requiere API/base/RAW desechables, catálogo controlado y registro de fallos.
5. **Procedencia:** resultado histórico sin hash del dataset, commit, versiones efectivas ni fecha de referencia. El inventario actual no añade esos datos retroactivamente a la ejecución pasada.

## Revisión detallada de EXP-04

1. `ai/datasets/drift_synthetic.csv` no existe en el checkout limpio y está excluido por `.gitignore`; hay generador determinista con seed 42. El siguiente paso es generarlo en una ruta de ensayo, registrar hash y comparar reproducibilidad sin sobrescribir evidencia.
2. Split de primeras 6/últimas 2 calibraciones por activo; B1 usa pendientes de entrenamiento de la familia. No utiliza etiquetas de test para el ajuste, pero las fechas iniciales varían: hay que verificar disponibilidad por calendario para cada origen de pronóstico, o declarar explícitamente evaluación por edad del activo y sus límites.
3. MAE/RMSE globales mezclan magnitudes físicas distintas; no sirven como una métrica física única de flota. Publicar por familia/horizonte y agregar solo errores adimensionales normalizados de forma prefijada.
4. B1 es **tendencia media de familia**, no media/mediana del error: reconciliar la descripción histórica del backlog con este contrato antes de comparar.
5. El benchmark implementa su propio ajuste lineal; no prueba automáticamente la equivalencia con el servicio expuesto por la API. El generador también es lineal: declarar alineación entre hipótesis y datos, incluir límites/escenarios adversos sin ajustar sobre el test final.
6. `determine_best_model` elige el menor RMSE de test: puede describir la comparación, pero no debe usarse para ajustar modelos y volver a presentar el mismo test como independiente. La semilla del reporte está escrita como constante, no verificada contra los bytes leídos.

## Orden y condiciones de ejecución

1. Reconciliar definiciones EXP con el equipo y fijar muestra, métricas y criterios; conservar esta revisión como preparación.
2. Preparar runner de EXP-03 que falle ante muestras perdidas, reloj explícito, cobertura por regla y entorno desechable. Acordar cómo demostrar aceptación R-TOL-01.
3. Preparar EXP-04 con datos identificados, controles temporales y métricas comparables. Separar mejoras de runner de cambios de modelo.
4. Congelar protocolo y datasets de la nueva ejecución en un commit previo: bytes/hashes, generación, semilla, reloj, catálogo y split; guardar versiones Python/dependencias e imágenes/digests efectivas.
5. Ejecutar cada EXP con ID de corrida, estado completo/parcial/fallido y logs, sin sobrescribir informes anteriores. Las desviaciones se registran; no se cambian criterios después de ver resultados.
6. EXP-01/02 comparten PDFs/catálogo con EXP-03; EXP-06 puede avanzar con Alexander en su tarjeta propia. EXP-07 requiere guion y, si procede, participantes, no bloquea la preparación de reglas/deriva.
7. Cerrar la tarjeta global solo con los siete informes, limitaciones, revisión e integración. Los resultados negativos no se ocultan y pueden ser conclusiones válidas del TFM.

Este documento no declara terminada ninguna tarjeta y no introduce cambios funcionales, de fórmulas ni en los datos del equipo.
