import os
import re
import sys
import threading
import time
from flask import request, jsonify
from queue import Queue
import requests  # type: ignore
import json


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)


from ModuleManagement import console
from ModuleManagement.rest_utils import get_experiment_context
from ModuleManagement.RestFactory import RestFactory
from Utilities.EndpointGenerator import ModuleEndpointGenerator


class CommandTranslatorModule():

    _instance = None
    @staticmethod
    def get_instance():
        if CommandTranslatorModule._instance is None:
            CommandTranslatorModule._instance = CommandTranslatorModule()
        return CommandTranslatorModule._instance
 
      
    def __init__(self):
        """
        Create a new command interpreter module. The module created is not initialized and cannot be used until it is explicitly 
        configured
        """
        if CommandTranslatorModule._instance is not None:
            raise Exception("Singleton: there can only be one object")
        else:
            self.translation_event_queue = Queue[dict](maxsize = 3)
            self._endpoint_generator_ = ModuleEndpointGenerator()


    def translationDispatcher_runner(self):
        """
        Runs an infinite loop to dispatch translation events to the Event Orchestrator.

        This method continuously retrieves events from the translation event queue, generates the URL for the Event Orchestrator,
        and sends the event to the Event Orchestrator using a POST request.

        Returns: 
        None
        """
        while True:        
            event: dict = self.translation_event_queue.get()
            print("forwarding event {}, to event orchestrator".format(event))
            url = self._endpoint_generator_.generate_endpoint(module_name="Event_Orchestrator", module_action="event")
            try:
                response = self.sendJsonCommand(url,event)
                console.output_to_console(url, str(response))
            except Exception as err:
                console.output_to_console(url, err)


    def sendJsonCommand(self, url, event: dict):
        """
        Sends a JSON command to the specified URL.

        This method defines the headers for the request, converts the event data to a JSON string, and sends a POST request to the URL.

        Parameters: 
        url: The URL to send the request to
        event: The event data to be sent
        
        Returns:
        The response from the server
        """
        # Define the headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Convert the data to a JSON string
        body_json = json.dumps(event)
        # Send the POST request
        response = requests.post(url, headers=headers, data=body_json)

        return response



class CommandTranslatorModuleREST:
    """
    This class creates the server to listen to incomming request and handles them
    """
    
    def __init__(self):
        
        self._factory_ = RestFactory()
        self._command_engine_ = CommandTranslatorModule.get_instance()
        self._endpoint_generator_ = ModuleEndpointGenerator()
        self._module_info_ = self._endpoint_generator_.get_module_info(module_name="Command_Translator")
        self._module_port_ = int(self._module_info_["port"])
        self._translation_endpoint_ = self._endpoint_generator_.generate_endpoint(module_name="Command_Translator", module_action="translate")
        self._translation_route = self._translation_endpoint_[self._translation_endpoint_.find("/",10):]
        self._factory_.create_POST_route(self._translation_route, self.handle_edp_translation)

    @staticmethod
    def process_command(command: str) -> dict:
        """
        Processes a command by splitting it into key-value pairs.

        This method takes an action and a list of commands, splits each command into a key-value pair,
        and returns a dictionary of these pairs.

        Parameters: 
        action: The action to be performed
        commands: A list of commands to be processed
        
        Returns: 
        A dictionary of key-value pairs
        """
        action_and_args = re.split(r'\s+', command.strip(), 1)
        action = action_and_args[0]
        key_lists = ["action"]
        value_list = [action]
        args = action_and_args[1] if len(action_and_args) > 1 else ''
        phrases = re.findall(r'''(\w+)\s*:\s*("[^"]*"|'[^']*'|\S+)''', args)

        if action == 'ssh' and not phrases:
            phrases = re.split(r'\s+', args)
            key_lists.extend(['src_device_type', 'src_device_name', 'command'])
            value_list.extend(phrases[0:2] + [" ".join(phrases[2:])])
        else:
            # split commands into actions and values
            for key, value in phrases:
                key_lists.append(key)
                if '"' in value or "'" in value:
                    try:
                        value = eval(value)
                    except Exception:
                        pass
                value_list.append(value)
        return dict(zip(key_lists, value_list))


    def handle_edp_translation(self):
        """
        Handles an EDP translation request.

        This method processes the request data, extracts the action and commands, 
        and puts the translation request into a queue to be sent to the Event Orchestrator.

        Returns:
        A JSON response indicating the success or failure of the request
        """
        command: str = request.data.decode()
        translation_json = self.process_command(command)
        translation_json['experiment_context'] = get_experiment_context(request.headers)

        try:
            if translation_json["action"] == "exit":
                pass
                #TODO: safely exit the module 
            
            else:
                self._command_engine_.translation_event_queue.put(translation_json)
                
        except Exception as e:
            print(f"Error handling translation: {e} is not allowed")
            return self.bad_request_error()

        return jsonify(translation_json), 200


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





if __name__ == '__main__':
    print('environment', os.environ)
    # Get an instance of the CommandTranslatorModule
    commandOrchestratorEngine = CommandTranslatorModule.get_instance()
    # Create an instance of the CommandTranslatorModuleREST
    commandTranslatorRESTEngine = CommandTranslatorModuleREST()

    # Create a thread to run the translation dispatcher
    t = threading.Thread(target=commandOrchestratorEngine.translationDispatcher_runner, args=())
    t.daemon= True
    t.start()

    # Create a thread to run the REST engine
    t3= threading.Thread(target=lambda: commandTranslatorRESTEngine._factory_.app.run(host="0.0.0.0",port=commandTranslatorRESTEngine._module_port_, debug=False, use_reloader=False))
    t3.daemon= True
    t3.start()

    # Keep the main thread running to prevent the program from exiting
    while True:
        time.sleep(0.5)
