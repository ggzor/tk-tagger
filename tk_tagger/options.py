from argparse import ArgumentParser

DEBUG = True

CELL_OPACITY = 0.5
CELL_SIZE = 100
CELL_BORDER_WIDTH = 1

POINTER_SIZE_MIN = 30
POINTER_SIZE_MAX = CELL_SIZE * 2
POINTER_SIZE_INITIAL = POINTER_SIZE_MIN

POINTER_OUTLINE_WIDTH = 2
POINTER_SIZE_CHANGE_DELTA = 20

# Reduce the pointer radius a bit to avoid millimetric cell accidental selection
REDUCE_RADIUS = 5


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
