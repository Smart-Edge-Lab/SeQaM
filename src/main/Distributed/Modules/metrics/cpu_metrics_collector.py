import os
import time
from threading import Thread

import psutil
from seqam_data_fh_dortmund_project_emulate.cpu import CpuState, CpuCoreTime, CpuCoreTemperature
from seqam_data_fh_dortmund_project_emulate.memory import MemoryState
from seqam_data_fh_dortmund_project_emulate.net import NetState
from seqam_data_fh_dortmund_project_emulate.system_state import SystemState

from ModuleManagement.rest_utils import api_post


class CpuMetricsCollector:
    CPU_METRIC_INTERVAL = float(os.environ.get('CPU_METRIC_INTERVAL') or 1)
    running: bool = True

    @classmethod
    def _collect_cpu_metrics(cls):
        while cls.running:
            temperatures = psutil.sensors_temperatures()
            cpu_state = CpuState(
                core_times = [
                    CpuCoreTime(idle=ct.idle)
                    for ct in psutil.cpu_times(percpu=True)
                ],
                core_temperatures = [
                    CpuCoreTemperature(
                        label=ct.label,
                        temperature=ct.current,
                    ) for ct in temperatures.get('coretemp', [])
                ]
            )
            memory_temperature_record = next(filter(
                lambda t: t,
                [next(filter(lambda t: t.label == 'Memory', st), None) for st in temperatures.values()]
            ), None)
            memory_temperature = memory_temperature_record.current if memory_temperature_record else None
            memory_data = psutil.virtual_memory()
            memory_state = MemoryState(
                total=memory_data.total,
                available=memory_data.available,
                temperature=memory_temperature,
            )
            net_state = [
                NetState(
                    nic=nic,
                    bytes_sent=ns.bytes_sent,
                    bytes_recv=ns.bytes_recv,
                    packets_sent=ns.packets_sent,
                    packets_recv=ns.packets_recv,
                ) for nic, ns in psutil.net_io_counters(pernic=True).items()
            ]
            api_post(
                '/metrics',
                SystemState(
                    time=time.time(),
                    cpu_state=cpu_state,
                    memory_state=memory_state,
                    net_state=net_state,
                ).model_dump()
            )
            time.sleep(cls.CPU_METRIC_INTERVAL)

    @classmethod
    def collect_cpu_metrics(cls):
        Thread(target=cls._collect_cpu_metrics).start()
