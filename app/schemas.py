from __future__ import annotations

from pydantic import BaseModel

from app.constants import GameStatus


def to_snake_case(name: str) -> str:
    return "".join(
        ["_" + char.lower() if char.isupper() else char for char in name]
    ).lstrip("_")


class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True,  # orm_mode
        "alias_generator": to_snake_case,
    }


class Game(BaseSchema):
    id: int
    white_id: int | None
    black_id: int | None
    status: GameStatus
    position: Position
    whitewin: bool | None
    # clocks: ...


class Position(BaseSchema):
    # id: int
    # game_id: int
    fen: str
    moves: list[Move]


class Move(BaseSchema):
    # id: int
    # position_id: int
    ply: int
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
