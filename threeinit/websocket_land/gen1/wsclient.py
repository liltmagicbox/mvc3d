#!/usr/bin/env python
from time import perf_counter,sleep
from time import time as t

def time():
    return t()

import json
import zlib

import asyncio
from websockets import connect


uri = "ws://localhost:30020"

async def hello(uri):    
    async with connect(uri) as websocket:
        for i in range(3):
            beg = time()
            await websocket.send(str(time()))
            await asyncio.sleep(1)

        listen=False
        if listen:
            msg = await websocket.recv()
            msg = zlib.decompress(msg).decode()
            msg,ss = json.loads(msg)
            print(time()-float(msg))
            print(ss)
            print(time()-beg,'final')
            #print(help(websocket.recv))
            #print(data)

asyncio.run(hello("ws://localhost:30020"))
exit()

while True:
    asyncio.run(hello("ws://localhost:30020"))
    sleep(0.1)
    #took 2-25ms, finally. server.send took 2-15ms!


##from websockets import connect
##
##def hello(uri):
##    #with connect(uri) as websocket:
##    ws = connect(uri)
##    #websocket.send("Hello world!")
##    #websocket.recv()
##
##uri = "ws://localhost:30020"
###hello()




0.002915620803833008
0.008800745010375977
0.017549991607666016
0.011272192001342773
0.0028498172760009766
0.01723337173461914
0.003717660903930664
0.002986907958984375
0.0031251907348632812
0.0065975189208984375
0.008825540542602539
0.025376319885253906
0.022341489791870117
0.006459474563598633
0.002150297164916992
0.005453586578369141
0.016694307327270508

#2 6 11 17 22 25
