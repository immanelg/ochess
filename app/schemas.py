from __future__ import annotations
from typing import Annotated, Literal
from chess import Color

from pydantic import BaseModel, ConfigDict, Field

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


class Error(BaseSchema):
    type: Literal["error"]
    detail: str


# lobby

# class LobbyRequest(BaseSchema):
#     request: Annotated[CreateGameRequest | AcceptGameRequest | CancelGameRequest, Field(discriminator="type")]


class CreateGameRequest(BaseSchema):
    type: Literal["create_game"]
    white: bool


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


# game channels

class MakeMoveRequest(BaseSchema):
    type: Literal["make_move"]
    move: str


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
