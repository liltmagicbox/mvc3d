from vec import Vec3,Euler


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
    
    def add(self, child):
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






class EventDispatcher:#it not requires init, nor forces having listners..
    #https://github.com/mrdoob/three.js/blob/dev/src/core/EventDispatcher.js
    #def __init__(self):
    #    self.listeners = {}
    def addEventListener(self, key, listener):
        ldict = getattr(self, 'listeners', {})
        if not key in ldict:
            ldict[key] = []
        ldict[key].append(listener)   
        
        self.listeners = ldict

e = EventDispatcher()
e.addEventListener('nub', 'hom')

print(e.listeners)




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

class Actor:
    def __init__(self):
        self._pos = Vec3(0,0,0, self,'pos')#if this Vec3 changes, it reports to self.pos=xxx
        self._rot = Euler(0,0,0, self,'rot')
        self._scale = Vec3(1,1,1 ,self,'scale')
    
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
        '''can pos=3,2'''
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

_test_xy()