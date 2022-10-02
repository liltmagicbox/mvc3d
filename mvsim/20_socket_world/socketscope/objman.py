import os
#smd format
#? vx vy vz / uu uv / nx ny nz / N b1 b2 b3 b4

# xyzxyz / uvuv indices. name is each-object name.


def main():
    targetdir = 'yup'
    filename = 'objobjects.obj'
    objdir = os.path.join(targetdir,filename)
    x = get_mesh_dicts(objdir, 1)
    print(get_material_dict(x[0]['mtl']))

def _load_obj(fdir, verbose=False):
    """
    objfile,
    object = [ mesh, mesh ]
    object has vert_dict.
    mesh has faces. shares object's vert_dict.
    """
    current_dir, file_name = os.path.split(fdir)
    mtl_name = 'no_mtl'    

    vert_dict = {}
    
    def get_objectdata():
        object_data = {}
        object_data['obj'] = fdir
        object_data['mtl'] = os.path.join(current_dir,mtl_name)
        object_data['meshes'] = []
        return object_data

    object_data = None
    objects = []
    for line in open(fdir, 'r', encoding = 'utf-8'):
        state = 0
        if line.startswith('#'):
            continue
        
        values = line.split()
        if not values:
            continue
            
        if values[0] == 'mtllib':
            material_file = values[1]
            mtl_name = material_file

        elif values[0] == 'o':#blender, another object. object is mesh holder.
            object_name = values[1]
            if object_data:
                objects.append(object_data)
            object_data = get_objectdata()
            object_data['name'] = object_name                        
        
        #===these are vert_dict! shared vert of meshes, same object.
        elif values[0] == 'v':
            position = list(map(float, values[1:]))
            if not 'position' in vert_dict:
                vert_dict['position'] = []
            vert_dict['position'].append(position)
        elif values[0] == 'vt':
            uv = list(map(float, values[1:]))
            if not 'uv' in vert_dict:
                vert_dict['uv'] = []
            vert_dict['uv'].append(uv)
        elif values[0] == 'vn':
            normal = list(map(float, values[1:]))
            if not 'normal' in vert_dict:
                vert_dict['normal'] = []
            vert_dict['normal'].append(normal)


        #========below seems of mesh
        elif values[0] == 'g':#dose it even happens?
            raise ValueError("group found!")
            group = values[1]
            mesh_data['group'] = group
        
        elif values[0] == 'usemtl':#assume it's initiator of .. each mesh.(joined)
            material = values[1]

            #add new mesh.
            object_data['meshes'].append({})
            mesh_data = object_data['meshes'][-1]
            mesh_data['material'] = material

        elif values[0] == 's':
            smoothing = values[1]
            mesh_data = object_data['meshes'][-1]
            if smoothing == 'off':
                val = 0
            mesh_data['smoothing'] = val

        elif values[0] == 'f':
            mesh_data = object_data['meshes'][-1]
            if len(values[1:])==3:
                for point in values[1:]:
                    #vertex, vertex/uv, vertex/uv/normal, vertex/normal
                    w = point.split('/')#f 5/1/1 3/2/1 1/3/1                
                    face = list(map(lambda x: int(x) ,w))                    
                    
                    if not 'face' in mesh_data:
                        mesh_data['face'] = []
                    mesh_data['face'].append(face)
            #[ [5,1,1],[3,2,1],[1,3,1] ]
            else:
                raise ValueError("Triangulate Faces!")
                v0,v1,v2,v3 = values[1:]#012 023 LH 0123 012 023 RH
                trifaces = [v0,v1,v2, v0,v2,v3]
                for v in trifaces:
                    w = v.split('/')
                    face = list(map(lambda x: int(x) ,w))
                    mesh_data['face'] = [] if not 'face' in mesh_data else mesh_data['face']            
                    mesh_data['face'].append(face)
        
    objects.append(object_data)
    for object_data in objects:
        object_data['vert_dict'] = vert_dict#memory shared, but not that bad.!
    
    if verbose:
        for obj in objects:
            print('===object===')
            for key,value in obj.items():
                if key == 'vert_dict':
                    print('-','vert_dict', value.keys())                    
                elif key == 'meshes':
                    for mesh in value:
                        print('=mesh=')
                        for key,value in mesh.items():
                            if key == 'face':
                                print('--',key,len(value))
                            else:
                                print('--',key,value)
                else:
                    print('-',key,value)
    return objects


#Mesh(name)->Geometry1,mat1, Geo2,mat2
#obj, Cube, Isosphere  , is 2 Mesh.  Cube[geo1,mat1,geo2,mat2]
#(obj)object-mesh,mesh -> (py)MeshActor[mesh,mesh]! , mesh=geo,mat.

