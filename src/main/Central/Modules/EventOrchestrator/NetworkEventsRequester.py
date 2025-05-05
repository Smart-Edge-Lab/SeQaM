import os
import sys

from ModuleManagement.DataModels.event import ChangeBandwidthEvent, GenerateNetworkLoadEvent
from Modules.EventOrchestrator.events_requester import EventsRequester

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Utilities.EndpointGenerator import DistributedEndpointGenerator



class NetworkEventsRequester(EventsRequester):

    def __init__(self):
        super().__init__()
        self._end_point_obj_ = DistributedEndpointGenerator()


    def _get_endpoint(self, device_type:str, device_name:str, device_action:str) -> str:
        """
        Gets the endpoint of a certain device as declared in the ScenarioConfig.json file

        device_type (str): The type of the device.
        device_name (str): The name of the device.
        device_action (str): The action to implement in the device. Must be included in the json file into "paths"
        
        Returns: 
        The generated endpoint
        """
        return self._end_point_obj_.generate_endpoint(device_type, device_name, device_action )
    

    def requestChangeBandwidth(self, event: ChangeBandwidthEvent):
        """
        Sends a POST request to the URL based on the type of device. For emulation, it only sends to one point 
        "ntw_agent" that handles all the routers

        src_device_name (str): The name of the source device.
        interface (str): The interface of the source device.
        bandwidth (int): The new bandwidth to set.
        time (str): The time the bandwidth change should be applied, ending in s,m,h (second/minute/hour)
        
        Returns: 
        The response from the server

        """
        # Send the POST request
        response = self.post("router", "ntw_agent", "network_bandwidth", event=event)

        return response


    def requestGenerateNetworkLoad(self, event: GenerateNetworkLoadEvent):
        """
        Sends a POST request to the URL based on the type of device. For emulation, it only sends to one point 
        "ntw_agent" that handles all the routers

        src_device_name (str): The name of the source device.
        interface (str): The interface of the source device.
        network_load (int): The amount of network load to generate.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns: 
        The response from the server

        """
        # Send the POST request
        has_destination = event.dst_device_type is not None
        if has_destination:
            event.destination_host = self._end_point_obj_._get_endpoint_host(
                self._end_point_obj_.get_dist_component_info(event.dst_device_type, event.dst_device_name)
            )
        src_device_type = event.src_device_type if event.src_device_type and has_destination else "router"
        src_device_name = event.src_device_name if event.src_device_name and has_destination else "ntw_agent"
        response = self.post(src_device_type, src_device_name, "network_load", event=event)

        return response
