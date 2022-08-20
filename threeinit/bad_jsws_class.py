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



# ws = JSWebSocket()
# def read(msg):
#     print(msg,'read')
# ws.onmessage = read

# for i in range(1000000):
#     ws.send(str(i)+'keyboard')
#     time.sleep(0.5)




#====================


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
    