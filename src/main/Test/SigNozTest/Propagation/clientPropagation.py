import requests
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace
from opentelemetry.propagate import inject, extract
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

"""
More information in: https://opentelemetry.io/docs/specs/otel/context/api-propagators/
"""

_SERVICE_NAME_ = "OTEL-TEST-TRACES-PROPAGATION"

resource = Resource(attributes={
    SERVICE_NAME: _SERVICE_NAME_
})

# --------------------- CREATE OTEL TRACER PROVIDER ----------------
traceProvider = TracerProvider(resource=resource)

# UNCOMMENT THIS LINE TO SEND LOGS TO THE CONSOLE
#trace_processor = BatchSpanProcessor(ConsoleSpanExporter())
# it is also possible to send the traces without batches

# UNCOMMENT THIS LINE TO SEND LOGS TO THE OTLP EXPORTER (COLLECTOR)
trace_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="127.0.0.1:4317", insecure = True))
traceProvider.add_span_processor(trace_processor)
trace.set_tracer_provider(traceProvider)
tracer = trace.get_tracer(_SERVICE_NAME_)

if __name__ == '__main__':

    with tracer.start_as_current_span("client_processing"):     
        print("processing data in client")

        with tracer.start_as_current_span('client_send_request'):
            print ("client request sent")
            headers = {}
            inject(headers)
            response = requests.get('http://127.0.0.1:5001/', headers=headers)
            print(response.text)

            with  tracer.start_as_current_span('client_child_process_response'):
                print ("server response received")