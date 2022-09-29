from OpenGL.GL import *
from OpenGL.GL import shaders

class Shader:    
    def __init__(self, vertstr, fragstr):
        assert bool(glCreateShader)#sometimes compile error occurs, before window() 
        vshader = shaders.compileShader( vertstr, GL_VERTEX_SHADER)
        fshader = shaders.compileShader( fragstr, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram( vshader,fshader)
        glDeleteShader(vshader)
        glDeleteShader(fshader)
        self.ID= program
        self._loc_cache = {}

    def bind(self):
        glUseProgram(self.ID)        
    def unbind(self):
        glUseProgram(0)

    def point_size(self,size):
        glPointSize(size)

    def get_loc(self, uniform_name):
        loc = self._loc_cache.get(uniform_name)
        if not loc:
            program = self.ID
            loc = glGetUniformLocation(program, uniform_name)
            self._loc_cache[uniform_name] = loc
        return loc

    def set_int(self, uniform_name, value):
        loc = self.get_loc(uniform_name)
        glUniform1i(loc,value)
    def set_float(self, uniform_name, value):
        loc = self.get_loc(uniform_name)
        glUniform1f(loc,value)
    def set_vec3(self, uniform_name, x,y,z):
        loc = self.get_loc(uniform_name)
        glUniform3f(loc, x,y,z)     
    def set_mat4(self, uniform_name, mat):
        """we need bind the shader first!"""
        loc = self.get_loc(uniform_name)
        glUniformMatrix4fv(loc,1,GL_FALSE, mat)# True for row major..[1,2,3,4, ,]
        #location count transpose data(nparr)
