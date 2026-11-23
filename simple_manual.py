import carla
import pygame
import numpy as np
import random

# ==============================
# PYGAME
# ==============================

pygame.init()

WIDTH = 800
HEIGHT = 600

display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CARLA Simple Manual Control")

clock = pygame.time.Clock()


# ==============================
# CONNECT CARLA
# ==============================

print("1. Connecting to CARLA...")

client = carla.Client("127.0.0.1", 2000)
client.set_timeout(10.0)

world = client.get_world()

print("2. Connected:", world.get_map().name)


# ==============================
# SPAWN VEHICLE
# ==============================

bp_library = world.get_blueprint_library()

vehicle_bp = bp_library.find("vehicle.tesla.model3")

spawn_points = world.get_map().get_spawn_points()

vehicle = None

while vehicle is None:
    spawn_point = random.choice(spawn_points)
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)

print("3. Vehicle spawned")


# ==============================
# SPAWN CAMERA
# ==============================

camera_bp = bp_library.find("sensor.camera.rgb")

camera_bp.set_attribute("image_size_x", str(WIDTH))
camera_bp.set_attribute("image_size_y", str(HEIGHT))
camera_bp.set_attribute("fov", "90")

camera_transform = carla.Transform(
    carla.Location(x=-5.5, z=2.8),
    carla.Rotation(pitch=-15)
)

print("4. Spawning camera...")

camera = world.spawn_actor(
    camera_bp,
    camera_transform,
    attach_to=vehicle
)

print("5. Camera spawned")


# ==============================
# CAMERA CALLBACK
# ==============================

surface = None


def process_image(image):

    global surface

    array = np.frombuffer(
        image.raw_data,
        dtype=np.dtype("uint8")
    )

    array = np.reshape(
        array,
        (image.height, image.width, 4)
    )

    array = array[:, :, :3]

    array = array[:, :, ::-1]

    surface = pygame.surfarray.make_surface(
        array.swapaxes(0, 1)
    )


camera.listen(process_image)

print("6. Camera listening")
print("")
print("W = throttle")
print("S = brake")
print("A = left")
print("D = right")
print("ESC = quit")


# ==============================
# MAIN LOOP
# ==============================

running = True

try:

    while running:

        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False


        keys = pygame.key.get_pressed()

        control = carla.VehicleControl()

        if keys[pygame.K_w]:
            control.throttle = 0.6

        if keys[pygame.K_s]:
            control.brake = 1.0

        if keys[pygame.K_a]:
            control.steer = -0.5

        if keys[pygame.K_d]:
            control.steer = 0.5

        vehicle.apply_control(control)


        if surface is not None:

            display.blit(surface, (0, 0))

        pygame.display.flip()


finally:

    print("Cleaning up...")

    camera.stop()
    camera.destroy()
    vehicle.destroy()

    pygame.quit()

    print("Done")