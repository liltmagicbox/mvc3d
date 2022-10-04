
#====================== 4th resturucture
"""
obj-> stucked single Meshdict  =actor loader
gltf-> seperated multi Meshdict =actors loader
gltf-> scene parented ..? = scene loader
..but mesh_dict cannot hold world.position or parent..
huhuhu..
gltf mesh loader -> meshdict, pos ->0,0,0.
gltf  scene loader -> SceneActor.attached ..Actors. (even lights!) /for io. fine.
SceneActor can save/load itself. wonderful!!!!
be strong. not limited by ue.

1. txt, smd, obj,gltf mesh loader -> meshdict(s), matdict(s) +animdict+bonedict. /note: obj returns broken origins.

2. meshdict,matdict -> geo.mat  mat+
+ geo->weight mat->bone[idx] => ?? / animdict->Anim is freeman. bonedict->Bone=> SKMesh.bone = Bone()

3. MeshActor([geos]),SKMeshActor(geo), SpriteActor([geos]), ParticleActor([geos]), #sprite axis has no rot.

#gltf scene loader, returns SceneActor->gltf.#what bout cubemap? it blocks too much..? ->without box, wecan just Actors setter.

"""

#====4 Horse Men absmesh.
# drawactor is, what actually draws. abstracting platform.
# actor1.drawactor = #too bad, long.
# actor1.mesh = SKMesh() #think it's better.. but ....do this. thats what we wanted, very first.
# actor1.absmesh = SKMesh() -this brings question: where is 'real Mesh',then? (we don't have it!)




class Animator:
    def __init__(self):#triangle problem. lets Actor holds all, and __init__()?
        self.animDict = {}
        self.at = 0
    def set_anim(self, target,anim):#replaces anim.
        self.animDict[target] = anim
    def _update_anim(self,dt):#call intensionally. if not, update cost free.
        animt = self.at + dt
        for target,anim in self.animDict.items():
            value = anim.get(animt)#encapsulated. we don't know, but it will loop or stuck. we know the length! playsleep(3.4)
            setattr(self,target,value)
        self.at = animt
        #it it reached., do we stop anim?? statemachine maybe will notice. keep it simple. do one role.
        #inf loop, how? we assumed anim is just data./.
    #def tick(self,dt):
        #if anim.reach:#anim is general data.
        #if anim.exceeds(time):
        #if time
        # try:
        #     value = anim.get(time)
        # except:
        #     if infloop:
        #if infloop:..let anim know this!
        #just get!

#================================
class AbsMesh:
    def get_uniform_dict(self):
        return {key:actor.value for key,value in self.shaderuniformDict.items()}#love this line!          
    def set_uniform(self,key,value):
        1
    
    def set_uniform_by_dict(self,uniform_dict):
        #parse , set_vec3 kinds.
        [self.geometry.set_uniform(key,value) for key,value in uniform_dict.items()]#set uniforms.
    
    def draw(self, vpmat, modelmat, uniform_dict):
        self.geometry.draw(vpmat, modelmat, uniform_dict)# depth rule.
    def draw_instanced
        self.geometry.draw_instanced(vpmat, modelmat, uniform_dict)

    #@SKMEsh
    def draw(self, vpmat, modelmat):#we do here,finally. haha! even shared geo, can draw each actor.# no actor again.
        "instanced, uniform set if by draw_seq. absmesh binds, not here"
        mat = self.mat
        mat.bind()
        mat.set_vpmat(vpmat)
        mat.set_modelmat( actor.get_modelmat() )
        if mat.skeletal:            
        if geo.skeletal:
            mat.set_pose(actor.pose)#since pose is just attr of actor concept.
        self.vao.bind()
        self.vao.draw()
        #ignmore above. we dont need to know those.
        #self.geometry.draw_pose(vpmat, modelmat, uniform_dict, pose=self.pose)#here decides what to order. ->Geometry
        self.geometry.draw(vpmat, modelmat, uniform_dict, self.pose)#here decides what to order. ->Geometry

class StaticMesh(Animator):
    """geometry.mat"""
    def __init__(self, geometry):
        Animator.__init__(self)
        self.geometries = []
        #self.matvar = 0actor, you mean it right?
        self.instanced = False
    def draw(self, actor):
        for geometry in self.geometries:#check overhead. 80%s will be Mesh.
            geometry.draw(actor)

#https://docs.unrealengine.com/5.0/ko/geometry-script-users-guide/
class DynamicMesh(Animator):#is from ue5! and seems it's not Actor..?
    1

