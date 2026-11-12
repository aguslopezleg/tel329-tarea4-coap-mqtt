'use strict';
// HTTP IPv6 -> Azure IoT Hub. Sin claves: sumidero de archivo LOCAL explicito.
const http = require('http');
const fs = require('fs');
function readSensor(url, timeout = 15000) {
 return new Promise((resolve,reject) => {
  const req=http.get(url,res => {
   let body='';
   res.on('data',d=>{body+=d;if(body.length>4096)req.destroy(new Error('Respuesta demasiado grande'));});
   res.on('end',()=>{
    try {
     if(res.statusCode!==200)throw new Error('HTTP '+res.statusCode);
     const x=JSON.parse(body);
     if(!Number.isInteger(x.temp)||x.temp<15||x.temp>39||!Number.isInteger(x.hum)||x.hum<80||x.hum>89)throw new Error('Datos fuera de rango');
     if(!Number.isInteger(x.seq)||!Number.isInteger(x.node))throw new Error('Falta identidad o secuencia');
     resolve(x);
    }catch(e){reject(e);}
   });
  });
  req.setTimeout(timeout,()=>req.destroy(new Error('Timeout sensor')));
  req.on('error',reject);
 });
}
async function main() {
 const url=process.env.SENSOR_URL;
 if(!url)throw new Error('Defina SENSOR_URL=http://[IPv6-del-sensor]/');
 const conn=process.env.IOTHUB_DEVICE_CONNECTION_STRING;
 const file=process.env.LOCAL_OUTPUT;
 if(Boolean(conn)===Boolean(file))throw new Error('Configure exactamente un destino: IOTHUB_DEVICE_CONNECTION_STRING o LOCAL_OUTPUT');
 let client,Message;
 if(conn) {
  const {Client}=require('azure-iot-device');
  const {Mqtt}=require('azure-iot-device-mqtt');
  Message=require('azure-iot-device').Message;
  client=Client.fromConnectionString(conn,Mqtt);
  await client.open();
 }
 const limit=Number(process.env.LIMIT||0), interval=Number(process.env.INTERVAL_MS||3000);
 if(!Number.isFinite(limit)||limit<0||!Number.isFinite(interval)||interval<100)throw new Error('Intervalo o limite invalido');
 const mode=client?'azure':'local-file';
 console.log(JSON.stringify({event:'START',mode,sensorUrl:url}));
 let errors=0;
 try {
  for(let count=0;!limit||count<limit;count++) {
   try {
    const x=await readSensor(url);
    const body={deviceId:process.env.DEVICE_ID||'contiki-ng-01',node:x.node,seq:x.seq,temperature:x.temp,humidity:x.hum,sampledAt:new Date().toISOString()};
    const properties={temperatureAlert:String(body.temperature>30)};
    if(client) {
     const message=new Message(JSON.stringify(body));
     message.contentType='application/json';message.contentEncoding='utf-8';
     message.properties.add('temperatureAlert',properties.temperatureAlert);
     await client.sendEvent(message);
    } else fs.appendFileSync(file,JSON.stringify({mode,body,properties})+'\n');
    console.log(JSON.stringify({event:'SENT',mode,body,properties}));
   }catch(e){errors++;console.error(JSON.stringify({event:'ERROR',message:e.message}));}
   if(!limit||count+1<limit)await new Promise(r=>setTimeout(r,interval));
  }
 }finally{if(client)await client.close();}
 if(errors)process.exitCode=1;
}
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
module.exports={readSensor};
