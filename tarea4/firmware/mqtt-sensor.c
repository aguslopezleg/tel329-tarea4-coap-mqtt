/* MQTT 3.1.1, QoS 1; un unico tema para las cinco instancias. */
#include "contiki.h"
#include "contiki-net.h"
#include "mqtt.h"
#include "net/routing/routing.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <stdio.h>
#include "capture.h"
PROCESS(sensor_process,"TEL329 MQTT temperature");
AUTOSTART_PROCESSES(&sensor_process);
static struct mqtt_connection conn;
static struct etimer timer;
static char client_id[24], payload[80];
static char topic[]="tel329/temperature";
static uint16_t mid;
static unsigned seq;
static clock_time_t started;
static uint8_t waiting;
static void event(struct mqtt_connection *c,mqtt_event_t ev,void *data) {
 if(ev==MQTT_EVENT_CONNECTED) printf("MQTT_CONNECTED node=%u\n",node_id);
 else if(ev==MQTT_EVENT_DISCONNECTED) {waiting=0;printf("MQTT_DISCONNECTED node=%u\n",node_id);}
 else if(ev==MQTT_EVENT_PUBACK) {
  printf("MQTT_ACK node=%u seq=%u mid=%u rtt_ticks=%lu\n",node_id,seq,mid,(unsigned long)(clock_time()-started));waiting=0;
 }
}
PROCESS_THREAD(sensor_process,ev,data) {
 PROCESS_BEGIN();
 netstack_ip_packet_processor_add(&capture);
 snprintf(client_id,sizeof(client_id),"tel329-node-%u",node_id);
 mqtt_register(&conn,&sensor_process,client_id,event,128);
 conn.auto_reconnect=0;
 printf("CONFIG node=%u clock_second=%lu\n",node_id,(unsigned long)CLOCK_SECOND);
 etimer_set(&timer,(60+node_id)*CLOCK_SECOND);
 PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
 while(1) {
  if(NETSTACK_ROUTING.node_is_reachable()) {
   if(!mqtt_connected(&conn)) {
    if(conn.state==MQTT_CONN_STATE_NOT_CONNECTED || conn.state==MQTT_CONN_STATE_ERROR)
     mqtt_connect(&conn,"fd00::1",1883,60,MQTT_CLEAN_SESSION_ON);
   } else if(mqtt_ready(&conn) && !waiting) {
    seq++;
    snprintf(payload,sizeof(payload),"{\"node\":%u,\"seq\":%u,\"temp\":%u}",node_id,seq,15+random_rand()%25);
    started=clock_time();
    if(mqtt_publish(&conn,&mid,topic,(uint8_t *)payload,strlen(payload),MQTT_QOS_LEVEL_1,MQTT_RETAIN_OFF)==MQTT_STATUS_OK) {
     waiting=1; printf("MQTT_SEND node=%u seq=%u mid=%u payload=%s\n",node_id,seq,mid,payload);
    }
   }
  }
  etimer_set(&timer,10*CLOCK_SECOND);
  PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
 }
 PROCESS_END();
}
