import os
import sys
import threading
import time
from queue import Queue

from flask import request, jsonify


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)


from ModuleManagement.console import output_to_console
from ModuleManagement.DataModels.event import EventFactory, Event, HelloEvent
from ModuleManagement.rest_utils import request_json_with_headers
from ModuleManagement.RestFactory import RestFactory
from Utilities.EndpointGenerator import ModuleEndpointGenerator
from Modules.EventOrchestrator.NetworkEventsTranslator import NetworkEventInterpreter
from Modules.EventOrchestrator.InfrastructureEventsTranslator import InfrastructureEventInterpreter
from Modules.EventOrchestrator.EdpEventsTranslator import EdpEventInterpreter


class EventOrchestratorModule():
    
    _instance = None
    @staticmethod
    def get_instance():

        if EventOrchestratorModule._instance is None:
            EventOrchestratorModule._instance = EventOrchestratorModule()
        return EventOrchestratorModule._instance


    def __init__(self):

        if EventOrchestratorModule._instance is not None:
            raise Exception("Singleton: there can only be one object")
        else:
            self._netw_event_object_ = NetworkEventInterpreter()
            self._infr_event_object_ = InfrastructureEventInterpreter()
            self._edp_event_object_ = EdpEventInterpreter()
            self.NETWORK_EVENT_ACTIONS = self._netw_event_object_.NETWORK_EVENT_ACTIONS
            self.INFRASTRUCTURE_EVENT_ACTIONS = self._infr_event_object_.INFRASTRUCTURE_EVENT_ACTIONS
            self.EDP_EVENT_ACTIONS = self._edp_event_object_.EDP_EVENT_ACTIONS
            # TODO: ALLOWED_ACTIONS is formed by all the individual actions in the submodules. However this is now ineffective and should be changed
            self.ALLOWED_ACTIONS = []
            self.ALLOWED_ACTIONS.extend(self.NETWORK_EVENT_ACTIONS)
            self.ALLOWED_ACTIONS.extend(self.INFRASTRUCTURE_EVENT_ACTIONS)
            self.ALLOWED_ACTIONS.extend(self.EDP_EVENT_ACTIONS)



class EventOrchestratorModuleREST:
    
    def __init__(self):
        
        self._factory_ = RestFactory()
        self._command_engine_ = EventOrchestratorModule.get_instance()
        self._endpoint_generator_ = ModuleEndpointGenerator()
        self._module_info_ = self._endpoint_generator_.get_module_info(module_name="Event_Orchestrator")
        self._module_port_ = int(self._module_info_["port"])
        self._event_endpoint_ = self._endpoint_generator_.generate_endpoint(module_name="Event_Orchestrator", module_action="event")
        self._event_route = self._event_endpoint_[self._event_endpoint_.find("/",10):]
        self._factory_.create_GET_route(self._event_route, self.get_edp_events)
        self._factory_.create_POST_route(self._event_route, self.handle_edp_event)

    
    def get_edp_events(self):
        """
        Not implemented
        """
        ip_address = request.headers.get('IP-Address')
        if ip_address:
            if not (self._factory_.ipv4_pattern.match(ip_address) or self._factory_.ipv6_pattern.match(ip_address)):
                return self.bad_request_error()


    def handle_edp_event(self):
        """
        Implements the endpoint to handle all platform events. Puts each event into an specific queue based on its type
        """
        event_json = request_json_with_headers()

        try:
            event = EventFactory.create(**event_json)
            if isinstance(event, HelloEvent):
                output_to_console(self.__class__.__name__, 'Guten Tag!')
                return 'hello', 200
            if event.action in self._command_engine_.ALLOWED_ACTIONS:
                action_type = self.determine_action_type(event.action)
                if action_type is not None:
                    event_queue = self.get_event_queue_for_action_type(action_type)
                    event_queue.put(event)
            else:
                return self.bad_request_error()
        except Exception as e:
            print(f"Error handling event: {e}")
            output_to_console(self.__class__.__name__, e)
            return self.bad_request_error()

        return jsonify(event.model_dump()), 200


    def determine_action_type(self, action: str):
        """
        Determines the name of the queue where to put the event

        Parameters:
        action (str): if the action is contained within one of the known actions for a certain device

        Returns:
        The name of the queue 
        
        """
        if action in self._command_engine_.NETWORK_EVENT_ACTIONS:
            return "net_event_queue"
        elif action in self._command_engine_.INFRASTRUCTURE_EVENT_ACTIONS:
            return "infr_event_queue"
        elif action in self._command_engine_.EDP_EVENT_ACTIONS:
            return "edp_event_queue"


    def get_event_queue_for_action_type(self, action_type: str) -> Queue[Event] | None:
        """
        Determines the queue where to put the event

        Parameters:
        action (str): if the action is contained within one of the known actions for a certain device

        Returns:
        The queue 
        
        """
        if action_type == "net_event_queue":
            return self._command_engine_._netw_event_object_.net_event_queue
        elif action_type == "infr_event_queue":
            return self._command_engine_._infr_event_object_.infr_event_queue
        elif action_type == "edp_event_queue":
            return self._command_engine_._edp_event_object_.edp_event_queue
        else:
            return None


    def bad_request_error(self):
        """
        Returns a bad request error response.
        This method returns a JSON response with a 400 status code, indicating a bad request.

        Returns:
        A JSON response with a 400 status code
        """  
        return jsonify({
            "code": "INVALID_ARGUMENT",
            "status": 400,
            "message": "Bad Request"
        }), 400


def main() -> list[threading.Thread]:
    eventOrchestratorEngine = EventOrchestratorModule.get_instance()
    eventOrchestratorRESTEngine = EventOrchestratorModuleREST()

    t0 = threading.Thread(target=eventOrchestratorEngine._netw_event_object_.networkEventInterpreter_runner, args=())
    t0.daemon = True
    t0.start()

    t1 = threading.Thread(target=eventOrchestratorEngine._infr_event_object_.infrastructureEventInterpreter_runner,
                         args=())
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=eventOrchestratorEngine._edp_event_object_.edpEventInterpreter_runner, args=())
    t2.daemon = True
    t2.start()

    t3 = threading.Thread(target=lambda: eventOrchestratorRESTEngine._factory_.app.run(
        host="0.0.0.0",
        port=eventOrchestratorRESTEngine._module_port_,
        debug=False, use_reloader=False
    ))
    t3.daemon = True
    t3.start()
    return [t0, t1, t2, t3]


if __name__ == '__main__':
    
    main()

    while True:
        time.sleep(0.5)
