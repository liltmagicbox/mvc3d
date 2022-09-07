import socket

class Server:
    def __init__(self, host='localhost', port=30030):        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind( (host,port) )
        server_socket.listen()
        
        conn, addr = server_socket.accept()
        self.conn = conn
    
    def run(self):
        while True:
            strdata = self.conn.recv(16).decode()
            #print(strdata)
            
            if strdata == 'get':
                strdata = 'fulldataall'

                blen = str(len(strdata)).encode()
                self.conn.sendall(blen)
                self.conn.sendall(strdata.encode())
                #self.conn.send(f"{dlen}".encode())
            elif strdata == 'put':
                blen = int( self.conn.recv(16).decode() )
                print(blen)            
                strdata = self.conn.recv(blen).decode()
                print(strdata)            

                        

    def put(self,data):
        1
    def get(self):
        strdata = self.conn.recv(1024).decode()
        if strdata == 'key':
            keys = '[1,2,3]'.encode()
            self.conn.sendall(keys)
        elif 'view' in strdata:
            print(strdata)
            strdata
            buffersize=2
            data=[]
            while True:
                chunk = self.conn.recv(buffersize)
                print(chunk)
                data.append(chunk)                
            fulldata = b''.join(data)
            return fulldata

s = Server()
s.run()

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