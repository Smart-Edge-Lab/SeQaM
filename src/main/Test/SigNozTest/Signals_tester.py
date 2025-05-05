import logging
import random
import time

from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs.export import (ConsoleLogExporter)


from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)


from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor , ConsoleSpanExporter)


# Service name is required for most backends
_SERVICE_NAME_ = "OTEL-TEST-EDP"

resource = Resource(attributes={
    SERVICE_NAME: _SERVICE_NAME_
})



# --------------------- CREATE OTEL LOGGER PROVIDER ----------------
# Create and set the logger provider
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

# UNCOMMENT THIS LINE TO SEND LOGS TO THE OTLP EXPORTER (COLLECTOR)
log_processor = BatchLogRecordProcessor(OTLPLogExporter(endpoint="127.0.0.1:4317", insecure = True))

logger_provider.add_log_record_processor(log_processor)

# Attach OTLP handler to root logger
handler = LoggingHandler(logger_provider=logger_provider)
logging.getLogger().addHandler(handler)


# --------------------- CREATE OTEL METRICS PROVIDER ----------------


metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="127.0.0.1:4317", insecure = True),1000)


provider = MeterProvider(metric_readers=[metric_reader])

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter(_SERVICE_NAME_)

# create two counters, one of the metrics you can create with OTEL
# We most likely use counter and updowncounter
work_counter = meter.create_counter(
    name = "work.counter", unit="1", description="Counts the number of times the function is called"
)



# --------------------- CREATE OTEL TRACER PROVIDER ----------------
traceProvider = TracerProvider(resource=resource)

# UNCOMMENT THIS LINE TO SEND LOGS TO THE OTLP EXPORTER (COLLECTOR)
trace_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="127.0.0.1:4317", insecure = True))

traceProvider.add_span_processor(trace_processor)
trace.set_tracer_provider(traceProvider)

tracer = trace.get_tracer(_SERVICE_NAME_)



## ----------------------- FUNCTION DECLARATION -----------------------


def do_work():
    work_counter.add(1, {"function": "do_work", "custom_information" : "customizable_message"})   
    with tracer.start_as_current_span("do_work_parent") as parent:
        # do some work that 'parent' tracks
        print("doing some work...")
        logging.warning("Into Parent Span")
        current_span = trace.get_current_span()
        current_span.set_attribute("device", "ue1")
        current_span.add_event("in do_work function")
        # this attribute can be used to identify the element that sends the trace
        time.sleep(0.2)
        # Create a nested span to track nested work
        with tracer.start_as_current_span("do_work_child 1") as child:
            # do some work that 'child' tracks
            print("doing some nested work...")
            logging.warning("Into Child 1 Span")
            current_span.add_event("in first child of do_work function")
            time.sleep(0.5)
            # the nested span is closed when it's out of scope
        
        do_more_work()
        
      # This span is also closed when it goes out of scope
        
  
  
def do_more_work():
    
    with tracer.start_as_current_span("do_more_work_child 2") as child:
        # do some work that 'child' tracks
        print("doing more work...")
        logging.warning("Into Child 2 Span")
        time.sleep(0.1)
        
    with tracer.start_as_current_span("do_more_work_child 3") as child:
        # do some work that 'child' tracks
        print("doing still more work...")
        logging.warning("Into Child 3 Span")
        time.sleep(0.2)
        with tracer.start_as_current_span("do_work_child 3.1") as child:
            # do some work that 'child' tracks
            print("doing some nested work...")
            logging.warning("Into Child 3.1 Span")
            time_hold = (random.randint(0,500))/1000
            time.sleep(time_hold)
            
          
    
## ----------------------- RUN EXAMPLE -----------------------      

        
if __name__ == '__main__':
      
    for i in range (5):
      
      time.sleep(1)
      print(i+1,"------------------")
      do_work()
  
      random_integer = random.randint(0,2)
      print("random integer: ", random_integer)
      try:
  	    10/random_integer
      except:
  	    print("random integer was 0")
  	    logging.error("division by 0")
  	    
  
    # Ensure the logger is shutdown before exiting so all pending logs are exported
    logger_provider.shutdown()





    
    
  
