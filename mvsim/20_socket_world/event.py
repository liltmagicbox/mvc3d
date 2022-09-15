

class Event:
    __slots__ = ['player','world','target']
    def __init__(self, player=None, world=None, target=None):
        self.player = player
        self.world = world
        self.target = target
    
    def __repr__(self):
        clsname = self.__class__.__name__        
        attrs = {}
        attrnames = [i for i in dir(self) if '__' not in i]        
        for attr in attrnames:            
            value = getattr(self,attr)
            attrs[attr] = value
        return f"Event {clsname}: {attrs}"


class Lambda(Event):
    def __init__(self, *data):
        self.data = data

#from Controller dict, 'key':['key',value, 'player',time]
class Key(Event):
    """Key means, Generalized Key Input! """
    __slots__ = ['key','value','time']
    #def __init__(self, key,value, time=None,  player=None, target=None, world=None):
    def __init__(self, key,value, player=None, time=None, **kwargs):#kwargs for Event class(freq.changed maybe)
        self.key = key
        self.value = value
        self.time = time#good for debug
        Event.__init__(self, **kwargs)        
        self.player = player#finally! after Event.


def _keymaketset():
    e = Key('k',1.0, 'player1', '12:05' )
    print(' keymake test',e)
    e = Key('k',1.0, world=55)
    print(' keymake test',e)



#=======================
#let Events not cross this line.
_VARS = vars()

def parse(clsname_datalist) -> list:
    """returns events. Key ***XY -> [***X,***Y] """
    if isinstance(clsname_datalist,Event):
        return [clsname_datalist]
    events = []
    for class_name, value_packed in clsname_datalist.items():
        class_found = _VARS.get(class_name, Lambda)

        if isinstance(value_packed,dict):
            event =class_found(**value_packed)
        else:
            event =class_found(*value_packed)
        events.append(event)
        #===keyinput xy parse
        if class_found == Key:
            events.extend( _parse_axis(event) )
    return events

#{ 'Key': ['M_XY', (340,240), round(time.time()%10,3) ] }#fromjs
#{'key': 'M_XY', 'time': 4.592, 'value': [340, 240]}#parsed

def _parse_axis(event):
    #move_forward by Lstick. J_LXY
    if 'XY' in event.key:
        front,end = event.key.split('XY')
        if not end:# 'M_',''
            X,Y = event.value
            e = Key(front+'X',X)
            e2 = Key(front+'Y',Y)
            return [e,e2]
    return []
 # input-> world  Event Key: {'key': 'M_XY', 'time': 1.093, 'value': [340, 240]}
 # input-> world  Event Key: {'key': 'M_X', 'time': None, 'value': 340}
 # input-> world  Event Key: {'key': 'M_Y', 'time': None, 'value': 240}

#=======================

def _keyparsetest():
    es = parse(  { 'Key': ['k', 1.0, 'ttt'] } )
    print(' ham', es)
    es = parse(  { 'Key': {'key':'k', 'value':1.0, 'world':'wow'} } )
    print(' ham', es)




def _eventtest():
    a = Key('a',1.0)
    #a = Key('a',1.0, 9949)

    #data = 'a',1.0, None
    data = 'a',1.0
    a = Key(*data)
    print(a)

    x = parse( {'Key': ['x',0.5] } )
    print(x)

def main():
    _eventtest()

if __name__ == '__main__':
    main()

#=====================================================================































#+===========================
#history




def _vars_spdtest():
    import time
    t = time.time()
    vv=vars()
    for i in range(100000):
        #a = vars().get('Key')
        a = vv.get('Key')
    print(time.time()-t)

    #10ms for 100k vars().get()
    #2ms for 100k
    #6ms v=vars() prepared.
    #but the position. 1st line, all after will not be..


#if hasattr(value_packed,'__iter__') #don't do this, let input be prepared.









#=========================
#===key Evnet class discussion.
def _input_to_event(i):

    finder_events = [
    ('abskey',EKey),
    ]
    #if 'abskey' in i:
    finder_events

{'abskey': 'k', 'value': 1.0, 'time': 4.538}

