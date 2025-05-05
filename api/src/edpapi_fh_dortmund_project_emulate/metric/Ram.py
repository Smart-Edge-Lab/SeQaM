from pydantic import BaseModel


class Ram(BaseModel):
    free: float
    total: float
