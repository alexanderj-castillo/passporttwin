# Sesión: 2026-11-08 · Pau/Codex · Claridad de la revisión documental

- Rama feature/claridad-revision-documental desde main 52ea913. Mejora de UI-05 en el entorno aislado ptwin-ensayo.
- Se muestran etiquetas en español para los campos del certificado y se conserva la distinción entre valor original y revisado. Las acciones de validar e incorporar se presentan en el mismo panel según el estado del documento.
- El estado final indica Incorporado al historial, con confirmación única, campos de solo lectura y enlace al pasaporte.
- npm run build y git diff --check correctos. Pau comprobó en navegador el documento sintético 21: subida, procesado, corrección, validación, incorporación y recarga con el estado final visible.
- Pendientes: publicación, revisión y comprobación completa de teclado y móvil. El cambio es de presentación en frontend.
