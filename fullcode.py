"""
1.Geo, Mat is factory,  has init attr guide.  Mat.get('phong',kwargs) don't.
2. Point, Lines, SKMesh, Sprite,.. all is near 3js, not ue4.
2-2,Helper factory. same way.
3.attrs of geo,, memory back. 3js seems save all attrs, via attrs,, not fixed structure. notbad.


Geometry
Geo.cube()

Material
SpriteMaterial
(Mesh)PhongMaterial
Mat.phong(color=0xff00ff)

class Mesh(Actor)
Mesh(geo,mat)
Point(geo,mat)
Line(geo,mat)
pointcloud = Point( Geo.cube(10,10,10, 100,100,100), Mat.Sprite(texture=xxx.jpg) )

SKMesh(geo,mat,sk,poses)?

Helper.arrow( (0,0,0), (1,1,1) )
Helper.axis(0,0,0)

morphtarget..

obj/smd/gltf loader
dict structure required.
attrname, stride, array.

"""

DEFAULT_COLOR = 0x888888

class Mat:
	"""factory of Material(args) -> SubClass(Material)"""
	@classmethod
	def phong(cls, **kwargs):
		1
	def basic(cls, color=DEFAULT_COLOR ):
		return BasicMaterial(color)
	def lambert(cls):
		1
	def pbr(cls):
		1

class Geo:
	"""factory of Geometry.. actually -> Geometry"""
	@classmethod
	def cube(cls):
		1
	def cylender(cls):
		1
	def sphere(cls):
		1
	def cone(cls):
		points = 1
		faces = 1
		return Geometry(points,faces)
	def honeycomb(cls):
		1
	#hexa

class Mesh:
	1

class ArrowHelper(Mesh):
	def __init__(self, begin,end):
		self.begin = begin
		self.end = end

		Geo.cone()# == Geometry(xxxx...)
		Geo.cylinder()
		Mat.basic(color='red') # == MeshDefaultMaterial(color='red')


class AxisHelper(Mesh):
	1


class Helper:
	"""factory of Mesh"""
	@classmethod
	#def arrow(cls, **kwargs):#this forgets what requird init!
	def arrow(cls, begin,end):
		return Arrow(begin,end)
	def axis(cls):
		1

#1.loader parse, formats attr. normal,phong,pbr..
#2.customshader, mat, requires certain attr, user knows it.
#3.toJSON is just save attrs. as like 3js.
#phong, has color,pos,normal,specular,, and if hit, shader will use it.simple.


#Point(geo,PointsMaterial())

class Geometry:
	def __init__(self, position=None, face=None, **kwargs):
		"""position, face, normal, uv, weight ... all via format"""
		self.attrs = {}
		
		position = [] if not position else position
		face = [] if not face else face
		self.position = position
		self.face = face

		for key,value in kwargs.items():
			setattr(self, key,value)

		
	#fixed form. access custom via attrs.
	def get(self, attr):
		return self.attrs.get(attr,[])
	def set(self, attr,value):
		#set('position',3,value)https://threejs.org/docs/#api/en/materials/PointsMaterial
		#avobe is for gpu. we don't do this here!ha! as py, we know what we do!
		#if attr in self.attrs:
		self.attrs[attr] = value
	@property
	def position(self):
		return self.get('position')
	@position.setter
	def position(self, value):
		self.set('position',value)
	@property
	def face(self):
		return self.get('face')
	@face.setter
	def face(self, value):
		self.set('face',value)
	@property
	def normal(self):
		return self.get('normal')
	@normal.setter
	def normal(self, value):
		self.set('normal',value)
	
	@property
	def uv(self):
		return self.get('uv')
	@uv.setter
	def uv(self, value):
		self.set('uv',value)
	
		#uvcoords1
		#{'uv1'}
		#normals
		#weights
		#colors
		#..coords.finally.
		#smd, xyz nxnynz, u,v, w1234
		#each point has own data.

	def calc_normal(self):
		1

	def export_normalmap(self):#via instructed seam, maybe unfold..
		1
	def merge(self,other):
		1

	def toJSON(self):
		ddict = {}
		ddict['metadata'] = {'version':0.1,'type':'BufferGeometry','generator':'BufferGeometry.toJSON'}
		
		ddict['uuid'] = self.uuid
		ddict['type'] = self.type		
		if self.name:
			ddict['name'] = self.name
		#ddict['name'] = self.name if self.name else None
		#self.userData
		#self.parameters

		ddict['data']={}

		#https://stackoverflow.com/questions/25150955/python-iterating-through-object-attributes
		#for key,value in self.attr():
		#for key,value in self.__dict__.items():
		#for key,value in vars(self).items()
		for key,value in self.attributes.items():
			ddict['data'][key] = value



