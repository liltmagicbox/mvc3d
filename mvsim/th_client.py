import socket

host='localhost'
port=30030

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect( (host,port) )


def get(sock):
    sock.sendall('get'.encode())
    dlen = int( sock.recv(16).decode() )
    print(dlen)
    return recvall(sock, dlen)

def recvall(sock, n):
    maxbuffer = 2**10
    
    data = bytearray()
    while len(data) < n:
        remain_bytes = n-len(data)
        recvlen = maxbuffer if remain_bytes>maxbuffer else remain_bytes
        packet = sock.recv(recvlen)
        if not packet:
            return None
        data.extend(packet)
    return data

def put(sock,data):
    sock.sendall('put'.encode())
    blen = str(len(data)).encode()
    sock.sendall(blen)
    sock.sendall(data.encode())
                

import time
while True:
    get(client)
    put(client, 'thisisdata')
    time.sleep(1)



print(data,'recv')


bdata = 'worldviewx'.encode()
blen = len(bdata)

client.sendall(f'view{blen}'.encode())
client.sendall(bdata)

time.sleep(3)
#client.close()

"""
1. server recvs.
2. client sends init msg (input,output..), recvs
3. server parse msg, sends pre-data
4. client recvs pre-data, recvs.
5. server sends data
6. client recvs data
"""

