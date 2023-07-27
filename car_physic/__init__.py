import math
import typing

import numpy as np

import car_physic.piece.brakes
import car_physic.piece.chassis
import car_physic.piece.motor
import car_physic.piece.steering


DEFAULT_GENERIC_MOTOR = car_physic.piece.motor.Motor(1 / 1000_000_00, 2 / 1000_000_000, 1 / 5, 1 / 100)
DEFAULT_GENERIC_BRAKES = car_physic.piece.brakes.Brakes(1 / 100000, 1 / 50000, 1 / 200000)
DEFAULT_GENERIC_STEERING = car_physic.piece.steering.Steering(120, 80)


def rotate_vector(vector: np.ndarray | list | tuple[int, int], radians: int | float) -> np.ndarray:
    rotation = np.array([[np.cos(radians), -np.sin(radians)],
                         [np.sin(radians), np.cos(radians)]])

    return np.dot(rotation, vector)


class CarPhysic:
    def __init__(self, chassis: car_physic.piece.chassis.Chassis, motor=DEFAULT_GENERIC_MOTOR, brakes=DEFAULT_GENERIC_BRAKES,
                 steering=DEFAULT_GENERIC_STEERING):
        self.velocity: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.force: np.ndarray = np.array([0, 0], dtype=np.float32)
        self.angular_velocity = 0

        self.chassis: car_physic.piece.chassis.Chassis = chassis
        self.motor: car_physic.piece.motor.Motor = motor
        self.brakes: car_physic.piece.brakes.Brakes = brakes
        self.steering: car_physic.piece.steering.Steering = steering

    def process(self, dt: float, throttle: int | float, brake_hand: bool, steering: int | float) -> typing.Tuple[
        np.ndarray, float]:
        ppu = 32

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
            self.velocity += (0, self.angular_velocity + math.copysign(self.motor.acceleration * self.chassis.mass, self.angular_velocity))
            print(self.angular_velocity, self.motor.acceleration * self.chassis.mass, self.velocity)

        self.chassis.position += rotate_vector(self.velocity, math.radians(-self.chassis.angle)) * dt
        self.chassis.angle += math.degrees(self.angular_velocity) * dt

        return self.chassis.position * ppu, self.chassis.angle
