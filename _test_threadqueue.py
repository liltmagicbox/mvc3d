import threading
from queue import Queue
import time

qq = Queue()

def adder(q):
    t = time.time()
    while True:
        for i in range(500):
            time.perf_counter()
        tt = time.time()-t
        q.put(tt, block=False)        

t = threading.Thread(target = adder, args=[qq])
t.start()

while True:
    # if qq.empty():
    #     continue
    #     print('ha')
    
    t = time.time()
    i = 0
    #while not qq.empty():
    while True:
        try:
            g = qq.get(block=False)
            i+=1
        except:
            break
    print(i)
    i = 0
    dt = time.time()-t
    #print(dt)
    if dt>0.001:
        print(dt,'dt')

    time.sleep(0.1)
    
