import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.PlatformModuleObject import PlatformModuleObject


class ConsoleModuleObject(PlatformModuleObject):
    """
    ConsoleModuleObject is a PlatformObject that is used to represent a console object in the console.
    """
 
    def __init__(self,  name: str):
        """
        Creates a new ConsoleModuleObject
        
        Parameters: 
        name: Name of the object
        """

        self._name = name





