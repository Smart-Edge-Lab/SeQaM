from pydantic import BaseModel


class CpuCoreTime(BaseModel):
    idle: float


class CpuCoreTemperature(BaseModel):
    label: str
    temperature: float


class CpuState(BaseModel):
    core_times: list[CpuCoreTime]
    core_temperatures: list[CpuCoreTemperature]
