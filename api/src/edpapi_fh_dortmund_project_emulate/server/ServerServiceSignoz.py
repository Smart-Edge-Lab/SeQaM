from itertools import chain

from edpapi_fh_dortmund_project_emulate.common.DbService import DbService
from edpapi_fh_dortmund_project_emulate.common.utils import abort
from edpapi_fh_dortmund_project_emulate.server.ServerService import ServerService


class ServerServiceSignoz(ServerService):
    def get_servers(self, app: str | None = None) -> list[str]:
        sql = '''
        SELECT DISTINCT simpleJSONExtractString(labels, 'host_name')
        FROM signoz_metrics.distributed_time_series_v4
        '''
        r = DbService.query(sql)
        if r and isinstance(r.result_rows, list):
            return list(
                chain.from_iterable(r.result_rows)
            )
        abort(500, str(r))
        return []
