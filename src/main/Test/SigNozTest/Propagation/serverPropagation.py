from flask import Flask, request
import time
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

"""
More information in: https://opentelemetry.io/docs/specs/otel/context/api-propagators/
"""
app = Flask(__name__)

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

@app.route('/')
def hello():

    headers = dict(request.headers)
    print(f"Received headers: {headers}")
    carrier ={'traceparent': headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
    print(f"Received context: {ctx}")

    #Start a span attached to the propagated trace
    with tracer.start_as_current_span("Server_received_request", context=ctx):
        print(ctx)

        with tracer.start_as_current_span('Server_process_request'):
            print ("Processing clients request")
            time.sleep(0.1)

            with tracer.start_as_current_span('Server_generate_response'):
                    print ("Generating clients response")
                    return "Hello from API 2!"

if __name__ == '__main__':
    app.run(port=5001)
