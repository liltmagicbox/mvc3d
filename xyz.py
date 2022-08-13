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
        self.set(xx,yy,zz)
        return self
    def __isub__(self, value):
        #x,y,z = value
        x,y,z = self._parse(value)
        xx = self._x-x
        yy = self._y-y
        zz = self._z-z
        self.set(xx,yy,zz)
        return self
    def __imul__(self, value):
        x,y,z = self._parse(value)
        xx = self._x*x
        yy = self._y*y
        zz = self._z*z
        self.set(xx,yy,zz)
        return self
    def __itruediv__(self, value):
        x,y,z = self._parse(value)
        xx = self._x/x
        yy = self._y/y
        zz = self._z/z
        self.set(xx,yy,zz)
        return self
    def __ifloordiv__(self, value):
        x,y,z = self._parse(value)
        xx = self._x//x
        yy = self._y//y
        zz = self._z//z
        self.set(xx,yy,zz)
        return self
    #=================