from time import time

import pyglet
#from pyglet.gl import *
#https://pyglet.readthedocs.io/en/latest/programming_guide/graphics.html

from pyglet.graphics import vertex_list, vertex_list_indexed, Batch
#pyglet.graphics.vertex_list


from OpenGL.GL import *
from OpenGL.GL import shaders
#=============================== SHADER
vertn = """
#version 410

layout (location = 0) in vec3 pos;
layout (location = 1) in vec2 uv;

out vec2 uvcord;

uniform int idx;
uniform mat4 Model[252];//253 max.. why not 255? 250 to remember easy
uniform mat4 View;
uniform mat4 Projection;

void main() 
{
    gl_Position = Projection * View * Model[idx] * vec4(pos,1);
    uvcord = uv;
}
"""

fragn = """
#version 410

in vec2 uvcord;

out vec4 outcolor;

uniform sampler2D tex0;
uniform sampler2D tex1;

void main()
{
    //outcolor = vec4(uvcord,1,1 );
    outcolor = texture2D(tex0, uvcord);
    //outcolor = mix(texture(tex0, uvcord), texture(tex1, uvcord), 0.4);
}
"""
vshader = shaders.compileShader( vertn, GL_VERTEX_SHADER)
fshader = shaders.compileShader( fragn, GL_FRAGMENT_SHADER)
shader_default = shaders.compileProgram( vshader,fshader)


#-----------window setting must be first, later gl settings.
window = pyglet.window.Window()
window.set_size(800, 600)
window.set_exclusive_mouse(True) #lock mouse x,y 0, hold. use dxdy!

window.set_vsync(False)
#============gl settings
glEnable(GL_DEPTH_TEST) #--skip depth less
pyglet.gl.glPointSize(5)



#--------------------------mesh data
from fastestobjread import OBJ
objname = 'resources/obj4ue4/obj_ue4_zupyfo_x1.obj'

from pymatrix import vec3, normalize, cross
from pymatrix import mperspective, mortho, mlookat

import math
from math import cos,sin,radians


def xquataxis(v1,v2):
    front = glmmat.normalize(v1)
    facing = glmmat.normalize(v2)
    
    #---qv
    axis = glmmat.cross(front, facing)#result not unit vector
    axis = glmmat.normalize(axis)
    #---qs    
    th = glmmat.acos( glmmat.dot(front,facing) )
    return axis,th


#-==--=--==--==--==-===-classs
#- we use world=Gameworld, which has up,front. for gravity or kinds.. no magic number.


class Gameworld:
    def __init__(self, shader=None ):
        self.front = vec3(1,0,0)
        self.up = vec3(0,1,0)

        self.actor = []
    def front_copy(self): #do we need it? .,. yeah if you not use ndarray more..
        return vec3(self.front)
    def up_copy(self):
        return vec3(self.up)

    def update(self,dt):
        for actor in self.actor:
            actor.update(dt)
    
    def get(self, name):
        for actor in self.actor:
            if actor.name == name:
                return actor
        return None

        

