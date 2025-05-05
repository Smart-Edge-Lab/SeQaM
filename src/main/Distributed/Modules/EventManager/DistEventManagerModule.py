import os
import sys
import threading
import time
from flask import request

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.DataModels.event import EventFactory
from ModuleManagement.RestFactory import RestFactory
from Modules.EventManager.Constants import DistrInfrastructureEventConstants
from Modules.EventManager.Infrastructure.InfrastructureEventsRequester import InfrastructureEventsRequester
from Modules.metrics.cpu_metrics_collector import CpuMetricsCollector



class DistrEventManagerModule:

    _instance = None

    @staticmethod
    def get_instance():

        if DistrEventManagerModule._instance is None:
            DistrEventManagerModule._instance = DistrEventManagerModule()
        return DistrEventManagerModule._instance

    def __init__(self):

        if DistrEventManagerModule._instance is not None:
            raise Exception("Singleton: there can only be one object")
        else:
            self._infr_constants_ = DistrInfrastructureEventConstants()
            self._infr_event_requester_ = InfrastructureEventsRequester()


class DistrEventManagerModuleREST:

    def __init__(self):

        self._factory_ = RestFactory()
        self._dist_event_manager_engine_ = DistrEventManagerModule.get_instance()
        self._factory_.create_POST_route(self._dist_event_manager_engine_._infr_constants_.CPU_LOAD_ROUTE, self.handler_cpu_related_events)
        self._factory_.create_POST_route(self._dist_event_manager_engine_._infr_constants_.MEMORY_LOAD_ROUTE, self.handler_memory_related_events)


    def handler_cpu_related_events(self):
        event_json = request.get_json()
        event = EventFactory.create(**event_json)
        return self._dist_event_manager_engine_._infr_event_requester_.requestCPULoad(event)


    def handler_memory_related_events(self):
        event_json = request.get_json()
        event = EventFactory.create(**event_json)
        return self._dist_event_manager_engine_._infr_event_requester_.requestMemoryLoad(event)


if __name__ == "__main__":
    CpuMetricsCollector.collect_cpu_metrics()
    eventManagerRESTEngine = DistrEventManagerModuleREST()
    port = int(os.environ.get('DISTRIBUTED_EVENT_MANAGER_PORT') or 9001)
    t3 = threading.Thread(
        target=lambda: eventManagerRESTEngine._factory_.app.run(
            host="0.0.0.0",
            port=port, debug=False, use_reloader=False
        )
    )
    t3.daemon = True
    t3.start()

    while True:
        time.sleep(0.5)
