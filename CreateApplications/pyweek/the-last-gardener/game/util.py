from __future__ import division, print_function, unicode_literals

import math

def get_tile_pos(world_pos, tile_size, y_offset):
    return (world_pos[0] // tile_size, (world_pos[1] - y_offset) // tile_size)

def get_world_pos(tile_pos, tile_size, y_offset):
    return (tile_pos[0] * tile_size, (tile_pos[1] * tile_size) + y_offset)

def get_velocity(speed, radians):
    return (speed * math.cos(radians), speed * math.sin(radians))

def get_angle(origin, point):
    """Gets the angle in radians between two points.

    The angle is measured along the x-axis.
    """
    return math.atan2(point[1] - origin[1], point[0] - origin[0])

def distance(a, b):
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def direction(start, end):
    """Returns a vector indicating the direction from 'start' to 'end'.

    The values that can be returned for each component is either -1, 0, or 1.
    """
    x_diff = end[0] - start[0]
    y_diff = end[1] - start[1]

    # math.copysign(1, 0) == 1
    x_sign = 0 if x_diff == 0 else int(math.copysign(1, x_diff))
    y_sign = 0 if y_diff == 0 else int(math.copysign(1, y_diff))

    return (x_sign, y_sign)

if __name__ == '__main__':
    a = [5, 7]
    b = get_tile_pos(get_world_pos(a, 20, 0), 20, 0)

    assert a[0] == b[0] and a[1] == b[1]

    assert direction((0, 0), (5, 5)) == (1, 1)
