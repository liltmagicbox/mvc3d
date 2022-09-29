






class Countess:
    _counter = 0
    @classmethod
    def _namefit(cls,name):
        clsname = cls.__name__
        cls._counter+=1
        if not name:
            name = f"{clsname}_{cls._counter}"
        return name

import os

from shader import Shader
from texture import Texture
class Material(Countess):
    """vertn,fragn filedir or string.
    texture_dict = {'diffuse':'diffuse.png','normal':'normal_ver4.png'}
    """
    def __init__(self, vertn,fragn, texture_dict, name=None):
        vertn,fragn = self._is_shader_path(vertn,fragn)
        shader = Shader(vertn,fragn)

        texdict = {}
        for channel,fdir in texture_dict.items():
            texdict[channel] = Texture(fdir)
        
        self.shader = shader
        self.textureDict = texdict
        self.name = self._namefit(name)

    def bind(self):
        self.shader.bind()
        for texture in self.textureDict.values():
            texture.bind()
    def set_vpmat(self, vpmat):
        self.shader.set_mat4('ViewProjection', vpmat)
    def set_modelmat(self, modelmat):
        self.shader.set_mat4('Model', modelmat)

    #===
    @staticmethod
    def _is_shader_path(vertn,fragn):
        if os.path.exists(vertn):
            with open(vertn, 'r', encoding='utf-8') as f:
                vertn = f.read()
        if os.path.exists(fragn):
            with open(fragn, 'r', encoding='utf-8') as f:
                fragn = f.read()    
        return vertn,fragn

from vao import VAO
class Geometry(Countess):
    def __init__(self, attr_dict, indices, name=None):
        vao = VAO(attr_dict, indices)
        self.vao = vao
        self.name = self._namefit(name)
    def bind(self):
        self.vao.bind()
    def draw(self):
        self.vao.draw()

class Mesh(Countess):
    def __init__(self, geo,mat, name=None):
        self.geo = geo
        self.mat = mat
        self.name = self._namefit(name)


#=====================================

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

class AssetManager:
    def __init__(self):
        self.geoDict = {}
        self.matDict = {}
        self.meshDict = {}
        #==========add defaults
        #vertn,fragn = 'vert.txt','frag.txt'
        texdict = {'diffuse':'frz.png'}
        mat = Material(vertn,fragn, texdict, name='default')
        #self.add_mat(mat)
        
        vao_attrs={    'position' : [ 0,0,0, 1,0,0, 1,1,0, 0,1,0,],
                        'uv' : [ 0,0,  1,0,  1,1,  0,1 ],    }
        vao_indices = [0,1,2,0,2,3,]
        geo = Geometry(vao_attrs,vao_indices, name='default')
        #self.add_geo(geo)
        
        mesh = Mesh(geo,mat, name='default')
        self.add_mesh(mesh)

    def get_geo(self, name):
        return self.geoDict.get(name, self.geoDict['default'] )
    def get_mat(self, name):
        return self.matDict.get(name, self.matDict['default'] )
    def get_mesh(self, name):
        return self.meshDict.get(name, self.meshDict['default'] )
    
    def add_geo(self, asset):
        self.geoDict[asset.name] = asset
    def add_mat(self, asset):
        self.matDict[asset.name] = asset
    def add_mesh(self, asset):
        """adds mesh.geo ,mesh.mat"""
        self.meshDict[asset.name] = asset
        self.add_geo(asset.geo)
        self.add_mat(asset.mat)


    #===============
    def load(self, fdir):
        1

def asset_load(directory):
    for file in os.listdir(directory):
        3

# # gltf, obj, tttp.
# -box
#  -box.obj
#  -box.mtl
#  -box_diffuse.png#orwhatever
# #tttf is..
# -box
#  -box_attr.txt -json style dict.
#  -box_vert.txt
#  -box_frag.txt
#  -box_diffuse.png
# box_ is ignored. optional. path rules first.




    # ue4, we have assets, and actors. we need both.
    # js, we have somewhere loaded mat,geo. and Mesh. and Mesh is actor, created.
    #js store geo,mat. -> Mesh(Actor)
    #ue4 geo,mat,Mesh(Actor) -> Mesh_created.
    #objloader -> object
    
    #object.copy
    #getObjectByName getObjectById
    #1.load a model = object = StaticMeshActor
    #2.copy-clone-instance to the world.
    #3. change mat or copy ->mat2, change and assign.