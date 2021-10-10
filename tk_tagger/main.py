"""
Módulo principal
"""
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from sys import argv
import tkinter as tk
from tkinter.constants import BOTH, NW, YES
from typing import Any, DefaultDict, Dict, List, Tuple
import time

from PIL import Image, ImageTk

if len(argv) != 2:
    print(f"Usage: {argv[0]} IMAGE")
    exit()

IMAGE = argv[1]

src = Image.open(IMAGE)
INITIAL_WIDTH, INITIAL_HEIGHT = src.size

CELL_OPACITY = 0.5
CELL_SIZE = 100
CELL_BORDER_WIDTH = 1


POINTER_SIZE_INITIAL = CELL_SIZE // 2
POINTER_SIZE_MIN = 30
POINTER_SIZE_MAX = CELL_SIZE * 2

POINTER_OUTLINE_WIDTH = 2
POINTER_SIZE_CHANGE_DELTA = 20


class CellType(Enum):
    IGNORE = auto()
    FIRE = auto()
    SMOKE = auto()
    OTHER = auto()


class State(Enum):
    NORMAL = auto()


@dataclass
class StateData:
    cell_state: DefaultDict[Tuple[int, int], CellType] = field(
        default_factory=lambda: defaultdict(lambda: CellType.OTHER)
    )

    mouse_x: int = 0
    mouse_y: int = 0
    pointer_size: int = POINTER_SIZE_INITIAL

    @property
    def pointer_coords(self):
        x0 = state.mouse_x - (state.pointer_size / 2)
        y0 = state.mouse_y - (state.pointer_size / 2)
        x1 = x0 + state.pointer_size
        y1 = y0 + state.pointer_size
        return x0, y0, x1, y1

    @property
    def pointer_affected_cells(self):
        pass

    @property
    def size_ratio(self):
        return image_dimensions[0] / INITIAL_WIDTH

    @property
    def real_cell_size(self):
        return int(state.size_ratio * CELL_SIZE)

    @property
    def rows(self):
        return INITIAL_HEIGHT // CELL_SIZE

    @property
    def columns(self):
        return INITIAL_WIDTH // CELL_SIZE

    @property
    def all_cells(self):
        for y in range(self.rows):
            for x in range(self.columns):
                yield (x, y, self.cell_state[(x, y)])


class TransitionType(Enum):
    MOVE = auto()
    DRAG = auto()
    RELEASE = auto()
    MODIFY_POINTER_SIZE = auto()


state_type = State.NORMAL
state = StateData()
image_dimensions = src.size

Transition = Tuple[TransitionType, Any]


def reduce_mut(transition: Transition):
    ttype, data = transition

    if ttype == TransitionType.MOVE or ttype == TransitionType.DRAG:
        mouse_x, mouse_y = data
        state.mouse_x = mouse_x
        state.mouse_y = mouse_y

    if ttype == TransitionType.MOVE or ttype == TransitionType.DRAG:
        pass
    elif ttype == TransitionType.MODIFY_POINTER_SIZE:
        state.pointer_size = max(
            POINTER_SIZE_MIN, min(state.pointer_size + data, POINTER_SIZE_MAX)
        )


def handle_transition(transition: Transition):
    start = time.time_ns()
    reduce_mut(transition)
    redraw()
    end = time.time_ns()
    print("Time drawing:", (end - start) / 1e6)


window = tk.Tk()
canvas = tk.Canvas()
image = canvas.create_image((0, 0), anchor=NW)


CELLS = "CELLS"


def make_cell_image(fill):
    cell_image = Image.new(
        "RGBA",
        (
            state.real_cell_size,
            state.real_cell_size,
        ),
        (*window.winfo_rgb(fill), int(CELL_OPACITY * 255)),
    )

    return ImageTk.PhotoImage(cell_image)


cell_image: Dict[CellType, ImageTk.PhotoImage] = {}


def redraw():
    canvas.delete(CELLS)

    global cell_image
    cell_image = {
        CellType.FIRE: make_cell_image("red"),
        CellType.SMOKE: make_cell_image("blue"),
        CellType.OTHER: make_cell_image("white"),
        CellType.IGNORE: make_cell_image("black"),
    }

    for x, y, cell_type in state.all_cells:
        canvas.create_image(
            x * state.real_cell_size,
            y * state.real_cell_size,
            image=cell_image[cell_type],
            anchor=NW,
            tags=CELLS,
        )

    for r in range(1, state.rows):
        x0 = 0
        y0 = r * state.real_cell_size
        x1 = image_dimensions[0]
        y1 = y0
        canvas.create_line(
            x0, y0, x1, y1, fill="black", width=CELL_BORDER_WIDTH, tags=CELLS
        )

    for c in range(1, state.columns):
        x0 = c * state.real_cell_size
        y0 = 0
        x1 = x0
        y1 = image_dimensions[1]
        canvas.create_line(
            x0, y0, x1, y1, fill="black", width=CELL_BORDER_WIDTH, tags=CELLS
        )

    canvas.create_oval(
        *state.pointer_coords,
        dash=[10, 8],
        outline="red",
        width=POINTER_OUTLINE_WIDTH,
        tags=CELLS,
    )


BUTTON1 = 1 << 8


def transition_from_mouse(event):
    if event.type == tk.EventType.Motion:
        if event.state & BUTTON1:
            handle_transition((TransitionType.DRAG, (event.x, event.y)))
        else:
            handle_transition((TransitionType.MOVE, (event.x, event.y)))
    elif event.type == tk.EventType.ButtonRelease:
        handle_transition((TransitionType.RELEASE, (event.x, event.y)))
    else:
        print(event)


def transition_from_wheel(event):
    if event.num == 4:
        handle_transition(
            (TransitionType.MODIFY_POINTER_SIZE, +POINTER_SIZE_CHANGE_DELTA)
        )
    elif event.num == 5:
        handle_transition(
            (TransitionType.MODIFY_POINTER_SIZE, -POINTER_SIZE_CHANGE_DELTA)
        )


def adjust_image(_):
    global image_dimensions

    raster = src.copy()
    raster.thumbnail((window.winfo_width(), 1000))
    image_dimensions = raster.size
    photo = ImageTk.PhotoImage(raster)
    canvas.itemconfigure(image, image=photo)

    # Avoid garbage collection
    canvas.photo = photo

    redraw()


canvas.bind("<Configure>", adjust_image)

canvas.bind("<Motion>", transition_from_mouse)
canvas.bind("<ButtonRelease-1>", transition_from_mouse)

window.bind("<Button-4>", transition_from_wheel)
window.bind("<Button-5>", transition_from_wheel)

window.bind("<KeyPress>", print)
window.bind("<KeyRelease>", print)


canvas.pack(fill=BOTH, expand=YES)
window.mainloop()
