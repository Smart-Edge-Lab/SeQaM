import requests  # type: ignore

from ModuleManagement.rest_utils import api_post


def output_to_console(sender: str, text: str | Exception) -> None:
    print(f'{sender} >>> {text}')

    is_error = isinstance(text, Exception)
    formatted_text = (
        f'{text.__class__.__name__} {text}' if is_error else text
    )
    body = dict(
        text=formatted_text,
        sender=sender,
        error=400 if is_error else 0,
    )
    api_post('/console', body)