#https://threejs.org/docs/#api/en/core/BufferGeometry
# class PointGeometry(Geometry):
# 	1
# class LineGeometry(Geometry):
# 	1


data = {
	'position': [],#3
	'normals': [],#3
	'uvcoords': (0.0, 0.125),#2
	'weights': (0,1.0, 1,0.0),#2-4.. ofcourse fixed in samefile.
	
	'color':[],
	'uv2':[]
}

class objloader:
	@classmethod
	def load(cls, fdir):
		ddict = {}
		if position:
			position
		if normal:
			1


#Mesh
#same geo, diff mat, drawn..
#..maybe via mat. mat has draw type..?


class BufferGeometry:
	def __init__(self):
		self.attributes = {}
	@property
	def position(self):
		return self.attributes['position']
	@position.setter
	def position(self,value):
		self.attributes['position'] = value
	#or
	def setAttr(self, location, data):
		self.attributes[location] = data
	
	@classmethod
	def test(cls):
		vertices = [ [0,0,0,],[1,0,0,],[0,1,0]]
		
		#geo = BufferGeometry()#is gpu ready form. we don't need it..
		#geo.position = vertices
		#geo.setattr('position', BufferAttribute(vertices,3) )#threejs style
		#mat = BasicMaterial()

		return Mesh(geo,mat)
	
	def toJSON(self):
		ddict = {}
		ddict['metadata'] = {'version':0.1,'type':'BufferGeometry','generator':'BufferGeometry.toJSON'}
		
		ddict['uuid'] = self.uuid
		ddict['type'] = self.type		
		if self.name:
			ddict['name'] = self.name
		#ddict['name'] = self.name if self.name else None
		#self.userData
		#self.parameters

		ddict['data']={}

		#https://stackoverflow.com/questions/25150955/python-iterating-through-object-attributes
		#for key,value in self.attr():
		#for key,value in self.__dict__.items():
		#for key,value in vars(self).items()
		for key,value in self.attributes.items():
			ddict['data'][key] = value


class Material:
	def __init__(self):
		self.visible = True
		self.lineWidth=1
		self.pointSize=1
		self.wireframe=False


class BasicMaterial(Material):
	1

#SpriteMaterial()#too long
#Mat.get('sprite')#not..bad,, but requires remember.
#Mat.Sprite()#method too vary
#Mat.factory.sprite()


#MeshMaterial

pv = [
[0,0,0],
[1,0,0],
[2,0,0],
]
#for p in pv:
#	geo.position.extend(p)

#Points(geo, SpriteMat())

class PointsMaterial:
	1

class ShaderMaterial:
	1

class SpriteMaterial:
	1

class Actor:
	1

class Mesh(Actor):
	def __init__(self, geo=None,mat=None):
		super().__init__()
		if geo==None:
			geo = Geometry.default()
		self.geo = geo
		self.mat = mat

class Points(Mesh):
	1
class Lines(Mesh):
	1


class SKMesh(Mesh):
	def __init__(self):
		self.skeletal = None
	def update(self,dt):
		1
	def frame(self,frame):
		self.skeletal[frame]


# class PointCloud:
# 	"""axis calculated"""
# 	def __init__(self):
# 		1


# class Sprite(Actor):
# 	def __init__(self):
# 		1


