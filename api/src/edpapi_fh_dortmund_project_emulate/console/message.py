from pydantic import BaseModel


class Message(BaseModel):
    error: int = 0
    sender: str
    text: str

    def __init__(self, **kwargs) -> None:  # type: ignore
        text = kwargs.get('text')
        if isinstance(text, Exception):
            kwargs['text'] = f'{text.__class__.__name__} {text}'
            kwargs['error'] = 400
        super().__init__(**kwargs)
