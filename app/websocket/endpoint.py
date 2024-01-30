from typing import Any

import anyio
from starlette.websockets import WebSocket

from app.logging import logger
from app.resources import broadcast
from app.websocket.client import Client
from app.websocket.lobby import LobbyClient
from app.websocket.game import GameClient


async def websocket_listener(socket: WebSocket) -> None:
    """
    Endpoint for websocket connections.
    """
    await socket.accept()

    async with anyio.create_task_group() as task_group:

        async def run_receiver(ws) -> None:
            await _receive(ws)
            task_group.cancel_scope.cancel()

        async def run_sender(ws) -> None:
            await _subscribe(ws)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_receiver, socket)
        task_group.start_soon(run_sender, socket)


async def _subscribe(socket: WebSocket) -> None:
    """
    Subscribes websocket to a channel.
    """

    channel = _get_channel(socket)
    if channel is None:
        return

    async with broadcast.subscribe(channel=str(channel)) as subscriber:
        async for event in subscriber:
            message = event.message
            await socket.send_text(message)


async def _receive(ws: WebSocket) -> None:
    """
    Receives messages from socket.
    """

    client = _get_client(ws)
    if client is None:
        return

    await client.receive_loop()


def _get_channel(socket: WebSocket) -> Any:
    game_id = socket.path_params.get("game_id")
    if game_id is not None:
        try:
            game_id = int(game_id)
        except ValueError:
            logger.warn(
                "attempt socket to connect invalid channel game_id=%s: %s",
                game_id,
                socket.client,
            )
            return None
        else:
            return game_id
    return "lobby"


def _get_client(socket: WebSocket) -> Client | None:
    channel = _get_channel(socket=socket)
    if channel is None:
        return None
    if channel == "lobby":
        return LobbyClient(socket=socket)
    else:
        return GameClient(socket=socket, game_id=channel)
