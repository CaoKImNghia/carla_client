import carla
import math
import os
import csv

TARGET_SPEED = 20.0  # km/h
SIM_TIME = 30
FIXED_DT = 0.025
TARGET_SPEED_MPS = TARGET_SPEED / 3.6

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "vehicle_data.csv")
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

#ket noi carla
client = carla.Client("127.0.0.1", 2000)
client.set_timeout(10.0)
world = client.get_world()

#tm client
tm = client.get_trafficmanager(8000)
tm_port = tm.get_port()


world.set_weather(carla.WeatherParameters.CloudyNoon)

print("Connected to CARLA")
print("Map:", world.get_map().name)

original_settings = world.get_settings()

vehicle = None
targets = []
try:

    # ======================================
    # SYNCHRONOUS MODE
    # ======================================

    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = FIXED_DT
    world.apply_settings(settings)
    tm.set_synchronous_mode(True)



    # ======================================
    # SPAWN EGO VEHICLE
    # ======================================

    bp_library = world.get_blueprint_library()

    vehicle_bp = bp_library.find("vehicle.tesla.model3")

    spawn_points = world.get_map().get_spawn_points()

    vehicle = None

    for spawn_point in spawn_points:

        vehicle = world.try_spawn_actor(
            vehicle_bp,
            spawn_point
        )

        if vehicle is not None:
            break

    if vehicle is None:
        raise RuntimeError("Khong spawn duoc ego vehicle")

    print("Ego vehicle:", vehicle.type_id)


    # target configs
    target_config = [
        {
            "name": "target 1",
            "blueprint": "vehicle.audi.tt",
            "distance_ahead": 20.0,
            "speed_diff": 10,
            "lane_change": True
        }
    ]

    #spawn target
    ego_waypoint = world.get_map().get_waypoint(vehicle.get_location())
    if ego_waypoint is None:
        raise RuntimeError("Khong tim duoc lan duong cua ego vehicle")

    for config in target_config:
        bp = bp_library.find(config["blueprint"])
        bp.set_attribute("role_name", config["name"])
        target = None
        # Thu cac vi tri gan nhau neu diem dau tien bi chiem.
        for offset in (0.0, 5.0, -5.0):
            candidates = ego_waypoint.next(config["distance_ahead"] + offset)
            if not candidates:
                continue
            spawn_transform = candidates[0].transform
            spawn_transform.location.z += 0.5
            target = world.try_spawn_actor(bp, spawn_transform)
            if target is not None:
                break
        if target is None:
            raise RuntimeError(
                f"Khong spawn duoc {config['name']} phia truoc ego: "
                "khong co waypoint phu hop hoac vi tri bi chiem"
            )

        targets.append(target)
        distance = target.get_location().distance(vehicle.get_location())
        print(f"Da spawn {config['name']} (id={target.id}), cach ego {distance:.1f} m")

        target.set_autopilot(
            True,
            tm_port
        )

        tm.vehicle_percentage_speed_difference(target, config["speed_diff"])
        tm.auto_lane_change(target, config["lane_change"])

    # ======================================
    # LAY MAX STEERING ANGLE
    # ======================================

    physics = vehicle.get_physics_control()

    max_steer_angle = 0.0

    for wheel in physics.wheels:
        max_steer_angle = max(
            max_steer_angle,
            wheel.max_steer_angle
        )

    print("Max steering angle:", max_steer_angle, "deg")


    # ======================================
    # CAMERA SPECTATOR
    # ======================================

    spectator = world.get_spectator()


    # ======================================
    # TAO THU MUC OUTPUT
    # ======================================

    os.makedirs(OUTPUT_DIR, exist_ok=True)


    # ======================================
    # MO FILE CSV
    # ======================================

    with open(OUTPUT_FILE, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "time_s",
            "x_m",
            "y_m",
            "v_mps",
            "vx_mps",
            "vy_mps",
            "ax_mps2",
            "ay_mps2",
            "steer_cmd",
            "steering_angle_deg",
            "pitch_deg",
            "roll_deg"
        ])


        # ==================================
        # SO BUOC MO PHONG
        # ==================================

        total_steps = int(SIM_TIME / FIXED_DT)

        for step in range(total_steps):

            # ==============================
            # LAY TRANG THAI XE
            # ==============================

            transform = vehicle.get_transform()
            velocity = vehicle.get_velocity()
            acceleration = vehicle.get_acceleration()

            x = transform.location.x
            y = transform.location.y

            vx = velocity.x
            vy = velocity.y
            vz = velocity.z

            ax = acceleration.x
            ay = acceleration.y

            speed = math.sqrt(
                vx * vx +
                vy * vy +
                vz * vz
            )


            # ==============================
            # SPEED CONTROLLER
            # ==============================

            speed_error = TARGET_SPEED_MPS - speed

            throttle = clamp(
                0.30 * speed_error,
                0.0,
                1.0
            )

            brake = 0.0

            if speed_error < 0:
                throttle = 0.0

                brake = clamp(
                    -0.20 * speed_error,
                    0.0,
                    1.0
                )


            # ==============================
            # LANE FOLLOWING DON GIAN
            # ==============================

            waypoint = world.get_map().get_waypoint(
                transform.location,
                project_to_road=True
            )

            next_waypoints = waypoint.next(3.0)

            steer = 0.0

            if len(next_waypoints) > 0:

                target_waypoint = next_waypoints[0]

                target_location = (
                    target_waypoint.transform.location
                )

                dx = target_location.x - transform.location.x
                dy = target_location.y - transform.location.y

                target_yaw = math.atan2(dy, dx)

                vehicle_yaw = math.radians(
                    transform.rotation.yaw
                )

                yaw_error = target_yaw - vehicle_yaw

                yaw_error = math.atan2(
                    math.sin(yaw_error),
                    math.cos(yaw_error)
                )

                steer = clamp(
                    1.5 * yaw_error,
                    -1.0,
                    1.0
                )


            # ==============================
            # GUI LENH DIEU KHIEN
            # ==============================

            control = carla.VehicleControl()

            control.throttle = throttle
            control.brake = brake
            control.steer = steer

            vehicle.apply_control(control)


            # ==============================
            # STEERING ANGLE XAP XI
            # ==============================

            steering_angle = (
                steer * max_steer_angle
            )


            # ==============================
            # PITCH / ROLL
            # ==============================

            pitch = transform.rotation.pitch
            roll = transform.rotation.roll


            # ==============================
            # THOI GIAN MO PHONG
            # ==============================

            simulation_time = step * FIXED_DT


            # ==============================
            # GHI CSV
            # ==============================

            writer.writerow([
                simulation_time,
                x,
                y,
                speed,
                vx,
                vy,
                ax,
                ay,
                steer,
                steering_angle,
                pitch,
                roll
            ])


            # ==============================
            # CAMERA THEO XE
            # ==============================

            forward = transform.get_forward_vector()

            camera_location = (
                transform.location
                - forward * 8.0
                + carla.Location(z=4.0)
            )

            camera_transform = carla.Transform(
                camera_location,
                carla.Rotation(
                    pitch=-15,
                    yaw=transform.rotation.yaw
                )
            )

            spectator.set_transform(
                camera_transform
            )


            # ==============================
            # CHAY 1 SIMULATION STEP
            # ==============================

            world.tick()


            # ==============================
            # PRINT MOI 1 GIAY
            # ==============================

            if step % int(1.0 / FIXED_DT) == 0:

                print(
                    "t = %.1f s | speed = %.2f m/s | "
                    "steer = %.3f"
                    % (
                        simulation_time,
                        speed,
                        steer
                    )
                )


    print("")
    print("TestRun completed")
    print("Output:", OUTPUT_FILE)


finally:

    # ======================================
    # XOA XE
    # ======================================

    try:
        for target in targets:
            target.destroy()

        if vehicle is not None:
            vehicle.destroy()
    finally:
        try:
            tm.set_synchronous_mode(original_settings.synchronous_mode)
        finally:
            world.apply_settings(original_settings)

    print("Cleanup completed")
