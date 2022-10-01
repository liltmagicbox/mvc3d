import math
from pymatvec import mlookat, Vec3, mperspective, mul4x4, mrotmat, mtranslate,mscale


class Actor:
    def __init__(self, id, pos,rot,scale, mesh='default'):
        self.id = id
        self.pos = Vec3(*pos)
        self.rot = Vec3(*rot)
        self.scale = Vec3(*scale)
        self.mesh = mesh
    def get_modelmat(self):
        #https://en.wikipedia.org/wiki/Rotation_matrix
        X,Y,Z = self.rot
        modelmat = mrotmat(X,Y,Z)
        X,Y,Z = self.pos
        #modelmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        mtranslate(modelmat, X,Y,Z)
        X,Y,Z = self.scale
        mscale(modelmat, X,Y,Z)
        return modelmat



def clamp(n, smallest, largest):return max(smallest, min(n, largest))

class Camera:
    def __init__(self, ratio = 1.65):
        self.fov = 50
        self.ratio = ratio
        self.near = 0.1
        self.far = 1000

        self.sensitivity = 1

        self._pos = Vec3(0,0,2)#little back from screen
        self._front = Vec3(0,0,-1)#toward screen
        self._up = Vec3(0,1,0)#usually always up.
        self._yaw = -1.57# means LH, ..fine. zaxis rot.
        self._pitch = 0

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        self._pos.set(*value)

    def get_promat(self):
        #[1,2,3,4,
        promat = mperspective(self.fov, self.ratio, self.near, self.far)
        #promat = [1.22,0,0,0,  0,1.74,0,0,  0,0,-1,-0.61,  0,0,-0.1,0]#fromweb
        return promat
    
    def get_viewmat(self):
        #viewmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,-2,1]#when VP, cam pos shall be z=2 , backstep.
        eye = self._pos
        target = self._pos+self._front
        upV = self._up
        viewmat = mlookat(eye,target,upV)
        return viewmat

    def get_vpmat(self):
        vpmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        promat = self.get_promat()
        viewmat = self.get_viewmat()
        vpmat = mul4x4( viewmat, promat)
        return vpmat

    def set_fov(self,value):
        self.fov = clamp( self.fov+value, 1, 180)

    def rotate_dxdy(self, dx,dy):
        #yaw LH rule, but works as we expect. use front, not yaw directly.
        yaw = self._yaw + dx*self.sensitivity
        pitch = self._pitch + dy*self.sensitivity
        pitch = clamp(pitch,-1.57,1.57)#-89,89

        #----------- fpscam, by yaw & pitch.
        #---note we do not use up-vector. it's just done by yaw,pitch.
        #since in view mat: target = cam.pos+cam.front
        x = math.cos(yaw) * math.cos(pitch)
        y = math.sin(pitch)
        z = math.sin(yaw) * math.cos(pitch)
        self._front = Vec3(x,y,z).normalize()
        self._yaw = yaw
        self._pitch = pitch

    def lookat(self, target):
        """is too hard. we need rotation by vector!"""
        front = (-self.pos + target).normalize()
        self._yaw = math.asin(z)-1.57#math.asin(self._front.z)#z=-1,-90. ->rad.
        self._pitch = math.asin(y)
        # facing = self.target.pos - self.pos
        # d = vdir(front)
        # m = mrotv(front,facing,dt*1)
        # new_front = normalize(d@m)

        #axis,rot = rotv(front,target)
        #self.front = rotv(axis,rot,[1,0,0])        



if __name__ == '__main__':
    Camera()
    #main()