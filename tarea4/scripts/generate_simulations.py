from pathlib import Path
import xml.etree.ElementTree as E
import copy
ROOT=Path(__file__).resolve().parents[1]
base=E.parse(ROOT/'references/cooja-template.csc').getroot()
for name in ('coap','mqtt','http'):
 doc=copy.deepcopy(base);sim=doc.find('simulation');sim.find('title').text='TEL329 Tarea4 '+name
 E.SubElement(sim,'speedlimit').text='1.0'
 template=copy.deepcopy(sim.find('motetype'))
 for mt in list(sim.findall('motetype')):sim.remove(mt)
 for role,ids,app in [('border-router',[1],'border'),(name+'-sensor',[2,3,4,5,6] if name!='http' else [2],'none' if name=='http' else name)]:
  mt=copy.deepcopy(template);mt.find('description').text=role;mt.find('identifier').text=role
  mt.find('source').text=f'[CONFIG_DIR]/../firmware/{role}.c'
  mt.find('commands').text=f'make TARGET=cooja clean\nmake -j4 {role}.cooja TARGET=cooja APP={app}'
  mote=copy.deepcopy(mt.find('mote'))
  for m in list(mt.findall('mote')):mt.remove(m)
  positions={1:(0,0),2:(35,0),3:(70,0),4:(105,0),5:(70,35),6:(105,35)}
  for i in ids:
   m=copy.deepcopy(mote);m.find('.//pos').set('x',str(positions[i][0]));m.find('.//pos').set('y',str(positions[i][1]));m.find('.//id').text=str(i);mt.append(m)
  sim.append(mt)
 for pl in list(doc.findall('plugin')):
  if any(x in (pl.text or '') for x in ('ScriptRunner','TimeLine','Notes')):doc.remove(pl)
 pl=E.SubElement(doc,'plugin');pl.text='org.contikios.cooja.serialsocket.SerialSocketServer'
 E.SubElement(pl,'mote_arg').text='0';cfg=E.SubElement(pl,'plugin_config');E.SubElement(cfg,'port').text='60001';E.SubElement(cfg,'bound').text='true'
 pl=E.SubElement(doc,'plugin');pl.text='org.contikios.cooja.plugins.ScriptRunner';cfg=E.SubElement(pl,'plugin_config');E.SubElement(cfg,'scriptfile').text='[CONFIG_DIR]/'+('capture-http.js' if name=='http' else 'capture.js');E.SubElement(cfg,'active').text='true'
 E.indent(doc);E.ElementTree(doc).write(ROOT/f'simulations/{name}.csc',encoding='utf-8',xml_declaration=True)
