from typing import Any, Awaitable, Callable, TypeAlias
import sys

from starlette.websockets import WebSocket

from app import schemas
from app.database.database import get_session
from app.database.service import GameService, UserService
from app.exception import ClientError
from app.logging import logger
from app.resources import broadcast

Data: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[Data], Awaitable[None]]

# TODO: send && receive camelCase in pydantic models

class Client:
    user_id: int | None = None
    socket: WebSocket
    handlers: dict[str, Handler]

    def __init__(
        self,
        socket: WebSocket,
    ) -> None:
        self.socket = socket
        self.handlers = {
            "auth": self._auth,
        }

    async def receive_loop(self) -> None:
        try:
            async for message in self.socket.iter_json():
                logger.info("message user_id=%s %s", self.user_id, message)
                await self._on_message(message)
        except Exception:
            await self.socket.send_json(
                schemas.ErrorResponse(
                    type="error", detail="internal server error"
                ).model_dump()
            )
            logger.error("exception while processing a message from user %s", self.user_id, exc_info=sys.exc_info())


    async def _on_message(self, data: Data) -> None:
        message_type = data.get("type", None)
        handle: Handler | None = self.handlers.get(message_type)
        if handle is None:
            await self.socket.send_json(
                schemas.ErrorResponse(
                    type="error", detail=f"unknown message type, should have correct `type` field in message: {data}"
                ).model_dump()
            )
            return

        try:
            logger.debug("calling handler %s", handle.__name__)
            await handle(data)
        except ClientError as error:
            await self.socket.send_json(
                schemas.ErrorResponse(
                    type="error", detail=f"client error: {error.detail}",
                ).model_dump()
            )

    async def _auth(self, data: Data) -> None:
        # dummy implementation.
        data_schema = schemas.AuthRequest(**data)
        service = UserService(get_session())
        await service.create_or_get_user(id=data_schema.user_id)
        self.user_id = data_schema.user_id
        resp = schemas.AuthOk(type="auth_ok")
        logger.debug("auth send %s", resp.model_dump())
        await self.socket.send_json(resp.model_dump())


class LobbyClient(Client):
    user_id: int | None
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
        service = GameService(get_session())
        data_schema = schemas.CreateGameRequest(**data)
        assert self.user_id
        game_orm = await service.create_game(self.user_id, data_schema)
        resp = schemas.CreateGameResponse(
            type="create_game",
            white_id=game_orm.white_id,
            black_id=game_orm.black_id,
            game_id=game_orm.id,
        )
        await broadcast.publish(channel="lobby", message=resp.model_dump())

    async def _accept_game(self, data: Data) -> None:
        data_schema = schemas.AcceptGameRequest(**data)
        assert self.user_id
        service = GameService(get_session())
        game_orm = await service.accept_game(self.user_id, data_schema)
        resp = schemas.AcceptGameResponse(
            type="accept_game",
            white_id=game_orm.white_id,
            black_id=game_orm.black_id,
            game_id=game_orm.id,
        )

        await broadcast.publish(channel="lobby", message=resp.model_dump())

    async def _cancel_game(self, data: Data) -> None:
        data_schema = schemas.CancelGameRequest(**data)
        assert self.user_id
        service = GameService(get_session())
        game_orm = await service.cancel_game(self.user_id, data_schema)
        resp = schemas.CancelGameResponse(type="cancel_game", game_id=game_orm.id)
        await broadcast.publish(channel="lobby", message=resp.model_dump())

    async def _get_waiting_games(self, data: Data) -> None:
        # TODO
        ...


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
            "reconnect_game": self._reconnect,
            "fetch_game": self._fetch_game,
            "resign": self._resign,
            # "claim_draw": self.claim_draw,
            # "get_moves": self.get_moves, # do we calculate legal moves on client or server?
        }

    async def _make_move(self, data: Data) -> None:
        data_schema = schemas.MakeMoveRequest(**data)
        assert self.user_id
        assert self.game_id
        service = GameService(get_session())
        game_orm = await service.make_move(self.user_id, self.game_id, data_schema)
        resp = schemas.GameResponse(type="game", game=game_orm)  # type: ignore
        await broadcast.publish(channel=str(self.game_id), message=resp.model_dump())

    async def _resign(self, data: Data) -> None:
        _ = schemas.ResignRequest(**data)
        assert self.user_id
        service = GameService(get_session())
        game_orm = await service.resign(self.user_id, self.game_id)
        resp = schemas.GameResponse(
            type="game",
            game=game_orm,  # type: ignore
        )
        await broadcast.publish(
            channel=str(self.game_id),
            message=resp.model_dump(),
        )

    async def _fetch_game(self, data: Data) -> None:
        assert self.user_id
        _ = schemas.FetchGameRequest(**data)
        service = GameService(get_session())
        game_orm = await service.fetch_game(self.game_id)
        resp = schemas.GameResponse(
            type="game",
            game=game_orm,  # type: ignore
        )
        await self.socket.send_json(resp.model_dump())

    async def _reconnect(self, message: Data):
        # TODO: broadcast connect/disconnect so everyone can see if a player is present or not
        ...
