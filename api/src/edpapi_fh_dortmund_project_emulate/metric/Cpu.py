from datetime import datetime
from typing import Annotated

from fastapi import Body
from pydantic import BaseModel


class CpuLoad(BaseModel):
    core: int
    percentage: Annotated[float, Body(description='load of CPU core as percent')]


class Cpu(BaseModel):
    """
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
    """
    cpu_load: Annotated[list[CpuLoad], Body(alias='cpu-load')]
    t0: Annotated[float, Body(description='measurement start time')]
    t0_datetime: Annotated[datetime | None, Body(description='measurement start time as datetime')] = None
    t1: Annotated[float, Body(description='measurement end time')]
    t1_datetime: Annotated[datetime | None, Body(description='measurement end time as datetime')] = None
    t1_t0: Annotated[float, Body(
        description='difference between t1 and t0',
        alias='t1-t0'
    )]


class CpuService:
    data: dict[str, tuple[float, dict[int, float]]] = {}

    @classmethod
    def get_last_idle_times(cls, host_name: str) -> tuple[float, dict[int, float]] | None:
        """
        Returns {core: idle_time} dictionary and time when that state was observed
        on the host with given host_name.

        :param host_name: host name where cpu idle times are measured
        :return: tuple of observation time and {core: idle_time} dictionary
        """
        return cls.data.get(host_name)

    @classmethod
    def set_last_idle_times(cls, host_name: str, time: float, idle_times: dict[int, float]) -> None:
        cls.data[host_name] = (time, idle_times)
