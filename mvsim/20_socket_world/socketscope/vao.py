from OpenGL.GL import *

import numpy as np


vao_attrs={
    'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
    'uv' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
    }
vao_indices = np.array([0,1,2,0,2,3,]).astype('uint')


class VAO:
    def __init__(self, attr_dict, indices):        
        attrlist=[]
        for data_array in attr_dict.values():
            attrlist.append(data_array)
        vertices = np.concatenate(attrlist).astype('float32')        
        indices = np.array(indices).astype('uint32')

        #====
        VAO = glGenVertexArrays(1) # create a VA. if 3, 3of VA got. #errs if no window.
        VBO = glGenBuffers(1) #it's buffer, for data of vao.fine.
        EBO = glGenBuffers(1) #indexed, so EBO also. yeah.
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        #====
        vert_count = len(attr_dict['position'])//3
        float_size = np.float32(0.0).nbytes #to ensure namespace-safe.        
        offset = ctypes.c_void_p(0)
        loc = 0#NOTE:opengl core no attr 0.
        
        for attr_name, data in attr_dict.items():
            data_len = len(data)
            size = data_len//vert_count#size 2,3,4
            stride = 0#size * float_size xyzuv, stride shall be 3forxyz, 2foruv..maybe?
            #loc = glGetAttribLocation(shader.ID, attr_name)
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc, size, GL_FLOAT, GL_FALSE, stride, offset)#datatype, normalized, stride, offset
            offset = ctypes.c_void_p(data_len*float_size)
            loc+=1

        self.VAO = VAO
        self.VBO = VBO
        self.EBO = EBO
        self.points = len(indices)
    def bind(self):
        glBindVertexArray(self.VAO)
    def draw(self):
        #GL_POINTS GL_LINE_STRIP GL_TRIANGLES        
        glDrawElements(GL_TRIANGLES, self.points, GL_UNSIGNED_INT, None)

    def update(self,attr_dict):
        """thats the way!"""
        VAO = self.VAO
        VBO = self.VBO
        attrlist=[]
        for data_array in attr_dict.values():
            attrlist.append(data_array)
        vertices = np.concatenate(attrlist).astype('float32')
        glBindVertexArray(VAO) #gpu bind VAO
        glBindBuffer(GL_ARRAY_BUFFER, VBO) #gpu bind VBO in VAO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)


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