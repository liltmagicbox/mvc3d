from vec import Vec3,Euler

import uuid
_ActorId = 0


def _test_meshinherit():
    #https://stackoverflow.com/questions/9575409/calling-parent-class-init-with-multiple-inheritance-whats-the-right-way
    class Actor:
        def __init__(self, pos=(0,0,0) , **kwargs):
            #super().__init__(**kwargs)
            self.pos = pos

    class MeshActor(Actor):
        def __init__(self, mesh=None, **kwargs):
            super().__init__(**kwargs)
            self.mesh = mesh

    a = Actor()
    print(a.pos)

    a = MeshActor(pos= [3,5,6] ,mesh=3)
    a = MeshActor(mesh=3)
    print(a.pos)
    print(a.mesh)

# a = Actor(pos=(5,0,0))
# b = Actor( parent=a)
# a.add(b)
# a.children.append(b)#extend.. -hope we not use propery to children..

#https://github.com/mrdoob/three.js/blob/dev/src/core/EventDispatcher.js
#https://github.com/mrdoob/three.js/blob/dev/src/core/Object3D.js
#https://github.com/mrdoob/three.js/blob/dev/src/objects/Mesh.js

_addedEvent = {'type':'added'}
_removedEvent = {'type':'removed'}#see how clever.!

#https://github.com/stemkoski/three.py/blob/master/three.py/core/Object3D.py

class Hierarchy:
    """all from Threejs, but not returns self, nor add([]).
    using set, fast add-remove.
    """
    def __init__(self, parent=None, **kwargs):
        self._parent = parent
        self._children = set()        

    @property
    def children(self):
        return self._children
    @children.setter
    def children(self, value):
        if isinstance(value, Hierarchy):#do we need it?
            self.add(value)

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, value):
        if isinstance(value, Hierarchy):#do we need it?
            value.add(self)
        #self._parent = value
    
    def add(self, child):#attach world pos. not add(keep=True,) if command..
        """not [child,] but child"""
        if self==child:#wow..
            'one cannot add itself!'
            return

        if isinstance(child, Hierarchy):
            if child.parent:
                #child.parent.remove(child)
                child.removeFromParent()#technically it's more OOP like..?
            
            child.parent = self
            self.children.add(child)#set.add!
            child.dispatchEvent( _addedEvent )

        else:
            'Hierarchy!'

    def remove(self, child):
        """using set(), fast remove"""
        child.parent = None
        self.children.remove(child)
        child.dispatchEvent( _removedEvent )
    def removeFromParent(self):
        parent = self.parent
        if parent:
            parent.remove(self)
    def clear(self):
        for child in self.children:
            child.removeFromParent()#has only one parent!
            #child.parent=None
            #you can use remove here, not[],, fast set().remove!
        #self.children = set()

    #===get kinds.
    #https://github.com/mrdoob/three.js/blob/dev/src/core/Object3D.js
    # def getObjectById(self,id):
    #     return self.getObjectByProperty('id',id)
    # def getObjectByName(self,name):
    #     return self.getObjectByProperty('name',name)
    # def getObjectByProperty(self, name,value):
    #     if getattr(self,name)==value:
    #         return self
    #     for child in self.children:
    #         obj = child.getObjectByProperty(name,value)
    #         if obj:
    #             return obj
    
    #less method rule..
    def getBy(self, name,value):
        if getattr(self,name)==value:
            return self
        for child in self.children:
            obj = child.getBy(name,value)
            if obj:
                return obj
    #===traverse
    # def traverse(self,callback, visible=False):
    #     if visible:
    #         if not self.visible:
    #             return
    def traverse(self,callback):
        callback(self)
        children = self.children
        for child in children:
            child.traverse(callback)


class Layers:
    def __init__(self):
        1

class Visual:
    def __init__(self):
        self.layers = Layers()
        self.visible = True
        
        self.castShadow = False
        self.receiveShadow = False

        self.frustumCulled = True
        self.renderOrder = 0

        self.animations = []
        self.userData = {}




history='''
ACtor
def __init__(self, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1), **kwargs):
        self._pos = Vec3(*pos,self,'pos')#if this Vec3 changes, it reports to self.pos=xxx
-> three.js style , no pos.. kinds.
if using for, thats fine
less method, narrow interface better.
for 'At a glance'
'''



#pos is parentpos+=
#rot is rot*rot
#scale is scale&scale


#a = Actor()
# a.pos = (1,0,0)
# a.speed = (0,1,0)
# a.acc = (0,0,-9.8)
# a.rpos
# a.rspeed
# a.racc

#a.pos.acc = (1,0,0)
#a.rot.speed = (1,0,0)

#a.scale.speed = (0,0,1)

#too bad range
# if a.scale.z>10:
#     a.scale.speed = (0,0,-1)
# else a.scale<0:
#     a.scale.speed = (0,0,1)

#a.scale.ociliate(0,10,1)
#a.scale.range(0,10,1)#start,end,step(speed),step(acc),curve?? we can't just acc..

#new way:

#self._pos = Vec3(0,0,0,axis)
#self._pos = Vec3AXIS(0,0,0)

#ID POS SPD ACC  RPOS RSPD RACC


