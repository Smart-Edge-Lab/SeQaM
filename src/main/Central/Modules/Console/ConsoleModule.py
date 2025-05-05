import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from  Modules.Console.ConsoleInput import ConsoleInput
from  Modules.Console.ConsoleOutput import ConsoleOutput


class ConsoleModule():
    """
    PlatformModule that adds user interacting functionality to the platform.

    The console module provides the necessary inputs and outputs to interact with the console (terminal),
    which means reading from standard input and printing to the standard output.
    """

    def __init__(self):
        """
        Create a new console module. The module created is not initialized and cannot be used until it is explicitly 
        configured
        """
        

    def configure(self, **kwargs):
        """
        Configures the module based on the provided keyword arguments.
        """
        for key, value in kwargs.items():
            if key == "_name":
                self._name = value
            elif key == "_input":
                self._input = ConsoleInput(value)
            elif key == "_output":
                self._output = ConsoleOutput(value)
            else:
                raise ValueError(f"Unknown keyword argument: {key}")





if __name__ == "__main__":
    console = ConsoleModule()
    console.configure(_name = "console", _input = "console.in", _output = "console.out")

    while (True):

        command = console._input.read()
        console._output.execute(command)
        
        if command == "exit":
            break
