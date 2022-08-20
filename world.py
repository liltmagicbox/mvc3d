
GROUP_DURINGPHYSICS = 2

class World:
    def __init__(self):
        self.actors = {}
        self.actorsAXIS = {}

        self.actorgroup = {}
        self.AXIS = None

    def add(self,actor):
        self.actors[actor.id] = actor
    def remove(self,actor):
        if actor.id in self.actors:
            self.actors.pop(actor.id)
    def update(self,dt):
        for group, actors in self.actorgroup.items():
            if group == GROUP_DURINGPHYSICS:
                if self.AXIS:
                    self.AXIS.update(dt)
                for actor in self.actors.values():#all actors!
                    actor.update_physics(dt)
                for actor in actors:
                    actor.update(dt)
            else:
                for actor in actors:
                    actor.update(dt)
            
            # for actor in actors:
            #     actor.update_pre(dt)
            # if not group == GROUP_NOPHYSICS:
            #     for actor in actors:
            #         actor.update_physics(dt)
            # for actor in actors:
            #     actor.update(dt)

    def put(self, commands):
        #command = {'key':'k','target':3383(controller id), ('time') }
        #commands = {id:[key,]}
        for controller_id, keys in commands.items():
            if controller_id in self.actors:
                controller = self.actors[controller_id]
                for key in keys:
                    controller.input_key(key,value)

    def eventHandle(self,events):
        for event in events:
            if event.type in self.eventListener:
                for actor in self.eventListener[event.type]:
                    actor

    def get(self):
        vs=[]
        for actor in self.actors.values():
            v=actor.get_view()
            vs.append(v)
        return vs
