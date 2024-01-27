from typing import Any, Awaitable, Callable, TypeAlias

from starlette.websockets import WebSocket

from app import schemas
from app.database.database import get_session
from app.database.service import GameService, UserService
from app.logging import logger
from app.resources import broadcast

Data: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[Data], Awaitable[None]]


# TODO: validation errors are not catched now at all. Catch them and send errors back. Also, catch exception raised by DB services.


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
            "auth": self.auth,
        }

    async def on_message(self, data: Data) -> None:
        message_type = data.get("type", None)
        handle: Handler | None = self.handlers.get(message_type)
        if handle is None:
            await self.socket.send(
                schemas.ErrorResponse(
                    type="error", detail=f"unknown message type {message_type}"
                ).model_dump()
            )
            return

        try:
            logger.debug("calling handler %s", handle.__name__)
            await handle(data)
        except Exception as exc:
            await self.socket.send_json(
                schemas.ErrorResponse(
                    type="error", detail="internal error"
                ).model_dump()
            )
            raise exc

    async def auth(self, data: Data) -> None:
        # dummy implementation.
        data_schema = schemas.AuthRequest(**data)
        service = UserService(get_session())
        await service.create_user(id=data_schema.user_id)
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
            "create_game": self.create_game,
            "accept_game": self.accept_game,
            "cancel_game": self.cancel_game,
            "get_waiting_games": self.get_waiting_games,
        }

    async def create_game(self, data: Data) -> None:
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

    async def accept_game(self, data: Data) -> None:
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

    async def cancel_game(self, data: Data) -> None:
        data_schema = schemas.CancelGameRequest(**data)
        assert self.user_id
        service = GameService(get_session())
        game_orm = await service.cancel_game(self.user_id, data_schema)
        resp = schemas.CancelGameResponse(type="cancel_game", game_id=game_orm.id)
        await broadcast.publish(channel="lobby", message=resp.model_dump())

    async def get_waiting_games(self, data: Data) -> None:
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
            "make_move": self.make_move,
            "reconnect_game": self.reconnect,
            "fetch_game": self.fetch_game,
            "resign": self.resign,
            # "claim_draw": self.claim_draw,
            # "get_moves": self.get_moves, # do we calculate legal moves on client or server?
        }

    async def make_move(self, data: Data) -> None:
        data_schema = schemas.MakeMoveRequest(**data)
        assert self.user_id
        assert self.game_id
        service = GameService(get_session())
        game_orm = await service.make_move(self.user_id, self.game_id, data_schema)
        resp = schemas.GameResponse(type="game", game=game_orm)  # type: ignore
        await broadcast.publish(channel=str(self.game_id), message=resp.model_dump())

    async def resign(self, data: Data) -> None:
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

    async def fetch_game(self, data: Data) -> None:
        assert self.user_id
        _ = schemas.FetchGameRequest(**data)
        service = GameService(get_session())
        game_orm = await service.fetch_game(self.game_id)
        resp = schemas.GameResponse(
            type="game",
            game=game_orm,  # type: ignore
        )
        await self.socket.send_json(resp.model_dump())

    async def reconnect(self, message: Data):
        # TODO: broadcast connect/disconnect so everyone can see if a player is present or not
        ...
