import os
import sys
import argparse
from flask import request, jsonify
import threading
import time

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_PATH)

from ModuleManagement.configuration_aware import ConfigurationAware
from Modules.experiment_dispatcher.ExperimentDispatcher import ExperimentDispatcher
from Utilities.JsonReader import JsonReader
from ModuleManagement.RestFactory import RestFactory
from Utilities.EndpointGenerator import ModuleEndpointGenerator


class ExperimentDispatcherModuleEngine(ConfigurationAware):

    _instance = None
    @staticmethod
    def get_instance():

        if ExperimentDispatcherModuleEngine._instance is None:
            ExperimentDispatcherModuleEngine._instance = ExperimentDispatcherModuleEngine()
        return ExperimentDispatcherModuleEngine._instance

    def __init__(self):
        super().__init__()
        if ExperimentDispatcherModuleEngine._instance is not None:
            raise Exception("Singleton: there can only be one object")
        else:
            self._file_name_ = "ExperimentConfig.json"
            self._file_path_ = os.path.join(self._home_path_, self._file_name_)
            self._reader_ = JsonReader(self._file_path_)
            self._dispatcher_ = ExperimentDispatcher()
            self._experiment_data_ = self._reader_.readFile()


    def runDistpatcher (self):
        """
        Runs the dispatcher thread
        """
        self._dispatcher_.run(self._experiment_data_)

    def stop_dispatcher(self):
        self._dispatcher_.stop()


def get_request_json():
    return request.get_json()


class ExperimentDispatcherModuleREST:
    
    def __init__(self):
        
        self._factory_ = RestFactory()
        self._command_engine_ = ExperimentDispatcherModuleEngine.get_instance()
        self._endpoint_generator_ = ModuleEndpointGenerator()
        self._module_info_ = self._endpoint_generator_.get_module_info(module_name="Experiment_Dispatcher")
        self._module_port_ = int(self._module_info_["port"])
        self._event_endpoint_ = self._endpoint_generator_.generate_endpoint(module_name="Experiment_Dispatcher", module_action="start")
        self._event_route = self._event_endpoint_[self._event_endpoint_.find("/",10):]
        self._factory_.create_POST_route(self._event_route, self.handle_dispatcher_event)
  

    def handle_dispatcher_event(self):
        """
        Implements the endpoint to handle the incomming events to start the module
        """
        event_json = get_request_json()
        engine = ExperimentDispatcherModuleEngine.get_instance()

        try:
            module_command = event_json["start"]
            if module_command == "True":
                engine._experiment_data_ = engine._reader_.readFile()
                engine.runDistpatcher()
            elif module_command == 'False':
                engine.stop_dispatcher()
            else:
                return self.bad_request_error()
        except Exception as e:
            print(f"Error handling event: {e}")
            return self.bad_request_error()

        return jsonify(event_json), 200

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





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Experiment Dispatcher Module')
    parser.add_argument('--mode', '-m', choices=['alone', 'trigger'], default='alone',
                        help='Specify the mode of operation. "alone" runs the module directly and "trigger" creates an endpoint that waits for a trigger from console. Default is "alone"')

    args = parser.parse_args()

    experimentDispatcherEngine = ExperimentDispatcherModuleEngine.get_instance()
    # print("*************************")
    # print(args.mode)
    if args.mode == 'trigger':
        experimentDispatcherEngineREST = ExperimentDispatcherModuleREST()

        t3= threading.Thread(target=lambda: experimentDispatcherEngineREST._factory_.app.run(host = '0.0.0.0', port=experimentDispatcherEngineREST._module_port_, debug=False, use_reloader=False))
        t3.daemon= True
        t3.start()
        while True:
            time.sleep(0.5)

    else:
        experimentDispatcherEngine.runDistpatcher()


