# Sesión 2026-11-10 · Pau/Codex · Primera carga de flota sintética

- Rama feature/flota-sintetica-piloto desde main efe59b8. Carga aditiva en ptwin-ensayo con referencia 2026-11-10.
- PT-101: ocho calibraciones, un certificado, riesgo 0/0/0 % y Health Score 100. PT-102: ocho calibraciones, un certificado, riesgo 31,932/94,563/99,947 % y Health Score 70. PH-304: cero calibraciones y documentos, riesgo no estimable por historial insuficiente y Health Score sin cálculo.
- Dos ejecuciones en Docker. La segunda conservó las tres identidades y la API confirmó los recuentos 8/8/0 y 1/1/0. Los dos originales respondieron HTTP 200 en la comprobación inicial.
- Los nombres técnicos y las etiquetas se registran en la auditoría de la carga. Sigue pendiente representarlos como campos propios del instrumento y ampliar al resto del catálogo. La carpeta original no recibió esta carga.
- Identidad técnica: se añadieron columnas opcionales technical_name y plant_tag. La migración aditiva instrument_identity.sql se aplica con tools/dev.py start. En instalaciones existentes que arranquen directamente con Compose, aplicarla antes de reiniciar el backend.
- La recarga rellenó los campos vacíos de los tres instrumentos sin cambiar sus resultados. La API confirmó los datos de PT-102 y valores nulos compatibles en un pasaporte anterior.
- Chromium verificó a 1280 y 390 px búsqueda por etiqueta, título técnico y modelo/serie separados. Build y sintaxis de Python correctos. La migración solo se ha aplicado al ensayo.
