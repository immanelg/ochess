from __future__ import annotations

from chess import STARTING_FEN
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from app.constants import GameStatus


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.to_dict()}"

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class HasId:
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base, HasId):
    pass


class Game(Base, HasId):
    white_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    black_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    status: Mapped[GameStatus] = mapped_column(default=GameStatus.waiting)
    whitewin: Mapped[
        bool | None
    ] = mapped_column()  # None if game doesn't have a winner

    # TODO: maybe simplify these relationships
    position: Mapped[Position] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )
    # clocks: ...


class Position(Base, HasId):
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    fen: Mapped[str] = mapped_column(default=STARTING_FEN)

    moves: Mapped[list[Move]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )


class Move(Base, HasId):
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"))
    ply: Mapped[int]
    move: Mapped[str]
