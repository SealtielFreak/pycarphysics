from pycarphysics.collisions.low import collide
from pycarphysics.collisions.shapes import PolygonShape
from pycarphysics.entities import VehicleEntity


def filter_all_collisions(entity: VehicleEntity, others: list[PolygonShape] | tuple[PolygonShape, ...]):
    for other in others:
        is_collide, move = collide(entity.points, other.points)

        if is_collide:
            yield other, move
