from __future__ import annotations
from chess import Color

from pydantic import BaseModel, ConfigDict

from app.constants import Result, Stage


def to_snake_case(name: str) -> str:
    return "".join(
        ["_" + ch.lower() if ch.isupper() else ch for ch in name]
    ).lstrip("_")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes = True,  # orm_mode
        alias_generator = to_snake_case,
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


class CreateInviteDataReceive(BaseSchema):
    white: bool


class CreateInviteDataSend(BaseSchema):
    user_id: int
    game_id: int
    white: bool


class AcceptInviteDataReceive(BaseSchema):
    game_id: int


class AcceptInviteDataSend(BaseSchema):
    white_id: int
    black_id: int
    game_id: int


class CancelInviteDataReceive(BaseSchema):
    game_id: int


class CancelInviteDataSend(BaseSchema):
    game_id: int


class MakeNewMoveDataReceive(BaseSchema):
    move: str


class GameDataSend(BaseSchema):
    game: Game
