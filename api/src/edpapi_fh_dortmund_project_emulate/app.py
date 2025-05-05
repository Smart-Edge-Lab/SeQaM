import os
from pathlib import Path

import requests  # type: ignore
from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from edpapi_fh_dortmund_project_emulate.application.ApplicationService import ApplicationService
from edpapi_fh_dortmund_project_emulate.application.ApplicationServiceSignoz import ApplicationServiceSignoz
from edpapi_fh_dortmund_project_emulate.console.message import Message
from edpapi_fh_dortmund_project_emulate.console.utils import send_message_to_console
from edpapi_fh_dortmund_project_emulate.experiment.experiment import ExperimentStatistics
from edpapi_fh_dortmund_project_emulate.experiment.experiment_service import ExperimentService
from edpapi_fh_dortmund_project_emulate.experiment.experiment_service_signoz import ExperimentServiceSignoz
from edpapi_fh_dortmund_project_emulate.metric.Cpu import Cpu
from edpapi_fh_dortmund_project_emulate.metric.MetricService import MetricService
from edpapi_fh_dortmund_project_emulate.metric.MetricServiceSignoz import MetricServiceSignoz
from edpapi_fh_dortmund_project_emulate.metric.Ram import Ram
from edpapi_fh_dortmund_project_emulate.server.ServerService import ServerService
from edpapi_fh_dortmund_project_emulate.server.ServerServiceSignoz import ServerServiceSignoz
from edpapi_fh_dortmund_project_emulate.span.Span import Span, SpanStatistics
from edpapi_fh_dortmund_project_emulate.span.SpanService import SpanService
from edpapi_fh_dortmund_project_emulate.span.SpanServiceSignoz import SpanServiceSignoz


current_file = Path(__file__)
current_file_dir = current_file.parent
static_root_absolute = str(current_file_dir / "static")


app = FastAPI(
    title='EDPAPI',
    version=os.environ['VERSION']
)

print(f'Current working directory: {os.getcwd()}')
print(f'Static directory: {static_root_absolute}')
print(f'Environment vars: {os.environ}')

app.mount("/static", StaticFiles(directory=static_root_absolute), name="static")
templates = Jinja2Templates(directory=static_root_absolute)

application_service: ApplicationService = ApplicationServiceSignoz()
span_service: SpanService = SpanServiceSignoz()
metric_service: MetricService = MetricServiceSignoz()
server_service: ServerService = ServerServiceSignoz()
experiment_service: ExperimentService = ExperimentServiceSignoz(span_service)

open_consoles: list[WebSocket] = []


@app.get("/health")
def get_health() -> str:
    return os.environ['VERSION']


@app.get("/apps")
def get_apps() -> list[str]:
    return application_service.get_apps()


@app.get('/apps/{app_name}/servers')
def get_servers(app_name: str) -> list[str]:
    return server_service.get_servers(app_name)


@app.get('/apps/{app_name}/spans/{span_name}')
def get_spans(
    app_name: str,
    span_name: str,
    length: int | None = None,
    start_time: int | None = None,
    duration: int | None = None,
) -> list[Span]:
    return span_service.get_spans(
        app_name=app_name,
        span_name=span_name,
        limit=length,
        start_time=start_time,
        duration=duration,
    )


@app.get('/apps/{app_name}/spans/{trace_id}/{span_id}/children')
def get_child_spans(
    app_name: str,
    trace_id: str,
    span_id: str,
) -> list[Span]:
    return span_service.get_child_spans(app_name, trace_id, span_id)


@app.get('/experiments')
def get_experiments() -> list[str]:
    return experiment_service.get_experiments()


@app.get('/experiments/{name}')
def get_experiment_by_name(name: str) -> list[Span]:
    return experiment_service.get_experiment_by_name(name)


@app.get('/experiments/{exp_name}/apps/{app_name}')
def get_experiment_statistics_for_app(
    exp_name: str,
    app_name: str,
    extra_statistics: bool = False,
    raw_data: bool = False,
    all: bool = False,
    nanos: bool = False,
) -> list[ExperimentStatistics] | list[SpanStatistics]:
    if all:
        exp_details = experiment_service.get_experiment_by_name(exp_name)
        start_time = min([e.timestamp for e in exp_details])
        end_time = max([e.timestamp + e.duration for e in exp_details])
        duration = end_time - start_time
        return span_service.get_span_statistics(
            app_name=app_name,
            start_time=start_time,
            duration=duration,
            extra_statistics=extra_statistics,
            raw_data=raw_data,
            nanos=nanos,
        )
    return experiment_service.get_experiment_statistics_for_app(
        exp_name=exp_name,
        app_name=app_name,
        extra_statistics=extra_statistics,
        raw_data=raw_data,
        nanos=nanos,
    )


@app.get('/servers/{server_name}/metrics/cpu')
def get_cpu(server_name: str, duration: int = 500) -> Cpu:
    return metric_service.get_cpu(server_name, duration)


@app.get('/servers/{server_name}/metrics/ram')
def get_ram(server_name: str, duration: int = 500) -> Ram:
    return metric_service.get_ram(server_name, duration)


@app.get("/", response_class=HTMLResponse)
async def get_frontend_page(request: Request):  # type: ignore
    return templates.TemplateResponse(
        request=request, name="index.html", context=dict(os.environ)
    )


@app.post("/console")
async def output_to_console(message: Message) -> None:
    print(message)
    for ws in open_consoles:
        await send_message_to_console(ws, message)


@app.websocket("/console/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    open_consoles.append(websocket)
    while True:
        data = await websocket.receive_text()
        headers = {
            'Content-Type': 'text/plain'
        }
        endpoint = f'http://{os.environ["COMMAND_TRANSLATOR_HOST"]}:{os.environ["COMMAND_TRANSLATOR_PORT"]}/translate/'
        try:
            response = requests.post(endpoint, headers=headers, data=data.encode())
            await send_message_to_console(websocket, Message(sender=endpoint, text=str(response)))
        except Exception as err:
            await send_message_to_console(websocket, Message(sender=endpoint, text=err))
