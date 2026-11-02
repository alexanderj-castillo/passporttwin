# EXP-05: preparación reproducible de riesgo 30/60/90 — 02/11/2026

Esta entrega prepara EXP-05 sin cambiar los modelos productivos. Reutiliza mecanismos y semilla de desarrollo conocidos, añade controles de disponibilidad y aplica dos servicios reales. **No es una nueva evaluación final independiente, ni sustituye la evaluación histórica.**

## Qué cubre y qué queda pendiente

| Requisito | Evidencia histórica | Preparación actual / pendiente |
| --- | --- | --- |
| Riesgo en fechas 30/60/90 | Protocolo previo y evaluación OLS de seis escenarios | Resultados por horizonte para núcleo OLS y política de mantenimiento |
| Comparación con último estado observado | Baseline de estado y persistencia gaussiana | Comparaciones pareadas, cobertura propia de cada baseline y denominadores explícitos |
| Precision/recall/F1 y Brier | Brier/ECE/cobertura; sin clasificación por umbral | Métricas con umbral candidato **0,5**, sin optimizarlo ni tratarlo como criterio final aprobado |
| Ausencia de datos y abstenciones | Contador global y tests de servicio | Motivo y cobertura por enfoque/horizonte/escenario; nulos conservados |
| Mantenimiento | Stress de reinicio futuro desconocido, sin contexto de mantenimiento en el servicio evaluado | Controles de mantenimiento conocido reciente y recuperado, con la política real; cambios futuros desconocidos siguen siendo adversos |
| Datos/protocolo congelados finales | Congelación previa del ensayo histórico, con su alcance | Paquete de preparación identificado y reproducible; falta acordar y congelar el nuevo protocolo/test final independiente |

Los archivos de `experiments/acceptance/` y sus resultados permanecen intactos. No se reejecuta el bloque histórico de Health Score v1 ni se presenta como validación actual del Health Score v2.

## Paquete y generación

`experiments/run_risk_exp05.py prepare` crea un directorio nuevo con `dataset.json` y `manifest.json`, sin sobrescribir uno existente. La generación usa RNG local y no modifica el estado aleatorio global. La evaluación verifica hashes, contrato, fuente del generador y regeneración exacta de bytes.

Configuración predeterminada: seed **20261027**, tres familias, historiales de 8/16 calibraciones y tres trayectorias por celda. Conserva las seis familias de escenario del protocolo conocido: estable, lineal, curvatura, cambio brusco, colas pesadas y reinicio futuro desconocido. Añade seis controles deterministas por familia:

- historial insuficiente;
- varianza residual nula;
- fechas duplicadas;
- tolerancia cambiante;
- mantenimiento conocido con solo una calibración posterior;
- mantenimiento conocido con tres calibraciones posteriores.

Son **126 casos y 378 fechas objetivo**, no 756 observaciones independientes. Se calculan dos enfoques sobre esas mismas fechas; las tres observaciones futuras de cada trayectoria están correlacionadas. Los controles repetidos por escala/familia tampoco son participantes o datos industriales independientes.

## Servicios y corte temporal

- `core_ols`: `estimate_tolerance_risk`, versión identificada por el commit/hash de `tolerance_risk.py`.
- `maintenance_policy`: `risk_after_maintenance`, versión identificada por el commit/hash de `lifecycle_health.py`.

Al modelo solo llegan fecha/error/tolerancia del historial y, para la política, las fechas de mantenimiento conocidas. Las etiquetas futuras permanecen separadas. Se evalúa excedencia **en la fecha objetivo**, no cualquier cruce durante el intervalo.

La política excluye calibraciones anteriores o iguales al último mantenimiento conocido en el origen. Con menos de tres posteriores puede abstenerse. Mantenimiento futuro no se usa para anticipar cambios desconocidos. Tests perturban etiquetas, tolerancias futuras, calibraciones futuras, eventos futuros y errores premantenimiento y verifican que no entren en los pronósticos correspondientes.

## Métricas sin ocultar abstenciones

Por enfoque, horizonte y escenario se registran fechas previstas/puntuadas, positivos antes/después del filtro, cobertura de estimación y motivos de abstención. Una probabilidad nula no se transforma en cero; una probabilidad **0,0** sí se puntúa como estimación disponible.

- Brier y precision/recall/F1: subconjunto con probabilidad disponible. Denominadores de clasificación indefinidos quedan en nulo.
- Baseline de estado: último error observado fuera de tolerancia, en el historial elegible de cada enfoque. Se abstiene si falta una observación válida o la fecha más reciente es ambigua.
- Persistencia gaussiana: media del último error y **desviación predictiva compartida con el modelo**, como en el ensayo previo. Es un comparador condicionado, no un modelo independiente de incertidumbre.
- Cada comparación con baseline usa exclusivamente muestras donde ambos están disponibles. Además se informa la cobertura y puntuación propia del baseline.
- La comparación núcleo/política usa solo sus pronósticos disponibles comunes. No se comparan promedios sobre muestras distintas como si fueran equivalentes.
- ECE de diez bins, cobertura nominal 95 % y MAE normalizado se informan sobre el subconjunto puntuado, con soportes. No acreditan calibración industrial y el tamaño de este ensayo es pequeño.

