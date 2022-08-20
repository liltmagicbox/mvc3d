import socket
import threading
import time


class Receiver:
    def __init__(self, host='localhost', port=30020):
        #self.host = host
        #self.port = port
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#port used 10048
        #and happens:[WinError 10013] 액세스 권한에 의해 숨겨진 소켓에 액세스를 시도했습니다
        server_socket.bind( (host,port) )
        server_socket.listen()

        client_socket, addr = server_socket.accept()

        #print(dir(client_socket))
        while True:
            data = client_socket.recv(4)
            print(data)
            time.sleep(1)
        client_socket.close()
        server_socket.close()

        #except ConnectionResetError as e:
Receiver()
