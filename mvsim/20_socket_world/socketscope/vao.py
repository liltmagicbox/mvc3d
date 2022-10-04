from OpenGL.GL import *
import numpy as np

#with metadata
geo_dict={
    'name':'mesh1',
    'mesh_dict':{
        'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
        'normal' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
        'indices' : np.array([0,1,2,0,2,3,]).astype('uint'),    
        'bone': [],
        'weight':[],
        }
    }
#mesh_dict = geo_dict['mesh_dict']

#no metadata
mesh_dict={
    'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
    'normal' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
    'indices' : np.array([0,1,2,0,2,3,]).astype('uint'),    
    'bone': [],
    'weight':[],
    }
#vert_dict = {key:value for key,value in mesh_dict.items() if key!='indices' }

#
vert_dict = {
    'position' : [1,2,3,4,5,6],
    'normal':[1,2,3,4,5,6],
    'bone':[1,2,3,4],
    'weight':[1,0,0,0],
}

#meshdict -> pos,ind,attrdict
#pos = mesh_dict['position']
#ind = mesh_dict['indices']
#attr_dict = {key:value for key,value in mesh_dict.items() if (key!='position' or key!='indices') }
attr_dict = {    
    'normal':[1,2,3,4,5,6],
    'bone':[1,2,3,4],
    'weight':[1,0,0,0],
}



class VAO:
    """not supports [ [] [] ]! narrow input rule!
    Geometry as abstract interface, VAO is concrete specific object. Geometry abss.
    """    
    def __init__(self, position, indices, attr_dict=None):#it fits narrow input rule,finally
        # process input
        vert_dict = self.get_vert_dict(position,attr_dict)
        vertices = self.vertdict_to_vertices(vert_dict)
        indices = np.array(indices).astype('uint32')

        # vertices , indices => GPU
        VAO = glGenVertexArrays(1) # create a VA. if 3, 3of VA got. #errs if no window.
        VBO = glGenBuffers(1) #it's buffer, for data of vao.fine.
        EBO = glGenBuffers(1) #indexed, so EBO also. yeah.
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # vert_dict => attribute info
        vert_count = len(vert_dict['position'])//3
        float_size = np.float32(0.0).nbytes #to ensure namespace-safe.        
        offset = ctypes.c_void_p(0)
        loc = 0#NOTE:opengl core no attr 0.
        for attr_name, data in vert_dict.items():
            data_type = GL_FLOAT if attr_name != 'bone' else GL_INT
            data_len = len(data)
            size = data_len//vert_count#size 2,3,4
            stride = 0#size * float_size xyzuv, stride shall be 3forxyz, 2foruv..maybe?
            #loc = glGetAttribLocation(shader.ID, attr_name)
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc, size, data_type, GL_FALSE, stride, offset)#datatype, normalized, stride, offset
            offset = ctypes.c_void_p(data_len*float_size)
            loc+=1

        self.ID = VAO
        self.VBO = VBO
        self.EBO = EBO
        self.points = len(indices)

    def destroy(self):
        self.ID
    def bind(self):
        glBindVertexArray(self.ID)
    def draw(self):
        #GL_POINTS GL_LINE_STRIP GL_TRIANGLES        
        glDrawElements(GL_TRIANGLES, self.points, GL_UNSIGNED_INT, None)

    def update_position(self,position):
        """position first appears. learngl5-7"""
        VAO = self.ID
        VBO = self.VBO
        position = np.array(position, dtype = np.float32) if not isinstance(position,np.ndarray) else position
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        offset = ctypes.c_void_p(0)#position first!hahaha
        glBufferSubData(GL_ARRAY_BUFFER, offset, vertices.nbytes, vertices)
    
    def update_vert_dict(self, position, attr_dict):
        """thats the way! vert_dict is without indices. ..Geometry holds MeshDict(fulldata), hmm.. """
        vert_dict = self.get_vert_dict(position, attr_dict)
        vertices = self.get_vertices(vert_dict)        
        VAO = self.ID
        VBO = self.VBO
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    @staticmethod
    def get_vertices(vert_dict):
        # vert_dict => vertices
        attrlist = []
        for data_array in vert_dict.values():
            attrlist.append(data_array)
        vertices = np.concatenate(attrlist).astype('float32')
        return vertices
    @staticmethod
    def get_vert_dict(position, attr_dict):
        vert_dict = {'position':position}
        vert_dict.update(attr_dict)
        return vert_dict


