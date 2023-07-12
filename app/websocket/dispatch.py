from typing import Any, Awaitable, Callable, TypeAlias

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from app import schemas
from app.database.service import GameRepository
from app.resources import broadcast
from app.validation import validated_json

Handler: TypeAlias = Callable[[], Awaitable[None]]

# TODO: reduce boilerblate for validation

class BaseDispatcher:
    """Dispatches event sent by WS client."""

    ws: WebSocket
    action: str
    data: dict[str, Any]
    user_id: int
    session: AsyncSession
    handlers: dict[str, Handler]

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
        # TODO: better auth
        self.user_id = int(self.ws.cookies.get("user_id", ""))
        assert self.user_id is not None


    async def dispatch(self) -> None:
        handler: Callable[[], Awaitable[None]] = self.handlers.get(self.action) or self.handle_invalid_message
        try:
            await handler()
        except ValidationError as error:
            await self.send_error(error)

    async def send_error(self, error) -> None:
        await self.ws.send_json({"action": "error", "data": error.errors(include_url=False)})


    async def handle_invalid_message(self):
        await self.ws.send_json(
            {"action": "error", "data": {"detail": "unknown action " + self.action}}
        )


class LobbyDispatcher(BaseDispatcher):
    def __init__(self, session: AsyncSession, ws: WebSocket, action: str, data: dict[str, Any]) -> None:
        super().__init__(session, ws, action, data)

        self.handlers = {
            "create-invite": self.create_invite,
            "accept-invite": self.accept_invite,
            "cancel-invite": self.cancel_invite,
            # TODO: "get-invites" action
        }
        self.game_repo = GameRepository(self.session)

    async def create_invite(self):
        data_schema = schemas.CreateInviteDataReceive(**self.data)

        game_orm = await self.game_repo.create_game(self.user_id, data_schema)
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

        game_orm = await self.game_repo.accept_invite(self.user_id, data_schema)
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
        game_orm = await self.game_repo.cancel_invite(self.user_id, data_schema)
        data = validated_json(
            {
                "game_id": game_orm.id,
            },
            schemas.CancelInviteDataSend,
        )

        response = {"action": "cancel-invite", "data": data}

        await broadcast.publish(channel="lobby", message=response)

class GameDispatcher(BaseDispatcher):

    def __init__(self, session: AsyncSession, ws: WebSocket, action: str, data: dict[str, Any], game_id: int) -> None:
        super().__init__(session, ws, action, data)
        self.game_id = game_id
        self.game_repo = GameRepository(self.session)

        self.handlers = {
            "make-move": self.make_move, 
            "connect-to-game": self.connect_to_game,
            "resign": self.resign, 
        }

    async def make_move(self):
        data_schema = schemas.MakeNewMoveDataReceive(**self.data)

        game_orm = await self.game_repo.make_move(self.user_id, self.game_id, data_schema)
        data = validated_json(
            {
                "game": game_orm,
            },
            schemas.GameDataSend,
        )

        response = {"action": "game", "data": data}

        await broadcast.publish(channel=str(self.game_id), message=response)

    async def resign(self):
        game_orm = await self.game_repo.resign(self.user_id, self.game_id)
        data = validated_json(
            {
                "game": game_orm,
            },
            schemas.GameDataSend,
        )

        response = {"action": "game", "data": data}
        await broadcast.publish(
            channel=str(self.game_id),
            message=response,
        )

    async def connect_to_game(self):
        # TODO: decouple connection to game and requesting for game state
        # send "connect" msg from client and then broadcast data about which players are connected
        # request game state on client with "get-game" action after connection and send it to this client
        game_orm = await self.game_repo.connect_to_game(self.user_id, self.game_id)
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
            channel=str(self.game_id),
            message=response,
        )
