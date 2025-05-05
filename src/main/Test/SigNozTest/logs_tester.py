import logging
import random
import time
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs.export import (ConsoleLogExporter)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource



# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "OTEL-TEST-LOGS"
})



# --------------------- CREATE OTEL LOGGER PROVIDER ----------------
# Create and set the logger provider
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)


# UNCOMMENT THIS LINE TO SEND LOGS TO THE CONSOLE
log_processor = BatchLogRecordProcessor(ConsoleLogExporter())
# This configuration sends the logs in batches


# UNCOMMENT THIS LINE TO SEND LOGS TO THE OTLP EXPORTER (COLLECTOR)
#log_processor = BatchLogRecordProcessor(OTLPLogExporter(endpoint="127.0.0.1:4317", insecure = True))


logger_provider.add_log_record_processor(log_processor)

# Attach OTLP handler to root logger
handler = LoggingHandler(logger_provider=logger_provider)
logging.getLogger().addHandler(handler)


## ----------------------- FUNCTION DECLARATION -----------------------

def do_work():

    logging.warning("Running Function")
    print("doing some work...")
    time.sleep(0.2)

    
        
## ----------------------- RUN EXAMPLE -----------------------
        
if __name__ == '__main__':
      
    for i in range (5):
      # You can use logging directly anywhere in your app now
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
