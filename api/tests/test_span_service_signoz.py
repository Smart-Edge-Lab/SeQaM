from tests.db_service_mock import DbServiceMockTest
from edpapi_fh_dortmund_project_emulate.span.Span import Span
from edpapi_fh_dortmund_project_emulate.span.SpanServiceSignoz import SpanServiceSignoz


class SpanServiceSignozTest(DbServiceMockTest):
    def test_get_spans_for_starting_time_and_duration(self) -> None:
        span_service = SpanServiceSignoz()
        result = span_service.get_spans(
            'image_processing',
            'aruco_detection',
            None,
            1721900595500,
            1000
        )
        self.assertEqual([
            Span(
                name='nit',
                trace_id='tid',
                span_id='sid',
                tags={'some': 'thing'},
                timestamp=1721900595500,
                duration=6
            )
        ], result)
