"""
Main module
"""
from pathlib import Path
import tkinter as tk
from tkinter.constants import BOTH, NW, VERTICAL, Y, YES
from typing import Dict

from PIL import Image, ImageTk

import options
from state import CellType, StateData, Transition, TransitionType
import state_io

args = options.parse_args()
SOURCE_IMG = Path(args.image)
TARGET_FILE = SOURCE_IMG.with_suffix(".cells.txt")

src = Image.open(SOURCE_IMG.absolute())
src_width, src_height = src.size
state = StateData(options.CELL_SIZE, src_width, src_height)

if TARGET_FILE.exists():
    state.cell_state = state_io.read_cells(TARGET_FILE)

window = tk.Tk()
canvas = tk.Canvas()
image = canvas.create_image((0, 0), anchor=NW)


def main():
    bind_events()
    make_layout()
    window.mainloop()


def save_and_close():
    state_io.write_cells(TARGET_FILE, state)
    exit(0)


def make_cell_image(fill):
    cell_image = Image.new(
        "RGBA",
        (
            state.real_cell_size,
            state.real_cell_size,
        ),
        (*window.winfo_rgb(fill), int(options.CELL_OPACITY * 255)),
    )

    return ImageTk.PhotoImage(cell_image)


# Blame the garbage collector
cell_image: Dict[CellType, ImageTk.PhotoImage] = {}
CELL_TAG = "CELLS"


def redraw():
    canvas.delete(CELL_TAG)

    global cell_image
    cell_image = {c: make_cell_image(options.CELL_COLORS[c]) for c in CellType}

    if state.show_cells:
        for x, y, cell_type in state.all_real_cells:
            canvas.create_image(
                x, y, image=cell_image[cell_type], anchor=NW, tags=CELL_TAG
            )

    for r in range(1, state.rows):
        x0 = 0
        y0 = r * state.real_cell_size
        x1 = state.real_image_width
        y1 = y0
        canvas.create_line(
            x0, y0, x1, y1, fill="black", width=options.CELL_BORDER_WIDTH, tags=CELL_TAG
        )

    for c in range(1, state.columns):
        x0 = c * state.real_cell_size
        y0 = 0
        x1 = x0
        y1 = state.real_image_height
        canvas.create_line(
            x0, y0, x1, y1, fill="black", width=options.CELL_BORDER_WIDTH, tags=CELL_TAG
        )

    focused_cell = state.get_focused_state_by_cell()
    for x, y, cell_type in state.all_cells:
        x0 = x * state.real_cell_size
        y0 = y * state.real_cell_size
        x1 = x0 + state.real_cell_size
        y1 = y0 + state.real_cell_size

        if focused_cell[(x, y)]:
            canvas.create_rectangle(
                x0, y0, x1, y1, outline="red", width=2, tags=CELL_TAG
            )

    canvas.create_oval(
        *state.pointer_coords,
        dash=(10, 8),
        outline="red",
        width=options.POINTER_OUTLINE_WIDTH,
        tags=CELL_TAG,
    )


BUTTON1 = 1 << 8


def handle_transition(transition: Transition):
    import time

    start = time.time_ns()
    state.reduce_mut(transition)
    redraw()
    end = time.time_ns()
    if options.DEBUG:
        print("Time drawing:", (end - start) / 1e6)


def transition_from_mouse(event):
    if event.type == tk.EventType.Motion:
        if event.state & BUTTON1:
            handle_transition((TransitionType.DRAG, (event.x, event.y)))
        else:
            handle_transition((TransitionType.MOVE, (event.x, event.y)))
    elif event.type == tk.EventType.ButtonRelease:
        handle_transition((TransitionType.RELEASE, (event.x, event.y)))
    elif event.type == tk.EventType.ButtonPress:
        handle_transition((TransitionType.PRESS, (event.x, event.y)))


def transition_from_wheel(event):
    if event.num == 4:
        handle_transition(
            (TransitionType.MODIFY_POINTER_SIZE, +options.POINTER_SIZE_CHANGE_DELTA)
        )
    elif event.num == 5:
        handle_transition(
            (TransitionType.MODIFY_POINTER_SIZE, -options.POINTER_SIZE_CHANGE_DELTA)
        )


def transition_from_key(event):
    if event.char == "t":
        handle_transition((TransitionType.TOGGLE_CELLS, None))
        adjust_brush_label()
    elif event.char == "\x1a" or event.char == "u":
        # Ctrl-Z
        handle_transition((TransitionType.UNDO_CELLS, None))
    elif event.char == "a":
        handle_transition((TransitionType.PREV_BRUSH, None))
        adjust_brush_label()
    elif event.char == "d":
        handle_transition((TransitionType.NEXT_BRUSH, None))
        adjust_brush_label()


def transition_from_reset():
    handle_transition((TransitionType.RESET_CELLS, None))


photo = None


def adjust_image(_):
    # Avoid garbage collection
    global photo

    raster = src.copy()
    raster.thumbnail((window.winfo_width(), int(window.winfo_height() * 0.7)))
    photo = ImageTk.PhotoImage(raster)
    canvas.itemconfigure(image, image=photo)
    canvas.configure(height=raster.height + 10)

    handle_transition((TransitionType.RESIZE_IMAGE, raster.size))


def bind_events():
    canvas.bind("<Configure>", adjust_image)

    canvas.bind("<Motion>", transition_from_mouse)
    canvas.bind("<ButtonRelease-1>", transition_from_mouse)
    canvas.bind("<ButtonPress-1>", transition_from_mouse)

    window.bind("<Button-4>", transition_from_wheel)
    window.bind("<Button-5>", transition_from_wheel)

    window.bind("<KeyPress>", transition_from_key)
    window.bind("<KeyRelease>", transition_from_key)


HELP_TEXT = """\
Help:
- Press a/d to select the previous/next brush
- Press t to toggle cells
- Press Ctrl-z to undo
- Scroll to increase/decrease pointer size
"""[
    :-1
]


brush_rect = None
brush_label = None


def adjust_brush_label():
    color_disabled = "" if state.show_cells else "(cells are hidden)"

    brush_rect.configure(background=options.CELL_COLORS[state.cell_brush])
    brush_label.configure(text=f"{state.cell_brush.name}{color_disabled}")


def make_layout():
    canvas.pack(fill=BOTH)

    indicators = tk.Frame()
    if True:
        global brush_rect, brush_label

        brush_rect = tk.Canvas(
            indicators,
            width=options.BRUSH_INDICATOR_SIZE,
            height=options.BRUSH_INDICATOR_SIZE,
        )
        brush_rect.grid(row=0, column=0)

        brush_label = tk.Label(
            indicators, font=str(int(options.BRUSH_INDICATOR_SIZE / 2))
        )
        brush_label.grid(row=0, column=1, padx=5, pady=5)

        adjust_brush_label()
    indicators.pack(anchor="center", pady=10, padx=10)

    l1 = tk.Label(text=HELP_TEXT, font="14", justify="left")
    l1.pack(pady=10, padx=10, anchor="nw", fill="y", expand=YES)

    buttons = tk.Frame()
    if True:
        b1 = tk.Button(
            buttons, text="Save and close", font="14", command=save_and_close
        )
        b1.grid(row=0, column=0, padx=10)

        b2 = tk.Button(buttons, text="Reset", font="14", command=transition_from_reset)
        b2.grid(row=0, column=1, padx=5)
    buttons.pack(anchor="center", pady=20)


if __name__ == "__main__":
    main()
