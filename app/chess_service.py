from typing import Any

import chess

from app.constants import GameStatus
from app.database import models

STARTING_FEN = chess.STARTING_FEN


def is_white_turn(moves: list[Any]) -> bool:
    return len(moves) % 2 == 0


def try_move(game: models.Game, move: str, white: bool) -> models.Game:
    """Validates move and returns mutated ORM model or raises an exception."""
    current_ply = len(game.position.moves)
    if white and current_ply % 2 != 0:
        raise chess.IllegalMoveError()

    chess_obj = chess.Board(game.position.fen)
    chess_obj.push_uci(move)

    if chess_obj.is_checkmate():
        game.status = GameStatus.checkmate

    if chess_obj.is_stalemate():
        game.status = GameStatus.stalemate

    game.position.fen = chess_obj.fen()
    game.position.moves.append(models.Move(move=move, ply=current_ply))

    return game
