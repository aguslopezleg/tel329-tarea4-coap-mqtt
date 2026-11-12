from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]/'results'
lines=[]
for proto in ['coap','mqtt']:
 text=(R/proto/'COOJA.testlog').read_text()
 sent=[json.loads(x) for x in re.findall(r'(?:COAP|MQTT)_SEND[^\n]+payload=(\{[^\n]+\})',text)]
 if proto=='coap':received=[{k:v for k,v in json.loads(x).items() if k!='event'} for x in (R/proto/'server.log').read_text().splitlines() if x.startswith('{')]
 else:received=[json.loads(x.split(' ',1)[1]) for x in (R/proto/'subscriber.log').read_text().splitlines() if x.startswith('tel329/temperature ')]
 key=lambda x:(x['node'],x['seq'],x['temp'])
 assert sorted(map(key,sent))==sorted(map(key,received)),proto
 assert all(15<=x['temp']<=39 for x in received)
 assert set(x['node'] for x in received)==set(range(2,7))
 assert len(set((x['node'],x['seq']) for x in received))==len(received)
 assert 'TEST OK' in text
 lines.append(f'PASS {proto}: {len(sent)} generated samples = {len(received)} delivered samples, identical node/seq/temp, five nodes, no duplicate application readings, simulation TEST OK.')
(R/'delivery-verification.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
