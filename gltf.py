"""gltf.py -- glTF 2.0 scene writer + reader. stdlib only, single file.

geometry format is the engine's attrs dict, same as vao.py / Geometry:
	attrs = {
	'position': [x,y,z, x,y,z, ...],   # flat, or [(x,y,z),...] both fine
	'normal':   [...],                 # optional
	'uv':       [...],                 # optional, 2 per vertex
	'color':    [...],                 # optional, 3 or 4 per vertex
	'index':    [0,1,2, ...],          # optional ('face' also accepted)
	}

axes: engine world is Z-up. glTF is Y-up RH.
	up='+Z' (default) puts one root node rotated -90deg about X, mesh bytes untouched.
	blender/three/UE importers all understand it, and blender comes back to Z-up.

units: glTF is meters. UE importer multiplies x100 (cm) by itself. keep world in meters.

use:
	g = Gltf()
	mat  = g.add_material(color=0xff8800, roughness=0.6)
	mesh = g.add_mesh(attrs, material=mat, name='body')
	node = g.add_node(mesh=mesh, pos=(0,0,1), rot=(0,0,0.5), name='unit1')
	g.add_node(camera=g.add_camera(fov=70), pos=(5,-5,3))
	g.add_node(light=g.add_light('sun'), rot=(0.9,0,0.8))
	g.save('scene.glb')          # .glb or .gltf by extension

	scene = load('scene.glb')    # -> plain dicts, attrs same shape as above
"""

import json
import math
import base64
import struct

#=============== component types
FLOAT = 5126
UBYTE = 5121
USHORT = 5123
UINT = 5125
BYTE = 5120
SHORT = 5122

_CSIZE = {BYTE:1, UBYTE:1, SHORT:2, USHORT:2, UINT:4, FLOAT:4}
_CFMT = {BYTE:'b', UBYTE:'B', SHORT:'h', USHORT:'H', UINT:'I', FLOAT:'f'}
_NCOMP = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4, 'MAT4':16}

TRIANGLES = 4
POINTS = 0
LINES = 1

# engine attr name <-> gltf semantic
_SEMANTIC = {'position':'POSITION', 'normal':'NORMAL', 'uv':'TEXCOORD_0',
	'color':'COLOR_0', 'tangent':'TANGENT'}
_SEMANTIC_BACK = {v:k for k,v in _SEMANTIC.items()}


#=============== small math (no numpy needed)

def euler_to_quat(rx,ry,rz):
	"xyz order (three.js 'XYZ'), radians. returns (x,y,z,w)."
	cx,sx = math.cos(rx/2), math.sin(rx/2)
	cy,sy = math.cos(ry/2), math.sin(ry/2)
	cz,sz = math.cos(rz/2), math.sin(rz/2)
	x = sx*cy*cz + cx*sy*sz
	y = cx*sy*cz - sx*cy*sz
	z = cx*cy*sz + sx*sy*cz
	w = cx*cy*cz - sx*sy*sz
	return (x,y,z,w)

def quat_to_euler(x,y,z,w):
	"back to xyz order euler, radians."
	# from rotation matrix of q, xyz order
	m13 = 2*(x*z + w*y)
	m13 = max(-1.0, min(1.0, m13))
	ry = math.asin(m13)
	if abs(m13) < 0.9999999:
		rx = math.atan2( -(2*(y*z - w*x)), 1-2*(x*x+y*y) )
		rz = math.atan2( -(2*(x*y - w*z)), 1-2*(y*y+z*z) )
	else:
		rx = math.atan2( 2*(y*z + w*x), 1-2*(x*x+z*z) )
		rz = 0.0
	return (rx,ry,rz)

def _flat(data):
	"[(x,y,z),..] / [x,y,z,..] / np arrays -> flat python float list"
	out = []
	for item in data:
		try:
			out.extend(float(v) for v in item)
		except TypeError:
			out.append(float(item))
	return out

def _flat_int(data):
	out = []
	for item in data:
		try:
			out.extend(int(v) for v in item)
		except TypeError:
			out.append(int(item))
	return out

