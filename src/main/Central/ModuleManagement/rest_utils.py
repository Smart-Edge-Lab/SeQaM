import json
import os
import sys
from typing import Any

from flask import request
import requests  # type: ignore
from requests import Response

EXPERIMENT_CONTEXT_HEADER = 'ExperimentContext'


def request_json_with_headers() -> dict:
    """
    Returns request json enriched with
    headers field.
    """
    request_body = request.get_json()
    request_body['headers'] = dict(request.headers)
    return request_body


def get_experiment_context(headers: dict | None) -> dict | None:
    return json.loads(
        headers.get(EXPERIMENT_CONTEXT_HEADER, '')
    ) if headers and EXPERIMENT_CONTEXT_HEADER in headers else None


def api_post(api_path: str, body: dict[str, Any]) -> Response:
    try:
        url = f'http://{os.environ["API_HOST"]}:{os.environ["API_PORT"]}{api_path}'
        return requests.post(url, json=body)
    except Exception as err:
        sys.stderr.write(f'{err.__class__.__name__} {err}')
