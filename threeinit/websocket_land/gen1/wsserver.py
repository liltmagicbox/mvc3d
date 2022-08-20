#!/usr/bin/env python
from time import perf_counter

from time import time as t

def time():
    return t()

import json
import zlib

import asyncio
from websockets import serve







##async def echo(websocket):
##    async for message in websocket:
##        print(time()-float(message))
##        await websocket.send(message)

async def echo(websocket):
    async for message in websocket:
        print(message)
        return
        trecv = time()
        print(trecv-float(message))

        message = time(),[1,2,3,4,56]
        message = json.dumps(message)
        message = zlib.compress(message.encode())
        await websocket.send(message)
        print(time()-trecv,'end')
        
async def main():
    async with serve(echo, "localhost", 30020):
        await asyncio.Future()  # run forever

asyncio.run(main())
