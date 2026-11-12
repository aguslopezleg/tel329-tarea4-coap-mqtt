'use strict';
const fs=require('fs');
async function main() {
 if(process.argv[2]==='--local') {
  const lines=fs.readFileSync(process.argv[3],'utf8').trim().split('\n').filter(Boolean);
  for(const line of lines) {
   const data=JSON.parse(line);
   if(data.mode!=='local-file')throw new Error('Modo local incorrecto');
   console.log(JSON.stringify({event:'LOCAL_RECEIVED',...data}));
  }
  return;
 }
 const cs=process.env.EVENTHUB_CONNECTION_STRING;
 if(!cs)throw new Error('Defina EVENTHUB_CONNECTION_STRING del endpoint integrado de IoT Hub; no la clave del dispositivo');
 const {EventHubConsumerClient}=require('@azure/event-hubs');
 const client=new EventHubConsumerClient(process.env.CONSUMER_GROUP||'$Default',cs);
 const subscription=client.subscribe({
  processEvents:async(events,context)=>{
   for(const event of events)console.log(JSON.stringify({event:'AZURE_RECEIVED',partition:context.partitionId,body:event.body,properties:event.properties,systemProperties:event.systemProperties}));
  },
  processError:async err=>console.error(JSON.stringify({event:'AZURE_ERROR',message:err.message}))
 },{startPosition:{enqueuedOn:new Date()}});
 console.log('Esperando eventos nuevos desde Azure IoT Hub');
 const close=async()=>{await subscription.close();await client.close();process.exit(0);};
 process.on('SIGINT',close);process.on('SIGTERM',close);
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
