import abc
from typing import List

from edpapi_fh_dortmund_project_emulate.metric.Cpu import Cpu
from edpapi_fh_dortmund_project_emulate.metric.Ram import Ram


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