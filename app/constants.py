from enum import Enum


class GameStatus(str, Enum):
    waiting = "waiting"
    playing = "playing"
    draw = "draw"
    stalemate = "stalemate"
    checkmate = "checkmate"
    resign = "resign"
    abandon = "abandon"
