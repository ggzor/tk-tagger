from argparse import ArgumentParser
from cell import CellType

DEBUG = True

CELL_COLORS = {
    CellType.IGNORE: "black",
    CellType.FIRE: "red",
    CellType.SMOKE: "blue",
    CellType.OTHER: "green",
}
DEFAULT_CELL_COLOR = CellType.IGNORE

CELL_OPACITY = 0.5
CELL_SIZE = 50

CELL_BORDER_WIDTH = 1
CELL_BORDER_COLOR = "white"

CELL_FOCUS_BORDER_WIDTH = 2
CELL_FOCUS_BORDER_COLOR = "red"

POINTER_SIZE_MIN = 30
POINTER_SIZE_MAX = CELL_SIZE * 5
POINTER_SIZE_INITIAL = POINTER_SIZE_MIN

POINTER_OUTLINE_WIDTH = 2
POINTER_SIZE_CHANGE_DELTA = 20

# Reduce the pointer radius a bit to avoid millimetric cell accidental selection
REDUCE_RADIUS = 5

BRUSH_INDICATOR_SIZE = 40

KEYBINDING_TOGGLE_KEY = "f"


def parse_args():
    parser = ArgumentParser(description="Tag cells from an image")
    parser.add_argument("image", metavar="IMAGE", help="The image to tag")
    parser.add_argument(
        "-v", "--verbose", help="Print useful debug output", action="store_true"
    )

    result = parser.parse_args()

    # Fill globals (bad idea?)
    global DEBUG
    DEBUG = result.verbose

    return result
