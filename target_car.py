import argparse
import csv
import math
import os
import random

import carla


CAMERA_SMOOTHING_SECONDS = 2.0
TOWN_NAME = "Town03"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run one CARLA test case and save ego/target trajectories."
    )
    parser.add_argument("--run-id", default="manual_run")
    parser.add_argument("--target-speed-kmh", type=float, default=20.0)
    parser.add_argument("--distance-ahead-m", type=float, default=20.0)
    parser.add_argument(
        "--target-speed-diff-pct",
        type=float,
        default=10.0,
        help=(
            "Percentage adjustment to min(ego speed, 4 m/s); "
            "negative increases target speed."
        ),
    )
    parser.add_argument(
        "--weather",
        choices=("ClearNoon", "CloudyNoon", "WetNoon"),
        default="CloudyNoon",
    )
    parser.add_argument("--sim-time-s", type=float, default=30.0)
    parser.add_argument("--tire-friction", type=float, default=2.0)
    parser.add_argument("--fixed-dt-s", type=float, default=0.05)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    positive_values = {
        "--target-speed-kmh": args.target_speed_kmh,
        "--distance-ahead-m": args.distance_ahead_m,
        "--sim-time-s": args.sim_time_s,
        "--tire-friction": args.tire_friction,
        "--fixed-dt-s": args.fixed_dt_s,
    }
    for name, value in positive_values.items():
        if not math.isfinite(value) or value <= 0:
            parser.error(f"{name} must be a finite number greater than 0")
    if not math.isfinite(args.target_speed_diff_pct):
        parser.error("--target-speed-diff-pct must be finite")
    return args


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


def is_straight_segment(waypoint, distance, max_heading_change=5.0):
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
                candidate
                for candidate in adjacent_waypoints
                if not candidate.is_junction
                and candidate.lane_id == current_waypoint.lane_id
            ]
            if not adjacent_waypoints:
                return False

            current_waypoint = min(
                adjacent_waypoints,
                key=lambda candidate: heading_difference(
                    candidate.transform.rotation.yaw, reference_yaw
                ),
            )
            if (
                heading_difference(
                    current_waypoint.transform.rotation.yaw, reference_yaw
                )
                > max_heading_change
            ):
                return False
            travelled += step

    return True


def find_spawn_pair(carla_map, requested_distance):
    spawn_points = carla_map.get_spawn_points()
    if not spawn_points:
        raise RuntimeError("Ban do khong co spawn point de tao xe")

    waypoints = [
        (spawn_point, carla_map.get_waypoint(spawn_point.location))
        for spawn_point in spawn_points
    ]
    candidates = []
    distance_tolerance = 5.0

    for ego_transform, ego_waypoint in waypoints:
        if ego_waypoint is None or not is_straight_segment(
            ego_waypoint, requested_distance
        ):
            continue

        forward = ego_transform.get_forward_vector()
        for target_transform, target_waypoint in waypoints:
            if (
                target_waypoint is None
                or target_waypoint.is_junction
                or ego_waypoint.road_id != target_waypoint.road_id
                or ego_waypoint.lane_id != target_waypoint.lane_id
            ):
                continue

            delta = target_transform.location - ego_transform.location
            distance_ahead = delta.x * forward.x + delta.y * forward.y
            lateral_offset = abs(delta.x * forward.y - delta.y * forward.x)
            target_forward = target_transform.get_forward_vector()
            heading_alignment = (
                forward.x * target_forward.x + forward.y * target_forward.y
            )
            if (
                abs(distance_ahead - requested_distance) <= distance_tolerance
                and lateral_offset <= 1.5
                and heading_alignment >= 0.98
            ):
                candidates.append(
                    (
                        abs(distance_ahead - requested_distance),
                        ego_transform,
                        target_transform,
                    )
                )

    if not candidates:
        raise RuntimeError(
            "Khong tim thay cap spawn point cung lan, cung chieu, tren doan "
            f"duong thang voi khoang cach gan {requested_distance:g} m"
        )

    best_distance_error = min(candidate[0] for candidate in candidates)
    best_candidates = [
        candidate
        for candidate in candidates
        if candidate[0] == best_distance_error
    ]
    _, ego_transform, target_transform = random.choice(best_candidates)
    return ego_transform, target_transform


