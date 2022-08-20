#!/usr/bin/env python
import time
import json
import asyncio
import datetime
import random
import websockets

CONNECTIONS = set()

async def register(websocket):
    CONNECTIONS.add(websocket)
    #print(dir(websocket))
    try:
        #await websocket.wait_closed()        
        async for message in websocket:#this is for,, with forever!
            print(message)
            event = json.loads(message)
            try:
                print(time.time()-float(event['time'])/1000)
            except:
                pass
        print('try done')
    except websockets.exceptions.ConnectionClosedError:
        #cannot read message from async for message in websocket:
        pass
        #print(type(e))<class 'websockets.exceptions.ConnectionClosedError'>
    #raise self.connection_closed_exc()
    #websockets.exceptions.ConnectionClosedError: no close frame received or sent

    finally:
        CONNECTIONS.remove(websocket)#it rellay finally disconnected.        
        print('DISCONNECTED',websocket)

async def show_time():
    while True:
        print(CONNECTIONS)#connection preserved!
        message = datetime.datetime.utcnow().isoformat() + "Z"
        websockets.broadcast(CONNECTIONS, message)
        
        await asyncio.sleep(1)
        #await asyncio.sleep(random.random() * 2 + 1)

async def main():
    #async with websockets.serve(register, "192.168.0.47", 5678):
    #async with websockets.serve(register, "liltbox.iptime.org", 80):
    async with websockets.serve(register, "localhost", 30020):
        await show_time()

if __name__ == "__main__":
    asyncio.run(main())


