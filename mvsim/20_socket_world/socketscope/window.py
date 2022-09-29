from glfw.GLFW import *

from queue import Queue
from time import perf_counter

ISINIT = False
def _pre_window_init(for_rpi ):
    global ISINIT
    if ISINIT:        
        return
    ISINIT = True
    #==init glfw
    if not glfwInit():#need thread safe, run by mainthread.
        raise Exception('glfw init error')
    #===pre-window
    if not for_rpi:
        major,minor = (4,3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, major)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, minor)

    else:
        #3.0 no 3.1 yeah
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1)
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, False)
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_ANY_PROFILE)
    #========
    #see window_tests
    #glfwWindowHint(GLFW_RESIZABLE,GLFW_FALSE)
    #glfwWindowHint(GLFW_FLOATING, GLFW_TRUE)
    #glfwWindowHint(GLFW_TRANSPARENT_FRAMEBUFFER, GLFW_TRUE)
    #glfwWindowHint(GLFW_CENTER_CURSOR , GLFW_TRUE)
    #glfwWindowHint(GLFW_DECORATED , GLFW_FALSE)#cool! no frame!
    
    #glfwWindowHint(GLFW_SAMPLES,4)#MSAA works fine. without glEnable(GL_MULTISAMPLE).



from OpenGL.GL import *

