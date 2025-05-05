import random
import time
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor , ConsoleSpanExporter)


# Service name is required for most backends
_SERVICE_NAME_ = "OTEL-TEST-TRACES"

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


## ----------------------- FUNCTION DECLARATION -----------------------

def do_work():
        
    with tracer.start_as_current_span("do_work_parent") as parent:
        # do some work that 'parent' tracks
        print("doing some work...")
        current_span = trace.get_current_span()
        current_span.set_attribute("device", "ue1")
        current_span.add_event("in do_work function")
        # this attribute can be used to identify the element that sends the trace
        time.sleep(0.2)
        # Create a nested span to track nested work
        with tracer.start_as_current_span("do_work_child 1") as child:
            # do some work that 'child' tracks
            print("doing some nested work...")
            current_span.add_event("in first child of do_work function")
            time.sleep(0.5)
            # the nested span is closed when it's out of scope
        
        do_more_work()
        
      # This span is also closed when it goes out of scope
        
  
  
def do_more_work():
    
    with tracer.start_as_current_span("do_more_work_child 2") as child:
        # do some work that 'child' tracks
        print("doing more work...")
        time.sleep(0.1)
        
    with tracer.start_as_current_span("do_more_work_child 3") as child:
        # do some work that 'child' tracks
        print("doing still more work...")
        time.sleep(0.2)
        with tracer.start_as_current_span("do_work_child 3.1") as child:
            # do some work that 'child' tracks
            print("doing some nested work...")
            time_hold = (random.randint(0,500))/1000
            time.sleep(time_hold)
            
          
    
## ----------------------- RUN EXAMPLE -----------------------      

if __name__ == '__main__':
        
    for i in range (5):
  
      time.sleep(1)
      print(i+1,"------------------")
      do_work()
  

