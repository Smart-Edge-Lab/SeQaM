from edpapi_fh_dortmund_project_emulate.application.ApplicationServiceSignoz import ApplicationServiceSignoz
from edpapi_fh_dortmund_project_emulate.experiment.experiment import ExperimentStatistics
from edpapi_fh_dortmund_project_emulate.experiment.experiment_service import ExperimentService
from edpapi_fh_dortmund_project_emulate.experiment.merge_utils import merge_experiment_steps
from edpapi_fh_dortmund_project_emulate.span.Span import Span
from edpapi_fh_dortmund_project_emulate.span.SpanService import SpanService


EXPERIMENT_DISPATCHER_SERVICE = 'experiment_dispatcher_fh_dortmund_project_emulate'


class ExperimentServiceSignoz(ExperimentService):
    def get_experiment_statistics_for_app(
        self,
        exp_name: str,
        app_name: str,
        extra_statistics: bool = False,
        raw_data: bool = False,
        nanos: bool = False,
    ) -> list[ExperimentStatistics]:
        experiment_steps = merge_experiment_steps([
            ExperimentStatistics(
                commands=[str(es.name)],
                indexes=[i],
                start_time=es.timestamp,
                end_time=es.timestamp + es.duration,
            ) for i, es in enumerate(self.get_experiment_by_name(exp_name))
        ])
        return [
            ExperimentStatistics(
                commands=es.commands,
                indexes=es.indexes,
                start_time=es.start_time,
                end_time=es.end_time,
                span_statistics=self.span_service.get_span_statistics(
                    app_name=app_name,
                    start_time=es.start_time,
                    duration=es.duration,
                    extra_statistics=extra_statistics,
                    raw_data=raw_data,
                    nanos=nanos,
                )
            ) for es in experiment_steps
        ]

    def __init__(self, span_service: SpanService) -> None:
        self.span_service = span_service

    def get_experiment_by_name(self, name: str) -> list[Span]:
        parent_span = self.span_service.get_spans(
            app_name=EXPERIMENT_DISPATCHER_SERVICE,
            span_name=name,
            limit=1
        )
        return (
            self.span_service.get_child_spans(
                app_name=EXPERIMENT_DISPATCHER_SERVICE,
                trace_id=parent_span[0].trace_id,
                span_id=parent_span[0].span_id
            ) if parent_span else []
        )

    def get_experiments(self) -> list[str]:
        sql = f'''
        SELECT DISTINCT name
        FROM signoz_traces.distributed_signoz_index_v2
        WHERE (serviceName = '{EXPERIMENT_DISPATCHER_SERVICE}') AND (parentSpanID = '')
        ORDER BY timestamp DESC
        LIMIT 100
        '''
        return ApplicationServiceSignoz.get_str_list(sql)

