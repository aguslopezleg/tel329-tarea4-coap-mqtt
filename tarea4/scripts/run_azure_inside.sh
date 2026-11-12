#!/usr/bin/env bash
set -euo pipefail
cd /work
r=/work/tarea4/results/azure
mkdir -p "$r"
cleanup() { jobs -pr | xargs -r kill 2>/dev/null || true; }
trap cleanup EXIT
make -C vendor/contiki-ng/tools/serial-io tunslip6 > "$r/tunslip-build.log" 2>&1
java --enable-preview --enable-native-access=ALL-UNNAMED -XX:-UseCompressedOops -XX:-UseCompressedClassPointers -jar vendor/contiki-ng/tools/cooja/build/libs/cooja.jar --no-gui --contiki=/work/vendor/contiki-ng "--logdir=$r" /work/tarea4/simulations/azure.csc > "$r/cooja-console.log" 2>&1 &
cooja=$!
for i in $(seq 1 120);do
 if ss -ltn | grep -q ':60001';then break;fi
 if ! kill -0 "$cooja" 2>/dev/null;then cat "$r/cooja-console.log";exit 1;fi
 sleep 1
done
vendor/contiki-ng/tools/serial-io/tunslip6 -a 127.0.0.1 -p 60001 fd00::1/64 > "$r/tunslip.log" 2>&1 &
for i in $(seq 1 30);do ip link show tun0 >/dev/null 2>&1 && break;sleep 1;done
ip -6 addr show > "$r/interfaces.txt"
tcpdump -U -i tun0 -w "$r/tunnel.pcap" > "$r/tcpdump.log" 2>&1 &
wait "$cooja"
