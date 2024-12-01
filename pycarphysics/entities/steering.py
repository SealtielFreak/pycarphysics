import dataclasses


@dataclasses.dataclass
class Steering:
    max_steering: int
    performance: float = 30
    direction: float = 0
