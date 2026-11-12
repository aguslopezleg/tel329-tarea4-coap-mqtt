#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
# La carpeta tarea4 y vendor quedan hermanas. No se incluye Contiki entero en el ZIP.
if [ ! -d vendor/contiki-ng/.git ];then
 git clone --depth 1 --branch release/v5.1 https://github.com/contiki-ng/contiki-ng.git vendor/contiki-ng
fi
test "$(git -C vendor/contiki-ng rev-parse HEAD)" = 2b87baf3ebdde3c8e37ca791d2bc84bfd76c49a4
git -C vendor/contiki-ng submodule update --init tools/cooja
python3 - <<'PY'
from pathlib import Path
p=Path('vendor/contiki-ng/arch/platform/cooja/cooja.ld')
p.write_text(p.read_text().replace('INSERT BEFORE .lbss;', 'INSERT AFTER .bss;'))
PY
docker build -t tel329-tarea4:1 -f tarea4/Dockerfile .
docker run --rm -v "$PWD:/work" -w /work/vendor/contiki-ng/tools/cooja tel329-tarea4:1 ./gradlew --no-daemon jar
