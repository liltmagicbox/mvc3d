import websocket
import time
import threading

#https://websocket-client.readthedocs.io/en/latest/examples.html#dispatching-multiple-websocketapps
#timeout whatever serverconnection fails, happend..maybe.

#https://websocket-client.readthedocs.io/en/latest/examples.html#creating-your-first-websocket-connection
#websocket.enableTrace(True)

info="""
websocket-client
is good oop thread style.

websockets can both server,client.
but using async, not friendly for client.

it 1st time connects via http. and seems using 80port..
likely using socket , but seems has own protocol
we can brutely create socket server doing websocket,but..

UE4 supports both socket
chrome only suppoerts(!) websocket.
py do both.
not that slow. has some lib to speedup, but seems ~20, x2, forget it.

internal seems using network bandwidth.

need to keep connection connected.
way 1: ws=WS(), in loop (thread)
way 2: app.run()
"""


def send_once(msg='default message'):    
    ws = websocket.WebSocket()#create instance. it can be in thread.
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors. t=9 seems weird
    ws.send(msg)#send msg
    #connection close


def app_echo():
    """app style. blocked"""
    def on_message(wsapp, message):
        wsapp.send('echo'+message)
        print(message)

    websocket.setdefaulttimeout(2)#if connection failed, next, without error.    
    wsapp = websocket.WebSocketApp("ws://localhost:30020", on_message=on_message)
    print('runningforerver')
    wsapp.run_forever()
    print('done')


#to simple, can use method(message)
#on close -> create block actor, via pos protocol. try reconnect.
#on open -> remove block, if exists.
#on message -> process that.

#a.onmessage = lambda data: print('data',data)
#a.onclose = lambda event: print('aaaaaaaaaaaaaaaaa)',event)
#a.send('ham')

#while closed, try send again, cause many onclose.. we need flag.


def instance_thread(msg='default message'):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:30020",timeout=2)#if server connect fail, errors.    
    #ws.send(msg)
    
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


def app_thread():
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


