


#we do: simple vector, heiricy,. (ue4 sep.actor data, if needed)
#..what? anyway we use localpos and parent.

class XYZ:
    #print(dir())#['__module__', '__qualname__']
    #print(__module__,__qualname__)#i love py!
    #__copyclass = __qualname__not this..
    def __init__(self,x,y,z, actor=None,attr=None):
        self._x = x
        self._y = y
        self._z = z
        self._actor = actor
        self._attr = attr

        self.isreporter = False
        if actor:
            if attr:
                self.isreporter = True
                self._report = self._real_report
            else:
                raise ValueError('XYZ __init__ requires attr,too!')
    
    #===report system. actor.pos=Vec3(0,0,0,self,'pos') -> actor.pos.x+=1 => actor.pos=(1,0,0)
    def _report(self):
        return
        #print('pass')
    def _real_report(self):
        #self.actor.pos = (self.x,self.y,self.z)
        setattr(self._actor, self._attr, (self._x,self._y,self._z) )    
    def set(self,x,y,z, report=False):
        self._x = x
        self._y = y
        self._z = z
        if report:
            self._report()
    def copy(self):
        return self.__class__(self._x,self._y,self._z)

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x = value
        self._report()
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y = value
        self._report()
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self,value):
        self._z = value
        self._report()

    def __repr__(self):
        repmsg = ''
        if self.isreporter:
            repmsg = f'isReporter'
        return f"{self.__class__.__name__} x:{self._x},y:{self._y},z:{self._z} {repmsg}"
    def __bool__(self):
        return any( (self._x,self._y,self._z) )
    def __iter__(self):
        yield from (self._x,self._y,self._z)
        #for i in [1,2,3]:
        #   yield i
    def __eq__(self,other):
        #x,y,z = self._x,self._y,self._z
        x,y,z = self
        xx,yy,zz = other
        return x==xx and y==yy and z==zz
        #return self._x==other.x and self._y==other.y and self._z==other.z
    def __ne__(self,other):
        x,y,z = self
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

















class XYZW:
    def __init__(self,x,y,z,w, actor=None,attr=None):
        self._x = x
        self._y = y
        self._z = z
        self._w = w
        self._actor = actor
        self._attr = attr

        self.isreporter = False
        if actor:
            if attr:
                self.isreporter = True
                self._report = self._real_report
            else:
                raise ValueError('XYZW __init__ requires attr too!')
    
    #===report system. actor.pos=Vec3(0,0,0,self,'pos') -> actor.pos.x+=1 => actor.pos=(1,0,0)
    def _report(self):
        return
    def _real_report(self):
        setattr(self._actor, self._attr, (self._x,self._y,self._z, self._w) )    
    def set(self,x,y,z,w):
        self._x = x
        self._y = y
        self._z = z
        self._w = w
        self._report()
    def copy(self):
        return self.__class__(self._x,self._y,self._z,self._w)

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x = value
        self._report()
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y = value
        self._report()
    @property
    def z(self):
        return self._z
    @z.setter
    def z(self,value):
        self._z = value
        self._report()
    @property
    def w(self):
        return self._w
    @w.setter
    def w(self,value):
        self._w = value
        self._report()

    def __repr__(self):
        repmsg = ''
        if self.isreporter:
            repmsg = f'isReporter'
        return f"{self.__class__.__name__} x:{self._x},y:{self._y},z:{self._z},w:{self._w} {repmsg}"
    def __bool__(self):
        return any( (self._x,self._y,self._z,self._w) )
    def __iter__(self):
        yield from (self._x,self._y,self._z,self._w)        

    def __eq__(self,other):        
        x,y,z,w = self
        xx,yy,zz,ww = other
        return x==xx and y==yy and z==zz and w==ww
        #return self._x==other.x and self._y==other.y and self._z==other.z
    def __ne__(self,other):
        x,y,z,w = self
        xx,yy,zz,ww = other
        return x!=xx or y!=yy or z!=zz or w!=ww
        #return not self == other
    
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
    vv=XYZ(1,2,3,)
    #v=XYZReport(1,2,3, vv,'vect')
    v=XYZ(1,2,3, vv,'vect')
    v.x=5
    v//=15,2,1
    print(v)
    v.set(3,2,1)
    print(vv.vect)#(3, 2, 1)
    v+=(1,2,3)
    print(v)
    vvv = vv+50
    
    vvv = v+50
    print(vvv)

    vv+=3
    print(vv,'addd')
    vv//=3,2,1
    vv.x=5
    vv.y=5
    vv.z=5

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