import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import service

from app.constants import Stage
from app.database import service
from app.database import models
from app import schemas

@pytest.mark.asyncio
async def test_database_service(session: AsyncSession) -> None:
    # TODO: separate to unit tests instead of doing it all in one big run?
    user_repo = service.UserService(session)
    game_repo = service.GameService(session)
    user_1 = await user_repo.create()
    user_2 = await user_repo.create()

    game = await game_repo.create_game(user_1.id, schemas.CreateInviteDataReceive(white=True))
    assert game.white_id == user_1.id
    assert game.stage == Stage.waiting
    game = await game_repo.accept_game(user_2.id, schemas.AcceptInviteDataReceive(game_id=game.id))

    await game_repo.connect_to_game(user_1.id, game.id)
    await game_repo.connect_to_game(user_2.id, game.id)
    game = await session.get(models.Game, game.id)
    assert game is not None
    assert game.stage == Stage.playing

    game = await game_repo.make_move(user_1.id, game.id, schemas.MakeNewMoveDataReceive(move="e2e4"))
    game = await game_repo.make_move(user_2.id, game.id, schemas.MakeNewMoveDataReceive(move="c7c5"))

    moves = game.position.moves
    assert [m.move for m in moves] == ["e2e4", "c7c5"]
    assert moves[0].ply == 0
    assert moves[1].ply == 1
    assert game.position.fen == "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"

    game = await game_repo.resign(user_1.id, game.id)
    assert game.stage == Stage.resign
    assert game.whitewin == True


