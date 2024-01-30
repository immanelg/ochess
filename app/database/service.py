from __future__ import annotations

import random

from app import chess_service, schemas
from app.constants import Color, Result, Stage
from app.database import models
from app.database.database import get_session
from app.exception import ClientError


class BaseService:
    def __init__(self) -> None:
        pass


class UserService(BaseService):
    async def create_or_get_user(self, id: int):
        async with get_session() as session:
            if (user := await session.get(models.User, id)) is not None:
                return user
            user = models.User(id=id)
            session.add(user)
            await session.commit()
            return user


class GameService(BaseService):
    async def create_game(
        self,
        user_id: int,
        data: schemas.CreateGame,
    ) -> models.Game:
        async with get_session() as session:
            if data.white is None:
                data.white = random.choice([False, True])
            game = models.Game(
                white_id=user_id if data.white is True else None,
                black_id=user_id if data.white is False else None,
            )
            session.add(game)
            await session.commit()
            return game

    async def accept_game(
        self,
        user_id: int,
        data: schemas.AcceptGame,
    ) -> models.Game:
        async with get_session() as session:
            game_id = data.game_id
            game = await session.get(models.Game, game_id)

            if game is None:
                raise ClientError("game doesn't exist")
            if game.stage != Stage.waiting:
                raise ClientError("game is already playing")
            if user_id in {game.white_id, game.black_id}:
                raise ClientError("cannot accept your own invite")
            if game.black_id is not None and game.white_id is not None:
                raise ClientError("accepted invite, but game is already playing")

            if game.black_id is None:
                game.black_id = user_id
            elif game.white_id is None:
                game.white_id = user_id
            await session.commit()
            return game

    async def cancel_game(
        self,
        user_id: int,
        data: schemas.CancelGame,
    ) -> models.Game:
        async with get_session() as session:
            game = await session.get(models.Game, data.game_id)
            if game is None:
                raise ClientError("game doesn't exist")
            if game.stage != Stage.waiting:
                raise ClientError("cannot cancel non-waiting game")
            if user_id not in {game.white_id, game.black_id}:
                raise ClientError("can only cancel your own game")

            await session.delete(game)
            await session.commit()
            return game

    async def make_move(
        self,
        user_id: int,
        game_id: int,
        data: schemas.MakeMove,
    ) -> models.Game:
        async with get_session() as session:
            game = await session.get(models.Game, game_id)
            if game is None:
                raise ClientError("game doesn't exist")
            if user_id not in {game.white_id, game.black_id}:
                raise ClientError("can only make move in your game")

            if game.stage not in {Stage.waiting, Stage.playing}:
                raise ClientError("make move should be called waiting or playing game")

            game.stage = Stage.playing

            game = chess_service.try_move(game, data, white=(user_id == game.white_id))
            await session.commit()
            return game

    async def fetch_game(
        self,
        game_id: int,
    ) -> models.Game | None:
        async with get_session() as session:
            game = await session.get(models.Game, game_id)
            return game

    async def resign(
        self,
        user_id: int,
        game_id: int,
    ) -> models.Game:
        async with get_session() as session:
            game = await session.get(models.Game, game_id)
            if game is None:
                raise ClientError("game doesn't exist")
            if game.stage != Stage.playing:
                raise ClientError("cannot resign in non-playing game")
            if user_id not in {game.white_id, game.black_id}:
                raise ClientError("can only resign in your game")

            game.stage = Stage.ended
            game.winner = Color.white if user_id == game.black_id else Color.black
            game.result = Result.resign
            await session.commit()
            return game
