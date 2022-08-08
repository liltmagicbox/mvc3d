
#three.js similar, but not that. fastest targeted. not position, but pos.
#z alwayse up. use -xy methods:like v = Vec3.xy(x,y) ..2d was not proper name..

class Posable:
    def __init__(self):
        self.id = 1
        self._pos = IDVec3(0,0,0, self.id)
        self._rot = IDVec3(0,0,0, self.id)
        self._scale = IDVec3(0,0,0, self.id)
    
    @property
    def pos(self):
        return self._pos
    @property
    def rot(self):
        return self._rot
    @property
    def scale(self):
        return self._scale

class Object3D:
    def __init__(self):
        self.children = []
    def add(self, child):
        self.children.append(child)


class Group(Object3D):
    1





exit()


#camera = three.PerspectiveCamera(70, 640 / 480, 0.01, 100)
camera.position.z = 1

scene = three.Scene()

geometry = three.BoxGeometry(0.2, 0.2, 0.2)
material = three.MeshNormalMaterial()

mesh = three.Mesh(geometry, material)

mesh2 = three.Mesh(geometry, material)
mesh2.position.x+=0.5
mesh.add(mesh2)

scene.add(mesh)

mesh.rotation.x += 0.01
mesh.rotation.y += 0.02



#======================================

class Camera:
    def __init__(self):
        self.orthographic = False
        self.position = Vec3(5,5,5)
        self.fov = 60
#========

#https://sbcode.net/threejs/object-hierarchy/

#THREE.MeshPhongMaterial({ color: 0x0000ff })
obejct3 = Mesh(SphereGeometry(), MeshPhongMaterial(color= 0x0000ff) )

#object3.position.set(4, 0, 0)
#object2.add(object3)
#object3.add(new THREE.AxesHelper(5))
object3.pos = 4,0,0#somewho weird. py naturaly will overwrite the attr!
object3.pos.set(4,0,0)
object3.add(AxisHelper(5))


# window.addEventListener('resize', onWindowResize, false)
# function onWindowResize() {
#     camera.aspect = window.innerWidth / window.innerHeight
#     camera.updateProjectionMatrix()
#     renderer.setSize(window.innerWidth, window.innerHeight)
#     render()
# }

# const light1 = new THREE.PointLight()
# light1.position.set(10, 10, 10)
# scene.add(light1)

light1 = PointLight()
light1.pos.set(10,10,10)
light1.pos = 10,10,10#i like it anyway!
scene.add(light1)



# const camera = new THREE.PerspectiveCamera(
#     75,
#     window.innerWidth / window.innerHeight,
#     0.1,
#     1000
# )

camera = PerspectiveCamera(fov=75, ratio= window.innerWidth/window.innerHeight, near=0.1,far=1000)
camera.pos.x = 4

#const controls = new OrbitControls(camera, renderer.domElement)
#controls.target.set(8, 0, 0)
controls = OrbitControls(camera, renderer.domElement)
controls.target.set(8, 0, 0)
controls.target = (8, 0, 0)
#if this is vector, we need eachtime, @property settings.. too bad.
#=lets not change vector attr of object. since it requires ID, and not all property settings.(too bad, really!)








#========================pos war. set,set2d,get2d is, while actor.pos=(3,3,3) works.
class Object:
    def __init__(self):
        self.pos = Vec3(0,0,0)

player.pos = Vec2d(5,2)
player.pos.set(5,0,2)
player.pos.set2d(5,2)#thats the one!

x,y,z = player.pos
x,y,z = player.pos.get()#too,too bad.. or not that bad?
x,y = player.pos.get2d()

#what shouldn't happen scenario:
pos = player.pos
pos+=(1,0,0)
player2.pos = pos

class Object:
    _vec3_attrs = set('pos','rot','scale')#x in list O(N)
class Camera(Object):
    _vec3_attrs = set('target')#x in list O(N)
#i dont wanna this..


#this, was not that good way.
#or lets just do this, one time, please??
class Object:
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        #self._pos = Vec3(*value)
        self._pos.set(value)#exquisite!

    
class Camera(Object):
    @property
    def target(self):
        return self._target
    @target.setter
    def target(self,value):
        self._target.set(value)
#not that bad, we do, with pythonic way.
#it prevents if one trying to replace the attr. thats all!


#gui = Gui()
#object1Folder = gui.addFolder('Object1')
#object1Folder.add(object1.pos, 'x', 0,10, 0.01).name('X Position') #assume it returns..

#-what we used to way..bad.
#item = object1Folder.Item(object1.pos, 'x', 0,10, 0.01)
#item.name('X Position')
#object1Folder.add(item)


#===it works!
# class Item:
#     def __init__(self):
#         self.name = 'noname'
# class Folder:
#     def add(self,*args):
#         return Item()

# object1Folder = Folder()
# object1Folder.add('pos', 'x', 0,10, 0.01).name = 'X Position'
#===but seems not pythonic..


#object1Folder.add(object1.pos, 'x', 0,10, 0.01)
#object1Folder[0].name = 'X Position'
#lets do this.
#or just really copy of js. anyway we need 2 lines!


#gui = Gui()
#object1Folder = gui.addFolder('Object1')
#object1Folder.add(object1.pos, 'x', 0,10, 0.01).name = 'X Position'
#object1Folder.add(object1.pos.x, 0,10, 0.01).name = 'X Position'
#this cannot be ..in ue4.

#we need 'HUD'
#and 'Controls' ..just hud.
#or just Panel, as we tried. ControlPanel

obj.pos
obj.rot
obj.quat
obj.scale
#const objectsWorldQuaternion = new THREE.Quaternion()
#object.getWorldQuaternion(objectsWorldQuaternion)

objWorldQuat = object.quat

pos = player.pos# returns copy of.
#pos = player.pos.copy()
pos+=(1,0,0)#this will change player.pos.
player2.pos = pos#get value from.
#player.pos.x=5 #this requires return original vector.
player2.pos = player.pos+(1,0,0)
player2.pos = player.pos#safe.fine.






#+==
#https://www.ursinaengine.org/platformer_tutorial.html
#ground = Entity(model='quad', scale_x=10, collider='box', color=color.black)#this seemslike using kwargs=>setattr..
ground = Mesh(geo=CubeGeometry())
ground.mat.color=COLOR.black#KEY.k

#idial way:
ground = Cube()
ground.scale.x=10
ground.color = color.black
ground.collider = collider.box
#or

#ground = Cube(collider = 'box', color=color.black, scale.x=10)#scale.x error. ..ah thats why..
#geometry has collider, since actor=mesh..


#...feels we need holding 4x4,global. so that we use collider.



