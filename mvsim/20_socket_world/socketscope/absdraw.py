from shader import Shader
from texture import Texture
from vao import VAO

from collections import defaultdict
#we have Counter,too.(is but string counter, not for here.) and set. object->set hashable.


#so user shall be know only mat_dict and geodict. fine.

#interface became mostly -dict. great unity!
class Geometry:
    _counter = defaultdict(int)
    """    
    is abstracted interface. if it stack to VAO, fill VAO's requirements!
    """
    _todo = """
    hide concrete vao. only interface! -NO! we all adult.
    """
    def __init__(self, geo_dict):

        #geokeys = set('position', 'indices')
        #assert set(geo_dict.keys()) in geokeys
        assert 'position' in geo_dict
        assert 'indices' in geo_dict
        assert len(geo_dict['position'])//3 == len(geo_dict['indices'])
        
        #copy after assert. save cost!
        #keep input geo_dict not harmed, bot store new self.geo_dict.
        geo_dict = geo_dict.copy()#thats the way!hahaha!finally we did.. it seemed too costy, but it clears the way.

        #iter but just one iter
        position = geo_dict['position']
        indices = geo_dict['indices']
        nokeys = set('position','indices','metadata')
        attr_dict = {key:value for key,value in geo_dict.items() if key not in nokeys}

        #way2
        # metadata = geo_dict.pop('metadata')#pop changes dict..
        # position = geo_dict.pop('position')
        # indices = geo_dict.pop('indices')
        # attr_dict = geo_dict
        
        # geo_dict = {'metadata':metadata,'position':position,'indices':indices}
        # geo_dict.update(attr_dict)




        #those are for vao, we don't want to care too much of it. more abstract!!!!
        # geo_dict(mesh+meta) -> mesh_dict(vert+indices)
        # # mesh_dict -> vao 
        #mesh_dict = geo_dict['mesh_dict']
        #NO MORE MESH_DICT. FOR TOO MANY MESH AND geo_dict is for create dict. thats all. metadata insided.
        #position,indices = mesh_dict['position'], mesh_dict['indices']
        #attr_dict = {key:value for key,value in mesh_dict.items() if (key!='position' or key!='indices') }
        
        # attr_dict = {}
        # for key,value in mesh_dict.items():
        #     if key == 'position':      #also brings error. since position is 'the must'.          
        #         position = value
        #     elif key == 'indices':
        #         indices = value
        #     elif key == 'metadata':
        #         pass
        #     else:
        #         attr_dict[key] = value        
        
        self.vao = VAO(position,indices,attr_dict)
        #self.vao = VAO(geo_dict['mesh_dict'])#so simple...but too simple.
        
        name = geo_dict.get('metadata',{}).get('name', 'Geometry')
        Geometry._counter[name]+=1
        count = Geometry._counter[name]
        self.name = name if count==1 else f"{name}_{count}"
        #those, too.
        # name = geo_dict.get('name', 'Geometry')
        # Geometry._counter[name]+=1
        # count = Geometry._counter[name]
        # self.name = name if count==1 else f"{name}_{count}"
        #self.material = None#this is place for geo! - lets not use this. brother cannot have younger.
        #self.geo_dict = geo_dict.copy()#can be shared.-not.
        self.geo_dict = geo_dict
    
    #for once?? NOt that much!
    # @classmethod
    # def _get_cname(cls,name):
    #     Geometry._counter[name]+=1
    #     count = Geometry._counter[name]
    #     name = name if count==1 else f"{name}_{count}"
    #     return name
        
    def __repr__(self):
        return f"{self.__class__.__name__} {self.name}"
        #return f"{self.__class__.__name__} {self.name}, material:{self.material}"
    
    #def destroy(self):
    # def __del__(self):
    #     self.vao.destroy()#vao is per-geometry. del geo / garbage collected.    
    #     #better not to use vao.__del__ ..? since vao is final object.
    #no, del->del. we don't need it here. actually we want is vao.__del!
    
    def save(self,fdir):
        self.geo_dict.save(fdir)
    #def load(self,fdir):#will replace self.

    def update(self,position=None, attr_dict=None):#so there is oonly a position, user can input what to.
        """update data, set gpus."""
        #attr_dict is narrow input, is dict, excludes indices.fine.
        #course if **kwargs can deal full geo_dict, but we don't update too much.
        #position, kwargs = {attr:value}
        """if want change points, just create new one.
        supports metadata,too.....NO!!! one method, one purpose.
        """
        #overwrite dict(to save), update vao.
        
        #[ i for i in self.geo_dict.keys() if i!='indices' and i!='metadata' and i!='position']
        #https://stackoverflow.com/questions/31433989/return-copy-of-dictionary-excluding-specified-keys
        #invalid = {"keyA", "keyB"}
        
        #exclude = {'position','indices','metadata'}
        #include = {key:value for key,value in self.geo_dict.items() if key not in exclude}
        #attr_dict = {key:value for key,value in kwargs.items() if key in include}
        #attr_dict = {key:value for key,value in kwargs.items() if key not in exclude and key in self.geo_dict}
        
        # for key,value in kwargs.items():
        #     if key in self.geo_dict:
        #         if key !='indices' and key !='metadata':
        #             self.geo_dict[key] = value
        #             attr_dict[key] = value
        #if key!='metadata' and key!='indices':

        # attr_dict.update(kwargs)
        # for key,value in attr_dict.items():
        #     if key in self.geo_dict:#better do this. geo.update(**geo_dict) happens..
        #         self.geo_dict[key] = value

        if position:
            assert len(self.geo_dict['position']) == len(position)
            if not attr_dict:
                self.vao.update_position(position)
                self.geo_dict['position'] = position#after gpu action.
        
        if attr_dict:
            attr_dict = {key:value for key,value in attr_dict.items() if key in self.geo_dict}#fitting first.safe!
            for key,value in attr_dict.items():
                assert len(self.geo_dict[key]) == len(value)#great assertion! since err comes from gpu..(even not error!)
            
            #creating vert_dict for to input of vao.update_vert_dict
            #vert_dict = {key:value for key,value in self.geo_dict.items()}#beautyful code! ..actually copy.
            vert_dict = self.geo_dict.copy()#copy.deepcopy(dict)
            if position:
                vert_dict['position'] = position

            #we can not use vertdict={'pos'=[]}, missing attrs!
            vert_dict.update(attr_dict)
            #attr_dict = {key:value for key,value in attr_dict.items() if key in vert_dict}
            #vert_dict.update(attr_dict)
            # for key,value in attr_dict.items():
            #     if key in vert_dict:
            #         vert_dict[key] = value

            #attr_dict = {key:value for key,value in kwargs.items() if key not in exclude and key in self.geo_dict}

            #exclude = {'position','indices','metadata'}#don't do this! user is adult, [We are all consenting adults]
            #attr_dict = {key:value for key,value in kwargs.items() if key not in exclude and key in self.geo_dict}
            #vert_dict = {'position':position}#keep innput safe.,, actually..
            #vert_dict.update(attr_dict)
            self.vao.update_vert_dict(vert_dict)#heavy gpu action
            if position:
                self.geo_dict['position'] = position#after gpu action.
            
            #2 lines shorter!
            #attr_dict = {key:value for key,value in attr_dict.items() if key in self.geo_dict}
            #skipped since attr_dict is fitted.
            self.geo_dict.update(attr_dict)           
            
            #3 lines loose
            # for key,value in attr_dict.items():
            #     if key in self.geo_dict:
            #         self.geo_dict[key] = value


    #we dont want to know more -dict..
    # def update(self, vert_dict):
    #     "if want change points, just create new one."
    #     #overwrite dict(to save), update vao.
    #     position = vert_dict.get('position')
    #     attr_dict = {key:value for key,value in vert_dict.items() if key!='position' }

    #     if position:
    #         self.geo_dict['mesh_dict']['position'] = position
    #         if not attr_dict:
    #             self.vao.update_position(position)
        
    #     if attr_dict:
    #         #keep innput safe.
    #         for key,value in attr_dict.items():
    #             self.geo_dict['mesh_dict'][key] = value
    #         vert_dict = {'position':position}
    #         vert_dict.update(attr_dict)
    #         self.vao.update_vert_dict(vert_dict)


    # def update(self,position=None, attr_dict=None):
    #     #overwrite dict(to save), update vao.
    #     if position:
    #         self.geo_dict['mesh_dict']['position'] = position
    #         if not attr_dict:
    #             self.vao.update_position(position)
        
    #     if attr_dict:
    #         #keep innput safe.
    #         for key,value in attr_dict.items():
    #             self.geo_dict['mesh_dict'][key] = value
    #         vert_dict = {'position':position}
    #         vert_dict.update(attr_dict)
    #         self.vao.update_vert_dict(vert_dict)

    # def update_pos(self,position):
    #     #overwrite dict(to save), update vao.
    #     self.geo_dict['position'] = position
    #     self.vao.update_position(position)
    # def update_vert(self,vert_dict):
    #     #keep innput safe.
    #     for key,value in vert_dict.items():
    #         self.geo_dict['mesh_dict'][key] = value        
    #     self.vao.update_vert_dict(vert_dict)
    #def update(self,position=None, attr_dict=None): #was actually, but we forgot the intension

    #def draw(self, vpmat, modelmat, uni_dict=None, skeletal=False):
    #def draw(self, vpmat,modelmat, uni_dict=None):
        #self.geometry.draw(vpmat, modelmat, uni_dict)# depth rule.-> now we geometry knows mat,vao. real draw ones.

    #well packed. bind-setmat, and not draw?? that not happens!
    def vao_don_need_toknow_such_draw(self, vpmat,modelmat, uni_dict=None):# too many dicts.. but kwargs hard to figure out.
        """uniform_dict = {'color':[0,0,1],'brightness':3.0}"""#we did explaned.
        material = self.material
        material.bind()
        material.set_vpmat(vpmat)
        material.set_modelmat(modelmat)
        #way1: always unidict if uniform atrs.  vs unidict only to target.
        #ue4like, we see, everytime, maybe. or ifchanged check.. cache. that's not bad however,too.
        #create unidict outside of geo??  in absesh?
        #its, if chached, ignore changes. least uniform set rule.
        #since this is the only route.

        if uni_dict:
            material.set_uniform(uni_dict)#ensures for once.
            #for key,value in uni_dict.items():
            #material.set_uniform(key,value)#this is fine here.
        # uniforms
        #we learned before at init..
        # for key,value in uni_dict.items():
        #     if key != 'bone':
        #         material.set_uniform(key,value)
        #     else:
        #         material.set_pose(value)

        # draw
        self.vao.bind()#we finally can see how vao works , here. absmesh---Geo-vao.
        self.vao.draw()

        material = self.material
        material.bind()
        material.set_vpmat(vpmat)
        material.set_modelmat(modelmat)
        if uni_dict:
            material.set_uniform(uni_dict)
    
    # we declare, least info rule. we do minimum!
    """uniform_dict = {'color':[0,0,1],'brightness':3.0}"""#we did explaned.
    def draw(self):# too many dicts.. but kwargs hard to figure out.
        self.vao.bind()#we finally can see how vao works , here. absmesh---Geo-vao.
        self.vao.draw()

    #def draw_instanced(self, vpmat,modelmat, count, uni_dict=None):        
    def draw_instanced(self,count):
        self.vao.bind()#we finally can see how vao works , here. absmesh---Geo-vao.
        self.vao.draw_instanced(count)

    




