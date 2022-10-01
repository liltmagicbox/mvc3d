from math import radians, tan, sqrt
from math import cos,sin

def eye4():
    mat = [0.0]*16
    mat[0]=1.0 #00
    mat[5]=1.0 #11
    mat[10]=1.0 #22
    mat[15]=1.0 #33
    return mat



def rotate_x(mat,th):
    th = radians(th)
    C = cos(th)
    S = sin(th)
    mat[5] = C
    mat[6] = -S
    mat[9] = S
    mat[10] = C
    return mat

def xxx_rotate_x(x,y,z,rad):
    mat = [1,0,0,0,1,0,0,0,1]
    C = cos(rad)
    S = sin(rad)
    mat[4] = C
    mat[5] = -S
    mat[7] = S
    mat[8] = C
    X = mat[0]*x+mat[1]*y+mat[2]*z
    Y = mat[3]*x+mat[4]*y+mat[5]*z
    Z = mat[6]*x+mat[7]*y+mat[8]*z
    return X,Y,Z

def rotate_x(x,y,z,rad):
    C = cos(rad)
    S = sin(rad)
    X = x
    Y = C*y -S*z
    Z = S*y +C*z
    return X,Y,Z
def rotate_y(x,y,z,rad):
    C = cos(rad)
    S = sin(rad)
    X = C*x + S*z
    Y = y
    Z = -S*x + C*z
    return X,Y,Z
def rotate_z(x,y,z,rad):
    C = cos(rad)
    S = sin(rad)
    X = C*x -S*y
    Y = S*x +C*y
    Z = z
    return X,Y,Z


def mrotmat(x,y,z):
    """rotate by gloval axis. yup.
    yaw(z) pitch(y) roll(x) 1,2,3,4->"""
    Ca = cos(x)
    Sa = sin(x)
    Cb = cos(y)
    Sb = sin(y)
    Cr = cos(z)
    Sr = sin(z)
    rotmat = [Cb*Cr, Sa*Sb*Cr-Ca*Sr, Ca*Sb*Cr+Sa*Sr, 0.0,
    Cb*Sr, Sa*Sb*Sr+Ca*Cr, Ca*Sb*Sr-Sa*Cr, 0.0,
    -Sb, Sa*Cb, Ca*Cb, 0.0,
    0.0,0.0,0.0,1.0]
    return rotmat

def mtranslate(mat,x,y,z):
    mat[12] += x
    mat[13] += y
    mat[14] += z
def mscale(mat,x,y,z):
    mat[0] *= x
    mat[5] *= y
    mat[10] *= z

#seems it WAS colmajor.
def mortho(left, right, bottom, top, near, far):
    #note: if you use fov,ratio, we need change some,,
    #by cam.pos.. not. use area kinds. attr for ortho.
    mat = [0.0]*16

    a = right - left
    b = top - bottom
    c = far - near
    mat[0] = 2 / a #00
    mat[5] = 2 / b #11
    mat[10] = -2 / c #22
    
    mat[3] = -(right + left) / a #03
    mat[7] = -(top + bottom) / b #13
    mat[11] = -(far + near) / c #23
    mat[15] = 1.0
    return mat




def mperspective(fov, ratio, near, far):
    fov = radians(fov)    
    f= 1/ tan(fov/2)

    mat0 = f/ratio
    mat5 = f #11 4*1+1 = 5
    mat10 = (far+near)/(near-far) #22 4*2+2=10
    
    mat11 = -1 #23, COL MAJOR.
    mat14 = (2*far*near)/(near-far) #32
    mat15 = 0 #33 4*3+3= 15
    mat = [mat0,0.0,0.0,0.0, 0.0,mat5,0.0,0.0, 0.0,0.0,mat10,mat11, 0.0,0.0,mat14,mat15]
    return mat



#see old pymatrix, it subclasses List! hahaha! even not ----List.
# (List):->: str->repr get/setattr ->'', ''->slots
from xyz import XYZ
class Vec3(XYZ):
    def __init__(self,x=0.0,y=0.0,z=0.0):
        super().__init__(x,y,z)

    def dot(self, other):
        x,y,z = self
        xx,yy,zz = other
        return x*xx+y*yy+z*zz
    def cross(self, other):
        d,e,f = self
        g,h,i = other
        x= (e*i-f*h)
        y=-(d*i-f*g)
        z= (d*h-e*g)
        return Vec3(x,y,z)
    def normalize(self):
        x,y,z = self
        if not x==y==z==0:
            dem = sqrt( x**2+y**2+z**2 )
            return Vec3( x/dem, y/dem, z/dem )
        return Vec3(0,0,0)#failsafe?



