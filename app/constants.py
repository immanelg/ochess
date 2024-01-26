from enum import Enum


class Stage(str, Enum):
    waiting = "waiting"
    playing = "playing"
    ended = "ended"

class Result(str, Enum):
    checkmate = "checkmate"
    draw = "draw"
    resign = "resign"
    abandoned = "abandoned"

class Color(str, Enum):
    white = "white"
    black = "black"

    def opposite(self) -> "Color":
        return Color.white if self == Color.black else Color.black
