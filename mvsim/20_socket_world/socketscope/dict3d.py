import json
from collections import UserDict, UserList

class JsonDict(UserDict):
    args = []
    @classmethod
    def _validate(cls, kwargs):
        for key in cls.args:
            if not key in kwargs:
                raise ValueError(f"{cls.__name__} requires .need_args={cls.args}")
    
    def __init__(self, **kwargs):
        self._validate(kwargs)
        super().__init__()
        self.update(kwargs)
    def __repr__(self):
        jstr = json.dumps( self.data )#, indent=4
        return "],\n".join( jstr.split('], ') )    
    def save(self, fdir):
        with open(fdir, 'w', encoding='utf-8') as f:
            f.write( str(self) )#love it!
    @classmethod
    def load(cls, fdir):
        with open(fdir, 'r', encoding='utf-8') as f:
            jstr = f.read()
        data = json.loads( jstr )
        return cls(**data)


class MeshDict(JsonDict):
    args = ['indices','position']
    """ cls(indices=[],position=[],normal=[],,,)
    """

def mdtest():
    a = MeshDict(indices=[],position=[], normal=[12,3])
    #print( a )
    a.save('toto.txt')
    a.load('toto.txt')

class MatDict(JsonDict):
    args = ['shader']#shader default, if not. shader needs stable, not broken one!
    #we did again, since it's also the save form.


class AnimDict(JsonDict):
    """anim changes target's value. ..i've seen it before.. """
#[[]].. data should be protected. ..read only? animdict[0]=[1,2] will change all.
anim_dict = {
    0: 0.1,
    1: 0.11,
    2: 0.12,
}
anim_dict = {
    0: [11,22],
    1: [33,44],
    2: [55,66],
}

skanim_dict = {
    0:{'pos':[1,2,3], 'rot':[1,2,3],},
}

#data 0,1,2
#data 0, ,,60
#data 0, 60,   ,i/o slope, weight.
#we aim gpu ready form, lets parse!
#where fps would be?

#we cannot m,, will not protect value change. since this is py.
# class DD(UserDict):
#     # def __getitem__(self,idx):
#     #    1
#     # def __getattr__(self,key,value):
#     #     print(key)
#     def __setattr__(self,key,value):
#         print(key)
#         if key == 0:
#             print('ya')
#             1
#         else:
#             super().__setattr__(key,value)
# a =DD()
# a.update( {0:[1,2,3],2:22})
# a[0] = 55
# print(a)

#...maybe it was too much if dicts.
attr_dict = {'normal':[],'uv':[] }
vert_dict = {'position':[], 'normal':[],'uv':[] }
mesh_dict = {'indices':[], 'position':[], 'normal':[],'uv':[] }
MeshDict( position = pos, indices = ind, attr_dict = attr_dict) #narrow input rule.
MeshDict( position = pos, indices = ind, attr_dict = attr_dict)

VAO(position, indices, attr_dict = None)

Shader( vert,frag, geo=None )

Texture( fdir, rawdata=None )
Texture( fdir, tex_dict=None )
Texture( fdir_or_rawdata )
Texture( fdir_or_rawdata, flip=False, fastdraw=False)
tex_dict = {    
    'data':fdir_or_rawdata,
    'flip':True,
    'fastdraw':True
}
attr_dict = {    
    'flip':True,
    'fastdraw':True
}



Material( sha_dict=None, tex_dict=None, attr_dict=None )
Material( vert,frag, geo=None, tex_dict=None, attr_dict=None )
Material( shader=None, tex_dict=None, attr_dict=None )
mat_dict = {
    'shader':[],
    'texture':[],
    'color':[1,2,3]
}

#==========================
#==========
#all data-> _dict family.
#dict is jsonio
#lets attr_dict be all. ,,,if needed. shader don't semes needit.
#gpu ready data..aspossible. human-friendly.

#==========
#we don't need to know it! this is for gpu, not abstract.
#Shader
#Texture
#VAO
#=====for , abs
#Mesh(from three.js) -this is sep. draw-mesh. (also actor but ignore now..)
#Geometry
#Material

#==========
#abstract draw
Mesh
SKMesh
#do we attr anim here, additially?
class iMesh:
    def draw():1
#==========
#physical actors
mesh_or_skmesh = iMesh
MeshActor.mesh = mesh_or_skmesh
SKMeshActor.mesh = skmesh#?? we have animator , can be..?
ParticleActor.mesh = mesh_or_skmesh #many people, animframes=[]?
SpriteActor.mesh = mesh_or_skmesh

class Anim:
    'shared data. returns value.'
    def __init__(self, anim_dict):
        self.data = [value for value in anim_dict.values()]
        self.fps = 30#from dict?
        self.loop = True
        self.frames = len(self.data)
        #self.name = 'no'
    def __getitem__(self, idx):
        return self.data[idx]
    @property
    def time(self):
        return self.frames/self.fps
    
    def get(self, time):
        'returns value, always. check before run. we have time.'
        frame = int(self.fps * time)
        if self.loop:
            frame = frame % self.frames#0th is[0], %3 =[0,1,2]
        try:
            return self[frame]
        except:
            print('retunning lastframe')
            return self[-1]

