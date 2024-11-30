import abc
import math
import typing

import numpy as np

from pycarphysics.transform import escalation, rotation

Verx = typing.TypeVar('Verx', tuple[int, int], tuple[float, float], list[int], list[float], np.ndarray)


class Shape(abc.ABC):
    def scale(self, axis: Verx): ...

    def translate(self, axis: Verx): ...

    def rotate(self, angle: int | float, origin=None): ...


class PolygonShape(Shape):
    def __init__(self, points, origin):
        self.__points = np.array(points, dtype=np.float64)
        self.__origin = np.array(origin, dtype=np.float64)
        self.__angle = math.radians(0)

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, angle: Verx):
        angle = self.angle - angle
        self.rotate(angle)

    @property
    def position(self):
        return np.array(self.__origin)

    @position.setter
    def position(self, axis: Verx):
        translate = np.array(axis) - self.origin
        self.translate(translate)

    @property
    def points(self):
        return self.__points

    @property
    def origin(self):
        return self.__origin

    def scale(self, axis: Verx):
        self.__points = np.dot(self.points - self.origin, escalation(axis)) + self.origin

    def translate(self, axis: Verx):
        self.__origin += axis
        self.__points += axis

    def rotate(self, angle: int | float, origin=None):
        r = math.radians(angle)

        if origin is None:
            origin = self.origin

        self.__angle = self.angle - angle
        self.__points = np.dot(self.points - origin, rotation(r)) + origin


class SquareShape(PolygonShape):
    def __init__(self, size: int | float, origin=None):
        if origin is None:
            origin = (0.5 * size, 0.5 * size)

        super().__init__(
            [(0, 0), (1 * size, 0), (1 * size, 1 * size), (0, 1 * size)], origin
        )


class RectangleShape(PolygonShape):
    def __init__(self, size: tuple[int, int] | tuple[float, float], origin=None):
        width, height = size

        if origin is None:
            origin = (0.5 * width, 0.5 * height)

        super().__init__(
            [(0, 0), (1 * width, 0), (1 * width, 1 * height), (0, 1 * height)], origin
        )
