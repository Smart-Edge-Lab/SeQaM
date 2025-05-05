from pydantic import BaseModel

from seqam_data_fh_dortmund_project_emulate.cpu import CpuState
from seqam_data_fh_dortmund_project_emulate.memory import MemoryState
from seqam_data_fh_dortmund_project_emulate.net import NetState


class SystemState(BaseModel):
    host: str | None = None
    time: float
    cpu_state: CpuState
    memory_state: MemoryState
    net_state: list[NetState]
