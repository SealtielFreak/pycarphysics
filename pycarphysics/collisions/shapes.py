import typing
import math
import numpy as np


V = typing.TypeVar("V")


def dot_product(dot_a: V, dot_2: V) -> int | float:
    return (dot_a.x * dot_2.x) + (dot_a.y * dot_2.y)


class Vertex2(tuple):
    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def __add__(self, other):
        return Vertex2((self.x + other[0], self.y + other[1]))

    def __sub__(self, other):
        return Vertex2((self[0] - other[0], self[1] - other[1]))

    def __mul__(self, other):
        return Vertex2((self.x * other.x, self.y * other.y))

    def __truediv__(self, n):
        return Vertex2(v / n for v in self)

    def __abs__(self):
        return math.sqrt(sum(v * v for v in self))

    @property
    def project(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __class_getitem__(cls, item):
        if isinstance(item, np.ndarray):
            if item.dtype in (np.float64, np.float32):
                return Vertex2(item.astype(float))

            return Vertex2(item.astype(int))

        return Vertex2(item)


class Polygon:
    def __init__(self, points, origin, color=(255, 255, 255)):
        self.__points = [Vertex2(p) for p in points]
        self.__origin = Vertex2(origin)
        self.__angle = math.radians(0)
        self.color = color

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, angle):
        angle = self.angle - angle
        self.rotate(angle)

    @property
    def position(self):
        return Vertex2(self.__origin)

    @position.setter
    def position(self, axis):
        translate = Vertex2(axis) - self.origin
        self.translate(translate)

    @property
    def points(self):
        return [Vertex2(p) for p in self.__points]

    @property
    def origin(self):
        return Vertex2(self.__origin)

    def scale(self, axis):
        origin = self.origin
        points = []
        axis = Vertex2(axis)

        for point in list(self.points):
            point -= origin
            point = axis.x * point.x, axis.y * point.y
            point = Vertex2(point)
            point += origin
            points.append(point)

        self.__points = points

    def translate(self, axis):
        points = []
        axis = Vertex2(axis)

        for point in list(self.points):
            point += axis
            points.append(point)

        self.__origin = self.__origin + axis
        self.__points = points

    def rotate(self, angle):
        origin = self.__origin
        r = math.radians(angle)
        points = []

        for point in list(self.points):
            point -= origin

            point = Vertex2((
                point[0] * math.cos(r) - point[1] * math.sin(r) + origin[0],
                point[0] * math.sin(r) + point[1] * math.cos(r) + origin[1]
            ))

            points.append(point)

        self.__angle = self.__angle - angle
        self.__points = points


class Square(Polygon):
    def __init__(self, size, color=(255, 255, 255)):
        super().__init__([(0, 0), (1 * size, 0), (1 * size, 1 * size), (0, 1 * size)], (0.5 * size, 0.5 * size), color)


class Rectangle(Polygon):
    def __init__(self, size, color=(255, 255, 255)):
        width, height = size
        super().__init__([(0, 0), (1 * width, 0), (1 * width, 1 * height), (0, 1 * height)],
                         (0.5 * width, 0.5 * height), color)
