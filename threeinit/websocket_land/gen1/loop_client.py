#https://stackoverflow.com/questions/53331127/python-websockets-send-to-client-and-keep-connection-alive
#https://stackoverflow.com/questions/53188951/how-to-keep-connection-alive-with-async-websockets-client

#https://websockets.readthedocs.io/en/stable/intro/tutorial2.html
#https://websockets.readthedocs.io/en/stable/intro/quickstart.html


import time
# WS client example

import asyncio
import websockets

async def hello_once():
    async with websockets.connect('ws://localhost:30020') as websocket:
        for i in range(5):
            name = 'akari'
            await websocket.send(name)
            print(f"> {name}")
        #https://websockets.readthedocs.io/en/stable/reference/server.html#websockets.server.WebSocketServerProtocol.send
        #except websockets.ConnectionClosed:

        # greeting = await websocket.recv()
        # print(f"< {greeting}")


async def hello():
    uri = 'ws://localhost:30020'
    async with websockets.connect(uri) as websocket:
        print('loop')
        names = ['akari', 'sumire', 'rin', 'juri']
        i=0
        while True:
            name = 'akari'
            name = names[i]
            i+=1
            if i==4:
                i=0
            await websocket.send(name)
            print(f"> {name}")
            await asyncio.sleep(0.5)
    print('done')

def main():
    #asyncio.get_event_loop().run_until_complete( hello() )
    print('start')
    asyncio.get_event_loop().run_until_complete( hello_once() )
    print('done')
    time.sleep(3)

if __name__ == '__main__':
    main()
