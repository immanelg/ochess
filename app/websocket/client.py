import sys
from typing import Any, Awaitable, Callable, TypeAlias

from starlette.websockets import WebSocket

from app import schemas
from app.database.service import GameService, UserService
from app.exception import ClientError
from app.logging import logger
from app.resources import broadcast

Data: TypeAlias = dict[str, Any]
Handler: TypeAlias = Callable[[Data], Awaitable[None]]


class Client:
    """
    A wrapper for websocket connection that handles authentication, loops and dispatches messages from socket.
    """

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
            await self.socket.send_text(
                schemas.ErrorResponse(
                    type="error", detail="internal server error"
                ).json()
            )
            logger.error(
                "exception while processing a message from user %s",
                self.user_id,
                exc_info=sys.exc_info(),
            )

    async def _on_message(self, data: Data) -> None:
        message_type = data.get("type", None)
        handle: Handler | None = self.handlers.get(message_type)
        if handle is None:
            logger.info("no handler for message %s", data)
            await self.socket.send_text(
                schemas.ErrorResponse(
                    type="error",
                    detail=f"client error: unknown message type, got incorrect `type` field in message: {data}",
                ).json()
            )
            return

        try:
            logger.debug("calling handler %s", handle.__name__)
            await handle(data)
        except ClientError as error:
            logger.info("client error %s", error.detail)
            await self.socket.send_text(
                schemas.ErrorResponse(
                    type="error",
                    detail=f"client error: {error.detail}",
                ).json()
            )

    async def _auth(self, data: Data) -> None:
        # dummy implementation.
        data_schema = schemas.AuthRequest(**data)
        service = UserService()
        await service.create_or_get_user(id=data_schema.user_id)
        self.user_id = data_schema.user_id
        resp = schemas.AuthOk(type="auth_ok")
        await self.socket.send_text(resp.json())


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
