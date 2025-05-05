import os
import sys

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)
from ModuleManagement.PlatformModuleSingletonObject import SingletonInterface



class EventOrchestratorModuleObject(SingletonInterface):

    _instance = None
    @staticmethod
    def get_instance():
        if EventOrchestratorModuleObject._instance is None:
            EventOrchestratorModuleObject._instance = EventOrchestratorModuleObject()
        return EventOrchestratorModuleObject._instance
    
    
    def __init__(self):
               
        pass
            
   




