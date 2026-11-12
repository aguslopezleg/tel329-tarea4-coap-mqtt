# TEL329 - Tarea 4: CoAP y MQTT

Entrega con firmware, simulaciones Cooja, registros originales, capturas PCAP, análisis y un informe PDF/Markdown. Las actividades 1-3 se ejecutaron sobre Contiki-NG. La actividad 4 se ejecutó con un sensor HTTP real de Contiki-NG, middleware y Azure IoT Hub F1: diez lecturas enviadas y recibidas de extremo a extremo. Se conserva además el control con sumidero local.

## Contenido

- `Informe.md` y `output/TEL329_Tarea4_Informe.pdf`: informe.
- `firmware/`: raíz RPL Lite, sensores CoAP, MQTT y HTTP, configuración y captura pasiva IPv6.
- `simulations/`: tres escenarios Cooja y observador de radio.
- `results/`: registros originales, capturas y tiempos de respuesta. `nodeN.pcap` se observa en el extremo N; `radio.pcap` contiene las transmisiones IEEE 802.15.4; `tunnel.pcap` se capturó con tcpdump en el anfitrión Linux.
- `scripts/`: preparación, simulación, correlación y generación del informe.
- `results/azure/`: registros del envío real, consumidor y verificación de diez lecturas.
- `cloud/`: middleware y consumidor Azure/local, pruebas y archivo de dependencias fijadas. Ver `LEEME_AZURE.md`.
- `references/`: enunciado original y referencias de versiones.

## Reproducir desde el ZIP

Extraer la carpeta `tarea4` en un directorio con espacio para Contiki-NG. El script creará `vendor` como carpeta hermana; no requiere los archivos de la tarea 3. Se necesitan Docker Desktop en ejecución, Git y Python 3. Node 22 solo es necesario fuera del contenedor para las pruebas y el modo Azure.

```bash
bash tarea4/scripts/setup.sh
bash tarea4/scripts/run.sh coap mqtt http
# Desde el directorio que contiene tarea4 y vendor:
docker run --rm -v "$PWD:/work" tel329-tarea4:1 python3 /work/tarea4/scripts/analyze.py
python3 tarea4/scripts/verify_delivery.py
python3 tarea4/scripts/check_cloud.py
node --test tarea4/cloud/test.cjs
python3 tarea4/scripts/build_report.py
```

La generación del PDF requiere `reportlab` y la figura requiere `matplotlib` (`python3 -m pip install reportlab matplotlib`). El análisis utiliza tshark del contenedor. Las simulaciones CoAP/MQTT duran 240 segundos; la prueba HTTP dura 120 segundos de tiempo simulado con velocidad 1:1 y necesita algunos segundos adicionales para compilar. No ejecutar dos escenarios simultáneos contra la misma carpeta de firmware. Para renovar resultados, conservar una copia previa o borrar la carpeta del escenario: el sumidero local se reinicia automáticamente.

En Windows ejecutar los scripts en WSL2/Linux con Docker. El contenedor usa `--cap-add NET_ADMIN --device /dev/net/tun` exclusivamente para crear el túnel virtual; no usa `--privileged`. El broker anónimo de laboratorio no se publica hacia Internet.

## Versiones y límites

Contiki-NG release/v5.1: `2b87baf3ebdde3c8e37ca791d2bc84bfd76c49a4`. Cooja: `cc31dbd202f6ea9cf82f83aab240a4074eae8af9`. Java 21, Linux AArch64 sobre Docker/macOS. El script adapta `cooja.ld` de `INSERT BEFORE .lbss` a `INSERT AFTER .bss`, necesario en GNU ld/AArch64; no altera RPL ni los protocolos. Las herramientas concretas de ejecución se registran en `results/environment.txt`.

Semilla 1, una raíz y cinco sensores, CSMA, UDGM, alcance 50 m/interferencia 100 m. Coordenadas en el generador. Una sola semilla no permite generalizar superioridad estadística entre protocolos. La captura IPv6 precede a la transmisión de radio y sigue a la recepción: incluye colas, multihop y procesamiento del anfitrión. La resolución del log de aplicación es 1 ms. No confundir PUBACK del broker con recepción de la aplicación suscriptora.

La adaptación CoAP usa notificaciones activas POST CON hacia `/temperature`; no implementa Observe. MQTT usa un solo tema `tel329/temperature`, versión 3.1.1 y QoS 1. Ambas transportan exclusivamente temperatura como magnitud sensada; identidad y secuencia son metadatos. TCP/MQTT se establece antes de medir los intercambios de publicación.

## Repetir la integración Azure

El Hub `tel329-t4-alopez-20261112` está activo en Brazil South, nivel F1 Free (el portal mostró USD 0/mes). El dispositivo es `contiki-ng-01`. Las claves solo están en `cloud/.env` local, excluido de Git/ZIP. En otra máquina completar ese archivo siguiendo `cloud/LEEME_AZURE.md`. El nodo Cooja y los procesos de Node.js 22 comparten la red del túnel:

```bash
bash tarea4/scripts/run_azure.sh
python3 tarea4/scripts/check_azure.py
```

La simulación Azure dura 300 s. No se requiere un broker ni un Event Hubs independiente de pago. El script usa las imágenes `tel329-tarea4:1` y `node:22-bullseye-slim`. No ejecutar al mismo tiempo que otro escenario sobre el mismo firmware.

## Repositorio público

La adaptación, el informe y las evidencias están publicados en [https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt](https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt). Las credenciales de Azure y las dependencias instaladas no se incluyen en el repositorio ni en el ZIP.

La captura del portal con datos personales se excluye de la edición pública, al igual que las credenciales. Las evidencias técnicas de la integración Azure permanecen incluidas.
