from __future__ import annotations

# TODO: refactor this module into DB Service class
import chess
from sqlalchemy.ext.asyncio import AsyncSession

from app import chess_service, schemas
from app.constants import GameStatus
from app.database import models


class AbstractRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class UserRepository(AbstractRepository):
    # TODO: this is dummy implementation that is only used in dummy middleware
    async def create(self):
        user = models.User()
        self.session.add(user)
        await self.session.commit()
        return user


class GameRepository(AbstractRepository):
    async def create_game(
        self,
        user_id: int,
        data: schemas.CreateInviteDataReceive,
    ) -> models.Game:
        game = models.Game(
            white_id=user_id if data.white else None,
            black_id=user_id if not data.white else None,
            status=GameStatus.waiting,
            position=models.Position(
                moves=[],
            ),
        )
        self.session.add(game)
        await self.session.commit()
        return game

    async def accept_invite(
        self,
        user_id: int,
        data: schemas.AcceptInviteDataReceive,
    ) -> models.Game:
        game_id = data.game_id
        game = await self.session.get(models.Game, game_id)
        # TODO: handle these checks and send errors back
        assert game is not None, "game doesnt exist"
        assert game.status == GameStatus.waiting, "game is already playing"
        assert user_id not in {
            game.white_id,
            game.black_id,
        }, "cannot accept your own invite"
        if game.black_id is None:
            game.black_id = user_id
        elif game.white_id is None:
            game.white_id = user_id
        # else request was too late?
        await self.session.commit()
        return game

    async def cancel_invite(
        self,
        user_id: int,
        data: schemas.CancelInviteDataReceive,
    ) -> models.Game:
        game = await self.session.get(models.Game, data.game_id)
        assert game is not None, "game doesnt exist"
        assert game.status == GameStatus.waiting, "game is already playing"
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
        data: schemas.MakeNewMoveDataReceive,
    ) -> models.Game:
        game = await self.session.get(models.Game, game_id)
        # TODO: handle these checks and send errors back
        assert game is not None, "game doesnt exist"
        assert user_id in {game.white_id, game.black_id}, "can only play in your game"
        assert game.status == GameStatus.playing, "game is not playing"

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

    async def connect_to_game(
        self,
        user_id: int,
        game_id: int,
    ) -> models.Game:
        game = await self.session.get(models.Game, game_id)
        # TODO: handle these checks and send errors back
        assert game is not None, "game doesnt exist"
        if user_id in {game.white_id, game.black_id}:  # joined with `accept-invite`
            game.status = GameStatus.playing
        else:
            assert False, "joined game, but you are not player? spectator?"
        await self.session.commit()
        return game

    async def resign(
        self,
        user_id: int,
        game_id: int,
    ) -> models.Game:
        game = await self.session.get(models.Game, game_id)
        assert game is not None, "game doesnt exist"
        assert game.status == GameStatus.playing, "game is not playing"
        assert user_id in {
            game.white_id,
            game.black_id,
        }, "can only resign in your own game"
        game.status = GameStatus.resign
        game.whitewin = user_id == game.white_id
        await self.session.commit()
        return game
