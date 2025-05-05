import os
import sys
import requests  # type: ignore


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Modules.Console.ConsoleModuleObject import ConsoleModuleObject
from Modules.Console.ConsoleException import ConsoleException
from Utilities.EndpointGenerator import ModuleEndpointGenerator


class ConsoleOutput(ConsoleModuleObject):
    """
    Class representing output to the console as a form of PlatformOutput
    """

    def __init__(self, name: str):
        """
        Creates a new ConsoleOutput

        Parameters: 
        module: Owner module of this output
        name: Name of this output
        """
        super().__init__(name)
        self._endpoint_generator_ = ModuleEndpointGenerator()
        

    def execute(self, response: str):
        """
        Method for outputting to the console
        Parameters:  
        response: Message to be outputted to the console.
                         The command has to be preceded by "console".
                         For example: "console hello" prints hello.
                         If more than one argument is passed, they should be separated by spaces and will be printed in the same way
        Raises:
        ConsoleOutputException: if the command is missing arguments (no argument passed after "console")
        """
        command = response.split(" ")
        # if command[0] == "exit":  # The commands must come like "console text"
        #     try:
        #         print("exiting EDP...")
        #     except IndexError:
        #         raise ConsoleException("Error while exiting EDP")
        #print(command)

        if command[0] == "console":  # The commands must come like "console text"
            try:
                result = " ".join(command[1:])  # Grab all arguments passed and space them
                print(result)
                
            except IndexError:
                raise ConsoleException("Arguments missing for command {} to ConsoleOutput".format(response))
        else:
            try:
                url =  self._endpoint_generator_.generate_endpoint(module_name="Command_Translator", module_action="translate")
                response = self.sendRawCommand(url, response)

            except IndexError:
                raise ConsoleException("Arguments missing for command {}".format(response))


    def sendRawCommand(self, endopoint, body):

        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.post(endopoint, headers=headers, data=body.encode())

        return response
