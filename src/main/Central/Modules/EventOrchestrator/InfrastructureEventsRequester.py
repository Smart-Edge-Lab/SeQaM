import os
import sys
from fabric import Connection, Result, Config  # type: ignore

from ModuleManagement.DataModels.event import CpuLoadEvent, MemoryLoadEvent, SshEvent
from Modules.EventOrchestrator.events_requester import EventsRequester
from Utilities.EndpointGenerator import DistributedEndpointGenerator


class InfrastructureEventsRequester(EventsRequester):

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


    def requestCPULoadServer(self, event: CpuLoadEvent):
        """
        Sends a POST request to the URL based on the type of device. 

        Parameters:
        src_device_name (str): The name of the source device.
        cores (int): The number of cores where to generate the load. 0 means all.
        load (int): The amount of load to generate in each core.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """
        # Send the POST request
        response = self.post("server", event.src_device_name, "cpu_load", event=event)

        return response


    def requestCPULoadUE(self, event: CpuLoadEvent):
        """
        Sends a POST request to the URL based on the type of device. 

        Parameters:
        src_device_name (str): The name of the source device.
        cores (int): The number of cores where to generate the load. 0 means all.
        load (int): The amount of load to generate in each core.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """
        # Send the POST request
        response = self.post("ue", event.src_device_name, "cpu_load", event=event)

        return response


    def requestMemoryLoadUE(self, event: MemoryLoadEvent):
        """
        Sends a POST request to the URL based on the type of device. 

        Parameters:
        src_device_name (str): The name of the source device.
        workers (int): The number of workers used to generate the load.
        load (int): The amount of memory load to generate.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """
        # Send the POST request
        response = self.post("ue", event.src_device_name, "memory_load", event=event)

        return response
    

    def requestMemoryLoadServer(self, event: MemoryLoadEvent):
        """
        Sends a POST request to the URL based on the type of device. 

        Parameters:
        src_device_name (str): The name of the source device.
        workers (int): The number of workers used to generate the load.
        load (int): The amount of memory load to generate.
        time (str): The time the network load should be generated, ending in s,m,h second/minute/hour
        
        Returns:
        None
        """
        # Send the POST request
        response = self.post("server", event.src_device_name, "memory_load", event=event)

        return response

    def do_ssh(self, event: SshEvent) -> Result:
        ssh = self._end_point_obj_.generate_ssh(event)
        return Connection(
            host=ssh.ssh_host,
            user=ssh.ssh_user,
            port=ssh.ssh_port,
            connect_kwargs=dict(
                key_filename=[os.path.join(self._home_path_, 'ecdsa')]
            ),
        ).run(ssh.command, hide=True)
