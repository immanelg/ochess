from typing import Any, Awaitable, Callable, TypeAlias

from starlette.websockets import WebSocket

from app import schemas
from app.database.service import GameService
from app.resources import broadcast
from app.websocket.client import Client

Data: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[Data], Awaitable[None]]


class LobbyClient(Client):
    user_id: int | None = None
    socket: WebSocket
    handlers: dict[str, Handler]

    def __init__(
        self,
        socket: WebSocket,
    ) -> None:
        super().__init__(socket)

        self.handlers |= {
            "create_game": self._create_game,
            "accept_game": self._accept_game,
            "cancel_game": self._cancel_game,
            "get_waiting_games": self._get_waiting_games,
        }

    async def _create_game(self, data: Data) -> None:
        # TODO: automatic pairing
        # when client connects, check if appropriate invite
        # alrady exists and immediatly accept it
        service = GameService()
        data_schema = schemas.CreateGame(**data)
        assert self.user_id
        game_orm = await service.create_game(self.user_id, data_schema)
        resp = schemas.CreateGameResp(
            type="create_game",
            white_id=game_orm.white_id,
            black_id=game_orm.black_id,
            game_id=game_orm.id,
        )
        await broadcast.publish(channel="lobby", message=resp.json())

    async def _accept_game(self, data: Data) -> None:
        data_schema = schemas.AcceptGame(**data)
        assert self.user_id
        service = GameService()
        game_orm = await service.accept_game(self.user_id, data_schema)
        resp = schemas.AcceptGameResp(
            type="accept_game",
            white_id=game_orm.white_id,
            black_id=game_orm.black_id,
            game_id=game_orm.id,
        )

        await broadcast.publish(channel="lobby", message=resp.json())

    async def _cancel_game(self, data: Data) -> None:
        data_schema = schemas.CancelGame(**data)
        assert self.user_id
        service = GameService()
        game_orm = await service.cancel_game(self.user_id, data_schema)
        resp = schemas.CancelGame(type="cancel_game", game_id=game_orm.id)
        await broadcast.publish(channel="lobby", message=resp.json())

    async def _get_waiting_games(self, data: Data) -> None:
        # TODO
        ...
