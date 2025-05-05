import abc
from typing import List

from edpapi_fh_dortmund_project_emulate.span.Span import Span, SpanStatistics


class SpanService:

    @abc.abstractmethod
    def get_spans(
        self,
        app_name: str,
        span_name: str,
        limit: int | None = None,
        start_time: int | None = None,
        duration: int | None = None,
    ) -> List[Span]:
        """
        Get `limit` last spans named `span_name` from a given app `app_name`

        :param app_name: application name
        :param span_name: user-defined span name
        :param limit: number of spans to collect
        :param start_time: get spans that happened after this specified time instance
        :param duration: get spans that happened during the specified interval

        :return: list of time stamps with durations in milliseconds like

        .. code-block:: json
            [
              {
                "timestamp": 1721734621982,
                "duration": 34729
              }
            ]
        """

    @abc.abstractmethod
    def get_child_spans(
        self,
        app_name: str,
        trace_id: str,
        span_id: str,
    ) -> list[Span]:
        """
        Get the children of a given span

        :param app_name: application name
        :param trace_id: trace id of the parent span whose children we get
        :param span_id: span id of the parent span whose children we get

        :returns: list of spans
        """

    @abc.abstractmethod
    def get_span_statistics(
        self,
        app_name: str,
        start_time: int | None = None,
        duration: int | None = None,
        extra_statistics: bool = False,
        raw_data: bool = False,
        nanos: bool = False,
    ) -> list[SpanStatistics]:
        """
        Get minimal, average and maximal durations for every span
        for given app in the given time range

        :param app_name: application name
        :param start_time: start of the time range
        :param duration: duration of the time range
        :param extra_statistics: calculate additional statistics using pandas
        :param raw_data: return raw span data
        :param nanos: return durations in nanoseconds

        :returns: list of span statistics for all the span names
        """
