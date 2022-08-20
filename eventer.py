
class Event:
    def __init__(self, type, target=None):
        self.type = type
        self.target = target

class MouseEvent(Event):
    #https://www.w3.org/TR/uievents/#mouseevent
    def __init__(self, type,clientX,clientY,target=None):
        super().__init__(type,target)
        self.cilentX = clientX
        self.cilentY = clientY


class EventDispatcher:
    #https://ko.javascript.info/dispatch-events
    def addEventL(self, type):
        print(type)
    def removeEventL(self):
        1
    def dispatchEvent(self, event):
        1

def ma(event):
    print(event.target.id)

# button.addEventL('click',ma)
# document.addEventL('click',ma)
# window.addEventL('click',ma)
# world.addEventL('click',ma)

class World(EventDispatcher):
    def __init__(self):
        self.listeners = {}

a = Actor()
#a.addEventL('keydown',a.jump)
# a.keymap = {'j',a.jump}
# a.keymap = {'j','jump'}
# a.keymap = {'s','jump*-0.1'}
# a.keymap = {'J_down','jump*-0.1'}



#AxisInput()

#EventJump
def Jump(self):
    1
a.Jump= Jump




class EventTarget:
    def addEvent(type, listner, once_capture_passive):
        1
    def removeEvent():
        1
    def dispatchEvent():
        1
    def eventHandle(event):
        if event.type== 'fullscreenchange':
            1
        if evnet.type=='click':
            1
        if event.type == 'keydown':
            if event.key=='k':
                1

#{'k':self.jump}
keymap = {
    'k':'jump',
    'w':'move_forward*1.0'
}
