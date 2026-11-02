# Memoria y metodología · índice inicial de evidencia

Borrador de reconstrucción del proceso, 02/11/2026. No es la memoria terminada ni una evaluación del efecto de la IA. El encargo actual exige preparar la redacción mientras se mejora producto y se valida. Faltan plantilla/rúbrica, fechas y material escrito fuera del repositorio; no se asumen.

## Qué podemos documentar con fuentes

| Hecho / tema | Evidencia consultable | Uso y límite |
| --- | --- | --- |
| Reglas de colaboración, estados de evidencia y cierres | `AGENTS.md`, `docs/sessions/TEMPLATE.md`, `docs/sessions/2026-10-26-codex-preparacion.md` | Describe procedimiento documentado; un procedimiento escrito no demuestra que se cumpliera siempre |
| Estado canónico y proyección reconstruible | README, contratos de `docs/architecture/`, API `/sync`, builder y tests | Justifica arquitectura PostgreSQL→AAS; distinguir semántica específica MVP de plantilla estándar certificada |
| Evolución del pasaporte, analítica y demo | Cierres del 26–27/10, PR #6–18 y documentos enlazados desde README | Fechar checkpoints; no sumar recuentos de suites distintas como número de pruebas únicas |
| Auditoría de reproducibilidad | PR #19 y `docs/experiments/final-experiments-matrix.md` | Reloj de casos FUTURE_DATE, muestra omitida, unidades y fuga temporal como problemas concretos detectados |
| Herramientas experimentales | PR #20–23/#25 y guías EXP-01…05 | Distinguir mejora del runner, resultado de preparación y validación independiente |
| Error descubierto y corregido con evidencia | PR #23 detecta matching ambiguo; PR #24 conserva candidatas y fuerza revisión | Caso útil de control de errores y revisión humano–IA. Mejora en casos conocidos no equivale a generalización |
| Interoperabilidad comprobada | PR #26, informe EXP-06 y cierre de sesión | Paquete real SDK/servidores, normalizaciones declaradas, 129/129 y 43/43 entradas; límites explícitos |
| Separación entre herramienta y datos humanos | PR #27, protocolo/analizador EXP-07 | Código comprobado sin inventar participantes; estudio pendiente |
| Comprobación después de integrar | `docs/verification/integrated-2026-11-02.md` | Diferencia entre tests verdes y tareas UI incompletas; fallos reales también son evidencia metodológica |

Las PR están en `https://github.com/projects-i40-ap/passporttwin/pull/<n>`. Usar sus commits/revisiones/fechas como fuentes; no atribuir una acción a una persona o asistente solo por el autor del commit. Contrastar reparto con registros y con Pau/Alexander.

## Estructura de redacción que puede empezar ahora

1. Problema, contexto de instrumentos y objetivos medibles. Delimitar MVP y circularidad futura frente a lo realmente implementado.
2. Requisitos y decisiones de arquitectura; modelo canónico, documentos, auditoría, AAS, analítica y visualización.
3. Metodología de desarrollo: organización, iteraciones, fuentes de verdad, ramas/PR/revisión, uso de IA y verificación. Registrar cambios de alcance y límites de la reconstrucción retrospectiva.
4. Implementación por recorrido funcional, con ejemplos y versiones identificables. Incluir mejoras frontend pendientes cuando existan.
5. Diseño experimental y datasets: sintéticos como ruta principal; cohortes reales solo si se consiguen. Baselines, independencia, criterios y amenazas a validez antes de resultados.
6. Resultados/discusión tras ejecución final: qué cumple cada objetivo, qué falla y qué no se ha podido evaluar. Separar validez técnica, usabilidad y extrapolación a industria.
7. Conclusiones, limitaciones y trabajo futuro. Evitar porcentajes globales de «proyecto terminado» sin denominador acordado.

## Recogida pendiente para la metodología humano–IA

Por hito, recopilar objetivo, contexto entregado al asistente, propuesta, revisión humana, cambio aceptado/descartado, comprobación, evidencia y limitación. Elegir ejemplos de éxito y fallo; no seleccionar solo casos favorables. Fuentes históricas DOCX/chats/exportaciones deben citar versión y fecha, contrastadas con Git.

No afirmar ahorro de tiempo, productividad superior, reducción de errores o causalidad atribuida a IA sin medidas comparables. Si no hay registros de horas/baseline, puede describirse el proceso y analizarse cualitativamente, con esa limitación.

## Defensa que puede prepararse en paralelo

Preparar la historia problema→caso rotulado→recorrido→evidencia→límites. Escoger un caso sintético reproducible si no hay real, sin presentarlo como certificado industrial. Incluir un fallo/abstención y su revisión, no solo el caso sano. Fijar tiempos y diapositivas cuando se conozca la duración oficial; después ensayar con alternativa grabada y preguntas sobre datos, modelos, AAS y uso de IA.
