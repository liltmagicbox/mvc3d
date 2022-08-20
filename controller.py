
class Controller:
    def __init__(self):
        self.keymap = {}
    def parse(self, functext):
        if '*' in functext:            
            funcname,multext = functext.split('*')
            mul = float(multext)

        else:
            funcname = functext
            func = getattr(self, funcname,lambda x:1)
            func()
    
    def input_key(self, key,value):
        if key in self.keymap:
            functext = self.keymap[key]
            self.parse(functext)






class FPSController:
    def __init__(self):
        self.keymap = {
        'w':'move_up*1',
        's':'move_up*-1.0',
        'd':'move_right*1.0',
        'a':'move_right*-1.0',
        'q':'turn*-1',
        'e':'turn*1',
        
        #'M_X':'look*1',
        #"M_Y":'look*1',
        "M_XY":'look*1',
        
        'J_LX':'move*1',
        'J_L1':'jump',
        }
        #'L1 L2 L3 DPAD(UP DOWN LEFT RIGHT) LX RY ABXY'#LSTICK TOO LONG
        #esc ctrl pagedown pageup insert delete home up down left right f11 space tap lshift rshift * - =
        #num1 num0 num. num+ num/
        #M_XY??? M_DX M_DXDY???

class FPSControlled:
    def move():1
    def turn():1
    def look():1

class Gunman:
    def move(self, value):
        1
    def turn(self):
        1
    def look(self,x,y):
        1

controller = FPSController()
gunman = Gunman()
controller.target = gunman