class Actor:
    def __init__(self): #name?? no. world.add do so.
        self.pos = vec3()
        self.speed = vec3()
        self.speed_factor = 10 #once it was 100000, float uncertainty occured.ha.

        self.front = world.front_copy()
        #self.right = vec3(0,-1,0) we calc when we want.
        self.up = world.up_copy() # yup..yeah..

        #---check if we need re-calculate rotmat. ..is it badway for steady fps? --but for maxfps!
        self.front_before = vec3(self.front) #if glm, it may not work. .. better than vec3(front)

        self.isgravity = False
        self.gravity_factor = 9.8 #if worldglobal, there will no be floting mascote..

        self.mesh_list = [] # a mesh is just [vbo, [textures]]

        self.scale = 1
        
        #---instant make 4x4 by front-up. just save 4x4rotmat for save time.
        #self.qv = vec3(0,0,0)
        #self.qs = 1
        self.rotxyz = 0,0,0#plane tuple. use actor.rotxyz[0] kinds.

        #self.name = 'actor' #actor_get_name('plane1')
        self.name = type(self).__name__#to access __ feels not good..
        
    def move_front(self,speed):
        self.speed = self.front * speed * self.speed_factor
    def move_right(self,speed):
        right = cross(self.front, self.up)
        self.speed = right * speed * self.speed_factor
    def move_up(self,speed):
        self.speed = self.up * speed * self.speed_factor

    def move_front_world(self,speed):
        self.speed = world.front * speed * self.speed_factor
    def move_right_world(self,speed):
        right = cross(world.front, world.up)
        self.speed = right * speed * self.speed_factor
    def move_up_world(self,speed):
        self.speed = world.up * speed * self.speed_factor
    
    def update(self,dt):
        #note cam also actor!
        #if self.isfreeze return0 kinds.
        if self.isgravity:
            self.speed -= self.up*dt *self.gravity_factor

        #dt*self.speed error occurs.
        self.pos += self.speed*dt

        #---- update_add added. may it be good?
        self.update_add()
    def update_add(self):
        pass

    def mesh_add(self, mesh):
        self.mesh_list.append(mesh)

    def get_matrix_model(self):
        axis,th = quataxis(glmmat.vec3(world.front), glmmat.vec3(self.front))
        worldrot = glmmat.rotmat(axis,th)
        mmodel = mtrans(self.pos)@worldrot@mrotxyz(self.rotxyz)@mscale(self.scale)
        #mmodel = mtrans(self.pos)@mrotxyz( (60,0,30) )@mscale(self.scale)

        mmodel = mtrans(self.pos)@mrotxyz(self.rotxyz)@mscale(self.scale)        
        return mmodel

    def on_key_press(self,symbol):
        pass
    def on_key_release(self,symbol):
        pass


class Camera(Actor):
    def __init__(self):
        super(Camera, self).__init__()

        self.front = vec3(0,0,-1)
        
        #self.yaw = -90# means LH, ..fine.
        self.yaw = math.degrees(math.asin(self.front.z))
        self.pitch = 0

        self.target = None
        self.istrack = False
        
        self.isperspective = True
        self.fov = 50
        self.window_ratio = 800/600
        self.near = 0.1
        self.far = 100

    def mouse_move(self, dx,dy):
        #yaw LH rule, but works as we expect. use front, not yaw directly.
        yaw = self.yaw
        pitch = self.pitch

        sensitivity = 0.1
        dx *= sensitivity
        dy *= sensitivity        

        yaw += dx
        pitch += dy
        if (pitch > 89.0): #not pitch = max kinds.
            pitch = 89.0
        if (pitch < -89.0):
            pitch = -89.0
        
        #----------- fpscam, by yaw & pitch.
        #---note we do not use up-vector. it's just done by yaw,pitch.
        #since in view mat: target = cam.pos+cam.front
        front = vec3(0,0,0)
        front.x = cos(radians(yaw)) * cos(radians(pitch))
        front.y = sin(radians(pitch))
        front.z = sin(radians(yaw)) * cos(radians(pitch)) 
        
        #ssems normalized but do again..
        self.front = normalize(front)
        self.yaw = yaw
        self.pitch = pitch


    
    def get_matrix_projection(self):#was set_..
        fov = self.fov
        window_ratio = self.window_ratio
        near = self.near
        far = self.far
        if self.isperspective:
            mprojection = mperspective(fov, window_ratio, near,far)
        else:
            mprojection = mortho(-5,5,-5,5,0.1,100)            
        return mprojection

    def get_matrix_view(self):
        eye = self.pos
        target = self.pos+self.front
        upV = self.up
        #target = world.actor_get('Car',0).pos
        # try:
        #     #target = world.actor_get('Missile',-1).pos
        #     target = world.actor_get('Car',-1).pos
        # except:
        #     pass
        mview = mlookat(eye,target,upV)
        return mview



    def update(self,dt):
        super().update(dt)
        #self.target = self.pos + self.front #was for camera only. yeah.
        if self.istrack:
            if self.target:
                front = self.target.pos - self.pos
                self.front = normalize(front)
    
    #seems better: target, on=True on=False..?
    # def keep_eye_on(self, target):
    #     front = target.pos - self.pos
    #     self.front = normalize(front)
    # def keep_eye_on_release(self):
    #     self.front = self.pos + self.front_default

    


import numpy as np

