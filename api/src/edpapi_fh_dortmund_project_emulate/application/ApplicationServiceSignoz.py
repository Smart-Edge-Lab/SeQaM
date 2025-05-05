from itertools import chain
from typing import List

from edpapi_fh_dortmund_project_emulate.common.utils import abort

from edpapi_fh_dortmund_project_emulate.application.ApplicationService import ApplicationService
from edpapi_fh_dortmund_project_emulate.common.DbService import DbService


class ApplicationServiceSignoz(ApplicationService):
    def get_apps(self) -> List[str]:
        sql = '''
            SELECT distinct serviceName as app 
            FROM signoz_traces.distributed_signoz_index_v2
            WHERE app != '' 
                AND timestamp > now() - INTERVAL 30 DAY
        '''
        return self.get_str_list(sql)

    @staticmethod
    def get_str_list(sql: str) -> list[str]:
        r = DbService.query(sql)
        if r and isinstance(r.result_rows, list):
            return list(
                chain.from_iterable(r.result_rows)
            )
        abort(500, str(r))
        return []
