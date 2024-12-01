import os

import numpy as np
import pygame

from pycarphysics.collisions import filter_all_collisions, collide
from pycarphysics.collisions.response import push, bounce, slide
from pycarphysics.collisions.shapes import SquareShape, RectangleShape
from pycarphysics.entities import VehicleEntity
from pycarphysics.entities.chassis import Chassis
from pycarphysics.entities.steering import Steering

SCREEN_TITLE = "Demo Pycarphysics"
SCREEN_SIZE = 640, 480
DEFAULT_OFFSET_CAMERA = np.array(SCREEN_SIZE) // 2
DEFAULT_FRAME_RATE = 120
CAR_IMAGE_FILENAME = "assets/car_image.png"


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
    )

    advert = RectangleShape((60, 15))
    advert.position = (50, 15 / 2)
    advert_color = (255, 0, 255)

    camera_translate = np.array([20, 0], dtype=np.float64)

    object_detected = False

    while not running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = True

        last_position = entity.collider.position
        last_angle = entity.collider.angle

        pressed = pygame.key.get_pressed()
        throttle = pressed[pygame.K_w] - pressed[pygame.K_s]
        brake = pressed[pygame.K_SPACE]
        steering = pressed[pygame.K_d] - pressed[pygame.K_a]

        position, angle = entity.process(dt, throttle, brake, steering)

        box1.rotate(0.025 * dt)

        entities = {
            box0: 'obstacle',
            box1: 'wall',
            advert: 'sensor',
        }

        for other, type_col in entities.items():
            is_collide, move = collide(entity.points, other.points)

            if not is_collide:
                continue

            match type_col:
                case 'wall':
                    entity, _ = slide(entity, other, move)
                case 'obstacle':
                    entity, _ = push(entity, other, move)

        advert.translate(entity.collider.position - last_position)
        advert.rotate((entity.collider.angle - advert.angle) * -1, entity.collider.origin)

        object_detected = False
        advert_color = (255, 0, 255)

        for other in (box0, box1):
            is_collide, move = collide(advert.points, other.points)


            if not is_collide:
                continue

            object_detected = is_collide
            advert_color = (0, 255, 255)



        screen.fill((255, 255, 255))
        car_image_rotate = pygame.transform.rotate(car_image, angle)
        car_image_size = car_image_rotate.get_rect()

        camera_translate = -entity.collider.position + DEFAULT_OFFSET_CAMERA

        pygame.draw.polygon(screen, (0, 255, 0), entity.points + camera_translate)
        pygame.draw.polygon(screen, (0, 0, 255), box0.points + camera_translate)
        pygame.draw.polygon(screen, (255, 0, 0), box1.points + camera_translate)
        pygame.draw.polygon(screen, advert_color, advert.points + camera_translate)

        screen.blit(car_image_rotate, (position - (car_image_size.width / 2, car_image_size.height / 2)) + camera_translate)

        pygame.display.update()

        dt = clock.tick(DEFAULT_FRAME_RATE)

    pygame.quit()
