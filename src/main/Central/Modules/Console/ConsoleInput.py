
import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)
print(ROOT_PATH)

from Modules.Console.ConsoleModuleObject import ConsoleModuleObject
from Modules.Console.ConsoleException import ConsoleException

class ConsoleInput(ConsoleModuleObject): 
    """
    Class representing input from the console as a form of PlatformInput
    """

    def __init__(self, name: str):
        """
        Creates a new ConsoleInput

        Parameters: 
        module: Owner module of this input
        name: Name of this input
        """
        super().__init__(name)
        self.IN = input
        print(f"ConsoleInput initialized with self.IN: {self.IN}")


    def read(self):
        """
        Method for reading from the console, blocks by terms of the underlying input function

        Returns:
        String object containing the last line inputted in the console
        """
        print("EDP >> ")
        reading = self.IN()
        if reading == "":
            raise ConsoleException("Arguments missing for command {}".format(reading))
            
        return reading



