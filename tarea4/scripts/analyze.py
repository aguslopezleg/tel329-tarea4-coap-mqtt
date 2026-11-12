"""Reconstruye PCAP desde capturas pasivas reales y correlaciona respuestas.
Ejecutar en el contenedor (incluye tshark). No fabrica paquetes ni retardos.
"""
from pathlib import Path
import csv,json,re,struct,subprocess,statistics,ipaddress,sys
ROOT=Path(__file__).resolve().parents[1]

def pcap(path,packets,linktype):
 with path.open('wb') as f:
  f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,linktype))
  for t,b in packets:
   f.write(struct.pack('<IIII',int(t)//1000000,int(t)%1000000,len(b),len(b)));f.write(b)

def writecsv(path,rows,fields=None):
 if not rows and not fields:return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def stats(values):
 values=sorted(values)
 def pct(p):
  x=(len(values)-1)*p;a=int(x);return values[a]+(values[min(a+1,len(values)-1)]-values[a])*(x-a)
 return dict(n=len(values),mean_ms=statistics.mean(values),median_ms=statistics.median(values),p95_ms=pct(.95),min_ms=min(values),max_ms=max(values),stdev_ms=statistics.stdev(values) if len(values)>1 else 0)

allsummary={};allpairs=[];checks=[]
for proto in (sys.argv[1:] or ['coap','mqtt']):
 folder=ROOT/'results'/proto
 text=(folder/'COOJA.testlog').read_text()
 ip={i:[] for i in range(2,7)};radio=[];app={};sent=set();acks={}
 for line in text.splitlines():
  m=re.match(r'(\d+)\t(\d+)\tIPCAP dir=(TX|RX) ticks=(\d+) hex=([a-f0-9]+)',line)
  if m:
   t,node,direction,ticks,h=m.groups();b=bytes.fromhex(h);node=int(node)
   own=ipaddress.IPv6Address(f'fd00::20{node}:{node}:{node}:{node}').packed
   # RPL source-routing rewrites IPv6 destination at intermediate hops.
   # Exclude transit RX with Segments Left > 0 in the routing header.
   nh=b[6];off=40;transit=False
   while nh in (0,43,60) and off+4<=len(b):
    if nh==43 and b[off+3]>0:transit=True
    nh,length=b[off],(b[off+1]+1)*8;off+=length
   if direction=='RX' and transit:continue
   if (direction=='TX' and b[8:24]==own) or (direction=='RX' and b[24:40]==own):ip[node].append((int(t),b))
  m=re.match(r'RADIO time=(\d+) start=(\d+) node=(\d+) hex=([a-f0-9]+)',line)
  if m:radio.append((int(m[2]),bytes.fromhex(m[4])))
  m=re.search(r'(COAP|MQTT)_SEND node=(\d+) seq=(\d+)',line)
  if m:sent.add((int(m[2]),int(m[3])))
  m=re.search(r'(COAP|MQTT)_ACK node=(\d+) seq=(\d+).*rtt_ticks=(\d+)',line)
  if m:acks[(int(m[2]),int(m[3]))]=int(m[4])
 pcap(folder/'radio.pcap',radio,195)
 pairs=[];attempts=[];unmatched=[]
 fields=['frame.number','frame.time_epoch','ipv6.src','ipv6.dst','tcp.stream','coap.type','coap.code','coap.mid','coap.token','mqtt.msgtype','mqtt.msgid','mqtt.topic','mqtt.msg']
 for node,packets in ip.items():
  capture=folder/f'node{node}.pcap';pcap(capture,packets,101)
  cmd=['tshark','-r',str(capture),'-Y','coap || mqtt','-T','fields','-E','separator=\t','-E','occurrence=f']
  for field in fields:cmd+=['-e',field]
  result=subprocess.run(cmd,text=True,capture_output=True,check=True)
  (folder/f'node{node}-decoded.tsv').write_text('\t'.join(fields)+'\n'+result.stdout)
  outstanding={};seen=set()
  for line in result.stdout.splitlines():
   vals=line.split('\t');vals+=['']*(len(fields)-len(vals));r=dict(zip(fields,vals));t=float(r['frame.time_epoch']);frame=int(r['frame.number'])
   src=r['ipv6.src'];out=src==f'fd00::20{node}:{node}:{node}:{node}'
   is_request=(proto=='coap' and out and r['coap.type']=='0' and r['coap.code']=='2') or (proto=='mqtt' and out and r['mqtt.msgtype']=='3')
   is_response=(proto=='coap' and not out and r['coap.type']=='2' and r['coap.code']=='68') or (proto=='mqtt' and not out and r['mqtt.msgtype']=='4')
   key=(r['coap.mid'],r['coap.token']) if proto=='coap' else (r['tcp.stream'],r['mqtt.msgid'])
   if is_request:
    if key in outstanding:outstanding[key]['transmissions']+=1;continue
    if key in seen:continue
    obj={'protocol':proto,'node':node,'id':r['coap.mid'] if proto=='coap' else r['mqtt.msgid'],'request_frame':frame,'request_s':t,'transmissions':1}
    # MQTT msg is a display string; sequence is matched later in capture order.
    outstanding[key]=obj;attempts.append(obj)
   elif is_response and key in outstanding:
    obj=outstanding.pop(key);seen.add(key);obj.update(response_frame=frame,response_s=t,rtt_ms=round((t-obj['request_s'])*1000,6));pairs.append(obj)
  unmatched.extend(outstanding.values())
 # Original application sequence numbers in time order per node.
 for node in range(2,7):
  ps=sorted([p for p in pairs if p['node']==node],key=lambda p:p['request_s'])
  # Wire/application correspondence requires same count, then order (one in flight).
  a=sorted((seq,v) for (n,seq),v in acks.items() if n==node)
  if len(ps)!=len(a):raise AssertionError(f'{proto} node{node}: wire={len(ps)}, app={len(a)}')
  for p,(seq,v) in zip(ps,a):
   p['seq']=seq;p['app_rtt_ms']=v # CLOCK_SECOND=1000 verified below
   if abs(v-p['rtt_ms'])>2:raise AssertionError(f'Clock/capture discrepancy {p}')
  if len(ps)<10:raise AssertionError(f'Insufficient representative sample {proto} node{node}: {len(ps)}')
 pairs.sort(key=lambda p:(p['node'],p['seq']))
 assert 'clock_second=1000' in text
 summary={'overall':stats([p['rtt_ms'] for p in pairs]),'per_node':{str(n):stats([p['rtt_ms'] for p in pairs if p['node']==n]) for n in range(2,7)},'application_sent':len(sent),'application_acked':len(acks),'wire_pairs':len(pairs),'unmatched':len(unmatched),'radio_frames':len(radio),'ip_frames':sum(map(len,ip.values()))}
 allsummary[proto]=summary;allpairs+=pairs
 writecsv(folder/'responses.csv',pairs)
 (folder/'unmatched.json').write_text(json.dumps(unmatched,indent=2))
 checks.append(f'{proto}: five nodes, >=10 confirmed exchanges/node, PCAP RTT agrees with app within 2ms; {len(pairs)} pairs')
 # Export RPL parent changes for interpretation of actual (not just geometric) paths.
 parent=[line for line in text.splitlines() if 'preferred parent' in line or 'parent switch' in line]
 (folder/'rpl-parents.txt').write_text('\n'.join(parent)+'\n')
writecsv(ROOT/'results/responses.csv',allpairs)
(ROOT/'results/summary.json').write_text(json.dumps(allsummary,indent=2))
(ROOT/'results/verification.txt').write_text('\n'.join(checks)+'\n')
print(json.dumps(allsummary,indent=2))
