import numpy as np


def rotation(radians: int | float) -> np.ndarray:
    return np.array([[np.cos(radians), -np.sin(radians)], [np.sin(radians), np.cos(radians)]])


def escalation(axis: tuple[int, int] | tuple[float, float] | list) -> np.ndarray:
    return np.array([[axis[0], 0], [0, axis[1]]])
