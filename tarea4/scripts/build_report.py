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
p('TEL329 - Redes de Sensores | 12 de noviembre de 2026.')
p('Integrantes: Agustín López, Sebastián Romero y Óscar Carrasco.')
p('En esta tarea comparamos el envío de lecturas de temperatura mediante CoAP y MQTT en una red de sensores simulada. Para ello usamos Contiki-NG y Cooja, medimos los tiempos de confirmación de ambos protocolos y luego conectamos un sensor a Azure IoT Hub. En la última parte comprobamos el recorrido completo de diez lecturas, desde el mote hasta el consumidor en la nube. Las lecturas se generan por software; representan datos de prueba, no mediciones ambientales.')
heading('1. Escenario experimental')
p('Preparamos dos escenarios con la misma distribución de nodos: una raíz RPL Lite y cinco sensores, identificados del 2 al 6. Ambos trabajan con IPv6/6LoWPAN y CSMA. Usamos Contiki-NG release/v5.1 y Cooja con Java 21, dentro de un entorno Linux AArch64 en Docker. La raíz conecta la red con Linux mediante SLIP y tunslip6. En ese anfitrión, con dirección fd00::1, ejecutamos el servidor CoAP o el broker Mosquitto. Así, cada red tiene seis motes y un servicio externo que recibe sus mensajes.')
image('topologia.png',490,152,'Fuente: coordenadas de simulations/*.csc. Las líneas muestran alcance geométrico, no padres RPL fijos.')
p('Cada comparación dura 240 s y usa la semilla 1, con velocidad de simulación 1:1. Configuramos UDGM con 50 m de alcance y 100 m de interferencia. Aunque la probabilidad de éxito del modelo está fijada en 1, todavía pueden existir colisiones, espera por el canal y retransmisiones. Dejamos pasar 60 s antes de iniciar los envíos y los desfasamos según el ID del nodo. La expresión 15 + random_rand() % 25 produce temperaturas enteras entre 15 y 39 °C.')
page();heading('2. Actividad 1: RPL Lite y CoAP')
p('Para la primera actividad adaptamos coap-sensor.c, de manera que cada cliente enviara su temperatura al recurso /temperature del servidor en fd00::1. Elegimos mensajes POST confirmables (CON) para que cada lectura tuviera una respuesta que pudiéramos medir. El JSON incluye la temperatura, el nodo que la generó y su secuencia. En este caso la notificación parte del sensor mediante POST; no usamos la extensión Observe.')
code('coap_init_message(request, COAP_TYPE_CON, COAP_POST, 0);\ncoap_set_header_uri_path(request, "temperature");\ncoap_set_header_content_format(request, APPLICATION_JSON);\nCOAP_BLOCKING_REQUEST(&endpoint, request, response);')
p('Al recibir una lectura válida, el servidor aiocoap devuelve 2.04 Changed dentro del ACK, conservando el Message ID y el token. En la salida de Contiki esta respuesta aparece como code=68. Pudimos comprobarla tanto en los paquetes capturados como en el registro del cliente. Después de recibirla, el sensor espera 10 s antes del siguiente envío. Por eso, el tiempo entre lecturas incluye esos 10 s más el RTT de la anterior.')
a=sample('coap',2,1)
code('Sensor 2, registro real:\nCOAP_SEND node=2 seq=1 payload={"node":2,"seq":1,"temp":20}\nCOAP_ACK node=2 seq=1 code=68 rtt_ticks='+a['app_rtt_ms']+'\n\nServidor: {"event":"COAP_RECEIVED","node":2,"seq":1,"temp":20}')
p(f'En total recibimos {S["coap"]["application_sent"]} notificaciones y sus {c["n"]} confirmaciones. Cada sensor completó 18 intercambios. El RTT medio fue {f(c["mean_ms"])} ms; mediana {f(c["median_ms"])} ms y percentil 95 {f(c["p95_ms"])} ms. En esta ejecución todos los envíos tuvieron respuesta.')
p('El ejemplo anterior corresponde a la primera lectura del nodo 2. Para revisar los demás intercambios dejamos los registros de Cooja y del servidor en results/coap/, junto con los PCAP y responses.csv. Cooja terminó la ejecución con TEST OK. El programa, el Makefile y la configuración están en firmware/.')
page();heading('3. Actividad 2: RPL Lite y MQTT')
p('En la segunda actividad usamos mqtt-sensor.c y el motor MQTT de Contiki-NG. Los cinco sensores se conectan a Mosquitto 2.0.11 en [fd00::1]:1883 y comparten un solo tema: tel329/temperature. Configuramos MQTT 3.1.1 con QoS 1 para contar con una confirmación por publicación. Cada nodo usa su propio identificador de cliente, tel329-node-ID, y mantiene abierta la conexión TCP. La opción retain queda desactivada.')
code('mqtt_register(&conn, &sensor_process, client_id, event, 128);\nmqtt_connect(&conn, "fd00::1", 1883, 60, MQTT_CLEAN_SESSION_ON);\nmqtt_publish(&conn, &mid, topic, (uint8_t *)payload,\n             strlen(payload), MQTT_QOS_LEVEL_1, MQTT_RETAIN_OFF);')
p('Cuando Mosquitto recibe un PUBLISH, responde con el PUBACK correspondiente. Además, dejamos mosquitto_sub suscrito al mismo tema para comprobar que las lecturas llegaban al otro extremo de la aplicación. Esta distinción importa al interpretar la medición: el PUBACK confirma que el broker recibió el mensaje; la entrega al suscriptor se comprueba por separado en su registro.')
# Se extraen las primeras líneas reales, sin fabricar valores.
text=(R/'results/mqtt/COOJA.testlog').read_text();lines=[]
for tag in ['MQTT_CONNECTED node=2','MQTT_SEND node=2 seq=1 ','MQTT_ACK node=2 seq=1 ']:
 line=next(x.split('\t',2)[-1] for x in text.splitlines() if tag in x);lines.append(line)
