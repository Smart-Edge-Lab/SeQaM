import unittest
from typing import Any
from unittest.mock import patch

from edpapi_fh_dortmund_project_emulate.common.utils import trim_sql


_MOCKS: dict[str, list[Any]] = {
     'SELECT toUnixTimestamp64Milli(timestamp), durationNano, traceID, spanID, name, numberTagMap '
     'FROM signoz_traces.distributed_signoz_index_v2 '
     "WHERE serviceName='image_processing' "
     "AND name='aruco_detection' "
     'AND toUnixTimestamp64Milli(timestamp) >= 1721900595500 '
     'AND toUnixTimestamp64Milli(timestamp) <= 1721900596500 '
     'order by timestamp desc': [
        [1721900595500, 6746250, 'tid', 'sid', 'nit', {'some': 'thing'}]
    ],
    "SELECT toUnixTimestamp64Milli(timestamp), durationNano, traceID, spanID, name, numberTagMap "
    "FROM signoz_traces.distributed_signoz_index_v2 WHERE serviceName='experiment_dispatcher_fh_dortmund_project_emulate'"
    " AND name='pigovsky-2024-10-07T11:38' order by timestamp desc limit 1": [
        (1728298110312, 4997839659, b'60ee0811e6d89e4ba03ab4fcf9ca2c71', '15eb5e0cc70315a1', 'pigovsky-2024-10-07T11:38', {})
    ],
    "SELECT toUnixTimestamp64Milli(timestamp), durationNano, traceID, spanID, name, numberTagMap FROM "
    "signoz_traces.distributed_signoz_index_v2 WHERE (parentSpanID = '15eb5e0cc70315a1') AND "
    "(traceID = '60ee0811e6d89e4ba03ab4fcf9ca2c71') order by timestamp": [
        (1728298110334, 5316150988, b'60ee0811e6d89e4ba03ab4fcf9ca2c71', '28c3800741d5a71c',
         'cpu_load comment:partition-point=1 time:5s load:10 src_device_type:ue src_device_name:ue001 '
         'mode:inc load_min:10 load_max:99 load_step:10 time_step:1 cores:5', {}),
        (1728298111330, 10010922250, b'60ee0811e6d89e4ba03ab4fcf9ca2c71', '897841e614e1c57e',
         'network_load time:10s load:10 src_device_type:ue src_device_name:ue002 dst_device_type:server '
         'dst_device_name:srv001 destination_host:172.22.174.190', {}),
        (1728298111352, 10014899268, b'60ee0811e6d89e4ba03ab4fcf9ca2c71', 'f2db8350e8f25965',
         'network_load time:10s load:10 src_device_type:ue src_device_name:ue002 dst_device_type:server '
         'dst_device_name:srv002 destination_host:192.168.122.194', {})
    ],
    "SELECT name, MIN(durationNano), AVG(durationNano), MAX(durationNano), COUNT(1), FROM "
    "signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND toUnixTimestamp64Milli(timestamp) >= "
    "1728298110334 AND toUnixTimestamp64Milli(timestamp) <= 1728298111330 GROUP BY name": [],
    "SELECT name, MIN(durationNano), AVG(durationNano), MAX(durationNano), COUNT(1), FROM "
    "signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND toUnixTimestamp64Milli(timestamp) >= "
    "1728298111330 AND toUnixTimestamp64Milli(timestamp) <= 1728298111352 GROUP BY name": [],
    "SELECT name, MIN(durationNano), AVG(durationNano), MAX(durationNano), COUNT(1), FROM "
    "signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND toUnixTimestamp64Milli(timestamp) >= "
    "1728298111352 AND toUnixTimestamp64Milli(timestamp) <= 1728298115650 GROUP BY name": [
        ('SQL SELECT', 246965000, 332921500.0, 545586000, 6)
    ],
    "SELECT toUnixTimestamp64Milli(timestamp), durationNano, traceID, spanID, name, numberTagMap "
    "FROM signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND name='SQL SELECT' AND "
    "toUnixTimestamp64Milli(timestamp) >= 1728298111352 AND toUnixTimestamp64Milli(timestamp) <= 1728298115650 "
    "order by timestamp desc": [
        (1728298115217, 251117000, b'000000000000000054dfbf42358775ad', '3d74b21c1538fab0', 'SQL SELECT', {}),
        (1728298114499, 405081000, b'00000000000000002304a16bbb4a6a5f', '16982c958dffa980', 'SQL SELECT', {}),
        (1728298114349, 257322000, b'00000000000000005db0f8747b1b575e', '1c2856dab26bcd1c', 'SQL SELECT', {}),
        (1728298112630, 246965000, b'00000000000000002085d72c041eb426', '587446c96e565f10', 'SQL SELECT', {}),
        (1728298111922, 545586000, b'00000000000000002f5f77e087216eb5', '6900e18f95989201', 'SQL SELECT', {}),
        (1728298111882, 291458000, b'00000000000000002827e23bf9a6dbed', '70ef03d9c58b6bb8', 'SQL SELECT', {})
    ],
    "SELECT name, MIN(durationNano), AVG(durationNano), MAX(durationNano), COUNT(1), "
    "FROM signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND toUnixTimestamp64Milli(timestamp) "
    ">= 1728298115650 AND toUnixTimestamp64Milli(timestamp) <= 1728298121340 GROUP BY name": [
        ('SQL SELECT', 275672000, 313730000.0, 357792000, 6)
    ],
    "SELECT toUnixTimestamp64Milli(timestamp), durationNano, traceID, spanID, name, numberTagMap FROM signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND name='SQL SELECT' AND toUnixTimestamp64Milli(timestamp) >= 1728298115650 AND toUnixTimestamp64Milli(timestamp) <= 1728298121340 order by timestamp desc": [
        (1728298121053, 349876000, b'0000000000000000485d5e3281bdb19d', '09443d72215aac3b', 'SQL SELECT', {}),
        (1728298120851, 303842000, b'0000000000000000535daf164a234cc3', '378eca99426a6dc3', 'SQL SELECT', {}),
        (1728298118863, 357792000, b'0000000000000000242336f845f1e766', '12542eb361feef54', 'SQL SELECT', {}),
        (1728298118591, 319505000, b'0000000000000000329f35bf26bd29b8', '3c0bbc06911bc212', 'SQL SELECT', {}),
        (1728298117347, 275693000, b'00000000000000002bd993f332ca6c5b', '1fb7509bb8708e47', 'SQL SELECT', {}),
        (1728298116843, 275672000, b'00000000000000002a38d632b4deb8ca', '468388df3cf39a67', 'SQL SELECT', {})
    ],
    "SELECT name, MIN(durationNano), AVG(durationNano), MAX(durationNano), COUNT(1), "
    "FROM signoz_traces.distributed_signoz_index_v2 WHERE serviceName='mysql' AND toUnixTimestamp64Milli(timestamp) "
    ">= 1728298121340 AND toUnixTimestamp64Milli(timestamp) <= 1728298121366 GROUP BY name": []
}


class MockResult:
    def __init__(self, result_rows: list[Any]):
        self.result_rows = result_rows


class MockClient:
    def __init__(self) -> None:
        self.query_log: list[str] = []

    def query(self, sql: str) -> MockResult:
        trimmed_sql = trim_sql(sql)
        self.query_log.append(trimmed_sql)
        res = _MOCKS.get(trimmed_sql, [])
        return MockResult(res)


class DbServiceMockTest(unittest.TestCase):
    def setUp(self) -> None:
        self.db_service_patcher = patch('edpapi_fh_dortmund_project_emulate.common.DbService.DbService.get_client')
        self.db_service_mock = self.db_service_patcher.start()
        self.db_service_mock.return_value = MockClient()

    def tearDown(self) -> None:
        self.db_service_patcher.stop()
