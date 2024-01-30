import sys
from typing import Any, Awaitable, Callable, TypeAlias

from starlette.websockets import WebSocket

from app import schemas
from app.database.service import UserService
from app.exception import ClientError
from app.logging import logger

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

        if self.user_id is None and message_type != "auth":
            await self.socket.send_text(
                schemas.ErrorResponse(
                    type="error",
                    detail="not authenticated",
                ).json()
            )

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
