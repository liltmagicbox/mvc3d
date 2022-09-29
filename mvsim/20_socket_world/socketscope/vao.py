from OpenGL.GL import *

import numpy as np


vao_attrs={
    'position' : np.array([ 0,0,0, 1,0,0, 1,1,0, 0,1,0,]).astype('float32'),
    'uv' : np.array([ 0,0,  1,0,  1,1,  0,1 ]).astype('float32'),
    }
vao_indices = np.array([0,1,2,0,2,3,]).astype('uint')


# positions = [1,2,3,1,2,3,1,2,3]
# normals = [1,1,1,2,2,2,3,3,3,]
# uvs = [1,2,1,2,1,2,1,2]
# indices = [0,1,2, 0,2,3]

class VAO:
    def __init__(self, attr_dict, indices):
        #vertices = np.array( [0,0,0, 0.5,0,0, 0,0.5,0] ).astype('float32')
        #indices = np.array( [0,1,2] ).astype('uint')#not uint8 but uint. since:GL_UNSIGNED_INT
        #[0. 0. 0. 1. 0. 0.  1. 1. 0. 0. 1. 0.    0. 0. 1. 0.  1. 1. 0. 1.]

        #===== attrdict -> vertices . secure np.
        attr_list = []
        for attr_name, nparr in attr_dict.items():
            if not isinstance(nparr,np.ndarray):
                nparr = np.array(nparr).astype('float32')
            attr_list.append(nparr)
        vertices = np.concatenate( attr_list ).astype('float32')

        if not isinstance(indices,np.ndarray):
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
        
        for attr_name, nparr in attr_dict.items():
            data_len = len(nparr)
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
        glDrawElements(GL_TRIANGLES, self.points, GL_UNSIGNED_INT, None)

