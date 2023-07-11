import typing

import anyio
from starlette.websockets import WebSocket

from app.database.database import get_session
from app.resources import broadcast
from app.websocket.dispatch import Dispatcher


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


async def _websocket_receiver(ws: WebSocket) -> None:
    """Receive json data from clients"""

    async for msg in ws.iter_json():
        msg = typing.cast(dict[str, typing.Any], msg)
        action = msg.get("action", "")
        data = msg.get("data", {})

        async with get_session() as session:
            # if ws.session.get("game_id") == "lobby": await LobbyDispatcher...
            await Dispatcher(session, ws, action, data).dispatch()
