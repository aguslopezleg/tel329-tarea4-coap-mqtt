import asyncio,json
import aiocoap,aiocoap.resource as resource
class Temperature(resource.Resource):
 async def render_post(self,request):
  data=json.loads(request.payload)
  assert 15<=data['temp']<=39
  print(json.dumps({'event':'COAP_RECEIVED',**data}),flush=True)
  return aiocoap.Message(code=aiocoap.CHANGED,payload=b'OK')
async def main():
 site=resource.Site();site.add_resource(['temperature'],Temperature())
 site.add_resource(['.well-known','core'],resource.WKCResource(site.get_resources_as_linkheader))
 await aiocoap.Context.create_server_context(site,bind=('::',5683),transports=['udp6'])
 print('CoAP server listening [::]:5683 /temperature',flush=True)
 await asyncio.get_running_loop().create_future()
asyncio.run(main())
