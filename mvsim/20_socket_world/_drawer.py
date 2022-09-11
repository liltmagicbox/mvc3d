from queuerecv import QueueRecvClient
import time

q = QueueRecvClient(verbose=True)

while True:
    for i in q.get_all():
        print('draw',i)
    time.sleep(0.1)
