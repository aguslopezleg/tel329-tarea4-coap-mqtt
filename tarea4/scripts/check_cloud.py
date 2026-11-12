from pathlib import Path
import json,re
p=Path(__file__).resolve().parents[1]/'results/http'
sensor=[json.loads(x) for x in re.findall(r'HTTP_SENSOR payload=(\{[^\n]+\})',(p/'COOJA.testlog').read_text())]
records=[json.loads(x) for x in (p/'local-cloud.jsonl').read_text().splitlines()]
received=[json.loads(x) for x in (p/'subscriber.log').read_text().splitlines()]
assert len(sensor)==len(records)==len(received)==10,(len(sensor),len(records),len(received))
for s,r,v in zip(sensor,records,received):
 b=r['body'];assert (s['node'],s['seq'],s['temp'],s['hum'])==(b['node'],b['seq'],b['temperature'],b['humidity'])
 assert r['properties']['temperatureAlert']==str(s['temp']>30).lower()
 assert v['body']==b and v['event']=='LOCAL_RECEIVED'
(p/'verification.txt').write_text('PASS: 10 lecturas reales Contiki-NG HTTP -> middleware -> archivo local -> consumidor local; identidad, secuencia, temperatura, humedad y alerta coinciden. Control local; la ejecución Azure se documenta por separado en results/azure/.\n')
print((p/'verification.txt').read_text())
