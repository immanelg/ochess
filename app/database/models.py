from __future__ import annotations

from chess import STARTING_FEN
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from app.constants import Color, Result, Stage


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.as_dict()}"

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class _Id:
    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base, _Id):
    rating: Mapped[int] = mapped_column(default=1500)
    # games: Mapped[list[Game]] = relationship()
    # created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    pass


class Game(Base, _Id):
    white_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    black_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))

    fen: Mapped[str] = mapped_column(default=STARTING_FEN)
    stage: Mapped[Stage] = mapped_column(default=Stage.waiting)

    # result and winner should be NULL if stage is 'playing' or 'waiting'
    result: Mapped[Result | None] = mapped_column(default=None)
    winner: Mapped[Color | None] = mapped_column(default=None)

    # created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    moves: Mapped[list[Move]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    # clock


class Move(Base, _Id):
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))

    ply: Mapped[int] = mapped_column()
    src: Mapped[str] = mapped_column(String(2))
    dest: Mapped[str] = mapped_column(String(2))
    promo: Mapped[str | None] = mapped_column(String(1))

    # created_at: Mapped[datetime] = mapped_column(server_default=func.now())
