import re

from fastapi import HTTPException


def abort(http_status: int, message: str) -> None:
    raise HTTPException(status_code=http_status, detail=message)


def trim_sql(sql: str) -> str:
    return re.sub(r'\s+', ' ', sql).strip()
