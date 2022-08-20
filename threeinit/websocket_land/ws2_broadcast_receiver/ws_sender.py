import websocket
import time
import threading

#https://websocket-client.readthedocs.io/en/latest/examples.html#dispatching-multiple-websocketapps
#timeout whatever serverconnection fails, happend..maybe.


def once(msg='default message'):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.    
    ws.send(msg)    

def app_echo():
    print('runningforerver')
    def on_message(wsapp, message):
        wsapp.send('echo'+message)
        print(message)

    websocket.setdefaulttimeout(2)#if connection failed, next, without error.
    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    wsapp.run_forever()
    print('done')


#once()
#app_echo()





import websocket
import threading
from queue import Queue

class WSSender:
    def __init__(self,ip='localhost',port=30020):
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{ip}:{port}")
        #timeout=2, #if server connect fail, errors.
    def send(self, msg='message from WSSender'):
        self.ws.send(msg)

class WSReceiver:
    def __init__(self,ip='localhost',port=30020, queue = None ):
        if queue==None:
            queue = Queue()
        self.queue = queue

        def apprunner(queue):
            def on_message(wsapp, message):
                queue.put(message)
            
            #websocket.setdefaulttimeout(2)#if connection failed, next, without error.
            wsapp = websocket.WebSocketApp(f"ws://{ip}:{port}", on_message=on_message)
            wsapp.run_forever()
        
        th = threading.Thread( target=apprunner, args=[queue])
        th.start()
        self.th = th
    
    def get_all(self):
        data = []
        try:
            data.append( self.queue.get(block=False) )
        finally:
            return data
        #while not self.queue.empty():


w = WSReceiver()
while True:
    print('/',end='')
    for i in w.get_all():
        print(i)
    time.sleep(0.1)


