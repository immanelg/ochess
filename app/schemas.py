from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.constants import Color, Result, Stage


class _BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def json(self) -> str:
        """
        Serialize to a JSON string with camelCase fields.
        """
        return self.model_dump_json(by_alias=True)


class Game(_BaseSchema):
    id: int
    white_id: int | None = None
    black_id: int | None = None

    stage: Stage | None = None
    result: Result | None = None
    winner: Color | None = None

    fen: str
    moves: list[Move] = []
    # clocks: ...


class User(_BaseSchema):
    id: int
    # rating


class Move(_BaseSchema):
    move: str


class ErrorResponse(_BaseSchema):
    type: Literal["error"]
    detail: str


class AuthRequest(_BaseSchema):
    type: Literal["auth"]
    user_id: int


class AuthOk(_BaseSchema):
    type: Literal["auth_ok"]


# lobby

# class LobbyRequest(BaseSchema):
#     request: Annotated[CreateGameRequest | AcceptGameRequest | CancelGameRequest, Field(discriminator="type")]


class CreateGame(_BaseSchema):
    type: Literal["create_game"]
    white: bool | None = None


class CreateGameResp(_BaseSchema):
    type: Literal["create_game"]
    white_id: int | None
    black_id: int | None
    game_id: int


class AcceptGame(_BaseSchema):
    type: Literal["accept_game"]
    game_id: int


class AcceptGameResp(_BaseSchema):
    type: Literal["accept_game"]
    white_id: int | None
    black_id: int | None
    game_id: int


class CancelGame(_BaseSchema):
    type: Literal["cancel_game"]
    game_id: int


class CancelGameResp(_BaseSchema):
    type: Literal["cancel_game"]
    game_id: int


class WaitingGames(_BaseSchema):
    type: Literal["get_waiting_games"]


class WaitingGamesResp(_BaseSchema):
    type: Literal["get_waiting_games"]
    games: list[_WaitingGame] = []


class _WaitingGame(_BaseSchema):
    white_id: int | None = None
    black_id: int | None = None
    game_id: int


# game channels


class MakeMove(_BaseSchema):
    type: Literal["make_move"]
    move: str
    # time


class FetchGame(_BaseSchema):
    type: Literal["fetch_game"]


class GameResp(_BaseSchema):
    type: Literal["game"]
    game: Game


class Resign(_BaseSchema):
    type: Literal["resign"]


class Reconnect(_BaseSchema):
    type: Literal["reconnect"]


class ReconnectResp(_BaseSchema):
    type: Literal["reconnect"]
    user_id: int
