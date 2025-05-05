from fastapi import HTTPException

from edpapi_fh_dortmund_project_emulate.common.DbService import DbService
from edpapi_fh_dortmund_project_emulate.metric.Cpu import Cpu
from edpapi_fh_dortmund_project_emulate.metric.MetricService import MetricService, build_cpu_usage
from edpapi_fh_dortmund_project_emulate.metric.Ram import Ram
from seqam_data_fh_dortmund_project_emulate.system_state import SystemState


def _get_last_cpu_measurement_time(server_name: str, where: str = '') -> int:
    """
    Get unix timestamp when the last CPU measurement was taken

    :param server_name: host name where the measurement take place
    :param where: optional additional where clause
    :return: unix timestamp when the last CPU measurement was taken
    """
    sql = f'''
                SELECT unix_milli
                FROM signoz_metrics.distributed_samples_v4
                INNER JOIN signoz_metrics.distributed_time_series_v4 
                    ON signoz_metrics.distributed_time_series_v4.fingerprint = 
                        signoz_metrics.distributed_samples_v4.fingerprint
                WHERE (metric_name = 'system_cpu_time') 
                    AND (simpleJSONExtractString(labels, 'state') = 'idle') 
                    AND (simpleJSONExtractString(labels, 'host_name') = '{server_name}')
                    {where}
                ORDER BY unix_milli DESC
                LIMIT 1
            '''
    r = DbService.query(sql)
    return int(r.result_rows[0][0]) if r and r.result_rows else 0


def _cumulative_cpu_idle_at(server_name: str, t: int) -> dict[int, float]:
    """
    Get total seconds each logical CPU was idle
    at time instant t

    :param server_name: server name to get the counter for
    :param t: time instant in question
    :return: dictionary, where key is a cpu core index,
        and value is the cumulative amount of milliseconds it was idle.
    """
    sql = f'''
        SELECT DISTINCT simpleJSONExtractString(labels, 'cpu'),
            value
        FROM signoz_metrics.distributed_samples_v4
        INNER JOIN signoz_metrics.distributed_time_series_v4 
            ON signoz_metrics.distributed_time_series_v4.fingerprint = 
                signoz_metrics.distributed_samples_v4.fingerprint
        WHERE (metric_name = 'system_cpu_time') 
            AND (simpleJSONExtractString(labels, 'state') = 'idle') 
            AND (simpleJSONExtractString(labels, 'host_name') = '{server_name}') 
            AND (unix_milli = {t})
    '''
    r = DbService.query(sql)
    return {
        int(m[0].replace('cpu', '')): m[1] * 1000
        for m in r.result_rows
    } if r else {}


def _latest_ram_measurement_time(server_name: str) -> int:
    sql = f'''
    SELECT unix_milli
    FROM signoz_metrics.distributed_time_series_v4
    WHERE (metric_name = 'system_memory_usage') 
        AND (simpleJSONExtractString(labels, 'host_name') = '{server_name}')
    ORDER BY unix_milli DESC
    LIMIT 1
    '''
    r = DbService.query(sql)
    return int(r.result_rows[0][0]) if r and r.result_rows else 0


def _average_ram_for_state(server_name: str, state: str, start_time: int) -> float:
    """
    Returns a mean Gigabyte value of ram on server host in `state`
    starting from the specified time

    :param server_name: server hostname
    :param state: state of the ram like "used" or "free"
    :param start_time: time from what the measurements are collected
    :returns: Average memory amount in Gigabytes
    """
    sql = f'''
    SELECT AVG(value)
    FROM signoz_metrics.distributed_samples_v4
    INNER JOIN signoz_metrics.distributed_time_series_v4 
        ON signoz_metrics.distributed_time_series_v4.fingerprint = signoz_metrics.distributed_samples_v4.fingerprint
    WHERE (metric_name = 'system_memory_usage')
        AND (simpleJSONExtractString(labels, 'host_name') = '{server_name}') 
        AND (simpleJSONExtractString(labels, 'state') = '{state}') 
        AND (unix_milli > {start_time})
    '''
    r = DbService.query(sql)
    return float(
        r.result_rows[0][0]/1024/1024/1024 if r and r.result_rows else 0
    )


class MetricServiceSignoz(MetricService):
    def get_ram_series(self, server_name: str, start_time: int, end_time: int) -> list[Ram]:
        raise HTTPException(
            status_code=501,
            detail='Not implemented in MetricServiceSignoz. See other implementations of MetricService'
        )

    def submit_host_metrics(self, system_state: SystemState) -> SystemState:
        raise HTTPException(
            status_code=501,
            detail='Not implemented in MetricServiceSignoz. See other implementations of MetricService'
        )

    def get_cpu_series(self, host_name: str, start_time: int, end_time: int) -> list[Cpu]:
        raise HTTPException(
            status_code=501,
            detail='Not implemented in MetricServiceSignoz. See other implementations of MetricService'
        )

    def get_cpu(self, server_name: str, duration: int) -> Cpu:
        t1 = _get_last_cpu_measurement_time(server_name)
        t0 = _get_last_cpu_measurement_time(server_name, f'AND unix_milli < {t1 - duration}')
        cpu_t1 = _cumulative_cpu_idle_at(server_name, t1)
        cpu_t0 = _cumulative_cpu_idle_at(server_name, t0)
        return build_cpu_usage(t0, t1, cpu_t0, cpu_t1)

    def get_ram(self, server_name: str, duration: int) -> Ram:
        t_now = _latest_ram_measurement_time(server_name)
        start_time = t_now - duration
        free = _average_ram_for_state(server_name, 'free', start_time)
        used = _average_ram_for_state(server_name, 'used', start_time)
        return Ram(
            free=free,
            total=used + free
        )