def _parse_object_data(object_data, verbose):
    print('============\n','parsing object') if verbose else 1
    #print(object_data.keys())#['vert_dict', 'obj', 'mtl', 'meshes', 'name'])
    vert_dict = object_data.pop('vert_dict')
    meshes = object_data.pop('meshes')
    object_data['meshes'] = []
    
    #print(meshes[0].keys())#dict_keys(['material', 'smoothing', 'face'])
    for mesh_data in meshes:
        mesh_data['vert_dict'] = vert_dict
        mesh_dict = _parse_mesh_data(mesh_data,verbose)
        
        object_data['meshes'].append(mesh_dict)
    return object_data

def _parse_mesh_data(mesh_data, verbose):
    "parse, [ [1,2,3],[4,5,6] ] -> [1,2,3,4,5,6]"
    vert_dict = mesh_data.pop('vert_dict')
    face_idxs = mesh_data.pop('face')
    output_dict = mesh_data
    #============
    vert_dict_values = list(vert_dict.values())
    multex_dict = {}
    indices = []
    for faceidx in face_idxs:
        multex = []
        for vert_idx, idx in enumerate(faceidx):
            vertex_data = vert_dict_values[vert_idx][idx-1]
            multex.append(tuple(vertex_data))
        new_multex = tuple(multex)
        
        index = multex_dict.get(new_multex)
        if index == None:
            index = len(multex_dict)
            multex_dict[new_multex] = index
        indices.append(index)

    #===new_vert_dict from indices. reuse multex!
    #'pos':[]
    #'uv':[]
    mesh_dict = {key:[] for key in vert_dict.keys()}
    for multex in multex_dict.keys():# [ ((x,y,z),(uv)),, ]
        for idx, vert_list in enumerate(mesh_dict.values()):
            vert_list.extend( multex[idx] )
    mesh_dict['indices'] = indices
    #============
    output_dict['mesh_dict'] = mesh_dict#this mesh_dict is iMeshDict
    return output_dict


def _parse_obj(objects, verbose=False):
    new_objects = []
    
    for object_data in objects:
        #print(object_data['name'])#good for debug
        new_object_data = _parse_object_data(object_data, verbose)        
        #print(new_object_data['meshes'][0].keys())
        #['obj', 'mtl', 'name', 'meshes']
        #dict_keys(['material', 'smoothing', 'mesh_dict'])        
        if verbose:
            for key,value in new_object_data.items():
                if key == 'meshes':
                    for mesh in value:
                        print(mesh.keys())                        
                else:
                    print(value[:22])

        new_objects.append(new_object_data)
    return new_objects



def get_mesh_dicts(fdir, verbose = False):
    print('////////loading////////') if verbose else 1
    x = _load_obj(fdir,verbose)
    print('////////parsing////////') if verbose else 1
    x = _parse_obj(x,verbose)
    return x




def get_material_dict(fdir, verbose = False):
    mats = {}
    mat_dict = {}
    
    for line in open(fdir, 'r', encoding = 'utf-8'):
        if line.startswith('#'):
            continue        
        values = line.split()
        if not values:
            continue
        #==============

        if values[0] == 'newmtl':
            if mat_dict:
                if 'name' in mat_dict:
                    mats[mat_dict['name']] = mat_dict
                    mat_dict = {}#here re-write appaired.!
            mat_name = values[1]
            mat_dict['name'] = mat_name

        elif values[0] == 'Ns':
            specular = values[1]

        elif values[0] == 'Ka':
            aaa = values[1:]
        elif values[0] == 'Kd':
            val = values[1:]
            mat_dict['Kd'] = tuple(map(float,val))
        elif values[0] == 'Ks':
            smoothness = values[1:]
        elif values[0] == 'Ke':
            eee = values[1:]
        
        elif values[0] == 'Ni':
            iii = values[1]
        elif values[0] == 'd':
            ddd = values[1]
        elif values[0] == 'illum':
            illum = values[1]

        elif values[0] == 'map_Kd':
            map_diffuse = values[1]
            if not 'texture' in mat_dict:
                mat_dict['texture'] = {}
            mat_dict['texture']['diffuse'] = diffuse#major shall be texture, not x,y,z!
        
    if 'name' in mat_dict:
        mats[mat_dict['name']] = mat_dict
    return mats

        
        




if __name__ == '__main__':
    main()
    






