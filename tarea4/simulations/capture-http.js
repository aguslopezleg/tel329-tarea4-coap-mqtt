TIMEOUT(120000, log.log("END time="+sim.getSimulationTime()+"\n"); log.testOK());
sim.setSpeedLimit(1.0);
var radio=sim.getRadioMedium();
radio.getRadioTransmissionTriggers().addTrigger(log,function(event,obj) {
 if(String(event)==="TRANSMISSION_FINISHED") {
  var c=radio.getLastConnection(),p=c.getSource().getLastPacketTransmitted(),hex="";
  if(p) {var b=p.getPacketData();for(var i=0;i<b.length;i++)hex+=("0"+(b[i]&255).toString(16)).slice(-2);}
  log.log("RADIO time="+sim.getSimulationTime()+" start="+c.getStartTime()+" node="+c.getSource().getMote().getID()+" hex="+hex+"\n");
 }
});
while(true) {YIELD();log.log(time+"\t"+id+"\t"+msg+"\n");}