class Actor:
    def __init__(self):
        self._pos = Vec3(0,0,0, self,'pos')#if this Vec3 changes, it reports to self.pos=xxx
        self._rot = Euler(0,0,0, self,'rot')
        self._scale = Vec3(1,1,1 ,self,'scale')
        #self._quat = Quat()
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

    #better rot has internal quat features..? and dynamically get quat..
    #rot.toQuat()..

    #===game vector kinds
    @property
    def front(self):
        return self._pos.toFront()




def _test_xy():
    #Vec3(5,4)# it says 3, so let this not happened..
    #v = Vec3.xy(5,4)#not do this.

    v = Vec3(5,0,4)
    v.set(3,2,1)
    print(v,'321')

    v.xy=(6,5)
    print(v)
    print(v.xy,'605')

    #v.setxy(3,2)
    #Vec3.xy=(3,2)
    #actor.pos.xy=(3,2)

    #actor.pos = Vec3.xy(3,2) #we not do this!
    actor = Actor()
    actor.pos=3,2,1
    print(actor)
    actor.pos=3,2#shall be placed in actor. not vector.fine.

    print(actor)
    print('aaa')


class Group(Actor):
    def __init__(self):
        super().__init__()
        self.isGroup=True#is for rendering..WEBGL.Renderer
        self.type = 'Group'

class MeshActor(Actor):
    1

class Matrix4:
    1

class Matrixer:
    def __init__(self):
        self.matrix = Matrix4()
        self.matrixWorld = Matrix4()

        #self.matrixAutoUpdate = False needit?
        self.matrixWorldNeedsUpdate = False



class Event:
    def __init__(self, type, target=None):
        self.type = type
        self.target = target

class MouseEvent(Event):
    #https://www.w3.org/TR/uievents/#mouseevent
    def __init__(self, type,clientX,clientY,target=None):
        super().__init__(type,target)
        self.cilentX = clientX
        self.cilentY = clientY


class EventDispatcher:
    #https://ko.javascript.info/dispatch-events
    def addEventL(self, type):
        print(type)
    def removeEventL(self):
        1
    def dispatchEvent(self, event):
        1

def ma(event):
    print(event.target.id)

# button.addEventL('click',ma)
# document.addEventL('click',ma)
# window.addEventL('click',ma)
# world.addEventL('click',ma)

class World(EventDispatcher):
    def __init__(self):
        self.listeners = {}

a = Actor()
#a.addEventL('keydown',a.jump)


a.keymap = {'j',a.jump}
a.keymap = {'j','jump'}
a.keymap = {'s','jump*-0.1'}
a.keymap = {'J_down','jump*-0.1'}

#AxisInput()

#EventJump
def Jump(self):
    1
a.Jump= Jump

class FPSController:
    def __init__(self):
        self.keymap = {
        'w':'move*1',
        's':'move*-1.0',
        'a':'turn*-1',
        'd':'turn*1',
        
        'M_X':'look*1',
        "M_Y":'look*1',
        
        'J_LX':'move*1',
        'J_L1':'jump',
        }
        #'L1 L2 L3 DPAD(UP DOWN LEFT RIGHT) LX RY ABXY'#LSTICK TOO LONG
        #esc ctrl pagedown pageup insert delete home up down left right f11 space tap lshift rshift * - =
        #num1 num0 num. num+ num/
        #M_XY??? M_DX M_DXDY???

keymap = {
        'W': 'move_forward(0.2)',
        'S': 'move_forward(-0.2)',
        #'S': 'move_forward-1',
        'D': 'move_right(0.2)',
        'A': 'move_right(-0.2)',
        'F': 'fire',
        'M_DXDY': 'mouse_move',

        'M_SCROLL_UP': 'set_fov(-5)',
        'M_SCROLL_DOWN': 'set_fov(5)',

        'J_LSTICK_Y': 'move_forward(0.1)',
        'J_LSTICK_X': 'move_right(-0.1)',
         }

class FPSControlled:
    def move():1
    def turn():1
    def look():1

class Gunman:
    def move(self, value):
        1
    def turn(self):
        1
    def look(self,x,y):
        1

controller = FPSController()
gunman = Gunman()
controller.target = gunman
        






class EventDispatcher:#it not requires init, nor forces having listners..
    #https://github.com/mrdoob/three.js/blob/dev/src/core/EventDispatcher.js
    #def __init__(self):
    #    self.listeners = {}
    #since this way, we not add attr {}, if not added
    def addEventListener(self, key, listener):
        ldict = getattr(self, 'listeners', {})
        if not key in ldict:
            ldict[key] = []
        ldict[key].append(listener)   
        
        self.listeners = ldict

e = EventDispatcher()
e.addEventListener('nub', 'hom')

print(e.listeners)



def main():
    _test_xy()


class Mesh(Actor):
    def __init__(self, geo=None,mat=None):
        super().__init__()
        
        if geo==None:
            geo = Geometry.default()
            geo = Geo.default()
            #geo = MeshGeometry.default()
            #geo = MeshGeometry.default()
            #PointNormalMaterial
            #MeshNormalMaterial

        self.geo = geo
        self.mat = mat