


#we do: simple vector, heiricy,. (ue4 sep.actor data, if needed)
#..what? anyway we use localpos and parent.

class XYZ:
    __slots__ = ['_x','_y','_z']
    def __init__(self,x,y,z):
        self._x = x
        self._y = y
        self._z = z    
    def set(self,x,y,z):
        self._x = x
        self._y = y
        self._z = z        
    def copy(self):
        return self.__class__(self._x,self._y,self._z)
    
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x = value
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y = value
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self,value):
        self._z = value

    def __repr__(self):        
        return f"{self.__class__.__name__} x:{self._x},y:{self._y},z:{self._z}"
    #=================
    def __bool__(self):
        return any( (self._x,self._y,self._z) )
    def __iter__(self):
        yield from (self._x,self._y,self._z)        
    def __eq__(self,other):
        #x,y,z = self
        x,y,z = self._x,self._y,self._z
        xx,yy,zz = other
        return x==xx and y==yy and z==zz
        #return self._x==other.x and self._y==other.y and self._z==other.z
    def __ne__(self,other):
        x,y,z = self._x,self._y,self._z
        xx,yy,zz = other
        return x!=xx or y!=yy or z!=zz
        #return not self == other
    
    @staticmethod
    def _parse(value):        
        try:
            x,y,z = value
            return x,y,z
        except TypeError:
            return value,value,value
        #they say this is pythonic. do first! catch expected exception!
    #=== newxyz = xyz+value
    def __add__(self, value):
        #x,y,z = value
        x,y,z = self._parse(value)
        return self.__class__(self._x+x,self._y+y,self._z+z)#shouldn't return Report class..        
    def __sub__(self, value):
        x,y,z = self._parse(value)
        return self.__class__(self._x-x,self._y-y,self._z-z) 
        #return self + (-x,-y,-z)#this is basic.don't do too much..
    def __mul__(self, value):
        x,y,z = self._parse(value)
        return self.__class__(self._x*x, self._y*y, self._z*z)
    def __truediv__(self, value):
        x,y,z = self._parse(value)
        return self.__class__(self._x/x, self._y/y, self._z/z)
    def __floordiv__(self, value):
        x,y,z = self._parse(value)
        return self.__class__(self._x//x, self._y//y, self._z//z)     
    
    #===self-effective. all uses self.set
    def __iadd__(self, value):
        #x,y,z = value
        #self._x+=x
        #self._y+=y
        #self._z+=z
        x,y,z = self._parse(value)
        xx = self._x+x
        yy = self._y+y
        zz = self._z+z
        self.set(xx,yy,zz,True)
        return self
    def __isub__(self, value):
        #x,y,z = value
        x,y,z = self._parse(value)
        xx = self._x-x
        yy = self._y-y
        zz = self._z-z
        self.set(xx,yy,zz,True)
        return self
    def __imul__(self, value):
        x,y,z = self._parse(value)
        xx = self._x*x
        yy = self._y*y
        zz = self._z*z
        self.set(xx,yy,zz,True)
        return self
    def __itruediv__(self, value):
        x,y,z = self._parse(value)
        xx = self._x/x
        yy = self._y/y
        zz = self._z/z
        self.set(xx,yy,zz,True)
        return self
    def __ifloordiv__(self, value):
        x,y,z = self._parse(value)
        xx = self._x//x
        yy = self._y//y
        zz = self._z//z
        self.set(xx,yy,zz,True)
        return self
    #=================










def test_ifvsfunc():
    #test 10M , self._report() is faster than if self._actor: self._report()
    #3.7699246406555176
    #3.9296185970306396
    class XYZ:
        __slots__ = ['_x','_y','_z','_actor','_attr']
        def __init__(self,x,y,z, actor=None,attr=None):
            self._x = x
            self._y = y
            self._z = z
            self._actor = actor
            self._attr = attr
        def _report(self):
            if self._actor:
                setattr(self._actor, self._attr, (self._x,self._y,self._z) )
        @property
        def x(self):
            return self._x
        @x.setter
        def x(self,value):
            self._x = value
            self._report()

    import time
    t = time.time()
    print(time.time()-t)

    class Actor:
        def __init__(self):
            self.pos = 0
   
    vv=Actor()
    a = XYZ(1,2,3,vv,'pos')
    
    t = time.time()
    for i in range(1000_0000):
        a.x+=0.2
    print(time.time()-t)


    class XYZ:
        __slots__ = ['_x','_y','_z','_actor','_attr']
        def __init__(self,x,y,z, actor=None,attr=None):
            self._x = x
            self._y = y
            self._z = z
            self._actor = actor
            self._attr = attr
        def _report(self):
            setattr(self._actor, self._attr, (self._x,self._y,self._z) )
        @property
        def x(self):
            return self._x
        @x.setter
        def x(self,value):
            self._x = value
            if self._actor:
                self._report()

    vv=Actor()
    a = XYZ(1,2,3,vv,'pos')
    t = time.time()
    for i in range(1000_0000):
        a.x+=0.2
    print(time.time()-t)





def test_x():
    #30% slower!
    #result: 1.func() is high cost, 600ms/10M, 6ms/100k. while if requires 150ms/10M. 15ms/1M. 1.5ms/100k
    2.2450010776519775
    1.6914513111114502
    1.54 #without if. not that difference!
    import time
    t = time.time()
    print(time.time()-t)


    class XYZ:
        __slots__ = ['_x','_y','_z','_actor','_attr']
        def __init__(self,x,y,z, actor=None,attr=None):
            self._x = x
            self._y = y
            self._z = z
            self._actor = actor
            self._attr = attr
        def _report(self):
            if self._actor:
                setattr(self._actor, self._attr, (self._x,self._y,self._z) )
        @property
        def x(self):
            return self._x
        @x.setter
        def x(self,value):
            self._x = value
            self._report()

    class Actor:
        def __init__(self):
            self.pos = 0
   

    t = time.time()

    a = XYZ(1,2,3)
    for i in range(1000_0000):
        a.x+=.2
    
    print(time.time()-t)


    class XYZ:
        __slots__ = ['_x','_y','_z','_actor','_attr']
        def __init__(self,x,y,z, actor=None,attr=None):
            self._x = x
            self._y = y
            self._z = z
            self._actor = actor
            self._attr = attr
        def _report(self):
            setattr(self._actor, self._attr, (self._x,self._y,self._z) )
        @property
        def x(self):
            return self._x
        @x.setter
        def x(self,value):
            self._x = value
            if self._actor:
                self._report()

    t = time.time()
    
    a = XYZ(1,2,3)
    for i in range(1000_0000):
        a.x+=.2
    
    print(time.time()-t)
    









class XYZW:
    __slots__ = ['_x','_y','_z','_w']
    def __init__(self,x,y,z,w):
        self._x = x
        self._y = y
        self._z = z
        self._w = w
    
    #===report system. actor.pos=Vec3(0,0,0,self,'pos') -> actor.pos.x+=1 => actor.pos=(1,0,0)
    def _report(self):
        1#setattr(self._actor, self._attr, (self._x,self._y,self._z, self._w) )
        #if self._actor:
    def set(self,x,y,z,w, report=False):
        self._x = x
        self._y = y
        self._z = z
        self._w = w
        if report and self._reporter:
            self._report()
    def copy(self):
        return self.__class__(self._x,self._y,self._z,self._w)

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x = value
        if self._reporter:
            self._report()
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y = value
        if self._reporter:
            self._report()
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self,value):
        self._z = value
        if self._reporter:
            self._report()
    @property
    def w(self):
        return self._w
    @w.setter
    def w(self,value):
        self._w = value
        if self._reporter:
            self._report()

    def __repr__(self):
        repmsg = ''
        if self.isreporter:
            repmsg = f'Reporting'
        return f"{self.__class__.__name__} x:{self._x},y:{self._y},z:{self._z},w:{self._w} {repmsg}"
    def __bool__(self):
        return any( (self._x,self._y,self._z,self._w) )
    def __iter__(self):
        yield from (self._x,self._y,self._z,self._w)        

    def __eq__(self,other):        
        x,y,z,w = self
        xx,yy,zz,ww = other
        return x==xx and y==yy and z==zz and w==ww
    def __ne__(self,other):
        x,y,z,w = self
        xx,yy,zz,ww = other
        return x!=xx or y!=yy or z!=zz or w!=ww
    
    @staticmethod
    def _parse(value):        
        try:
            x,y,z,w = value
            return x,y,z,w
        except TypeError:
            return value,value,value,value        
    #=== newxyz = xyz+value
    def __add__(self, value):        
        x,y,z,w = self._parse(value)
        return self.__class__(self._x+x,self._y+y,self._z+z, self._w+w)#shouldn't return Report class..        
    def __sub__(self, value):
        x,y,z,w = self._parse(value)
        return self.__class__(self._x-x,self._y-y,self._z-z, self._w-w) 
        #return self + (-x,-y,-z)#this is basic.don't do too much..
    def __mul__(self, value):
        x,y,z,w = self._parse(value)
        return self.__class__(self._x*x, self._y*y, self._z*z, self._w*w)
    def __truediv__(self, value):
        x,y,z,w = self._parse(value)
        return self.__class__(self._x/x, self._y/y, self._z/z, self._w/w)
    def __floordiv__(self, value):
        x,y,z,w = self._parse(value)
        return self.__class__(self._x//x, self._y//y, self._z//z, self._w//w)     
    
    #===self-effective. all uses self.set
    def __iadd__(self, value):
        x,y,z,w = self._parse(value)
        xx = self._x+x
        yy = self._y+y
        zz = self._z+z
        ww = self._w+w
        self.set(xx,yy,zz,ww,True)
        return self
    def __isub__(self, value):
        x,y,z,w = self._parse(value)
        xx = self._x-x
        yy = self._y-y
        zz = self._z-z
        ww = self._w-w
        self.set(xx,yy,zz,ww,True)
        return self
    def __imul__(self, value):
        x,y,z,w = self._parse(value)
        xx = self._x*x
        yy = self._y*y
        zz = self._z*z
        ww = self._w*w
        self.set(xx,yy,zz,ww,True)
        return self
    def __itruediv__(self, value):
        x,y,z,w = self._parse(value)
        xx = self._x/x
        yy = self._y/y
        zz = self._z/z
        ww = self._w/w
        self.set(xx,yy,zz,ww,True)
        return self
    def __ifloordiv__(self, value):
        x,y,z,w = self._parse(value)
        xx = self._x//x
        yy = self._y//y
        zz = self._z//z
        ww = self._w//w
        self.set(xx,yy,zz,ww,True)
        return self




















#==================================
def _test_xyz():
    print('=======\n\n')
    x = XYZ(1,2,3)
    print(x)
    x+=3
    x*=3
    new = x//3
    new = x//(3,2,1)
    print(new,'newnn')
    print(x)
    x.x//=3
    x.y//=3
    x.z//=3
    print(x,'td')

    print()
    #print(len(x),'length')#if euler.. it's for vector only.


    x*=(1,2,3)
    print(x)
    print('/////')
    exit()

    x/=10,1,10
    print(x)
    #actor.pos+=(1,2,3)
    #actor.pos*=3

def _test_xyzw():
    w = XYZW(1,2,3,4)
    w+=5
    print(w)
    w/=5
    print(w)
    w*=5
    print(w)
    w//=5
    print(w)
    
    w.x+=5
    print(w)
    w.w/=50
    w*=1,1,1,50
    print(w)




def _test_report():
    class Actor:
        def __init__(self):
            self.pos = 0
    vv=Actor()

    #v=XYZReport(1,2,3, vv,'vect')
    v=XYZ(1,2,3, vv,'pos')
    v.x=5
    v//=15,2,1
    print(v,'v is')

    v.set(3,2,1,True)
    print(vv.pos,'vv pos')#(3, 2, 1)
    v+=(1,2,3)
    print(v)
    
    vvv = v+50
    print(vvv)

    v//=3,2,1
    v.x=5
    v.y=5
    v.z=5

    try:
        no=XYZ(1,2,3,4)
        print(no,'no')
    except:
        print('xyz init fail with 1,2,3,4')

def main():
    _test_report()

if __name__ == '__main__':
    main()







history='''

class __XYZReport(XYZ):#was consumed XYZ, finally. since self.__class__ error.. newvector = actor.pos+3-> not Vec3.
    def __init__(self,x,y,z, actor,attr):    
        XYZ.__init__(self,x,y,z)
        self._actor = actor
        self._attr = attr

    #===report system. actor.pos=Vec3(0,0,0,self,'pos') -> actor.pos.x+=1 => actor.pos=(1,0,0)
    def _report(self):
        #self.actor.pos = (self.x,self.y,self.z)
        setattr(self._actor, self._attr, (self._x,self._y,self._z) )
    def set(self, x,y,z):
        self._x,self._y,self._z = x,y,z
        self._report()

    #===>self._report()
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x = value
        if self._actor:
            self._report()
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y = value
        if self._actor:
            self._report()
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self,value):
        self._z = value
        if self._actor:
            self._report()

    def __repr__(self):
        return f"XYZReport x:{self._x},y:{self._y},z:{self._z}"
'''