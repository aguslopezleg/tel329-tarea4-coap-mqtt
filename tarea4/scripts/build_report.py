from pathlib import Path
import json,csv,html,re,os,tempfile
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'tel329-tarea4-matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Preformatted,Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
R=Path(__file__).resolve().parents[1];O=R/'output';O.mkdir(exist_ok=True)
S=json.loads((R/'results/summary.json').read_text())
P=list(csv.DictReader((R/'results/responses.csv').open()))
H=[json.loads(x) for x in (R/'results/http/local-cloud.jsonl').read_text().splitlines()]
A=json.loads((R/'results/azure/summary.json').read_text())
# Figuras estaticas exportables con metricas y ejes explicitos.
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.4,2.3))
coords={1:(0,0),2:(35,0),3:(70,0),4:(105,0),5:(70,35),6:(105,35)}
for a,b in [(1,2),(2,3),(2,5),(3,4),(3,5),(3,6),(4,5),(4,6),(5,6)]:
 x,y=coords[a];xx,yy=coords[b]
 if (x-xx)**2+(y-yy)**2<=50**2:ax.plot([x,xx],[y,yy],color='#bac8cf',lw=1,zorder=1)
for n,(x,y) in coords.items():
 ax.scatter(x,y,s=470,color='#17334b' if n==1 else '#087f8c',zorder=2)
 ax.text(x,y,str(n),ha='center',va='center',color='white',weight='bold')
ax.text(0,-13,'Raíz / SLIP',ha='center',fontsize=9)
ax.set(xlabel='Posición x (m)',ylabel='Posición y (m)',title='Topología UDGM: enlaces geométricamente posibles (alcance 50 m)',xlim=(-20,125),ylim=(-22,55))
fig.tight_layout();fig.savefig(O/'topologia.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.4,2.7))
for j,(proto,color) in enumerate([('coap','#087f8c'),('mqtt','#b16b2e')]):
 vals=[[float(p['rtt_ms']) for p in P if p['protocol']==proto and int(p['node'])==n] for n in range(2,7)]
 bp=ax.boxplot(vals,positions=[n+(-.17 if j==0 else .17) for n in range(2,7)],widths=.26,patch_artist=True,manage_ticks=False)
 for box in bp['boxes']:box.set(facecolor=color,alpha=.65)
 ax.plot([],[],color=color,lw=6,label='CoAP CON' if proto=='coap' else 'MQTT QoS 1')
ax.set(xlabel='Nodo sensor',ylabel='Tiempo de confirmación RTT (ms)',xticks=range(2,7),title='Confirmaciones por nodo: todos los intercambios completados')
ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(O/'rtt.png',dpi=180);plt.close(fig)
styles=getSampleStyleSheet();navy=colors.HexColor('#17334b');teal=colors.HexColor('#087f8c');light=colors.HexColor('#eef3f6')
styles.add(ParagraphStyle(name='T',fontName='Helvetica-Bold',fontSize=25,leading=29,textColor=navy,spaceAfter=14))
styles.add(ParagraphStyle(name='H',fontName='Helvetica-Bold',fontSize=17,leading=21,textColor=navy,spaceAfter=12))
styles.add(ParagraphStyle(name='B',fontSize=10,leading=14,spaceAfter=9,textColor=navy))
styles.add(ParagraphStyle(name='C',fontSize=8,leading=11,spaceAfter=7,textColor=navy))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=7,leading=10,backColor=light,borderPadding=7,spaceBefore=7,spaceAfter=12))
story=[];md=[]
def title(t):story.append(Paragraph(html.escape(t),styles['T']));md.append('# '+t+'\n')
def heading(t):story.append(Paragraph(html.escape(t),styles['H']));md.append('## '+t+'\n')
def p(t):story.append(Paragraph(html.escape(t),styles['B']));md.append(t+'\n')
def code(t):story.append(Preformatted(t,styles['CodeCustom']));md.append('```text\n'+t+'\n```\n')
def image(name,w,h,caption):
 story.append(Image(str(O/name),width=w,height=h));story.append(Paragraph(html.escape(caption),styles['C']));md.append(f'![{caption}](output/{name})\n')
