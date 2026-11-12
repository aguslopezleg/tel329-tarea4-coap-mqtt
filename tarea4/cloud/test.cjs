const test=require('node:test');const assert=require('node:assert/strict');const http=require('node:http');
const {readSensor}=require('./middleware.cjs');
async function serve(handler,fn){const s=http.createServer(handler);await new Promise(r=>s.listen(0,'127.0.0.1',r));try{await fn(`http://127.0.0.1:${s.address().port}/`);}finally{await new Promise(r=>s.close(r));}}
test('acepta JSON completo y preserva identidad',async()=>serve((q,r)=>r.end(JSON.stringify({node:2,seq:7,temp:31,hum:85})),async url=>assert.deepEqual(await readSensor(url),{node:2,seq:7,temp:31,hum:85})));
test('rechaza temperatura fuera del rango del sensor',async()=>serve((q,r)=>r.end('{"node":2,"seq":7,"temp":99,"hum":85}'),async url=>assert.rejects(readSensor(url),/fuera de rango/)));
test('rechaza error HTTP antes de reenviar datos',async()=>serve((q,r)=>{r.statusCode=503;r.end('unavailable');},async url=>assert.rejects(readSensor(url),/HTTP 503/)));
test('limita espera de sensores sin respuesta',async()=>serve(()=>{},async url=>assert.rejects(readSensor(url,50),/Timeout sensor/)));
