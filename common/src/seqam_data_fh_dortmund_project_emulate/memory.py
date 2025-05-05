from pydantic import BaseModel


class MemoryState(BaseModel):
    """
    total: total physical memory (exclusive swap).

    available: the memory that can be given instantly to processes without the system going into swap.
    This is calculated by summing different memory metrics that vary depending on the platform.
    It is supposed to be used to monitor actual memory usage in a cross platform fashion.
    """
    total: int
    available: int
    temperature: float | None = None
