
import time
import random


from opentelemetry.sdk.resources import SERVICE_NAME, Resource


from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)



# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "OTEL-TEST-METRICS"
})



# --------------------- CREATE OTEL METRICS PROVIDER ----------------

metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(),1000) #we force to export the metrics each 1000 ms
provider = MeterProvider(metric_readers=[metric_reader])

"""
# A Meter Provider (MeterProvider) is a factory for Meters. In most applications, a Meter Provider is initialized 
# once and its lifecycle matches the application’s lifecycle. Meter Provider initialization also includes Resource 
# and Exporter initialization.
"""

# Sets the global default meter provider
metrics.set_meter_provider(provider)


"""
A Meter creates metric instruments, capturing measurements about a service at runtime. Meters are created from Meter Providers
"""
# Creates a meter from the global meter provider
meter = metrics.get_meter("OTEL-TEST-METRICS")

# create two counters, one of the metrics you can create with OTEL
# We most likely use counter and updowncounter
work_counter = meter.create_counter(
    name = "work.counter", unit="1", description="Counts the number of times the function is called"
)

exception_counter = meter.create_counter(
    name = "exception.counter", unit="1", description="dummy counter to count exceptions"
)


"""
Metric Exporters send metric data to a consumer. This consumer can be standard output for debugging during development, the OpenTelemetry Collector, or any open source or vendor backend of your choice.

In this example, we use the ConsoleMetricExporter(), so we can visualize the metrics in the console. Afterwards, we will need to configure the OTLPMetricExporter
"""


## ----------------------- FUNCTION DECLARATION -----------------------

def do_work():

    work_counter.add(1, {"function": "do_work", "custom_information" : "customizable_message"})
    print("doing some work...")

    
  
## ----------------------- RUN EXAMPLE -----------------------
        
if __name__ == '__main__':
      
    for i in range (8):
      
      time.sleep(1)
      print(i+1,"------------------")
      do_work()
  
      random_integer = random.randint(0,2)
      print("random integer: ", random_integer)
      try:
  	    10/random_integer
      except:
  	    print("random integer was 0")
  	    exception_counter.add(1, {"exception_type": "division by zero"})
  
  
  
  

