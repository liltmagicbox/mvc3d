from shader import Shader
from texture import Texture
from vao import VAO



class Countess:
    "is for indexed id. ......57!"
    _count = 0
    @classmethod
    def _namefit(cls,name):
        clsname = cls.__name__
        cls._count+=1
        if not name:
            name = f"{clsname}_{cls._count}"
        return name

#=======was first three.js style : Mesh(Geometry(),Material())
#but chagned to ue style. StaticMesh( Geometry() )  geo.mat = Material()

#type 1
mesh_dict = {
    'indices': [],
    'position':[],
    'normal':[],
}

#type 2
vert_dict = {
    'position':[],
    'normal':[],
}
mesh_dict = {
    'name':'type2mesh',
    'indices': [],
    'vert_dict' : vert_dict
}
#type 2! we need info, metadata , while parsing vert_dict!
#it's not just dict, since we declare the format, save/load file. it's a file format!
#since it's file, lets not harm mesh_dict. which can be shared, stored.



class Duchess:
    _namedict = {}
    @classmethod
    def get(cls,name):
        return cls._namedict.get(cls.__name__,{}).get(name)
        #return cls._namedict[cls.__name__][name]
    
    def _add(self):
        cls = self.__class__
        name = self.name
        while name in cls._namedict:
            name = cls.__get_numname(name)
        self.name = name
        if not cls.__name__ in cls._namedict:
            cls._namedict[cls.__name__] = {}
        cls._namedict[cls.__name__][self.name] = self    
    
    def _destroy(self):
        cls = self.__class__
        if self.name in cls._namedict[cls.__name__]:
            cls._namedict[cls.__name__].pop(self.name)

    @staticmethod
    def __get_numname(name):
        ddd = name.rfind('_')
        if ddd == -1:
            return name+'_1'
        namesplit = name[:ddd]
        isnum = name[ddd+1:]
        if not isnum.isnumeric():
            return name+'_1'    
        return namesplit + str(int(isnum)+1)

def _nametest():
    class Dum(Duchess):
        def __init__(self,name):
            self.name = name
            #print(self._add)#<bound method Duchess._add of <__main__.Dum object at 0x00000297DD5997C0>>
            #print(Dum._add)#<function Duchess._add at 0x000001B07F544C10>
            #print(Dum._namedict == Duchess._namedict)
            self._add()
    class Dummer(Duchess):
        def __init__(self,name):
            self.name = name
            self._add()

    
    a = Dum('dum1')
    b = Dum.get('dum1')
    print(a)
    print(b)
    
    a = Dummer.get('notexist')
    print(a)
    a = Dummer('new')
    a = Dummer.get('new')
    print(a)
    print(a._namedict)
    a._destroy()
    print(Dummer._namedict)
    print(a._namedict)
    
#_nametest()

class Geometry(Duchess):
    """is abstracted interface. if it stack to VAO, fill VAO's requirements!"""
    def __init__(self, geo_dict, material = None):
        # parse geo_dict(general) -> data for VAO.
        mesh_dict = geo_dict['mesh_dict']
        pos,ind = mesh_dict['position'],mesh_dict['indices']
        attr_dict = {key:value for key,value in mesh_dict.items() if (key!='position' or key!='indices') }
        #since attr_dict = {key.. is used here, only!

        self.geo_dict = geo_dict#thats the first! geo_dict can be shared.
        self.name = geo_dict.get('name', 'Geometry')
        self.vao = VAO(pos,ind,attr_dict)
        self.material = material
        #self.instanced = False#haha!
        self._add()
    def __repr__(self):
        return f"{self.__class__.__name__} {self.name}"
    
    @material.setter
    def material(self,material):
        if material.pose:#donno how to.
            if 'weight' in self.mesh_dict:
                self.material = material
            else:
                raise ValueError('skam material requires weight of vert_dict')
    
    def destroy(self):
        self.vao.destroy()
        self._destroy()
    
    def save(self,fdir):
        self.geo_dict.save(fdir)

    def babydraw(self, vpmat, modelmat):#we do here,finally. haha! even shared geo, can draw each actor.# no actor again.
        "instanced, uniform set if by draw_seq. absmesh binds, not here ,,,huh,here again. why? uniformset becam dict."
        mat = self.mat
        mat.bind()
        mat.set_vpmat(vpmat)
        mat.set_modelmat( actor.get_modelmat() )
        if mat.skeletal:            
        if geo.skeletal:
            mat.set_pose(actor.pose)#since pose is just attr of actor concept.
        self.vao.bind()
        self.vao.draw()
    
    #def draw(self, vpmat, modelmat, uniform_dict=None, skeletal=False):
    def draw(self, vpmat,modelmat, uniform_dict=None):
        #self.geometry.draw(vpmat, modelmat, uniform_dict)# depth rule.-> now we geometry knows mat,vao. real draw ones.
        mat = self.mat
        mat.bind()
        mat.set_vpmat(vpmat)
        mat.set_modelmat(modelmat)
        # uniforms
        uniform_dict
        # draw
        self.vao.bind()#we finally can see how vao works , here. absmesh---Geo-vao.
        self.vao.draw()

    def draw_instanced(self, vpmat,modelmat, uniform_array_dict=None):
        1
    #def get_instance_dict(self):see absmesh.
    def draw_pose(self, vpmat,modelmat,pose, uniform_dict=None):#finally. we don't need annoying skeletal kwarg.
        mat = self.mat
        mat.bind()
        mat.set_vpmat(vpmat)
        mat.set_modelmat( modelmat )
        
        mat.set_pose(pose)#since pose is just attr of actor(actor.pose) concept. ->more decoupled~!
        
        self.vao.bind()
        self.vao.draw()

    def draw_pose_instanced(self, vpmat,modelmat,pose, uniform_array_dict=None):#doweneedit?? ..maybe?
        1




