import uuid
import math
from queue import Queue

from interface import IWorld,IActor
import event

def uuidstr():
    return str(uuid.uuid4()).replace('-','_')

class World(IWorld):
    """
    world not method of: get_player_target(player_id)->actor_id.
    #final data actor_id is very close to world itself. not sim!
    #maybe world has event_console kinds, verbose=True??
    """
    def __init__(self):
        self.id = uuidstr()

        self.actorDict = {}
        self.playerDict = {}#or class Players()?

        self.event_queue = Queue()#internal usage!        
    def add(self,actor):
        self.actorDict[actor.id] = actor
    def remove(self,actor):
        if actor.id in self.actorDict:
            self.actorDict.pop(actor.id)
    def get(self,actor_id):
        return self.actorDict.get(actor_id)

    def get_player_target(self, player_id):
        if player_id in self.playerDict:#7%faster, .get(id).
            player = self.playerDict[player_id]
            return player.target

    def put_event(self, event):        
        event.world = self.id#all created by here.
        self.event_queue.put(event)
    def get_events(self):
        queue = self.event_queue
        while not queue.empty():
            yield queue.get()

    #======API
    def input(self, rawEvent):
        "rawE->E', E'->E_targeted. instant execution!"
        events = event.parse(rawEvent)#dict->E, E->E, EXY-> EX,EY
        for parsedEvent in events:
            if parsedEvent.target == None:
                actor_id = self.get_player_target(parsedEvent.player)
                parsedEvent.target = actor_id
            self._input_Event(parsedEvent)

    def _input_Event(self, Event_targeted):
        "Event_targeted -> actor"
        actor = self.get(Event_targeted.target)
        if actor:
            actor.input(Event_targeted)

    def output(self):
        "world -> E_outer, draws"
        for_outer_world = []
        for Event in self.get_events():
            if Event.world == self.id:#is it for this world?
                self.put_event(Event)
            else:
                for_outer_world.append(Event)
        #===draw
        draws = self._draw()
        return {'draws':draws, 'events':for_outer_world}
    
    def update(self,dt):        
        "internal Event loopback system."
        for e in self.get_events():#events from last update
            self._input_Event(e)
        
        #============
        for id,actor in self.actorDict.items():
            if id=='5549':
                continue
            actor.update(dt)
        #self.put_event(Event)
    
    def _draw(self):
        draws = {}
        for id,actor in self.actorDict.items():
            draw_data = {'pos':actor.pos}
            draws[actor.id] = draw_data
        return draws
    




keymap_general={
    'F':'jump',
    'W':'move_forward*1.0',
    'MOUSE_X': 'setx*1',
    'MOUSE_Y': 'sety*-1',
}


def keymap_parse(actor,keymap,i):
    if i.key in actor.keymap:
        funcname = actor.keymap[i.key]
        
        if '*' in funcname:
            funcname, mul = funcname.split('*')
            mul = float(mul)
        else:
            mul = None
        if hasattr(actor, funcname):
            func = getattr(actor,funcname)
            if mul == None:
                if i.value>0:
                    func()
            else:
                func(i.value*mul)


class Actor:
    count = 0
    def __init__(self):
        self.id = str(uuid.uuid4()).replace('-','_')
        self.name = f"{self.__class__.__name__}_{Actor.count}"
        Actor.count += 1
        #===
        #self.keymap = {'f':lambda actor,key,value:print('-input:',actor,key,value)}
        self.keymap = keymap_general
        self.pos = [0,0,0]
        #===
        self.t = 0
    def __repr__(self):
        return f"{self.name}"

    def update(self,dt):
        self.t+=dt
        x = math.cos(self.t)*0.8
        y = math.sin(self.t)*0.8
        self.pos[0:2] = x,y

    def input(self,i):        
        keymap_parse(self,self.keymap, i)
    
    def jump(self):
        print('jump!')
    def setx(self, x):
        self.pos[0] = x
    def sety(self, y):
        self.pos[1] = y



def main():
    w=World()
    
    a = Actor()
    w.add(a)

    ee = event.Key('F',1.0, target = a.id)
    w.input(ee)

if __name__ == '__main__':
    main()