def _mat3_to_quat(r):
	"r: column-major flat9, columns = x,y,z axes. -> (x,y,z,w)"
	tr = r[0]+r[4]+r[8]
	if tr > 0:
		s = math.sqrt(tr+1.0)*2
		w = 0.25*s
		x = (r[5]-r[7])/s
		y = (r[6]-r[2])/s
		z = (r[1]-r[3])/s
	elif r[0]>r[4] and r[0]>r[8]:
		s = math.sqrt(1.0+r[0]-r[4]-r[8])*2
		x = 0.25*s
		w = (r[5]-r[7])/s
		y = (r[3]+r[1])/s
		z = (r[6]+r[2])/s
	elif r[4]>r[8]:
		s = math.sqrt(1.0+r[4]-r[0]-r[8])*2
		y = 0.25*s
		w = (r[6]-r[2])/s
		x = (r[3]+r[1])/s
		z = (r[7]+r[5])/s
	else:
		s = math.sqrt(1.0+r[8]-r[0]-r[4])*2
		z = 0.25*s
		w = (r[1]-r[3])/s
		x = (r[6]+r[2])/s
		y = (r[7]+r[5])/s
	return (x,y,z,w)

def look_at_quat(pos, target, up=(0,0,1)):
	"""rotation quat that aims node -Z at target (gltf camera/light forward), +Y toward up.
	up=(0,0,1) for engine z-up placement. use for camera and sun nodes."""
	fx = target[0]-pos[0]
	fy = target[1]-pos[1]
	fz = target[2]-pos[2]
	fl = math.sqrt(fx*fx+fy*fy+fz*fz) or 1.0
	zx,zy,zz = -fx/fl, -fy/fl, -fz/fl  # node z = -forward
	ux,uy,uz = up
	xx = uy*zz - uz*zy
	xy = uz*zx - ux*zz
	xz = ux*zy - uy*zx
	xl = math.sqrt(xx*xx+xy*xy+xz*xz)
	if xl < 1e-6:  # looking straight along up
		xx,xy,xz, xl = 1,0,0, 1
	xx,xy,xz = xx/xl, xy/xl, xz/xl
	yx = zy*xz - zz*xy
	yy = zz*xx - zx*xz
	yz = zx*xy - zy*xx
	return _mat3_to_quat([xx,xy,xz, yx,yy,yz, zx,zy,zz])

