# Consulta del original documental · TD-01 / UI-01

El pasaporte separa **Abrir original** de **Revisar campos**. La revisión enlaza también al original del documento efectivamente cargado, aunque se cambie el ID del formulario sin cargar otro. La ruta React `/documents/{id}/original` conserva navegación a revisión y al pasaporte cuando se conoce su UUID.

## Contrato

`GET /api/v1/documents/{id}/original` lee el documento en PostgreSQL y el archivo en RAW. `?download=true` pide attachment. No cambia estados, calibraciones, correcciones ni auditoría de aceptación.

- Solo archivos regulares cuya ruta resuelta queda dentro de `STORAGE_RAW_DIR`; incluye subcarpetas de demo y rechaza symlinks hacia fuera. Nunca se toma una ruta del cliente ni se devuelve la ruta interna en errores.
- Lee bytes, calcula SHA-256 y exige coincidencia con `sha256_hash`. Sirve esos mismos bytes sin reabrir el archivo tras verificarlo. No regenera ni sobrescribe originales.
- PDF por firma `%PDF-`: `application/pdf`, inline salvo descarga explícita. Otros formatos: `application/octet-stream`, attachment; no se renderiza HTML de una subida como contenido activo.
- Nombre original saneado sin componentes de ruta ni controles; `Content-Disposition` UTF-8. Expone esa cabecera y `X-Content-SHA256` a los orígenes CORS ya configurados. Incluye ETag, `no-store` y `nosniff`.
- 404 si el documento o archivo no está disponible/fuera de RAW; 409 si el hash falta, es inválido o no coincide. Mensajes legibles sin rutas ni bytes del archivo rechazado.

La UI obtiene el original verificado, crea una URL Blob para el visor nativo del navegador y la revoca al salir. Permite descargarlo con su nombre original y muestra el SHA-256. Si el navegador no muestra PDF integrado, la descarga sigue disponible. El hash demuestra coincidencia con lo registrado, no autenticidad del emisor ni validez metrológica del certificado.

## Evidencia del 02/11/2026

[Resumen](../verification/document-original-2026-11-02.json): 282 pruebas backend/BI correctas en Docker/Python 3.11/PostgreSQL 17, incluidas 12 nuevas sobre bytes, hashes, estados, descarga, 404, manipulación, rutas externas/symlink y nombre/cabeceras. Build frontend Node 20/Vite correcto con dependencias de imagen existente, no instalación limpia.

Chromium contra API/PostgreSQL/RAW reales desechables: siete controles correctos, visor nativo cargado e imagen del certificado inspeccionada, descarga con nombre y hash idénticos, enlaces desde ficha/revisión, recarga, móvil 390 px sin overflow y errores de ausencia/manipulación/ID desconocido sin errores JS. Las pruebas negativas modifican solo PDFs sintéticos de ensayo y restauran bytes; los originales normales siguen siendo de lectura. Hubo intentos de manipulación fallidos por permisos de los fixtures inmutables: se habilitó escritura únicamente en esos fixtures para ejecutar el control negativo; no se cambió la política de producción.

Límites: el despliegue debe conservar RAW y configurar su raíz correctamente; archivos históricos fuera de esa raíz quedan indisponibles, sin moverlos automáticamente. La respuesta se mantiene en memoria durante lectura/verificación y la UI carga el blob completo; no se añade streaming/range. No cambia el modelo de acceso de la API actual ni añade autenticación. No completa TD-02/03 (materialización/estados) ni selecciona automáticamente el certificado vigente. No es estudio humano EXP-07.
