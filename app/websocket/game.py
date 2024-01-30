from typing import Any, Awaitable, Callable, TypeAlias

from starlette.websockets import WebSocket

from app import schemas
from app.database.service import GameService
from app.resources import broadcast
from app.websocket.client import Client

Data: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[Data], Awaitable[None]]


class GameClient(Client):
    socket: WebSocket
    handlers: dict[str, Handler]
    user_id: int | None = None
    game_id: int

    def __init__(
        self,
        socket: WebSocket,
        game_id: int,
    ) -> None:
        super().__init__(socket)
        self.game_id = game_id

        self.handlers |= {
            "make_move": self._make_move,
            "reconnect": self._reconnect,
            "fetch_game": self._fetch_game,
            "resign": self._resign,
            # "claim_draw": self.claim_draw,
            # "get_dests": self.get_dests, # maybe we want to send legal moves
        }

    async def _make_move(self, data: Data) -> None:
        data_schema = schemas.MakeMove(**data)
        assert self.user_id
        assert self.game_id
        service = GameService()
        game_orm = await service.make_move(self.user_id, self.game_id, data_schema)
        resp = schemas.GameResp(type="game", game=game_orm)  # type: ignore
        await broadcast.publish(channel=str(self.game_id), message=resp.json())

    async def _resign(self, data: Data) -> None:
        _ = schemas.Resign(**data)
        assert self.user_id
        service = GameService()
        game_orm = await service.resign(self.user_id, self.game_id)
        resp = schemas.GameResp(
            type="game",
            game=game_orm,  # type: ignore
        )
        await broadcast.publish(
            channel=str(self.game_id),
            message=resp.json(),
        )

    async def _fetch_game(self, data: Data) -> None:
        assert self.user_id
        _ = schemas.FetchGame(**data)
        service = GameService()
        game_orm = await service.fetch_game(self.game_id)
        resp = schemas.GameResp(
            type="game",
            game=game_orm,  # type: ignore
        )
        await self.socket.send_text(resp.json())

    async def _reconnect(self, data: Data) -> None:
        _ = schemas.Reconnect(**data)
        assert self.user_id
        resp = schemas.ReconnectResp(type="reconnect", user_id=self.user_id)
        await broadcast.publish(
            channel=str(self.game_id),
            message=resp.json(),
        )
