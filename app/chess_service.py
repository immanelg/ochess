import chess

from app.constants import Color, Result, Stage
from app.database import models
from app.exception import ClientError


def try_move(game: models.Game, move: str, white: bool) -> models.Game:
    """
    Plays move (mutating model) or raises ClientError
    """
    length = len(game.moves)
    if not white != length % 2:
        raise ClientError(
            f"illegal move {move}: wrong turn, attempts {'white' if white else 'black'} move, "
            f"but there are {length} moves played"
        )

    board = chess.Board(fen=game.fen)
    try:
        board.push_uci(move)
    except chess.IllegalMoveError as e:
        raise ClientError(f"illegal move {move}") from e
    except chess.InvalidMoveError as e:
        raise ClientError(f"invalid move {move}") from e
    except chess.AmbiguousMoveError as e:
        raise ClientError(f"ambigious move {move}") from e

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