def table(rows,widths):
 t=Table([[Paragraph(html.escape(str(v)),styles['C']) for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,teal),('LINEBELOW',(0,1),(-1,-1),.3,colors.lightgrey),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.extend([t,Spacer(1,10)])
 md.append('| '+' | '.join(map(str,rows[0]))+' |\n| '+' | '.join('---' for _ in rows[0])+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows[1:])+'\n')
def page():story.append(PageBreak())
def f(x):return f'{x:.2f}'
def sample(proto,node,seq):return next(x for x in P if x['protocol']==proto and int(x['node'])==node and int(x['seq'])==seq)
c=S['coap']['overall'];m=S['mqtt']['overall']
title('Tarea 4: Mensajería CoAP y MQTT')
p('TEL329 - Redes de Sensores - 2026. Informe de implementación y mediciones. Fecha: 12 de noviembre de 2026.')
p('Se implementaron y ejecutaron las cuatro actividades. CoAP y MQTT se midieron en Contiki-NG/Cooja, y la actividad 4 se verificó con diez lecturas reales del sensor simulado enviadas a Azure IoT Hub y recibidas desde su endpoint integrado. Se conserva además una prueba local independiente. Las temperaturas y humedades son sintéticas, generadas por firmware de Contiki-NG.')
heading('1. Escenario experimental')
p('Se utilizó Contiki-NG release/v5.1, Cooja, Java 21 y Linux AArch64 en Docker. Cada escenario usa una raíz RPL Lite y cinco sensores (IDs 2 a 6), IPv6/6LoWPAN y MAC CSMA. La raíz conecta la WSN al anfitrión Linux por SLIP y tunslip6; el anfitrión tiene fd00::1 y ejecuta el servidor CoAP o el broker Mosquitto. Son seis motes, además del anfitrión de servicios.')
image('topologia.png',490,152,'Fuente: coordenadas de simulations/*.csc. Las líneas muestran alcance geométrico, no padres RPL fijos.')
p('La semilla es 1; cada simulación de comparación dura 240 s, a velocidad 1:1. UDGM utiliza 50 m de alcance, 100 m de interferencia y probabilidad de éxito configurada 1. Esto no elimina contención, colisiones ni retransmisiones. Se esperan 60 s antes de iniciar tráfico, con desfase por ID. La temperatura sintética es 15 + random_rand() % 25: enteros entre 15 y 39 °C. No proviene de un sensor físico.')
page();heading('2. Actividad 1: RPL Lite y CoAP')
p('Los cinco clientes ejecutan coap-sensor.c y notifican un único recurso mediante POST confirmable (CON) a coap://[fd00::1]/temperature. El mensaje JSON contiene temperatura y metadatos node/seq. Se eligió notificación activa mediante POST; no se implementó la extensión Observe ni una consulta GET periódica.')
code('coap_init_message(request, COAP_TYPE_CON, COAP_POST, 0);\ncoap_set_header_uri_path(request, "temperature");\ncoap_set_header_content_format(request, APPLICATION_JSON);\nCOAP_BLOCKING_REQUEST(&endpoint, request, response);')
p('El servidor aiocoap valida la lectura y devuelve 2.04 Changed con el mismo Message ID y token en el ACK. En el registro de Contiki aparece code=68, codificación binaria de 2.04. La confirmación se observa en la captura y en el callback del sensor. Después de la respuesta, el cliente espera 10 s para enviar otra lectura; por ello el intervalo entre envíos incluye el RTT.')
a=sample('coap',2,1)
code('Sensor 2, registro real:\nCOAP_SEND node=2 seq=1 payload={"node":2,"seq":1,"temp":20}\nCOAP_ACK node=2 seq=1 code=68 rtt_ticks='+a['app_rtt_ms']+'\n\nServidor: {"event":"COAP_RECEIVED","node":2,"seq":1,"temp":20}')
p(f'Se obtuvieron {S["coap"]["application_sent"]} notificaciones y {c["n"]} confirmaciones, con 18 intercambios por sensor y ningún intercambio sin respuesta en la captura analizada. El RTT medio fue {f(c["mean_ms"])} ms; mediana {f(c["median_ms"])} ms y percentil 95 {f(c["p95_ms"])} ms. Estos resultados corresponden al escenario y semilla indicados.')
p('Evidencias: results/coap/COOJA.testlog, server.log, node2.pcap a node6.pcap, radio.pcap, tunnel.pcap y responses.csv. La salida de terminal de Cooja finaliza con TEST OK. El código adaptado, Makefile y configuración se incluyen en firmware/.')
page();heading('3. Actividad 2: RPL Lite y MQTT')
p('Los cinco sensores ejecutan mqtt-sensor.c con el motor MQTT de Contiki-NG. Se conectan al broker Mosquitto 2.0.11 en [fd00::1]:1883 y publican exclusivamente en tel329/temperature, usando MQTT 3.1.1, QoS 1 y retain desactivado. Cada cliente tiene un identificador distinto: tel329-node-ID. La conexión TCP se mantiene abierta.')
code('mqtt_register(&conn, &sensor_process, client_id, event, 128);\nmqtt_connect(&conn, "fd00::1", 1883, 60, MQTT_CLEAN_SESSION_ON);\nmqtt_publish(&conn, &mid, topic, (uint8_t *)payload,\n             strlen(payload), MQTT_QOS_LEVEL_1, MQTT_RETAIN_OFF);')
p('Mosquitto recibe el PUBLISH y devuelve PUBACK con el identificador correspondiente. Un suscriptor independiente, mosquitto_sub, recibe el mismo tema y permite comprobar el comportamiento publicación/suscripción. El PUBACK confirma recepción por el broker; no demuestra por sí solo que la aplicación suscriptora haya procesado el dato.')
# Se extraen las primeras líneas reales, sin fabricar valores.
text=(R/'results/mqtt/COOJA.testlog').read_text();lines=[]
for tag in ['MQTT_CONNECTED node=2','MQTT_SEND node=2 seq=1 ','MQTT_ACK node=2 seq=1 ']:
 line=next(x.split('\t',2)[-1] for x in text.splitlines() if tag in x);lines.append(line)
code('\n'.join(lines)+'\nSuscriptor:\n'+(R/'results/mqtt/subscriber.log').read_text().splitlines()[0])
p(f'Se registraron {S["mqtt"]["application_sent"]} publicaciones y {m["n"]} PUBACK correlacionados. El RTT medio fue {f(m["mean_ms"])} ms; mediana {f(m["median_ms"])} ms y p95 {f(m["p95_ms"])} ms. Las conexiones se inician tras 60 s; la primera publicación ocurre en una iteración posterior. El establecimiento TCP/CONNECT queda en los PCAP, pero no se suma al RTT PUBLISH-PUBACK.')
p('Evidencias: results/mqtt/COOJA.testlog, broker.log, subscriber.log, nodeN.pcap, radio.pcap, tunnel.pcap y responses.csv. El laboratorio utiliza MQTT sin TLS y un broker anónimo dentro del contenedor. No se usa un broker simulado ni se reemplaza MQTT por UDP.')
page();heading('4. Actividad 3: captura y tiempos de respuesta')
p('Se capturaron tres niveles: transmisiones IEEE 802.15.4 mediante el observador de Cooja; paquetes IPv6 en cada sensor mediante un procesador pasivo de NETSTACK; y tráfico del túnel mediante tcpdump. Los bytes se conservan sin alterar. analyze.py exporta las capturas a PCAP y usa tshark para decodificar los protocolos. Los PCAP de sensores y radio tienen timestamps de simulación; el túnel usa el reloj real del contenedor.')
p('El RTT se calcula en el mismo sensor: t(ACK recibido) - t(CON enviado), o t(PUBACK recibido) - t(PUBLISH enviado). CoAP se correlaciona por Message ID y token; MQTT por flujo TCP e identificador de paquete. Se mide desde el primer envío y se conserva el número de solicitudes decodificadas; ese contador no equivale a retransmisiones TCP. Se excluyen paquetes de tránsito RPL con Segments Left mayor que cero. Los registros de aplicación verifican los RTT con una tolerancia de 2 ms; CLOCK_SECOND=1000.')
rows=[['Protocolo','n','Media ms','Mediana ms','p95 ms','Mín-max ms']]
for proto,label in [('coap','CoAP CON'),('mqtt','MQTT QoS 1')]:
 s=S[proto]['overall'];rows.append([label,s['n'],f(s['mean_ms']),f(s['median_ms']),f(s['p95_ms']),f(s['min_ms'])+'-'+f(s['max_ms'])])
table(rows,[88,32,70,77,63,160])
rows=[['Nodo','n CoAP','Media CoAP ms','n MQTT','Media MQTT ms']]
for n in range(2,7):
 a=S['coap']['per_node'][str(n)];b=S['mqtt']['per_node'][str(n)];rows.append([n,a['n'],f(a['mean_ms']),b['n'],f(b['mean_ms'])])
table(rows,[55,70,145,70,150])
image('rtt.png',490,178,'Fuente: results/responses.csv; 60-240 s de simulación, semilla 1. Cajas: cuartiles; línea: mediana; puntos: valores atípicos.')
page();heading('5. Muestra trazable y análisis')
p('La tabla presenta las secuencias 1 y 10 de cada nodo en cada protocolo, seleccionadas con una regla fija. Las estadísticas anteriores utilizan todos los intercambios completados, no solo esta muestra. Los CSV conservan los números de trama, instantes, identificadores y RTT para reproducir cada pareja en Wireshark.')
rows=[['Nodo','Secuencia','CoAP RTT ms','MQTT RTT ms']]
for n in range(2,7):
 for seq in [1,10]:rows.append([n,seq,f(float(sample('coap',n,seq)['rtt_ms'])),f(float(sample('mqtt',n,seq)['rtt_ms']))])
table(rows,[65,85,170,170])
diff=m['mean_ms']-c['mean_ms']
p(f'En esta ejecución, la diferencia de medias MQTT menos CoAP fue {f(diff)} ms. La dispersión por nodo muestra el efecto de los recorridos multihop y de la planificación CSMA. CoAP utiliza UDP y un ACK con respuesta; MQTT agrega TCP, su control de flujo y PUBACK. La captura incluye el procesamiento del servicio, el túnel y las colas, de modo que el tamaño de cabecera por sí solo no explica el resultado.')
p('En los dos escenarios, el registro RPL sitúa al nodo 2 a un salto de la raíz; 3 y 5 a dos saltos; 4 y 6 a tres saltos. La ruta concreta del nodo 6 cambia de padre entre escenarios. Por tanto, el mismo alcance geométrico no garantiza idénticos caminos ni condiciones de contención.')
p('No es una comparación de consultas idénticas: se mide confirmación de telemetría. CoAP 2.04 confirma el procesamiento del POST, mientras PUBACK confirma la aceptación por el broker. Las garantías y los destinatarios son distintos. Los motores de protocolo también consumen números aleatorios y generan tráfico de control diferente. El intervalo CoAP es 10 s después de cada respuesta; MQTT revisa su estado cada 10 s. Estas diferencias limitan la comparación.')
p('Una sola topología y semilla no permiten concluir que un protocolo sea universalmente más rápido. Tampoco equivalen a mediciones sobre hardware físico ni incluyen DTLS/TLS. Para generalizar habría que repetir con varias semillas, distancias, tasas de publicación y pérdidas, manteniendo explícita la métrica. Se incluyen los intercambios no emparejados en unmatched.json, aunque su número en esta ejecución puede ser cero.')
page();heading('6. Actividad 4: integración real con Azure')
p('Se creó el IoT Hub tel329-t4-alopez-20261112 en Brazil South, nivel F1 Free. El portal confirmó USD 0/mes y una cuota de 8.000 mensajes diarios. Se registró contiki-ng-01 con autenticación simétrica. No se contrató un nivel pagado ni se habilitaron complementos de pago.')
p('El escenario utiliza una raíz RPL Lite border router y un sensor HTTP de Contiki-NG (http-sensor.c). El middleware Node.js 22 consulta GET / en la dirección IPv6 del mote, recibe temperatura y humedad y las envía a Azure mediante MQTT/TLS. Un consumidor independiente usa EventHubConsumerClient y AMQP/TLS para leer el endpoint integrado compatible con Event Hubs.')
p('4.a - Resultado del middleware. Se confirmaron diez envíos con event=SENT y mode=azure. El middleware transforma temp/hum en temperature/humidity, conserva node/seq y agrega deviceId, sampledAt y temperatureAlert. Esta última propiedad vale true solo cuando la temperatura supera 30 °C. Las claves permanecen exclusivamente en .env local y no se incluyen en el ZIP.')
ex=A['first_sample'];b=ex['body'];sensor={'node':b['node'],'seq':b['seq'],'temp':b['temperature'],'hum':b['humidity']}
code('4.b - Respuesta real del mote:\n'+json.dumps(sensor,separators=(',',':'))+'\n\n4.a - Envío real a Azure:\n'+f'event=SENT, mode=azure, deviceId={b["deviceId"]}\nnode={b["node"]}, seq={b["seq"]}, temperature={b["temperature"]}\nhumidity={b["humidity"]}, temperatureAlert={ex["properties"]["temperatureAlert"]}\n\n4.c - Consumidor:\nevent=AZURE_RECEIVED, partition='+str(A['azure_first_event']['partition']))
p('4.b - Resultado del sensor. El mote entregó diez respuestas JSON por IPv6/TCP. La humedad se genera en el intervalo 80-89 % y la temperatura en 15-39 °C. Los registros HTTP_SENSOR de Cooja conservan las lecturas originales. No se sustituyó el mote por un generador de datos del anfitrión.')
p('4.c - Resultado del suscriptor. Se recibieron diez eventos únicos desde Azure, con event=AZURE_RECEIVED. check_azure.py compara todas las lecturas originales, los envíos y los eventos recibidos: coinciden identidad, secuencia, temperatura, humedad y alerta. También comprueba que iothub-connection-device-id coincide con contiki-ng-01, autenticado por el servicio.')
p('Evidencias: results/azure/COOJA.testlog, middleware.log, subscriber.log, tunnel.pcap, device-registration.log, readings.csv, summary.json y verification.txt. Las evidencias CoAP, MQTT y del control local se conservan en carpetas separadas. Las cuatro pruebas unitarias del middleware también fueron superadas.')
page();heading('7. Evidencia de Azure y lecturas recibidas')
table([['Propiedad del recurso','Valor verificado'],['IoT Hub','tel329-t4-alopez-20261112'],['Estado','Active'],['Nivel','F1 Free (USD 0/mes)'],['Región','Brazil South'],['Dispositivo','contiki-ng-01'],['Lecturas enviadas / recibidas','10 / 10']],[180,310])
p('Se omite la captura del portal en esta edición pública para proteger los datos de la cuenta. La configuración del recurso se comprobó en el portal; los resultados se acreditan mediante los registros originales del mote, middleware y consumidor de Azure.')
rows=[['Secuencia','Temperatura °C','Humedad %','Alerta >30 °C']]
for row in csv.DictReader((R/'results/azure/readings.csv').open()):
 rows.append([row['seq'],row['temperature'],row['humidity'],row['temperatureAlert']])
table(rows,[75,145,130,140])
p('La tabla deriva de los eventos recibidos desde Azure y se contrasta con el mote y el middleware. El suscriptor se inició antes del envío, leyendo desde su instante de arranque. Se utilizó la directiva service para el consumidor; la identidad de dispositivo se configuró mediante el SDK oficial azure-iothub porque la vista Dispositivos del portal devolvía un error. No se ampliaron permisos del usuario ni se deshabilitó TLS.')
p('La prueba local anterior también conservó diez lecturas idénticas entre sensor, archivo y consumidor. Esa prueba se mantiene como control adicional; la evidencia de cumplimiento de la nube es la ejecución real de results/azure/.')
page();heading('8. Reproducción, publicación y referencias')
p('El ZIP contiene firmware, simulaciones, scripts, PCAP, registros originales, datos procesados y este informe en PDF y Markdown. Los servicios y el túnel se ejecutan dentro del mismo contenedor Linux. setup.sh obtiene los commits fijados de Contiki-NG/Cooja y prepara el entorno; run.sh ejecuta los escenarios por separado. No se requieren los archivos de la tarea anterior.')
code('bash tarea4/scripts/setup.sh\nbash tarea4/scripts/run.sh coap mqtt http\ndocker run --rm -v "$PWD:/work" tel329-tarea4:1 \\\n  python3 /work/tarea4/scripts/analyze.py\npython3 tarea4/scripts/check_cloud.py\n# Con .env de Azure configurado:\nbash tarea4/scripts/run_azure.sh\npython3 tarea4/scripts/check_azure.py\nnode --test tarea4/cloud/test.cjs\npython3 tarea4/scripts/build_report.py')
p('La integración Azure quedó ejecutada y verificada. cloud/LEEME_AZURE.md documenta cómo repetirla con las credenciales locales. El Hub permanece disponible en el nivel F1 gratuito. La adaptación, el informe y las evidencias se publican en el repositorio público https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt, para cumplir el requisito del enunciado.')
p('Conclusión. CoAP y MQTT funcionaron sobre RPL Lite con cinco sensores, respaldados por capturas y tiempos correlacionados. La actividad 4 completó el recorrido sensor Contiki-NG, middleware, Azure IoT Hub y consumidor: diez lecturas fueron verificadas de extremo a extremo. El código y las evidencias se incluyen en el repositorio público de la entrega.')
refs=[('Repositorio público de esta entrega','https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt'),('Enunciado TEL329 Tarea 4, versión 1.0, 2026','references/TEL329-Tarea4-2026-v1.0.html'),('Contiki-NG release/v5.1 y fuentes de CoAP/MQTT','https://github.com/contiki-ng/contiki-ng/tree/2b87baf3ebdde3c8e37ca791d2bc84bfd76c49a4'),('Contiki-NG: Cooja, simulating a border router','https://docs.contiki-ng.org/en/master/doc/tutorials/Cooja-simulating-a-border-router.html'),('RFC 7252: CoAP, secciones 4 y 5','https://www.rfc-editor.org/rfc/rfc7252'),('OASIS MQTT 3.1.1, secciones 3.3 y 4.3.2','https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html'),('Microsoft Learn: endpoints de IoT Hub','https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-endpoints'),('Microsoft Learn: SDK Event Hubs JavaScript','https://learn.microsoft.com/en-us/javascript/api/overview/azure/event-hubs-readme?view=azure-node-latest')]
for label,url in refs:
 story.append(Paragraph(html.escape(label)+'<br/><font size="7">'+html.escape(url)+'</font>',styles['C']));md.append(f'- [{label}]({url})')
(R/'Informe.md').write_text('\n\n'.join(md)+'\n')
def footer(canvas,doc):
 canvas.setStrokeColor(teal);canvas.line(43,39,552,39);canvas.setFillColor(navy);canvas.setFont('Helvetica',8);canvas.drawString(43,26,'TEL329 - Tarea 4 | Resultados reales y alcance declarado');canvas.drawRightString(552,26,str(doc.page))
doc=SimpleDocTemplate(str(O/'TEL329_Tarea4_Informe.pdf'),pagesize=(595.28,841.89),leftMargin=43,rightMargin=43,topMargin=43,bottomMargin=51,title='TEL329 Tarea 4 - CoAP y MQTT',author='TEL329')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Informe generado:',O/'TEL329_Tarea4_Informe.pdf')
