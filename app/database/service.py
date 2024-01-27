from __future__ import annotations

import random

import chess
from sqlalchemy.ext.asyncio import AsyncSession

from app import chess_service, schemas
from app.constants import Color, Result, Stage
from app.database import models


class BaseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class UserService(BaseService):
    # TODO: this is dummy implementation that is only used in dummy middleware
    async def create(self):
        user = models.User()
        self.session.add(user)
        await self.session.commit()
        return user


# TODO! return errors instead of assertions.


class GameService(BaseService):
    async def create_game(
        self,
        user_id: int,
        data: schemas.CreateGameRequest,
    ) -> models.Game:
        if data.white is None:
            data.white = random.choice([False, True])
        game = models.Game(
            white_id=user_id if data.white is True else None,
            black_id=user_id if data.white is False else None,
        )
        self.session.add(game)
        await self.session.commit()
        return game

    async def accept_game(
        self,
        user_id: int,
        data: schemas.AcceptGameRequest,
    ) -> models.Game:
        game_id = data.game_id
        game = await self.session.get(models.Game, game_id)
        assert game is not None, "game doesn't exist"
        assert game.stage == Stage.waiting, "game is already playing"
        assert user_id not in {
            game.white_id,
            game.black_id,
        }, "cannot accept your own invite"
        assert (
            game.black_id is not None or game.white_id is not None
        ), "invalid game state: both players are null"
        assert (
            game.black_id is None or game.white_id is None
        ), "accepted invite, but game already playing"
        if game.black_id is None:
            game.black_id = user_id
        elif game.white_id is None:
            game.white_id = user_id
        await self.session.commit()
        return game

    async def cancel_game(
        self,
        user_id: int,
        data: schemas.CancelGameRequest,
    ) -> models.Game:
        game = await self.session.get(models.Game, data.game_id)
        assert game is not None, "game doesnt exist"
        assert game.stage == Stage.waiting, "game is already playing"
        assert user_id in {
            game.white_id,
            game.black_id,
        }, "can only cancel your own game"
        await self.session.delete(game)
        await self.session.commit()
        return game

    async def make_move(
        self,
        user_id: int,
        game_id: int,
        data: schemas.MakeMoveRequest,
    ) -> models.Game:
        game = await self.session.get(models.Game, game_id)
        assert game is not None, "game doesn't exist"
        assert user_id in {game.white_id, game.black_id}, "can only play in your game"

        assert game.stage in {
            Stage.waiting,
            Stage.playing,
        }, "make move should be called waiting or playing game"
        game.stage = Stage.playing

        try:
            game = chess_service.try_move(
                game, data.move, white=(user_id == game.white_id)
            )
        except chess.IllegalMoveError as e:
            assert False, f"illegal move {e!s}"
        except chess.InvalidMoveError as e:
            assert False, f"invalid move {e!s}"

        await self.session.commit()
        return game

    async def fetch_game(
        self,
        game_id: int,
    ) -> models.Game | None:
        game = await self.session.get(models.Game, game_id)
        return game

    async def resign(
        self,
        user_id: int,
        game_id: int,
    ) -> models.Game:
        game = await self.session.get(models.Game, game_id)
        assert game is not None, "game doesn't exist"
        assert game.stage == Stage.playing, "game is not playing"
        assert user_id in {
            game.white_id,
            game.black_id,
        }, "can only resign in your own game"
        game.stage = Stage.ended
        game.winner = Color.white if user_id == game.black_id else Color.black
        game.result = Result.resign
        await self.session.commit()
        return game
