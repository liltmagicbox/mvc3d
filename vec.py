from xyz import XYZ, XYZW



class Vec3(XYZ):
    def __init__(self, x,y,z=0, actor=None,attr=None ):
        #if z==None:#means 2d xy
            #x,y,z = x,0,y
        XYZ.__init__(self,x,y,z,actor,attr)

    # @classmethod
    # def xy(cls,x,y):
    #     """fancy way to xy 2d..(keep z up)"""
    #     return cls(x,0,y)
    #     #cls.__init__(x,0,y)#notthisway
    
    @property
    def xy(self):
        x,y,z = self
        return x,y
    @xy.setter
    def xy(self,value):
        x,y = value
        self.set(x,0,y,True)
    
    #===vec3 method
    def to_euler(self):
        """ front vector >> angluar position """
        #x,y,z = self.x,self.y,self.z
        x,y,z = self
        1
    #===method

class Euler(XYZ):
    def __init__(self, x,y,z=0, actor=None,attr=None ):
        XYZ.__init__(self,x,y,z,actor,attr)        

    def to_front(self):#def front(self):return self.pos.toFront()
        """front is 1,0,0 x=1"""
        x,y,z = self
        front = (1,0,0)
        front = rotate_x(front,x)
        front = rotate_y(front,y)
        front = rotate_z(front,z)
        return front

class Quat(XYZW):
    1




class Actor:
    def __init__(self):
        self._pos = Vec3(0,0,0,self,'pos')#if this Vec3 changes, it reports to self.pos=xxx
        self._rot = Euler(0,0,0,self,'rot')
        self._scale = Vec3(1,1,1,self,'scale')
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





class Vec4(XYZW):
    def __init__(self, x,y,z,w, actor=None,attr=None ):
        XYZW.__init__(self,x,y,z,w, actor,attr)



def _test_vec3():
    v = Vec3(1,2,3)
    print(v)
    #v = Vec3.xy(5,4)
    v = Vec3(5,0,4)
    print(v)

    v = Vec3(1,2,3)
    vv = Vec3(1,2,3,4,5)
    print(vv,'vv')

def main():
    _test_vec3()

if __name__ == '__main__':
    main()