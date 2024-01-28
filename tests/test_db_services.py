import pytest

from app import schemas
from app.constants import Color, Result, Stage
from app.database import service


@pytest.mark.asyncio
async def test_database_service() -> None:
    # TODO: separate to unit tests instead of doing it all in one big run?
    user_repo = service.UserService()
    game_repo = service.GameService()
    user_1 = await user_repo.create_or_get_user(1)
    user_2 = await user_repo.create_or_get_user(2)

    game = await game_repo.create_game(
        user_1.id, schemas.CreateGame(type="create_game", white=True)
    )
    assert game.white_id == user_1.id
    assert game.stage == Stage.waiting
    game = await game_repo.accept_game(
        user_2.id, schemas.AcceptGame(type="accept_game", game_id=game.id)
    )

    game = await game_repo.make_move(
        user_1.id, game.id, schemas.MakeMove(type="make_move", move="e2e4")
    )
    game = await game_repo.make_move(
        user_2.id, game.id, schemas.MakeMove(type="make_move", move="c7c5")
    )
    game = await game_repo.fetch_game(game.id)
    assert game is not None
    assert game.stage == Stage.playing
    assert game.result == None
    assert game.winner == None

    moves = game.moves
    assert [m.move for m in moves] == ["e2e4", "c7c5"]
    assert game.fen == "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"

    game = await game_repo.resign(user_2.id, game.id)
    assert game.stage == Stage.ended
    assert game.result == Result.resign
    assert game.winner == Color.white
