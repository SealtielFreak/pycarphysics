import numpy as np

from carphysic import Vehicle
from carphysic.components import Chassis
from carphysic.controls import ControllerInput


if __name__ == "__main__":
    chassis = Chassis(
        4, np.array([32, 8], dtype=np.float32), 1500)

    chassis.angle = 90

    vehicle = Vehicle(
        chassis
    )

    while True:
        vehicle.update(1, ControllerInput(1, 0, True))
        print(vehicle.position)

