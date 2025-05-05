from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from fastapi.param_functions import Body


class Ram(BaseModel):
    free: float
    total: float
    t: Annotated[float | None, Body(description='measurement time')] = None
    t_datetime: Annotated[datetime | None, Body(description='measurement time as datetime')] = None
