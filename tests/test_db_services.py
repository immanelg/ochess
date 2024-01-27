import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.constants import Color, Result, Stage
from app.database import models, service


@pytest.mark.asyncio
async def test_database_service(session: AsyncSession) -> None:
    # TODO: separate to unit tests instead of doing it all in one big run?
    user_repo = service.UserService(session)
    game_repo = service.GameService(session)
    user_1 = await user_repo.create_or_get_user(1)
    user_2 = await user_repo.create_or_get_user(2)

    game = await game_repo.create_game(
        user_1.id, schemas.CreateGameRequest(type="create_game", white=True)
    )
    assert game.white_id == user_1.id
    assert game.stage == Stage.waiting
    game = await game_repo.accept_game(
        user_2.id, schemas.AcceptGameRequest(type="accept_game", game_id=game.id)
    )

    await session.refresh(game)
    game = await game_repo.make_move(
        user_1.id, game.id, schemas.MakeMoveRequest(type="make_move", move="e2e4")
    )
    game = await game_repo.make_move(
        user_2.id, game.id, schemas.MakeMoveRequest(type="make_move", move="c7c5")
    )
    game = await session.get(models.Game, game.id)
    assert game is not None
    assert game.stage == Stage.playing
    assert game.result == None
    assert game.winner == None

    moves = game.moves
    assert [m.move for m in moves] == ["e2e4", "c7c5"]
    assert [m.ply for m in moves] == [1, 2]
    assert game.fen == "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"

    game = await game_repo.resign(user_2.id, game.id)
    assert game.stage == Stage.ended
    assert game.result == Result.resign
    assert game.winner == Color.white