#mat shader ->instanced changer.  1.float or vec3 -> instanced attr(add AXIS) 2.4x4.

#lets we can see shader's tex channels, so we can intentionally change. not by texture idx(quite encapsulated one)
class Material:
    def set_pose(self, pose):
        #uniform mat4 Bone;
        #vec4 vert_Position = Bone * vec4(pos,1);
        bonemat = [1,0,0,0, 0,0.51,0,0, 0,0,1,0, 0,0,0,1]
        #mat.set_mat4('Bone',bonemat)

    def update_texture(self, channel, data_fdir ):
        1
    def change_texture(self, channel, data_fdir ):
        1
    def change_shader(self, vertex=None,fragment=None,geometry=None):
        1#if compile error OR draw error, rollback. ,,or draw will ?


#=================

"""vertn,fragn filedir or string.
texture_dict = {'diffuse':'diffuse.png','normal':'normal_ver4.png'}
->vertn,fragn, mat_dict, ->mat_dict,finally.
"""
class Material(Countess):
    def __init__(self, mat_dict, name=None):
        #default shall be here, not inside Shader.(cannot access)
        shader_dict = mat_dict.get('shader',  {'vertex': vertn,'fragment': fragn}  )
            #for key,value in shader_dict.items():#'vertex','fragment'...
        # for value in shader_dict.values():
        #     vertn,fragn = self._is_shader_path(value,fragn)#all gone!wow.
        shader = Shader(shader_dict)#Shader(vertn,fragn)
        
        valueDict = {}
        valueDict.update(mat_dict)
        
        texdict = {}
        if 'texture' in valueDict:
            #texture_dict = mat_dict.pop('texture')#this will break origin dict!
            texture_dict = valueDict.pop('texture')
            for channel,fdir in texture_dict.items():
                texdict[channel] = Texture(fdir)

        
        self.shader = shader
        self.valueDict = valueDict
        self.textureDict = texdict
        #print(self.valueDict,self.textureDict)
        self.name = self._namefit(name)
    def update(self, key, value):
        """diffuse:data or color=[1,2,3] or smoothing=3 .."""
        if key in self.textureDict:
            texture = self.textureDict[key]
            texture.update(value)
        else:
            self.valueDict[key] = value#not load and setvec3 actor.color=1,2,3 ,direcly, but thisway.  
        #from help of:
        #mat.texture[0].update(data)
        #mat.color.update(value)
        #mat.update('texture',0,value)
        #mat.update('diffuse',value)
        #mat.update('color',value)
    
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
                self.shader.set_vec3(key, value)
        for texture in self.textureDict.values():
            texture.bind()
    def set_vpmat(self, vpmat):
        self.shader.set_mat4('ViewProjection', vpmat)
    def set_modelmat(self, modelmat):
        self.shader.set_mat4('Model', modelmat)
    
    def set_vec3(self, name, vec3):
        self.shader.set_vec3(name, vec3)
    def set_mat4(self, name, mat4):
        self.shader.set_mat4(name, mat4)
    
