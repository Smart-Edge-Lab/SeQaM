import os
import sys
from queue import Queue

from ModuleManagement.DataModels.event import StartModuleEvent, EdpEvent, ExitEdpEvent, StopModuleEvent

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)

from Modules.EventOrchestrator.EDPEventsRequester import EDPEventsRequester



class EdpEventInterpreter(): 

    def __init__(self):
        self.edp_event_queue= Queue[EdpEvent](maxsize = 3)
        self.edp_translator_engine = EdpEventsTranslator() 
        self.EDP_EVENT_ACTIONS = ["exit", "start_module", "stop_module"]


    def interpret_event(self, event: EdpEvent):
        """
        Interpret the event and return the corresponding command
        """
        try:
            if isinstance(event, ExitEdpEvent):
                self.edp_translator_engine.exit_edp()
            elif isinstance(event, StartModuleEvent):
                self.edp_translator_engine.start_edp_module(event)
            elif isinstance(event, StopModuleEvent):
                self.edp_translator_engine.stop_edp_module(event)
            else:
                # Handle the case when action is not found
                print (f"Unknown action: {event.action}")

        except Exception as e:
            print(f"Missing Parameter: {e}")
    

    def edpEventInterpreter_runner(self):
        """ 
        Run a thread to listen to the event queue. When an event arrives, interpret it and run the
        corresponding method.
        """
        while True:
            event = self.edp_event_queue.get()
            print("EDP EVENT: forwarding event {}, to edp".format(event))
            self.interpret_event(event)



class EdpEventsTranslator(): 

    def __init__(self) -> None:
        self._requester_= EDPEventsRequester()


    def exit_edp(self):
        print("EDP EVENT: Safely exiting...")


    def stop_edp_module(self, event: StopModuleEvent):
        self._requester_.stop_edp_module(event)


    def start_edp_module(self, event: StartModuleEvent):
        """
        Starts a platform's module. Only implemented for Experiment Dispatcher
        
        Parameters:
        module (str): The name of the module to start
        """
        self._requester_.start_edp_module(event)
        
