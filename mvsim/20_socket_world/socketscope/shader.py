import os
from OpenGL.GL import *
from OpenGL.GL import shaders

class Shader:
    def __init__(self, shader_dict):
        shas = []
        for key,value in shader_dict.items():
            value = self._is_shader_path(value)
            if key == 'vertex':glsha = GL_VERTEX_SHADER
            elif key == 'fragment':glsha = GL_FRAGMENT_SHADER                
            elif key == 'geometry':glsha = GL_GEOMETRY_SHADER                
            sha = shaders.compileShader( value, glsha)
            shas.append(sha)

        program = shaders.compileProgram(*shas)#ORDER SAFE.
        [ glDeleteShader(sha) for sha in shas]
        #https://pyopengl.sourceforge.net/documentation/pydoc/OpenGL.GL.shaders.html
        #ShaderProgram()#maybe it's the default??
        self.ID = program
        self._loc_cache = {}

    @staticmethod
    def _is_shader_path(vertn):
        if os.path.exists(vertn):
            with open(vertn, 'r', encoding='utf-8') as f:
                vertn = f.read()  
        return vertn

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



# def __init__(self, vert,frag,geo=None):#vertstr, fragstr->shader_dict!        
#     assert bool(glCreateShader)#sometimes compile error occurs, before window()
#     vsha = shaders.compileShader( vert, GL_VERTEX_SHADER)
#     fsha = shaders.compileShader( frag, GL_FRAGMENT_SHADER)        
#     if geo:
#         gsha = shaders.compileShader( geo, GL_GEOMETRY_SHADER) if geo else None
#         program = shaders.compileProgram(vsha,fsha, gsha)#ORDER SAFE.
#         glDeleteShader(gsha)
#     else:
#         program = shaders.compileProgram(vsha,fsha)#ORDER SAFE.
#     glDeleteShader(vsha)
#     glDeleteShader(fsha)

