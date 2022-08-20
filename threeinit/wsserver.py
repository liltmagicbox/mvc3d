#!/usr/bin/env python
import time
#import json

import asyncio
import datetime
import random
import websockets

class Broadcaster:
    def __init__(self, host='localhost', port=30020):
        #localhost, "192.168.0.47"(localipaddress) ..even texturl.
        self.host = host
        self.port = port
        #self.uri = f"ws://{host}:{port}/"

        self.on_message = None
        self.message= 'x'
    
    def _on_message(self, data):
        if self.on_message:
            self.on_message(data)


    def run(self):
        """forever"""
        CONNECTIONS = set()

        async def register(websocket):
            #if message == 'watch': ===not actually. register is the 1st conection.
            CONNECTIONS.add(websocket)
            print('connected',len(CONNECTIONS),websocket)

            try:
                #await websocket.wait_closed()
                async for message in websocket:#this is for,, with forever!                    
                    self._on_message(message)
                    
                    #send back, but function too big. server simple best.
                    # if data_back !=None:
                    #     await websocket.send(data_back)

                    #print(message,'messageinput')
                    #print(dir(websocket))
                    # for i in range(1000000):
                    #     time.time()
                    
                    #RuntimeWarning: Enable tracemalloc to get the object allocation traceback
                    #await added, works fine.

            except websockets.exceptions.ConnectionClosedError:
                #cannot read message from async for message in websocket:
                pass
                #print(type(e))<class 'websockets.exceptions.ConnectionClosedError'>
            #raise self.connection_closed_exc()
            #websockets.exceptions.ConnectionClosedError: no close frame received or sent

            finally:
                CONNECTIONS.remove(websocket)#it rellay finally disconnected.        
                print('DISCONNECTED',len(CONNECTIONS), websocket)



        async def show_time():
            while True:
                #print(len(CONNECTIONS),CONNECTIONS)#connection preserved!
                #message = datetime.datetime.utcnow().isoformat() + "BroadCast"
                websockets.broadcast(CONNECTIONS, self.message)
                
                await asyncio.sleep(1)
                #await asyncio.sleep(random.random() * 2 + 1)

        
        async def main():
            async with websockets.serve(register, self.host, self.port):
                await show_time()
        asyncio.run( main() )


def main():
    b = Broadcaster()
    def mas(m):
        print(m,'recv')
        if m=='encoded':
            return            
        return 'ba'
    b.on_message = mas
    b.message = 'ham'
    b.run()

if __name__ == '__main__':
    main()