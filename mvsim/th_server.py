import socket


class Server:
    def __init__(self, host='localhost', port=30030):        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind( (host,port) )
        server_socket.listen()
        
        conn, addr = server_socket.accept()
        self.conn = conn
    
    def run(self):
        1
    def put(self,data):
        1
    def get(self):
        strdata = self.conn.recv(1024).decode()
        if strdata == 'key':
            keys = '[1,2,3]'.encode()
            self.conn.sendall(keys)
        elif strdata == 'view':
            strdata = self.conn.recv(1024).decode()
        
        return strdata

s = Server()

while True:
    data = s.get()
    if not data:
        break
    print(data)

exit()

#keys = [1,2,3]
#s.put(keys)

import time

while True:
    x = s.get()
    print(x)
    time.sleep(1)










while True:
    data = conn.recv(1024)
    if not data:
        break
    
    if data.decode() == 'input':
        1



class Server:
    def put(self,data):
        1
    def get(self):

        return data

    def __init__(self, host='localhost', port=30030):
        def runserver(connected):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(1)
            server_socket.bind( (host,port) )            
            
            server_socket.listen()
            conn, addr = server_socket.accept()
            connected = True

            while True:
                header = conn.recv(8).decode()
                if not header:
                    break
                if header == 'key':
                    conn.sendall('keykeykeykeykeykeykeykeykey'.encode())
                
                elif header == 'view':
                    views = []
                    while True:
                        data = conn.recv(4096)
                        views.append(data)
                        if not data:
                            break
                    strdata = b''.join(views).decode()
                    print(strdata)
        
        self.connected = False
        th = threading.Thread( target = runserver, args=(self.connected,) )
        th.start()

#s = Server()

# port = Port()
# port.run()

# while True:
#     keys = []
#     while not queue.empty():
#         key = queue.get()
#         keys.append(key)
#     port.put( keys)
    
#     view = port.get()
#     # if not view:
#     #     view = []
#     cast(view)