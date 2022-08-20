import websocket
import threading


CLOSED = 0
CONNECTING = 1
CONNECTED = 2
CLOSING = 3


class WSClient:
    def __init__(self, host='localhost',port=30020):
        uri=f"ws://{host}:{port}/"

        ws = websocket.WebSocket()
        self.ws = ws
        self.state = CONNECTING

        self.on_message = None
        self.on_close = None
        self.on_error = None
        self.on_open = None

        def connect():
            try:
                ws.connect(uri)
                self.state = CONNECTED
                self._on_open()
            except ConnectionRefusedError:
                connect()
                return

            while True:
                try:
                    data = ws.recv()
                    self._on_message(data)
                except (ConnectionResetError):
                    self.state = CLOSED
                    self._on_close()
                    break
            connect()

        t = threading.Thread(target = connect)
        t.start()

        #websocket._exceptions.WebSocketPayloadException: cannot decode: b'\x81\x1b2022-08-15T18:18:35.71835'
        #websocket._exceptions.WebSocketProtocolException: rsv is not implemented, yet
        
    def send(self, data):
        if not self.state == CONNECTED:
            return
        try:
            self.ws.send(data)        
        #except ():
        except websocket._exceptions.WebSocketConnectionClosedException:
            print('canyouseethis'*200)
            self.state = CLOSED
            self._on_error()
            self._on_close()
        #self.ws.send(data)#ConnectionResetError: [WinError 10054] 현재 연결은 원격 호스트에 의해 강제로 끊겼습니다
        #self.ws.send(data)#ConnectionAbortedError: [WinError 10053] 현재 연결은 사용자의 호스트 시스템의 소프트웨어의 의해 중단되었습니다
        #..when if ..whole process done.

    def _on_message(self, data):
        if self.on_message:
            self.on_message(data)
    def _on_open(self):        
        if self.on_open:
            self.on_open('e')    
    def _on_error(self):
        if self.on_error:
            self.on_error('e')
    def _on_close(self):
        if self.on_close:
            self.on_close('e')


def main():
    import time
    ws = WSClient()
    def mas(m):
        print(m,'recved')
    ws.on_message = mas
    ws.on_open = lambda x: print('open')
    ws.on_close = lambda x: print('close')
    while True:
        ws.send('encoded'.encode('utf-8'))#is sent str.
        time.sleep(2)

if __name__ == '__main__':
    main()

