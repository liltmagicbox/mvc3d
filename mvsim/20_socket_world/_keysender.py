from queuerecv import Sender


import time

s = Sender(host='192.168.0.47', verbose=True)

data = round(time.time()%10,3)
while True:
	senddata = { 'Key': ['k', 1.0, data] }
	s.send(senddata)
	time.sleep(0.1)
