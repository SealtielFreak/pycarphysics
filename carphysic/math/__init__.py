import dataclasses
import typing

import numpy as np


T = typing.TypeVar("T", float, int)


def rotate_vector(vector: np.ndarray | typing.List[T] | typing.Tuple[T, T], radians: T) -> np.ndarray:
    rotation = np.array([[np.cos(radians), -np.sin(radians)],
                         [np.sin(radians), np.cos(radians)]])

    return np.dot(rotation, vector)


@dataclasses.dataclass
class DynamicBody:
    angular_velocity: T = 0
    acceleration: T = 0
    mass: T = 0
    position = np.array([0, 0], dtype=np.float32)
    velocity = np.array([0, 0], dtype=np.float32)
