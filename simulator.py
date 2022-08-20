import time

from inputman import Inputman

from interface import *

# class ThreadRunner:
#     def run_thread(self, method):
#         1




import sys
def get_sleep_time():
    #https://docs.python.org/3.5/library/sys.html#sys.platform
    if sys.platform == 'win32':
        return 0.001
    else:
        return 15.9
SLEEPTIME = get_sleep_time()



class Simulator(ISimulator):
    def __init__(self, inputman, world, viewman):
        self.inputman = inputman
        self.world = world
        self.viewman = viewman

        self.t_before = 0
        self.running = False
    
    def tick(self):
        tnow = time.time()
        dt = tnow - self.t_before
        self.t_before = tnow

        #process input
        # for i in self.inputman.get_input():
        #     self.world.put_input(i)
        inputs = self.inputman.get_input()
        self.world.put_input(inputs)

        #update
        self.world.update(dt)
        
        #draw
        view_data = world.get_draw()
        self.viewman.put_draw(view_data)

    def run(self):
        self.running = True
        self.t_before = time.time()
        
        while self.running:
            self.tick()
            time.sleep(SLEEPTIME)


i = Inputman()
w = World()
v = Viewman()
Simulator(i,w,v)








'''

class Timer:
    def __init__(self):
        self.time = 0
    def get_dt(self):
        tnow = time.time()
        if not self.time:
            self.time = tnow-0.0001
        dt = tnow - self.time
        self.time = tnow
        return dt


'''