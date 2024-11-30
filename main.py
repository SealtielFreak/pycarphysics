import os

import numpy as np
import pygame

from pycarphysics import VehicleEntity
from pycarphysics.collisions.low import collide
from pycarphysics.collisions.shapes import SquareShape, RectangleShape, PolygonShape
from pycarphysics.piece.chassis import Chassis
from pycarphysics.piece.steering import Steering

SCREEN_TITLE = "Car demo physic"
SCREEN_SIZE = 640, 480
DEFAULT_FRAME_RATE = 120
CAR_IMAGE_FILENAME = "assets/car_image.png"


def filter_all_collisions(entity: VehicleEntity, others: list[PolygonShape] | tuple[PolygonShape, ...]):
    for other in others:
        is_collide, move = collide(entity.points, other.points)

        if is_collide:
            yield other, move


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


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption(SCREEN_TITLE)

    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    dt = 1.0
    running = False

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, CAR_IMAGE_FILENAME)

    car_image = pygame.image.load(image_path)
    car_image = pygame.transform.smoothscale(car_image, (car_image.get_width() // 24, car_image.get_height() // 24))
    car_image_size = car_image.get_rect()

    box0 = SquareShape(80)
    box0.position = (100, 100)

    box1 = SquareShape(120)
    box1.position = (350, 250)
    box1.scale((2, 2))

    entity = VehicleEntity(
        Chassis(
            1.2,
            np.array(car_image.get_rect().size, dtype=np.float32),
            np.array([0, 0], dtype=np.float32),
            15
        ),
        RectangleShape((40, 15)),
        steering=Steering(100, 5 ** 10)
    )

    while not running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = True

        pressed = pygame.key.get_pressed()
        throttle = pressed[pygame.K_w] - pressed[pygame.K_s]
        brake = pressed[pygame.K_SPACE]
        steering = pressed[pygame.K_d] - pressed[pygame.K_a]
        position, angle = entity.process(dt, throttle, brake, steering)

        box1.rotate(0.025 * dt)

        for box, move in filter_all_collisions(entity, (box0, box1)):
            entity, box = push(entity, box, move)

        screen.fill((255, 255, 255))
        car_image_rotate = pygame.transform.rotate(car_image, angle)
        car_image_size = car_image_rotate.get_rect()

        pygame.draw.polygon(screen, (0, 255, 0), entity.points)
        pygame.draw.polygon(screen, (0, 0, 255), box0.points)
        pygame.draw.polygon(screen, (255, 0, 0), box1.points)
        screen.blit(car_image_rotate, position - (car_image_size.width / 2, car_image_size.height / 2))

        pygame.display.update()

        dt = clock.tick(DEFAULT_FRAME_RATE)

    pygame.quit()