#mat shader ->instanced changer.  1.float or vec3 -> instanced attr(add AXIS) 2.4x4.

#lets we can see shader's tex channels, so we can intentionally change. not by texture idx(quite encapsulated one)
    
   


#=================

"""vertn,fragn filedir or string.
texture_dict = {'diffuse':'diffuse.png','normal':'normal_ver4.png'}
->vertn,fragn, mat_dict, ->mat_dict,finally.
"""
class Material:
    _counter = defaultdict(int)
    #def __init__(self, mat_dict, name=None):
    def __init__(self, mat_dict):
        """gpu action"""
        # assert - doorguard
        #geokeys = set('position', 'indices')
        #assert set(geo_dict.keys()) in geokeys
        assert 'shader' in mat_dict#we dont do this. too many shaders! ...but actually a Mat, a shader./but whatif same shader..
        #input shader object?? andway we load data. thats the first!wow!!!! Texture(rawdata)-NO however!
        #remember thre format.
        #assert 'texture' in mat_dict

        #input data safe
        mat_dict = mat_dict.copy()
        
        #default shall be here, not inside Shader.(cannot access)
        #sha_dict = mat_dict.get('shader',  {'vertex': vertn,'fragment': fragn}  )#default here?? hmm.
            #for key,value in shader_dict.items():#'vertex','fragment'...
        # for value in shader_dict.values():
        #     vertn,fragn = self._is_shader_path(value,fragn)#all gone!wow.
        #shader = Shader(shader_dict)#Shader(vertn,fragn)#toomanydict..
        sha_dict = mat_dict['shader']
        #shader = Shader(sha_dict)#Shader(vertn,fragn)#toomanydict..
        shader = Shader(**sha_dict)#do we create it everytime??!
        
        #too many dict..
        # valueDict = {}
        # valueDict.update(mat_dict)        
        # texdict = {}
        # if 'texture' in valueDict:
        #     #texture_dict = mat_dict.pop('texture')#this will break origin dict!
        #     texture_dict = valueDict.pop('texture')
        #     for channel,fdir in texture_dict.items():
        #         texdict[channel] = Texture(fdir)
        #if 'texture' in mat_dict:
        #tex_dict = mat_dict.get('texture',  {'diffuse':'default.png'} )#here,too? i think both sha,mat shared default.
        tex_dict = mat_dict['texture']
        textureDict = {}
        for channel,fdir_data in tex_dict.items():#check same data here??hmm.. but not a=b=c.
            textureDict[channel] = Texture(fdir_data)

        #and what is called mat_dict without shader,texture??
        #geo_dict , vert_dict is.
        #uni_dict is {uniform:value}
        #..think uni_dict is answer.
        
        self.shader = shader
        self.textureDict = textureDict#not multiple.#yes multiple
        #self.valueDict = valueDict
        #self.textureDict = tex_dict
        #print(self.valueDict,self.textureDict)

        name = geo_dict.get('metadata',{}).get('name', 'Material')
        Material._counter[name]+=1
        count = Material._counter[name]
        self.name = name if count==1 else f"{name}_{count}"
        #self.mat_dict = mat_dict
        #self.mat_dict = mat_dict.copy()#RAM is free resource! even full texture data.
        self.mat_dict = mat_dict
    
    
    #those are acomplished ,in the end.
    # def update_texture(self, channel, data_fdir ):
    #     1
    # def change_texture(self, channel, data_fdir ):
    #     1
    # def change_shader(self, vertex=None,fragment=None,geometry=None):
    #     1#if compile error OR draw error, rollback. ,,or draw will ?

    #donno what update is. what you wanted?
    #ssermss set properttry,, when draw, actor.attr-> ..no.notaht. it seems really changes data..

    """diffuse:data or color=[1,2,3] or smoothing=3 .."""
    #def update_shader(self, vertex,geometry,fragment=None):
    #def update_shader(self, **kwargs):
    def _update_shader(self, sha_dict):
        #we do not check here! here is sacried interier place.
        #new_sha_dict = self.mat_dict['shader'].copy()#get final form, first!
        #new_sha_dict.update(sha_dict)#since input is not **kwargs, we can do this!

        #vert = sha_dict.get('vertex', self.mat_dict['shader']['vertex'])
        #geo = sha_dict.get('geometry', self.mat_dict['shader']['geometry'])
        #frag = sha_dict.get('fragment', self.mat_dict['shader'].get('fragment', None) )
        #self.shader.update(vert,geo,frag)
        self.shader.update(sha_dict)#like vao.
        #self.mat_dict['shader'].update(sha_dict)#notsafe
    
    #def update_texture(self, **kwargs):
    def _update_texture(self, tex_dict):
        for key,value in tex_dict.items():
            if key in self.textureDict:
                texture = self.textureDict[key]
                texture.update(value)#dose this only with bound shader??? assume not, now.
                #self.mat_dict['texture'][key] = value
    #def update(self, **kwargs):
    #def update(self, uni_dict):
    def update(self, uni_dict=None, tex_dict=None, sha_dict=None):#inversed, huh?
        """update .dict, set default. change gpus for sha,tex."""
        if sha_dict:
            shakey = {'vertex', 'geometry','fragment'}#validation. like assert of geo.
            #sha_dict = {key:value for key,value in sha_dict.items() if key in self.mat_dict['shader']}#clean input first.
            sha_dict = {key:value for key,value in sha_dict.items() if key in shakey}#we need to do thisway, in shader.
            new_sha_dict = self.mat_dict['shader'].copy()#get final form
            new_sha_dict.update(sha_dict)#update!great 3 seq. since dict copy is not that costy..wait! 1D dict acts like deepcopy.
            #but we next write copy, to self.matdict. it's nessesary!
            self._update_shader(new_sha_dict)
            #sha_dict = {key:value for key,value in sha_dict.items() if key in self.mat_dict}#since it's for inside.
            self.mat_dict.update(sha_dict)
        if tex_dict:
            tex_dict = {key:value for key,value in tex_dict.items() if key in self.mat_dict}#clean input first. it's doorguard!
            #assertion...no needed. since it's texture! same wh check?no!
            self._update_texture(tex_dict)
            self.mat_dict.update(tex_dict)
        #those are heavy.gpu actions

        #exclude = {'shader','texture','metadata'}
        #update_dict = {key:value for key,value in kwargs.items() if key not in exclude and key in self.mat_dict}
        #create new one, if no attr in self! this keeps narrow expect.
        if uni_dict:
            uni_dict = {key:value for key,value in uni_dict.items() if key in self.mat_dict}#get hits
            #assertion.
            for key,value in uni_dict.items():
                try:
                    len_same = len(value) == len(self.mat_dict[key])
                except TypeError:#if not [],()..
                    continue
                assert len_same

            #skip gpu action here. we can check if all uniforms are in shader, but don't do too much.. for faster.
            self.mat_dict.update(uni_dict)#too bad but i will sleep now.. -it was good job,sleeper.
        
        # if 'shader' in kwargs:
        #     sha_dict = kwargs['shader']
        #     self.shader.update(**sha_dict)
        # if 'texture' in kwargs:
        #     tex_dict = kwargs['texture']
        #     self.texture.update(**tex_dict)
        
        # if key in self.textureDict:
        #     texture = self.textureDict[key]
        #     texture.update(value)
        # else:
        #     self.valueDict[key] = value#not load and setvec3 actor.color=1,2,3 ,direcly, but thisway.  
        #from help of:
        #mat.texture[0].update(data)
        #mat.color.update(value)
        #mat.update('texture',0,value)
        #mat.update('diffuse',value)
        #mat.update('color',value)
    
    def bind(self):#need values to int,float kinds..?
        self.shader.bind()

    def set_vpmat(self, vpmat):
        self.shader.set_mat4('ViewProjection', vpmat)
    def set_modelmat(self, modelmat):
        self.shader.set_mat4('Model', modelmat)
    
    def set_pose(self, pose):
        #uniform mat4 Bone;
        #vec4 vert_Position = Bone * vec4(pos,1);
        bonemat = [1,0,0,0, 0,0.51,0,0, 0,0,1,0, 0,0,0,1]
        self.set_mat4('bone',bonemat)
    
    def set_vec3(self, name, vec3):
        self.shader.set_vec3(name, vec3)
    def set_mat4(self, name, mat4):
        self.shader.set_mat4(name, mat4)
    
    def set_vec4(self, name, vec4):
        self.shader.set_vec4(name, vec4)
    def set_ivec4(self, name, ivec4):
        self.shader.set_ivec4(name, ivec4)

    #we sep. add_uniform and set_! it makes both easyly!
    def set_uniform(self, uni_dict):#if bone, youknow whattodo?
        #color=[1,2,3] / colors=[ [1,2,3],[3,2,1] ] #check 2D?..thats good.yeah.
        uni_dict = {key,value for key,value in uni_dict.items() if key in self.mat_dict}

        for key,value in uni_dict.items():
            #.. many lines. you know what to..NO. do here. -to give them all shader, extreamly bad!
            
            #= self.get_type(key)
            #vertn finally has info of var.
            #material.uni_dict
            #material.shader.uni_dict
            #material.shader.get_uni_dict()
            {
                'vec3':self.set_vec3
            }
            {
             :'vec3',
             :'int8',
             :'ins8[]'
            }

            #mateirla.shader = shader#too pythonic. not do thisway.
            #material.update('vertex',vertn)#this assumes storing sha_dict.!
            #so, mat stores sha_dict. and change it even to var-> var[].
            #..ithink but actuall data shall be stored in shader. since it's final one.

            def set_uniform(self, dtype, value):#tooabs. not for shader.
                if dtype == 'vec3':
                    self.set_vec3(value)

            try:
                lenval = len(value)
                if lenval == 1:

                if key == 'bone':
                    self.set_pose(value)
                #if len(value)==3:#
                if isinstance(value,list)
                    self.shader.set_vec3(key, value)
            except:
                if value == None:#getattr?
                    continue
                if isinstance(value, float):
                    self.shader.set_float(key, value)
                    continue
                elif isinstance(value, int):
                    self.shader.set_int(key, value)
                    continue            

            #shader.findtype('color')
            #https://stackoverflow.com/questions/4724243/how-to-get-the-data-type-of-an-uniform-variable
            #glGetActiveUniformARB
            #glGetProgram(GL_ACTIVE_UNIFORMS)
            #we cant, since if anyway final value is value.
            #self.speed = 0 (how can we decide it's float or int?!)

        # for texture in self.textureDict.values():
        #     texture.bind()

    

