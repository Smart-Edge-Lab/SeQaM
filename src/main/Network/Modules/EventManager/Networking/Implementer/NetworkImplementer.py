import re
import os
from threading import Thread

from ModuleManagement.DataModels.event import GenerateNetworkLoadEvent, ChangeBandwidthEvent
from ModuleManagement.os_utils import run_event_command
from stress_network import invoke_network_load

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class NetworkBandwidthImplementer():

    def __init__(self) -> None:
        pass

    @staticmethod
    def network_bandwidth_to_cmd(data: ChangeBandwidthEvent) -> str:
        rate = int(data.bandwidth)
        time = data.time
        router_name = data.src_device_name
        interface = data.interface

        # Parse the time string into seconds
        time_parts = re.findall(r'\d+|\D+', time)
        time_value = int(time_parts[0])
        time_unit = time_parts[1]

        time_in_seconds = {
            's': time_value,
            'm': time_value * 60,
            'h': time_value * 3600
        }.get(time_unit, 0)

        print(f"BANDWIDTH INVOKER: Rate is:  {rate} Mbps Time is: {time_in_seconds} seconds in Router {router_name} {interface}")
        psath = os.path.join(ROOT_PATH, 'Implementer', 'manageInterface.sh')
        print(psath)
        return f'{psath} {rate} {time_in_seconds} {router_name} {interface}'

    @staticmethod
    def invoke_network_bandwidth(data: ChangeBandwidthEvent):
        run_event_command([data], NetworkBandwidthImplementer.network_bandwidth_to_cmd, data, do_shlex=False, shell=True)


class NetworkLoadImplementer():

    def __init__(self) -> None:
        pass

    @staticmethod
    def invoke_network_load(event: GenerateNetworkLoadEvent) -> Thread | None:
        return invoke_network_load(event)
