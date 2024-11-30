import math
import typing

import numpy as np

from pycarphysics.collisions.shapes import PolygonShape
from pycarphysics.piece.brakes import Brakes
from pycarphysics.piece.chassis import Chassis
from pycarphysics.piece.motor import Motor
from pycarphysics.piece.steering import Steering
from pycarphysics.transform import rotation

DEFAULT_GENERIC_MOTOR = Motor(1 / 1000_000_00, 2 / 1000_000_000, 1 / 5, 1 / 100)
DEFAULT_GENERIC_BRAKES = Brakes(1 / 100000, 1 / 50000, 1 / 200000)
DEFAULT_GENERIC_STEERING = Steering(120, 80)


class VehicleEntity:
    def __init__(self,
                 chassis: Chassis,
                 collider: PolygonShape,
                 motor: Motor = DEFAULT_GENERIC_MOTOR,
                 brakes: Brakes = DEFAULT_GENERIC_BRAKES,
                 steering: Steering = DEFAULT_GENERIC_STEERING):
        self.velocity: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.force: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.angular_velocity = 0

        self.chassis = chassis
        self.motor = motor
        self.brakes = brakes
        self.steering = steering
        self.__collider = collider
        self.__ppu = 32

    @property
    def collider(self):
        return self.__collider

    @property
    def points(self):
        return self.collider.points

    @property
    def ppu(self):
        return self.__ppu

    def process(
            self,
            dt: float,
            throttle: int | float,
            brake_hand: bool,
            steering: int | float) -> typing.Tuple[np.ndarray, float]:

        if throttle != 0:
            if throttle > 0:
                if self.velocity[0] < 0:
                    self.motor.acceleration = self.brakes.brake_deceleration
                else:
                    self.motor.acceleration += self.motor.forward_acceleration_factor * dt
            else:
                if self.velocity[0] > 0:
                    self.motor.acceleration = -self.brakes.brake_deceleration
                else:
                    self.motor.acceleration -= self.motor.back_acceleration_factor * dt

        if brake_hand:
            if throttle == 0:
                if abs(self.velocity[0]) > dt * self.brakes.brake_deceleration:
                    self.motor.acceleration = -math.copysign(self.brakes.brake_hand_deceleration, self.velocity[0])
                else:
                    self.motor.acceleration = -self.velocity[0] / dt
            else:
                self.motor.acceleration = -math.copysign(self.brakes.free_deceleration, self.velocity[0])

        if not brake_hand and not throttle != 0:
            if abs(self.velocity[0]) > dt * self.brakes.free_deceleration:
                self.motor.acceleration = -math.copysign(self.brakes.free_deceleration, self.velocity[0])
            else:
                if dt != 0:
                    self.motor.acceleration = -self.velocity[0] / dt

        self.motor.acceleration = max(-self.motor.max_acceleration,
                                      min(self.motor.acceleration, self.motor.max_acceleration))

        if steering > 0:
            self.steering.direction -= self.steering.performance * dt
        elif steering < 0:
            self.steering.direction += self.steering.performance * dt
        else:
            self.steering.direction = 0

        self.steering.direction = max(-self.steering.max_steering,
                                      min(self.steering.direction, self.steering.max_steering))

        self.velocity += (self.motor.acceleration * self.chassis.mass, 0)
        self.velocity[0] = max(-self.motor.max_velocity, min(self.velocity[0], self.motor.max_velocity))

        self.angular_velocity *= 0.1 * dt
        self.velocity[1] *= 2 / self.chassis.mass

        if self.steering.direction != 0 and abs(self.motor.acceleration * dt) != 0:
            turning_radius = (self.chassis.length * 15) / math.sin(math.radians(self.steering.direction))
            self.angular_velocity = (self.velocity[0] / turning_radius) * dt
            self.velocity += (0, math.copysign(self.motor.acceleration * self.chassis.mass, self.angular_velocity))

        if abs(self.steering.direction) > (self.steering.max_steering * 0.75):
            if brake_hand and abs(self.motor.acceleration) > 0:
                self.angular_velocity += math.copysign(0.0025, self.angular_velocity) + self.motor.acceleration

        if abs(self.motor.acceleration * self.chassis.mass) > self.motor.max_acceleration * 0.05:
            self.velocity += (0, self.angular_velocity + math.copysign(
                self.motor.acceleration * self.chassis.mass,
                self.angular_velocity
            ))

        position = self.chassis.position * self.ppu

        r = math.radians(-self.chassis.angle)

        self.chassis.position += np.dot(rotation(r), self.velocity) * dt
        self.chassis.angle += math.degrees(self.angular_velocity) * dt

        self.__collider.angle = -self.chassis.angle
        self.__collider.position = position

        return position, self.chassis.angle
