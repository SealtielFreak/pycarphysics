import dataclasses
import math
import typing

import numpy as np

import carphysic.math
import carphysic.controls

T = typing.TypeVar("T", float, int)


class Engine:
    def __init__(self, max_rpm, torque):
        self.__max_rpm = max_rpm
        self.__torque = torque
        self.__factor_acceleration = 0.025
        self.__factor_deceleration = 1 / 100_000_000
        self.__current_rpm = 0

    def get_acceleration(self, body: carphysic.math.DynamicBody, step_torque=1):
        current_torque = self.__torque * (self.current_rpm / self.__max_rpm)

        acceleration = current_torque / body.mass

        if abs(step_torque) > 0:
            self.__current_rpm += step_torque * self.__factor_acceleration
        else:
            self.__current_rpm *= self.__factor_deceleration

        self.__current_rpm = min(self.current_rpm, self.__max_rpm)

        return acceleration

    @property
    def current_rpm(self):
        return self.__current_rpm


class Chassis:
    def __init__(self, length: float, size: np.ndarray, mass: float, angle=0.0):
        self.__length = length
        self.__size = size
        self.__mass = mass
        self.angle: float = 0.0

    @property
    def length(self):
        return self.__length

    @property
    def size(self):
        return self.__size

    @property
    def mass(self):
        return self.__mass


@dataclasses.dataclass
class Brakes:
    brake_deceleration: float
    brake_hand_deceleration: float


@dataclasses.dataclass
class Steering:
    def __init__(self, max_steering: float | int, performance: float):
        self.__max_steering = max_steering
        self.__performance = performance
        self.direction = 0

    @property
    def max_steering(self):
        return self.__max_steering

    @property
    def performance(self):
        return self.__performance


@dataclasses.dataclass(frozen=True)
class AllComponents:
    engine: Engine
    brakes: Brakes
    chassis: Chassis
    steering: Steering

    def __iter__(self):
        return iter(
            (self.engine, self.brakes, self.chassis, self.steering)
        )


def process_input(ppu: float, dt: float, body: carphysic.math.DynamicBody, controls: carphysic.controls.ControllerInput, all_components: AllComponents):
    engine, brakes, chassis, steering = all_components

    body.acceleration = engine.get_acceleration(body, step_torque=controls.throttle) * ppu

    if controls.brake_hand:
        body.acceleration -= math.copysign(all_components.brakes.brake_hand_deceleration, body.velocity[0]) * ppu

    """
    if not controls.brake_hand and not controls.throttle != 0:
        if abs(body.velocity[0]) > dt * brakes.free_deceleration:
            engine.acceleration = -math.copysign(brakes.free_deceleration, body.velocity[0])
        else:
            if dt != 0:
                engine.acceleration = -body.velocity[0] / dt

    engine.acceleration = max(-engine.max_acceleration, min(engine.acceleration, engine.max_acceleration))
    """

    if controls.steering != 0:
        steering.direction += math.copysign(steering.performance, controls.steering) * dt
    else:
        steering.direction = 0

    steering.direction = max(-steering.max_steering, min(steering.direction, steering.max_steering))

    body.angular_velocity *= 0.1 * dt
    body.velocity += (body.acceleration, 0)

    if steering.direction != 0:
        turning_radius = (chassis.length * 100) / math.sin(math.radians(steering.direction))
        body.angular_velocity = (body.velocity[0] / turning_radius) * dt

    # Fc = (m * v^2) / r
    if body.angular_velocity != 0:
        body.velocity += (
            0, math.copysign(body.acceleration / body.angular_velocity, body.angular_velocity) * ppu)
        velocity = (
            0, math.copysign(body.acceleration / body.angular_velocity, body.angular_velocity) * ppu)

    print(body.velocity, abs(body.angular_velocity))

    move = carphysic.math.rotate_vector(body.velocity, math.radians(-chassis.angle)) * dt
    rotation = math.degrees(body.angular_velocity) * dt

    return move, rotation