def objrows2(objname):
    obj =OBJ(objname)
    
    try:
        pic = pyglet.image.load(obj.texture)
        texture = pic.get_texture()
        print(obj.multices, objname)
    except:
        texture = None

    faces = obj.idxs#indices better

    vertex_count = len(obj.multices)
    vertex_xyz = []
    vertex_uv = []

    for multex in obj.multices:
        vert = multex[0]
        uv = multex[1]
        vertex_xyz.extend(vert)
        vertex_uv.extend(uv)
    #-------- we have vertex_xyz,vertex_uv, faces, and texture. not textures.
    #vertex_xyz = [1,2,3,4,0.0] #anyway if has float,it'sfloat64.

    vxyz = np.array( vertex_xyz) # ,dtype='f') #f 32, float 64.huh..
    #print(vxyz.dtype)
    vuv = np.array( vertex_uv)
    vface = np.array( faces ) # better then indices, i think..
    #print(vface.dtype)#int32!HUH..

    #vertices for vertex buffer array
    xyz = vxyz.reshape(-1,3)
    uv = vuv.reshape(-1,2)#actually this not changes, also.
    #vface.reshape(-1,1) this never changes, send to VEO.
    vertices = np.hstack([xyz,uv]) #since 3+2. cant vstack of xyz
    #print(vertices.shape) 30,5, fine.

    #indices for v e o
    indices = vface
    
    vertices = vertices.flatten().astype('float32') #4
    indices =indices.astype('uint')

    #vertices = vertices.flatten()[:46].astype('float32') #4
    #indices =np.array([0,1,2, 3,4,5, 6,7,8]).astype('uint')
    #vertices = np.array([0,0,0, 0,0,  0.5,0,0, 1,0,  0.5,0.5,0, 1,1,  0,0.5,0, 0,1,  0,-0.5,0.50, 0,1]).astype('f')
    #indices =np.array([0,1,2,0,2,3, 0,2,4]).astype('uint')
    
    return vertices,indices,texture

objname = 'resources/snowspike/snowspike.obj'
objv,obji,objt = objrows2(objname)


class VAO_indexed:
    def __init__(self, stride,  vertices, indices, nth_xs_tuple, row_major=True, *args   ):
        datatype = GL_FLOAT
        iscolumn = GL_FALSE
        if not row_major:
            iscolumn = GL_TRUE
        fsize = np.float32(0.0).nbytes
        
        VAO = glGenVertexArrays(1) # create a VA. if 3, 3of VA got.
        VBO = glGenBuffers(1) #its buffer, for data of vao.fine.
        EBO = glGenBuffers(1) #indexed, so EBO also. yeah.

        glBindVertexArray(VAO) #gpu bind VAO

        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        
        pre_offset = 0
        for i in range(int(len(nth_xs_tuple)/2)):
            nth = nth_xs_tuple[i*2]
            size = nth_xs_tuple[i*2+1]

            if pre_offset==0:
                offset = None
                glVertexAttribPointer(nth, size, datatype, iscolumn, stride * fsize, offset)
                glEnableVertexAttribArray(nth)
                pre_offset = size    
            else:
                offset = ctypes.c_void_p( pre_offset *fsize)
                glVertexAttribPointer(nth, size, datatype, iscolumn, stride * fsize, offset)
                glEnableVertexAttribArray(nth)
                pre_offset +=size
            
        self.VAO = VAO
        self.VBO = VBO
        #self.mode = GL_TRIANGLES some model drawn lines kind thing requires not use it.
        self.size = len(indices)

    def update_vertices(self,vertices):
        VAO = self.VAO
        VBO = self.VBO
        glBindVertexArray(VAO)
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        #GL_STREAM_DRAW for little change, if you want someday..
        



vaocart = VAO_indexed( 5,
    np.array([0,0,0, 0,0,  0.5,0,0, 1,0,  0.5,0.5,0, 1,1,  0,0.5,0, 0,1, ]).astype('f'),
    np.array([0,1,2,0,2,3,]).astype('uint'),
    (0,3,1,2)
    )

vaocart = VAO_indexed( 5,
    objv,
    obji,
    (0,3,1,2)
    )

from PIL import Image

def texture_load(imgname):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture) # all upcoming GL_TEXTURE_2D operations now have effect on this texture object
    # set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # set texture wrapping to GL_REPEAT (default wrapping method)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # load image, create texture and generate mipmaps
    try:
        img = Image.open(imgname)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)

        img.close()

    except:
        print("Failed to load texture")

    return texture

