import unittest

from Modules.CommandTranslator.CommandTranslatorModule import CommandTranslatorModuleREST


class CommandTranslatorModuleTest(unittest.TestCase):
    def test_short_ssh_command_is_parsed(self):
        self.assertEqual(
            {
                'action': 'ssh',
                'command': 'echo hello world',
                'src_device_name': 'ue001',
                'src_device_type': 'ue'
            }, CommandTranslatorModuleREST
                .process_command('ssh ue ue001 echo hello world')
        )

    def test_long_ssh_command_is_parsed(self):
        self.assertEqual(
            {
                'action': 'ssh',
                'command': 'echo hello world',
                'src_device_name': 'ue001',
                'src_device_type': 'ue'
            }, CommandTranslatorModuleREST
                .process_command('ssh src_device_type:ue src_device_name:ue001 command:"echo hello world"')
        )

    def test_long_ssh_command_with_quotes_is_parsed(self):
        self.assertEqual(
            {
                'action': 'ssh',
                'command': 'echo "hello world" > some.txt',
                'src_device_name': 'ue001',
                'src_device_type': 'ue'
            }, CommandTranslatorModuleREST
                .process_command('''ssh src_device_type:ue src_device_name:ue001 command:'echo "hello world" > some.txt' ''')
        )

    def test_hello_command_should_work(self):
        self.assertEqual(
            {"action": "hello"},
            CommandTranslatorModuleREST.process_command('hello')
        )

    def test_network_load_command_works(self):
        self.assertEqual(
            {
                'action': 'network_load',
                'src_device_type': 'ue',
                'src_device_name': 'load-client',
                'dst_device_type': 'server',
                'dst_device_name': 'load-server',
                'load': '5',
                'time': '5s',
            },
            CommandTranslatorModuleREST.process_command(
                'network_load src_device_type:ue src_device_name:load-client dst_device_type:server '
                'dst_device_name:load-server load:5 time:5s'
            )
        )