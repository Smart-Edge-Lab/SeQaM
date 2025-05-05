import os
import sys

from flask import jsonify
import queue
import logging


# Configure logging
logging.basicConfig(level=logging.ERROR)

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Modules")[0]
sys.path.append(ROOT_PATH)

# from Constants import StressEventConstants
from ModuleManagement.RestFactory import RestFactory
from ModuleManagement.DataModels.event import StressEvent
from ModuleManagement.DataModels.StressEvent import construct_stress_event
from ModuleManagement.stress_utils import apply_stress


# Define a thread-safe queue to pass events between threads
event_queue = queue.Queue()


# Class to handle stress events coming from the API
class StressHandlerModule:
    def __init__(self):
        self._factory_ = RestFactory()

    def good_request_details(self, message="Request successful"):
        return jsonify({
            "code": "SUCCESS",
            "status": 200,
            "message": message
        }), 200

    def bad_request_error(self, message="Bad Request"):
        return jsonify({
            "code": "ERROR",
            "status": 400,
            "message": message
        }), 400

    # Function to handle stress events
    def handle_stress_event(self, stress_event: StressEvent):
        try:
            try:
                apply_stress(stress_event, construct_stress_event, do_shlex=True)
                return self.good_request_details()
            except Exception as e:
                logging.error(f"Error handling event: {e}")
                return self.bad_request_error(e.args[0])
        except ValueError as e:
            logging.error(f"Error handling event: {e}")
            return self.bad_request_error(e.args[0])
        except Exception as e:
            logging.error(f"Error handling event: {e}")
            return self.bad_request_error(e.args[0])
