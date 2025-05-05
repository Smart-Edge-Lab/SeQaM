import copy
import random
import re
import unittest
from threading import Thread
import time
from unittest.mock import patch

import freezegun
from Modules.experiment_dispatcher.ExperimentDispatcher import ExperimentDispatcher
from Modules.experiment_dispatcher.ExperimentDispatcherModule import ExperimentDispatcherModuleREST, \
    ExperimentDispatcherModuleEngine


_EXPERIMENT = {
  "experiment_name": "test_case_1",
  "eventList": [
    {
      "command": "migrate src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102",
      "executionTime": 100
    },
    {
      "command": "disconnect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102",
      "executionTime": 200
    },
    {
      "command": "cpu_load src_device_type:ue src_device_name:ue001 cores:5 load:20 time:60s",
      "executionTime": 201
    },
    {
      "command": "connect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr101",
      "executionTime": 300
    },
    {
      "command": "memory_load src_device_type:ue src_device_name:ue001 workers:5 load:20 time:10s",
      "executionTime": 500
    },
    {
      "command": "network_load src_device_type:router src_device_name:router1 interface:eth2 load:5 time:5s",
      "executionTime": 700
    },
    {
      "command": "network_bandwidth src_device_type:router src_device_name:router1 interface:eth2 bandwidth:20 time:30s",
      "executionTime": 800
    },
    {
      "command": "exit",
      "executionTime": 1000
    }
  ]
}


@freezegun.freeze_time('2024-07-01')
class ExperimentDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.module_endpoint_generator_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.ModuleEndpointGenerator')
        self.module_endpoint_generator_mock = self.module_endpoint_generator_patcher.start()
        self.experiment_file_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.ExperimentFile')
        self.experiment_file_mock = self.experiment_file_patcher.start()
        self.queue_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.Queue')
        self.queue_mock = self.queue_patcher.start()
        self.print_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.print')
        self.print_mock = self.print_patcher.start()
        self.jsonify_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcherModule.jsonify')
        self.jsonify_patcher.start()
        self.tracer_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.tracer')
        self.tracer_mock = self.tracer_patcher.start()
        self.output_to_console_patcher = patch('Modules.experiment_dispatcher.ExperimentDispatcher.output_to_console')
        self.output_to_console_mock = self.output_to_console_patcher.start()
        self.tracer_mock.start_as_current_span.return_value.__enter__.return_value = 'some'
        self.tracer_mock.start_as_current_span.return_value.__exit__.return_value = True
        self.experiment_dispatcher: ExperimentDispatcher = ExperimentDispatcher()
        self.experiment_dispatcher.ongoing = True

    def tearDown(self):
        self.queue_patcher.stop()
        self.module_endpoint_generator_patcher.stop()
        self.experiment_file_patcher.stop()
        self.print_patcher.stop()
        self.tracer_patcher.stop()
        self.output_to_console_patcher.stop()
        self.jsonify_patcher.stop()

    def test_run_iterator(self):
        self.experiment_dispatcher._run_iterator(copy.deepcopy(_EXPERIMENT))
        self.tracer_mock.start_as_current_span.assert_called_once_with('test_case_1-01.07.2024T00:00:00')
        self.ensure_commands_order()
        self.ensure_timing()

    def test_run_iterator_on_unordered_event_list(self):
        experiment_data = copy.deepcopy(_EXPERIMENT)
        random.shuffle(experiment_data['eventList'])
        self.experiment_dispatcher._run_iterator(experiment_data)
        self.ensure_commands_order()
        self.ensure_timing()

    def test_stop_command(self):
        exp_disp_module_rest = MockExperimentDispatcherModuleREST()
        request_json_patch = patch('Modules.experiment_dispatcher.ExperimentDispatcherModule.get_request_json')
        request_json_mock = request_json_patch.start()
        request_json_mock.return_value = {'start': "True"}
        file_reader_patch = patch('Utilities.JsonReader.JsonReader.readFile')
        file_reader_mock = file_reader_patch.start()
        file_reader_mock.return_value = copy.deepcopy(_EXPERIMENT)
        processing = Thread(target=exp_disp_module_rest.handle_dispatcher_event)
        processing.start()
        time.sleep(201e-3)
        request_json_mock.return_value = {'start': "False"}
        Thread(target=exp_disp_module_rest.handle_dispatcher_event).start()
        processing.join()
        self.experiment_dispatcher = ExperimentDispatcherModuleEngine.get_instance()._dispatcher_
        calls = [
            c.args[0][0] for c in self.experiment_dispatcher._instruction_queue_.method_calls if c[0] == 'put'
        ]
        self.assertLess(len(calls), len(_EXPERIMENT['eventList']))
        self.ensure_timing()
        time.sleep(.5)
        self.output_to_console_mock.assert_called_once_with(
            'ExperimentDispatcher', 'Experiment test_case_1-01.07.2024T00:00:00 is stopped'
        )
        request_json_patch.stop()
        file_reader_patch.stop()

    def ensure_timing(self, tolerance: int = 5):
        logs = [
            re.search(r'ITERATOR: event at (\d+) ms:(.*)', log.args[0]) for log in self.print_mock.call_args_list
        ]
        for i in range(len(logs)):
            time = int(logs[i].group(1))
            cmd = logs[i].group(2)
            event = _EXPERIMENT['eventList'][i]
            expected_time = event['executionTime']
            expected_command = event['command']
            self.assertIn(expected_command, cmd)
            self.assertLess(
                time - expected_time,
                tolerance,
                f'Time difference between {time} and {expected_time} is too large for {cmd}'
            )

    def ensure_commands_order(self, custom_list: list[str] | None = None):
        calls = [
            c.args[0][0] for c in self.experiment_dispatcher._instruction_queue_.method_calls if c[0] == 'put'
        ]
        self.assertEqual(
            custom_list or [
                'migrate src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102',
                'disconnect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102',
                'cpu_load src_device_type:ue src_device_name:ue001 cores:5 load:20 time:60s',
                'connect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr101',
                'memory_load src_device_type:ue src_device_name:ue001 workers:5 load:20 time:10s',
                'network_load src_device_type:router src_device_name:router1 interface:eth2 load:5 time:5s',
                'network_bandwidth src_device_type:router src_device_name:router1 interface:eth2 bandwidth:20 time:30s',
                'exit'
            ], calls
        )


class MockExperimentDispatcherModuleREST(ExperimentDispatcherModuleREST):
    def __init__(self):
        pass  # Intentionally do not call superclass constructor
