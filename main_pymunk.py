import math
import os

import pygame
import pymunk.pygame_util

SCREEN_TITLE = "Car demo physic and Pymunk"
SCREEN_SIZE = 640, 480
DEFAULT_FRAME_RATE = 120
CAR_IMAGE_FILENAME = "assets/car_image.png"


class VehicleBody2d:
    pass


class VehicleWheel2d:
    pass


def transformed_vertices_poly(vertices: list) -> list:
    height, width = SCREEN_SIZE
    transformed_vertices = []

    for vertex in vertices:
        x, y = vertex.rotated(body.angle) + body.position
        y = height - y
        transformed_vertices.append((x, y))

    return transformed_vertices


def transformed_position(position):
    height, width = SCREEN_SIZE

    x = int(position.x)
    y = int(height - position.y)

    return pymunk.Vec2d(x, y)


def get_lateral_velocity(body):
    current_right_normal = body.rotation_vector.cpvrotate((1, 0))
    return current_right_normal.dot(body.velocity) * current_right_normal


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption(SCREEN_TITLE)

    space = pymunk.Space()
    space.gravity = (0, 0)

    mass = 1
    size = 25, 50
    moment = pymunk.moment_for_box(mass, size)
    body = pymunk.Body(mass, moment)
    body.position = 0, 640

    shape = pymunk.Poly.create_box(body, size)
    space.add(body, shape)

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    clock = pygame.time.Clock()
    running = True
    window_focus = True

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, CAR_IMAGE_FILENAME)

    car_image = pygame.image.load(image_path)
    car_image = pygame.transform.smoothscale(car_image, (car_image.get_width() // 24, car_image.get_height() // 24))
    car_image = pygame.transform.rotate(car_image, 90)
    car_image_size = car_image.get_rect()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.WINDOWFOCUSLOST:
                window_focus = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                window_focus = True

        dt = clock.tick(120) / 1000.0

        if window_focus:
            linear_velocity = body.velocity.length

            damping_force = 0.95
            damping_angular_velocity = 0.95

            max_lateral_impulse = 5

            torque = 0
            angular_velocity = 0

            keys = pygame.key.get_pressed()

            throttle = keys[pygame.K_w] - keys[pygame.K_s]
            brake_hand = keys[pygame.K_SPACE]
            steering = keys[pygame.K_a] - keys[pygame.K_d]

            if throttle != 0:
                if not linear_velocity > 200:
                    pass

                force_value = math.copysign(25000, throttle)
                torque += force_value * dt
            else:
                body.velocity *= damping_force

            if steering != 0 and (abs(linear_velocity) > 25 or brake_hand != 0):
                angular_velocity_value = 0

                if abs(linear_velocity) > 0:
                    angular_velocity_value = math.copysign(1 / linear_velocity, steering) * math.copysign(1, throttle)

                angular_velocity += math.radians(angular_velocity_value) * dt
            else:
                body.angular_velocity *= damping_angular_velocity

            acceleration = torque / body.mass
            force_direction = pymunk.Vec2d(0, torque).rotated(angular_velocity)

            body.angular_velocity += angular_velocity
            body.apply_force_at_local_point(force_direction)

            print(angular_velocity, tuple(force_direction), acceleration, linear_velocity)

            space.step(dt)

            screen.fill((255, 255, 255))

            pygame.draw.polygon(screen, (0, 255, 0), transformed_vertices_poly(shape.get_vertices()))

            car_image_rotate = pygame.transform.rotate(car_image, math.degrees(body.angle))
            car_image_size = car_image_rotate.get_rect()
            screen.blit(car_image_rotate,
                        transformed_position(body.position) - (car_image_size.width / 2, car_image_size.height / 2))

        pygame.display.flip()

    pygame.quit()
