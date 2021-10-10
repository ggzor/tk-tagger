from enum import Enum, auto


class CellType(Enum):
    IGNORE = auto()
    FIRE = auto()
    SMOKE = auto()
    OTHER = auto()