#wee neeed updateee , positions only., atleast.




        #for the history. the module inside shall be simple. not general-input!
        #===== attrdict -> vertices . secure np.
        # list_for_vert = []
        # data_dict = {}        
        # for attr_name, nparr in attr_dict.items():#if nparr == [ [1,2,3],[4,5,6]]
        #     if not isinstance(nparr,np.ndarray):
        #         nparr = np.array(nparr).flatten().astype('float32')
        #     list_for_vert.append(nparr)
        #     data_dict[attr_name] = len(nparr)        
        
        # vertices = np.concatenate(list_for_vert).astype('float32')
        # if not isinstance(indices,np.ndarray):
        #     indices = np.array(indices).astype('uint32')
        # points = data_dict['position']//3


#vert_dict is vertex info, without indices(which complites mesh_dict)
    # meshdict => vertdict + indices.
    #vert_dict.update(mesh_dict)#indices = mesh_dict.pop('indices') breaks input dict!
    #nomore meshdict.!haha!
    #def __init__(self, mesh_dict):#finally savation. LIP.
    #def __init__(self, position, indices, attr_dict=None):#and it fits narrow input rule.
    #def __init__(self, vert_dict, indices):#we did vert->attr->vert. bad.
    #def __init__(self, mesh_dict):#mesh_dict again.. since indices acts like attr.
        # indices = mesh_dict['indices']
        # assert list(vert_dict.keys())[0] == 'position'
        # indices = np.array(indices).astype('uint32')






#holy,, there was json3d!
#https://json3d.tftlabs.com/doc/info.php
#http://www.cgdev.net/json/index.php
#https://cables.gl/ops/Ops.Json3d

#obj->models loader (single models)
#gltf ->models loader (single models)
#gltf ->scene loader (if yu want models, relpos=>0,0,0 kinds. )

# obj-> [[geo_dict,mat_dict]] ->  geo,mat = Geometry(geo_dict), Material(mat_dict) -> StaticMesh( geo,mat )
# gltf -> [[geo_dict,mat_dict], ] ->  geo,mat = Geometry(geo_dict), Material(mat_dict) -> StaticMesh( geo,mat )
#gltf-> geodict,matdict,bonedict,animdict. lets this be another dict!
#so, obj-> {'geodict':[geodict], 'matdict': [matdict]} .
#and finally, 
# scene = {
#     'node':[ 
#         {'id':i,'parent':i, 'mesh':'StaticMesh', 'geometry':'ball','material':'m2', 'positon':[],'rotation':[],'scale':[] },
#         {'id':i,'parent':i, 'mesh':'StaticMesh', 'positon':[],'rotation':[],'scale':[] },
#     ],#do we need parenting??  course if a man with hat..

#     'geodict':[
#         {'name':'ball',
#         'position':[],#Geo holding full info data(can save/load!),   and give minimal data VAO kinds.
#         'indices':[]}
#     ],
#     'geodict':{
#         'ball':{'position':[],'indices':[]}        #not thisway,  GeoDict is also single form of a file.
#     },

#     'matdict':[
#     {'name':'m2','shader':'sha','texture':[],'color':[1,0,0]},
#     {'name':'m2','shader':'sha','texture':[], 'attrs':{'color':[1,0,0]} },
#     ]
# }

# #this is internal data form.
# #vert save/load. and like: mat, anim , bone, ,
# {"indices": [],
# "position": [],
# "normal": [12, 3]}    

# vao_attrs={
#     'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
#     'uv' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
#     }
# vao_indices = np.array([0,1,2,0,2,3,]).astype('uint')