code('\n'.join(lines)+'\nSuscriptor:\n'+(R/'results/mqtt/subscriber.log').read_text().splitlines()[0])
p(f'Al finalizar registramos {S["mqtt"]["application_sent"]} publicaciones y {m["n"]} PUBACK correlacionados. El RTT medio fue {f(m["mean_ms"])} ms; mediana {f(m["median_ms"])} ms y p95 {f(m["p95_ms"])} ms. La primera publicación se realiza en una iteración posterior a la conexión, lo que explica que haya 17 lecturas por sensor, frente a las 18 de CoAP. Para calcular el RTT de publicación dejamos fuera el establecimiento TCP/CONNECT, aunque también quedó capturado.')
p('La salida del suscriptor coincide con el mensaje enviado por el nodo 2. En results/mqtt/ se incluyen los registros de Cooja, Mosquitto y el suscriptor, además de las capturas y la tabla completa de respuestas. Para esta comparación local usamos un broker anónimo dentro del contenedor y MQTT sin TLS. La conexión con Azure, presentada más adelante, sí utiliza cifrado.')
page();heading('4. Actividad 3: captura y tiempos de respuesta')
p('Para relacionar los mensajes con sus respuestas registramos el tráfico en tres lugares: la radio IEEE 802.15.4 de Cooja, la capa IPv6 de cada sensor y el túnel hacia Linux, donde usamos tcpdump. El script analyze.py convierte los registros a PCAP y los decodifica con tshark. Las capturas de radio y sensores usan el tiempo de simulación, mientras que la del túnel usa el reloj del contenedor.')
p('Calculamos el RTT como la diferencia entre el primer envío y la recepción de su confirmación, siempre desde el mismo sensor. En CoAP emparejamos CON y ACK por Message ID y token; en MQTT usamos el flujo TCP y el identificador de PUBLISH/PUBACK. Excluimos los paquetes RPL que todavía iban en tránsito (Segments Left mayor que cero). También contrastamos los tiempos de los PCAP con los del programa: coincidieron con una tolerancia de 2 ms, usando CLOCK_SECOND=1000. El contador de solicitudes decodificadas se conserva aparte y no representa todas las retransmisiones TCP.')
rows=[['Protocolo','n','Media ms','Mediana ms','p95 ms','Mín-max ms']]
for proto,label in [('coap','CoAP CON'),('mqtt','MQTT QoS 1')]:
 s=S[proto]['overall'];rows.append([label,s['n'],f(s['mean_ms']),f(s['median_ms']),f(s['p95_ms']),f(s['min_ms'])+'-'+f(s['max_ms'])])
