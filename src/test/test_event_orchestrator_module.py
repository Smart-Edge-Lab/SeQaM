import json
import os
import threading
import time
import unittest
from unittest.mock import patch

from Modules.EventOrchestrator import EventOrchestratorModule


class EventOrchestratorModuleTest(unittest.TestCase):
    def setUp(self):
        self.rest_factory_patcher = patch('Modules.EventOrchestrator.EventOrchestratorModule.RestFactory')
        self.rest_factory_mock = self.rest_factory_patcher.start()
        self.rest_factory_mock.return_value.app.run.side_effect = self.simulate_incoming_request
        self.request_patcher = patch('Modules.EventOrchestrator.EventOrchestratorModule.request_json_with_headers')
        self.request_mock = self.request_patcher.start()
        self.post_patcher = patch('Modules.EventOrchestrator.events_requester.requests.post')
        self.post_mock = self.post_patcher.start()
        self.output_to_console_patcher = patch('Modules.EventOrchestrator.events_requester.output_to_console')
        self.output_to_console_mock = self.output_to_console_patcher.start()
        self.jsonify_patcher = patch('Modules.EventOrchestrator.EventOrchestratorModule.jsonify')
        self.jsonify_patcher.start()
        self.threads: list[threading.Thread] = []

    def tearDown(self):
        self.rest_factory_patcher.stop()
        self.request_patcher.stop()
        self.post_patcher.stop()
        self.output_to_console_patcher.stop()
        self.jsonify_patcher.stop()

    def simulate_incoming_request(self, *args, **kwargs):
        route_method = self.rest_factory_mock.return_value.create_POST_route.call_args[0][1]
        route_method()

    def test_propagates_experiment_context(self):
        self.request_mock.return_value = {
            'action': 'cpu_load', 'src_device_type': 'ue', 'src_device_name': 'ue001',
            'cores': '0', 'load': '80', 'time': '60s',
            'experiment_context': {"traceparent": "00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01"}
        }
        self.threads = EventOrchestratorModule.main()
        time.sleep(1)

        self.assertEqual(('http://192.168.122.38:9001/event/stress/cpu_load',), self.post_mock.call_args.args)
        self.assertEqual(
            {
                'action': 'cpu_load',
                "cores": 0, "load": "80", "time": "60s",
                'src_device_name': 'ue001',
                'src_device_type': 'ue',
                'experiment_context': {"traceparent": "00-a9c3b99a95cc045e573e163c3ac80a77-d99d251a8caecd06-01"}
            }, json.loads(self.post_mock.call_args.kwargs['data']))

    def test_network_load_works_with_interface(self):
        self.request_mock.return_value = dict(
            action='network_load',
            experiment_context={'some': 'a'},
            interface='eth0',
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='ue001',
        )
        self.threads = EventOrchestratorModule.main()
        time.sleep(1)

        self.assertEqual('http://172.22.174.175:8887/event/network/load', self.post_mock.call_args.args[0])
        self.assertEqual(
            {
                'action': 'network_load',
                'experiment_context': {'some': 'a'},
                'interface': 'eth0',
                'load': '10',
                'src_device_name': 'ue001',
                'src_device_type': 'ue',
                'time': '20s'
            }, json.loads(self.post_mock.call_args.kwargs['data'])
        )

    def test_network_load_resolves_destination_host(self):
        self.request_mock.return_value = dict(
            action='network_load',
            experiment_context={'some': 'a'},
            time='20s',
            load='10',
            src_device_type='ue',
            src_device_name='load-client',
            dst_device_name='load-server',
            dst_device_type='server',
        )
        self.threads = EventOrchestratorModule.main()
        time.sleep(1)

        self.assertEqual(('http://192.168.122.121:9002/event/network/load',), self.post_mock.call_args.args)
        self.assertEqual(
            {
                'action': 'network_load',
                'dst_device_name': 'load-server',
                'dst_device_type': 'server',
                'experiment_context': {'some': 'a'},
                'load': '10',
                'src_device_name': 'load-client',
                'src_device_type': 'ue',
                'time': '20s',
                'destination_host': '192.168.122.44'
            }, json.loads(self.post_mock.call_args.kwargs['data'])
        )

    def test_server_network_load_resolves_destination_host(self):
        self.request_mock.return_value = dict(
            action='network_load',
            experiment_context={'some': 'a'},
            time='20s',
            load='10',
            src_device_type='server',
            src_device_name='load-server',
            dst_device_name='load-client',
            dst_device_type='ue',
        )
        self.threads = EventOrchestratorModule.main()
        time.sleep(1)

        self.assertEqual(('http://192.168.122.44:9002/event/network/load',), self.post_mock.call_args.args)
        self.assertEqual(
            {
                'action': 'network_load',
                'dst_device_name': 'load-client',
                'dst_device_type': 'ue',
                'experiment_context': {'some': 'a'},
                'load': '10',
                'src_device_name': 'load-server',
                'src_device_type': 'server',
                'time': '20s',
                'destination_host': '192.168.122.121'
            }, json.loads(self.post_mock.call_args.kwargs['data'])
        )