# {   type:
#     key:
#     value: }

# {   type:
#     value1:
#     value2: }

# {   type:
#     datatuple: }

{'type':'EKey', 'data': ['k',1.0,4.583]}#it requires time, maybe?? seems fixed..

{'Ekey':['k',1.0,4.858]}#more less data. 1/2 !

{'Ekey1.0':['k',1.0]}
{'Ekey1.1':['k',1.0,4.858]}
#version has info of parse..?
{'Ekey/kvt':['k',1.0,4.858]} #key value time .. seemd not that good.

{'Ekey':['k',1.0,None,'future']}#finally.
#'{"key":null}' is from js.
#>>> json.loads('{"key":null}')
#{'key': None}
#fine,fine,fine.

#===key Evnet class discussion.
#=========================















class _oldbad_Event:
    def __repr__(self):
        clsname = self.__class__.__name__
        
        # dict or slots. inherit one using slots will fail this.
        # attrs = self.__dict__        
        # if hasattr(self,'__slots__'):
        #    slotattrs = { i:getattr(self,i) for i in self.__slots__ }
        #    attrs.update(slotattrs)
        
        #final stable form
        attrs = [i for i in dir(self) if '__' not in i]
        
        return f"Event {clsname}: {attrs}"
        #below sacrificed. too big if branch.
        # if hasattr(self,'__slots__'):
        #     attrs = { i:getattr(self,i) for i in self.__slots__ }
        #     return f"Event {self.__class__.__name__}: {attrs}"#vars seems using dict.
        # return f"Event {self.__class__.__name__}: {self.__dict__}"#not working with slots.

class _Key_slots(Event):    
    __slots__ = ['key','value','time']
    def __init__(self, key,value,time=None):
        self.key = key
        self.value = value
        self.time = time

class _Key_slots_inherited(Key):
    """wecannot find just dict or slots. we finally :'__' not in dir(self)"""
    __slots__ = ['height']
    def __init__(self,key,value,height):
        super().__init__(key,value)
        self.height = height

#print(Key2(1,2,8764), dir(Key2(1,2,8764)), Key2(1,2,8764).__dict__, )
#print(Key2(1,2,8764))
#attrs = [i for i in dir(self) if '__' not in i]

# class Point3D(Point2D):
#     __slots__ = ('z',)

#     def __init__(self, x, y, z):
#         super().__init__(x, y)
#         self.z = z










def _old_parse(_clsname_datalist) -> Event:
    for class_name, value_packed in _clsname_datalist.items():        
        class_found = VARS.get(class_name, Lambda)
        #vars locals searching inside of func get..
        return class_found(*value_packed)



def _split_test():
    import timefor
    def ff():
        'mus' in 'maximus'
    timefor.run(ff)

    def ff():
        'maximus'.endswith('mus')
    timefor.run(ff)

    def ff():
        'maximus'[-3:] == 'mus'
    timefor.run(ff)
    #0.004645099999999999
    0.006392600000000002
    0.011521799999999999
    0.0100774


    def ff():
        'maxi_mus'.split('_')
    timefor.run(ff)
    def ff():
        'maxi_mus'.replace('mus','mu')
    timefor.run(ff)
    0.013179200000000002 
    0.012057600000000002 

    #a in b is fast. and index accessing is whatever,.


#move_forward by Lstick. J_LXY
def _doweneedtostore_parse_axis(event):
    #i'm tired, don't do this and nethier stuck here.
    #device,axis = event.key.split('_')
    #we have limited kinds, so let it be case-by-case.!
    #below is skilled result!
    if 'XY' in event.key:
        front,end = event.key.split('XY')
        if not end:# 'M_',''
            X,Y = event.value
            e = Key(front+'X',X)
            e2 = Key(front+'Y',Y)
            return [e,e2]
    return []
 # input-> world  Event Key: {'key': 'M_XY', 'time': 1.093, 'value': [340, 240]}
 # input-> world  Event Key: {'key': 'M_X', 'time': None, 'value': 340}
 # input-> world  Event Key: {'key': 'M_Y', 'time': None, 'value': 240}
