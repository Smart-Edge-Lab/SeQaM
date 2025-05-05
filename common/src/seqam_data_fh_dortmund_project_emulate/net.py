from pydantic import BaseModel


class NetState(BaseModel):
    """
    bytes_sent: number of bytes sent
    bytes_recv: number of bytes received
    packets_sent: number of packets sent
    packets_recv: number of packets received
    """
    nic: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
