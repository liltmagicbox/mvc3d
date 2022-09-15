
from abc import ABC, abstractmethod

class IActor(ABC):
    @abstractmethod
    def update(self,dt):
        1

class IWorld(ABC):
    #===api
    @abstractmethod
    def input(self,Event):
        print(' input-> world ', Event)
    @abstractmethod
    def update(self,dt):
        self.actors.append(2)
    @abstractmethod
    def draw(self):
        "world -> {draws,Event} -basically draw"
        
class GameMaster:
    @abstractmethod
    def x():1

class IViewControl(ABC):
    """ get_inputs -> []"""
    #===api
    @abstractmethod
    def get_inputs(self):
        "Event or raw_abskey."
        return []
    @abstractmethod
    def draw(self,draws):
        print(len(draws) )

class ISimulator(ABC):
    @abstractmethod
    def run(self):
        1
    @abstractmethod
    def pause(self):
        self._flag_pause.set()
    @abstractmethod
    def resume(self):
        self._flag_pause.clear()
    @abstractmethod
    def _stop(self):
        self._flag_stop.set()

def main():
    w = IWorld()
    print(w)

if __name__ == '__main__':
    main()