from abc import ABC, abstractmethod

class SingletonInterface(ABC):
    _instance = None

    @staticmethod
    @abstractmethod
    def get_instance():
        if SingletonInterface._instance is None:
            SingletonInterface._instance = SingletonInterface()
        return SingletonInterface._instance

    @abstractmethod
    def __init__(self):
        if SingletonInterface._instance is not None:
            raise Exception("Singleton: there can only be one object")
        else:
            self.name = ""