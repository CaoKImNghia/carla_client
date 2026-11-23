import carla
import os
import math
import csv

TARGET_SPEED = 20.0
SIM_TIME = 30
FIXED_DT = 0.05 #fps cua simulation


OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gia_tri_sau_ra.csv")
#kết nối carla
client = carla.Client("127.0.0.1", 2000)
client.set_timeout(10.0)
world = client.get_world()
print("đã kết nối với carla")
print("map:", world.get_map().name)

original_settings = world.get_setting()
vehicle = None

try:
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = FIXED_DT
    world.apply_settings(settings)

# chọn xe
    bp_library = world.get_blueprint_library()
    vehicle_bp = bp_library.find("vehicle.tesla.model3")
    spawn_points = world.get_map().get_spawn_points()

    vehicle = None

      for spawn_point inspawn_points:
        veehicle = world.try_spawn_points_actor(
            vehicle_bp,
            spawn_point
        )
        if vehicle is not None:
            break
     if veehicle is None:
        print("không spwn được xe")
        exit()
physics = vehicle.get_physics_control()

    max_steer_angle = 0.0

    for wheel in physics.wheels:
        max_steer_angle = max(
            max_steer_angle,
            wheel.max_steer_angle
        )

    print("Max steering angle:", max_steer_angle, "deg")

    spectator = world.get_spectator()

    # tạo thư mục output
    