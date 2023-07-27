import dataclasses
import numpy as np

@dataclasses.dataclass
class Chassis:
    length: int | float
    size: np.ndarray
    position: np.ndarray
    mass: float
    angle: float = 0.0
