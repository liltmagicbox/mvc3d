import json
from collections import UserDict

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
    args = ['shader']


vert_dict = {
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
