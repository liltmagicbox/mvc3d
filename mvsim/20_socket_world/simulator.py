import threading
import time

from world import World,Actor
from interface import ISimulator, IViewControl

class Simulator(ISimulator):
    """ Simulator, that simulates world.
    requires IView_Control to init.    
    sim.run(world).
    sim.run(world2)
    sim.pause() (pauses world.update. )
    sim.resume()
    sim._stop() if you want.
    win32, fps ~=70. fine. or sleep_time = 0
    """
    def __init__(self, view_control):
        self.view_control = view_control

        self._flag_stop = threading.Event()
        self._flag_pause = threading.Event()

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
        #self.pause()
        self._stop()
        
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
                draws = world.draw()
                self.view_control.draw(draws)#view_control now another role: event to outer world!
                #lets keep it simple.
                #draw_and_events = world.output()
                #split event, if it's for internal!..nothere. since we split outer event anyway.                

                time.sleep(self._sleep_time)
        
        th = threading.Thread( target = simrun )
        th.start()

        self._flag_stop = flag_stop
        self._flag_pause = flag_pause
    
    def pause(self):
        """stops world update, while in-out still connected. do resume."""
        self._flag_pause.set()        
    def resume(self):
        self._flag_pause.clear()
    def _stop(self):
        """stops thread while, if you want. .run also stops."""
        self._flag_stop.set()





#player press s, swap charactor. c1 -> c2 changed.
#..is player input, not that world-actor path.
#so, virtual local-world player got the raw input,
# vplayer translates via keymap,  (no,if player changes,,) _assume same.
# human press 's' -> controller sends 's' via socket.. /controller has keymap?! great!
# abskey input is comming from socket. view_controll got this.
# userid sent by     view_controller / somewhere stored {port:player}. or {session_key:player}
# anymplayer sends abskey. what's next?
# if the sim accepts anym key, it will send it to .. 'current player'
# or gets player,(actually player actor.). fine.

# anym keyinput -> current player.
# session keyinput -> session's player.

#where current/session player data (dict is fine) is stored?
# human-> viewcontroller -> ~||~ -> SocketViewController -> simulator -> world ->actor.


#VC ->rawinput -> Event ->simulator.
# simulator only accepts Event
# VC only returns rawinput(impossible)

#or simulator holds GameMaster, parse player, parse rawinput, parse XY?
#or VC has Gamemaster, do all and send to sim pared event.(current)

class GameMaster:
    def __init__(self, max_player=4):
        self.max_player = max_player
        self.players = {}

    def add_player(self,player):
        if len(self.players)<self.max_player:
            self.players[player_id] = player

def player_to_actor(player_id):
    player_id



#simulator.put(event)

#import event #now sim has no rel.with sim!

from queuerecv import QueueRecv,QueueRecvClient, Sender, Caster


class SocketViewController(IViewControl):
    def __init__(self, inport=30020, outport=30021):
        self.queue = QueueRecv(port = inport, verbose=True)
        self.caster = Caster(port = outport, verbose=True)
    #===api
    def get_inputs(self):
        "raw_input/eventdict -> [Event]"
        return [i for i in self.queue.get_all()]#now viewController outs rawinput/eventdict.
        #events = event.parse(i)
        #yield from events
    def draw(self,draws):#and events.
        real_draws = draws.get('draws')
        self.caster.cast(real_draws)

class SocketSimulator(Simulator):
    def __init__(self):
        view_control = SocketViewController()
        super().__init__(view_control)




def socketsimultaing():

    sim = SocketSimulator()
    world = World()
    actor = Actor()
    world.add(actor)
    world.default_player.target = actor

    sim.run(world)

    time.sleep(2)
    sim.pause()








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


    class ViewControl:
        #===api
        def get_inputs(self):
            return []
        def draw(self,draws):
            print(len(draws) )

    

    v = ViewControl()

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