table(rows,[88,32,70,77,63,160])
rows=[['Nodo','n CoAP','Media CoAP ms','n MQTT','Media MQTT ms']]
for n in range(2,7):
 a=S['coap']['per_node'][str(n)];b=S['mqtt']['per_node'][str(n)];rows.append([n,a['n'],f(a['mean_ms']),b['n'],f(b['mean_ms'])])
table(rows,[55,70,145,70,150])
image('rtt.png',490,178,'Fuente: results/responses.csv; 60-240 s de simulación, semilla 1. Cajas: cuartiles; línea: mediana; puntos: valores atípicos.')
page();heading('5. Comparación de las mediciones')
p('Para mostrar algunos intercambios concretos elegimos las secuencias 1 y 10 de cada nodo en ambos protocolos. Aplicamos la misma regla a los cinco sensores para evitar escoger solo los casos más favorables. Los promedios y percentiles de la página anterior se calcularon con la muestra completa. Los CSV permiten ubicar cada solicitud y respuesta en Wireshark mediante sus números de trama e identificadores.')
rows=[['Nodo','Secuencia','CoAP RTT ms','MQTT RTT ms']]
for n in range(2,7):
 for seq in [1,10]:rows.append([n,seq,f(float(sample('coap',n,seq)['rtt_ms'])),f(float(sample('mqtt',n,seq)['rtt_ms']))])
