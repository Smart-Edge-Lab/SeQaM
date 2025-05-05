import os
import sys


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

sys.path.insert(0, ROOT_PATH)

from ModuleManagement.configuration_aware import ConfigurationAware
from ModuleManagement.DataModels.event import SshEvent
from ModuleManagement.DataModels.ssh import SshCommand
from Utilities.JsonReader import JsonReader


class ModuleEndpointGenerator(ConfigurationAware):
    """
    A class to generate module endpoints based on a configuration file.
    """

    def __init__(self):
        super().__init__()
        self._file_name_ = "ModuleConfig.json"
        self._file_path_ = os.path.join(self._home_path_, self._file_name_)
        self._reader_ = JsonReader(self._file_path_)
        self._module_data_ = self._reader_.readFile()


    def get_module_info(self, module_name:str):
        """
        Retrieves module information from the configuration file.
        
        Parameters:
            module_name (str): The name of the module.
        
        Returns:
            The module information.
        
        Raises:
            Exception: If the module is not found in the configuration file.
        """
        module_name = module_name.lower()
        if not any(module_name in module for module in self._module_data_['modules']):
            raise Exception(f"Module {module_name} not found in configuration file")
        module_info = [value for module in self._module_data_['modules'] for value in module.values() if module_name in module]
        return module_info[0]
                

    def generate_endpoint(self, module_name:str, module_action:str) -> str:
        """
        Generates a module endpoint based on the module name and action.
        
        Parameters:
            module_name (str): The name of the module.
            module_action (str): The action of the module.
        
        Returns:
            The generated endpoint URL.
        
        Raises:
            Exception: If the module or action is not found in the configuration file.
        """ 
        module_action = module_action.lower()
        module_info = self.get_module_info(module_name)
        #validate if the action exists in the module
        if not any(module_action in actions for actions in module_info["paths"]):
            raise Exception(f"Action {module_action} not found in configuration file")
        url = "http://" + self._get_endpoint_host(module_info) + ":" + str(self._get_endpoint_port(module_info)) + self._get_endpoint_path(module_info["paths"], module_action)
        return url


    def _get_endpoint_host(self, module_info: dict[str, str]) -> str:
        """
        Retrieves the host from the module information.
        
        Parameters:
            module_info (str): The module information.
        
        Returns:
            The host IP.
        """
        return module_info["host"]


    def _get_endpoint_port(self, module_info: dict[str, int]) -> int:
        """
        Retrieves the port from the module information.
        
        Parameters:
            module_info (str): The module information.
        
        Returns:
            The port of the module.
        """
        return module_info["port"]
    

    def _get_endpoint_path(self, paths: list[dict[str,dict[str,str]]], module_action: str) -> str:
        """
        Retrieves the endpoint from the module paths based on the action.
        
        Parameters:
            paths (str): The module paths.
            module_action (str): The action to be performed with the module.
        
        Returns:
            The endpoint path.
        """
        for path in paths:
            if module_action in path:
                return path[module_action]["endpoint"]
            else:
                return "/"
        return ''
                
    
    
class DistributedEndpointGenerator(ConfigurationAware):

    def __init__(self):
        super().__init__()
        self._file_name_ = "ScenarioConfig.json"
        self._file_path_ = os.path.join(self._home_path_, self._file_name_)
        self._reader_ = JsonReader(self._file_path_)
        self._component_data_ = self._reader_.readFile()


    def get_dist_component_info(self, component_type:str, component_name:str):
        """
        Retrieves component information from the ScenarioConfig file.
        
        Parameters:
            component_type (str): The type of the component.
            component_name (str): The name of the component.

        Returns:
            The module information.
        
        Raises:
            Exception: If the module is not found in the configuration file.
        """
        component_name = component_name.lower()
        component_type= component_type.lower()
        
        if not any(component_type in allowed_type for allowed_type in self._component_data_["distributed"]):
            raise Exception(f"Component type not valid")
        
        try: 
            index = [i for i, d in enumerate(self._component_data_["distributed"][component_type]) if d['name'] == component_name][0]
            return self._component_data_["distributed"][component_type][index]
        except:
            raise Exception(f"{component_type} Component with name {component_name} does not exist")
                

    def generate_endpoint(self, component_type:str, component_name:str, component_action:str) -> str:
        """
        Generates a component endpoint based on the component name and action.
        
        Parameters:
            component_type (str): The name of the component.
            component_name (str): The name of the component.
            component_action (str): The action of the component.
        
        Returns:
            The generated endpoint URL.
        
        Raises:
            Exception: If the action is not found in the configuration file.
        """ 
        component_action = component_action.lower()
        component_info = self.get_dist_component_info(component_type, component_name)
        #validate if the action exists in the component
        if not any(component_action in actions for actions in component_info["paths"]):
            raise Exception(f"Action {component_action} not found in configuration file")
        url = "http://" + self._get_endpoint_host(component_info) + ":" + str(self._get_endpoint_port(component_info)) + self._get_endpoint_path(component_info["paths"], component_action)
        return url

    def generate_ssh(self, ssh_event: SshEvent) -> SshCommand:
        """
        Generates a component ssh command based on the component name

        Parameters:
            component_type (str): The name of the component.
            component_name (str): The name of the component.

        Returns:
            The generated ssh command.
        """
        component_info = self.get_dist_component_info(ssh_event.src_device_type, ssh_event.src_device_name)
        return SshCommand(
            ssh_port=component_info.get('ssh_port') or 22,
            ssh_user=component_info['ssh_user'],
            ssh_host=self._get_endpoint_host(component_info),
            command=ssh_event.command,
        )

    def _get_endpoint_host(self, component_info: dict[str, str]) -> str:
        """
        Retrieves the host from the component information.
        
        Parameters:
            component_info (str): The component information.
        
        Returns:
            The component IP.
        """
        return component_info["host"]


    def _get_endpoint_port(self, component_info: dict[str, int]) -> int:
        """
        Retrieves the port from the component information.
        
        Parameters:
            component_info (str): The component information.
        
        Returns:
            The port of the module.
        """
        return component_info["port"]
    

    def _get_endpoint_path(self, paths: list[dict[str, dict[str, str]]], component_action: str) -> str:
        """
        Retrieves the endpoint from the module paths based on the action.
        
        Parameters:
            paths (str): The module paths.
            component_action (str): The action to be performed with the component.
        
        Returns:
            The endpoint path.
        """        
        for path in paths:
            if component_action in path:
                return path[component_action]["endpoint"]
            else:
                return "/"
        return ''
