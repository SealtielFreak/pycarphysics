import math

import numpy as np


def get_vertex_from_rect(rect):
    return np.array(
        (
            rect.topleft,
            rect.topright,
            rect.bottomright,
            rect.bottomleft
        )
    )


def rotate_point(point, angle, center, translate):
    angle_rad = math.radians(angle)

    tx, ty = translate
    x, y = point
    cx, cy = center

    return (
        math.ceil(cx + (math.cos(angle_rad) * (x - cx)) - (math.sin(angle_rad) * (y - cy)) + tx),
        math.ceil(cy + (math.sin(angle_rad) * (x - cx)) + (math.cos(angle_rad) * (y - cy)) + ty)
    )


def get_local_transform(vertices, angle: int | float, center=(0, 0), translate=(0, 0)):
    return [rotate_point(vertex, angle, center, translate) for vertex in vertices]


def get_mead_vertices(vertices):
    length = len(vertices)
    x, y = 0, 0

    for vertex in vertices:
        x += vertex[0]
        y += vertex[1]

    return x / length, y / length
