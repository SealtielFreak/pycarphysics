import numpy as np

from pycarphysics.collisions.shapes import PolygonShape
from pycarphysics.entities import VehicleEntity


def slide(entity: VehicleEntity, other: PolygonShape, move: np.ndarray, **kwargs):
    force = kwargs.get("force", 0.35)
    deceleration = kwargs.get("deceleration", 0.25)

    entity.collider.translate(move)

    entity.chassis.position += move / entity.ppu
    entity.motor.acceleration *= -deceleration
    entity.velocity[0] *= -1 * force
    entity.velocity[1] *= -1 * force

    return entity, other


def bounce(entity: VehicleEntity, other: PolygonShape, move: np.ndarray, **kwargs):
    force = kwargs.get("force", 0.35)

    entity.collider.translate(move)

    entity.chassis.position += move / entity.ppu

    entity.velocity[0] *= -1 * force
    entity.velocity[1] *= -1 * force

    return entity, other


def push(entity: VehicleEntity, other: PolygonShape, move: np.ndarray, **kwargs):
    force = kwargs.get("force", 0.95)
    deceleration = kwargs.get("deceleration", 0.05)

    entity.collider.translate(move)

    entity.chassis.position += move / entity.ppu
    entity.motor.acceleration *= deceleration

    other.translate(-move)

    entity.velocity[0] *= force
    entity.velocity[1] *= force

    return entity, other
