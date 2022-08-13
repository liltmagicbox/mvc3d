from vec import Vec3,Euler

import uuid

class Actor:
    _id = 0    
    def __init__(self):
        self._pos = Vec3(0,0,0)
        self._speed = Vec3(0,0,0)
        self._acc = Vec3(0,0,0)
        
        self._rot = Euler(0,0,0)
        self._rotspeed = Euler(0,0,0)
        self._rotacc = Euler(0,0,0)

        self._scale = Vec3(1,1,1)

        self._grav_acc = Vec3(0,0,0)
        
        self.id = self.__class__._id
        self.__class__._id+=1
        
        self.uuid = str(uuid.uuid4()).replace('-','_')

        self.name = ''
        self.type = self.__class__.__name__

    def __repr__(self):
        return f"{self.type} name:{self.name} id:{self.id} uuid:{self.uuid} pos:{self._pos}"

    @staticmethod
    def _parse2d(value):
        x,y,*z = value
        #print(bool(z),'boo',z)#True boo [0]
        if z:
            value = x,y,z[0]
        else:
            value = x,0,y
        return value
    
    #===pos rot scale
    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self,value):
        x,y,z = value
        self._scale.set(x,y,z)

    @property
    def grav_acc(self):
        return self._grav_acc
    @grav_acc.setter
    def grav_acc(self,value):
        x,y,z = value
        self._grav_acc.set(x,y,z)

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        x,y,z = value
        self._pos.set(x,y,z)    
    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self,value):
        x,y,z = value
        self._speed.set(x,y,z)
    @property
    def acc(self):
        return self._acc
    @acc.setter
    def acc(self,value):
        x,y,z = value
        self._acc.set(x,y,z)

    @property
    def rot(self):
        return self._rot
    @rot.setter
    def rot(self,value):
        x,y,z = value
        self._rot.set(x,y,z)    
    @property
    def rotspeed(self):
        return self._rotspeed
    @rotspeed.setter
    def rotspeed(self,value):
        x,y,z = value
        self._rotspeed.set(x,y,z)
    @property
    def rotacc(self):
        return self._rotacc
    @rotacc.setter
    def rotacc(self,value):
        x,y,z = value
        self._rotacc.set(x,y,z)
    #===pos rot scale


    #===game vector kinds
    @property
    def front(self):
        return self._pos.to_front()

    #===function
    def update(self,dt):
        1

    def update_physics(self, dt):
        if self.grav_acc:
            self.speed += self.grav_acc*dt
        
        if self.acc:
            self.speed += self.acc*dt
        if self.speed:
            self.pos += self.speed*dt

        if self.rotacc:
            self.rotspeed += self.rotacc*dt
        if self.rotspeed:
            self.rot += self.rotspeed*dt
    def update_pre(self,dt):
        1
    def update_post(self,dt):
        1#self.update_physics(dt)

    def to_matrix(self):
        return 1
        axis,th = quataxis(glmmat.vec3(world.front), glmmat.vec3(self.front))
        worldrot = glmmat.rotmat(axis,th)
        #return worldrot

        #print(world.front, self.front, worldrot)
        
        #worldrot = mrotv(vec3(1,0,0), self.front)#

        #mmodel = eye4()
        #mmodel = mtrans(self.pos)@worldrot@mrotxyz(self.rotxyz)@mscale(self.scale)@mmodel
        #mmodel = mtrans(self.pos)@worldrot@mrotxyz(self.rotxyz)@mscale(self.scale)
        #mmodel = mtrans(self.pos)
        mmodel = mtrans(self.pos)@worldrot@mrotxyz(self.rotxyz)@mscale(self.scale)
    def get_view(self):
        return {'id':self.id, 'pos':self.pos, 'rot':self.rot, 'scale':self.scale}

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
                for actor in actors:
                    actor.update(dt)
                for actor in self.actors.values():#all actors!
                    actor.update_physics(dt)
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

    def put(self,events):
        for event in events:
            if event.type in self.eventListener:
                for actor in self.eventListener[event.type]:
                    actor.

    def get(self):
        vs=[]
        for actor in self.actors.values():
            v=actor.get_view()
            vs.append(v)
        return vs


class EventTarget:
    def addEvent(type, listner, once_capture_passive):
        1
    def removeEvent():
        1
    def dispatchEvent():
        1
    def eventHandle(event):
        if event.type== 'fullscreenchange':
            1
        if evnet.type=='click':
            1
        if event.type == 'keydown':
            if event.key=='k':
                1

{'k':self.jump}



class Simulator:
    def __init__(self, inputman, world, viewman):
        self.inputman = inputman
        self.world = world
        self.viewman = viewman

        self.time = 0
    def update(self):
        1

    def tick(self):
        dt = timer.get_dt()
        self.time += dt
        #input
        commands = self.inputman.get()
        self.world.put(commands)

        self.world.update(dt)
        
        vs = world.get()
        self.viewman.put(vs)





w=World()
a=Actor()
a.speed=1,0,0
w.add(a)
w.update(0.1)
print(w.get_view())


a = Actor()
print(a)

a = Actor()
a.pos+=2,3,3
a.pos.x+=1
print(a)


a = Actor()
a.speed=1,0,0
a.update(0.1)
a.acc=1,0,-9.8
a.update(0.1)
print(a.acc)
print(a.speed)
print(a.pos)

a=Actor()
a.rotacc=1,2,2
a.rotspeed.x=1
a.update(0.1)
print(a.rotspeed)
print(a.rot)


# a=Actor()
# a.pos=3,2
# a.speed=(0,1)
# a.update(1)
# print(a.pos)

a=Actor()
a.pos=1,1,1
a.rot.z=0.5
print(a.to_matrix())


a=Actor()
a.grav_acc= (0,0,-9.8)
for i in range(10):
    a.update(0.1)
print(a.pos)
print(a.speed)

#print(dir(a))
def main():
    1
if __name__ == '__main__':
    main()