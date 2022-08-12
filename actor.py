from vec import Vec3,Euler

import uuid

_ActorId = 0


class Actor:
    def __init__(self):
        self._pos = Vec3(0,0,0)
        self._rot = Euler(0,0,0)
        self._scale = Vec3(1,1,1)
        #self.isActor = True
        
        self.id = _ActorId
        _ActorId+=1
        self.uuid = uuid.uuid4()

        self.name = ''
        self.type = 'Actor'

    def __repr__(self):
        return f"{self._pos}"

    @staticmethod
    def _parse(value):
        x,y,*z = value
        #print(bool(z),'boo',z)#True boo [0]
        if z:
            value = x,y,z[0]
        else:
            value = x,0,y
        return value    
    
    #===pos rot scale
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        '''can pos=(3,2)'''
        x,y,z = self._parse(value)
        #self._pos = x,y,z
        self._pos.set(x,y,z)
    
    @property
    def rot(self):
        return self._rot
    @rot.setter
    def rot(self,value):
        x,y,z = self._parse(value)
        self._rot.set(x,y,z)

    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self,value):
        x,y,z = self._parse(value)
        self._scale.set(x,y,z)

    #===game vector kinds
    @property
    def front(self):
        return self._pos.toFront()