table(rows,[65,85,170,170])
diff=m['mean_ms']-c['mean_ms']
p(f'Al comparar los promedios, MQTT tardó {f(diff)} ms más que CoAP en confirmar los mensajes. Sin embargo, esa diferencia no aparece de la misma manera en todos los nodos. Cada salto agrega transmisiones y oportunidades de esperar por el canal. Además, MQTT incorpora el funcionamiento de TCP, mientras que CoAP trabaja sobre UDP. Como también medimos el paso por el túnel y el procesamiento del servicio, no podemos atribuir la diferencia únicamente a las cabeceras de los protocolos.')
p('La distancia en saltos ayuda a entender las diferencias entre sensores. El nodo 2 llega a la raíz en un salto; los nodos 3 y 5 necesitan dos, y los nodos 4 y 6, tres. Además, RPL eligió un padre distinto para el nodo 6 en cada escenario. Aunque conservamos las posiciones, las rutas y la competencia por el canal no fueron exactamente iguales.')
p('También hay diferencias en lo que confirma cada protocolo. La respuesta CoAP 2.04 indica que el servidor procesó el POST, mientras que PUBACK confirma la aceptación por el broker. Estamos comparando tiempos de confirmación de telemetría, con alcances distintos. A esto se suma que CoAP espera 10 s después de cada respuesta y MQTT revisa su estado cada 10 s. Los protocolos también generan tráfico de control y consumen números aleatorios de manera diferente.')
p('Con estas condiciones, la diferencia observada es pequeña y depende del escenario. Una sola ejecución no permite afirmar que uno de los protocolos siempre sea más rápido. Para sostener una conclusión más amplia habría que repetir con varias semillas, cargas y condiciones de pérdida. También sería necesario evaluar el efecto del cifrado y del hardware físico. En esta ejecución todos los mensajes enviados tuvieron confirmación; los archivos unmatched.json registran cero intercambios pendientes.')
page();heading('6. Actividad 4: integración real con Azure')
p('Para llevar las lecturas a la nube usamos el Hub tel329-t4-alopez-20261112, en Brazil South, y registramos el dispositivo contiki-ng-01 con autenticación simétrica. Elegimos el nivel F1 Free: el portal indicaba USD 0 al mes y una cuota de 8.000 mensajes diarios, suficiente para las diez lecturas de esta prueba.')
p('El recorrido parte de un mote que ejecuta http-sensor.c y se conecta a Linux a través del border router RPL Lite. El middleware, escrito para Node.js 22, consulta GET / en la dirección IPv6 del sensor, lee temperatura y humedad y las envía a Azure por MQTT/TLS. Finalmente, un programa independiente usa EventHubConsumerClient para recibirlas desde el endpoint integrado, mediante AMQP/TLS.')
p('4.a - Middleware. Obtuvimos diez envíos confirmados, identificados en el registro con event=SENT y mode=azure. Antes de enviarlos, el programa cambia los nombres temp/hum por temperature/humidity y agrega el dispositivo, la fecha de lectura y temperatureAlert. Esta alerta se activa sobre 30 °C. El nodo y la secuencia se conservan para seguir cada lectura a través de todo el recorrido. Las claves se guardan en el archivo local .env, que se excluye de la entrega.')
ex=A['first_sample'];b=ex['body'];sensor={'node':b['node'],'seq':b['seq'],'temp':b['temperature'],'hum':b['humidity']}
code('4.b - Respuesta real del mote:\n'+json.dumps(sensor,separators=(',',':'))+'\n\n4.a - Envío real a Azure:\n'+f'event=SENT, mode=azure, deviceId={b["deviceId"]}\nnode={b["node"]}, seq={b["seq"]}, temperature={b["temperature"]}\nhumidity={b["humidity"]}, temperatureAlert={ex["properties"]["temperatureAlert"]}\n\n4.c - Consumidor:\nevent=AZURE_RECEIVED, partition='+str(A['azure_first_event']['partition']))
p('4.b - Sensor. El mote respondió diez consultas con datos JSON sobre IPv6/TCP. La primera lectura, mostrada arriba, fue de 31 °C y 85 % de humedad. El firmware genera temperaturas entre 15 y 39 °C y humedades entre 80 y 89 %. Cada respuesta queda registrada como HTTP_SENSOR en Cooja, lo que permite contrastar el dato original con el enviado a la nube.')
p('4.c - Suscriptor. Recibimos diez eventos únicos desde Azure, registrados como AZURE_RECEIVED. Al compararlos con el mote y el middleware, coincidieron el nodo, la secuencia, la temperatura, la humedad y la alerta. La propiedad iothub-connection-device-id también confirmó que Azure los recibió del dispositivo contiki-ng-01. El script check_azure.py realiza estas comprobaciones para toda la muestra.')
p('Los registros del mote, del middleware y del consumidor están en results/azure/, junto con readings.csv y el resultado de la verificación. La simulación terminó normalmente con TEST OK. Como comprobación adicional, el middleware superó cuatro pruebas para lecturas válidas, datos fuera de rango, errores HTTP y sensores que no responden.')
page();heading('7. Evidencia de Azure y lecturas recibidas')
table([['Propiedad del recurso','Valor verificado'],['IoT Hub','tel329-t4-alopez-20261112'],['Estado','Active'],['Nivel','F1 Free (USD 0/mes)'],['Región','Brazil South'],['Dispositivo','contiki-ng-01'],['Lecturas enviadas / recibidas','10 / 10']],[180,310])
p('La tabla resume la configuración que comprobamos en el portal de Azure. Dejamos fuera de la edición pública la captura de esa pantalla, porque contiene datos de la cuenta. Para respaldar los resultados incluimos los registros originales del sensor, del middleware y del consumidor, además de las diez lecturas recibidas que se muestran a continuación.')
rows=[['Secuencia','Temperatura °C','Humedad %','Alerta >30 °C']]
for row in csv.DictReader((R/'results/azure/readings.csv').open()):
 rows.append([row['seq'],row['temperature'],row['humidity'],row['temperatureAlert']])
