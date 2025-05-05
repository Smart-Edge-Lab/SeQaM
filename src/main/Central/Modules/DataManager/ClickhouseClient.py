from typing import Sequence

import clickhouse_connect
import ast

from clickhouse_connect.driver import Client
from clickhouse_connect.driver.summary import QuerySummary


class ClickhouseClient:
    """
    Class used to interact with the clickhouse data base it 
    is abstracted by the DBclient module. Therefore, hre only the 
    queries are contained
    """

    def __init__(self) -> None:
        self._client_: Client | None = None


    def create_client(self, db_host="127.0.0.1"):
        self._client_ = clickhouse_connect.get_client(host = db_host)


    def get_client(self):
        return self._client_ 
    

    def send_generic_query(self, query: str) -> int | Sequence[str] | QuerySummary | None:
        return self._client_.command(query) if self._client_ else None


    def get_single_core_idle(self, cpu_name, host_name, time_difference):
        
        cpu_state = 'idle'
        single_core_query = f"""
        WITH 
        -- Step 1: Get the fingerprint dynamically
        fingerprint_cte AS (
            SELECT fingerprint
            FROM signoz_metrics.distributed_time_series_v4
            WHERE 
                metric_name = 'system_cpu_time' 
                AND simpleJSONExtractString(labels, 'host_name') = '{host_name}' 
                AND simpleJSONExtractString(labels, 'cpu') = '{cpu_name}' 
                AND simpleJSONExtractString(labels, 'state') = '{cpu_state}'
            ORDER BY unix_milli DESC 
            LIMIT 1
        ),
        -- Step 2: Get the latest timestamp and value
        latest AS (
            SELECT unix_milli, value
            FROM signoz_metrics.samples_v4
            WHERE 
                metric_name = 'system_cpu_time' 
                AND fingerprint = (SELECT fingerprint FROM fingerprint_cte)
            ORDER BY unix_milli DESC
            LIMIT 1
        ),
        -- Step 3: Calculate the target timestamp (latest - {time_difference} milliseconds)
        target_time AS (
            SELECT (unix_milli - {time_difference}) AS target_unix_milli
            FROM latest
        ),
        -- Step 4: Find the row closest to the target timestamp
        closest AS (
            SELECT 
                value AS closest_value,
                unix_milli AS closest_unix_milli
            FROM signoz_metrics.samples_v4
            WHERE 
                metric_name = 'system_cpu_time'
                AND fingerprint = (SELECT fingerprint FROM fingerprint_cte)
            ORDER BY abs(unix_milli - (SELECT target_unix_milli FROM target_time)) ASC
            LIMIT 1
        )
        -- Step 5: Calculate the value difference
        SELECT 
            l.value - c.closest_value AS value_difference,
            l.unix_milli AS latest_unix_milli,
            c.closest_unix_milli AS closest_unix_milli
        FROM 
            latest l,
            closest c;
        """
        result = self._client_.command(single_core_query)
        
        if isinstance(result, list):
            #fist parameter is in seconds, parameters of the division come in milliseconds, need to adjust, thus it multiplies by 1000
            normalized_load = 100 - (float(result[0]) * 100 * 1000)/(float(result[1]) - float(result[2]))
            result.append(normalized_load)

        return result


    def get_all_cores_idle(self, host_name, time_difference):

        cpus_query = f"""
        SELECT DISTINCT simpleJSONExtractString(labels, 'cpu') AS cpu_name
        FROM signoz_metrics.distributed_time_series_v4_6hrs
        WHERE (metric_name = 'system_cpu_time') AND (simpleJSONExtractString(labels, 'host_name') = '{host_name}')
        ORDER BY cpu_name ASC
        """
        core_information = {}

        response = self._client_.command(cpus_query)
        cpu_list = response.split("\n")

        for cpu in cpu_list:
            core_info = self.get_single_core_idle(cpu_name = cpu, host_name = host_name, time_difference = time_difference )
            
            core_information[cpu] = core_info
        
        return core_information


    def get_raw_memory_usage(self, host_name):

        query = f"""
        WITH
            used_memory_fingerprints AS (
                SELECT DISTINCT
                    fingerprint,
                    simpleJSONExtractString(labels, 'state') AS state
                FROM signoz_metrics.distributed_time_series_v4
                WHERE (metric_name = 'system_memory_usage') 
                    AND (simpleJSONExtractString(labels, 'host_name') = '{host_name}') 
            ),
            latest_values AS (
                SELECT
                    fingerprint,
                    unix_milli,
                    value,
                    ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY unix_milli DESC) AS rn
                FROM signoz_metrics.samples_v4
                WHERE metric_name = 'system_memory_usage'
            ),
            combined AS (
                SELECT
                    lv.value AS latest_value,
                    lv.unix_milli AS latest_unix_milli,
                    uf.state
                FROM latest_values AS lv
                INNER JOIN used_memory_fingerprints AS uf ON lv.fingerprint = uf.fingerprint
                WHERE lv.rn = 1
            )
        SELECT array_agg((latest_value, latest_unix_milli, state)) AS result_array
        FROM combined
        """

        result = self._client_.command(query)
        
        return ast.literal_eval(result)


    def get_memory_usage_percentage(self, host_name):

        total_memory = 0
        used_memory = 0
        other_memory = 0
        free_memory = 0
        for item in self.get_raw_memory_usage(host_name):       
            if item[2] == 'free':
                free_memory = item[0]
            elif item[2] == 'used':
                used_memory = item[0]
            else:
                other_memory += item[0]

        total_memory = free_memory + used_memory + other_memory
            
        return (used_memory/total_memory)*100


    def get_cpu_load_avg(self, host_name,time_avg):
        
        query = f"""
        WITH
            cpu_load_fingerprints AS (
                SELECT DISTINCT
                    fingerprint,
                    metric_name AS metric_name
                FROM signoz_metrics.distributed_time_series_v4
                WHERE (metric_name = '{time_avg}') 
                    AND (simpleJSONExtractString(labels, 'host_name') = '{host_name}')
            ),
            latest_values AS (
                SELECT
                    fingerprint,
                    unix_milli,
                    value,
                    ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY unix_milli DESC) AS rn
                FROM signoz_metrics.samples_v4
                WHERE metric_name = '{time_avg}'
            ),
            combined AS (
                SELECT
                    lv.value AS latest_value,
                    lv.unix_milli AS latest_unix_milli,
                    uf.metric_name
                FROM latest_values AS lv
                INNER JOIN cpu_load_fingerprints AS uf ON lv.fingerprint = uf.fingerprint
                WHERE lv.rn = 1
            )
        SELECT array_agg((latest_value, latest_unix_milli, metric_name)) AS result_array
        FROM combined
        """

        result = self._client_.command(query)

        return ast.literal_eval(result)


    def get_cpu_load_15m(self, host_name):

        return self.get_cpu_load_avg(host_name, 'system_cpu_load_average_15m')
    

    def get_cpu_load_5m(self, host_name):

        return self.get_cpu_load_avg(host_name, 'system_cpu_load_average_5m')
    

    def get_cpu_load_1m(self, host_name):

        return self.get_cpu_load_avg(host_name, 'system_cpu_load_average_1m')
    

    def get_trace_avg_number_based(self, trace_size, traces_to_avg):

        _limit_ = trace_size * traces_to_avg
        query = f"""
        SELECT 
        AVG(duration) / 1000000 AS latency, 
        metrics  
        FROM 
            (SELECT 
                simpleJSONExtractString(model, 'name') AS metrics , 
                simpleJSONExtractInt(model, 'durationNano') AS duration 
            FROM 
                signoz_traces.signoz_spans 
            ORDER BY 
                timestamp DESC 
            LIMIT {_limit_}
            ) 
        GROUP BY 
        metrics ;
        """

        result = self._client_.command(query)

        return result

        
    def get_span_avg_time_based(self, span_name, limit_time = '1716284654061083614'):

        query = f"""
        SELECT  
            MAX(simpleJSONExtractInt(model, 'startTimeUnixNano')) AS max_unix,
            MAX(timestamp) AS max_timestamp, 
            AVG(simpleJSONExtractInt(model, 'durationNano')) / 1000000 AS duration, 
            COUNT(name) AS count, 
            simpleJSONExtractString(model, 'name') AS name
        FROM 
            signoz_traces.signoz_spans
        WHERE 
            name = '{span_name}' 
            AND simpleJSONExtractInt(model, 'startTimeUnixNano') > '{limit_time}'
        GROUP BY 
            name;
        """
        result = self._client_.command(query)

        return result
