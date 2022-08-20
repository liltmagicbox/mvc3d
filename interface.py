from abc import ABC, abstractmethod

class ISimulator(ABC):
    def __init__(self, inputman, world, viewman):
        1
    @abstractmethod
    def run():
        1

class IInputman(ABC):
    @abstractmethod
    def get_input():
        1

class IViewman(ABC):
    @abstractmethod
    def put_draw():
        1





class IWorld(ABC):
    @abstractmethod
    def update():
        1
    @abstractmethod
    def get_draw():
        1
    @abstractmethod
    def put_input():
        1