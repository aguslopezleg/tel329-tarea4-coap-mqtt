/* TEL329: captura pasiva en el limite IPv6, sin alterar paquetes. */
#ifndef TEL329_CAPTURE_H
#define TEL329_CAPTURE_H
#include "net/netstack.h"
#include "net/ipv6/uip.h"
static void capture_packet(const char *dir) {
  unsigned i;
  printf("IPCAP dir=%s ticks=%lu hex=", dir, (unsigned long)clock_time());
  for(i = 0; i < uip_len; i++) printf("%02x", uip_buf[i]);
  printf("\n");
}
static enum netstack_ip_action capture_in(void) {
  capture_packet("RX"); return NETSTACK_IP_PROCESS;
}
static enum netstack_ip_action capture_out(const linkaddr_t *dest) {
  capture_packet("TX"); return NETSTACK_IP_PROCESS;
}
static struct netstack_ip_packet_processor capture = {NULL, capture_in, capture_out};
#endif
