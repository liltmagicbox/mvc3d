from glfw.GLFW import *
from OpenGL.GL import *

from queue import Queue
from time import perf_counter

from asset import AssetManager
from actorcamera import Camera,Actor

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
        self._mouse_lock = False
        self.mouse_xy_before = self.mouse_xy
        self._bind()
        self.camera = Camera(ratio = w/h)

        ddict = {'id':5595, 'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'default'}
        aa = Actor( **ddict)
        self.scene = [aa]
        self.asset = AssetManager()

    
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
        glfwSetKeyCallback(self.window, key_callback)
        
        # def cursor_pos_callback(window, xpos,ypos):
        #     #https://www.glfw.org/docs/3.3/input_guide.html#events
        #     W,H = self.size
        #     mx = xpos/W
        #     my = ypos/H
        #     self.mouse_xy = (mx,my)
        # glfwSetCursorPosCallback(self.window, cursor_pos_callback)

        #==============
        def fb_size_callback(window, width, height):
            self.size = width,height
            glViewport(0, 0, width, height)#need context?
            self.camera.ratio = width/height
        glfwSetFramebufferSizeCallback(self.window, fb_size_callback)        

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
            self.draw()

            glfwSwapBuffers(window)
            #glfwWaitEventsTimeout(5)
    
    #======API
    def input(self, inputs):
        [print(i) for i in inputs ]
        #simulator.input(inputs)
        [glfwSetWindowShouldClose(self.window,True) for i in inputs if i['key']==256]
        for i in inputs:
            if i['key']=='D':
                self.camera.pos.x+=0.1
            if i['key']=='A':
                self.camera.pos.x-=0.1

        
    def update(self,dt):
        x,y = self.mouse_xy
        xx,yy = self.mouse_xy_before
        dx,dy = x-xx, y-yy
        self.camera.rotate_dxdy(dx,dy)
        self.mouse_xy_before = x,y

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

        #===behold and see!
        #ddict = {'pos':[0,0,0],'rot':[0,0,0],'scale':[1,1,1], 'mesh':'default'}
        x,y = self.mouse_xy
        print(x,y)

        X,Y = 2*x-1, 2*y-1

        vpmat = self.camera.get_vpmat()      

        for actor in self.scene:
            #actor.pos = (X,Y,0)
            modelmat = actor.get_modelmat()
            mesh = self.asset.get_mesh(actor.mesh)
            mat,geo = mesh.mat,mesh.geo

            #========internal draw seq.
            mat.bind()
            mat.set_vpmat(vpmat)
            mat.set_modelmat(modelmat)
            
            geo.bind()
            geo.draw()
    #===========================
    @property
    def mouse_xy(self):
        xpos,ypos = glfwGetCursorPos(self.window)
        W,H = self.size
        mx = xpos/W
        my = -ypos/H# 0bottom 1top
        return mx,my
    
    @property
    def mouse_lock(self):
        return self._mouse_lock
    @mouse_lock.setter
    def mouse_lock(self, value):
        if value == True:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
            #if glfwRawMouseMotionSupported():
                #glfwSetInputMode(self.window, GLFW_RAW_MOUSE_MOTION, GLFW_TRUE)
            #disables acc , seems weird! but accu acc.
        else:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)            
        self._mouse_lock = value
    




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
    




window = Window()
window.mouse_lock=True
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