texturex = texture_load('texture.jpg')
qpittex = texturex



    

class Controller:
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.mouseX_before = 0
        self.mouseY_before = 0

    def on_mouse_motion(self, x,y,dx,dy):
        self.mouseX += dx
        self.mouseY += dy
    def on_mouse_press(self, x, y, button, modifiers):
        1
    def on_key_press(self,symbol,modifiers):
        actor = world.player
        if symbol == key.W:
            actor.move_front(1)
        if symbol == key.S:
            actor.move_front(-1)
        if symbol == key.A:
            actor.move_right(-1)
        if symbol == key.D:
            actor.move_right(1)
    def on_key_release(self,symbol,modifiers):
        actor = world.player
        if symbol == key.W:
            actor.move_front(0)        
        if symbol == key.S:
            actor.move_front(0)
        if symbol == key.A:
            actor.move_right(0)
        if symbol == key.D:
            actor.move_right(0)

    def get_dxdy(self):
        dx = self.mouseX - self.mouseX_before
        dy = self.mouseY - self.mouseY_before
        self.mouseX_before = self.mouseX
        self.mouseY_before = self.mouseY
        return dx,dy
    def update(self, dt):
        dx,dy = self.get_dxdy()
        world.get('default_camera').mouse_move(dx,dy)
        return 0


controller = Controller()

world = Gameworld()

cam = Camera()
cam.name = 'default_camera'
world.actor.append(cam)
world.player = cam
cam.far = 1000
cam.pos = vec3(0,0.5,2)

#=====================================MOUSE EVENT
@window.event
def on_mouse_motion(x, y, dx, dy):
    controller.on_mouse_motion(x, y, dx, dy)
@window.event
def on_mouse_press(x, y, button, modifiers):
    controller.on_mouse_press(x, y, button, modifiers)
#=====================================KEY EVENT
from pyglet.window import key
@window.event
def on_key_press(symbol,modifiers):
    controller.on_key_press(symbol,modifiers)
@window.event      
def on_key_release(symbol, modifiers):
    controller.on_key_release(symbol,modifiers)


def update(dt):
    if not dt==0:
        1
        print(1/dt)
    controller.update(dt)
    world.update(dt)
pyglet.clock.schedule(update)

@window.event
def on_draw():
    gldraw()

# a = glGetIntegerv(GL_MAX_VERTEX_ATTRIBS) 
# print(a)
# a = glGetIntegerv(GL_MAX_VERTEX_UNIFORM_VECTORS)# number of 4 vectors.
# # since it 1024, 4of 4vectors, 1024/4, 255 kinds.yeah.
# print(a)
# exit()
#print(glGetIntegerv(GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB))
#print(glGetIntegerv(GL_MAX_VERTEX_UNIFORM_COMPONENTS))#4096.. donno why.anyway.
#maybe we manually set and if err occurs, change value..kinds.yeah we use python.
#music = pyglet.resource.media('resources/beesound.mp3')# pyinstaller err. only mp3.
#music.play()

source = pyglet.media.load('beesound.mp3')
player = pyglet.media.Player()
player.queue(source)
#player.play()

import numpy as np
import pymatrix
import random
maxvec4 = glGetIntegerv(GL_MAX_VERTEX_UNIFORM_VECTORS)
max4x4 = int(maxvec4/4)-4 #for save reason..


totalN=6500 # 66% speed up from 2000-4x4each.
#we started by noticing: 4x4 14%, int 7%, draw16%. elimated of 4x4 14%.

batchN = int(totalN / max4x4)+1 # 10/3 we need 3*4..

#modelcol = 250
modelcol = max4x4
modelrow = 16
modelN = modelcol*modelrow
area = 50
def get_batch():
    models = np.zeros(modelN).reshape(modelcol,modelrow).astype('float32')
    for i in range(modelcol): #glm had booster, x2speed after 2sec but no with py. ..booster found.
        x = random.uniform(-area,area)#randint 20s of line.
        y = random.uniform(-area,area)
        z = random.uniform(-area,area)
        modelmat = pymatrix.eye4()
        modelmat[3]=x
        modelmat[7]=y
        modelmat[11]=z
        models[i] = modelmat
    return models

