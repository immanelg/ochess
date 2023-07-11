import asyncio
from typing import Any, Awaitable, Callable, Literal

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from app import schemas
from app.database.service import GameRepository
from app.resources import broadcast
from app.validation import validated_json

# refactor:

# class AbstractDispatcher:
#     ws: WebSocket
#     action: str
#     data: dict[str, typing.Any]
#     room: str
#     user: User
#     session: AsyncSession
#     handlers: dict[str, Handler]

# class LobbyDispatcher(AbstractDispatcher):
#     ...

# class GameDispatcher(AbstractDispatcher):
#     ...


class Dispatcher:
    """Dispatches event sent by WS client."""

    ws: WebSocket
    action: str
    data: dict[str, Any]
    room: int | Literal["lobby"]
    user_id: int
    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        ws: WebSocket,
        action: str,
        data: dict[str, Any],
    ) -> None:
        self.session = session
        self.ws = ws
        self.action = action
        self.data = data
        # TODO: refactor
        room = ws.path_params.get("game_id", "lobby")
        self.room = int(room) if room != "lobby" else "lobby"
        self.user_id = int(self.ws.cookies.get("user_id", ""))
        assert self.user_id is not None

    async def dispatch(self) -> None:
        handlers = {
            "ping": self.ping,
            # lobby-only
            "create-invite": self.create_invite,
            "accept-invite": self.accept_invite,
            "cancel-invite": self.cancel_invite,
            # game-only
            "make-move": self.make_move, # sends GameData
            "connect-to-game": self.connect_to_game, # sends GameData
            "resign": self.resign, # sends GameData
        }

        handler: Callable[[], Awaitable[None]] = (
            handlers.get(self.action) or self.handle_invalid_message
        )
        try:
            await handler()
        except ValidationError as error:
            await self.ws.send_json({"action": "error", "data": error.json()})

    async def ping(self):
        await asyncio.sleep(1)
        await self.ws.send_json(
            {
                "action": "ping",
            }
        )

    # TODO: extract this boilerplate with pydantic models

    async def create_invite(self):
        data_schema = schemas.CreateInviteDataReceive(**self.data)

        repo = GameRepository(self.session)
        game_orm = await repo.create_game(self.user_id, data_schema)
        data = validated_json(
            {
                "user_id": game_orm.white_id
                if game_orm.white_id is not None
                else game_orm.black_id,
                "game_id": game_orm.id,
                "white": game_orm.white_id == self.user_id,
            },
            schemas.CreateInviteDataSend,
        )
        response = {
            "action": "create-invite",
            "data": data,
        }
        await broadcast.publish(
            channel="lobby",
            message=response,
        )

    async def accept_invite(self):
        data_schema = schemas.AcceptInviteDataReceive(**self.data)

        repo = GameRepository(self.session)
        game_orm = await repo.accept_invite(self.user_id, data_schema)
        data = validated_json(
            {
                "white_id": game_orm.white_id,
                "black_id": game_orm.black_id,
                "game_id": game_orm.id,
            },
            schemas.AcceptInviteDataSend,
        )

        response = {
            "action": "accept-invite",
            "data": data,
        }

        await broadcast.publish(channel="lobby", message=response)

    async def cancel_invite(self):
        data_schema = schemas.CancelInviteDataReceive(**self.data)
        repo = GameRepository(self.session)
        game_orm = await repo.cancel_invite(self.user_id, data_schema)
        data = validated_json(
            {
                "game_id": game_orm.id,
            },
            schemas.CancelInviteDataSend,
        )

        response = {"action": "cancel-invite", "data": data}

        await broadcast.publish(channel="lobby", message=response)

    async def make_move(self):
        data_schema = schemas.MakeNewMoveDataReceive(**self.data)

        game_id = self.room
        assert game_id != "lobby"
        repo = GameRepository(self.session)
        game_orm = await repo.make_move(self.user_id, game_id, data_schema)
        data = validated_json(
            {
                "game": game_orm,
            },
            schemas.GameDataSend,
        )

        response = {"action": "game", "data": data}

        await broadcast.publish(channel=str(game_id), message=response)

    async def resign(self):
        game_id = self.room
        assert game_id != "lobby"
        repo = GameRepository(self.session)
        game_orm = await repo.resign(self.user_id, game_id)
        data = validated_json(
            {
                "game": game_orm,
            },
            schemas.GameDataSend,
        )

        response = {"action": "game", "data": data}
        await broadcast.publish(
            channel=str(game_id),
            message=response,
        )

    async def connect_to_game(self):
        # (re)connect to a game to start or to rejoin
        # TODO: ensure both players are connected
        game_id = self.room
        assert game_id != "lobby"
        repo = GameRepository(self.session)
        game_orm = await repo.connect_to_game(self.user_id, game_id)
        data = validated_json(
            {
                "game": game_orm,
            },
            schemas.GameDataSend,
        )

        response = {
            "action": "game",
            "data": data,
        }
        await broadcast.publish(
            channel=str(game_id),
            message=response,
        )

    async def handle_invalid_message(self):
        await self.ws.send_json(
            {"action": "error", "data": {"detail": "unknown action " + self.action}}
        )
