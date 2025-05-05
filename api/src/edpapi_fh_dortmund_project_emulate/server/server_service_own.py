from itertools import chain

from edpapi_fh_dortmund_project_emulate.common.DbService import DbService
from edpapi_fh_dortmund_project_emulate.common.utils import abort
from edpapi_fh_dortmund_project_emulate.migration.migrator import DB_NAME
from edpapi_fh_dortmund_project_emulate.server.ServerService import ServerService


class ServerServiceOwn(ServerService):
    def get_servers(self, app: str | None = None) -> list[str]:
        try:
            r = DbService.query(f'''
            SELECT DISTINCT host FROM {DB_NAME}.metrics
            ''')
        except Exception as err:
            abort(500, str(err))
            r = None
        return list(
            chain.from_iterable(r.result_rows)
        ) if r and r.result_rows else []
