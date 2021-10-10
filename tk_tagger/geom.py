EPSILON = 1e-4


def solve_circle_line_intersection(cx, cy, r, x):
    det = r ** 2 - (x - cx) ** 2

    if det < 0:
        return []
    elif abs(det) < EPSILON:
        return [cy]
    else:
        root = det ** 0.5
        return [+root + cy, -root + cy]


def get_circle_grid_overlapping_rects(center, radius, cell_width, cell_height):
    originalx, originaly = center

    norm_x = originalx / cell_width
    norm_y = originaly / cell_height

    norm_rx = radius / cell_width
    norm_ry = radius / cell_height

    north = norm_y - norm_ry
    south = norm_y + norm_ry

    west = norm_x - norm_rx
    east = norm_x + norm_rx

    # Cells within circle bounding box
    for y in range(int(north) + 1, int(south)):
        for x in range(int(west) + 1, int(east)):
            yield x, y

    # Check circle intersections with lines of each direction
    # FIXME: Refactor
    north_row = int(north) + 1
    south_row = int(south)

    west_column = int(west) + 1
    east_column = int(east)

    north_intersections = [
        x / cell_width
        for x in sorted(
            solve_circle_line_intersection(
                originaly, originalx, radius, north_row * cell_height
            )
        )
    ]
    if len(north_intersections) == 2:
        start, end = north_intersections
        for x in range(int(start), int(end) + 1):
            yield x, north_row - 1

    south_intersections = [
        x / cell_width
        for x in sorted(
            solve_circle_line_intersection(
                originaly, originalx, radius, south_row * cell_height
            )
        )
    ]
    if len(south_intersections) == 2:
        start, end = south_intersections
        for x in range(int(start), int(end) + 1):
            yield x, south_row

    west_intersections = [
        y / cell_height
        for y in sorted(
            solve_circle_line_intersection(
                originalx, originaly, radius, west_column * cell_width
            )
        )
    ]
    if len(west_intersections) == 2:
        start, end = west_intersections
        for y in range(int(start), int(end) + 1):
            yield west_column - 1, y

    east_intersections = [
        y / cell_height
        for y in sorted(
            solve_circle_line_intersection(
                originalx, originaly, radius, east_column * cell_width
            )
        )
    ]
    if len(east_intersections) == 2:
        start, end = east_intersections
        for y in range(int(start), int(end) + 1):
            yield east_column, y
