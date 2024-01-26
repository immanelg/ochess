import chess

from app.constants import Color, Result, Stage
from app.database import models

# TODO: refactor logic somehow somewhere


def try_move(game: models.Game, move: str, white: bool) -> models.Game:
    """Validates move and returns mutated ORM model or raises an exception."""
    current_ply = len(game.moves)
    if white and current_ply % 2 != 0:
        raise chess.IllegalMoveError()

    board = chess.Board(fen=game.fen)
    board.push_uci(move)

    if board.is_checkmate():
        game.stage = Stage.ended
        game.result = Result.checkmate
        game.winner = Color.white if white else Color.black
    elif board.is_stalemate():
        game.stage = Stage.ended
        game.result = Result.draw

    game.fen = board.fen()
    game.moves.append(models.Move(move=move))

    return game
