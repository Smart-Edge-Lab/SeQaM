import os
import sys

from ModuleManagement.DataModels.event import StartModuleEvent, StopModuleEvent
from Modules.EventOrchestrator.events_requester import EventsRequester

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Utilities.EndpointGenerator import ModuleEndpointGenerator



class EDPEventsRequester(EventsRequester):

    def __init__(self):
        super().__init__()
        self._end_point_obj_ = ModuleEndpointGenerator()


    def _get_endpoint(self, module:str, action:str) -> str:
        """
        Gets the endpoint of a certain module as in the ModuleConfig.json file

        module (str): The tname of the module, must match with the key in the file.
        action (str): The action to implement in the device. Must be included in the json file into "paths"
        
        Returns: 
        The generated endpoint
        """
        _module_ = module.lower()
        return self._end_point_obj_.generate_endpoint(module_name=_module_, module_action = action)

    def start_edp_module(self, event: StartModuleEvent):
        """
        Sends a POST request to the URL based on the name of the module to start. 

        Parameters:
        module (str): The name of the module to start.
        
        Returns: 
        The response from the server

        """
        # Send the POST request
        response = self.post(event.module, "start", event=event)

        return response

    def stop_edp_module(self, event: StopModuleEvent):
        """
        Sends a POST request to the URL based on the name of the module to stop.

        Parameters:
        module (str): The name of the module to stop.

        Returns:
        The response from the server

        """
        # Send the POST request
        response = self.post(event.module, "stop", event=event)

        return response