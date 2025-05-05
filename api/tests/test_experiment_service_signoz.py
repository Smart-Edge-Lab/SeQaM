import json
import os
from typing import Any

from edpapi_fh_dortmund_project_emulate.experiment.experiment_service import ExperimentService
from edpapi_fh_dortmund_project_emulate.experiment.experiment_service_signoz import ExperimentServiceSignoz
from edpapi_fh_dortmund_project_emulate.span.SpanService import SpanService
from edpapi_fh_dortmund_project_emulate.span.SpanServiceSignoz import SpanServiceSignoz
from tests.db_service_mock import DbServiceMockTest


TEST_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


def read_test_data(json_filename: str) -> Any | None:
    with open(os.path.join(TEST_DATA, json_filename), 'r') as fd:
        expected = json.load(fd)
    return expected


class ExperimentServiceTest(DbServiceMockTest):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def test_return_durations_in_ms(self) -> None:
        span_service: SpanService = SpanServiceSignoz()
        experiment_service: ExperimentService = ExperimentServiceSignoz(span_service)
        result = experiment_service.get_experiment_statistics_for_app(
            exp_name='pigovsky-2024-10-07T11:38',
            app_name='mysql',
            extra_statistics=True,
            raw_data=True,
        )
        expected = read_test_data('test_experiment_service_durations_ms.json')
        self.assertEqual(expected, [r.model_dump() for r in result])

    def test_return_durations_in_nanos(self) -> None:
        span_service: SpanService = SpanServiceSignoz()
        experiment_service: ExperimentService = ExperimentServiceSignoz(span_service)
        result = experiment_service.get_experiment_statistics_for_app(
            exp_name='pigovsky-2024-10-07T11:38',
            app_name='mysql',
            extra_statistics=True,
            raw_data=True,
            nanos=True,
        )
        expected = read_test_data('test_experiment_service_durations_nanos.json')
        self.assertEqual(expected, [r.model_dump() for r in result])
