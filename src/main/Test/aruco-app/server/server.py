from fastapi import FastAPI, WebSocket
import cv2 as cv
import numpy as np
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.propagate import extract
from opentelemetry.context import get_current
import time
import json
import base64

_SERVICE_NAME_ = "image_processing"
# Set up the tracer provider with service name
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: _SERVICE_NAME_}))
)

# Configure OTLP Exporter to send data to SigNoz
otlp_exporter = OTLPSpanExporter(
    endpoint="http://172.22.174.176:4317",  # Default SigNoz OTLP receiver port
    insecure=True
)

# Add OTLP Exporter to the tracer provider
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Instrument FastAPI
app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint to handle incoming frames, process them for ArUco marker detection,
    and send back the processed frames.
    """
    await websocket.accept()
    tracer = trace.get_tracer(_SERVICE_NAME_)
    while True:
        data = await websocket.receive_text()
        data = json.loads(data)
        context_data = data['context']
        extracted_context = extract(json.loads(context_data))

        with tracer.start_as_current_span("receive_data", context=extracted_context) as receive_span:
            receive_span.add_event("data_received") 

        with tracer.start_as_current_span("handle_frame", context=extracted_context) as span:
            receive_time = time.time()
            span.add_event("received_request", {"time": receive_time})

        with tracer.start_as_current_span("process_image", context=extracted_context) as process_span:
            image_data = base64.b64decode(data['data'])
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv.imdecode(nparr, cv.IMREAD_COLOR)  # Decode the JPEG directly
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            process_span.add_event("image_processed")

        with tracer.start_as_current_span("aruco_detection", context=extracted_context) as aruco_span:
            # Define the dictionary for ArUco markers
            ARUCO_DICT = {
                "DICT_4X4_50": cv.aruco.DICT_4X4_50,
                "DICT_4X4_100": cv.aruco.DICT_4X4_100,
                "DICT_4X4_250": cv.aruco.DICT_4X4_250,
                "DICT_4X4_1000": cv.aruco.DICT_4X4_1000,
                "DICT_5X5_50": cv.aruco.DICT_5X5_50,
                "DICT_5X5_100": cv.aruco.DICT_5X5_100,
                "DICT_5X5_250": cv.aruco.DICT_5X5_250,
                "DICT_5X5_1000": cv.aruco.DICT_5X5_1000,
                "DICT_6X6_50": cv.aruco.DICT_6X6_50,
                "DICT_6X6_100": cv.aruco.DICT_6X6_100,
                "DICT_6X6_250": cv.aruco.DICT_6X6_250,
                "DICT_6X6_1000": cv.aruco.DICT_6X6_1000,
                "DICT_7X7_50": cv.aruco.DICT_7X7_50,
                "DICT_7X7_100": cv.aruco.DICT_7X7_100,
                "DICT_7X7_250": cv.aruco.DICT_7X7_250,
                "DICT_7X7_1000": cv.aruco.DICT_7X7_1000,
                "DICT_ARUCO_ORIGINAL": cv.aruco.DICT_ARUCO_ORIGINAL,
            }

            aruco_dict_type = "DICT_5X5_100"  # Example, change as needed
            dictionary = cv.aruco.getPredefinedDictionary(ARUCO_DICT[aruco_dict_type])
            parameters = cv.aruco.DetectorParameters()
            detector = cv.aruco.ArucoDetector(dictionary, parameters)

            # Detect markers
        
            start_process_time = time.time()
            corners, ids, rejected = detector.detectMarkers(gray)
            end_process_time = time.time()
            processing_time = end_process_time - start_process_time
            aruco_span.set_attribute("processing_time", processing_time)

        if ids is not None:
            with tracer.start_as_current_span("draw_markers", context=extracted_context) as draw_span:
                frame = cv.aruco.drawDetectedMarkers(frame, corners, ids)
                for i, corner in enumerate(corners):
                    id = ids[i][0]
                    corner = corner.reshape((4, 2))
                    topLeft, topRight, bottomRight, bottomLeft = corner[0], corner[1], corner[2], corner[3]
                    # Ensure coordinates are integers
                    topLeft = (int(topLeft[0]), int(topLeft[1]))
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    
                    cv.line(frame, tuple(topLeft), tuple(topRight), (0, 255, 0), 2)
                    cv.line(frame, tuple(topRight), tuple(bottomRight), (0, 255, 0), 2)
                    cv.line(frame, tuple(bottomRight), tuple(bottomLeft), (0, 255, 0), 2)
                    cv.line(frame, tuple(bottomLeft), tuple(topLeft), (0, 255, 0), 2)
                    cv.putText(frame, str(id), tuple(topLeft), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                draw_span.add_event("markers_drawn")
        with tracer.start_as_current_span("send_processed_data", context=extracted_context) as send_span:
            # Send the processed frame back
            _, buffer = cv.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())  # Send image data as binary
            send_span.add_event("data_sent")
