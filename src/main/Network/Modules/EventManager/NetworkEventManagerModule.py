import os
import shlex
import sys
import threading
import time
from flask import request, jsonify

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.os_utils import run_os_process
from ModuleManagement.DataModels.event import EventFactory, GenerateNetworkLoadEvent, ChangeBandwidthEvent
from ModuleManagement.RestFactory import RestFactory
from Modules.EventManager.Constants import DistrNetworkEventConstants
from Modules.EventManager.Networking.NetworkEventsRequester import NetworkEventsRequester


class DistrEventManagerModule():
    
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
            self._net_constants_ = DistrNetworkEventConstants()
            self._net_event_requester_ = NetworkEventsRequester()



class DistrEventManagerModuleREST:


    def __init__(self):
        
        self._factory_ = RestFactory()
        self._dist_event_manager_engine_ = DistrEventManagerModule.get_instance()
        self._factory_.create_POST_route(self._dist_event_manager_engine_._net_constants_.BANDWIDTH_ROUTE, self.handler_bandwidth_related_events)
        self._factory_.create_POST_route(self._dist_event_manager_engine_._net_constants_.NETWORK_LOAD_ROUTE, self.handler_network_load_related_events)

    def handler_bandwidth_related_events(self):
        event_json = EventFactory.create(**request.get_json())
        print(event_json)
        try:
            if isinstance(event_json, ChangeBandwidthEvent):
                self._dist_event_manager_engine_._net_event_requester_.requestBandwidthEvent(event_json)
            else:
                return self.bad_request_error()
        except Exception as e:
            print(f"Error handling event: {e}")
            return self.bad_request_error()

        return jsonify(event_json.model_dump()), 200

    def handler_network_load_related_events(self):
        event_json = EventFactory.create(**request.get_json())
        print(event_json)

        try:
            if isinstance(event_json, GenerateNetworkLoadEvent):
                self._dist_event_manager_engine_._net_event_requester_.requestNetworkLoadEvent(event_json)
            else:
                return self.bad_request_error()
        except Exception as e:
            print(f"Error handling event: {e}")
            return self.bad_request_error()

        return jsonify(event_json.model_dump()), 200


    def bad_request_error(self):
        
        return jsonify({
            "code": "INVALID_ARGUMENT",
            "status": 400,
            "message": "Bad Request"
        }), 400





if __name__ == '__main__':
    run_os_process(shlex.split('iperf3 -s -D'))
    eventManagerRESTEngine = DistrEventManagerModuleREST()

    port = int(os.environ.get('NETWORK_EVENT_MANAGER_PORT') or 8887)
    t3= threading.Thread(target=lambda: eventManagerRESTEngine._factory_.app.run(host = '0.0.0.0', port=port, debug=False, use_reloader=False))
    t3.daemon= True
    t3.start()

    while True:
        time.sleep(0.5)