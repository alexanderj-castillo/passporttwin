# EXP-06 · Recorrido AASX de la proyección MVP

Estado: herramienta implementada; ensayo técnico con datos sintéticos. No equivale a validación final ni certificación IDTA. PostgreSQL sigue siendo el estado canónico.

El recorrido usa el `AASBuilder` de producción sin modificar: proyección → BaSyx Java 1.4.0 vacío → normalización AAS v2 → SDK → paquete OPC AASX → lector SDK → REST PUT en un segundo BaSyx vacío → lectura y comparación. No se utiliza un endpoint nativo de importación AASX del servidor.

## Perfil y aceptación

Dos instrumentos sintéticos, uno con dos calibraciones y dos documentos aceptados (incluye Unicode) y otro con historiales vacíos. Se exige conservar el 100% de las entradas críticas en cada frontera: identidad shell/asset, referencias resolubles, identidad y semanticId de los cuatro submodelos, nombres de hijos y cada tipo/valor/datatype de Property o Collection. Los números double se comparan como decimales, sin tolerancia que oculte cambios; los strings se conservan exactamente. Tipos desconocidos se rechazan.

BaSyx devuelve el activo embebido y referencias compuestas. El adaptador separa el Asset y convierte las referencias a globales con los mismos identificadores; elimina el `parent` REST. Se comparan datos semánticos, no igualdad byte a byte del JSON REST. No se incluyen binarios PDF: se conservan sus referencias y hashes. Tampoco se demuestra conservar UUID público o unidad, que el builder actual no proyecta.

## Ejecución aislada

Desde la raíz, construir la herramienta opcional (no cambia requirements de backend):

```sh
docker build -f experiments/aasx/Dockerfile -t passporttwin-exp06-tool .
docker network create passporttwin-exp06
docker run -d --name exp06-source --network passporttwin-exp06 -e 'JAVA_TOOL_OPTIONS=-Xmx256m -XX:-UseContainerSupport' eclipsebasyx/aas-server:1.4.0
docker run -d --name exp06-target --network passporttwin-exp06 -e 'JAVA_TOOL_OPTIONS=-Xmx256m -XX:-UseContainerSupport' eclipsebasyx/aas-server:1.4.0
```

Esperar a que ambos respondan GET `/aasServer/shells` con `[]`. Ejecutar en una sola línea de PowerShell, en un checkout limpio; `results/exp06` debe ser nuevo y sus padres deben existir:

```powershell
docker run --rm --network passporttwin-exp06 -v "${PWD}:/repo:ro" -v "${PWD}/results:/results" passporttwin-exp06-tool --source-url http://exp06-source:4001/aasServer --target-url http://exp06-target:4001/aasServer --run-dir /results/exp06 --code-commit (git rev-parse HEAD)
```

Linux/macOS: sustituir `${PWD}` por `$(pwd)` y `(git rev-parse HEAD)` por `$(git rev-parse HEAD)`. El commit suministrado cuando falta Git queda identificado como no verificado; se registran además hashes del código ejecutado. No usar repositorios compartidos: el runner exige ambos vacíos, vuelve a comprobar el destino después de sembrar la fuente y nunca los reinicia. Para repetir, recrear únicamente estos contenedores desechables y elegir otro directorio. Limpiar los dos contenedores y su red al terminar.

El entorno opcional fija SDK 0.2.2 (AAS v2) y pip 24.0 por metadatos antiguos del SDK. Esta dependencia heredada queda aislada; no se instala en producción. Detrás de un proxy corporativo puede suministrarse el certificado mediante el secreto BuildKit `proxy_ca`, sin desactivar TLS.

`report.json` registra versión SDK/Python, commit, estado del árbol cuando Git está disponible, hashes, conteos y diferencias. Los `.aasx` quedan fuera de Git. Un fallo sale con código 2 y conserva artefactos parciales; no se declara PASS si no termina todo el recorrido. Las comprobaciones unitarias usan respuestas sintéticas; el ensayo entre servidores debe registrarse por separado.

```sh
PYTHONPATH=backend:experiments python -m pytest experiments/tests/test_exp06_aasx.py -q
```
