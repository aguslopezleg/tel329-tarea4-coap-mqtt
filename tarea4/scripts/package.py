from pathlib import Path
import zipfile,hashlib,re,shutil
R=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if any(x in rel.parts for x in ('node_modules','build','__pycache__','.git')):continue
 if p.name=='.env' or p.suffix in ('.zip','.cooja','.a','.o','.pyc','.png.tmp'):continue
 if rel.parts[0]=='output' and p.name!='TEL329_Tarea4_Informe.pdf' and p.name not in ('topologia.png','rtt.png'):continue
 if p.name in ('SHA256SUMS.txt','hub-active.jpg'):continue
 files.append(p)
# Comprobar que ninguna clave local se incorpora accidentalmente a los artefactos.
private=R/'cloud/.env'
if private.exists():
 secrets=re.findall(r'SharedAccessKey=([^;\n]+)',private.read_text())
 for p in files:
  content=p.read_bytes()
  if any(key.encode() in content for key in secrets):
   raise AssertionError('Clave privada detectada en '+str(p.relative_to(R)))
(R/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(R)) for p in files)+'\n')
files.append(R/'SHA256SUMS.txt')
output=R.parent/'TEL329_Tarea4_Entrega_Completa.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,'tarea4/'+str(p.relative_to(R)))
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 names=z.namelist();assert not any('/node_modules/' in x or x.endswith('/.env') for x in names)
 assert 'tarea4/output/TEL329_Tarea4_Informe.pdf' in names
print(f'{output}: {len(files)} archivos, {output.stat().st_size} bytes; integridad ZIP OK')

shutil.copyfile(output,R.parent/'TEL329_Tarea4_Entrega.zip')
