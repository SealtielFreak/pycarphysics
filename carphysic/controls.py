import dataclasses


@dataclasses.dataclass(frozen=True)
class ControllerInput:
    throttle: int | float
    steering: int | float
    brake_hand: bool
