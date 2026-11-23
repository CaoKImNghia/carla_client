import csv
import math
import random
import threading
import time

import carla


# Chinh thoi tiet tai day (gia tri tu 0 den 100, tru goc mat troi).
WEATHER = carla.WeatherParameters(
    cloudiness=0.0,
    precipitation=0.0,
    precipitation_deposits=0.0,
    wind_intensity=0.0,
    fog_density=0.0,
    wetness=0.0,
    sun_altitude_angle=70.0,
)

# He so bam lop; giam gia tri de xe de truot hon.
TIRE_FRICTION = 0.95
CAMERA_SMOOTHING_SECONDS = 2.0
TELEMETRY_CSV = "vehicle_telemetry.csv"
TOWN_NAME = "Town03"


def heading_difference(yaw_a, yaw_b):
    return abs((yaw_a - yaw_b + 180.0) % 360.0 - 180.0)


def interpolate_angle(start, end, alpha):
    difference = (end - start + 180.0) % 360.0 - 180.0
    return start + difference * alpha


def interpolate_transform(current, target, alpha):
    return carla.Transform(
        carla.Location(
            x=current.location.x
            + (target.location.x - current.location.x) * alpha,
            y=current.location.y
            + (target.location.y - current.location.y) * alpha,
            z=current.location.z
            + (target.location.z - current.location.z) * alpha,
        ),
        carla.Rotation(
            pitch=current.rotation.pitch
            + (target.rotation.pitch - current.rotation.pitch) * alpha,
            yaw=interpolate_angle(
                current.rotation.yaw, target.rotation.yaw, alpha
            ),
            roll=interpolate_angle(
                current.rotation.roll, target.rotation.roll, alpha
            ),
        ),
    )


def set_vehicle_physics(vehicle, tire_friction, world):
    physics = vehicle.get_physics_control()
    if not physics.wheels:
        raise RuntimeError("Xe khong co thong tin banh de chinh tire friction")

    new_wheels = []
    for wheel in physics.wheels:
        wheel.tire_friction = float(tire_friction)
        new_wheels.append(wheel)

    physics.wheels = new_wheels
    vehicle.apply_physics_control(physics)

    if world.get_settings().synchronous_mode:
        world.tick()
    else:
        world.wait_for_tick()

    check_physics = vehicle.get_physics_control()
    print(
        f"Da dat tire_friction cho xe id={vehicle.id}: "
        f"{[wheel.tire_friction for wheel in check_physics.wheels]}"
    )


def get_max_steering_angle(vehicle):
    steering_angles = [
        wheel.max_steer_angle
        for wheel in vehicle.get_physics_control().wheels
        if wheel.max_steer_angle > 0.0
    ]
    return max(steering_angles, default=0.0)


def write_vehicle_telemetry(writer, vehicle, label, elapsed_time, max_steering_angle):
    transform = vehicle.get_transform()
    velocity = vehicle.get_velocity()
    acceleration = vehicle.get_acceleration()
    yaw = math.radians(transform.rotation.yaw)
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    control = vehicle.get_control()

    writer.writerow(
        {
            "elapsed_time_s": f"{elapsed_time:.3f}",
            "vehicle": label,
            "vehicle_id": vehicle.id,
            "vx_mps": velocity.x * cos_yaw + velocity.y * sin_yaw,
            "vy_mps": -velocity.x * sin_yaw + velocity.y * cos_yaw,
            "ax_mps2": acceleration.x * cos_yaw + acceleration.y * sin_yaw,
            "ay_mps2": -acceleration.x * sin_yaw + acceleration.y * cos_yaw,
            "steering_angle_deg": control.steer * max_steering_angle,
            "roll_angle_deg": transform.rotation.roll,
        }
    )


