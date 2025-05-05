from starlette.websockets import WebSocket

from edpapi_fh_dortmund_project_emulate.console.message import Message


async def send_message_to_console(ws: WebSocket, message: Message) -> None:
    try:
        await ws.send_text(message.model_dump_json())
    except Exception as err:
        print(err)
