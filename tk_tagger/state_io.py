from pathlib import Path
import re
from typing import Tuple
from state import CellStates, CellType, StateData


def write_cells(target: Path, state: StateData):
    with open(target, "w") as f:
        f.write(f"offset,{state.offset_x},{state.offset_y}\n")
        for row in range(state.rows):
            for col in range(state.columns):
                f.write(f"{row},{col},{state.cell_state[(col, row)].name}\n")


OFFSET_LINE_RE = re.compile(r"offset,(?P<offset_x>\d+),(?P<offset_y>\d+)")
CELL_LINE_RE = re.compile(r"(?P<row>\d+),(?P<column>\d+),(?P<type>\w+)")


def read_cells(target: Path) -> Tuple[int, int, CellStates]:
    offset_x = 0
    offset_y = 0
    result = CellStates()

    with open(target, "r") as f:
        for line in f:
            if m := CELL_LINE_RE.match(line):
                g = m.groupdict()

                row = int(g["row"])
                column = int(g["column"])
                t = CellType[g["type"]]

                result[(column, row)] = t
            elif m := OFFSET_LINE_RE.match(line):
                g = m.groupdict()

                offset_x = int(g["offset_x"])
                offset_y = int(g["offset_y"])

    return offset_x, offset_y, result
