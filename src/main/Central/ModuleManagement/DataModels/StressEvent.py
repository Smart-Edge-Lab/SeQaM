import os
import sys

from ModuleManagement.DataModels.event import StressEvent, CpuLoadEvent, MemoryLoadEvent

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_PATH = ROOT_PATH.split("Stress")[0]
sys.path.append(ROOT_PATH)


def construct_stress_event(event: StressEvent) -> str:
    # Construct a stress event from the object.
    # Returns:
    #     a string representation of the stress event.
    if isinstance(event, CpuLoadEvent):
        return f"stress-ng --cpu {event.cores} --cpu-load {event.load} --timeout {event.time}"
    elif isinstance(event, MemoryLoadEvent):
        return f"stress-ng --vm 1 --vm-bytes {event.load} --vm-keep --timeout {event.time}"
    return ''