def calc_normals(attrs):
	"""smooth (area-weighted) vertex normals from triangles.
	sets attrs['normal'] and returns it. the mvc3d Geometry.calc_normal, done."""
	pos = _flat(attrs['position'])
	index = attrs.get('index', attrs.get('face'))
	if index is None:
		index = list(range(len(pos)//3))
	index = _flat_int(index)
	normal = [0.0]*len(pos)
	for t in range(0, len(index)-2, 3):
		i,jj,k = index[t]*3, index[t+1]*3, index[t+2]*3
		ax,ay,az = pos[jj]-pos[i], pos[jj+1]-pos[i+1], pos[jj+2]-pos[i+2]
		bx,by,bz = pos[k]-pos[i], pos[k+1]-pos[i+1], pos[k+2]-pos[i+2]
		nx = ay*bz - az*by
		ny = az*bx - ax*bz
		nz = ax*by - ay*bx
		for v in (i,jj,k):
			normal[v] += nx
			normal[v+1] += ny
			normal[v+2] += nz
	for v in range(0, len(normal), 3):
		l = math.sqrt(normal[v]**2 + normal[v+1]**2 + normal[v+2]**2) or 1.0
		normal[v] /= l
		normal[v+1] /= l
		normal[v+2] /= l
	attrs['normal'] = normal
	return normal

def _color3(value):
	"0xff8800 or (r,g,b) 0..1 -> [r,g,b]"
	if isinstance(value, int):
		r = ((value>>16)&0xff)/255
		g = ((value>>8)&0xff)/255
		b = (value&0xff)/255
		return [r,g,b]
	return [float(v) for v in value][:3]


#=============== writer

class Gltf:
	def __init__(self, name='scene', up='+Z', generator='axis3d.gltf'):
		self.up = up
		self.j = {
			'asset': {'version':'2.0', 'generator':generator},
			'scene': 0,
			'scenes': [ {'name':name, 'nodes':[]} ],
			'nodes': [],
			'meshes': [],
			'materials': [],
			'accessors': [],
			'bufferViews': [],
			'buffers': [],
		}
		self.bin = bytearray()
		self.lights = []
		self.cameras = []
		self._root = None  # z-up wrapper node idx

	#=========== data plumbing
	def _view(self, blob, target=None):
		while len(self.bin)%4:
			self.bin += b'\x00'
		view = {'buffer':0, 'byteOffset':len(self.bin), 'byteLength':len(blob)}
		if target:
			view['target'] = target
		self.bin += blob
		self.j['bufferViews'].append(view)
		return len(self.j['bufferViews'])-1

	def _accessor(self, values, ctype, atype, target=None, minmax=False):
		n_comp = _NCOMP[atype]
		count = len(values)//n_comp
		blob = struct.pack(f"<{len(values)}{_CFMT[ctype]}", *values)
		acc = {'bufferView': self._view(blob,target),
			'componentType':ctype, 'count':count, 'type':atype}
		if minmax:
			mins = [ min(values[i::n_comp]) for i in range(n_comp)]
			maxs = [ max(values[i::n_comp]) for i in range(n_comp)]
			acc['min'],acc['max'] = mins,maxs
		self.j['accessors'].append(acc)
		return len(self.j['accessors'])-1

	#=========== content
	def add_mesh(self, attrs, material=None, name=None, mode=TRIANGLES):
		"attrs dict -> mesh index. one primitive per call (see add_primitive to stack)."
		mesh = {'primitives':[]}
		if name: mesh['name'] = name
		self.j['meshes'].append(mesh)
		idx = len(self.j['meshes'])-1
		self.add_primitive(idx, attrs, material, mode)
		return idx

	def add_primitive(self, mesh_idx, attrs, material=None, mode=TRIANGLES):
		"a mesh can hold multi primitives (= submeshes with own material)."
		position = _flat(attrs['position'])
		n_verts = len(position)//3
		prim_attrs = {'POSITION': self._accessor(position, FLOAT,'VEC3', 34962, minmax=True)}

		for key in ('normal','uv','color','tangent'):
			if key not in attrs or attrs[key] is None or not len(attrs[key]):
				continue
			data = _flat(attrs[key])
			n_comp = len(data)//n_verts
			atype = {1:'SCALAR',2:'VEC2',3:'VEC3',4:'VEC4'}[n_comp]
			prim_attrs[_SEMANTIC[key]] = self._accessor(data, FLOAT, atype, 34962)

		# free-form engine attrs ride along as _NAME (gltf allows underscore customs)
		for key in attrs:
			if key in ('position','normal','uv','color','tangent','index','face'):
				continue
			data = _flat(attrs[key])
			n_comp = len(data)//n_verts
			atype = {1:'SCALAR',2:'VEC2',3:'VEC3',4:'VEC4'}.get(n_comp)
			if atype:
				prim_attrs['_'+key.upper()] = self._accessor(data, FLOAT, atype, 34962)

		prim = {'attributes':prim_attrs}
		if mode != TRIANGLES:
			prim['mode'] = mode
		index = attrs.get('index', attrs.get('face'))
		if index is not None and len(index):
			index = _flat_int(index)
			ctype = USHORT if max(index) < 65536 else UINT
			prim['indices'] = self._accessor(index, ctype,'SCALAR', 34963)
		if material is not None:
			prim['material'] = material
		self.j['meshes'][mesh_idx]['primitives'].append(prim)

	def add_material(self, name=None, color=0x888888, metallic=0.0, roughness=0.9,
			emissive=None, opacity=1.0, double_sided=False):
		"maps to PBR metallic-roughness. color: 0xRRGGBB or (r,g,b) 0..1."
		mat = {'pbrMetallicRoughness': {
			'baseColorFactor': _color3(color)+[float(opacity)],
			'metallicFactor': float(metallic),
			'roughnessFactor': float(roughness),
		}}
		if name: mat['name'] = name
		if emissive is not None:
			mat['emissiveFactor'] = _color3(emissive)
		if opacity < 1.0:
			mat['alphaMode'] = 'BLEND'
		if double_sided:
			mat['doubleSided'] = True
		self.j['materials'].append(mat)
		return len(self.j['materials'])-1

	def add_camera(self, fov=70, ratio=None, near=0.01, far=1000):
		"perspective. fov: vertical, degrees (same meaning as vector.Camera). looks down its -Z(gltf) = -Y(engine front... place via rot)."
		cam = {'type':'perspective','perspective':{
			'yfov': math.radians(fov), 'znear': float(near), 'zfar': float(far)}}
		if ratio:
			cam['perspective']['aspectRatio'] = float(ratio)
		self.cameras.append(cam)
		return len(self.cameras)-1

	def add_light(self, kind='point', color=(1,1,1), intensity=None, range=None,
			inner_angle=0.0, outer_angle=math.pi/4, name=None):
		"""kind: 'sun'/'directional', 'point', 'spot'. KHR_lights_punctual.
		intensity is PHOTOMETRIC: lux for sun, candela for point/spot. use real-world-ish
		values (daylight 10k~100k lux, room bulb ~1k cd) -- blender divides by 683 to get
		watts, UE reads lux/cd directly. tiny values render pitch black in blender/UE.
		light shines down node -Z. place via rot (look_at_quat helps)."""
		kind = {'sun':'directional'}.get(kind, kind)
		if intensity is None:
			intensity = 10000.0 if kind=='directional' else 1000.0
		light = {'type':kind, 'color':_color3(color), 'intensity':float(intensity)}
		if name: light['name'] = name
		if range and kind!='directional':
			light['range'] = float(range)
		if kind == 'spot':
			light['spot'] = {'innerConeAngle':float(inner_angle),'outerConeAngle':float(outer_angle)}
		self.lights.append(light)
		return len(self.lights)-1

	def add_node(self, name=None, mesh=None, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1),
			parent=None, camera=None, light=None, extras=None):
		"rot: euler xyz radians (3,) or quaternion (4,). parent=None -> scene root."
		node = {}
		if name: node['name'] = name
		if mesh is not None: node['mesh'] = mesh
		if camera is not None: node['camera'] = camera
		if light is not None:
			node['extensions'] = {'KHR_lights_punctual': {'light':light}}
		pos = tuple(float(v) for v in pos)
		scale = tuple(float(v) for v in scale)
		rot = tuple(float(v) for v in rot)
		if len(rot) == 3:
			rot = euler_to_quat(*rot)
		if pos != (0,0,0): node['translation'] = list(pos)
		if rot != (0,0,0,1): node['rotation'] = list(rot)
		if scale != (1,1,1): node['scale'] = list(scale)
		if extras: node['extras'] = extras
		self.j['nodes'].append(node)
		idx = len(self.j['nodes'])-1
		if parent is None:
			self._scene_add(idx)
		else:
			self.j['nodes'][parent].setdefault('children',[]).append(idx)
		return idx

	def _scene_add(self, idx):
		if self.up == '+Z':
			if self._root is None:
				s = math.sin(-math.pi/4)
				c = math.cos(-math.pi/4)
				self.j['nodes'].append({'name':'zup_root','rotation':[s,0,0,c],'children':[]})
				self._root = len(self.j['nodes'])-1
				self.j['scenes'][0]['nodes'].append(self._root)
			if idx != self._root:
				self.j['nodes'][self._root]['children'].append(idx)
		else:
			self.j['scenes'][0]['nodes'].append(idx)

	#=========== output
	def _finish(self):
		j = self.j
		if self.cameras:
			j['cameras'] = self.cameras
		if self.lights:
			j.setdefault('extensionsUsed',[])
			if 'KHR_lights_punctual' not in j['extensionsUsed']:
				j['extensionsUsed'].append('KHR_lights_punctual')
			j['extensions'] = {'KHR_lights_punctual':{'lights':self.lights}}
		for key in ('materials','accessors','bufferViews','buffers','meshes','nodes'):
			if not j[key]:
				j.pop(key)
		return j

	def save(self, path):
		if str(path).endswith('.glb'):
			blob = self.to_glb()
		else:
			blob = self.to_gltf().encode()
		with open(path,'wb') as f:
			f.write(blob)
		return path

	def to_gltf(self):
		"single .gltf file, buffer embedded base64."
		j = self._finish()
		if self.bin:
			uri = 'data:application/octet-stream;base64,' + base64.b64encode(bytes(self.bin)).decode()
			j['buffers'] = [ {'uri':uri, 'byteLength':len(self.bin)} ]
		return json.dumps(j)

	def to_glb(self):
		j = self._finish()
		binblob = bytes(self.bin)
		while len(binblob)%4:
			binblob += b'\x00'
		if binblob:
			j['buffers'] = [ {'byteLength':len(binblob)} ]
		jblob = json.dumps(j, separators=(',',':')).encode()
		while len(jblob)%4:
			jblob += b' '
		total = 12 + 8+len(jblob) + (8+len(binblob) if binblob else 0)
		out = struct.pack('<III', 0x46546C67, 2, total)
		out += struct.pack('<II', len(jblob), 0x4E4F534A) + jblob
		if binblob:
			out += struct.pack('<II', len(binblob), 0x004E4942) + binblob
		return out


#=============== reader

def load(path):
	"""read .glb / .gltf -> plain dict:
	{
	'meshes': [ {'name':.., 'primitives':[ {'attrs':{engine attrs dict}, 'material':i, 'mode':4} ]} ],
	'materials': [ {'name':..,'color':[r,g,b,a],'metallic':f,'roughness':f,'emissive':[rgb],'double_sided':b} ],
	'nodes': [ {'name':..,'pos':(x,y,z),'quat':(x,y,z,w),'rot':(euler xyz),'scale':..,'mesh':i,'camera':i,'light':i,'children':[..],'extras':{}} ],
	'roots': [node idx],   # scene root nodes
	'cameras': [ {'fov':deg,'ratio':..,'near':..,'far':..} ],
	'lights': [ {'kind':..,'color':..,'intensity':..} ],
	}
	limitations: no sparse accessors, no draco. textures: uri kept as-is in material['textures'].
	"""
	blob = open(path,'rb').read()
	if blob[:4] == b'glTF':
		j, buffers = _parse_glb(blob)
	else:
		j = json.loads(blob)
		buffers = [_load_buffer(b, path) for b in j.get('buffers',[])]
	return _parse(j, buffers)

def _parse_glb(blob):
	magic, version, length = struct.unpack_from('<III', blob, 0)
	offset = 12
	j = None
	buffers = []
	while offset < length:
		clen, ctype = struct.unpack_from('<II', blob, offset)
		offset += 8
		chunk = blob[offset:offset+clen]
		offset += clen
		if ctype == 0x4E4F534A:
			j = json.loads(chunk)
		elif ctype == 0x004E4942:
			buffers.append(chunk)
	return j, buffers

def _load_buffer(buf, path):
	import os
	uri = buf.get('uri','')
	if uri.startswith('data:'):
		return base64.b64decode(uri.split(',',1)[1])
	fdir = os.path.dirname(os.path.abspath(path))
	with open(os.path.join(fdir,uri),'rb') as f:
		return f.read()

def _read_accessor(j, buffers, idx):
	acc = j['accessors'][idx]
	if 'sparse' in acc:
		raise NotImplementedError('sparse accessor')
	n_comp = _NCOMP[acc['type']]
	count = acc['count']
	ctype = acc['componentType']
	csize = _CSIZE[ctype]
	fmt = _CFMT[ctype]
	if 'bufferView' not in acc:
		return [0]*(count*n_comp)
	view = j['bufferViews'][acc['bufferView']]
	data = buffers[view['buffer']]
	start = view.get('byteOffset',0) + acc.get('byteOffset',0)
	stride = view.get('byteStride') or n_comp*csize
	out = []
	for i in range(count):
		offset = start + i*stride
		out.extend( struct.unpack_from(f"<{n_comp}{fmt}", data, offset) )
	if acc.get('normalized'):
		top = {UBYTE:255, USHORT:65535, BYTE:127, SHORT:32767}[ctype]
		out = [ max(v/top,-1.0) for v in out ]
	return out

def _parse(j, buffers):
	scene = {'meshes':[], 'materials':[], 'nodes':[], 'roots':[], 'cameras':[], 'lights':[]}

	for m in j.get('materials',[]):
		pbr = m.get('pbrMetallicRoughness',{})
		mat = {'name': m.get('name',''),
			'color': pbr.get('baseColorFactor',[1,1,1,1]),
			'metallic': pbr.get('metallicFactor',1.0),
			'roughness': pbr.get('roughnessFactor',1.0),
			'emissive': m.get('emissiveFactor',[0,0,0]),
			'double_sided': m.get('doubleSided',False)}
		textures = {}
		if 'baseColorTexture' in pbr:
			textures['color'] = pbr['baseColorTexture'].get('index')
		if 'normalTexture' in m:
			textures['normal'] = m['normalTexture'].get('index')
		if textures:
			mat['textures'] = textures
		scene['materials'].append(mat)

	for m in j.get('meshes',[]):
		mesh = {'name':m.get('name',''), 'primitives':[]}
		for p in m.get('primitives',[]):
			attrs = {}
			for semantic, acc_idx in p.get('attributes',{}).items():
				key = _SEMANTIC_BACK.get(semantic)
				if key is None:
					key = semantic.lower().lstrip('_')
				attrs[key] = _read_accessor(j, buffers, acc_idx)
			if 'indices' in p:
				attrs['index'] = [int(v) for v in _read_accessor(j, buffers, p['indices'])]
			prim = {'attrs':attrs, 'mode':p.get('mode',TRIANGLES)}
			if 'material' in p:
				prim['material'] = p['material']
			mesh['primitives'].append(prim)
		scene['meshes'].append(mesh)

	for n in j.get('nodes',[]):
		node = {'name': n.get('name','')}
		if 'matrix' in n:
			pos,quat,scl = _decompose(n['matrix'])
		else:
			pos = tuple(n.get('translation',(0,0,0)))
			quat = tuple(n.get('rotation',(0,0,0,1)))
			scl = tuple(n.get('scale',(1,1,1)))
		node['pos'] = pos
		node['quat'] = quat
		node['rot'] = quat_to_euler(*quat)
		node['scale'] = scl
		if 'mesh' in n: node['mesh'] = n['mesh']
		if 'camera' in n: node['camera'] = n['camera']
		light = n.get('extensions',{}).get('KHR_lights_punctual',{}).get('light')
		if light is not None: node['light'] = light
		if 'children' in n: node['children'] = list(n['children'])
		if 'extras' in n: node['extras'] = n['extras']
		scene['nodes'].append(node)

	scene_idx = j.get('scene',0)
	scenes = j.get('scenes',[{'nodes':[]}])
	scene['roots'] = list(scenes[scene_idx].get('nodes',[]))

	for c in j.get('cameras',[]):
		p = c.get('perspective',{})
		scene['cameras'].append({'kind':c.get('type'),
			'fov': math.degrees(p.get('yfov',0.8)),
			'ratio': p.get('aspectRatio'),
			'near': p.get('znear',0.01), 'far': p.get('zfar',1000)})

	for l in j.get('extensions',{}).get('KHR_lights_punctual',{}).get('lights',[]):
		scene['lights'].append({'kind':l.get('type'), 'color':l.get('color',[1,1,1]),
			'intensity':l.get('intensity',1.0), 'name':l.get('name','')})

	return scene

def _decompose(m):
	"column-major 16 -> pos, quat, scale. same layout the renderer uses."
	pos = (m[12],m[13],m[14])
	sx = math.sqrt(m[0]**2 + m[1]**2 + m[2]**2)
	sy = math.sqrt(m[4]**2 + m[5]**2 + m[6]**2)
	sz = math.sqrt(m[8]**2 + m[9]**2 + m[10]**2)
	# handedness
	det = (m[0]*(m[5]*m[10]-m[6]*m[9]) - m[4]*(m[1]*m[10]-m[2]*m[9]) + m[8]*(m[1]*m[6]-m[2]*m[5]))
	if det < 0: sx = -sx
	r = [m[0]/sx,m[1]/sx,m[2]/sx, m[4]/sy,m[5]/sy,m[6]/sy, m[8]/sz,m[9]/sz,m[10]/sz]
	return pos, _mat3_to_quat(r), (sx,sy,sz)


def main():
	# tiny smoke: one triangle
	g = Gltf()
	mat = g.add_material(color=0xff8800)
	mesh = g.add_mesh({'position':[0,0,0, 1,0,0, 0,1,0], 'index':[0,1,2]}, material=mat)
	g.add_node(mesh=mesh, name='tri')
	g.save('_smoke.glb')
	s = load('_smoke.glb')
	print(s['meshes'][0]['primitives'][0]['attrs']['position'])
	import os
	os.remove('_smoke.glb')

if __name__ == '__main__':
	main()
