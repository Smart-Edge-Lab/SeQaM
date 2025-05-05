import asyncio
import cv2 as cv
import websockets
import numpy as np
import time
import json
import base64
import backoff
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.propagate import inject
from opentelemetry.context import get_current

# Constants
_SERVICE_NAME_ = "image_processing"
VIDEO_SOURCE = "aruco_markers.mkv"
SERVER_ADDRESS = "server"
ENDPOINT = "http://172.22.174.176:4317"

# Set up the tracer provider with service name
resource = Resource.create({SERVICE_NAME: _SERVICE_NAME_})
trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure OTLP Exporter to send data to SigNoz
otlp_exporter = OTLPSpanExporter(
    endpoint=ENDPOINT,
    insecure=True
)

# Add OTLP Exporter to the tracer provider
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

tracer = trace.get_tracer(_SERVICE_NAME_)

def serialize_context(context):
    """
    Serialize the context into a JSON string.
    Assuming context is a dictionary for demonstration.
    """
    return json.dumps(context)

@backoff.on_exception(backoff.expo, websockets.ConnectionClosedError, max_tries=8)
@backoff.on_exception(backoff.expo, OSError, max_tries=8)
async def send_frames(uri: str) -> None:
    """
    Connects to a WebSocket server, reads video frames, and sends them for processing.
    
    Args:
        uri (str): WebSocket URI to connect for sending frames.
    """
    async with websockets.connect(uri) as websocket:
        cap = cv.VideoCapture(VIDEO_SOURCE)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"output_{SERVER_ADDRESS}_{timestamp}.mp4"
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(filename, fourcc, 60, (640, 480))
        if not out.isOpened():
            print("Error: Could not open video writer. Check codec and file path.")
            return

        try:
            while True:
                with tracer.start_as_current_span("end_to_end_latency") as end_to_end_span:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Span for frame processing
                    with tracer.start_as_current_span("process_frame"):
                        frame = cv.resize(frame, (640, 480))
                        _, buffer = cv.imencode('.jpg', frame)
                        encoded_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

                    # Span for preparing and sending data
                    with tracer.start_as_current_span("edge_server_communication") as communication_span:
                        headers = {}
                        inject(headers)
                        context_data = serialize_context(headers)
                        payload = {
                            'context': context_data,
                            'data': encoded_image
                        }

                        start_time = time.time()
                        await websocket.send(json.dumps(payload))
                        data = await websocket.recv()  # Receive processed frame
                        end_time = time.time()
                        communication_span.set_attribute("receiving_time", end_time - start_time)

                    # Span for handling received data
                    with tracer.start_as_current_span("handle_received_data"):
                        if not data:
                            continue

                        nparr = np.frombuffer(data, np.uint8)
                        frame = cv.imdecode(nparr, cv.IMREAD_COLOR)

                        if frame is None:
                            continue

                    # Span for video writing
                    with tracer.start_as_current_span("video_writing"):
                        out.write(frame)
        finally:
            out.release()
            cap.release()
            cv.destroyAllWindows()

# Start sending frames to the server
if __name__ == "__main__":
    asyncio.run(send_frames('ws://server:8000/ws'))