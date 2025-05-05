import os
import sys
import unittest
from threading import Thread
from unittest.mock import patch

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'main', 'Network'))
sys.path.insert(0, ROOT_PATH)

from stress_network import invoke_network_load
from ModuleManagement.DataModels.event import CpuLoadEvent, GenerateNetworkLoadEvent
from ModuleManagement.DataModels.StressEvent import construct_stress_event
from ModuleManagement.stress_utils import apply_stress


class StressHandlerModuleTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tracer_patcher = patch('ModuleManagement.otlp_utils.OnlyTracer.get')
        self.tracer_mock = self.tracer_patcher.start()
        self.tracer_mock.return_value.start_as_current_span.return_value.__enter__.return_value = 'some'
        self.tracer_mock.return_value.start_as_current_span.return_value.__exit__.return_value = True
        self.run_os_process_await_patcher = patch('ModuleManagement.os_utils.run_os_process_await')
        self.run_os_process_await_mock = self.run_os_process_await_patcher.start()
        self.trace_context_text_map_propagator_patcher = patch('ModuleManagement.os_utils.TraceContextTextMapPropagator')
        self.trace_context_text_map_propagator_mock = self.trace_context_text_map_propagator_patcher.start()

    def tearDown(self):
        super().tearDown()
        self.tracer_patcher.stop()
        self.run_os_process_await_patcher.stop()
        self.trace_context_text_map_propagator_patcher.stop()

    def test_static_cpu_load(self):
        event = CpuLoadEvent(
            action='cpu_load',
            experiment_context={'some': 'a'},
            cores=5,
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
        )
        t = apply_stress(event.model_copy(), construct_stress_event, do_shlex=True)
        t.join()
        self.assertEqual(
            [
               ['stress-ng', '--cpu', '5', '--cpu-load', '10', '--timeout', '20s'],
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        self.tracer_mock.return_value.start_as_current_span.assert_called_once_with(
            'cpu_load time:20s load:10 src_device_type:ue src_device_name:ue001 '
            'cores:5',
            context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
        )

    def test_random_cpu_load(self):
        event = CpuLoadEvent(
            action='cpu_load',
            experiment_context={'some': 'a'},
            cores=5,
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
            mode='rand',
            random_seed=33,
            time_step=2,
            load_max=40,
            load_step=10,
        )
        t = apply_stress(event.model_copy(), construct_stress_event, do_shlex=True)
        t.join()
        self.assertEqual(
            [
               ['stress-ng', '--cpu', '5', '--cpu-load', '18', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '13', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '23', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '20', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '18', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '23', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '33', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '40', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '40', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '35', '--timeout', '2s']
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        self.tracer_mock.return_value.start_as_current_span.assert_called_once_with(
            'cpu_load time:20s load:10 src_device_type:ue src_device_name:ue001 mode:rand random_seed:33 '
            'load_max:40 load_step:10 time_step:2 cores:5',
            context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
        )

    def test_increasing_cpu_load(self):
        event = CpuLoadEvent(
            action='cpu_load',
            experiment_context={'some': 'a'},
            cores=5,
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
            mode='inc',
            time_step=2,
            load_min=10,
            load_max=99,
            load_step=10,
        )
        t = apply_stress(event.model_copy(), construct_stress_event, do_shlex=True)
        t.join()
        self.assertEqual(
            [
               ['stress-ng', '--cpu', '5', '--cpu-load', '10', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '20', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '30', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '40', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '50', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '60', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '70', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '80', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '90', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '99', '--timeout', '2s']
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        for load in [10, 20, 30, 40, 50, 60, 70, 80, 90, 99]:
            self.tracer_mock.return_value.start_as_current_span.assert_any_call(
                f'cpu_load time:2s load:{load} src_device_type:ue src_device_name:ue001 mode:inc '
                'load_min:10 load_max:99 load_step:10 time_step:2 cores:5',
                context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
            )

    def test_decreasing_cpu_load(self):
        event = CpuLoadEvent(
            action='cpu_load',
            experiment_context={'some': 'a'},
            cores=5,
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
            mode='dec',
            time_step=2,
            load_min=10,
            load_max=99,
            load_step=10,
        )
        t = apply_stress(event.model_copy(), construct_stress_event, do_shlex=True)
        t.join()
        self.assertEqual(
            [
               ['stress-ng', '--cpu', '5', '--cpu-load', '99', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '89', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '79', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '69', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '59', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '49', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '39', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '29', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '19', '--timeout', '2s'],
               ['stress-ng', '--cpu', '5', '--cpu-load', '10', '--timeout', '2s']
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        for load in [99, 89, 79, 69, 59, 49, 39, 29, 19, 10]:
            self.tracer_mock.return_value.start_as_current_span.assert_any_call(
                f'cpu_load time:2s load:{load} src_device_type:ue src_device_name:ue001 mode:dec '
                'load_min:10 load_max:99 load_step:10 time_step:2 cores:5',
                context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
            )

    def test_static_network_load(self):
        event = GenerateNetworkLoadEvent(
            action='network_load',
            experiment_context={'some': 'a'},
            interface='eth0',
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
        )
        t = invoke_network_load(event.model_copy())
        t.join()
        self.assertEqual(
            [
                f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 10 20 1'
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        self.assertEqual({'shell': True}, self.run_os_process_await_mock.call_args_list[0][1])
        self.tracer_mock.return_value.start_as_current_span.assert_called_once_with(
            'network_load time:20s load:10 src_device_type:ue src_device_name:ue001 interface:eth0',
            context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
        )

    def test_static_network_load_for_custom_destination(self):
        event = GenerateNetworkLoadEvent(
            action='network_load',
            experiment_context={'some': 'a'},
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
            dst_device_name='srv101',
            dst_device_type='server',
            destination_host='server1.iperf3.fh-dortmund.de'
        )
        t = invoke_network_load(event.model_copy())
        t.join()
        self.assertEqual(
            [
                [
                    'iperf3', '-c', 'server1.iperf3.fh-dortmund.de', '-b10M', '-t', '20', '--timestamps',
                    '--logfile', 'iperfLog-server1.iperf3.fh-dortmund.de.txt'
                ]
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        self.tracer_mock.return_value.start_as_current_span.assert_called_once_with(
            'network_load time:20s load:10 src_device_type:ue src_device_name:ue001 '
            'dst_device_type:server dst_device_name:srv101 '
            'destination_host:server1.iperf3.fh-dortmund.de',
            context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
        )

    def test_random_network_load(self):
        event = GenerateNetworkLoadEvent(
            action='network_load',
            experiment_context={'some': 'a'},
            interface='eth0',
            time='20s',
            load='10',
            src_device_type='router',
            src_device_name='router001',
            mode='rand',
            random_seed=33,
            time_step=2,
            load_max=40,
            load_step=10,
        )
        t = invoke_network_load(event.model_copy())
        t.join()
        self.assertEqual(
            [
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 18 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 13 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 23 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 20 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 18 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 23 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 33 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 40 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 40 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 35 2 1',
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        self.tracer_mock.return_value.start_as_current_span.assert_called_once_with(
            'network_load time:20s load:10 src_device_type:router src_device_name:router001 mode:rand random_seed:33 '
            'load_max:40 load_step:10 time_step:2 interface:eth0',
            context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
        )

    def test_increasing_network_load(self):
        event = GenerateNetworkLoadEvent(
            action='network_load',
            experiment_context={'some': 'a'},
            interface='eth0',
            time='20s',
            load='10',
            src_device_type='router',
            src_device_name='router001',
            mode='inc',
            time_step=2,
            load_min=10,
            load_max=99,
            load_step=10,
        )
        t = invoke_network_load(event.model_copy())
        t.join()
        self.assertEqual(
            [
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 10 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 20 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 30 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 40 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 50 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 60 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 70 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 80 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 90 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 99 2 1',
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        for load in [10, 20, 30, 40, 50, 60, 70, 80, 90, 99]:
            self.tracer_mock.return_value.start_as_current_span.assert_any_call(
                f'network_load time:2s load:{load} src_device_type:router src_device_name:router001 mode:inc '
                'load_min:10 load_max:99 load_step:10 time_step:2 interface:eth0',
                context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
            )

    def test_decreasing_network_load(self):
        event = GenerateNetworkLoadEvent(
            action='network_load',
            experiment_context={'some': 'a'},
            interface='eth0',
            time='20s',
            load='10',
            src_device_type='router',
            src_device_name='router001',
            mode='dec',
            time_step=2,
            load_min=10,
            load_max=99,
            load_step=10,
        )
        t = invoke_network_load(event.model_copy())
        t.join()
        self.assertEqual(
            [
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 99 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 89 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 79 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 69 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 59 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 49 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 39 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 29 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 19 2 1',
               f'{ROOT_PATH}/Modules/EventManager/Networking/Implementer/manageLoad.sh 10 2 1',
            ],
            [i[0][0] for i in self.run_os_process_await_mock.call_args_list]
        )
        for load in [99, 89, 79, 69, 59, 49, 39, 29, 19, 10]:
            self.tracer_mock.return_value.start_as_current_span.assert_any_call(
                f'network_load time:2s load:{load} src_device_type:router src_device_name:router001 mode:dec '
                'load_min:10 load_max:99 load_step:10 time_step:2 interface:eth0',
                context=self.trace_context_text_map_propagator_mock.return_value.extract.return_value
            )
