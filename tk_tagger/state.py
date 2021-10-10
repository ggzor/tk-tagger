"""
State handler
"""

from enum import Enum, auto
from collections import defaultdict
from typing import Any, DefaultDict, Tuple

import options
import geom


class CellType(Enum):
    IGNORE = auto()
    FIRE = auto()
    SMOKE = auto()
    OTHER = auto()


class TransitionType(Enum):
    MOVE = auto()
    DRAG = auto()
    PRESS = auto()
    RELEASE = auto()
    MODIFY_POINTER_SIZE = auto()
    TOGGLE_CELLS = auto()
    UNDO_CELLS = auto()
    RESIZE_IMAGE = auto()


Transition = Tuple[TransitionType, Any]

Coord = Tuple[int, int]
CellStates = DefaultDict[Coord, CellType]


class StateData:
    def __init__(
        self, cell_size: int, initial_image_width: int, initial_image_height: int
    ):
        self.prev_cell_states = []
        self.cell_state = defaultdict(lambda: CellType.OTHER)
        self.show_cells = True

        self.cell_size = cell_size

        self.initial_image_width = initial_image_width
        self.initial_image_height = initial_image_height

        self.real_image_width = 100
        self.real_image_height = 100

        self.mouse_x = 0
        self.mouse_y = 0

        self.pointer_size = options.POINTER_SIZE_INITIAL

    def get_focused_state_by_cell(self):
        cells: DefaultDict[Coord, bool] = defaultdict(lambda: False)

        sx, sy = self.pointer_cell
        cells[(sx, sy)] = True

        for coord in geom.get_circle_grid_overlapping_rects(
            (self.mouse_x, self.mouse_y),
            self.pointer_size // 2 - options.REDUCE_RADIUS,
            self.real_cell_size,
            self.real_cell_size,
        ):
            cells[coord] = True

        return cells

    @property
    def pointer_cell(self):
        return self.mouse_x // self.real_cell_size, self.mouse_y // self.real_cell_size

    @property
    def pointer_coords(self):
        x0 = self.mouse_x - (self.pointer_size / 2)
        y0 = self.mouse_y - (self.pointer_size / 2)
        x1 = x0 + self.pointer_size
        y1 = y0 + self.pointer_size
        return x0, y0, x1, y1

    @property
    def pointer_affected_cells(self):
        pass

    @property
    def size_ratio(self):
        return self.real_image_width / self.initial_image_width

    @property
    def real_cell_size(self):
        return int(self.size_ratio * self.cell_size)

    @property
    def rows(self):
        return self.initial_image_height // self.cell_size

    @property
    def columns(self):
        return self.initial_image_width // self.cell_size

    @property
    def all_cells(self):
        for y in range(self.rows):
            for x in range(self.columns):
                yield x, y, self.cell_state[(x, y)]

    @property
    def all_real_cells(self):
        for (x, y, state) in self.all_cells:
            yield x * self.real_cell_size, y * self.real_cell_size, state

    def reduce_mut(self, transition: Transition):
        ttype, data = transition

        if ttype == TransitionType.MOVE or ttype == TransitionType.DRAG:
            mouse_x, mouse_y = data
            self.mouse_x = mouse_x
            self.mouse_y = mouse_y

        if ttype == TransitionType.DRAG or ttype == TransitionType.PRESS:
            focused_cells = self.get_focused_state_by_cell()

            prev_state = self.cell_state.copy()

            for coords, focused in focused_cells.items():
                if focused:
                    self.cell_state[coords] = CellType.FIRE

            if self.cell_state != prev_state:
                self.prev_cell_states.append(prev_state)

        elif ttype == TransitionType.UNDO_CELLS:
            if self.prev_cell_states:
                self.cell_state = self.prev_cell_states.pop()
        elif ttype == TransitionType.MODIFY_POINTER_SIZE:
            self.pointer_size = max(
                options.POINTER_SIZE_MIN,
                min(
                    self.pointer_size + data,
                    options.POINTER_SIZE_MAX,
                ),
            )
        elif ttype == TransitionType.TOGGLE_CELLS:
            self.show_cells = not self.show_cells
        elif ttype == TransitionType.RESIZE_IMAGE:
            self.real_image_width, self.real_image_height = data
