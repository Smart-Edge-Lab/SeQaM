import shlex
import subprocess
import threading
from threading import Thread
from typing import Callable, Sequence

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from ModuleManagement.DataModels.event import Event
from ModuleManagement.otlp_utils import OnlyTracer
from ModuleManagement.DataModels.event import StressMode


def run_os_process(command_args: list[str] | str, **kwargs):
    print(command_args)
    return subprocess.Popen(command_args, **kwargs)


def run_os_process_await(command_args: list[str] | str, **kwargs):
    return run_os_process(command_args, **kwargs).communicate()


def run_event_command(sub_events: Sequence[Event], cmd_from_event: Callable[[Event], str], event: Event, do_shlex: bool, **kwargs) -> Thread | None:
    def _run_without_context() -> None:
        for se in sub_events:
            cmd = cmd_from_event(se)
            run_os_process_await(shlex.split(cmd) if do_shlex else cmd, **kwargs)

    def _run_with_context() -> None:
        ctx = TraceContextTextMapPropagator().extract(carrier=event.experiment_context)
        if getattr(event, 'mode', None) in [StressMode.increasing, StressMode.decreasing]:
            for se in sub_events:
                cmd = cmd_from_event(se)
                with OnlyTracer.get().start_as_current_span(se.get_console_command(), context=ctx):
                    run_os_process_await(shlex.split(cmd) if do_shlex else cmd, **kwargs)
        else:
            with OnlyTracer.get().start_as_current_span(event.get_console_command(), context=ctx):
                _run_without_context()

    t = threading.Thread(target=_run_with_context if event.experiment_context else _run_without_context)
    t.start()
    return t
