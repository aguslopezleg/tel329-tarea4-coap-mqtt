/* Cinco instancias notifican un unico recurso: POST /temperature, CON. */
#include "contiki.h"
#include "contiki-net.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "net/routing/routing.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <stdio.h>
#include <string.h>
#include "capture.h"
PROCESS(sensor_process, "TEL329 CoAP temperature");
AUTOSTART_PROCESSES(&sensor_process);
static struct etimer timer;
static unsigned seq;
static clock_time_t started;
static char payload[80];
static void response(coap_message_t *r) {
 if(r) printf("COAP_ACK node=%u seq=%u code=%u rtt_ticks=%lu\n", node_id, seq, r->code, (unsigned long)(clock_time()-started));
 else printf("COAP_TIMEOUT node=%u seq=%u\n", node_id, seq);
}
PROCESS_THREAD(sensor_process, ev, data) {
 static coap_endpoint_t endpoint;
 static coap_message_t request[1];
 static uint8_t token[2];
 PROCESS_BEGIN();
 netstack_ip_packet_processor_add(&capture);
 coap_endpoint_parse("coap://[fd00::1]", strlen("coap://[fd00::1]"), &endpoint);
 printf("CONFIG node=%u clock_second=%lu\n", node_id,(unsigned long)CLOCK_SECOND);
 etimer_set(&timer, (60+node_id)*CLOCK_SECOND);
 PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
 while(1) {
  if(NETSTACK_ROUTING.node_is_reachable()) {
   seq++;
   snprintf(payload,sizeof(payload),"{\"node\":%u,\"seq\":%u,\"temp\":%u}",node_id,seq,15+random_rand()%25);
   coap_init_message(request,COAP_TYPE_CON,COAP_POST,0);
   token[0]=node_id; token[1]=seq;
   coap_set_token(request,token,2);
   coap_set_header_uri_path(request,"temperature");
   coap_set_header_content_format(request,APPLICATION_JSON);
   coap_set_payload(request,(uint8_t *)payload,strlen(payload));
   started=clock_time();
   printf("COAP_SEND node=%u seq=%u payload=%s\n",node_id,seq,payload);
   COAP_BLOCKING_REQUEST(&endpoint,request,response);
  }
  etimer_set(&timer,10*CLOCK_SECOND);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
 }
 PROCESS_END();
}
