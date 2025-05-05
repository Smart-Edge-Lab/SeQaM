import os
import unittest

from Utilities.JsonReader import JsonReader

dir_path = os.path.dirname(os.path.realpath(__file__))


class JsonReaderTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        os.environ.pop('COMMAND_TRANSLATOR_PORT', None)
        os.environ.pop('COMMAND_TRANSLATOR_HOST', None)
        os.environ.pop('EXPERIMENT_DISPATCHER_PORT', None)
        os.environ.pop('EXPERIMENT_DISPATCHER_HOST', None)
        os.environ.pop('EVENT_ORCHESTRATOR_PORT', None)
        os.environ.pop('EVENT_ORCHESTRATOR_HOST', None)
        self.json_reader = JsonReader(os.path.join(dir_path, '../main/Central/Configuration/ModuleConfig.json'))

    def test_uses_defaults(self):
        res = self.json_reader.readFile()
        DEFAULT_HOST = "172.22.174.157"
        self.assertEqual({
            "modules":
                [
                    {
                        "console": {
                            "name": "Console",
                            "description": "Console module to input commands",
                            "port": 0,
                            "host": "0.0.0.0",
                            "paths": [

                            ]
                        }
                    },
                    {
                        "command_translator": {
                            "name": "Command Translator",
                            "description": "Get raw commands and forward them to orchestrators in json format",
                            "port": 8001,
                            "host": DEFAULT_HOST,
                            "paths": [
                                {
                                    "translate": {
                                        "endpoint": "/translate/"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "event_orchestrator": {
                            "name": "Event Orchestrator",
                            "description": "Get event requests",
                            "port": 8002,
                            "host": DEFAULT_HOST,
                            "paths": [
                                {
                                    "event": {
                                        "endpoint": "/event/"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "data_manager": {
                            "name": "Data Manager",
                            "description": "Provides an access to the data collected by EDP",
                            "port": 8003,
                            "host": DEFAULT_HOST,
                            "paths": [
                                {
                                    "cpu": {
                                        "endpoint": "/metrics/cpu/"
                                    }
                                },
                                {
                                    "memory": {
                                        "endpoint": "/metrics/memory/"
                                    }
                                },
                                {
                                    "traces": {
                                        "endpoint": "/traces/"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "experiment_dispatcher": {
                            "name": "Experiment Dispatcher",
                            "description": "Executes the configured experiment",
                            "port": 8004,
                            "host": DEFAULT_HOST,
                            "paths": [
                                {
                                    "start": {
                                        "endpoint": "/experiment/init/"
                                    },
                                    "stop": {
                                        "endpoint": "/experiment/init/"
                                    },
                                }
                            ]
                        }
                    }
                ]
        }, res)

    def test_substitutes_port(self):
        os.environ['COMMAND_TRANSLATOR_PORT'] = '9999'
        res = self.json_reader.readFile()
        self.assertEqual(9999, res['modules'][1]['command_translator']['port'])  # add assertion here

    def test_substitutes_host(self):
        os.environ['COMMAND_TRANSLATOR_HOST'] = '172.23.34.5'
        res = self.json_reader.readFile()
        self.assertEqual('172.23.34.5', res['modules'][1]['command_translator']['host'])  # add assertion here
