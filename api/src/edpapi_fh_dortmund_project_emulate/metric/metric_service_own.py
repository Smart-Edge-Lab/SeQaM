import json
import sys
from datetime import datetime

from fastapi import HTTPException
from clickhouse_connect.driver.query import QueryResult
from clickhouse_connect.driver.exceptions import DatabaseError

from seqam_data_fh_dortmund_project_emulate.system_state import SystemState
from edpapi_fh_dortmund_project_emulate.common.DbService import DbService
from edpapi_fh_dortmund_project_emulate.metric.Cpu import Cpu, CpuService
from edpapi_fh_dortmund_project_emulate.metric.MetricService import MetricService, build_cpu_usage
from edpapi_fh_dortmund_project_emulate.metric.Ram import Ram
from edpapi_fh_dortmund_project_emulate.migration.migrator import DB_NAME


def _get_cpu_idle_times(host: str, t: float | None = None) -> tuple[float, dict[int, float]]:
    """
    Gets latest cpu idle times observation, but not newest as at time t,
    i.e. before time t. If no time t is given, then the newest available
    observation is returned.

    :param host: host name of IP address
    :param t: time, before what we are looking for the newest observation
    :return: actual time of the found observation and observation itself as a tuple
    """
    system_state = get_system_state_at(host, t)
    if not system_state:
        raise HTTPException(status_code=500, detail=f'Cannot get system {host} state at {t}')
    return system_state_to_cpu_idle_times(system_state)


def system_state_to_cpu_idle_times(system_state: SystemState) -> tuple[float, dict[int, float]]:
    return system_state.time, {
        core: idletime.idle for core, idletime in
        enumerate(system_state.cpu_state.core_times)
    }


def get_system_state_at(host: str, t: float | None = None) -> SystemState:
    """
    Return latest system state before time t.
    If no time t is supplied, then return the newest available system state observation.

    :param host: host name of IP address for what the system states were collected
    :param t: time before what we are looking for the newest system state observation
    :return: the latest system state before time t, if it was found
    """
    time_clause = f'AND time < {t}' if t else ''
    sql = f'''
    SELECT state
    FROM {DB_NAME}.metrics
    WHERE host = '{host}'
    {time_clause}
    ORDER BY time DESC
    LIMIT 1
    '''
    res = DbService.query(sql)
    if not res or not res.result_rows:
        raise HTTPException(status_code=500, detail=f'Cannot get system {host} state at {t}')
    row = next(iter(res.result_rows))
    return SystemState(**json.loads(row[0]))


def get_metrics_in_range(host_name: str, start_time: int, end_time: int) -> QueryResult:
    sql = f'''
        SELECT state
        FROM {DB_NAME}.metrics
        WHERE host = '{host_name}'
        AND time >= {start_time / 1000.0}
        AND time <= {end_time / 1000.0}
        ORDER BY time
        LIMIT 10000
    '''
    res = DbService.query(sql)
    if not res or not res.result_rows:
        raise HTTPException(
            status_code=500,
            detail=f'Cannot get system {host_name} states at {start_time}..{end_time}'
        )
    return res


class MetricServiceOwn(MetricService):
    def get_ram_series(self, server_name: str, start_time: int, end_time: int) -> list[Ram]:
        res = get_metrics_in_range(server_name, start_time, end_time)
        def system_state_to_ram(system_state: SystemState) -> Ram:
            return Ram(
                free=system_state.memory_state.available,
                total=system_state.memory_state.total,
                t=system_state.time,
                t_datetime=datetime.fromtimestamp(system_state.time),
            )
        return [
            system_state_to_ram(SystemState(**json.loads(row[0])))
            for row in res.result_rows
        ]

    def get_cpu_series(self, host_name: str, start_time: int, end_time: int) -> list[Cpu]:
        res = get_metrics_in_range(host_name, start_time, end_time)
        idle_time_seria = [
            system_state_to_cpu_idle_times(SystemState(**json.loads(row[0])))
            for row in res.result_rows
        ]
        return [
            build_cpu_usage(
                idle_time_seria[i][0],
                idle_time_seria[i+1][0],
                idle_time_seria[i][1],
                idle_time_seria[i+1][1]
            )
            for i in range(len(idle_time_seria)-1)
        ]

    def get_cpu(self, server_name: str, duration: int) -> Cpu:
        t1, idle_times_at_t1 = _get_cpu_idle_times(server_name)
        t0, idle_times_at_t0 = _get_cpu_idle_times(server_name, t1 - duration / 1000.0)
        return build_cpu_usage(t0, t1, idle_times_at_t0, idle_times_at_t1)

    def get_ram(self, server_name: str, duration: int) -> Ram:
        current_state = get_system_state_at(server_name)
        last_state = get_system_state_at(server_name, current_state.time - duration / 1000.0)
        return Ram(
            free=(current_state.memory_state.available + last_state.memory_state.available) / 2.0,
            total=(current_state.memory_state.total + last_state.memory_state.total) / 2.0
        )

    def submit_host_metrics(self, system_state: SystemState) -> SystemState:
        try:
            DbService.query(f"""
                INSERT INTO TABLE {DB_NAME}.metrics (host, time, state) 
                VALUES ('{system_state.host}', {system_state.time}, 
                    '{system_state.model_dump_json()}'
                )
            """)
            t1, idle_times_at_t1 = system_state_to_cpu_idle_times(system_state)
            cpu_usage = None
            last_cpu_idle_times = CpuService.get_last_idle_times(system_state.host) if system_state.host else None
            if last_cpu_idle_times:
                t0, idle_times_at_t0 = last_cpu_idle_times
                cpu_usage = build_cpu_usage(t0, t1, idle_times_at_t0, idle_times_at_t1)
            if system_state.host:
                CpuService.set_last_idle_times(system_state.host, t1, idle_times_at_t1)
            if cpu_usage:
                for cu in cpu_usage.cpu_load:
                    DbService.query(f"""
                        INSERT INTO TABLE {DB_NAME}.cpu_load (host, time, core, load) 
                        VALUES ('{system_state.host}', {system_state.time}, 
                            {cu.core}, {cu.percentage}
                        )
                    """)
        except DatabaseError as err:
            sys.stderr.write(f'{err.__class__} {err}')
        return system_state
