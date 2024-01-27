from __future__ import annotations

import random

import chess
from sqlalchemy.ext.asyncio import AsyncSession

from app import chess_service, schemas
from app.constants import Color, Result, Stage
from app.database import models
from app.exception import ClientError


class BaseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class UserService(BaseService):
    async def create_or_get_user(self, id: int):
        if (user := await self.session.get(models.User, id)) is not None:
            return user
        user = models.User(id=id)
        self.session.add(user)
        await self.session.commit()
        return user


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

        if game is None:
            raise ClientError("game doesn't exist")
        if game.stage != Stage.waiting:
            raise ClientError("game is already playing")
        if user_id  in {game.white_id, game.black_id}:
            raise ClientError("cannot accept your own invite")
        if game.black_id is not None and game.white_id is not None:
            raise ClientError("accepted invite, but game is already playing")

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
        if game is None:
            raise ClientError("game doesn't exist")
        if game.stage != Stage.waiting:
            raise ClientError("cannot cancel non-waiting game")
        if user_id not in { game.white_id, game.black_id}:
            raise ClientError("can only cancel your own game")

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
        if game is None:
            raise ClientError("game doesn't exist")
        if user_id not in {game.white_id, game.black_id}:
            raise ClientError("can only make move in your game")

        if game.stage not in { Stage.waiting, Stage.playing }:
            raise ClientError("make move should be called waiting or playing game")

        game.stage = Stage.playing

        game = chess_service.try_move(
            game, data.move, white=(user_id == game.white_id)
        )
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
        if game is None:
            raise ClientError("game doesn't exist")
        if game.stage != Stage.playing:
            raise ClientError("cannot resign in non-playing game")
        if user_id not in {game.white_id, game.black_id}:
            raise ClientError("can only resign in your game")

        game.stage = Stage.ended
        game.winner = Color.white if user_id == game.black_id else Color.black
        game.result = Result.resign
        await self.session.commit()
        return game
