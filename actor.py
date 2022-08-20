from vec import Vec3,Euler

import uuid

class Actor:
    _id = 0
    def __init__(self):
        self.id = self.__class__._id
        self.__class__._id+=1
        self.uuid = str(uuid.uuid4()).replace('-','_')
        self.name = ''
        self.type = self.__class__.__name__
        
        #===
        self._pos = Vec3(0,0,0)
        self._speed = Vec3(0,0,0)
        self._acc = Vec3(0,0,0)
        
        self._rot = Euler(0,0,0)
        self._rotspeed = Euler(0,0,0)
        self._rotacc = Euler(0,0,0)

        self._scale = Vec3(1,1,1)

        #===
        self._simulate_physics = False
        self._gravity = Vec3(0,0,-9.8)
        
        


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
    

    #===internal
    @property
    def gravity(self):
        return self._gravity
    @gravity.setter
    def gravity(self,value):
        x,y,z = value
        self._gravity.set(x,y,z)
    
    @property
    def simulate_physics(self):
        return self._simulate_physics
    @simulate_physics.setter
    def simulate_physics(self,value):
        self._simulate_physics = value
        self.world.set_group_physics(self,value)


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



        



















def main():
    1
if __name__ == '__main__':
    main()