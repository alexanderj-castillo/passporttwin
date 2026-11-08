# Sesión: 2026-11-08 · Pau/Codex · Rediseño del pasaporte y navegación común

- Rama feature/rediseno-pasaporte desde main afbd281. Trabajo de interfaz sobre el entorno de ensayo.
- Pasaporte: identificación visible, navegación por secciones con recuentos, Health Score semicircular, tres horizontes de riesgo, estado y acción de calibración, y detalle organizado por temas.
- Inventario, Revisión documental, Auditoría y visor de originales comparten la navegación y el estilo del pasaporte. Se mantienen las rutas y los flujos de revisión existentes.
- Compilación Vite y git diff --check correctos. Comprobación de carga con Chromium y datos sintéticos en Inventario, Revisión documental, Auditoría, visor de originales y Pasaporte a 1280 y 390 px. Sin desbordamiento horizontal de página ni excepciones JavaScript detectadas.
- También se revisó el resumen a 390 px en Brave con Pau. La comprobación de Chromium fue de lectura y no repitió la incorporación de certificados. El acceso QR desde un teléfono sigue pendiente.
- Cortes de color 50 y 75 provisionales. La foto y el plano muestran estados sin datos y quedan pendientes de asociar a activos reales.
