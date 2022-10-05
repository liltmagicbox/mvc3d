import os
from OpenGL.GL import *
from OpenGL.GL import shaders

#from collections import defaultdict
#https://docs.python.org/3/library/collections.html#collections.OrderedDict
#has LRU cache, btw.


class Shader:
    def __init__(self, vertex,geometry, fragment=None):
        shas = []
        # for key,value in sha_dict.items():
        #     value = self._is_shader_path(value)
        #     if key == 'vertex':glsha = GL_VERTEX_SHADER
        #     elif key == 'fragment':glsha = GL_FRAGMENT_SHADER                
        #     elif key == 'geometry':glsha = GL_GEOMETRY_SHADER                
        #     sha = shaders.compileShader( value, glsha)
        #     shas.append(sha)
        
        if not fragment:
            shas = []
        else:
            fragment = self._is_shader_path(fragment)
            shas = [shaders.compileShader( fragment, GL_FRAGMENT_SHADER)]
        
        vertex,geometry = map(self._is_shader_path, [vertex,geometry] )        
        shas.append( shaders.compileShader( vertex, GL_VERTEX_SHADER) )
        shas.append( shaders.compileShader( geometry, GL_GEOMETRY_SHADER) )
        program = shaders.compileProgram(*shas)#ORDER SAFE.
        [ glDeleteShader(sha) for sha in shas]

        #https://pyopengl.sourceforge.net/documentation/pydoc/OpenGL.GL.shaders.html
        #ShaderProgram()#maybe it's the default??
        #self.sha_dict = sha_dict#we can hold RAM, but not VRAM.fine. ..actualy let it be shared.
        #not hold here. its concrete final object!
        self.ID = program
        self._cache = {}
    #def update(self, sha_dict):
    def update(self, vertex,geometry, fragment=None):
        glDeleteProgram(self.ID)
        Shader.__init__(self, vertex,geometry, fragment)

    # def update(self, key,value):
    #     #self.shader_dict[key] = value#..it will change that all.
    #     self._destroy_program(self.ID)
    #     newdict = {}
    #     newdict.update(self.shader_dict)
    #     newdict[key] = value
    #     self.__init__(self)
        #self.shader_dict = newdict
        
        #this will be destroy, while ID is required.. huh..
        #newObj = Shader(newdict)
        #self.__dict__.update(newObj.__dict__)#this keeps id(self), atleast..
    
    def __del__(self):#NO!! this requires somewhat gpu action, even it's not in draw loop! occured by gc. ..whynot?
        glDeleteProgram(self.ID)
        #https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDeleteProgram.xhtml
    
    @staticmethod
    def _is_shader_path(vertn):
        if os.path.exists(vertn):#tested, 100times/seconds will take 1ms.
            with open(vertn, 'r', encoding='utf-8') as f:
                vertn = f.read()  
        return vertn

    def bind(self):
        glUseProgram(self.ID)        
    def unbind(self):
        glUseProgram(0)

    def point_size(self,size):
        glPointSize(size)

    def _get_loc(self, uniform_name):
        if uniform_name in self._cache:
            return self._cache[uniform_name]
        program = self.ID
        loc = glGetUniformLocation(program, uniform_name)
        self._cache[uniform_name] = loc
        return loc

    def set_int(self, uniform_name, value):
        """we need bind the shader first!"""
        loc = self._get_loc(uniform_name)
        glUniform1i(loc,value)
    def set_float(self, uniform_name, value):
        loc = self._get_loc(uniform_name)
        glUniform1f(loc,value)
    
    def set_vec2(self, uniform_name, value):#ivec2 uvec2 ,glUniform2fv ?? +v is not x,y,z but vec3.
        loc = self._get_loc(uniform_name)
        glUniform2fv(loc, value)
    def set_vec3(self, uniform_name, value):
        loc = self._get_loc(uniform_name)
        glUniform3fv(loc, value)

    def set_vec4(self, uniform_name, value):
        loc = self._get_loc(uniform_name)
        glUniform4fv(loc, value)
    def set_ivec4(self, uniform_name, value):
        loc = self._get_loc(uniform_name)
        glUniform4iv(loc, value)

    def set_mat4(self, uniform_name, mat):
        "mat = mats if for instanced uniform mat4 Model[250];"
        loc = self._get_loc(uniform_name)
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

#update tese
# def main():
#     s=Shader({})
#     s.update('vert','')
#     a=Shader({})
#     print('===')
# if __name__ == '__main__':
#     main()
#boom! 1738041671632
#===
#boom! 1738041671536#gc



def _class_update_test():    
    class Boom:
        COUNT = 0
        def __init__(self):
            Boom.COUNT+=1
            self.count = Boom.COUNT        
            print('init',self.count,id(self))
        def __del__(self):
            print(self.count,'boom',id(self))
        def update(self):
            Boom.__init__(self)

    a = Boom()
    b = Boom()
    b.update()
    del a
    del b
    print('===')
#_class_update_test()
# init 1 2801033188400
# init 2 2801069577072
# init 3 2801069577072
# 1 boom 2801033188400
# 3 boom 2801069577072
