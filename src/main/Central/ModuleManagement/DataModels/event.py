from enum import Enum
from typing import Any

from pydantic import BaseModel

from ModuleManagement.Constants import StressEventConstants


class Event(BaseModel):
    action: str
    experiment_context: dict | None = None
    comment: str | None = None

    def payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def get_console_command(self) -> str:
        command = [
            self.action
        ] + [f'{k}:{v}' for k, v in self.payload().items() if k not in ('action', 'experiment_context')]
        return ' '.join(command)


class HelloEvent(Event):
    pass


class SshEvent(Event):
    src_device_type: str
    src_device_name: str
    command: str


class EdpEvent(Event):
    module: str


class StartModuleEvent(EdpEvent):
    def payload(self) -> dict[str, Any]:
        p = super(StartModuleEvent, self).payload()
        p.update(
            {
                "start": "True",
            }
        )
        return p


class StopModuleEvent(EdpEvent):
    def payload(self) -> dict[str, Any]:
        p = super(StopModuleEvent, self).payload()
        p.update(
            {
                "start": "False",
            }
        )
        return p


class ExitEdpEvent(EdpEvent):
    pass


class DurableEvent(Event):
    time: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.time.endswith(tuple(StressEventConstants.TIME_UNITS)):
            raise ValueError("Time unit is wrong.")


class StressMode(str, Enum):
    static = 'stat'
    random = 'rand'
    increasing = 'inc'
    decreasing = 'dec'

    def __str__(self):
        return str(self.value)


class StressEvent(DurableEvent):
    # This class is used to represent a stress event that can be applied to the infrastructure.
    # It is used to store the details of the event and to validate the event before applying it.

    # Required fields that must be present in the event
    load: str
    src_device_type: str
    src_device_name: str
    mode: StressMode | None = None
    random_seed: int | None = None
    load_min: int | None = None
    load_max: int | None = None
    load_step: int | None = None
    time_step: int | None = None


class CpuLoadEvent(StressEvent):
    cores: int


class MemoryLoadEvent(StressEvent):
    workers: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.load.endswith(tuple(StressEventConstants.MEMORY_UNITS)):
            raise ValueError("Memory load is wrong. Please send a number followed by a unit (b, k, m, g)")


class NetworkEvent(DurableEvent):
    src_device_type: str
    src_device_name: str
    interface: str | None = None

    def __init__(self, **kwargs):
        super(NetworkEvent, self).__init__(**kwargs)
        self.src_device_type = str(self.src_device_type).lower() if self.src_device_type else None


class ExtendedNetworkEvent(NetworkEvent):
    dst_device_type: str | None = None
    dst_device_name: str | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dst_device_type = str(self.dst_device_type).lower() if self.dst_device_type else None


class MigrateEvent(ExtendedNetworkEvent):
    pass


class ConnectEvent(ExtendedNetworkEvent):
    pass


class DisconnectEvent(ExtendedNetworkEvent):
    pass


class ChangeBandwidthEvent(NetworkEvent):
    bandwidth: str


class GenerateNetworkLoadEvent(ExtendedNetworkEvent, StressEvent):
    destination_host: str | None = None


class EventFactory:
    _ACTION_TO_EVENT_CLASS: dict[str, type[Event]] = {
        'hello': HelloEvent,
        'ssh': SshEvent,
        'start_module': StartModuleEvent,
        "exit": ExitEdpEvent,
        "stop_module": StopModuleEvent,

        "cpu_load": CpuLoadEvent,
        "memory_load": MemoryLoadEvent,

        "network_bandwidth": ChangeBandwidthEvent,
        "network_load": GenerateNetworkLoadEvent,
        "migrate": MigrateEvent,
        "connect": ConnectEvent,
        "disconnect": DisconnectEvent,
    }

    @classmethod
    def create(cls, **kwargs) -> Event:
        return cls._ACTION_TO_EVENT_CLASS[kwargs['action']](**kwargs)