def is_straight_segment(waypoint, distance=40.0, max_heading_change=5.0):
    if waypoint is None or waypoint.is_junction:
        return False

    reference_yaw = waypoint.transform.rotation.yaw
    for forward, segment_distance in ((True, distance), (False, 20.0)):
        current_waypoint = waypoint
        travelled = 0.0

        while travelled < segment_distance:
            step = min(2.0, segment_distance - travelled)
            adjacent_waypoints = (
                current_waypoint.next(step)
                if forward
                else current_waypoint.previous(step)
            )
            adjacent_waypoints = [
                adjacent_waypoint
                for adjacent_waypoint in adjacent_waypoints
                if not adjacent_waypoint.is_junction
                and adjacent_waypoint.lane_id == current_waypoint.lane_id
            ]
            if not adjacent_waypoints:
                return False

            current_waypoint = min(
                adjacent_waypoints,
                key=lambda adjacent_waypoint: heading_difference(
                    adjacent_waypoint.transform.rotation.yaw,
                    reference_yaw,
                ),
            )
            if (
                heading_difference(
                    current_waypoint.transform.rotation.yaw,
                    reference_yaw,
                )
                > max_heading_change
            ):
                return False
            travelled += step

    return True


def get_lane_change_directions(waypoint):
    directions = []
    for adjacent_waypoint, change_left in (
        (waypoint.get_left_lane(), True),
        (waypoint.get_right_lane(), False),
    ):
        if (
            adjacent_waypoint is not None
            and adjacent_waypoint.lane_type == carla.LaneType.Driving
            and heading_difference(
                adjacent_waypoint.transform.rotation.yaw,
                waypoint.transform.rotation.yaw,
            )
            < 10.0
        ):
            directions.append(change_left)
    return directions


