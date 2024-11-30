import abc
import math

import numpy as np

from pycarphysics.transform import escalation, rotation


class Shape(abc.ABC):
    def scale(self, axis): ...

    def translate(self, axis): ...

    def rotate(self, angle): ...


class PolygonShape(Shape):
    def __init__(self, points, origin):
        self.__points = np.array(points, dtype=np.float64)
        self.__origin = origin
        self.__angle = math.radians(0)

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, angle):
        angle = self.angle - angle
        self.rotate(angle)

    @property
    def position(self):
        return np.array(self.__origin)

    @position.setter
    def position(self, axis):
        translate = np.array(axis) - self.origin
        self.translate(translate)

    @property
    def points(self):
        return self.__points

    @property
    def origin(self):
        return self.__origin

    def scale(self, axis):
        self.__points = np.dot(self.points - self.origin, escalation(axis)) + self.origin

    def translate(self, axis):
        self.__origin += axis
        self.__points += axis

    def rotate(self, angle):
        r = math.radians(angle)

        self.__angle = self.angle - angle
        self.__points = np.dot(self.points - self.origin, rotation(r)) + self.origin


class SquareShape(PolygonShape):
    def __init__(self, size: int | float):
        super().__init__([(0, 0), (1 * size, 0), (1 * size, 1 * size), (0, 1 * size)], (0.5 * size, 0.5 * size))


class RectangleShape(PolygonShape):
    def __init__(self, size: tuple[int, int] | tuple[float, float]):
        width, height = size
        super().__init__([(0, 0), (1 * width, 0), (1 * width, 1 * height), (0, 1 * height)],
                         (0.5 * width, 0.5 * height))