table(rows,[75,145,130,140])
p('Iniciamos el suscriptor antes de enviar la primera lectura para que pudiera recibir toda la muestra desde su arranque. El consumidor usa la directiva service. Para registrar la identidad del sensor recurrimos al SDK oficial azure-iothub, ya que la vista Dispositivos del portal devolvía un error. La conexión posterior del dispositivo y la recepción de los mensajes permitieron comprobar que el registro había quedado operativo.')
p('Antes de conectar con Azure también probamos el recorrido local, guardando diez lecturas en un archivo y leyéndolas con otro programa. Ese control ayudó a verificar la transformación de los datos. Sus registros se conservan en results/http/; la prueba de conexión con la nube está en results/azure/.')
page();heading('8. Reproducción, publicación y referencias')
p('Organizamos la entrega para que se puedan revisar los resultados y repetir las pruebas. El ZIP reúne el firmware, las simulaciones, los scripts, los PCAP, los registros y el informe en PDF y Markdown. setup.sh descarga las versiones fijadas de Contiki-NG y Cooja, y run.sh ejecuta los escenarios por separado. Para Azure, los procesos de Node.js comparten la red del contenedor que contiene el túnel IPv6.')
code('bash tarea4/scripts/setup.sh\nbash tarea4/scripts/run.sh coap mqtt http\ndocker run --rm -v "$PWD:/work" tel329-tarea4:1 \\\n  python3 /work/tarea4/scripts/analyze.py\npython3 tarea4/scripts/check_cloud.py\n# Con .env de Azure configurado:\nbash tarea4/scripts/run_azure.sh\npython3 tarea4/scripts/check_azure.py\nnode --test tarea4/cloud/test.cjs\npython3 tarea4/scripts/build_report.py')
p('Las instrucciones para repetir la integración con Azure están en cloud/LEEME_AZURE.md. Las credenciales se configuran localmente y el Hub utilizado permanece en el nivel gratuito F1. Publicamos el código, el informe y las evidencias en https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt, de acuerdo con lo solicitado en el enunciado.')
p('En conjunto, las pruebas permitieron observar dos formas distintas de enviar telemetría sobre RPL Lite. Ambos protocolos entregaron todas las lecturas generadas; CoAP tuvo una media de confirmación ligeramente menor, aunque esa diferencia no basta para generalizar. La integración con Azure completó el recorrido desde el mote hasta el consumidor y conservó los valores de las diez lecturas. Las capturas y los registros incluidos permiten revisar esas conclusiones a partir de los datos.')
refs=[('Repositorio público de esta entrega','https://github.com/aguslopezleg/tel329-tarea4-coap-mqtt'),('Enunciado TEL329 Tarea 4, versión 1.0, 2026','references/TEL329-Tarea4-2026-v1.0.html'),('Contiki-NG release/v5.1 y fuentes de CoAP/MQTT','https://github.com/contiki-ng/contiki-ng/tree/2b87baf3ebdde3c8e37ca791d2bc84bfd76c49a4'),('Contiki-NG: Cooja, simulating a border router','https://docs.contiki-ng.org/en/master/doc/tutorials/Cooja-simulating-a-border-router.html'),('RFC 7252: CoAP, secciones 4 y 5','https://www.rfc-editor.org/rfc/rfc7252'),('OASIS MQTT 3.1.1, secciones 3.3 y 4.3.2','https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html'),('Microsoft Learn: endpoints de IoT Hub','https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-endpoints'),('Microsoft Learn: SDK Event Hubs JavaScript','https://learn.microsoft.com/en-us/javascript/api/overview/azure/event-hubs-readme?view=azure-node-latest')]
for label,url in refs:
 story.append(Paragraph(html.escape(label)+'<br/><font size="7">'+html.escape(url)+'</font>',styles['C']));md.append(f'- [{label}]({url})')
(R/'Informe.md').write_text('\n\n'.join(md)+'\n')
def footer(canvas,doc):
 canvas.setStrokeColor(teal);canvas.line(43,39,552,39);canvas.setFillColor(navy);canvas.setFont('Helvetica',8);canvas.drawString(43,26,'TEL329 - Tarea 4 | CoAP, MQTT y Azure IoT Hub');canvas.drawRightString(552,26,str(doc.page))
doc=SimpleDocTemplate(str(O/'TEL329_Tarea4_Informe.pdf'),pagesize=(595.28,841.89),leftMargin=43,rightMargin=43,topMargin=43,bottomMargin=51,title='TEL329 Tarea 4 - CoAP y MQTT',author='Agustín López; Sebastián Romero; Óscar Carrasco')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Informe generado:',O/'TEL329_Tarea4_Informe.pdf')
