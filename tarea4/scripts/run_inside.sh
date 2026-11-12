#!/usr/bin/env bash
set -euo pipefail
cd /work
scenario=${1:-coap}
r=/work/tarea4/results/$scenario
mkdir -p "$r"
cleanup() { jobs -pr | xargs -r kill 2>/dev/null || true; }
trap cleanup EXIT
make -C vendor/contiki-ng/tools/serial-io tunslip6 > "$r/tunslip-build.log" 2>&1
java --enable-preview --enable-native-access=ALL-UNNAMED -XX:-UseCompressedOops -XX:-UseCompressedClassPointers -jar vendor/contiki-ng/tools/cooja/build/libs/cooja.jar --no-gui --contiki=/work/vendor/contiki-ng "--logdir=$r" "/work/tarea4/simulations/$scenario.csc" > "$r/cooja-console.log" 2>&1 &
cooja=$!
# Wait for the serial server, without consuming its one client connection.
for i in $(seq 1 120); do
 if ss -ltn | grep -q ':60001'; then break; fi
 if ! kill -0 "$cooja" 2>/dev/null; then cat "$r/cooja-console.log";exit 1;fi
 sleep 1
done
vendor/contiki-ng/tools/serial-io/tunslip6 -a 127.0.0.1 -p 60001 fd00::1/64 > "$r/tunslip.log" 2>&1 &
for i in $(seq 1 30); do ip link show tun0 >/dev/null 2>&1 && break;sleep 1;done
ip -6 addr show > "$r/interfaces.txt"
tcpdump -U -i tun0 -w "$r/tunnel.pcap" > "$r/tcpdump.log" 2>&1 &
if [ "$scenario" = coap ];then
 python3 -u tarea4/scripts/coap_server.py > "$r/server.log" 2>&1 &
elif [ "$scenario" = mqtt ];then
 printf 'listener 1883\nallow_anonymous true\n' > /tmp/tel329-mosquitto.conf
 mosquitto -c /tmp/tel329-mosquitto.conf -v > "$r/broker.log" 2>&1 &
 sleep 1
 mosquitto_sub -h ::1 -t tel329/temperature -q 1 -v > "$r/subscriber.log" 2>&1 &
else
 # HTTP sensor at node 2, accessed over real simulated IPv6 + TCP.
 sleep 65
 : > "$r/local-cloud.jsonl"
 SENSOR_URL='http://[fd00::202:2:2:2]/' LOCAL_OUTPUT="$r/local-cloud.jsonl" LIMIT=10 INTERVAL_MS=3000 node tarea4/cloud/middleware.cjs > "$r/middleware.log" 2>&1
 node tarea4/cloud/subscriber.cjs --local "$r/local-cloud.jsonl" > "$r/subscriber.log" 2>&1
fi
wait "$cooja"
