import threading
import time

class World:
    def __init__(self):
        self.actors = []
    def add(self,actor):
        self.actors.append(actor)
    #===api
    def input(self,Event):
        print(' input-> world ', Event)
    def update(self,dt):
        self.actors.append(2)
    def get_draw(self):
        return self.actors


class Viewer:
    #===api
    def get_inputs(self):
        return []
    def draw(self,draws):
        print(len(draws) )


class Simulator:
    """ Simulator, that simulates world.
    requires View_Control, API of .get_inputs()->[i], .draw(draws)

    sim.run(world).
    sim.run(world2)
    sim.pause() (pauses world.update. )
    sim.resume()
    sim.stop() if you want.
    win32, fps ~=70. fine. or sleep_time = 0
    """
    def __init__(self, view_control):
        self.view_control = view_control

        self._flag_stop = None
        self._flag_pause = None

        self._sleep_time = 0.014#60fps windows.

    @property
    def sleep_time(self):
        return self._sleep_time
    @sleep_time.setter
    def sleep_time(self,value):
        self._sleep_time = value        
    
    @property
    def fps(self):
        return round(1/self._sleep_time , 3)
    @fps.setter
    def fps(self,value):        
        value = 1/value
        self._sleep_time = value
    

    def run(self,world):
        """simulate world. world API: .input(i) .update(dt) .get_draw()->draws"""
        self._stop()
        self.pause()
        
        flag_stop = threading.Event()
        flag_pause = threading.Event()
        def simrun():
            t = time.perf_counter()
            t_before = t
            while not flag_stop.is_set():
                t = time.perf_counter()
                dt = t - t_before
                t_before = t

                #===input update draw
                #=input
                for i in self.view_control.get_inputs():
                    world.input(i)
                #=update
                if not flag_pause.is_set():
                    world.update(dt)

                #=draw
                draws = world.get_draw()
                self.view_control.draw(draws)

                time.sleep(self._sleep_time)
        
        th = threading.Thread( target = simrun )
        th.start()
        
        self._flag_stop = flag_stop
        self._flag_pause = flag_pause
    
    def pause(self):
        """stops world update, while in-out still connected. do resume."""
        if self._flag_pause:
            self._flag_pause.set()
    def resume(self):
        if self._flag_pause:
            self._flag_pause.clear()
    def _stop(self):
        """stops thread while, if you want. .run also stops."""
        if self._flag_stop:
            self._flag_stop.set()    









import event

from queuerecv import QueueRecv,QueueRecvClient, Sender, Caster

class SocketViewer:
    def __init__(self):
        self.queue = QueueRecv(verbose=True)
        self.caster = Caster(verbose=True)
    #===api
    def get_inputs(self):
        """here gets raw dict data. which shall be Event class.."""
        for i in self.queue.get_all():
            events = event.parse(i)
            yield from events
    def draw(self,draws):
        self.caster.cast(draws)

class SocketSimulator(Simulator):
    def __init__(self):
        view_control = SocketViewer()
        super().__init__(view_control)


def socketsimultaing():

    a = SocketSimulator()
    world = World()
    world.add(1)
    a.run(world)

    time.sleep(2)
    #a.pause()







def main():
    socketsimultaing()

if __name__ == '__main__':
    main()







#====do we needit??  it's old design. bury it.
#===was good but client side.
# from portqueue import PortQueue

# class PortViewer:
#     def __init__(self):
#         self.inputs = []
#         self.queue = PortQueue()
#     #===api
#     def get_input(self):
#         for i in self.queue.get_all():            
#             yield i
#     def draw(self,draws):
#         print(len(draws) )


# class PortSimulator(Simulator):
#     def __init__(self):
#         vc = PortViewer()
#         super().__init__(vc)












#just remember win you use 90fps ~65fps, or 30fps or 15fps.. if fullspeed, sleep_time=0.
# import sys
# SYS_MIN_SLEEP_TIME = 0.001#1000fps will be fine..
# if sys.platform == 'win32':
#     SYS_MIN_SLEEP_TIME = 0.0029
#time.sleep(0.000001)#65fps
#time.sleep(0.0140)#65fps
#time.sleep(0.0141)#46fps

#time.sleep(0.015)#46fps
#time.sleep(0.020)#34fps
#time.sleep(self._sleep_time-SYS_MIN_SLEEP_TIME)




def run_fps_test():

    

    v = Viewer()

    #print(help(Simulator))
    world = World()
    world.add(1)

    s = Simulator(v)
    s.run(world)

    time.sleep(2)

    world.add(99)
    print(world)
    world = None#not affects the one in the thread.
    print(world)



    world = World()
    print(world)
    s.sleep_time = 0.5
    print(s.fps)
    s.run(world)

    print(dir(s))
    time.sleep(3)

    world = World()
    print(world)
    for i in range(100):
        world.add(99)
    s.fps = 30
    print(s.fps,s.sleep_time)
    s.run(world)


    time.sleep(3)
    s.pause()
    for i in range(10):
        print(len(world.actors),'pausing')
        time.sleep(0.1)
    s.resume()
    time.sleep(1)
    s._stop()

