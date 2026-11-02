# Comprobación integrada de main · 02/11/2026

Base comprobada: `823a4bb061c0ca855636fe5052c6b312131765de`, PR #19–27 integradas. Rama de esta entrega `test/integrated-closeout`. [Resumen estructurado](integrated-2026-11-02.json). Datos sintéticos y servicios desechables; no se ha modificado la instalación de Pau ni el PostgreSQL/BaSyx habituales del workspace.

## Resultado

| Comprobación nueva sobre main | Resultado |
| --- | --- |
| Backend y BI, Python 3.11 / PostgreSQL 17 | 270 pruebas pasan |
| SDK AASX y analizador EXP-07, Python 3.11 | 32 pruebas pasan (10 + 22) |
| Build React/Vite, Node 20.20.2 / Vite 5.4.21 | Correcto; dependencias de imagen cacheada, fuentes main |
| API real, PDFs digitales con etiqueta soportada `Serial:` | Tres calibraciones para C; ambigüedad C/D fuerza revisión, corrección a D y materialización de una calibración |
| Duplicado RAW y segunda materialización del mismo documento | Ambos rechazados con 409; no se añaden calibraciones repetidas en el ensayo |
| Reconstrucción AAS, UUID, QR, redirección y snapshots | Ambos activos del flujo sincronizados; QR PNG y destino configurado correctos; snapshots CURRENT |
| Escenarios demo y SQL de flota | Cuatro escenarios; seis activos ejercitados CURRENT y dos activos diagnósticos sin snapshot; diez consultas SQL ejecutadas |
| Metabase v0.64.3.4 real | Diez tarjetas; 30 consultas correctas sin filtro y con ubicación/familia. Los filtros demo devuelven cuatro activos |
| Chromium, escritorio 1280 px y móvil 390 px | Búsqueda, pasaporte, revisión, auditoría y retorno comprobados; sin errores JS ni overflow en vistas revisadas |

Los recuentos 270 y 32 son suites diferentes de esta ejecución, no una suma de checkpoints históricos. Esto demuestra comportamiento técnico de los casos comprobados; no completa los siete experimentos finales ni un estudio humano.

## Fallos y tareas bloqueadas

1. **Etiqueta de serie no soportada correctamente.** PDF digital controlado con `Serial Number: CLOSEOUT-A`: el extractor devuelve `serial_number=Number`; matching no encuentra activo y devuelve REVIEW_REQUIRED/R-ID-01. Se conserva como diagnóstico. El recorrido posterior utiliza otra serie C/D y `Serial:`, formato que admite el producto. No se altera el caso fallido para presentarlo como éxito.
2. **Abrir el original pendiente.** El nombre PDF del pasaporte lleva a revisar campos; no se localiza ruta de archivo/descarga en OpenAPI. CERT de EXP-07 exige resolver este acceso antes del piloto.
3. **Validación no es materialización.** Revalidación real de la corrección devuelve ACCEPTED pero el historial de D sigue con cero calibraciones hasta POST `/documents/{id}/accept`. La UI solo ofrece revalidar y muestra «Documento validado y aceptado»; falta una acción explícita de incorporación canónica.
4. **Estados por campo confusos.** Documento aceptado con campos STAGING («Pendiente de validación»). Hace falta resolver semántica y presentación; no ocultarlo pintando todos los campos como válidos.

Las tareas están priorizadas en [backlog frontend/usabilidad](../frontend-usability-backlog.md). Esta entrega no corrige código productivo ni declara realizadas las tareas faltantes.

## Entorno y límites de reproducción

Se usan imágenes locales existentes con el código de main montado en lectura: backend `1f1420649bc8`, frontend `daae8a8c406e`, herramienta AASX `117df192b86c`, PostgreSQL `82903352d6fa`, BaSyx 1.4.0 `1d44b0ef4f9a` y Metabase `645c1977a286`. No se reconstruyen dependencias desde cero ni se modifica requirements. Los avisos Requests/Starlette siguen presentes; no causan fallos en las suites, pero no se consideran resueltos.

Comandos base realmente utilizados, con red `ptwin-closeout`, base `passporttwin_test` y montajes aislados:

```sh
python -m pytest tests /repo/bi/tests -q -p no:cacheprovider --tb=short
python -m pytest /repo/experiments/tests -q -p no:cacheprovider
npm run build
```

Backend/BI necesita `DATABASE_URL` del PostgreSQL desechable, `STORAGE_RAW_DIR` temporal y `PYTHONPATH=/repo/backend:/repo`. Esquema SQL aplicado con `psql -v ON_ERROR_STOP=1` por stdin. No ejecutar estas pruebas contra datos operativos. Los probes API/Chromium/Metabase son scripts de sesión fuera de Git, con IDs efímeros; el JSON registra sus hashes y los de sus informes. Esta entrega **no proporciona un nuevo runner E2E portable**; no confundir un resumen de evidencia con un paquete de reproducción completo.

Incidencias del montaje, conservadas como parte del ensayo: primer PostgreSQL no pudo leer el bind mount del esquema; se recreó únicamente esa base y se aplicó por stdin. Las variables de proxy internas requerían configurar tanto `NO_PROXY` como `no_proxy` para los hosts Docker locales; no se cambió acceso externo. Primer Metabase consultó antes de crear vistas; se repitió con vistas preparadas y otra base desechable. El probe de navegador esperaba una traducción antigua de STAGING y se corrigió contra el mapeo vigente antes de terminar la comprobación. Ninguno de esos intentos se contabiliza como un PASS inicial.

No se ha demostrado apertura del RAW desde UI, conservación de archivos a través de recreaciones de contenedores API, toda la accesibilidad, ni recorrido íntegro exclusivamente desde UI. Los probes usaron endpoints API para cargar/procesar/materializar. Tampoco se ha repetido aquí el round-trip de dos servidores AASX completo; sí sus diez controles SDK y la sincronización productiva real. El informe histórico EXP-06 permanece identificado por su propio commit.

## Continuación

Cerrar UI-01/02/03 y DOC-01 en cambios acotados; después mejorar presentación y ejecutar piloto separado. Preparar datos/baseline y contrastar EXP en paralelo. Congelar la versión del estudio después de esas mejoras. Datos reales opcionales, sintéticos explícitos como ruta principal.
