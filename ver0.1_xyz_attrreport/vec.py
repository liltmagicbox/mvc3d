from xyz import XYZ, XYZW



class Vec3(XYZ):
    def __init__(self, x,y,z=0):
        #if z==None:#means 2d xy
            #x,y,z = x,0,y
        #XYZ.__init__(self,x,y,z,actor,attr)
        super().__init__(x,y,z)

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
    def __init__(self, x,y,z):
        #XYZ.__init__(self,x,y,z,actor,attr)
        super().__init__(x,y,z)        

    def to_front(self):#def front(self):return self.pos.toFront()
        """front is 1,0,0 x=1"""
        x,y,z = self
        front = (1,0,0)
        front = rotate_x(front,x)
        front = rotate_y(front,y)
        front = rotate_z(front,z)
        return front
    def to_quat(self):
        """hope not that used again.."""
        return 1,1,1,1

class Quat(XYZW):
    1




class Vec4(XYZW):
    def __init__(self, x,y,z,w):
        #XYZW.__init__(self,x,y,z,w, actor,attr)
        super().__init__(x,y,z,w)



def main():
    1#_test_vec3()

if __name__ == '__main__':
    main()