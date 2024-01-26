import typing

import anyio
from starlette.websockets import WebSocket

from app.resources import broadcast
from app.websocket.dispatch import Client, GameClient, LobbyClient


async def websocket_listener(ws: WebSocket) -> None:
    """WebSocket connection endpoint"""
    await ws.accept()

    async with anyio.create_task_group() as task_group:

        async def run_receive() -> None:
            await _websocket_receiver(ws)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_receive)
        await _websocket_sender(ws)


async def _websocket_sender(ws: WebSocket) -> None:
    """Send json data to clients"""

    room: int | typing.Literal["lobby"] = ws.path_params.get("game_id", "lobby")
    async with broadcast.subscribe(channel=str(room)) as subscriber:
        async for event in subscriber:
            await ws.send_json(event.message)


def get_client(socket: WebSocket) -> Client | None:
    game_id = socket.path_params.get("game_id")
    if game_id is not None:
        try:
            game_id = int(game_id)
        except ValueError:
            return None
        return GameClient(socket=socket, game_id=game_id)
    return LobbyClient(socket=socket)

async def _websocket_receiver(ws: WebSocket) -> None:
    """Receive json data from clients"""

    client = get_client(ws)
    if client is None:
        return

    async for msg in ws.iter_json():
        typing.cast(dict[str, typing.Any], msg)
        await client.on_message(msg)
