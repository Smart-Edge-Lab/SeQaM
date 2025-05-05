from typing import List

import pandas

from edpapi_fh_dortmund_project_emulate.common.DbService import DbService
from edpapi_fh_dortmund_project_emulate.span.Span import Span, SpanStatistics
from edpapi_fh_dortmund_project_emulate.span.SpanService import SpanService
from edpapi_fh_dortmund_project_emulate.common.utils import abort


def nanos_to_millis(nanos: float) -> int:
    return int(nanos * 1e-6)


def get_start_time_clause(start_time: int | None) -> str:
    return f'AND toUnixTimestamp64Milli(timestamp) >= {start_time}' if start_time else ''


def get_end_time_clause(start_time: int | None, duration: int | None) -> str:
    return (
        f'AND toUnixTimestamp64Milli(timestamp) <= {start_time + duration}'
        if start_time and duration else ''
    )


SPAN_FIELDS = '''
    toUnixTimestamp64Milli(timestamp), durationNano,
    traceID, spanID, name, numberTagMap
    '''

class SpanServiceSignoz(SpanService):
    def enrich_span_statistics(
        self,
        ss: SpanStatistics,
        app_name: str,
        start_time: int | None,
        duration: int | None,
        extra_statistics: bool,
        raw_data: bool,
        nanos: bool = False,
    ) -> SpanStatistics:
        spans = (
            self.get_spans(
                app_name=app_name,
                span_name=ss.name,
                start_time=start_time,
                duration=duration,
                nanos=nanos,
            )
        ) if extra_statistics or raw_data else None
        ss.raw_data = spans if raw_data else None
        ss.extra_statistics = (
            pandas.Series([s.duration for s in spans])
            .describe().to_dict()
        ) if spans and extra_statistics else None
        return ss

    def get_span_statistics(
        self,
        app_name: str,
        start_time: int | None = None,
        duration: int | None = None,
        extra_statistics: bool = False,
        raw_data: bool = False,
        nanos: bool = False,
    ) -> list[
        SpanStatistics]:
        sql = f'''
        SELECT
            name,
            MIN(durationNano), 
            AVG(durationNano), 
            MAX(durationNano), 
            COUNT(1),
        FROM signoz_traces.distributed_signoz_index_v2
        WHERE serviceName='{app_name}'
            {get_start_time_clause(start_time)}
            {get_end_time_clause(start_time, duration)}
        GROUP BY name
        '''
        r = DbService.query(sql)
        if r and isinstance(r.result_rows, list):
            span_statistics = [
                SpanStatistics(
                    name=s[0],
                    min_duration=s[1] if nanos else nanos_to_millis(s[1]),
                    avg_duration=s[2] if nanos else nanos_to_millis(s[2]),
                    max_duration=s[3] if nanos else nanos_to_millis(s[3]),
                    count=s[4],
                ) for s in
                r.result_rows
            ]
            return [
                self.enrich_span_statistics(
                    ss=ss,
                    app_name=app_name,
                    start_time=start_time,
                    duration=duration,
                    extra_statistics=extra_statistics,
                    raw_data=raw_data,
                    nanos=nanos,
                )
                for ss in span_statistics
            ]
        abort(500, str(r))
        return []

    def get_spans(
            self,
            app_name: str,
            span_name: str,
            limit: int | None = None,
            start_time: int | None = None,
            duration: int | None = None,
            nanos: bool = False,
    ) -> List[Span]:
        start_time_clause = get_start_time_clause(start_time)
        end_time_clause = get_end_time_clause(start_time, duration)
        limit_clause = f'limit {limit or 10}' if not start_time else ''
        sql = f'''
            SELECT
                {SPAN_FIELDS} 
            FROM signoz_traces.distributed_signoz_index_v2
            WHERE serviceName='{app_name}'  
            AND name='{span_name}'
            {start_time_clause} 
            {end_time_clause}
            order by timestamp desc
            {limit_clause}
        '''
        return self._get_spans(sql, nanos=nanos)

    @staticmethod
    def _get_spans(sql: str, nanos: bool = False) -> list[Span]:
        r = DbService.query(sql)
        if r and isinstance(r.result_rows, list):
            return [
                Span(
                    trace_id=s[2],
                    span_id=s[3],
                    name=s[4],
                    tags=s[5],
                    timestamp=s[0],
                    duration=s[1] if nanos else nanos_to_millis(s[1]),
                ) for s in
                r.result_rows
            ]
        abort(500, str(r))
        return []

    def get_child_spans(
        self,
        app_name: str,
        trace_id: str,
        span_id: str,
    ) -> list[Span]:
        sql = f"""
        SELECT
            {SPAN_FIELDS}
        FROM signoz_traces.distributed_signoz_index_v2
        WHERE (parentSpanID = '{span_id}') AND (traceID = '{trace_id}')
        order by timestamp
        """
        return self._get_spans(sql)
