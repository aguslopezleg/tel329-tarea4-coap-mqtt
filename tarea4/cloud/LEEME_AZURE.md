# Continuar la actividad 4 con Azure

**Estado: ejecutado y verificado.** Diez lecturas del mote Contiki-NG llegaron a Azure IoT Hub y fueron recibidas por el consumidor. Ver `results/azure/verification.txt`, `readings.csv`, `middleware.log` y `subscriber.log`. Hub: `tel329-t4-alopez-20261112`, Brazil South, F1 Free; dispositivo `contiki-ng-01`. El control local anterior se conserva aparte.

## Configuración para repetir en otra máquina

1. Acceso a una suscripción de Azure y un IoT Hub existente o nuevo. No es necesario que la cuenta sea personal si la universidad proporciona acceso.
2. Un dispositivo registrado, por ejemplo `contiki-ng-01`, con autenticación simétrica. Su cadena `HostName=...;DeviceId=...;SharedAccessKey=...` se usa exclusivamente en el middleware.
3. La cadena del endpoint integrado compatible con Event Hubs: `Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=...`. Se utiliza en el suscriptor. Una cadena de dispositivo no puede sustituirla.
4. Acceso IPv6 desde el proceso middleware a la red de Cooja mediante el border router y `tunslip6`. En Docker, ejecutar el middleware en el mismo contenedor o espacio de red que el túnel. Un proceso en macOS no ve automáticamente la interfaz `tun0` del contenedor.

## Ejecución

Con Node.js 22 o posterior:

```bash
cd tarea4/cloud
npm ci
cp .env.example .env
# Completar .env localmente; no compartirlo.
node --env-file=.env subscriber.cjs
# En otra terminal, después de iniciar sensor/router y comprobar conectividad:
node --env-file=.env middleware.cjs
```

El suscriptor comienza desde su instante de arranque; iniciarlo antes que el middleware. El middleware lee cada tres segundos, verifica el JSON y envía un mensaje con temperatura, humedad, identidad, secuencia y fecha. `temperatureAlert` vale `true` solo cuando la temperatura supera 30 °C. El SDK MQTT de Azure usa el transporte seguro correspondiente a IoT Hub.

Para la prueba local, dejar vacía la cadena de dispositivo y definir `LOCAL_OUTPUT` (exactamente un destino puede estar activo). El script automático ya ejecuta este modo sin dependencias Azure.

## Evidencias de la ejecución

- La captura del portal se conserva solo localmente y se excluye de esta edición pública porque contiene datos de la cuenta. El estado técnico del recurso está resumido en el informe.
- `results/azure/middleware.log`: diez envíos confirmados con `mode: azure`.
- `results/azure/subscriber.log`: diez eventos `AZURE_RECEIVED` con identidad y secuencia verificadas.
- El informe ya incorpora las evidencias 4.a, 4.b y 4.c. El código se publica en https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt, según pide el enunciado.

Documentación: [endpoint integrado](https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-endpoints) y [SDK Event Hubs](https://learn.microsoft.com/en-us/javascript/api/overview/azure/event-hubs-readme?view=azure-node-latest).

## Ejecución automática en Docker

Desde el directorio que contiene `tarea4` y `vendor`: ejecutar `bash tarea4/scripts/run_azure.sh` y luego `python3 tarea4/scripts/check_azure.py`. Los procesos Node.js 22 comparten el espacio de red de la simulación para acceder a IPv6. El archivo `.env` no debe definir LOCAL_OUTPUT durante la ejecución Azure. La prueba tiene LIMIT=10 y termina automáticamente.

El registro opcional `register-device.cjs` utiliza la directiva existente registryReadWrite; la telemetría usa la clave exclusiva del dispositivo y el consumidor la directiva service. El portal presentó un error en la vista Dispositivos; el registro por SDK oficial y la conexión real del dispositivo quedaron verificados.
