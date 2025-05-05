import os

import requests  # type: ignore


def output_to_console(sender: str, text: str | Exception) -> None:
    print(f'{sender} >>> {text}')
    url = f'http://{os.environ["API_HOST"]}:{os.environ["API_PORT"]}/console'

    is_error = isinstance(text, Exception)
    formatted_text = (
        f'{text.__class__.__name__} {text}' if is_error else text
    )
    body = dict(
        text=formatted_text,
        sender=sender,
        error=400 if is_error else 0,
    )
    try:
        r = requests.post(url, json=body)
        print(f'api responds {r}')
    except Exception as err:
        print(err)
