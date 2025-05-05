import os
import sys
from pathlib import Path

from clickhouse_connect.driver.exceptions import DatabaseError
from edpapi_fh_dortmund_project_emulate.common.DbService import DbService


DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")

DB_NAME = 'seqam_fh_dortmund_project_emulate'


def migrate(last_iter: int | None = None) -> bool:
    if os.environ.get('SEQAM_SKIP_MIGRATIONS'):
        return True
    if last_iter is None:
        try:
            res = DbService.query(f"SELECT max(iter) FROM {DB_NAME}._migrations")
        except DatabaseError as err:
            sys.stderr.write(f'{err.__class__} {err}')
            res = None
            DbService.query(f'''CREATE DATABASE IF NOT EXISTS {DB_NAME}''')
            DbService.query(f'''
            CREATE TABLE IF NOT EXISTS {DB_NAME}._migrations (
                iter UInt32,
                time DateTime
            ) ENGINE = MergeTree PRIMARY KEY (iter)
            ''')
        last_iter = res.result_rows[0][0] if res and res.result_rows else -1

    current_iter = last_iter + 1
    file_name = os.path.join(DATA_DIR, f'{current_iter:03}.sql')
    if not os.path.isfile(file_name):
        return True
    try:
        ddl = Path(file_name).read_text()
        DbService.query(ddl)
        DbService.query(f'''
            INSERT INTO {DB_NAME}._migrations (iter, time) VALUES ({current_iter}, NOW())
        ''')
        return migrate(current_iter)
    except Exception as err:
        sys.stderr.write(f'{err.__class__} {err}')
        return False