def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]


def cross(v1,v2):
    d,e,f = v1
    g,h,i = v2
    x= (e*i-f*h)
    y=-(d*i-f*g)
    z= (d*h-e*g)
    return Vec3(x,y,z)

def normalize(v):
    x,y,z = v
    if not x==y==z==0:
        dem = sqrt( x**2+y**2+z**2 )
        return Vec3( x/dem, y/dem, z/dem )    
    return Vec3(0,0,0)

def mlookat(eye,target,upV):
    front = eye-target#donno why but this way.fine. we have lot to do.
    #front = front/norm(front) #orrurs div/0
    front = normalize(front)

    right = cross(upV, front)
    right = normalize(right)

    up = cross(front, right)#donno why 2.
    up = normalize(up)

    right0,right1,right2, = right
    up0,up1,up2 = up
    front0,front1,front2 = front
    
    minus_eye = eye*-1
    v1 = [
    right0,up0,front0,0,
    right1,up1,front1,0,
    right2,up2,front2,0,
    dot(right , minus_eye),dot(up , minus_eye),dot(front , minus_eye),1]
    return v1




def dot4(A,B):
    A0,A1,A2,A3 = A
    B0,B1,B2,B3 = B
    return A0*B0 + A1*B1 + A2*B2 + A3*B3

def mul4x4(A,B):
    row0 = A[0:4]
    row1 = A[4:8]
    row2 = A[8:12]
    row3 = A[12:16]
    
    B0,B1,B2,B3, B4,B5,B6,B7, B8,B9,B10,B11, B12,B13,B14,B15 = B
    col0 = B0,B4,B8,B12
    col1 = B1,B5,B9,B13
    col2 = B2,B6,B10,B14
    col3 = B3,B7,B11,B15

    m0 = dot4(row0,col0)
    m1 = dot4(row0,col1)
    m2 = dot4(row0,col2)
    m3 = dot4(row0,col3)
    
    m4 = dot4(row1,col0)
    m5 = dot4(row1,col1)
    m6 = dot4(row1,col2)
    m7 = dot4(row1,col3)
    
    m8 = dot4(row2,col0)
    m9 = dot4(row2,col1)
    m10 = dot4(row2,col2)
    m11 = dot4(row2,col3)
    
    m12 = dot4(row3,col0)
    m13 = dot4(row3,col1)
    m14 = dot4(row3,col2)
    m15 = dot4(row3,col3)
    mat = [m0,m1,m2,m3, m4,m5,m6,m7, m8,m9,m10,m11, m12,m13,m14,m15]
    
    return mat







def mortho_row(left, right, bottom, top, near, far):
    #note: if you use fov,ratio, we need change some,,
    #by cam.pos.. not. use area kinds. attr for ortho.
    mat = [0.0]*16

    a = right - left
    b = top - bottom
    c = far - near
    mat[0] = 2 / a #00
    mat[5] = 2 / b #11
    mat[10] = -2 / c #22
    mat[3] = -(right + left) / a #03
    mat[7] = -(top + bottom) / b #13
    mat[11] = -(far + near) / c #23
    mat[15] = 1.0
    return mat

def mperspective_row(fov, ratio, near, far):
    fov = radians(fov)
    
    f= 1/ tan(fov/2)

    mat = [0.0]*16

    mat[0] = f/ratio
    mat[5] = f #11 4*1+1 = 5
    mat[10] = (far+near)/(near-far) #22 4*2+2=10
    mat[11] = (2*far*near)/(near-far) #23 8+3=11    
    mat[14] = -1 #32 3*4+2=14
    mat[15] = 0 #33 4*3+3= 15
    return mat




def mlookat_row(eye,target,upV):
    front = eye-target#donno why but this way.fine. we have lot to do.
    #front = front/norm(front) #orrurs div/0
    front = normalize(front)

    right = cross(upV, front)
    right = normalize(right)

    up = cross(front, right)#donno why 2.
    up = normalize(up)
    
    minus_eye = eye*-1
    v1 = [
    right[0],right[1],right[2], dot(right , minus_eye),
    up[0],up[1],up[2], dot(up , minus_eye),
    front[0],front[1],front[2], dot(front , minus_eye),
    0,0,0,1]
    return v1

    # v1 = [
    # right[0],right[1],right[2],0,
    # up[0],up[1],up[2],0,
    # front[0],front[1],front[2],0,
    # 0,0,0,1]
    
    # #isthis just ..tx ty tz?
    # v2 = eye4()
    # v2[3] = -eye[0] #03
    # v2[7] = -eye[1] #13
    # v2[11] = -eye[2] #23
    # return mul4x4(v1,v2)
