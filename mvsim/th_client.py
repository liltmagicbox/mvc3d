import socket

host='localhost'
port=30030

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect( (host,port) )

client.sendall('key'.encode())
data = client.recv(4096)
print(data)

import time
time.sleep(1)

client.sendall('view'.encode())

client.sendall('worldview'.encode())

time.sleep(3)