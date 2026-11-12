# Fuentes y versiones

Contiki-NG release/v5.1, commit `2b87baf3ebdde3c8e37ca791d2bc84bfd76c49a4`.
Cooja, commit `cc31dbd202f6ea9cf82f83aab240a4074eae8af9`.

Las aplicaciones de firmware de esta entrega utilizan las APIs de CoAP, MQTT, TCP socket y RPL border router de esos fuentes. El paquete no redistribuye el árbol completo de Contiki-NG. `setup.sh` lo obtiene desde su repositorio original con sus licencias.

- https://github.com/contiki-ng/contiki-ng
- https://github.com/contiki-ng/cooja
- https://www.rfc-editor.org/rfc/rfc7252
- https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html
- https://mosquitto.org/
- https://docs.contiki-ng.org/en/master/doc/tutorials/Cooja-simulating-a-border-router.html
- https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-endpoints
- https://learn.microsoft.com/en-us/javascript/api/overview/azure/event-hubs-readme?view=azure-node-latest

SDKs Azure: versiones exactas en `cloud/package-lock.json`; conexión real con Azure IoT Hub verificada con diez lecturas, documentada en results/azure/.