Un error técnico conserva el caso y anula las métricas finales, separando diagnósticos parciales. También se rechazan filas de pronóstico faltantes/duplicadas y cambios de inputs durante la ejecución. COMPLETE significa ejecución completa, **no aceptación académica**. El contrato contiene `acceptance_thresholds: null`.

## Resultado de preparación

- Dos generaciones sin red produjeron dataset/manifiesto idénticos. SHA-256 del dataset: `bee0dc555d2e9cbeecf70db1372d1a4e84535a4ab2070e41afdcd10169a2f034`.
- CLI sin red ni base de datos: 126/126 casos, sin errores técnicos.
- Núcleo: 342 fechas puntuadas y 36 abstenciones; política: 333 puntuadas y 45 abstenciones. La diferencia añade nueve abstenciones por historial postmantenimiento insuficiente.
- 180 tests backend+BI antes de la última adición métrica, 17 tests focales finales y **270 tests backend+BI** con la composición local de PR #19–24 más esta entrega. Sin conflictos ni cambios de modelos; composición conservada en `test/ambiguity-pending-prs`.

Se conservan resultados adversos. Ejemplo del núcleo en este pequeño paquete, 54 fechas por escenario:

| Escenario | Brier | Cobertura nominal 95 % observada |
| --- | ---: | ---: |
| Estable | 0,0771 | 96,30 % |
| Lineal | 0,0243 | 100 % |
| Curvatura | 0,1415 | 55,56 % |
| Cambio brusco | 0,4909 | 0 % |
| Colas pesadas | 0,0546 | 85,19 % |
| Reinicio futuro desconocido | 0,2676 | 29,63 % |

No se ajustaron modelos ni umbrales para mejorar esos resultados. Los grupos son de desarrollo conocidos y no reproducen la muestra completa de 1.080 trayectorias anterior: no comparar sus cifras como una mejora entre versiones.

[Manifiesto registrado](../../experiments/results/exp05_preparation_manifest.json) y [resumen versionado](../../experiments/results/exp05_runner_preparation.json). El informe completo local contiene las 756 filas enfoque/fecha; para evitar duplicar datos voluminosos en Git, el resumen conserva su recuento y hash canónico. Se regeneran con los comandos siguientes. Fuentes contrastadas contra el commit; Python e identidad de imagen Docker registrados. Sin Git en la imagen, el SHA del host queda etiquetado como declarado/no verificado y el árbol como desconocido: comprobar correspondencia/árbol limpio antes del test final.

## Uso desde PowerShell

Requiere esta rama integrada y la imagen backend con dependencias (`docker compose build backend` si falta). Desde la raíz, cada línea por separado:

```powershell
New-Item -ItemType Directory -Force data/generator/output | Out-Null
```

```powershell
git status --short
```

```powershell
$commitExp05 = git rev-parse HEAD
```

```powershell
docker run --rm --network none -v "$($PWD.Path):/repo:ro" -v "$($PWD.Path)/data/generator/output:/runs" -w /tmp passporttwin-backend:latest python /repo/experiments/run_risk_exp05.py prepare --bundle /runs/exp05-preparation-a
```

```powershell
docker run --rm --network none -v "$($PWD.Path):/repo:ro" -v "$($PWD.Path)/data/generator/output:/runs" -w /tmp passporttwin-backend:latest python /repo/experiments/run_risk_exp05.py evaluate --bundle /runs/exp05-preparation-a --code-commit $commitExp05 --output /runs/exp05-preparation-a-report.json
```

No requiere Metabase, PostgreSQL o AAS arrancados. Repetir requiere otro nombre de informe; comprobar otra generación requiere otro directorio de paquete. No se sobrescriben resultados anteriores. El hash de filas se calcula como SHA-256 del JSON de `report.details` con claves ordenadas, separadores `(',', ':')`, UTF-8 y `ensure_ascii=False`.

## Pendiente para el EXP-05 final

Acordar operación/umbral de clasificación y criterios de aceptación antes de observar el nuevo test final; separar desarrollo y evaluación independiente; congelar protocolo, datos, código y versiones. Incluir los límites y abstenciones en las conclusiones. No introducir M2 ni calibrar probabilidades sobre este paquete para volver a presentarlo como independiente. La tarjeta global de siete experimentos sigue en curso.