def animtest():
    animtarget = 0
    anim_dict = {0:0, 1:1, 2:2}
    anim = Anim(anim_dict)
    animtarget = anim[2]
    print(animtarget)
    animtarget = anim.get(0.070)#0.0-0.033 0.033-0.066 0.066-0.099
    print(animtarget)
    print(anim.time)



#by frame or by time seconds?
#actor.val = anim[0]
#actor.update = lambda self,dt: self.val = self.anim[0]
#or
#class LedLamp(Actor):
class LedLamp:
    def __init__(self, color=[0,0,0] ):#actor init itself.. no, we need args.
        super().__init__()
        self.t = 0
        self.color = color
        self.state = 1

        self.animDict = {}
    def update(self,dt):
        self.t+=dt
        if self.state ==2:
            self.color[0] = math.cos(self.t)
            self.color[1] = math.cos(self.t+1.57)
            self.color[2] = math.cos(self.t+3.14)
    def _update(self,dt):
        self.t += dt
        self.update(dt)
    def update(self,dt):
        #R,G,B = self.anim[frame]
        self.color = self.anim.get(self.t)#if t exceeds, last frame. great!
        #anim not holds time, actor(player) does. this can shared anim.
    
    def add_anim(self, target,anim):
        self.animDict[target] = anim
    def update(self,dt):
        for target,anim in self.animDict.items():
            value = anim.get(self.t)
            setattr(self,target,value)

def animbytimetest():
    ledblink_anim_dict = {0:[0,0,0], 1:[1,1,0], 2:[2,0,2], 3:[3,3,3],}
    ledblink = Anim(ledblink_anim_dict)
    a = LedLamp()
    a.add_anim('color', ledblink)
    a._update(0.01)
    print(a.color)
    a._update(0.033)
    print(a.color)
    a._update(0.033)
    print(a.color)




#actor has 
skactor.pose = skactor.bone.set(skanim[1])
skactor.pose = skactor.set(skanim[1])
skactor.set(skanim[1])
skactor.set(1)

#====CAUTION   : UPDATE IS NOT DEEPCOPY! keep list 1D.
#xyz = [4,5,6]
# a = { 'd':[[1,2,3],xyz]}
# b.update(a)
# a['d'][1] = 5
# print(a)
# print(b)
# {'d': [[1, 2, 3], 5]}
# {'d': [[1, 2, 3], 5]}



class Bone:
    """Bone is basic structure, fits mesh_dict's weight. """
    def __init__(self, bone_dict):
        bone_dict
        self.data = anim_dict
#bone = Bone()



#vert_dict is without indices, we say.
mesh_dict = {
    'indices': [0,1,2, 0,2,3],#poped.
    'position': [1,2,3, 4,5,6, 1,2,3, 4,5,6],#//3 points
    'custum':[9,9,9, 8,8,8, 8,8,8, 9,9,9],#by target shader's attrb idx 1~
}
mat_dict = {
    'shader':{'vert':'mtl_vert.glsl','frag':'mtl_frag.txt'},
    'texture':{},
    'custum':[1,2,3],
    'custum':3.0,
}
bone_dict2 = {
    'id': [0,1,2],
    'name': ['root','pelvis','spine'],
    'position': [ 0,0,0, 0,0,0, 0,0,0,],#//3 points
}
bone_dict = {
    0:{'id':0,'name':'boneloot', 'pos':[1,2,3], 'rot':[1,2,3], 'normal':[1,2,3] },
}
anim_dict = {
    0:{'pos':[1,2,3], 'rot':[1,2,3],},
}


# mesh_dict
# mat_dict
# skmesh_dict
# bone_dict
# anim_dict
# skanim_dict
# uvanim_dict

#mesh_dict anim_dict only
#vs sk- uv- kinds.
#anim_dict for pos?? actor.attr??

#Mesh(mesh_dict, mat_dict)
#SKMesh(skmesh_dict, mat_dict, bone_dict)
##Anim(anim_dict) #or
#SKAnim(bone_dict,skanim_dict)
#UVAnim(uvanim_dict)#really we need!
#anim_dict = {0:value, 1:value}

vert_dict = {'position':[], 'normal':[]}
mesh_dict = {'position':[], 'normal':[],  'indices':[]}
#geo = Geometry( mesh_dict ) -> VAO(mesh_dict)

#mat = Material( mat_dict) ->  Shader(shader_dict) + Texture(texture_dict)??? -tex requires RGBA kinds? hoply not.
# or both sha tex is attrs, while mesh vao is special one.

# absMesh(mesh_dict, mat_dict)
# absSKMesh(mesh_dict, mat_dict, bone_dict)
# absSKAnim(skanim_dict)#-target is absSKMesh
# absAnim(anim_dict)#-target is , value of ..actor? or abs one? ..or uvanim?

# MeshActor( absMesh )
# SKMeshActor( absSKMesh )
# ParticleActor( *meshes ) #both mesh and skmesh. anyway they have draw, right? 

