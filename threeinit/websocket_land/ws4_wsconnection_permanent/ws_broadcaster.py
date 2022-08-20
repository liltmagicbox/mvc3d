#!/usr/bin/env python
import time
import json
import zlib

import asyncio
import datetime
import random
import websockets

x = zlib.compress('message'.encode('utf-8'))
print(x)

#===compress sqeuence
dict_message = {'ham':1,'egg':12}
json_message = json.dumps(dict_message)
byte_message = json_message.encode('utf-8')
comp_message = zlib.compress(byte_message)

byte_message = zlib.decompress(comp_message)
json_message = byte_message.decode('utf-8')
dict_message = json.loads(json_message)
print(dict_message)
#===compress sqeuence

#===no need to compress
#print(byte_message)
#print(comp_message)
#b'{"ham": 1, "egg": 12}'
#b'x\x9c\xabV\xcaH\xccU\xb2R0\xd4QPJMO\x07\xb1\x8cj\x01>\x9a\x05~'
#note: smallsize,seems no need to compress!
#===no need to compress


#===what is byte code??
#byte_message = 'a'.encode()
#b'x\x9cK\x04\x00\x00b\x00b' a
#b'x\x9cKL\x04\x00\x01%\x00\xc3' aa
#b'x\x9cKL$\x12\x00\x00Fu\x0f\x8a' aaa
#b'x\x9cKL$\x12$\x01\x00Va\x0f\xec' aaaaa...

#33 is b''.__sizeof__().
# \xabc... is len =3.

#b'x\x9cK\x04\x00\x00b\x00b' a
#size is 33+9 = 42.   seems of: 9cK 4 0 0b 0b
#b'    b'
#===what is byte code??




class Broadcaster:
    def __init__(self):
        1

    def run(self):
        """forever"""
        CONNECTIONS = set()

        async def register(websocket):
            #if message == 'watch': ===not actually. register is the 1st conection.
            CONNECTIONS.add(websocket)
            try:
                #await websocket.wait_closed()
                async for message in websocket:#this is for,, with forever!
                    
                    print(message,'messageinput')
                    #print(dir(websocket))
                    # for i in range(1000000):
                    #     time.time()
                    await websocket.send('ccccccccaseter')
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
                print('DISCONNECTED',websocket)



        async def show_time():
            while True:
                print(CONNECTIONS)#connection preserved!
                message = datetime.datetime.utcnow().isoformat() + "Z"
                websockets.broadcast(CONNECTIONS, message)
                
                await asyncio.sleep(1)
                #await asyncio.sleep(random.random() * 2 + 1)

        async def main():
        #"192.168.0.47", 5678 "liltbox.iptime.org", 80
            async with websockets.serve(register, "localhost", 30020):
                await show_time()
        asyncio.run( main() )


b = Broadcaster()
b.run()