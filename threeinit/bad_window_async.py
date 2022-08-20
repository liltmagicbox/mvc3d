from glfw.GLFW import *# we not use this.. but too ..bad.

import glfw

from wsclient import WSClient

import time



def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)

    ws = WSClient()
    #=============
    def key_callback(window, key, scancode, action, mods):
        if (key == GLFW_KEY_ESCAPE and action == GLFW_PRESS):
            glfwSetWindowShouldClose(window,True)
        if key == GLFW_KEY_A:
            print(key)
            print('a')
        elif key == GLFW_KEY_B:
            print('b')
        if action == 1:
            if key == GLFW_KEY_F:
                realkey = chr(key)#ord. key is code.
            if action == GLFW_PRESS:
                ws.send(chr(key))
                #send(realkey)

    #print(key, scancode, action, mods)
    #action 0=unp 1=pressed 2pressing
    # if action==1:
    #     event = {'type':'key_pressed','key':key}
    # elif action==2:
    #     event = {'type':'key_pressing','key':key}
    # elif action==0:
    #     event = {'type':'key_unpressed','key':key}

    glfw.set_key_callback(window, key_callback)
    #=============

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    
    glfw.terminate()

if __name__ == "__main__":
    main()

exit()







#https://webnautes.tistory.com/1103
def errorCallback(errcode, errdesc):
    print(errcode, errdesc)
glfwSetErrorCallback(errorCallback)

#===============glfw minimum requirements.
#====on setup
#glfw.init()
#(window settings)
window = glfw.create_window(640, 480, 'new window', None, None)
glfw.make_context_current(window)#we gl, we write to here.
#(event callback)
#====on_draw
# glClearColor(0, 0, 0, 1)
# glClear(GL_COLOR_BUFFER_BIT)
# glfw.swap_buffers(window)
# glfw.poll_events()
#====return ram
#glfwTerminate()
#===============glfw minimum requirements.

if not glfw.init():#need thread safe, run by mainthread.
    raise Exception('glfw init error')

class Window:
    def __init__(self, windowname = 'a window'):
        glfwSwapInterval(1)#0 too fast, tearing. 1 is mx 60fps kinds.        
        #0 or not this is ..no vsync.
        self.window = window
    
    def set_time(self, time=120):
        #just sets internal time. for test..?
        glfw.set_time(time)
    def close(self):
        window = self.window
        glfw.set_window_should_close(window,True)
        #glfwDestroyWindow
    def set_current(self):
        window = self.window
        glfw.make_context_current(window)
    def bind_input(self):
        #events = self.events not this. this becomes new object. use self.events directly.

        #bind all events. since file drop occured by event..
        #step 1. all call funcs.
        def drop_callback(path_count, paths):
            #no window, why??
            #https://www.glfw.org/docs/3.3/group__input.html#ga1caf18159767e761185e49a3be019f8d
            #path_count
            #<glfw.LP__GLFWwindow object at 0x0000028FE773B7C0>
            #print(int(path_count))#b'\x90\xca\xc5\xd7\x97\x02\x00\x00' .. bury it.
            #paths
            #['C:\\Users\\liltm\\Desktop\\vvv.png', 'C:\\Users\\liltm\\Desktop\\ff.png']    
            print(paths)
            event = paths
            self.events.append(event)

        def key_callback(window, key, scancode, action, mods):
            #if (key == GLFW_KEY_ESCAPE and action == GLFW_PRESS):
            #    glfwSetWindowShouldClose(window,True)
            #print(key, scancode, action, mods)
            #action 0=unp 1=pressed 2pressing
            if action==1:
                event = {'type':'key_pressed','key':key}
            elif action==2:
                event = {'type':'key_pressing','key':key}
            elif action==0:
                event = {'type':'key_unpressed','key':key}
            self.events.append(event)

        #step 2. actual bind.
        window = self.window
        glfw.set_key_callback(window, key_callback)
        glfw.set_drop_callback(window, drop_callback)

    def input(self, events):
        1#print(events)
    def update(self, dt):
        1
    def draw(self):
        1
    def run(self):
        window = self.window
        timewas = 0
        while not glfw.window_should_close(window):
            #input, update(ai,physics), draw 3-type.
            #---1 input
            self.input(self.events)
            self.events = []

            #---2 update
            #t = glfw.get_timer_value()#20540838386 2054 is seconds.
            t = glfw.get_time()
            dt = t-timewas
            self.update(dt)
            
            #---3 draw
            glClearColor(0, 0, 0, 1)
            glClear(GL_COLOR_BUFFER_BIT)
            self.draw()#[]=empty world
            # Swap front and back buffers
            glfw.swap_buffers(window)
            glfw.poll_events()#this , is the input! but to next time!

        glfw.terminate()#This function destroys all remaining windows and cursors, 

