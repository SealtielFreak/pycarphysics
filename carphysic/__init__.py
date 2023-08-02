import dataclasses
import math
import typing

import numpy as np

import carphysic.components
import carphysic.controls
import carphysic.math

DEFAULT_GENERIC_ENGINE = carphysic.components.Engine(200, 6000)
DEFAULT_GENERIC_BRAKES = carphysic.components.Brakes(1, 0.05)
DEFAULT_GENERIC_STEERING = carphysic.components.Steering(120, 80)


class Vehicle:
    def __init__(self, chassis, engine=DEFAULT_GENERIC_ENGINE, brakes=DEFAULT_GENERIC_BRAKES, steering=DEFAULT_GENERIC_STEERING):

        self.__all_components = carphysic.components.AllComponents(
            engine, brakes, chassis, steering
        )

        self.__body = carphysic.math.DynamicBody(mass=chassis.mass)

    def update(self, dt: float, controller: carphysic.controls.ControllerInput):
        ppu = 0.05

        move, rotation = carphysic.components.process_input(
            ppu, dt, self.__body, controller, self.__all_components)

        self.__body.position += move
        self.__all_components.chassis.angle += rotation

        return self.__body.position, self.__all_components.chassis.angle
