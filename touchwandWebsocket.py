import asyncio
import websockets
import json


login_url = "ws://{}/async"

async def msgLoop():

    controller_address = input('TouchWand controller IP address : ')
	uri = login_url.format(controller_address)
	ws = await websockets.connect(uri,subprotocols=['relay_protocol'])
	#client shout send this message with his contId it could be different name
	await ws.send(json.dumps({"contId": "mySuperClient123"})) 
	try:
		while True:
			d = await ws.recv()
			print(f"< {d}")
			msg = json.loads(d)
#            print(msg["type"])
	except KeyboardInterrupt:
		print('close')
		await ws.close
asyncio.run(msgLoop())