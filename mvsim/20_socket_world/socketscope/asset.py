from objman import get_mesh_dicts, get_material_dict

def main():
    from window import Window
    w = Window()
    AssetManager().load_obj('yup/objobjects.obj')    
    #AssetManager().load_obj('warhawk/s-13_warhawk.obj')
    #w.run()

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
    def x__init__(self, vertn,fragn, texture_dict, name=None):
        vertn,fragn = self._is_shader_path(vertn,fragn)
        shader = Shader(vertn,fragn)

        texdict = {}
        for channel,fdir in texture_dict.items():
            texdict[channel] = Texture(fdir)
        
        self.shader = shader
        self.textureDict = texdict
        self.name = self._namefit(name)
    def __init__(self, vertn,fragn, mat_dict, name=None):
        vertn,fragn = self._is_shader_path(vertn,fragn)
        shader = Shader(vertn,fragn)
        
        texdict = {}
        if 'texture' in mat_dict:
            texture_dict = mat_dict.pop('texture')
            for channel,fdir in texture_dict.items():
                texdict[channel] = Texture(fdir)

        valueDict = {}
        valueDict.update(mat_dict)
        
        self.shader = shader
        self.valueDict = valueDict
        self.textureDict = texdict
        #print(self.valueDict,self.textureDict)
        self.name = self._namefit(name)

    def bind(self):#need values to int,float kinds..?
        self.shader.bind()
        for key,value in self.valueDict.items():
            # if value == None:
            #     continue
            if isinstance(value, float):
                self.shader.set_float(key, value)
                continue
            elif isinstance(value, int):
                self.shader.set_int(key, value)
                continue            
            if len(value)==3:                
                self.shader.set_vec3(key, *value)
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
    gl_Position = ViewProjection * Model * vec4(pos,1);
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
    FragColor = texture2D(tex0, uv_out);
}
"""


vertn_mtl_notex = """
#version 410 core
layout (location = 0) in vec3 pos;
layout (location = 1) in vec2 uv;
out vec2 uv_out;
out vec3 diffuse_color;

uniform mat4 Model;
uniform mat4 ViewProjection;

uniform vec3 Kd;//uint
//uniform float Kd;//uint

void main() 
{
    //gl_Position = vec4( pos, 1);
    gl_Position = ViewProjection * Model * vec4(pos,1);
    uv_out = uv;
    diffuse_color = Kd;
}
"""

fragn_mtl_notex = """
#version 410 core

in vec2 uv_out;
in vec3 diffuse_color;
out vec4 FragColor;

uniform sampler2D tex0;
uniform sampler2D tex1;

void main()
{   
    FragColor = vec4(diffuse_color,1);
    //FragColor = texture2D(tex0, uv_out);
}
"""

def _get_numname(name):
    ddd = name.rfind('_')
    if ddd == -1:
        return name+'_1'
    namesplit = name[:ddd]
    isnum = name[ddd+1:]
    if not isnum.isnumeric():
        return name+'_1'    
    return namesplit + str(int(isnum)+1)

class AssetManager:
    def __init__(self):
        self.meshDict = {}
        #self.drawmeshDict = {}
        #==========add defaults
        #vertn,fragn = 'vert.txt','frag.txt'
        texdict = {'diffuse':'frz.png'}
        mat_dict = {'texture': texdict }
        mat = Material(vertn,fragn, mat_dict, name='default')
        #self.add_mat(mat)

        vao_attrs={    'position' : [ 0,0,0, 1,0,0, 1,1,0, 0,1,0,],
                        'uv' : [ 0,0,  1,0,  1,1,  0,1 ],    }
        vao_indices = [0,1,2,0,2,3,]
        geo = Geometry(vao_attrs,vao_indices, name='default')
        #self.add_geo(geo)
        
        mesh = Mesh(geo,mat, name='default')        
        self.add_mesh(mesh)
        #self.add_drawmesh('default', [mesh])

    def names(self):
        return list(self.meshDict.keys())
    def get_mesh(self, name):
        return self.meshDict.get(name, self.meshDict['default'] )
    def add_mesh(self,mesh):
        self.meshDict[mesh.name] = mesh
    
    # def get_drawmesh(self, name):
    #     return self.drawmeshDict.get(name, self.drawmeshDict['default'] )
    # def add_drawmesh(self, drawname, meshes):
    #     """adds mesh.geo ,mesh.mat"""        
    #     self.drawmeshDict[drawname] = meshes
    #===============
    def load_obj(self, fdir):
        meshes_for_actor = {}
        
        mesh_dicts = get_mesh_dicts(fdir)#and mtl parsed data??
        for mesh_dict in mesh_dicts:#this will break hat and body..            
            fdir_obj = mesh_dict['obj']
            name = mesh_dict.get('name', os.path.splitext( os.path.split(fdir)[1] )[0] )
            meshes_for_actor[name] = []

            fdir_mtl = mesh_dict['mtl']
            material_dict = get_material_dict(fdir_mtl)
            #===name shall be 1. Mesh is draw object, not actor.            
            
            #print(mesh.keys())dict_keys(['obj', 'mtl', 'name', 'meshes'])
            #name rule: 1.each internal 2.out_internal 3.out_N ..lets 2. internal name is! filename can be changed!

            #print(mesh_dict['meshes'][0].keys())#(['material', 'smoothing', 'vert_dict', 'indices'])            
            for mdict in mesh_dict['meshes']:
                vert_dict = mdict['vert_dict']
                indices = mdict['indices']
                geo = Geometry(vert_dict,indices)

                #===mat
                material = mdict['material']
                smoothing = mdict.get('smoothing')              
                mat_dict = material_dict.get(material, {'diffuse':'default.png'} )
                if smoothing:
                    mat_dict.update( {'smoothing':smoothing} )

                if not 'texture' in mat_dict:
                    #mat_dict['texture'] = {'diffuse':'default.png'}
                    vvv, fff = vertn_mtl_notex, fragn_mtl_notex
                else:
                    vvv, fff = vertn, fragn
                mat = Material(vvv, fff, mat_dict)
            
                #only mesh survives,from now. geo,mat is bound. both devliers abstract interface.
                mesh = Mesh(geo,mat, name=name)
                mesh.fdir = fdir_obj

                while mesh.name in self.meshDict:
                    mesh.name = _get_numname(mesh.name)
                self.add_mesh(mesh)
                #meshes_for_actor[name].append(mesh)
            #self.add_drawmesh(name, meshes_for_actor[name])
        return list(meshes_for_actor.keys())
        
        # gltf wins all. not do too much! since gltf can screen-capture. obj lost vertex origin,rot axis!
        #lets obj just single loader, spread by origin.
        # structure = {
        #     'Cube': [(geo,mat),(geo2,mat2)] ,
        #     'isopod':[geo3,mat3],
        # }
#meshactor=object -mesh(geo,mat).fine.! same structure blender.





if __name__ == '__main__':
    main()






from objloadtest import ma

def xxasset_load(directory):
    for file in os.listdir(directory):
        3



class xxxgeomatAssetManager:
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

    def names(self):
        return list(self.meshDict.keys())
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