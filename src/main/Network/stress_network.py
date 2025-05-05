import os
import re
from threading import Thread

from ModuleManagement.DataModels.event import GenerateNetworkLoadEvent
from ModuleManagement.stress_utils import apply_stress

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def extract_number_from_name(input_string):
    match = re.search(r'\d+$', input_string)
    if match:
        return int(match.group())
    else:
        return None


def network_stress_command(data: GenerateNetworkLoadEvent) -> str:
    load = int(data.load)
    time = data.time
    router_name = data.src_device_name
    interface = data.interface
    load_client_name = extract_number_from_name(router_name)
    time_in_seconds = get_time_in_seconds(time)

    if load_client_name is not None:
        print(
            f"LOAD INVOKER: Load is:  {load} Mbps Time is: {time_in_seconds} seconds in Router {router_name} {interface}")
        psath = os.path.join(ROOT_PATH, 'Modules', 'EventManager', 'Networking', 'Implementer', 'manageLoad.sh')
        print(psath)
        return f'{psath} {load} {time_in_seconds} {load_client_name}'
    else:
        print(
            f"LOAD INVOKER: Load client for Router {router_name} {interface} cannot be determined. Numbers must match"
        )
        return ''


def network_stress_command_for_custom_destination(data: GenerateNetworkLoadEvent) -> str:
    load = int(data.load)
    time = data.time
    time_in_seconds = get_time_in_seconds(time)

    return (
        f'iperf3 -c {data.destination_host} -b{load}M -t {time_in_seconds} --timestamps '
        f'--logfile iperfLog-{data.destination_host}.txt'
    )


def get_time_in_seconds(time: str) -> int:
    time_parts = re.findall(r'\d+|\D+', time)
    time_value = int(time_parts[0])
    time_unit = time_parts[1]
    time_in_seconds = {
        's': time_value,
        'm': time_value * 60,
        'h': time_value * 3600
    }.get(time_unit, 0)
    return time_in_seconds


def invoke_network_load(event: GenerateNetworkLoadEvent) -> Thread | None:
    if event.destination_host:
        return apply_stress(event, network_stress_command_for_custom_destination, do_shlex=True)
    else:
        return apply_stress(event, network_stress_command, do_shlex=False, shell=True)
