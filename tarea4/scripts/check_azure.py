from pathlib import Path
import json,re,csv
R=Path(__file__).resolve().parents[1]/'results/azure'
sent=[json.loads(x) for x in (R/'middleware.log').read_text().splitlines() if x.startswith('{') and json.loads(x).get('event')=='SENT']
received=[json.loads(x) for x in (R/'subscriber.log').read_text().splitlines() if x.startswith('{') and json.loads(x).get('event')=='AZURE_RECEIVED']
sensor=[json.loads(x) for x in re.findall(r'HTTP_SENSOR payload=(\{[^\n]+\})',(R/'COOJA.testlog').read_text())]
assert 'TEST OK' in (R/'COOJA.testlog').read_text(), 'La simulación debe finalizar normalmente'
assert len(sent)==10 and all(x['mode']=='azure' for x in sent)
key=lambda b:(b['node'],b['seq'])
recv={key(x['body']):x for x in received}
assert len(recv)==10
raw={(x['node'],x['seq']):x for x in sensor}
for x in sent:
 b=x['body'];s=raw[key(b)];v=recv[key(b)]
 assert v['body']==b
 assert (b['temperature'],b['humidity'])==(s['temp'],s['hum'])
 assert v['properties']['temperatureAlert']==str(s['temp']>30).lower()
 assert v['systemProperties']['iothub-connection-device-id']==b['deviceId']
summary={'hub':'tel329-t4-alopez-20261112','tier':'F1 Free','region':'Brazil South','device':'contiki-ng-01','sent':len(sent),'received_unique':len(recv),'sensor_samples':len(sensor),'transport_device_to_cloud':'MQTT/TLS','transport_consumer':'AMQP/TLS','first_sample':sent[0],'azure_first_event':received[0]}
rows=[{'node':x['body']['node'],'seq':x['body']['seq'],'temperature':x['body']['temperature'],'humidity':x['body']['humidity'],'temperatureAlert':x['properties']['temperatureAlert'],'partition':x['partition'],'sampledAt':x['body']['sampledAt']} for x in received]
rows.sort(key=lambda x:(x['node'],x['seq']))
with (R/'readings.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(R/'summary.json').write_text(json.dumps(summary,indent=2))
(R/'verification.txt').write_text('PASS: 10 lecturas reales Contiki-NG IPv6/HTTP -> middleware -> Azure IoT Hub -> Event Hubs consumer. Coinciden identidad, secuencia, temperatura, humedad, alerta y deviceId autenticado.\n')
print((R/'verification.txt').read_text())
