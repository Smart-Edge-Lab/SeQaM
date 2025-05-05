import random
import re
from threading import Thread
from typing import Callable

from ModuleManagement.DataModels.event import Event, StressEvent, StressMode
from ModuleManagement.os_utils import run_event_command


def get_time_value_and_unit(stress_event) -> tuple[int, str]:
    _time_and_unit = re.findall(r'(\d+)(\w+)', stress_event.time)
    _time = 0
    _time_unit = ''
    if _time_and_unit:
        _time, _time_unit = _time_and_unit[0]
    return int(_time), _time_unit


def apply_random_stress(stress_event: StressEvent) -> list[StressEvent]:
    _time, _time_unit = get_time_value_and_unit(stress_event)
    commands = []
    time_step = stress_event.time_step or 1
    load_max = stress_event.load_max or 100
    load_min = stress_event.load_min or 0
    load_step = stress_event.load_step or 1
    new_load = int(stress_event.load)
    elapsed = 0
    random.seed(stress_event.random_seed)
    while elapsed < _time:
        new_load += random.randint(-load_step, load_step)
        if new_load < load_min:
            new_load = load_min
        elif new_load > load_max:
            new_load = load_max
        subevent = stress_event.model_copy(
            update=dict(
                time=f'{time_step}{_time_unit}',
                load=f'{new_load}',
            )
        )
        commands.append(subevent)
        elapsed += time_step
    return commands


def apply_increasing_stress(stress_event: StressEvent) -> list[StressEvent]:
    _time, _time_unit = get_time_value_and_unit(stress_event)
    commands = []
    time_step = stress_event.time_step or 1
    load_max = stress_event.load_max or 100
    load_min = stress_event.load_min or 0
    new_load = int(stress_event.load_min or 0)
    elapsed = 0
    while elapsed < _time:
        subevent = stress_event.model_copy(
            update=dict(
                time=f'{time_step}{_time_unit}',
                load=f'{new_load}',
            )
        )
        commands.append(subevent)
        new_load += stress_event.load_step or 1
        if new_load < load_min:
            new_load = load_min
        elif new_load > load_max:
            new_load = load_max
        elapsed += time_step
    return commands


def apply_decreasing_stress(stress_event: StressEvent) -> list[StressEvent]:
    _time, _time_unit = get_time_value_and_unit(stress_event)
    commands = []
    time_step = stress_event.time_step or 1
    load_max = stress_event.load_max or 100
    load_min = stress_event.load_min or 0
    new_load = int(stress_event.load_max or 50)
    elapsed = 0
    while elapsed < _time:
        subevent = stress_event.model_copy(
            update=dict(
                time=f'{time_step}{_time_unit}',
                load=f'{new_load}',
            )
        )
        commands.append(subevent)
        new_load -= stress_event.load_step or 1
        if new_load < load_min:
            new_load = load_min
        elif new_load > load_max:
            new_load = load_max
        elapsed += time_step
    return commands


def apply_stress(stress_event: StressEvent, construct_stress_event: Callable[[Event], str], do_shlex: bool, **kwargs) -> Thread | None:
    if stress_event.mode in (StressMode.static, None):
        stress_events = [stress_event]
    elif stress_event.mode == StressMode.random:
        stress_events = apply_random_stress(stress_event)
    elif stress_event.mode == StressMode.increasing:
        stress_events = apply_increasing_stress(stress_event)
    elif stress_event.mode == StressMode.decreasing:
        stress_events = apply_decreasing_stress(stress_event)
    else:
        raise Exception('Unimplemented stress mode')
    return run_event_command(stress_events, construct_stress_event, stress_event, do_shlex, **kwargs)