#=================history

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
#type 3! meshdict is for only data,  geometry needs name, so geodict['name'].
#trype3
geo_dict = {
    'mesh_dict':{'pos':[],'ind':[],'uv':[],'bone':[]},#real mesh data. 
    'name':'ham'#metadata
}



class Countess:
    "is for indexed id. ......57! ,and delete3, 3 again!"
    _count = 0
    @classmethod
    def _namefit(cls,name):
        clsname = cls.__name__
        cls._count+=1
        if not name:
            name = f"{clsname}_{cls._count}"
        return name


#this is bad: while name / Geo itself holds dict,bad. outer class required to do this.
class Duchess:
    _namedict = {}
    @classmethod
    def get(cls,name):
        return cls._namedict.get(cls.__name__,{}).get(name)
        #return cls._namedict[cls.__name__][name]
    
    def _add(self):
        cls = self.__class__
        name = self.name
        while name in cls._namedict:#this uses for, if 10000 objects, too badthing happens. what bringed countess.
            name = cls.__get_numname(name)
        self.name = name
        
        #no more do this. try except tells exactly what should we do.
        if not cls.__name__ in cls._namedict:
            cls._namedict[cls.__name__] = {}        
        cls._namedict[cls.__name__][self.name] = self    
        
        # try:
        #     clsdict = cls._namedict[cls.__name__]
        # except KeyError:
        #     cls._namedict[cls.__name__] = {}
        #     clsdict = cls._namedict[cls.__name__]
        
        # try:
        #     clsdict = cls._namedict[cls.__name__]
        # except KeyError:
        #     cls._namedict[cls.__name__] = {}
        # finally:
        #     clsdict = cls._namedict[cls.__name__]#why we do, if we did?

        # defaultdict(list)#thats the winner!
    
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




