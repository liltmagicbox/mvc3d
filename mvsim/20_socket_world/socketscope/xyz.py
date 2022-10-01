#@staticmethod
def _parse(value):        
    try:
        x,y,z = value
        return x,y,z
    except TypeError:
        return value,value,value
    #they say this is pythonic. do first! catch expected exception!

def main():
    xx = XYZ()
    print(xx[0],xx[-1],xx[-2],xx[-3])
    xx == XYZ()
    for i in xx:
        print(i,'ha')
    xx+=1
    print(xx)
    xx/=2
    print(xx)
    xx/=2
    print(xx)
    try:
        xx==1
    except:
        xx == XYZ(1,0,0)

class XYZ:
    __slots__ = ['x','y','z']
    def __init__(self,x=0.0,y=0.0,z=0.0):
        self.x = x
        self.y = y
        self.z = z    
    def set(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z        
    def copy(self):
        return self.__class__(self.x,self.y,self.z)
    
    def __repr__(self):        
        return f"{self.__class__.__name__} x:{self.x:.4f},y:{self.y:.4f},z:{self.z:.4f}"

    def __getitem__(self, idx):
        if idx==0:
            return self.x
        elif idx==1:
            return self.y
        elif idx==2:
            return self.z
        elif idx==-1:
            return self.z
        elif idx==-2:
            return self.y
        elif idx==-3:
            return self.x
        else:
            raise IndexError
    # def __iter__(self):
    #     X,Y,Z = self
    #     yield from (X,Y,Z)        
    #=================
    def __bool__(self):
        return any( (self.x,self.y,self.z) )

    def __eq__(self,other):
        "not support self==1"
        xx,yy,zz = other
        return self.x==xx and self.y==yy and self.z==zz
        #return self.x==other.x and self.y==other.y and self.z==other.z
    def __ne__(self,other):
        "not support self==1"
        xx,yy,zz = other
        return self.x!=xx or self.y!=yy or self.z!=zz
        #return not self == other    
    
    def __neg__(self):#unary
        return self.__class__(-self.x,-self.y,-self.z)
    #below not occur iteration, maybe faster. not x,y,z = self
    #=== newxyz = xyz+value
    def __add__(self, value):
        #x,y,z = value
        x,y,z = _parse(value)
        return self.__class__(self.x+x,self.y+y,self.z+z)#shouldn't return Report class..        
    def __sub__(self, value):
        x,y,z = _parse(value)
        return self.__class__(self.x-x,self.y-y,self.z-z) 
        #return self + (-x,-y,-z)#this is basic.don't do too much..
    def __mul__(self, value):
        x,y,z = _parse(value)
        return self.__class__(self.x*x, self.y*y, self.z*z)
    def __truediv__(self, value):
        x,y,z = _parse(value)
        return self.__class__(self.x/x, self.y/y, self.z/z)
    def __floordiv__(self, value):
        x,y,z = _parse(value)
        return self.__class__(self.x//x, self.y//y, self.z//z)     
    
    #===self-effective. all uses self.set
    def __iadd__(self, value):
        xx,yy,zz = _parse(value)
        self.set(self.x+xx,self.y+yy,self.z+zz)
        return self
    def __isub__(self, value):
        xx,yy,zz = _parse(value)
        self.set(self.x-xx,self.y-yy,self.z-zz)
        return self
    def __imul__(self, value):
        xx,yy,zz = _parse(value)
        self.set(self.x*xx,self.y*yy,self.z*zz)
        return self
    def __itruediv__(self, value):
        xx,yy,zz = _parse(value)
        self.set(self.x/xx,self.y/yy,self.z/zz)
        return self
    def __ifloordiv__(self, value):
        xx,yy,zz = _parse(value)
        self.set(self.x//xx,self.y//yy,self.z//zz)
        return self
    #=================

if __name__ == '__main__':
    main()