def set_tire_friction(vehicle, tire_friction):
    physics = vehicle.get_physics_control()
    if not physics.wheels:
        raise RuntimeError(
            f"Xe id={vehicle.id} khong co thong tin banh de chinh tire friction"
        )

    for wheel in physics.wheels:
        wheel.tire_friction = tire_friction
    vehicle.apply_physics_control(physics)


def get_max_steer_angle(vehicle):
    steering_angles = [
        wheel.max_steer_angle
        for wheel in vehicle.get_physics_control().wheels
        if wheel.max_steer_angle > 0.0
    ]
    return max(steering_angles, default=0.0)


def write_vehicle_row(writer, vehicle, name, simulation_time, max_steer_angle):
    transform = vehicle.get_transform()
    velocity = vehicle.get_velocity()
    acceleration = vehicle.get_acceleration()
    control = vehicle.get_control()
    speed = math.sqrt(
        velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2
    )
    writer.writerow(
        [
            simulation_time,
            vehicle.id,
            name,
            transform.location.x,
            transform.location.y,
            speed,
            velocity.x,
            velocity.y,
            acceleration.x,
            acceleration.y,
            control.steer,
            control.steer * max_steer_angle,
            transform.rotation.pitch,
            transform.rotation.roll,
        ]
    )


def main():
    args = parse_arguments()
    target_speed_kmh = args.target_speed_kmh
    ego_speed_mps = target_speed_kmh / 3.6
    target_speed_mps = max(
        0.0,
        min(ego_speed_mps, 4.0)
        * (1.0 - args.target_speed_diff_pct / 100.0),
    )
    ego_output_file = os.path.join(args.output_dir, "data_ego.csv")
    target_output_file = os.path.join(args.output_dir, "target_data.csv")
    weather_presets = {
        "ClearNoon": carla.WeatherParameters.ClearNoon,
        "CloudyNoon": carla.WeatherParameters.CloudyNoon,
        "WetNoon": carla.WeatherParameters.WetNoon,
    }

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)
    world = client.load_world(TOWN_NAME)
    world.set_weather(weather_presets[args.weather])
    original_settings = world.get_settings()

    print("Da ket noi voi CARLA")
    print("Map:", world.get_map().name)
    print(
        f"TestRun {args.run_id}: ego={target_speed_kmh:g} km/h, "
        f"target={target_speed_mps:g} m/s, "
        f"distance={args.distance_ahead_m:g} m, "
        f"weather={args.weather}, tire friction={args.tire_friction:g}"
    )

    vehicles = []
    sensors = []
    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = args.fixed_dt_s
        world.apply_settings(settings)

        ego_transform, target_transform = find_spawn_pair(
            world.get_map(), args.distance_ahead_m
        )
        blueprint_library = world.get_blueprint_library()
        ego_blueprint = blueprint_library.find("vehicle.tesla.model3")
        ego_blueprint.set_attribute("role_name", "ego")
        target_blueprint = blueprint_library.find("vehicle.tesla.model3")
        target_blueprint.set_attribute("role_name", "target")

        ego_car = world.try_spawn_actor(ego_blueprint, ego_transform)
        if ego_car is None:
            raise RuntimeError("Khong spawn duoc ego car tai vi tri da chon")
        vehicles.append(ego_car)

        target_car = world.try_spawn_actor(target_blueprint, target_transform)
        if target_car is None:
            raise RuntimeError(
                "Khong spawn duoc target car; vi tri co the bi vat the chiem"
            )
        vehicles.append(target_car)

        for vehicle in vehicles:
            set_tire_friction(vehicle, args.tire_friction)

        max_steer_angles = {
            ego_car.id: get_max_steer_angle(ego_car),
            target_car.id: get_max_steer_angle(target_car),
        }

        collision_detected = False

        def on_collision(_event):
            nonlocal collision_detected
            collision_detected = True

        collision_blueprint = blueprint_library.find("sensor.other.collision")
        for vehicle in vehicles:
            sensor = world.spawn_actor(
                collision_blueprint,
                carla.Transform(),
                attach_to=vehicle,
            )
            sensors.append(sensor)
            sensor.listen(on_collision)

        os.makedirs(args.output_dir, exist_ok=True)
        header = [
            "time_s", "actor_id", "name", "x_m", "y_m", "v_mps",
            "vx_mps", "vy_mps", "ax_mps2", "ay_mps2", "steer_cmd",
            "steering_angle_deg", "pitch_deg", "roll_deg",
        ]
        spectator = world.get_spectator()
        camera_initialized = False
        total_steps = int(args.sim_time_s / args.fixed_dt_s)
        collision_occurred = False

        with open(ego_output_file, "w", newline="", encoding="utf-8") as ego_csvfile, \
             open(target_output_file, "w", newline="", encoding="utf-8") as target_csvfile:
            ego_writer = csv.writer(ego_csvfile)
            target_writer = csv.writer(target_csvfile)
            ego_writer.writerow(header)
            target_writer.writerow(header)

            for step in range(total_steps):
                ego_forward = ego_car.get_transform().get_forward_vector()
                target_forward = target_car.get_transform().get_forward_vector()
                ego_car.set_target_velocity(
                    carla.Vector3D(
                        x=ego_forward.x * ego_speed_mps,
                        y=ego_forward.y * ego_speed_mps,
                        z=ego_forward.z * ego_speed_mps,
                    )
                )
                target_car.set_target_velocity(
                    carla.Vector3D(
                        x=target_forward.x * target_speed_mps,
                        y=target_forward.y * target_speed_mps,
                        z=target_forward.z * target_speed_mps,
                    )
                )
                world.tick()

                ego_transform = ego_car.get_transform()
                camera_transform = carla.Transform(
                    ego_transform.transform(carla.Location(x=-8.0, z=4.0)),
                    carla.Rotation(
                        pitch=-15.0,
                        yaw=ego_transform.rotation.yaw,
                        roll=0.0,
                    ),
                )
                if not camera_initialized:
                    spectator.set_transform(camera_transform)
                    camera_initialized = True
                else:
                    alpha = 1.0 - math.exp(
                        -args.fixed_dt_s / CAMERA_SMOOTHING_SECONDS
                    )
                    spectator.set_transform(
                        interpolate_transform(
                            spectator.get_transform(), camera_transform, alpha
                        )
                    )

                simulation_time = step * args.fixed_dt_s
                write_vehicle_row(
                    ego_writer,
                    ego_car,
                    "ego",
                    simulation_time,
                    max_steer_angles[ego_car.id],
                )
                write_vehicle_row(
                    target_writer,
                    target_car,
                    "target",
                    simulation_time,
                    max_steer_angles[target_car.id],
                )

                if step % max(1, int(1.0 / args.fixed_dt_s)) == 0:
                    ego_velocity = ego_car.get_velocity()
                    ego_speed = math.sqrt(
                        ego_velocity.x ** 2
                        + ego_velocity.y ** 2
                        + ego_velocity.z ** 2
                    )
                    print(
                        f"t = {simulation_time:.1f} s | "
                        f"ego speed = {ego_speed:.2f} m/s"
                    )

                if collision_detected:
                    collision_occurred = True
                    break

        if collision_occurred:
            print("Da ghi nhan va cham!")
        else:
            print("Het thoi gian mo phong nhung chua ghi nhan va cham")

    finally:
        for sensor in sensors:
            sensor.stop()
            sensor.destroy()
        for vehicle in vehicles:
            if vehicle.is_alive:
                vehicle.destroy()
        world.apply_settings(original_settings)
        print("Cleanup completed")

    print("TestRun completed")
    print("Ego CSV:", ego_output_file)
    print("Target CSV:", target_output_file)


if __name__ == "__main__":
    main()
