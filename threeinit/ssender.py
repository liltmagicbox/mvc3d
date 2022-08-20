import socket
import threading

class Sender:
	def __init__(self, host='localhost', port=30020):
		#self.host = host
		#self.port = port
		
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect( (host,port) )

		bdata = 'hellddddddddddddddddddddddddddddddddo'.encode()
		client.sendall( bdata )

		self.client = client
	#def send(self, message):
	
	def close(self):
		self.client.close()


s = Sender()
#s.close()


#data = client.recv(4096)


for i in input_queue:
	process(i)
world.update(dt)

vs = world.get_view()
#cast(vs)
for i in vs:
	output_queue.put(i)
