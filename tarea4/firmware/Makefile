CONTIKI_PROJECT = coap-sensor mqtt-sensor http-sensor border-router
all: $(CONTIKI_PROJECT)
CONTIKI ?= ../../vendor/contiki-ng
include $(CONTIKI)/Makefile.dir-variables
MAKE_ROUTING = MAKE_ROUTING_RPL_LITE
MAKE_MAC = MAKE_MAC_CSMA
ifeq ($(APP),coap)
MODULES += $(CONTIKI_NG_APP_LAYER_DIR)/coap
endif
ifeq ($(APP),mqtt)
MODULES += $(CONTIKI_NG_APP_LAYER_DIR)/mqtt
endif
ifeq ($(APP),border)
MODULES += $(CONTIKI_NG_SERVICES_DIR)/rpl-border-router
endif
include $(CONTIKI)/Makefile.include
