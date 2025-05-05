import logging
import os

from clickhouse_connect.driver.query import QueryResult

from edpapi_fh_dortmund_project_emulate.common.utils import abort, trim_sql

import clickhouse_connect
from clickhouse_connect.driver.client import Client


logger = logging.getLogger(__name__)


class DbService:
    _client = None

    @staticmethod
    def get_client() -> Client | None:
        if not DbService._client:
            clickhouse_endpoint = os.environ.get('DATABASE_ENDPOINT')
            if clickhouse_endpoint:
                DbService._client = clickhouse_connect.get_client(host=clickhouse_endpoint)
            else:
                abort(
                    500,
                    'Please specify the DATABASE_ENDPOINT environment variable'
                )
        return DbService._client

    @staticmethod
    def query(sql: str) -> QueryResult | None:
        client = DbService.get_client()
        result = client.query(sql) if client else None
        logger.debug(f'{trim_sql(sql)} returns {result.result_rows if result else None}')
        return result
