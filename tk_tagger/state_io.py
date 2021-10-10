from pathlib import Path
import re
from state import CellStates, CellType, StateData


def write_cells(target: Path, state: StateData):
    with open(target, "w") as f:
        for row in range(state.rows):
            for col in range(state.columns):
                f.write(f"{row},{col},{state.cell_state[(col, row)].name}\n")


CELL_LINE_RE = re.compile(r"(?P<row>\d+),(?P<column>\d+),(?P<type>\w+)")


def read_cells(target: Path) -> CellStates:
    result = CellStates()

    with open(target, "r") as f:
        for line in f:
            if m := CELL_LINE_RE.match(line):
                g = m.groupdict()

                row = int(g["row"])
                column = int(g["column"])
                t = CellType[g["type"]]

                result[(column, row)] = t

    return result