#??? if tree.. TreeActor all.. for draw..

def draw_seq(self):
    instanced_Dict = {}#instanced_Dict is visually great.
    absmesh_Dict = {}

    # per-draw & fill instanced dict.
    for actor in actors:
        absmesh = actor.mesh
        if not absmesh.instanced:
            absmesh.bind()
            #uniform_dict = {key:actor.value for key,value in self.shaderuniformDict.items()}#love this line!  
            uniform_dict = self.get_uniform_dict()
            #[absmesh.set_uniform(key,value) for key,value in uniform_dict.items()]#set uniforms.
            absmesh.set_uniform_by_dict(uniform_dict)
            modelmat = actor.get_modelmat()
            absmesh.draw(vpmat,modelmat)
            #better
            #bind, setuniform, draw(vp,m)
            absmesh.draw(vpmat,modelmat, uniform_dict)
        else:
            if not absmesh.name in instanced_Dict:
                instanced_Dict[absmesh.name] = {}
                absmesh_Dict[absmesh.name] = absmesh
            #instanced_Dict[absmesh.name].append( self.position )
            uniform_dict = {key:actor.value for key,value in self.shaderuniformDict.items()}#love this line!         
            #instanced_Dict[absmesh.name].append( uniform_dict )
            
            #we need axis inverted list form. { 'var1':[], 'var2':[] }
            for key,value in uniform_dict.items():
                if not key in instanced_Dict[absmesh.name]:
                    instanced_Dict[absmesh.name][key] = []
                instanced_Dict[absmesh.name][key].append( value )
    
    # instanced draw
    for absmesh_name, uniform_key_dict in instanced_Dict.items():
        #absmesh = AbsMesh.get(absmesh_name)#this seems great, but keep watch it..
        absmesh = absmesh_Dict[absmesh_name]

        absmesh.bind()#donot forgetit, since setuniform requires..
        for key,valuelist in uniform_key_dict.items():
            absmesh.set_uniform(key,valuelist)#since it's instanced, shader has var[];
        absmesh.draw(vpmat, modelmat)
        #better
        absmesh.draw_instanced(vpmat,modelmats, uniform_key_dict)#yerah draw_instanced!!!!!!!

#below acomplished.great.
#we neeed draw sequence. with actor. since actor.attr will be used. +since geo is shared.
        #draw seq.
        # for actor in actors:
        #     geo = actor.geo
        #     mat = geo.mat
        #     if geo.instanced:
        #         instanced_Dict[geo.name] = geo
        #         #or if not in , append.
        #     else:
        #         geo.draw()

#ue4, requires Material: Used with Skeletal Mesh!
class SkeletalMesh(Animator):
    def __init__(self, geo, bone):
        self.bone = None
        self.pose = None#these will animated by Animator, as like same.
        #self.animDict ={}?
    #need more anim seq,statemachine, mixer, kinds..
    def add_anim(self, anim):
        1
    def baba(self, posedata):
        pose = self.bone.transform(posedata)
        self.pose = pose
    def transform(self, posedata):
        self.bone
        return pose
    def mama(self, data):
        self.pose_data = data#not calc more, update free! if lod, it helps calc. ..notthatmuch. it's from anim/bone form..abs/rel
        #we do lod. !
        section = world.quadtree[self.id]
        #for subsection in section:
        #    if actor.id in subsection:
        #for actor in section.actors:
        #anyway set lod level -> update frequency.
        for actor in section.actors:
            if self.distance(actor)< self.radius_collision:
                self.collision_test(actor)


#lets this hgolding SM/SKM?? all easy.
#if geo, firework avector pos, color can be shader?  ..or instanced..
#class ParticleMesh(AbsMesh):#is also a absmesh.  for interface.draw(actor)

class ParticleMesh(Animator):
    """
    has AXIS kinds.
    1.Mesh. per-draw. get attr from the table
    1.Mesh. instanced, draw all with [idx].
    2.SKMesh per-draw. get attr from the table
    2.SKMesh instanced. give to bone = bones[idx] ( idx:pose or idx:idx (with shader loaded all anims!))
    3.SKMesh vertex anim. for 1000~ human.
    """
    def __init__(self):
        self.geos = []
    def draw(self):
        for geo in geos:
            if not geo.instanced:
                geo.draw(self)#-thats the one!
            else:
                append()
        for igeo in igeos:
            igeo.set(instanced_Dict)
            igeo.draw()