def main():
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)

    world = client.load_world(TOWN_NAME)
    world.set_weather(WEATHER)
    traffic_manager = client.get_trafficmanager(8000)

    print("Da ket noi CARLA")
    print("Map:", world.get_map().name)

    spawn_points = world.get_map().get_spawn_points()
    if not spawn_points:
        raise RuntimeError("Ban do khong co spawn point de tao xe")

    carla_map = world.get_map()
    waypoints = [
        (spawn_point, carla_map.get_waypoint(spawn_point.location))
        for spawn_point in spawn_points
    ]
    candidates = []
    for ego_transform, ego_waypoint in waypoints:
        if ego_waypoint is None:
            continue
        if not is_straight_segment(ego_waypoint):
            continue
        lane_change_directions = get_lane_change_directions(ego_waypoint)
        if not lane_change_directions:
            continue
        forward = ego_transform.get_forward_vector()
        for target_transform, target_waypoint in waypoints:
            if target_waypoint is None:
                continue
            if (
             
                ego_waypoint.lane_id != target_waypoint.lane_id
            ):
                continue
            if target_waypoint.is_junction:
                continue

            delta = target_transform.location - ego_transform.location
            distance_ahead = delta.x * forward.x + delta.y * forward.y
            lateral_offset = abs(delta.x * forward.y - delta.y * forward.x)
            heading_alignment = (
                forward.x * target_transform.get_forward_vector().x
                + forward.y * target_transform.get_forward_vector().y
            )
            if (
                15.0 <= distance_ahead <= 25.0
                and lateral_offset <= 1.5
                and heading_alignment >= 0.98
            ):
                candidates.append(
                    (ego_transform, target_transform, lane_change_directions)
                )

    if not candidates:
        raise RuntimeError(
            "Khong tim thay cap spawn point cung lan, cung chieu, cach nhau "
            "15-25 m tren duong thang co lan ben canh cung chieu"
        )

    ego_transform, target_transform, lane_change_directions = random.choice(
        candidates
    )
    change_left = random.choice(lane_change_directions)
    forward = ego_transform.get_forward_vector()

    blueprint_library = world.get_blueprint_library()
    vehicle_blueprint = blueprint_library.find("vehicle.tesla.model3")
    vehicles = []
    sensors = []
    collision_detected = threading.Event()
    telemetry_file = None

    try:
        ego_car = world.try_spawn_actor(vehicle_blueprint, ego_transform)
        if ego_car is None:
            raise RuntimeError("Khong spawn duoc ego car tai vi tri da chon")
        vehicles.append(ego_car)

        target_car = world.try_spawn_actor(vehicle_blueprint, target_transform)
        if target_car is None:
            raise RuntimeError(
                "Khong spawn duoc target car; vi tri co the bi vat the chiem"
            )
        vehicles.append(target_car)

        for vehicle in vehicles:
            set_vehicle_physics(vehicle, TIRE_FRICTION, world)

        telemetry_file = open(TELEMETRY_CSV, "w", newline="", encoding="utf-8")
        telemetry_columns = (
            "elapsed_time_s",
            "vehicle",
            "vehicle_id",
            "vx_mps",
            "vy_mps",
            "ax_mps2",
            "ay_mps2",
            "steering_angle_deg",
            "roll_angle_deg",
        )
        telemetry_writer = csv.DictWriter(
            telemetry_file,
            fieldnames=telemetry_columns,
        )
        telemetry_writer.writeheader()
        max_steering_angles = {
            ego_car.id: get_max_steering_angle(ego_car),
            target_car.id: get_max_steering_angle(target_car),
        }

        target_car.set_autopilot(True, traffic_manager.get_port())
        target_speed = 4.0
        target_speed_limit = target_car.get_speed_limit() / 3.6
        if target_speed_limit <= 0.0:
            raise RuntimeError(
                "Khong lay duoc toc do gioi han cua lan duong cho target car"
            )
        traffic_manager.vehicle_percentage_speed_difference(
            target_car,
            100.0 * (target_speed_limit - target_speed) / target_speed_limit,
        )
        traffic_manager.force_lane_change(target_car, change_left)

        collision_blueprint = blueprint_library.find("sensor.other.collision")
        for vehicle in vehicles:
            sensor = world.spawn_actor(
                collision_blueprint,
                carla.Transform(),
                attach_to=vehicle,
            )
            sensors.append(sensor)
            sensor.listen(lambda event: collision_detected.set())

        lane_change_side = "trai" if change_left else "phai"
        print(
            "Da spawn ego car phia sau target car, cung chieu; "
            f"target dang chuyen sang lan ben {lane_change_side}"
        )

        spectator = world.get_spectator()

        ego_speed = 10.0
        print(
            "Ego car dang duoi target car: "
            f"ego={ego_speed} m/s, target={target_speed} m/s"
        )
        timeout = time.monotonic() + 15.0
        telemetry_start_time = time.monotonic()
        previous_camera_update = time.monotonic()
        camera_initialized = False
        while time.monotonic() < timeout:
            if collision_detected.is_set():
                break
            ego_transform = ego_car.get_transform()
            target_camera_transform = carla.Transform(
                ego_transform.transform(carla.Location(x=8.0, z=4.0)),
                carla.Rotation(
                    pitch=-15.0,
                    yaw=ego_transform.rotation.yaw,
                    roll=0.0,
                ),
            )
            camera_update_time = time.monotonic()
            if not camera_initialized:
                spectator.set_transform(target_camera_transform)
                camera_initialized = True
            else:
                elapsed_camera_time = camera_update_time - previous_camera_update
                alpha = 1.0 - math.exp(
                    -elapsed_camera_time / CAMERA_SMOOTHING_SECONDS
                )
                spectator.set_transform(
                    interpolate_transform(
                        spectator.get_transform(),
                        target_camera_transform,
                        alpha,
                    )
                )
            previous_camera_update = camera_update_time
            ego_car.set_target_velocity(
                carla.Vector3D(
                    x=forward.x * ego_speed,
                    y=forward.y * ego_speed,
                    z=forward.z * ego_speed,
                )
            )
            elapsed_time = time.monotonic() - telemetry_start_time
            write_vehicle_telemetry(
                telemetry_writer,
                ego_car,
                "ego",
                elapsed_time,
                max_steering_angles[ego_car.id],
            )
            write_vehicle_telemetry(
                telemetry_writer,
                target_car,
                "target",
                elapsed_time,
                max_steering_angles[target_car.id],
            )
            telemetry_file.flush()
            collision_detected.wait(timeout=0.05)

        if collision_detected.is_set():
            print("Da ghi nhan va cham!")
        else:
            print("Het thoi gian cho nhung chua ghi nhan va cham")

        time.sleep(2.0)
    finally:
        if telemetry_file is not None:
            telemetry_file.close()
        for sensor in sensors:
            sensor.stop()
            sensor.destroy()
        for vehicle in vehicles:
            vehicle.destroy()
        print("Da don dep cac actor")


if __name__ == "__main__":
    main()
