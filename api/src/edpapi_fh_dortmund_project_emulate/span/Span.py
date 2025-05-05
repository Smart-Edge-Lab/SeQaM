from typing import Any

from pydantic import BaseModel


class Span(BaseModel):
    trace_id: str
    span_id: str
    name: str | None
    timestamp: int
    duration: int
    tags: dict[str, Any]


class SpanStatistics(BaseModel):
    name: str
    min_duration: float
    avg_duration: float
    max_duration: float
    count: int
    extra_statistics: dict[str, Any] | None = None
    raw_data: list[Span] | None = None
