from pydantic import BaseModel, computed_field

from edpapi_fh_dortmund_project_emulate.span.Span import Span, SpanStatistics


class ExperimentStatistics(BaseModel):
    commands: list[str]
    indexes: list[int]
    start_time: int
    end_time: int

    @computed_field  # type: ignore
    @property
    def duration(self) -> int:
        return self.end_time - self.start_time

    span_statistics: list[SpanStatistics] | None = None
