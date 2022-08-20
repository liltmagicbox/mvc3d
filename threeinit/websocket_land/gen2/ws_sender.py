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



#on close -> create block actor, via pos protocol. try reconnect.
#on open -> remove block, if exists.
#on message -> process that.

#while closed, try send again, cause many onclose.. we need flag.



import websocket
import threading
from queue import Queue

CLOSED = 0
CONNECTING = 1
CONNECTED = 2
CLOSING = 3

STATES ={
    CLOSED:[CONNECTING],
    CONNECTING:[CLOSED,CONNECTED],
    CONNECTED:[CLOSED],
    CLOSING:[CLOSED],
}

DISCONNECTED = (ConnectionResetError,
    )
x=(
        ConnectionResetError, ConnectionAbortedError,
        websocket._exceptions.WebSocketConnectionClosedException
        )



class JSWebSocket:
    def __init__(self, uri='ws://localhost:30020/'):
        ws = websocket.WebSocket()
        self.ws = ws
        self.state = CONNECTING

        self.onmessage = None
        self.onclose = None
        self.onerror = None
        self.onopen = None

        def connect():
            print('connect inti')
            try:
                ws.connect(uri)
                self.state = CONNECTED
            except ConnectionRefusedError:
                connect()
                return

            while True:
                try:
                    data = ws.recv()
                    self._on_message(data)
                except (ConnectionResetError):
                    self.state = CLOSED
                    break
            connect()

        t = threading.Thread(target = connect)
        t.start()

        #websocket._exceptions.WebSocketPayloadException: cannot decode: b'\x81\x1b2022-08-15T18:18:35.71835'
        #websocket._exceptions.WebSocketProtocolException: rsv is not implemented, yet
        
    def send(self, data):
        if not self.state == CONNECTED:
            return        
        print('send')
        try:
            self.ws.send(data)        
        #except ():
        except websocket._exceptions.WebSocketConnectionClosedException:
            print('some='*200)
            self.state = CLOSED
            self._on_error()
            self._on_close()
        #self.ws.send(data)#ConnectionResetError: [WinError 10054] 현재 연결은 원격 호스트에 의해 강제로 끊겼습니다
        #self.ws.send(data)#ConnectionAbortedError: [WinError 10053] 현재 연결은 사용자의 호스트 시스템의 소프트웨어의 의해 중단되었습니다
        #..when if ..whole process done.

    def _on_message(self, data):
        if self.onmessage:
            self.onmessage(data)
    def _on_open(self):        
        if self.onopen:
            self.onopen('e')    
    def _on_error(self):
        if self.onerror:
            self.onerror('e')
    def _on_close(self):
        if self.onclose:
            self.onclose('e')



# ws = None

# def connect():
#     global ws
#     ws = JSWebSocket()
    
#     def read(msg):
#         print(msg,'read')
#     ws.onmessage = read
#     def close(e):        
#         print('closed!')
#         connect()
#     ws.onclose = close

# connect()

ws = JSWebSocket()
def read(msg):
    print(msg,'read')
ws.onmessage = read


for i in range(1000000):
    ws.send(str(i)+'keyboard')
    time.sleep(0.5)

exit()



class JSWebSocket:
    """
    ws = WebSocket(uri)
    ws.onmessage = lambda data:print(data)
    ws.send( JSON.stringify( {action:'keypress'} ) )
    """
    def __init__(self, uri='ws://localhost:30020/'):
        self.state = CLOSED
        self.ws = websocket.WebSocket()
        self.uri = uri

        self.onmessage = None
        self.onclose = None
        self.onerror = None
        self.onopen = None
        #lambda data: print('onmessage',data)
        #lambda event=None: print('socket closed (by server)')

        self.connect()

    @property
    def connected(self):
        return self.state == CONNECTED        
    
    def connect(self):
        if not self.state == CLOSED:
            return        
        
        self.state = CONNECTING

        def inner_connect():
            try:
                self.ws.connect(self.uri)#timeout=2 if server connect fail.
                #socket.timeout: timed out
                #ConnectionRefusedError: [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다
            except ConnectionRefusedError:
                self.state = CLOSED
                self._on_error()
                self._on_close()
                "WebSocket connection to 'ws://localhost:30020/' failed: "
                return
            self.state = CONNECTED
            self._on_open()
            self.receive_forever()
        t = threading.Thread(target = inner_connect)
        t.start()        

    def receive_forever(self):
        if not self.connected:
            return

        def inner_forever():
            while self.connected:
                try:
                    data = self.recv()#ConnectionResetError
                    #websocket._exceptions.WebSocketPayloadException: cannot decode: b'\x81\x1b2022-08-15T18:18:35.71835'
                    #websocket._exceptions.WebSocketProtocolException: rsv is not implemented, yet
                    self._on_message(data)
                except ConnectionResetError:
                    #print('server disconnected. finish while,thread.')
                    self._on_error()
                    self._on_close()
                    break
        t = threading.Thread(target = inner_forever)
        t.start()

    def send(self, data):
        #self.ws.send(data)#ConnectionResetError: [WinError 10054] 현재 연결은 원격 호스트에 의해 강제로 끊겼습니다
        #self.ws.send(data)#ConnectionAbortedError: [WinError 10053] 현재 연결은 사용자의 호스트 시스템의 소프트웨어의 의해 중단되었습니다
        #..when if ..whole process done.
        if not self.connected:
            return
        self.ws.send(data)

        # try:
        #     self.ws.send(data)
        # except ConnectionResetError:
        #     self._on_error()
        #     self._on_close()
    def recv(self):
        if not self.connected:
            return
        return self.ws.recv()


    def _on_message(self, data):
        if self.onmessage:
            self.onmessage(data)

    def _on_open(self):        
        if self.onopen:
            self.onopen('e')
    
    def _on_error(self):
        print('error')
        if self.onerror:
            self.onerror('e')

    def _on_close(self):
        print('close')
        if not self.connected:
            return        
        print('ccccccccccccccccccccc\n ccccccccccccccccccccccccc')
        def inner_close():
            self.onclose('c')
        t = threading.Thread(target = inner_close)
        t.start()
        #we need thread, as doc said. send brings this, mainthread endless block.
        #need thread.see api.



def run():
    print('wsgo')
    ws = JSWebSocket()
    print('done anyway fast.')

    def reconnect(e):
        print('reeeeeeeeeeeeeeeee')
        ws.connect()        

    def parse(msg):
        print(msg,'onmsg')
    
    ws.onopen
    #ws.onerror = reconnect
    ws.onclose = reconnect
    ws.onmessage = parse

    while True:
        ws.send('ham')
        time.sleep(0.1)
    
run()

exit()

#a.onmessage = lambda data: print('data',data)

#a.onclose = lambda event: print('aaaaaaaaaaaaaaaaa)',event)
#a.onclose = lambda event: a.reconnect()

#a.send('ham')

for i in range(100):
    time.sleep(2)
    print('haaaaa')
    a.onmessage = lambda data: print('data',data,i)
    #a.send(f"howmany{i}")

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


