# Navegación por tareas y selección legible

Base main `602b659` con PR #33 efectivamente integrada. Esta entrega prepara UI-04/05: mejora de navegación y textos comunes, no rediseño final ni carga/procesado de archivos.

## Recorridos

- `/` abre Inicio con tres tareas: consultar pasaporte, revisar documento, consultar trazabilidad. Ya no abre por defecto el documento 1 ni presenta un formulario de revisión sin contexto.
- Búsqueda de instrumentos por serie/ubicación para abrir pasaporte o auditoría según tarea.
- `/?tab=review` permite buscar documentos por nombre, serie o ubicación, incluidos los sin vínculo. Filtro de pendientes y paginación. El documento seleccionado muestra su nombre recuperado del servidor.
- `/?tab=audit` ofrece selección de documento o instrumento por nombre, con enlaces que consultan su auditoría. IDs conservados en controles avanzados cerrados por defecto.
- Enlaces anteriores `documentId`, `entity`, `id` y `passport` siguen admitidos. La vista/contexto seleccionado se representa en la URL; recarga y Atrás/Adelante reconstruyen el contexto. Los filtros de búsqueda son locales y se reinician al cambiar de vista.
- Textos comunes de auditoría y columnas en español; se conserva el código real de acción, actor/proceso, procedencia y valores before/after para trazabilidad. Validación documental e incorporación al historial usan tonos/etiquetas distintos.

La aplicación bloquea enlaces internos y carga manual de otro ID con cambios sin guardar, ofreciendo guardar o descartar valores locales; al cerrar/recargar se usa aviso nativo cuando hay borrador. **No hay persistencia de borradores ni garantía de conservación al usar Atrás/Adelante con cambios sin guardar**: cerrar ese caso requiere gestión de borradores/navegación adicional antes del piloto que lo incluya. La prueba de historial se hace con formularios sin cambios pendientes. No afirmar protección completa de todos los mecanismos de salida.

## API de listado

`GET /api/v1/documents?q=&review_only=false&limit=20&offset=0`:

- `q` máximo 200 caracteres, búsqueda parcial sin distinción de mayúsculas por nombre/serie/ubicación; `%`, `_` y barra inversa escapados como texto literal. Consultas parametrizadas.
- `review_only` incluye REVIEW_REQUIRED y FAILED_EXTRACTION.
- `limit` entre 1 y 100, offset no negativo, orden descendente por fecha/ID, `has_more` basado en una fila adicional. No es un snapshot estable ante inserciones concurrentes.
- Cada item expone ID, nombre, estado, tipo, serie/ubicación y UUID público si existe. No devuelve rutas RAW/internas ni contenido de archivos; documentos no vinculados se conservan mediante outer join.
- GET de campos añade `original_filename` para identificar de forma autoritativa el documento cargado. No cambia estados ni materializa datos.

Se mantiene el modelo de acceso actual de la API. El listado no añade autenticación ni aislamiento por usuarios; no se presenta como despliegue multiusuario de producción.

## Evidencia del 02/11/2026

[Resumen](../verification/task-navigation-2026-11-02.json): **332 backend/BI** correctos en Docker/Python 3.11/PostgreSQL 17, ocho nuevos casos sobre listado, búsquedas, literales, vínculo/paginación y límites. Build Node 20/Vite correcto con dependencias cacheadas; avisos Requests/Starlette anteriores persisten.

**12 controles Chromium**: inicio sin revisión por defecto, documentos sin vínculo/paginación, selección por nombre, URL/recarga/historial, borrador protegido y descarte explícito, auditoría por serie y nombre, sin resultados, móvil 390 px, fallo 503 inyectado y reintento contra servidor real, nombre del seleccionado y carga manual avanzada protegida. Sin errores JS en recorridos comprobados. Capturas locales inspeccionadas. Fixtures sintéticos de demo y metadatos sin archivo para páginas de búsqueda, no datos reales ni estudio humano.

El probe adicional de borradores usó inicialmente un selector por valor que cambiaba al editar; se sustituyó por selector estable y se comprobaron los dos casos adicionales. Un primer probe de Atrás esperaba conservar el filtro local y falló; se corrigió la expectativa para comprobar el contrato real de URL/contexto, sin afirmar persistencia del filtro. No hay nueva prueba de calibración o AAS en esta entrega; esos contratos no cambian. Falta evaluar accesibilidad y tareas con participantes, subir/procesar desde UI y diseñar el sistema visual común.
