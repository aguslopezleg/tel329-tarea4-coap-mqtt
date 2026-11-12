/* El modulo rpl-border-router inicia RPL Lite al recibir el prefijo por SLIP. */
#include "contiki.h"
#include <stdio.h>
PROCESS(root_process, "TEL329 RPL Lite border router");
AUTOSTART_PROCESSES(&root_process);
PROCESS_THREAD(root_process, ev, data) {
 PROCESS_BEGIN();
 printf("ROOT RPL-Lite SLIP ready\n");
 PROCESS_END();
}
