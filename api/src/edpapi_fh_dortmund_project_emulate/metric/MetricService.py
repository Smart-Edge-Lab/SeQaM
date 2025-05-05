import abc
from datetime import datetime

from edpapi_fh_dortmund_project_emulate.metric.Cpu import Cpu, CpuLoad
from edpapi_fh_dortmund_project_emulate.metric.Ram import Ram
from seqam_data_fh_dortmund_project_emulate.system_state import SystemState


class MetricService:
    @abc.abstractmethod
    def get_cpu(self, server_name: str, duration: int) -> Cpu:
        """
        Get CPU load during the last `duration` milliseconds

        :param server_name: server name to get the cpu load for
        :param duration: time window duration
        :return: list of cpu load percentage on every core and timestamp info like
            .. code-block:: json
            {
                "cpu-load": [
                  {
                    "core": 0,
                    "percentage": 10
                  }
                ],
                "t0": 1722235579726,
                "t1": 1722235699726,
                "t1-t0": 120000
            }
        where t0 is the measurement start time,
            t1 is the measurement end time,
            t1-t0 is the difference between the above two
        """

    @abc.abstractmethod
    def get_ram(self, server_name: str, duration: int) -> Ram:
        """
        Get ram metric

        :param server_name: host name to collect the metric for
        :param duration: duration in milliseconds

        :returns: free and total memory in bytes
        """

    @abc.abstractmethod
    def submit_host_metrics(self, system_state: SystemState) -> SystemState:
        """
        Saves the system metrics observation into a database

        :param system_state:
        :return:
        """

    @abc.abstractmethod
    def get_cpu_series(self, host_name: str, start_time: int, end_time: int) -> list[Cpu]:
        """
        Get cpu load history in time range

        :param host_name: host for what the cpu load measurements were collected
        :param start_time: start of the time range
        :param end_time: end of the time range
        :return: Time seria of cpu usage in the requested time range
        """

    @abc.abstractmethod
    def get_ram_series(self, server_name: str, start_time: int, end_time: int) -> list[Ram]:
        """
        Get memory history in time range

        :param server_name: host where the memory amounts were observed
        :param start_time: time range start
        :param end_time: time range end
        :return: Time seria of memory amount in the requested time range
        """


def build_cpu_usage(t0: float, t1: float, cpu_t0: dict[int, float], cpu_t1: dict[int, float]) -> Cpu:
    """
    Builds CPU usage entity

    :param t0: time of the last observation
    :param t1: time of the current observation
    :param cpu_t0: the last cpu idle times as {coreN: idletime, ...}
    :param cpu_t1: the current cpu idle times as {coreN: idletime, ...}
    :return: Cpu usage in percents
    """
    cpu_load = [
        CpuLoad(
            core=r[0],
            percentage=(
                1 - (cpu_t1[r[0]] - r[1]) / (t1 - t0)
            ) * 100.0 if t1 > t0 else 0.0
        ) for r in sorted(cpu_t0.items())
    ]
    return Cpu(
        cpu_load=cpu_load,
        t0=t0,
        t0_datetime=datetime.fromtimestamp(t0),
        t1=t1,
        t1_datetime=datetime.fromtimestamp(t1),
        t1_t0=t1 - t0
    )
