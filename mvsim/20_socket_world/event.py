

class Event:
    def __repr__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"

class Lambda(Event):
    def __init__(self, *data):
        self.data = data

class Key(Event):
    def __init__(self, key,value,time=None):
        self.key = key
        self.value = value
        self.time = time











#=======================
#let Events not below this line.
VARS = vars()

def parse(_clsname_datalist):
    for class_name, value_packed in _clsname_datalist.items():        
        class_found = VARS.get(class_name, Lambda)
        #vars locals searching inside of func get..
        return class_found(*value_packed)


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


def _eventtest():
    a = Key('a',1.0)
    a = Key('a',1.0, 9949)

    data = 'a',1.0, None
    a = Key(*data)
    print(a)

    x = parse( {'Key': ['x',0.5] } )
    print(x)

def main():
    _eventtest()

if __name__ == '__main__':
    main()


#+===========================
#history




#=========================
#===key Evnet class discussion.
def input_to_event(i):

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
