from typing import Annotated

from fastapi import Body
from pydantic import BaseModel


class CpuLoad(BaseModel):
    core: int
    percentage: Annotated[int, Body(description='load of CPU core as percent')]


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
    t0: Annotated[int, Body(description='measurement start time')]
    t1: Annotated[int, Body(description='measurement end time')]
    t1_t0: Annotated[int, Body(
        description='difference between t1 and t0',
        alias='t1-t0'
    )]
