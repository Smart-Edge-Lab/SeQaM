import os
import sys

from ModuleManagement.DataModels.event import CpuLoadEvent, MemoryLoadEvent

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Infrastructure")[0]
sys.path.insert(0, ROOT_PATH)

from Modules.EventManager.Infrastructure.Stress.StressHandlerModule import StressHandlerModule



class InfrastructureEventsRequester():

    def __init__(self):
        self._stress_handler_ = StressHandlerModule()
   

    def requestCPULoad(self, event: CpuLoadEvent):
        response = self._stress_handler_.handle_stress_event(event)
        return response


    def requestMemoryLoad(self, event: MemoryLoadEvent):
        response = self._stress_handler_.handle_stress_event(event)
        return response
