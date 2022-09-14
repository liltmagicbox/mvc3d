from interface import IViewControl
from queuerecv import QueueOnRecv

class Nexus(IViewControl):
    def __init__(self, N):
        
        #===input
        def input_to_sim(inputdict):
            world_id = inputdict.world
            if world_id in self.simulatorDict:
                simworld = self.simulatorDict[world_id]
                #simworld.input(inputdict)#we cant..
                simworld.input(inputdict)#no, we can. LocalSimulator().
        self.input_queue = QueueOnRecv(on_recv = input_to_sim)
        #input done.

        #===output.
        for sim in self.simulatorDict.values():
            events = sim.output()
            for event in events:
                input_to_sim(event)
            
            draws = sim.draw()
            self.caster.cast(draws)
            #self.draw_update(draws)
            
            #really bad actor near draws getter.
            #the system designed originally: giva all draws , to every viewer.
            # for i in self.viewers:
            #     i.id
            # "each viewer, control target( of global simworld's position)"
            # simworld = self.simulatorDict.get(viewer.id)
            # actorid = simworld.get_actor_id(viewer.id)            
            # actor = self.draws.get_actor(actorid)
            # coord = actor.pos
            # self.get_draws(coord)


        
        #for i in range(N):
        s1 = SocketSimulator(port1)
        s2 = SocketSimulator(port2)

        self.queue = QueueRecv(verbose=True)
        self.caster = Caster(verbose=True)

        self.simulators = {}
        #player -> simulator dict??

    def run(self):
        self.queue.get_all()
    
    def distribute(self):
        for sim in self.simulators:
            if event.player in sim:
                sim.input(event)


    #===api
    def get_inputs(self):
        return [i for i in self.queue.get_all()]
    def draw(self,draws):
        real_draws = draws.get('draws')
        self.caster.cast(real_draws)

class Nexus2(IViewControl):
    def __init__(self):
        s1 = Simulator()
        s2 = Simulator()
        self.simulators = [s1,s2]

# s1 = Simulator()
# s1.run()
# s2 = Simulator()
# s2.run()

# nexus_input = QueueRecv()

# sender = Sender(port = 5595)
def run(self):
    while True:
        dict_event = queue.get()#halt here

        world_id = dict_event.get('world')
        #for sim in simulators:
        #    if world_id == sim.world.id:
        sim = simDict.get(world_id)#{worldid:simulator}

        #sim.input(dict_event)
        #sim.view_control
        #sim_viewer_attached(5595)
        sender.send(dict_event)


#Nexus
#s1 = SocketSimView(port=5595)
#s2 = SocketSimView(port=5596)
#sender1 = Sender(5595)
#sender2 = Sender(5596)

#