#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
# .env contiene claves locales y se excluye de Git/ZIP. Completar siguiendo LEEME_AZURE.
test -f tarea4/cloud/.env
r=tarea4/results/azure
mkdir -p "$r"
cleanup() {
 docker stop tel329-azure-subscriber >/dev/null 2>&1 || true
 docker stop tel329-azure-wsn >/dev/null 2>&1 || true
}
trap cleanup EXIT
# Confirmar que no hay una ejecución anterior con estos nombres antes de iniciar.
docker run -d --rm --name tel329-azure-wsn --cap-add NET_ADMIN --device /dev/net/tun -v "$PWD:/work" tel329-tarea4:1 bash /work/tarea4/scripts/run_azure_inside.sh > "$r/wsn-container.txt"
for i in $(seq 1 180);do
 if docker exec tel329-azure-wsn ip link show tun0 >/dev/null 2>&1;then break;fi
 sleep 1
done
# El consumidor empieza antes que el middleware y comparte la red del túnel.
docker run -d --rm --name tel329-azure-subscriber --network container:tel329-azure-wsn -v "$PWD:/work" --env-file tarea4/cloud/.env node:22-bullseye-slim sh -c 'node /work/tarea4/cloud/subscriber.cjs > /work/tarea4/results/azure/subscriber.log 2>&1' > "$r/subscriber-container.txt"
# Esperar formación RPL y arranque del consumidor.
sleep 65
docker run --rm --network container:tel329-azure-wsn -v "$PWD:/work" --env-file tarea4/cloud/.env -e LIMIT=10 -e INTERVAL_MS=3000 node:22-bullseye-slim node /work/tarea4/cloud/middleware.cjs > "$r/middleware.log" 2>&1
sleep 8
# Dejar terminar la simulación para conservar TEST OK y cierre normal de la captura.
docker wait tel329-azure-wsn > "$r/wsn-exit.txt"
