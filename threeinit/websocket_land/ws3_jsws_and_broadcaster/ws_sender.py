import websocket
import time
import threading

#https://websocket-client.readthedocs.io/en/latest/examples.html#dispatching-multiple-websocketapps
#timeout whatever serverconnection fails, happend..maybe.


#https://websocket-client.readthedocs.io/en/latest/examples.html#creating-your-first-websocket-connection
#websocket.enableTrace(True)

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


class JSWebSocket:
    """
    ws = WebSocket(uri)
    ws.onmessage = lambda data:print(data)
    ws.send( JSON.stringify( {action:'keypress'} ) )
    """
    def __init__(self, uri='ws://localhost:30020/'):
        ws = websocket.WebSocket()
        ws.connect(uri)#timeout=2 if server connect fail.
        self.ws = ws
        self.onmessage = lambda data:print('onmessage',data)        
        def receive_endless():
            while True:
                try:
                    data = ws.recv()#ConnectionResetError                
                    self.onmessage(data)
                except ConnectionResetError:
                    #print('server disconnected. finish while,thread.')
                    break
        t = threading.Thread(target = receive_endless)
        t.start()
    def send(self, data):
        self.ws.send(data)

a = JSWebSocket()
a.onmessage = lambda data: print('data',data)
#a.send('ham')

for i in range(100):
    time.sleep(2)
    print('haaaaa')
    a.onmessage = lambda data: print('data',data,i)
    a.send(f"howmany{i}")

exit()



def instance_send_recv(msg='default message'):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.    
    ws.send(msg)
    
    qq = Queue()

    def rec(qq):
        while True:
            d = ws.recv()
            qq.put(d)
    t = threading.Thread(target = rec, args=[qq])
    t.start()

    while True:
        if not qq.empty():
            d = qq.get()
            print(d)
        time.sleep(0.1)
        ws.send(msg)
        print('/',end='')

#instance_send_recv()


def app_send_recv():
    def on_message(wsapp, message):
        #wsapp.send('echo'+message)#works fine!
        print(message)

    websocket.setdefaulttimeout(2)#if connection failed, next, without error.
    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    
    def runner():
        wsapp.run_forever()
    threading.Thread(target = runner).start()    

    while True:
        time.sleep(0.1)        
        wsapp.send('ha')
        #websocket._exceptions.WebSocketConnectionClosedException: Connection is already closed.
    print('done')

app_send_recv()
exit()

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


# class Sender:
#     @classmethod
#     def websocket(cls):
#         return ws
#     @classmethod
#     def socket(cls):
#         return ws




class Factory:
    #def __init__(self, iswebsocket=False):
        #if:
    def __init__(self, socketfactory):
        self.socketfactory = socketfactory
    @classmethod
    def Sender(cls, ip,port):
        return self.socketfactory.Sender(ip,port)
    @classmethod
    def Receiver(cls, ip,port,queue):
        return self.socketfactory.Receiver(ip,port,queue)


class Factory_ver2:
    @classmethod
    def Sender(cls, ip,port):
        #if:===is bad structure. ..not that in 2 kinds though.
        return WSSender(ip,port)
    @classmethod
    def Receiver(cls, ip,port,queue):
        return WSReceiver(ip,port,queue)


# qq = Queue()
# w = WSReceiver(queue = qq)
# while True:
#     print('/',end='')
#     for i in w.get_all():
#         print(i)
#     time.sleep(0.1)



s = WSSender()
s.send('ha')


