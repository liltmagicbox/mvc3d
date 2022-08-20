from interface import *

from queue import Queue



import json
import zlib
import asyncio
from websockets import serve

import threading

class Wsman:
    def __init__(self):
        1
    def connect(self, ip,port):
        uri = f"ws://{ip}:{port}"

        async def hello(uri):    
            async with connect(uri) as websocket:
                await websocket.send('sendmessage')
                #msg = await websocket.recv()
                
                #msg = zlib.decompress(msg).decode()
                #msg,ss = json.loads(msg)
        asyncio.run(hello(uri))


class WebSocket:
    def __init__(self, ip='localhost', port=30020, compress=False):
        self.ip = ip
        self.port = port
        self.compress = compress
    def compress(self,data):
        if not self.compress:
            return data
    def decompress(self,data):
        1
    
    def cast(self):
        connected = set()

        async def register(websocket):
            connected.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                connected.remove(websocket)

        async def handler(websocket):
            connected.add(websocket)
            try:

    def connect(self):
        uri = f"ws://{self.ip}:{self.port}"

        async def hello(uri):    
            async with connect(uri) as websocket:
                await websocket.send('sendmessage')
                #msg = await websocket.recv()
                
                #msg = zlib.decompress(msg).decode()
                #msg,ss = json.loads(msg)
        asyncio.run(hello(uri))

    def listen2(self,queue):
        
        #def thread_in(queue):
        async def echo(websocket):
            async for message in websocket:
                queue.put(message)
                print(message)            
        
        async def main():
            async with serve(echo, self.ip, self.port):
                await asyncio.Future()  # run forever       
        asyncio.run(main())

        # t = threading.Thread(target = thread_in, args=[queue])
        # t.start()

    def listen(self,queue):
        async def func(num):
            for i in range(num):
                #time.sleep(1)#this blocks 1st one 1st.. 1111,2222  not 1212
                await asyncio.sleep(1)
                print(i,num)
            return i

        async def main():
            task1 = asyncio.create_task( func(3) )
            task2 = asyncio.create_task( func(5) )
            re = await task1
            re2 = await task2
            print(re,re2,'finally')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        #asyncio.run(main())

        return

        #def thread_in(queue):
        async def echo(websocket):
            async for message in websocket:
                queue.put(message)
                print(message)

        async def main():
            async with serve(echo, self.ip, self.port):
                await asyncio.Future()  # run forever       
        asyncio.run(main())


    #def broadcast(self,queue):

w = WebSocket('localhost',30021)
q = Queue()
w.cast()

print('done')
exit()


class ClientSend:
    def __init__(self):
        1
    def fire(self):
        async def hello(uri):    
            async with connect(uri) as websocket:
                await websocket.send('sendmessage')
                #msg = await websocket.recv()
                
                #msg = zlib.decompress(msg).decode()
                #msg,ss = json.loads(msg)                
        asyncio.run(hello("ws://localhost:30021"))

class ServerRecv:
    def __init__(self):
        1
    def run(self):      
        async def echo(websocket):
            async for message in websocket:
                print(message)
        
        async def main():
            async with serve(echo, "localhost", 30021):
                await asyncio.Future()  # run forever       
        asyncio.run(main())

#s = ServerRecv()
#s.run()

class ServerSend:
    def __init__(self):
        1
    def run(self):      
        async def echo(websocket):
            async for message in websocket:
                message = time(),[1,2,3,4,56]
                message = json.dumps(message)
                message = zlib.compress(message.encode())
                await websocket.send(message)
        
        async def main():
            async with serve(echo, "localhost", 30020):
                await asyncio.Future()  # run forever       
        asyncio.run(main())



class Inputman(IInputman):
    def __init__(self):
        self.input_queue = Queue()
        self.run()
    def put_input(self, input):
        self.input_queue.put(input)
    def get_input(self):
        # while not self.input_queue.empty():
        #   yield self.input_queue.get()        
        inputs = []
        while not self.input_queue.empty():
            inputs.append(self.input_queue.get())
        return inputs
    
    #seems factory method..
    def open_socket_server(self, queue):
        1
    def run(self):
        # socket = openport(ip,port)
        # while True:
        #   data = get()
        #   queue.put(data)
        #   socket.listen()

        # self.IP
        # self.PORT
        # thread(self.input_queue)
        
        t = threading.Thread(target = self.socket_server_run, args=[self.input_queue])
        t.start()

def main():
    i = Inputman()
    i.put_input('ham')
    #for r in i.get_input():
    #   print(r)
    print(i.get_input())
if __name__ == '__main__':
    main()