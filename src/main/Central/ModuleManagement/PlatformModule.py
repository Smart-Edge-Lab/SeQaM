from abc import ABC, abstractmethod

class PlatformModule(ABC):
    """
    Abstract class to define platform modules structure
    """

    @abstractmethod
    def make_sound(self):
        """
        Abstract method for making a sound
        """
        pass

    @abstractmethod
    def move(self):
        """
        Abstract method for movement
        """
        pass