class Window:
    def __init__(self, size=(640,480), name = 'a window', vsync = True, for_rpi = False ):
        _pre_window_init(for_rpi)
        #==window
        w,h = size
        window = glfwCreateWindow(w,h, name, None, None)
        if not window:
            glfwTerminate()
        glfwMakeContextCurrent(window)
        #===settings after window
        vsinterval = 1 if vsync else 0
        glfwSwapInterval(vsinterval)#1 to vsync.. 10 maybe 10x slower monitor hz.        
        
        self.window = window
        self.size = size
        
        self._input_queue = Queue()
        self.mouse_xy = 0
        self._bind()

        self.view_model = {}
        self.asset = {
            'default' : 1
        }

    def _bind(self):        
        def key_callback(window, key, scancode, action, mods):
            #if (key == GLFW_KEY_SPACE and action == GLFW_PRESS):
            if key>50 and key<100:
                abskey = chr(key)
            else:
                abskey = key
            value = int(action)
            data = {'key':abskey, 'value':value, 'player':737}
            self._input_queue.put(data)
        
        def cursor_pos_callback(window, xpos,ypos):
            #https://www.glfw.org/docs/3.3/input_guide.html#events
            W,H = self.size
            mx = xpos/W
            my = ypos/H
            self.mouse_xy = (mx,my)
        glfwSetKeyCallback(self.window, key_callback)
        glfwSetCursorPosCallback(self.window, cursor_pos_callback)


        def errorCallback(errcode, errdesc):
            print('ERR',errcode, errdesc)
        glfwSetErrorCallback(errorCallback)

    def run(self):
        window = self.window
        
        time_0 = perf_counter()
        while not glfwWindowShouldClose(window):
            #===clear
            glClearColor(0, 0.0, 0.5, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            #===input
            glfwPollEvents()#this , is the input!
            inputs = []
            iq = self._input_queue
            while not iq.empty():
                inputs.append( iq.get() )
            self.input(inputs)
            
            #===update
            time_1 = perf_counter()
            dt = time_1-time_0
            time_0 = time_1
            self.update(dt)
            #===draw
            self.draw(self)

            glfwSwapBuffers(window)
            #glfwWaitEventsTimeout(5)
    
    #======API
    def input(self, inputs):
        [print(i) for i in inputs ]
        #simulator.input(inputs)
        [glfwSetWindowShouldClose(self.window,True) for i in inputs if i['key']==256]
        
    def update(self,dt):
        print(dt)
        1#simulator.tick(dt)
        view_update_data = {
        '5549':{'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1]},
        #'5546':{'4x4':[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]},#hopely, not this. transfer small data rule.
        }
        #[5549,0,0,0,0,0,0,1,1,1]#fast byte data. json byte overhead! bytes= 32*10. 320B.. or 32*7,usually.
        #however, 12345, 1.2345 5.6789 9.1234 , 20B.,.not!
        #BBBBB BBBBB BBBBB VS BBBB BBBB BBBB ..32bit wins. ..never mind.
    def draw(self):
        #===update view_model.
        #vc = simulator.get_view_command()
        #self.view_model.update(vc)        
        #===real draw
        view_model = {5595: {'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'box'} }

        #for vid, data in view_model.items():
        #    pos = data['pos']

    def _draw(self):
        # ue4, we have assets, and actors. we need both.
        # js, we have somewhere loaded mat,geo. and Mesh. and Mesh is actor, created.
        #js store geo,mat. -> Mesh(Actor)
        #ue4 geo,mat,Mesh(Actor) -> Mesh_created.
        #objloader -> object
        self.view_model
        self.asset
        #object.copy
        #getObjectByName getObjectById
        #1.load a model = object = StaticMeshActor
        #2.copy-clone-instance to the world.
        #3. change mat or copy ->mat2, change and assign.








#from OpenGL.GL import *
#from OpenGL.GL import shaders
#vshader = shaders.compileShader( vertn, GL_VERTEX_SHADER)
#fshader = shaders.compileShader( fragn, GL_FRAGMENT_SHADER)
#default_shader = shaders.compileProgram( vshader,fshader)


#shader -> vao ->
# mat -> geo.

#Scene
#Object

        
# Material()
# Shader()
# Texture()

# Geometry()
# VAO()

# Object3D
# Scene


# mat.bind()

# viewprojection = camera.get_view_projection()
# mat.set_VP(viewprojection)

# modelmat = object3d.get_model()
# mat.set_M(modelmat)

# geo.draw()

#class Shader:
#class VAO:

# vao_attrs={
#     'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
#     'uv' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
#     }
# vao_indices = np.array([0,1,2,0,2,3,]).astype('uint')


class Material:
    def __init__(self, shader,textureDict):
        self.shader = shader
        self.textureDict = textureDict
    def bind(self):
        self.shader.bind()
    def set_vp(self, vpmat):
        self.shader.set_mat4('ViewProjection', vpmat)
    def set_model(self, modelmat):
        self.shader.set_mat4('Model', modelmat)

#s = Shader()
#a = Material()


class Geometry:
    def __init__(self):
        self.vao = vao
    def draw(self):
        self.vao.bind()
        self.vao.draw()












window = Window()
#window.keyinput = lambda key:print('key',key)





vertn = """
#version 410 core
layout (location = 0) in vec3 pos;
layout (location = 1) in vec2 uv;

out vec2 uv_out;

uniform mat4 Model;
uniform mat4 ViewProjection;

void main() 
{
    //gl_Position = vec4( pos, 1);
    gl_Position = Model * vec4(pos,1);
    uv_out = uv;
}
"""

fragn = """
#version 410 core

in vec2 uv_out;
out vec4 FragColor;

uniform sampler2D tex0;
uniform sampler2D tex1;

void main()
{
    //FragColor = vec4(1,0,1,1);
    FragColor = texture2D(tex0, uv_out);
}
"""
from shader import Shader
from texture import Texture
from vao import VAO

import numpy as np
#modelmat = np.array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]).astype('float32')
modelmat = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

#modelmat[3]=0.5
modelmat[12]=0.2
modelmat[13]=0.2
modelmat[14]=0.2
#modelmat[7]=0
#modelmat[11]=0

s = Shader(vertn,fragn)
s.bind()
s.set_mat4('Model',modelmat)

t = Texture('frz.png')

vao_attrs={
    'position' : [ 0,0,0, 1,0,0, 1,1,0, 0,1,0,],
    'uv' : [ 0,0,  1,0,  1,1,  0,1 ],
    }
vao_indices = [0,1,2,0,2,3,]

vao = VAO(vao_attrs,vao_indices)

def testdraw(self):
    view_model = {5595: {'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'default'} }
    for actorid, actor in view_model.items():
        pos = actor['pos']
        rot = actor['rot']
        scale = actor['scale']
        mesh = actor['mesh']

        #geo,mat = self.asset.get(mesh, self.asset['default'] )
        #print(self.mouse_xy)
        vao.draw()

        #mat.bind()
        #mat.set_vp(vpmat)
        #mat.set_model(modelmat)        
        #geo.draw()

window.draw = testdraw
window.run()


exit()


# rman = Renderer()

# rman.render(world)

# #============
# #actor1 = Mesh('rocket')
# #actor2 = Mesh('box')
# #actor2.position = 1,1,1

# actor = Actor()

# world = World()
# world.add(actor)

# #=way 1
# renderer = Renderer()
# while True:
#     world.input({'key':'A'})
#     renderer.tick(world)
#     renderer.render(world)

# #way2
# simulator = Simulator()
# simulator.run(world)




"""
    def draw(self):
        1#print('draw')
        # ID : {pos,rot,scale,}
        # id, pos,rot,scale, geoid, matid(even it was created by meshid.)
        view_model = {
        '5549':{'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'geoid':1, 'matid':1},
        }
        #geo,mat split if modified. target:mat or target:actor.
        #actor.mat.tex1 = newdata => {'5595',}
        #mat.tex1 = newdata
        #datatypes:
        #0:pos, 1:pos,rot 2:pos,rot,scale
        #3:geo
        
        #/target   key       value
        # actor    pos       [1,0,0]
        # actor    matid     3393
        # geometry positions newdata
        # material tex1      newdata
        
        update_jsondata = {
        5549:
        {'pos':[1,0,0],
        'rot':[0,0,1]
        }
        }
        update_bytedata = [5549,'pos',[1,0,0],'rot',[0,0,1]]
        update_bytedata = [5549,'p',[1,0,0],'r',[0,0,1]]        #need update both protocol..

        geos = {
        0: SphereGeometry(),
        1: BoxGeometry(),
        }
        mats = {
        0: Material('default'),
        1: Material('checker')
        }


        Material()
        Shader()
        Texture()

        Geometry()
        VAO()

        mat.bind()
        geo.draw()


        view_model = {
        '5549':{'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'geoid':1, 'matid':1},
        }
        #obj_load('box.obj')
        storage.load('box')#stored mat,tex? ,geo.
        #ue4 SM, mat(Tex) .
        #sm = Mesh(geo,mat)

        view_model = {
        '5549':{'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'box' },
        '9949':{'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'star', 'positions':[0,1,2, 0,1,2,] },
        }
        #not thisway.

        #only via command.
        'create', 5549,0-,0-,1-,'box'
        'pos': 1,0,0
        #========create/delete
        static mesh
        skeletal mesh
        particles
        #=====modify
        pos,rot,scale
        mesh

        #copy mat->mat2, overwrite data.?
        #===5AM.
        view_command = {5595:{'pos':[2,0,0],'rot':[1,0,1]} }
        view_model = {5595: {'pos':[1,0,0],'rot':[1,0,1],'scale':[1,1,1], 'mesh':'box'} }

        #view_controller /<-view_command<- sim
        #view_controller(viewmodel compat.) <-VC/VM ~|~ <-VC/VM socket_vc(with viewmodel dealer) /<-view_command<- sim
        #viewer onetime uses viewmodel. dose not store dict!

        #ue4 loads obj, creates mat,  finally mesh.
        #ue4 commanded, copy mesh's material, changes texture. named mat2
        #ue4 commanded, SM_actor2's material is changed to mat2.        
        #all same.fine.+

        {5595: {'mesh':'box'} } #=> box_geo , box_mat

        {'box_mat': {'copy':'box_mat2'} }
        #{'box_mat2_tex': {'copy':'box_mat2'} }
        #{'box_mat2': {'tex0':'box_mat2'} }#not that yet ue4. need xy coords -> node shader kinds..
        {'box_mat2': {'color':[255,0,0]} }#of node. uniform value,most.

        {5595:'mat':'box_mat2'}
        #https://docs.unrealengine.com/4.26/en-US/BlueprintAPI/Utilities/GetClass/
        #ue4 bp fail. we need c++. 0.socket in /1.spawnActor via(ifnot) and add. /2.foreach dict, update data.fine.
        #and BP actor has var, of id. fine.
        #

        #we cnat, 1.create newmat33 , 2.load viewmodel.. have not newmat33. replaced default. ..thats the way.
        #instanced! 300 meshes..

"""