models = []
for i in range(batchN):
    models.append( get_batch() )

#@profile
def gldraw():
    #glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.0, 0.24, 0.5, 1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  

    program = shader_default
    glUseProgram(program)


    #=====================    
    # MVP minimum setting: eye4.
    # note: view mat requires atleast +z offset. if z=0, not working. (or clipped and see nothing maybe)
    #projectionmat = pymatrix.eye4()
    #viewmat = pymatrix.eye4()
    #viewmat[3]=-0  #x
    #viewmat[7]=-0  #y
    #viewmat[11]=-2 #z
    # glUniformMatrix4fv Transpose option True for row-major.

    #===EXAMPLE: Transpose = True check via modelmat.
    #modelmat = glm_modelmat.eye4()
    #modelmat[3]=1 #with True not this.(row major)
    #modelmat[12]=5 with glTransepose = False (col.major)



    camera = world.get('default_camera')

    fov = camera.fov
    window_ratio = camera.window_ratio
    near = camera.near
    far = camera.far
    projectionmat = mperspective(fov, window_ratio, near,far)
    
    eye = camera.pos
    target = camera.pos+camera.front
    upV = camera.up
    viewmat = mlookat(eye,target,upV)    
    
    
    #projectionmat = world.get('default_camera').get_matrix_projection() #want world.currentcam kidns..
    #viewmat = world.get('default_camera').get_matrix_view()
    modelmat = pymatrix.eye4()
    modelmat = np.array(modelmat).astype('float32')
    
    projectionmatID = glGetUniformLocation(program, "Projection")
    viewmatID = glGetUniformLocation(program, "View")
    modelmatID = glGetUniformLocation(program, "Model")    
    glUniformMatrix4fv(projectionmatID,1,True, projectionmat)
    glUniformMatrix4fv(viewmatID,1,True, viewmat)
    #glUniformMatrix4fv(modelmatID,1,True, modelmat)# True for row major.ha.[1,2,3,4, ,]

    glBindVertexArray(vaocart.VAO)
    glBindTexture(GL_TEXTURE_2D, texturex)
    #glDrawElements(GL_TRIANGLES, vaocart.size, GL_UNSIGNED_INT, None)

    
    #faster way: send 4x4 once, draw by idx
    #======================= send 4x4 once, just change idx. ////modelmat=[*model] ,draw model[i]
    # modelmat2 = pymatrix.eye4()
    # modelmat2 = np.array(modelmat).astype('float32')
    # modelmat2[3]=1
    # modelmat2[7]=0
    # modelmat2[11]=0
    # #longmodel = np.array([modelmat, modelmat2])
    # longmodel = np.append(modelmat, modelmat2)
    # locationOfMatrix = glGetUniformLocation(program, "Model")
    # glUniformMatrix4fv(locationOfMatrix,2,True, longmodel)# not 1, but 2! hahaha.

    
    # idxID = glGetUniformLocation(program, "idx")
    # glUniform1i(idxID, 0)
    # glDrawElements(GL_TRIANGLES, vaocart.size, GL_UNSIGNED_INT, None)

    # idxID = glGetUniformLocation(program, "idx")
    # glUniform1i(idxID, 1)
    # glDrawElements(GL_TRIANGLES, vaocart.size, GL_UNSIGNED_INT, None)
    #======================= send 4x4 once, just change idx.
    
    

    idxID = glGetUniformLocation(program, "idx")
    
    for i in range(batchN):
        glUniformMatrix4fv(modelmatID,modelcol,True, models[i])
        for i in range(modelcol):
            glUniform1i(idxID, i)
            glDrawElements(GL_TRIANGLES, vaocart.size, GL_UNSIGNED_INT, None)
    return 0

    #print(models)
    glUniformMatrix4fv(modelmatID,modelcol,True, models)

    glBindVertexArray(vaocart.VAO)
    glBindTexture(GL_TEXTURE_2D, texturex)
    idxID = glGetUniformLocation(program, "idx")
    #glUniformMatrix4fv(modelmatID,1,True, modelmat)
    for i in range(modelcol):
        glUniform1i(idxID, i)
        glDrawElements(GL_TRIANGLES, vaocart.size, GL_UNSIGNED_INT, None)
    return 0

pyglet.app.run()
