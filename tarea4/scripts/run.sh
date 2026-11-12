#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tarea4/scripts/generate_simulations.py
for scenario in "${@:-coap mqtt http}";do
 for one in $scenario;do
  docker run --rm --cap-add NET_ADMIN --device /dev/net/tun -v "$PWD:/work" tel329-tarea4:1 bash /work/tarea4/scripts/run_inside.sh "$one"
 done
done
