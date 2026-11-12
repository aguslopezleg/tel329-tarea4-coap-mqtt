'use strict';
// Crear/consultar identidad sin imprimir claves. Credenciales solo en .env local.
const {Registry}=require('azure-iothub');const fs=require('fs');
async function main(){
 const cs=process.env.REGISTRY_CONNECTION_STRING;
 if(!cs)throw new Error('Falta REGISTRY_CONNECTION_STRING');
 const registry=Registry.fromConnectionString(cs);
 const deviceId=process.env.DEVICE_ID||'contiki-ng-01';
 let result,created=false;
 try{result=await registry.get(deviceId);}catch(e){
  if(e.name!=='DeviceNotFoundError'&&e.statusCode!==404)throw e;
  result=await registry.create({deviceId,status:'enabled',authentication:{type:'sas'}});created=true;
 }
 const device=result.responseBody;
 if(!device.authentication?.symmetricKey?.primaryKey)throw new Error('No se obtuvo clave simétrica');
 const serviceHost=cs.match(/HostName=([^;]+)/)[1];
 const deviceHost=serviceHost.replace('.service.azure-devices.net','.device.azure-devices.net');
 const value=`HostName=${deviceHost};DeviceId=${deviceId};SharedAccessKey=${device.authentication.symmetricKey.primaryKey}`;
 const path=process.env.ENV_FILE||require('path').join(__dirname,'.env');let env=fs.readFileSync(path,'utf8');
 env=env.split('\n').filter(x=>!x.startsWith('IOTHUB_DEVICE_CONNECTION_STRING=')).join('\n');
 fs.writeFileSync(path,env.trimEnd()+'\nIOTHUB_DEVICE_CONNECTION_STRING='+value+'\n',{mode:0o600});
 console.log(JSON.stringify({event:'DEVICE_READY',deviceId,created,status:device.status,authentication:device.authentication.type,deviceHost}));
}
main().catch(e=>{console.error(JSON.stringify({error:e.name,message:e.message,status:e.statusCode}));process.exitCode=1;});
