import json
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.trace import Tracer
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class OnlyTracer:
    _tracer: Tracer | None = None

    @classmethod
    def get(cls) -> Tracer:
        return cls._tracer if cls._tracer else cls._set()

    @classmethod
    def _set(cls) -> Tracer:
        tracer = instrument_with_otlp()
        cls._tracer = tracer
        return tracer


def instrument_with_otlp() -> Tracer:
    _SERVICE_NAME = "experiment_dispatcher_fh_dortmund_project_emulate"
    resource = Resource.create({SERVICE_NAME: _SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    OTLP_URL = os.environ.get('OTLP_URL')
    otlp_exporter = OTLPSpanExporter(
        endpoint=OTLP_URL,
        insecure=True
    ) if OTLP_URL else ConsoleSpanExporter()
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    # Sets the global default tracer provider
    trace.set_tracer_provider(provider)
    # Creates a tracer from the global tracer provider
    return trace.get_tracer(_SERVICE_NAME)


def serialize_span_context_to_str() -> str:
    span_context: dict[str, str] = {}
    TraceContextTextMapPropagator().inject(span_context)
    return json.dumps(span_context)
