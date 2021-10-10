from argparse import ArgumentParser

CELL_OPACITY = 0.5
CELL_SIZE = 100
CELL_BORDER_WIDTH = 1

POINTER_SIZE_INITIAL = CELL_SIZE // 2
POINTER_SIZE_MIN = 30
POINTER_SIZE_MAX = CELL_SIZE * 2

POINTER_OUTLINE_WIDTH = 2
POINTER_SIZE_CHANGE_DELTA = 20


def parse_args():
    parser = ArgumentParser(description="Tag cells from an image")
    parser.add_argument("image", metavar="IMAGE", help="The image to tag")
    return parser.parse_args()
