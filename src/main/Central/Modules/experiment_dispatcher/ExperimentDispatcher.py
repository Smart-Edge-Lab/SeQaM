from datetime import datetime
import os
import sys
import threading
import time
from queue import Queue
import requests  # type: ignore

from ModuleManagement.console import output_to_console
from ModuleManagement.otlp_utils import instrument_with_otlp, serialize_span_context_to_str
from ModuleManagement.rest_utils import EXPERIMENT_CONTEXT_HEADER
from Utilities.EndpointGenerator import ModuleEndpointGenerator
from Modules.experiment_dispatcher.ExperimentFileManager import ExperimentFile

tracer = instrument_with_otlp()

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.insert(0, ROOT_PATH)


class ExperimentDispatcher():

    def __init__(self) -> None:
        self.ongoing = False
        self._instruction_queue_ = Queue[tuple[str, str]](maxsize=5)
        self._endpoint_generator_ = ModuleEndpointGenerator()
        self._experiment_file_ = ExperimentFile()

    def sendRawCommand(self, endpoint: str, body: str, experiment_context: str | None = None):
        """
        Sends a raw command to the specified endpoint.

        This method defines the headers for the request and sends a POST request to the endpoint.

        :param endpoint: The URL to send the request to
        :param body: The raw command
        :param experiment_context: optional context of the experiment.
            This is a parent span for all the commands in the experiment
        
        :returns: The response from the server
        """
        # Define the headers
        headers = {
            'Content-Type': 'text/plain'
        }
        if experiment_context:
            headers[EXPERIMENT_CONTEXT_HEADER] = experiment_context

        # Send the POST request
        response = requests.post(endpoint, headers=headers, data=body.encode())

        return response

    def _run_dispatcher(self):
        """
        As long as the command is not exit, dispatch the events in the queue
        """
        command = [""]
        while self.ongoing and command[0] != "exit":
            (instruction, span_context) = self._instruction_queue_.get()
            command = instruction.split(" ")
            print("DISPATCHER: command", command)
            # TODO: check if command == exit and properly exit the module

            try:
                url = self._endpoint_generator_.generate_endpoint(
                    module_name="Command_Translator",
                    module_action="translate"
                )
                response = self.sendRawCommand(url, instruction, span_context)
                #TODO: Only write if the action is correct and was implemented
                self._experiment_file_.write_to_file(instruction)

            except IndexError:

                print("error")

    def _run_iterator(self, experiment_data: dict) -> None:
        """
        A thread that reads the events in the file and then puts them in a queue to be dispatched 
        """
        experiment_name = (
            f'{experiment_data["experiment_name"]}-'
            f'{datetime.now().strftime("%d.%m.%YT%H:%M:%S")}'
        )
        event_list = experiment_data["eventList"]
        event_list = sorted(event_list, key=lambda e: e['executionTime'])
        init_time_in_milliseconds = int(round(time.time() * 1000))
        self._experiment_file_.create_file(experiment_name)
        with tracer.start_as_current_span(experiment_name):
            for event in event_list:
                if not self.ongoing:
                    break
                command = event["command"]
                time_execution = init_time_in_milliseconds + event["executionTime"]
                current_time_in_milliseconds = int(round(time.time() * 1000))
                time_to_wait = time_execution - current_time_in_milliseconds
                if time_to_wait > 0:
                    # to give the processor some time
                    time.sleep(time_to_wait * 1e-3)

                print(f"ITERATOR: event at {current_time_in_milliseconds - init_time_in_milliseconds} ms:  {event}")
                span_context = serialize_span_context_to_str()
                self._instruction_queue_.put((command, span_context))
        log_message = f'Experiment {experiment_name} is {"finished" if self.ongoing else "stopped"}'
        output_to_console(self.__class__.__name__, log_message)

    def run(self, experiment_data):
        """
        Run the module with the data of the experiment. Create individual threads for reading the events and dispatching them
        #TODO: can create an individual thread per event to avoid any delay in dispatching consequtive events
        """
        self.ongoing = True
        iterator_thread = threading.Thread(target=self._run_iterator, args=(experiment_data,))
        iterator_thread.daemon = True
        iterator_thread.start()

        dispatcher_thread = threading.Thread(target=self._run_dispatcher)
        dispatcher_thread.daemon = True
        dispatcher_thread.start()

    def stop(self):
        self.ongoing = False
