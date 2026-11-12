# TEL329 - Tarea 4: CoAP, MQTT y Azure IoT Hub

**Integrantes:** Agustín López, Sebastián Romero y Óscar Carrasco.

Implementación académica en Contiki-NG/Cooja de redes RPL Lite con cinco sensores, captura de tráfico y medición de tiempos de respuesta. Incluye la integración real de un sensor HTTP de Contiki-NG con Azure IoT Hub y un consumidor de Event Hubs.

- [Informe PDF (8 páginas)](tarea4/output/TEL329_Tarea4_Informe.pdf)
- [Informe en Markdown](tarea4/Informe.md)
- [Entrega completa ZIP](TEL329_Tarea4_Entrega_Completa.zip)
- [Instrucciones de ejecución](tarea4/README.md)
- [Firmware C](tarea4/firmware)
- [Simulaciones Cooja](tarea4/simulations)
- [Resultados y capturas PCAP](tarea4/results)

## Resultados verificados

- CoAP: 90 mensajes confirmados, media RTT 124,31 ms.
- MQTT QoS 1: 85 publicaciones confirmadas, media RTT 130,41 ms.
- Azure IoT Hub: 10 lecturas enviadas desde el mote simulado y recibidas desde la nube; identidad, secuencia, temperatura, humedad y alerta verificadas.

Las lecturas son sintéticas, generadas por el firmware. Las mediciones corresponden a una topología y semilla; no establecen superioridad general entre protocolos.

El Hub utilizado pertenece al nivel F1 Free. Las claves de Azure y las dependencias instaladas se excluyen de la entrega. Las instrucciones indican cómo configurar credenciales propias para reproducir la prueba.
