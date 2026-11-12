/* HTTP/1.1 JSON real sobre TCP de Contiki-NG. Una conexion simultanea. */
#include "contiki.h"
#include "contiki-net.h"
#include "net/ipv6/tcp-socket.h"
#include "lib/random.h"
#include "sys/node-id.h"
#include <stdio.h>
#include <string.h>
PROCESS(sensor_process,"TEL329 Websense JSON");
AUTOSTART_PROCESSES(&sensor_process);
static struct tcp_socket sock;
static uint8_t input[384], output[384];
static char header[384];
static unsigned seq;
static uint8_t answered;
static int receive(struct tcp_socket *s,void *p,const uint8_t *d,int n) {
 char body[96];int len,temp,hum;
 if(answered) return 0;
 /* tcp-socket retains partial input until a complete HTTP header arrives. */
 int complete=0,i;
 for(i=3;i<n;i++) if(d[i-3]=='\r' && d[i-2]=='\n' && d[i-1]=='\r' && d[i]=='\n') {complete=1;break;}
 if(!complete) return n;
 answered=1;
 if(n<6 || memcmp(d,"GET / ",6)!=0) {
  tcp_socket_send_str(s,"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n");return 0;
 }
 temp=15+random_rand()%25;hum=80+random_rand()%10;
 snprintf(body,sizeof(body),"{\"node\":%u,\"seq\":%u,\"temp\":%d,\"hum\":%d}",node_id,++seq,temp,hum);
 len=snprintf(header,sizeof(header),"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: %u\r\nConnection: close\r\n\r\n%s",(unsigned)strlen(body),body);
 tcp_socket_send(s,(uint8_t *)header,len);
 printf("HTTP_SENSOR payload=%s\n",body);
 return 0;
}
static void event(struct tcp_socket *s,void *p,tcp_socket_event_t ev) {
 if(ev==TCP_SOCKET_CONNECTED) answered=0;
 if(ev==TCP_SOCKET_DATA_SENT) tcp_socket_close(s);
}
PROCESS_THREAD(sensor_process,ev,data) {
 PROCESS_BEGIN();
 tcp_socket_register(&sock,NULL,input,sizeof(input),output,sizeof(output),receive,event);
 tcp_socket_listen(&sock,80);
 printf("HTTP_READY node=%u port=80\n",node_id);
 PROCESS_END();
}
