import asyncio
import websockets
 
async def accept(websocket, path):
    while True:
        data = await websocket.recv()
        print("receive : " + data)        
        await websocket.send("echo : " + data)
        
 
start_server = websockets.serve(accept, "localhost", 9998)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
#출처: https://nowonbun.tistory.com/674 [명월 일지:티스토리]
