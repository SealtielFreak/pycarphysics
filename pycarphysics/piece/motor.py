import dataclasses


@dataclasses.dataclass
class Motor:
    forward_acceleration_factor: float
    back_acceleration_factor: float
    max_acceleration: float
    max_velocity: float
    acceleration: float = 0.0
