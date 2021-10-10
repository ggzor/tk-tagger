"""
State handler
"""

from enum import Enum, auto
from collections import defaultdict
from typing import Any, DefaultDict, Tuple

import options
import geom
from cell import CellType


class TransitionType(Enum):
    MOVE = auto()
    DRAG = auto()
    PRESS = auto()
    MODIFY_POINTER_SIZE = auto()
    TOGGLE_CELLS = auto()
    UNDO_CELLS = auto()
    RESIZE_IMAGE = auto()
    RESET_CELLS = auto()
    FILL_WITH_BRUSH = auto()

    PREV_BRUSH = auto()
    NEXT_BRUSH = auto()

    DRAG_GRID = auto()
    DRAG_GRID_PRESS = auto()
    DRAG_GRID_RELEASE = auto()


Transition = Tuple[TransitionType, Any]

Coord = Tuple[int, int]


class CellStates(DefaultDict[Coord, CellType]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = lambda: options.DEFAULT_CELL_COLOR


class StateData:
    def __init__(
        self, cell_size: int, initial_image_width: int, initial_image_height: int
    ):
        self.prev_cell_states = []
        self.cell_state = CellStates()
        self.cell_brush = CellType.FIRE
        self.show_cells = True

        self.cell_size = cell_size

        self.initial_image_width = initial_image_width
        self.initial_image_height = initial_image_height

        self.real_image_width = 100
        self.real_image_height = 100

        self.offset_x = 0
        self.offset_y = 0

        self.mouse_x = 0
        self.mouse_y = 0

        self.pointer_size = options.POINTER_SIZE_INITIAL

        self.dragging = False
        self.dragging_start = None

    def get_focused_state_by_cell(self):
        cells: DefaultDict[Coord, bool] = defaultdict(lambda: False)

        sx, sy = self.pointer_cell
        cells[(sx, sy)] = True

        for coord in geom.get_circle_grid_overlapping_rects(
            (self.mouse_x - self.offset_x, self.mouse_y - self.offset_y),
            self.pointer_size // 2 - options.REDUCE_RADIUS,
            self.real_cell_size,
            self.real_cell_size,
        ):
            cells[coord] = True

        return cells

    @property
    def pointer_cell(self):
        return (
            (self.mouse_x - self.offset_x) // self.real_cell_size,
            (self.mouse_y - self.offset_y) // self.real_cell_size,
        )

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
    def max_offset_x(self):
        return self.real_image_width % self.real_cell_size

    @property
    def max_offset_y(self):
        return self.real_image_height % self.real_cell_size

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
            yield (
                x * self.real_cell_size + self.offset_x,
                y * self.real_cell_size + self.offset_y,
                state,
            )

    def update_cell_state(self, new_state: CellStates):
        if new_state != self.cell_state:
            self.prev_cell_states.append(self.cell_state)
            self.cell_state = new_state

    def reduce_mut(self, transition: Transition):
        ttype, data = transition

        if ttype in [
            TransitionType.MOVE,
            TransitionType.DRAG,
            TransitionType.DRAG_GRID,
        ]:
            mouse_x, mouse_y = data
            self.mouse_x = mouse_x
            self.mouse_y = mouse_y

        if not self.dragging:
            if ttype == TransitionType.DRAG or ttype == TransitionType.PRESS:
                focused_cells = self.get_focused_state_by_cell()
                new_state = self.cell_state.copy()

                for coords, focused in focused_cells.items():
                    if focused:
                        new_state[coords] = self.cell_brush

                self.update_cell_state(new_state)

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
            elif ttype == TransitionType.RESET_CELLS:
                self.update_cell_state(CellStates())
            elif (
                ttype == TransitionType.PREV_BRUSH or ttype == TransitionType.NEXT_BRUSH
            ):
                offset = -1 if ttype == TransitionType.PREV_BRUSH else +1
                brushes = list(CellType)
                new_brush_idx = (brushes.index(self.cell_brush) + offset) % len(brushes)
                self.cell_brush = brushes[new_brush_idx]
            elif ttype == TransitionType.FILL_WITH_BRUSH:
                new_state = CellStates()
                new_state.update(
                    {
                        (col, row): data
                        for col in range(self.columns)
                        for row in range(self.rows)
                    }
                )
                self.update_cell_state(new_state)
            elif ttype == TransitionType.DRAG_GRID_PRESS:
                sx, sy = data

                self.dragging = True
                self.dragging_start = sx - self.offset_x, sy - self.offset_y
        else:
            if ttype == TransitionType.DRAG_GRID_RELEASE:
                self.dragging = False
                self.dragging_start = None
            elif ttype == TransitionType.DRAG_GRID:
                sx, sy = self.dragging_start
                x, y = data

                self.offset_x = x - sx
                self.offset_y = y - sy

                self.offset_x = max(0, min(self.offset_x, self.max_offset_x))
                self.offset_y = max(0, min(self.offset_y, self.max_offset_y))
