from __future__ import annotations

from typing import Literal

from chess import Color
from pydantic import BaseModel, ConfigDict

from app.constants import Result, Stage


def to_snake_case(name: str) -> str:
    return "".join(["_" + ch.lower() if ch.isupper() else ch for ch in name]).lstrip(
        "_"
    )


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # orm_mode
        alias_generator=to_snake_case,
    )


class Game(BaseSchema):
    id: int
    white_id: int | None
    black_id: int | None

    stage: Stage
    result: Result
    winner: Color

    fen: str
    moves: list[Move]
    # clocks: ...


class User(BaseSchema):
    id: int
    # rating


class Move(BaseSchema):
    move: str


class ErrorResponse(BaseSchema):
    type: Literal["error"]
    detail: str


# dummy auth
class AuthRequest(BaseSchema):
    type: Literal["auth"]
    user_id: int


class AuthOk(BaseSchema):
    type: Literal["auth_ok"]


# lobby

# class LobbyRequest(BaseSchema):
#     request: Annotated[CreateGameRequest | AcceptGameRequest | CancelGameRequest, Field(discriminator="type")]


class CreateGameRequest(BaseSchema):
    type: Literal["create_game"]
    white: bool | None = None


class CreateGameResponse(BaseSchema):
    type: Literal["create_game"]
    white_id: int | None
    black_id: int | None
    game_id: int


class AcceptGameRequest(BaseSchema):
    type: Literal["accept_game"]
    game_id: int


class AcceptGameResponse(BaseSchema):
    type: Literal["accept_game"]
    white_id: int | None
    black_id: int | None
    game_id: int


class CancelGameRequest(BaseSchema):
    type: Literal["cancel_game"]
    game_id: int


class CancelGameResponse(BaseSchema):
    type: Literal["cancel_game"]
    game_id: int


class GetWaitingGamesRequest(BaseSchema):
    type: Literal["get_waiting_games"]


class GetWaitingGamesResponse(BaseSchema):
    type: Literal["get_waiting_games"]
    games: list[_WaitingGame]


class _WaitingGame(BaseSchema):
    white_id: int | None
    black_id: int | None
    game_id: int


# game channels


class MakeMoveRequest(BaseSchema):
    type: Literal["make_move"]
    move: str


class FetchGameRequest(BaseSchema):
    type: Literal["fetch_game"]


class GameResponse(BaseSchema):
    type: Literal["game"]
    game: Game


class ResignRequest(BaseSchema):
    type: Literal["resign"]


class ReconnectRequest(BaseSchema):
    type: Literal["reconnect"]


class ReconnectResponse(BaseSchema):
    type: Literal["reconnect"]
    user_id: int
