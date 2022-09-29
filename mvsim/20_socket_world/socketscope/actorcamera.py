import math
from pymatvec import mlookat, Vec3, mperspective, mul4x4,  translate,scale,rotate


class Actor:
    def __init__(self, id, pos,rot,scale, mesh='default'):
        self.id = id
        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.mesh = mesh
    def get_modelmat(self):
        #https://en.wikipedia.org/wiki/Rotation_matrix

        X,Y,Z = self.pos
        modelmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        translate(modelmat, X,Y,Z)
        return modelmat



def clamp(n, smallest, largest):return max(smallest, min(n, largest))

class Camera:
    def __init__(self, ratio = 1.65):
        self.fov = 50
        self.ratio = ratio
        self.near = 0.1
        self.far = 1000

        self.sensitivity = 1

        self.pos = Vec3(0,0,2)#little back from screen
        self.front = Vec3(0,0,-1)#toward screen
        self.up = Vec3(0,1,0)#usually always up.
        #self.front = Vec3(0,0,-1)
        #self.yaw = -90# means LH, ..fine.
        self.yaw = math.degrees(math.asin(self.front.z))
        self.pitch = 0

    def get_promat(self):
        #[1,2,3,4,
        promat = mperspective(self.fov, self.ratio, self.near, self.far)
        #promat = [1.22,0,0,0,  0,1.74,0,0,  0,0,-1,-0.61,  0,0,-0.1,0]#fromweb
        return promat
    
    def get_viewmat(self):
        #viewmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,-2,1]#when VP, cam pos shall be z=2 , backstep.
        eye = self.pos
        target = self.pos+self.front
        upV = self.up
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
        self.yaw += dx*self.sensitivity*100
        self.pitch += dy*self.sensitivity*100
        self.pitch = clamp(self.pitch,-89,89)

        pitch = self.pitch
        yaw = self.yaw
        #----------- fpscam, by yaw & pitch.
        #---note we do not use up-vector. it's just done by yaw,pitch.
        #since in view mat: target = cam.pos+cam.front
        x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        y = math.sin(math.radians(pitch))
        z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)) 
        self.front = Vec3(x,y,z).normalize()
        #ssems normalized but do again.. ...sin-cos never over 1.0.?
if __name__ == '__main__':
    Camera()
    #main()