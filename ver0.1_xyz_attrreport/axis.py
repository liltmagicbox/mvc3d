import numpy as np

class AXIS:
    def __init__(self):
        row = modelN
        column = attributes
        self.array = np.zeros(column*row).reshape(column,row).astype('float32')
    def add(self, actor):
        #ID pos spd acc rpos rspd racc
        data = [actor.id, actor.pos, actor.speed, actor.acc, actor.rotpos, actor.rotspeed, actor.rotacc ]
        b = np.array(data)
        np.hstack( [self.array , b.reshape(-1,1)] )


# class Actor:
#     def __init__(self):
#         self.pos = 3
#         self.speed=3
#         self.acc=3
#         self.apos = 3
#         self.aspeed=3
#         self.aacc=3
#         self.scale = 3
# a=  Actor()
# print(dir(a))


# class Actor:
#     def __init__(self):
#         self.pos = 3
#         self.speed=3
#         self.acc=3
#         self.rot = 3
#         self.rotspeed=3
#         self.rotacc=3
#         self.scale = 3
# a=  Actor()
# print(dir(a))

class Actorarray_with_comment:
    def __init__(self, modelN):
        attributes = 30# slicing takes time.
        #assert attributes >=10,"attrs more than 10."
        row = modelN
        column = attributes
        self.array = np.zeros(column*row).reshape(column,row).astype('float32')
        #shape = (attrs,N) it's fast ~10x.
        #id0 id1 id2 id3...
        #x0 x1 x2 x3...
        #y0 y1 y2 y3...
        #z0 z1 z2 z3...
        #self.intarray = np.zeros(column*row).reshape(column,row).astype('int32')
        
        row = 16
        self.gpumodelmat = np.zeros(column*row).reshape(column,row).astype('float32')
        # col.major modelmat shape = (N,16) [ [x0,x4,x8,x12,x1,,,], [x0,x4,x8,x12,x1,,,] ,,, ]



        #index setting.
        #self.id= np.index_exp[0,:]
        #self.id= np.index_exp[0]
        #np.index_exp == (slice(1, 4, None),) <class 'tuple'> ,,, a[slice(4,7)] == a[4:7]
        #you can use simply: slice(a,b), for a[a:b], instead of :np.index_exp[a:b]
        
        self.IDX = 0

        self.posx = 1 #by doing so, it seems like attr, not idx.
        self.posy = 2
        self.posz = 3
        self.pos = np.index_exp[1:4]
        self.speedx = 4
        self.speedy = 5
        self.speedz = 6
        self.speed = np.index_exp[4:7]
        self.accx = 7
        self.accy = 8
        self.accz = 9
        self.acc = np.index_exp[7:10]

        self.rposupdate = 10 #since a dot don't rotate..
        self.rposx = 11
        self.rposy = 12
        self.rposz = 13
        self.rpos = np.index_exp[11:14]
        self.rspeedx = 14
        self.rspeedy = 15
        self.rspeedz = 16
        self.rspeed = np.index_exp[14:17]
        self.raccx = 17
        self.raccy = 18
        self.raccz = 19
        self.racc = np.index_exp[17:20]

        #----post attr value setting. this,,slice slower, since row major grabs all continueous memory.
        #such 'hashing' delays too much.

        #self.array[self.posupdate] = 1 #1 faster than 1.0
        #self.array[self.rposupdate] = 0
        #self.intarray[self.posupdate] = 1 #float faster than int

        #self.scale = 20
        self.scalex = 21
        self.scaley = 22
        self.scalez = 23
        self.scale = np.index_exp[21:24]

        # we don store it . keep it simple
        #finally quat!
        #self.quatx = 24
        #self.quaty = 25
        #self.quatz = 26
        #self.quatw = 27
        #self.quat = np.index_exp[24:28]

        #front. c++ style oop. update with your intention.
        self.frontx = 31
        self.fronty = 32
        self.frontz = 33
        self.front = np.index_exp[31:34]
        # self.upx = 34
        # self.upy = 35
        # self.upz = 36
        # self.up = np.index_exp[34:37]
        # self.rightx = 37
        # self.righty = 38
        # self.rightz = 39
        # self.right = np.index_exp[37:40]
        


    def update(self,dt):
        self.update_location(dt)
        self.update_rotation(dt)

    def update_location(self,dt):
        pos = self.array[self.pos]
        speed = self.array[self.speed]
        acc = self.array[self.acc]
        pos,speed = axis3_posspeed(pos,speed,acc,dt)
        #pos = ufunc_pos(pos,speed,dt)        

    #@profile
    def update_rotation(self,dt):
        pos = self.array[self.rpos]
        speed = self.array[self.rspeed]
        acc = self.array[self.racc]        
        pos,speed = axis3_posspeed(pos,speed,acc,dt)
        #pos = ufunc_pos(pos,speed,dt)

    
    #--- not such way..
    def xxxcalc_quat(self):
        pos = self.array[self.pos]
        rot = self.array[self.rpos]
        scale = self.array[self.scale]
        self.array[self.quat] = ufunc_quat(pos,rot,scale) #input 3,3,1. output 4.

    def xxxcalc_modelmat(self):
        quatx = self.array[self.quatx]
        quaty = self.array[self.quaty]
        quatz = self.array[self.quatz]
        quatw = self.array[self.quatw]        
        self.gpumodelmat = ufunc_modelmat(quatx,quaty,quatz,quatw) #input 4 output 16..of row.



def test_actorarray():

    a=Actorarray_with_comment(100_0000)

    NN = a.array.shape[1]
    a.array[a.accx] = np.random.rand(NN)
    a.array[a.posupdate] = np.random.rand(NN)>0.5
    a.intarray[a.posupdate] = np.random.rand(NN)>0.5
    a.array[a.raccx] = np.random.rand(NN)

    a.update_location(0.1)
    a.update_rotation(0.1)
    print(a.array)

    from time import time

    t = time()
    for i in range(99999999):
        a.update(0.01)
        if time()-t>1.0:
            break
    print(i,NN,'complexed location') #62fps pos+rot 217withjit..huh? jit18fps 10M..slow!
    # 3x for .. rom maxsleed,already..

#test_actorarray()