#self._add()# get(name), .name is unique. -> get is not here. rather assetmanager.yeah. /name is.. countess.

#geo = Geometry(geo_dict)
#def __call__(self, arg):
#geo(arg)


def babydraw(self, vpmat, modelmat):#we do here,finally. haha! even shared geo, can draw each actor.# no actor again.
        "instanced, uniform set if by draw_seq. absmesh binds, not here ,,,huh,here again. why? uniformset becam dict."
        mat = self.mat
        mat.bind()
        mat.set_vpmat(vpmat)
        mat.set_modelmat( actor.get_modelmat() )
        if mat.skeletal:
            1
        if geo.skeletal:
            mat.set_pose(actor.pose)#since pose is just attr of actor concept.
        self.vao.bind()
        self.vao.draw()
    #def get_instance_dict(self):see absmesh.
    #for draw, it's better.
    def draw_pose(self, vpmat,modelmat,pose, uniform_dict=None):#finally. we don't need annoying skeletal kwarg.
        mat.set_pose(pose)#since pose is just attr of actor(actor.pose) concept. ->more decoupled~!
    #def draw_pose_instanced(self, vpmat,modelmat,pose, uniform_array_dict=None):#doweneedit?? ..maybe?











def _assume():
    #we want know dict types as minimum.
    #which shall be : geo_dict / mat_dict
    #every is internal usage.
    geo_dict = {'position':[],'indices':[],}
    #geo_dict = {'position':[],'indices':[], 'name':'ham','file':'ff.fx'}
    geo_dict = {'position':[],'indices':[], 'metadata':{'name':'ham','file':'ff.fx'} }#so there be no mesh_dict.
    Geometry(geo_dict)
    #VAO(vao_dict)
    #geo.update({'position':position})
    geo.update(position)
    geo.update(normal = [],uv=[])#kwargs
    geo.update({'normal':[],'uv':[]})#dict
    geo.update(attr_dict)

    #uni_dict
    mat_dict = {'shader':{},'texture':{}, }
    mat_dict = {'shader':{},'texture':{}, 'metadata':{'name':'ham','file':'ff.fx'}, }
    Material(mat_dict)
    #Shader(sha_dict)
    #Texture(tex_dict)
    mat.update_texture(diffuse = 'data.png')
    mat.update_texture({'diffuse':'data.png'})
    mat.update_shader(vertex = 'ham.vs')#confirm.
    #mat.update('shader',)
    #mat.update('texture',)
    #shader.update(sha_dict)
    #texture.update(fdir_rawdata)