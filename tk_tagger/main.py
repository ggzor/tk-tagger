"""
Main module
"""
import tkinter as tk
from tkinter.constants import BOTH, NW, YES
from typing import Dict

from PIL import Image, ImageTk

import options
from state import CellType, StateData, Transition, TransitionType

args = options.parse_args()

src = Image.open(args.image)
src_width, src_height = src.size
state = StateData(options.CELL_SIZE, src_width, src_height)

window = tk.Tk()
canvas = tk.Canvas()
image = canvas.create_image((0, 0), anchor=NW)


def main():
    bind_events()
    make_layout()
    window.mainloop()


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
    cell_image = {
        CellType.FIRE: make_cell_image("red"),
        CellType.SMOKE: make_cell_image("blue"),
        CellType.OTHER: make_cell_image("white"),
        CellType.IGNORE: make_cell_image("black"),
    }

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
    elif event.char == "\x1a" or event.char == "u":
        # Ctrl-Z
        handle_transition((TransitionType.UNDO_CELLS, None))


photo = None


def adjust_image(_):
    # Avoid garbage collection
    global photo

    raster = src.copy()
    raster.thumbnail((window.winfo_width(), 1000))
    photo = ImageTk.PhotoImage(raster)
    canvas.itemconfigure(image, image=photo)

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
- Press t to toggle cells
- Press Ctrl-z to undo
- Scroll to increase/decrease pointer size
"""[
    :-1
]


def make_layout():
    l1 = tk.Label(text=HELP_TEXT, font="14", justify="left")
    l1.pack(pady=10, padx=10, anchor="w")

    buttons = tk.Frame()

    b1 = tk.Button(buttons, text="Save and close", font="14")
    b1.grid(row=0, column=0, padx=10)

    b2 = tk.Button(buttons, text="Reset", font="14")
    b2.grid(row=0, column=1, padx=5)

    buttons.pack(anchor="w", pady=20)
    canvas.pack(fill=BOTH, expand=YES)


if __name__ == "__main__":
    main()
