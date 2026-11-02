# Frontend y usabilidad · backlog inicial observado

Inspección de `main` `823a4bb` y ensayo aislado del 02/11/2026. Es un punto de partida para Pau/Alexander, no una lista de preferencias visuales ya aprobadas. No se ha modificado el producto en esta entrega.

El [registro técnico central](technical-debt.md) enlaza UI-01/02/03 y DOC-01 como TD-01…04; este backlog conserva el detalle de producto y diseño. Actualizar ambos al resolver un elemento compartido.

| ID / prioridad | Problema y evidencia | Acción propuesta / aceptación | Dependencias |
| --- | --- | --- | --- |
| UI-01 · P0 | El nombre PDF del pasaporte abre el formulario de revisión; no hay ruta de descarga/visualización del original en el OpenAPI inspeccionado. EXP-07 CERT pide abrirlo. | Acción separada «Abrir original»/descargar y «Revisar campos». Servir por ID desde RAW, sin exponer rutas de infraestructura. Archivo correcto, hash coherente, 404 legible y acceso desde pasaporte/revisión. | Endpoint backend y tratamiento de archivo ausente; antes del piloto CERT |
| UI-02 · P0 | Revalidar devuelve ACCEPTED y la UI dice «Documento validado y aceptado», pero no invoca `/accept`. En ensayo real, después de revalidar había 0 calibraciones nuevas; solo `/accept` creó la calibración. | Explicar y permitir las dos fases. Una acción explícita materializa; mostrar resultado y actualizar historial/sincronización. Evitar doble envío y tratar el 409 existente. No inventar materialización por el estado ACCEPTED. | Contrato/indicador verificable de materialización, API y auditoría |
| UI-03 · P0 | Documento aceptado conserva campos STAGING, traducidos «Pendiente de validación». Se observa en documento corregido y aceptado. | Estado documental, revisión por campo y materialización diferenciados. No pintar todos los campos como validados solo por ocultar la inconsistencia. Criterio: usuario identifica qué falta y qué se ha guardado. | Acordar semántica backend/UI; preservar original/correcciones |
| DOC-01 · P0 para muestra amplia | PDF digital con `Serial Number: CLOSEOUT-A` produce `serial_number=Number`, no el activo; queda en revisión. `Serial:` funciona. | Ampliar detección de etiquetas y probar variantes, múltiples series y orden. No eliminar el caso de evaluación ni usar la misma regresión como muestra independiente final. | Corrección del extractor, separada del rediseño; EXP-01/02 |
| UI-04 · P1 | Home mezcla búsqueda y herramientas de revisión/auditoría por IDs; no ofrece desde UI el recorrido completo de upload/process/materialización. | Entrada orientada a tareas; seleccionar documento por nombre/activo, carga/procesado accesibles cuando estén dentro del alcance UI. Mantener enlaces directos y regreso al pasaporte. | UI-01/02; decidir alcance del operador |
| UI-05 · P1 | Mensajes, campos y auditoría mezclan español/inglés y nombres técnicos; auditoría anuncia inmutabilidad en inglés. | Terminología coherente, etiquetas comprensibles, feedback visible de guardar/revalidar/materializar y errores accionables. Mantener detalles técnicos donde aportan trazabilidad. | Catálogo de textos y estados |
| UI-06 · P1 | Ficha extensa; resultados analíticos y acciones requieren lectura larga. Estilo del pasaporte y formularios no comparte un sistema visual. | Resumen de estado con acciones principales; detalle accesible. Tipografía, espacios, botones, tarjetas y tablas coherentes. Conservar «No calculado» y vigencia, sin convertir score/riesgo en garantías. | Propuesta visual para revisión; tareas prioritarias |
| UI-07 · P1 | Solo se han comprobado viewports concretos; no hay auditoría completa de accesibilidad. | Navegación por teclado, foco, etiquetas, mensajes de carga/error, contraste y responsive. Comprobar tablas y revisión en móvil; no asumir accesibilidad por no tener errores JS. | UI estabilizada y pruebas de tareas |
| UI-08 · P1 | Vigencia de snapshots informa del problema, pero el operador depende de comandos/API para actualizar; dashboard es instalación aparte. | Acceso claro a flota y refresco con estado de operación, si se incluye en alcance. No presentar snapshots viejos como resultados vigentes. | API refresh, URL Metabase y definición del rol operador |
| UI-09 · P2 | La demo de defensa necesita una historia corta y repetible. | Recorrido guiado con caso rotulado, datos preparados, evidencia de antes/después, restauración reproducible y vídeo alternativo. | Producto estable, resultados finales y duración de defensa |

Seguimiento UI-01: implementado/probado en [PR #29](https://github.com/projects-i40-ap/passporttwin/pull/29), pendiente de revisión/integración. Las observaciones de la tabla describen la base inspeccionada; no se declara cerrado por existir una PR.

Seguimiento UI-02: implementado/probado en [PR #30](https://github.com/projects-i40-ap/passporttwin/pull/30), apilada sobre #29 y pendiente de integración. UI-03 se sigue en PR #31, también pendiente de integración.

Seguimiento UI-03: implementado/probado en [PR #31](https://github.com/projects-i40-ap/passporttwin/pull/31), apilada sobre #30. No se repintan históricos ni campos sin reglas como validados.

Seguimiento DOC-01: implementado/probado en [PR #32](https://github.com/projects-i40-ap/passporttwin/pull/32), independiente sobre main y compatible en composición comprobada con #29–31. Pendiente de integración.

P0 bloquea tareas o interpreta incorrectamente el estado. P1 mejora la operación y su comprensión; P2 prepara la presentación. No hace falta implementar cada extensión del backlog para cerrar el TFM: acordar qué tareas se defenderán y validar su recorrido completo.

La comprobación integrada no prueba que la UI permita hacer todo lo que existe en la API. Tampoco sustituye a sesiones con usuarios; las métricas humanas solo se recogerán después del piloto y congelación.