#pack inversed index dict.
# { 
# ([x,y,z],[u,v],[nx,ny,nz]):0,
# ([x,y,z],[u,v],[nx,ny,nz]):1,
# ([x,y,z],[u,v],[nx,ny,nz]):2,
# }
#anyway we did.
#indices [0, 1, 2, 3, 2, 3, 4, 5, 6, 4, 6, 7, 8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15, 16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23] 36 



# {
#     'position':[ [1,2,3],[1,2,3],],
#     'normal':[ [1,2,3],[1,2,3],],
#     'face':[ [0,0],[1,1],[2,2]],
#     'smoothing':'off'
# }

#
# {
#     'position':[ [1,2,3],[1,2,3],[1,2,3],],
#     'normal':[ [1,2,3],[1,2,3],[1,2,3],],
#     'indices':[ [1,2,3],[1,2,3],[1,2,3],],
#     'smoothing':'off'
# }



def _ver1_parse_mesh_data(mesh_data, verbose):
    mesh_data['vert'].pop('normal')
    vert_names = []
    vert_raw_data = []
    for key,data in mesh_data['vert'].items():
        vert_names.append(key)
        vert_raw_data.append(data)
    #[ [pos1,pos2,pos3], [norm1,norm2,norm3,]]

    vert_dict = {}
    #print('wwww',len(mesh_data['face']))#36 points.
    # keys = list(mesh_data['vert'].keys())
    # for idx, i in enumerate(face):
    #     realkey = keys[idx]
    #     real_data = mesh_data['vert'][realkey][i-1]
    for face in mesh_data['face']:
        print('___________-',face)
        for idx, vertidx in enumerate(face):
            vertidx-=1
            if idx==2:
                break
            vert_real_data = vert_raw_data[idx][vertidx]
            vert_name = vert_names[idx]
            print('vr',vert_real_data, vert_name) if verbose else 1
            
            vert_dict[vert_name] = [] if not vert_name in vert_dict else vert_dict[vert_name]                            
            vert_dict[vert_name].append(vert_real_data)
    
    new_mesh_data = {}
    indices = [i for i in range( len(mesh_data['face']) )]
    new_mesh_data['indices'] = indices
    new_mesh_data['vert_dict'] = vert_dict
    
    mesh_data.pop('vert')
    mesh_data.pop('face')
    new_mesh_data.update(mesh_data)

    # ppp = [0.499727, 1.0, 0.499727,-0.499727, 1.0, -0.499727,
    #  -0.499727, 1.0, 0.499727,-0.499727, 1.0, -0.499727,
    #  1.0, -1.0, -1.0,-1.87501, -1.0, -1.0, 0.499727, 1.0, -0.499727,
    # ]
    # new_mesh_data = {
    # 'vert_dict':{
    # 'position':ppp,
    # },
    # 'indices':[0,1,2, 3,4,5],
    # 'name':'ham'
    # }
    return new_mesh_data

def _ver2_parse_mesh_data(mesh_data, verbose):
    vert_names = []
    vert_raw_data = []
    for key,data in mesh_data['vert'].items():
        vert_names.append(key)
        vert_raw_data.append(data)
    #[ [pos1,pos2,pos3], [norm1,norm2,norm3,]]

    indices = []
    vert_packed_inversed_dict = {}
    vert_dict = {}
    for vert_idxs in mesh_data['face']:
        vert_packed_data = []
        mini_vert_dict = {}

        for idx, vertidx in enumerate(vert_idxs):
            vert_real_data = vert_raw_data[idx][vertidx-1]
            vert_name = vert_names[idx]
            #print('vr',vert_real_data, vert_name) if verbose else 1
            
            mini_vert_dict[vert_name] = vert_real_data
            vert_packed_data.append(tuple(vert_real_data))
        vert_packed_data = tuple(vert_packed_data)
        
        pack_idx = vert_packed_inversed_dict.get(vert_packed_data,None)
        if pack_idx == None:# bool(0) was also False.ha!
            index = len(vert_packed_inversed_dict)
            vert_packed_inversed_dict[vert_packed_data] = index
            
            #fill the dict!
            for key,value in mini_vert_dict.items():
                vert_dict[key] = [] if not key in vert_dict else vert_dict[key]                            
                vert_dict[key].extend(value)#here flattens.
                #assert len(vert_dict[key]) ==len(vert_packed_inversed_dict)
        else:
            index = pack_idx
        indices.append(index)

    new_mesh_data = {} 
    new_mesh_data['vert_dict'] = vert_dict
    new_mesh_data['indices'] = indices
    
    mesh_data.pop('vert')
    mesh_data.pop('face')
    new_mesh_data.update(mesh_data)
    return new_mesh_data