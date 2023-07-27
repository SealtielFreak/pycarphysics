import os

import numpy as np
import pygame

from car_physic import CarPhysic, Chassis

SCREEN_TITLE = "Car demo physic"
SCREEN_SIZE = 640, 480
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

    chassis = Chassis(4, np.array(car_image.get_rect().size, dtype=np.float32), np.array([0, 0], dtype=np.float32), 15)
    car_physic = CarPhysic(chassis)

    ppu = 1

    while not running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = True

        pressed = pygame.key.get_pressed()
        throttle = pressed[pygame.K_w] - pressed[pygame.K_s]
        brake = pressed[pygame.K_SPACE]
        steering = pressed[pygame.K_d] - pressed[pygame.K_a]
        position, angle = car_physic.process(dt, throttle, brake, steering)

        screen.fill((255, 255, 255))

        car_image_rotate = pygame.transform.rotate(car_image, angle)
        car_image_size = car_image_rotate.get_rect()
        screen.blit(car_image_rotate, position - (car_image_size.width / 2, car_image_size.height / 2))

        pygame.display.update()

        dt = clock.tick(DEFAULT_FRAME_RATE)

    pygame.quit()