uvplate = {
    'coords':[]
}
uvanimdict = {
    0:[ 0.0, 1.0],
    1:[ 0.1, 0.9],
}
#we have mat.update('faceuv',coords). do we need uvanim kinds?  maybe just attranim is fine..

#bone anim uses bone origin data. it's difirrent, normal animation. (target->value.)
#shader will get actor's attr, when draw. (not actor->sha but sha~actor. since bind..)
#actor.facialuv = (0,0)? or direct shader.
#...maybe since lod collision, skactor have .bones . (and .bones_origin?) current bone state.
#...yeah. finally we say: anim changes target's value. actor.bone actor.pose(?), actor.facialuv actor.facialpose actor.
#bone pose bone_anim skam  bone_pose..  bone/pose facialbone / facialpose ..fine. since all bones rel.pos of origin..?
#..why don't abs pos? if you got rawdata, it will be all live bone..?abspos? 


#mesh_dict has no header, for human-friendly. while filename became critical.
#lets skmesh subclasses Mesh, so it can used, drawn.
#Mesh SKMesh Bone

#golilla_mesh_dict = load('golliaMesh.txt')
#bone = load('4footanimalbone.txt')
#bone.fit( absMesh(golilla_mesh_dict) )#hope this simmlilar opens new window..? ..or sep.gui.
#bone.save('golillaBone.txt')
#MissilePenguin ..someday, Penguin became Actor,all -Penguin became actor.. massive happens..

#hopefully: pose1 = anim[0] , skmesh.set_pose(pose1) #skmesh.pose is bone-like structure.!
#skmesh.bone = {}
#skmesh.pose = {}
#cat.set_pose(pose1), human.set_pose(pose1)..?
#dont think. do first, and make better. we have not enough exp,know, and ..sense.





#history
#===========================
# class old_notpretty_VertDict(UserDict):
#     """ cls(indices=[],position=[],normal=[],,,)
#     """
#     def __init__(self, **kwargs):
#         if not ('indices' in kwargs and 'position' in kwargs):
#             raise ValueError("VertDict requires indices, position")
#         super().__init__()
#         self.update(kwargs)
#     def __repr__(self):
#         # strs = []
#         # for key,value in self.items():
#         #     strs.append( f"{key}: [{len(value)}], " )
#         # return "vert_dict ={ "+"".join(strs)+"}"
#         return "vert_dict= { self._pretty(jstr) }"
    
#     @staticmethod
#     def _pretty(jstr):
#         return "],\n".join( jstr.split('], ') )#for pretty look.
#     def save(self, fdir):
#         jstr = json.dumps( self.data )#, indent=4
#         jstr = self._pretty(jstr)
#         with open(fdir, 'w', encoding='utf-8') as f:
#             f.write(jstr)
#     @classmethod
#     def load(cls, fdir):
#         with open(fdir, 'r', encoding='utf-8') as f:
#             jstr = f.read()
#         data = json.loads( jstr )
#         return cls(**data)




aa = MeshDict.load('fff')
Geometry(aa)
#?

#==================static to sk. not that good for now..
#MeshDict is just file form, like obj,gltf!
#so as like BoneDict. we need Bone!
class Bone:
    1

for animal in animals:
    animal.fit(bone)
    animal = bone.fit(animal)

#load bone
bone = load('4foot.txt')
#load static mesh (without weight)
meshdict = load('cheeta.txt')
mat = load('cheetamat.txt')#???? YES.cheetamat.
geo = Geometry(meshdict)
#geo.has('weight') == False#more abs!
geo.static == True
geo.skeletal == False

geo = geo.fit(bone)#now geo has weight. fitted. #remember:since shared, we need to get new one!
geo = fitter(geo,bone)#or this external way. like gui.. new window..

#geo.mat = mat# still not skeletal shader. ..hmm..
mat = mat.to_skletal()#like to instanced?
geo.mat = mat
#==================static to sk. not that good for now..

vert_dict
vert_dict + indices = mesh_dict

obj mesh loader -> multi mesh_dict, mat_dict (origin broken) -> stuck MeshActor(geo,geo)
gltf mesh loader -> multi mesh_dict, mat_dict -> seperated MeshActor(geo,geo) (coords broken)
gltf scene loader -> SceneActor (including lights?) (keep coords)

mesh_dict -> Geometry
if mesh_dict has 'weight':
    Geometry.skeletal = True#need better name..

mat_dict -> Material
if mat_dict['shader'] has 'bone':
    Material.skeletal = True#need better name..

mat = mat.to_instanced('attr1','attr2') -> shader changes 4x4, attrs.
mat = mat.to_skeletal() ->shader adds bone

geo.mat = mat#check if geo.skeletal, mat has skeletal.? (1:create mat 2:only accepts mat.skeletal if geo.skeletal.)

#for, keep this. and draw.
instanced_Dict = {
'imatname': {   'idx': [0,1,2,3],
    'color':[[255,0,0], [0,0,255],],
    }
}

#http://www.cgdev.net/json/index.php
#became so suprized
