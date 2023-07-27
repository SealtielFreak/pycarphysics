import dataclasses


@dataclasses.dataclass
class Brakes:
    brake_deceleration: float
    brake_hand_deceleration: float
    free_deceleration: float
