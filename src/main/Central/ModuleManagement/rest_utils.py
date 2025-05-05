import json

from flask import request


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
