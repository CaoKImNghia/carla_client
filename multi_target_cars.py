"""Spawn multiple CARLA target vehicles and save their routes and telemetry."""

import argparse
import csv
import math
import random
import time
from contextlib import ExitStack
from pathlib import Path

import carla


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--town", default="Town03")
    parser.add_argument(
        "--ego-spawn-point",
        type=int,
        help=(
            "Index of the map spawn point for the stationary ego car. "
            "If omitted, choose an index interactively. Run with "
            "--list-spawn-points to see available indices."
        ),
    )
    parser.add_argument(
        "--list-spawn-points",
        action="store_true",
        help="List spawn-point indices and coordinates for the selected town.",
    )
    parser.add_argument(
        "--num-target-cars",
        type=int,
        help="Number of target cars. If omitted, enter the number in the terminal.",
    )
    parser.add_argument(
        "--target-coordinate",
        action="append",
        metavar="X,Y,YAW",
        help=(
            "World coordinates and yaw for a target car. Repeat once per target; "
            "if omitted, enter each target's coordinates in the terminal."
        ),
    )
    parser.add_argument(
        "--vehicle-blueprint",
        action="append",
        help=(
            "CARLA vehicle blueprint ID for a target car. Repeat once per car; "
            "the order matches the cars that are spawned."
        ),
    )
    parser.add_argument(
        "--list-vehicles",
        action="store_true",
        help="List available four-or-more-wheel vehicle blueprint IDs and exit.",
    )
    parser.add_argument("--target-speed-kmh", type=float, default=35.0)
    parser.add_argument("--sim-time-s", type=float, default=30.0)
    parser.add_argument("--fixed-dt-s", type=float, default=0.05)
    parser.add_argument("--route-distance-m", type=float, default=500.0)
    parser.add_argument(
        "--ego-blueprint",
        default="vehicle.tesla.model3",
        help="CARLA vehicle blueprint ID to use for the reference ego car.",
    )
    parser.add_argument(
        "--lane-change-probability",
        type=float,
        default=0.0,
        help=(
            "Probability of planning a lane change at route opportunities. "
            "Defaults to 0 so the target cars stay in their formation lanes."
        ),
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results" / "multi_target_run",
    )
    args = parser.parse_args()

    if args.num_target_cars is None and not (
        args.list_spawn_points or args.list_vehicles
    ):
        while True:
            try:
                args.num_target_cars = int(input("Number of target cars: "))
                break
            except ValueError:
                print("Please enter a whole number.")
            except EOFError:
                parser.error(
                    "provide --num-target-cars when standard input is unavailable"
                )

    if args.num_target_cars is None:
        return args
    if args.num_target_cars < 1:
        parser.error("--num-target-cars must be at least 1")
    if (
        args.target_coordinate is not None
        and len(args.target_coordinate) != args.num_target_cars
    ):
        parser.error(
            "provide --target-coordinate exactly once for each "
            "--num-target-cars value"
        )
    if args.target_coordinate is not None:
        for coordinate in args.target_coordinate:
            try:
                values = [float(value.strip()) for value in coordinate.split(",")]
            except ValueError:
                parser.error(
                    "--target-coordinate must use X,Y,YAW "
                    "(for example 10.5,20.0,90)"
                )
            if len(values) != 3 or not all(math.isfinite(value) for value in values):
                parser.error(
                    "--target-coordinate must contain three finite numbers: X,Y,YAW"
                )
    if (
        args.vehicle_blueprint is not None
        and len(args.vehicle_blueprint) != args.num_target_cars
    ):
        parser.error(
            "provide --vehicle-blueprint exactly once for each "
            "--num-target-cars value"
        )
    for name in (
        "target_speed_kmh",
        "sim_time_s",
        "fixed_dt_s",
        "route_distance_m",
    ):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be a positive finite number")
    if (
        not math.isfinite(args.lane_change_probability)
        or not 0.0 <= args.lane_change_probability <= 100.0
    ):
        parser.error("--lane-change-probability must be between 0 and 100")
    return args


def heading_difference(yaw_a, yaw_b):
    return abs((yaw_a - yaw_b + 180.0) % 360.0 - 180.0)


def choose_continuation(candidates, waypoint):
    same_lane = [
        candidate
        for candidate in candidates
        if candidate.lane_id == waypoint.lane_id
    ]
    if not same_lane:
        return None
    continuation = min(
        same_lane,
        key=lambda candidate: heading_difference(
            candidate.transform.rotation.yaw,
            waypoint.transform.rotation.yaw,
        ),
    )
    return continuation


def build_route(
    carla_map, spawn_transform, distance_m, lane_change_probability, rng
):
    waypoint = carla_map.get_waypoint(
        spawn_transform.location,
        project_to_road=True,
        lane_type=carla.LaneType.Driving,
    )
    if waypoint is None:
        raise RuntimeError("Could not find a driving-lane waypoint for a spawn point")

    route = [waypoint.transform.location]
    lane_change_segments = [False]
    travelled = 0.0
    segment_length = 5.0
    next_lane_change_distance = rng.uniform(40.0, 80.0)

    while travelled < distance_m:
        if (
            lane_change_probability > 0.0
            and travelled >= next_lane_change_distance
            and rng.random() * 100.0 < lane_change_probability
        ):
            directions = [
                candidate
                for candidate in (waypoint.get_left_lane(), waypoint.get_right_lane())
                if candidate is not None
                and candidate.lane_type == carla.LaneType.Driving
                and heading_difference(
                    candidate.transform.rotation.yaw,
                    waypoint.transform.rotation.yaw,
                )
                < 10.0
            ]
            if directions:
                target_waypoint = rng.choice(directions)
                source_waypoint = waypoint
                change_points = []
                for index in range(1, 5):
                    source_next = choose_continuation(
                        source_waypoint.next(segment_length), source_waypoint
                    )
                    target_next = choose_continuation(
                        target_waypoint.next(segment_length), target_waypoint
                    )
                    if source_next is None or target_next is None:
                        change_points = []
                        break
                    alpha = index / 4.0
                    source_location = source_next.transform.location
                    target_location = target_next.transform.location
                    change_points.append(
                        carla.Location(
                            x=source_location.x
                            + (target_location.x - source_location.x) * alpha,
                            y=source_location.y
                            + (target_location.y - source_location.y) * alpha,
                            z=source_location.z
                            + (target_location.z - source_location.z) * alpha,
                        )
                    )
                    source_waypoint = source_next
                    target_waypoint = target_next

                if change_points:
                    route.extend(change_points)
                    lane_change_segments.extend([True] * len(change_points))
                    waypoint = target_waypoint
                    travelled += segment_length * len(change_points)
                    next_lane_change_distance = travelled + rng.uniform(80.0, 140.0)
                    continue
            next_lane_change_distance = travelled + rng.uniform(80.0, 140.0)

        step = min(segment_length, distance_m - travelled)
        next_waypoints = waypoint.next(step)
        next_waypoint = choose_continuation(next_waypoints, waypoint)
        if next_waypoint is None:
            break
        waypoint = next_waypoint
        route.append(waypoint.transform.location)
        lane_change_segments.append(False)
        travelled += step
    return route, lane_change_segments


def get_max_steer_angle(vehicle):
    angles = [
        wheel.max_steer_angle
        for wheel in vehicle.get_physics_control().wheels
        if wheel.max_steer_angle > 0.0
    ]
    return max(angles, default=0.0)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def target_spawn_transform(carla_map, x, y, yaw):
    waypoint = carla_map.get_waypoint(
        carla.Location(x=x, y=y, z=0.0),
        project_to_road=True,
        lane_type=carla.LaneType.Driving,
    )
    if waypoint is None:
        raise ValueError(f"No driving lane found near x={x:g}, y={y:g}")

    road_transform = waypoint.transform
    return carla.Transform(
        carla.Location(
            x=road_transform.location.x,
            y=road_transform.location.y,
            z=road_transform.location.z + 0.5,
        ),
        carla.Rotation(
            pitch=road_transform.rotation.pitch,
            yaw=yaw,
            roll=road_transform.rotation.roll,
        ),
    )


def select_target_transforms(carla_map, num_target_cars):
    selected = []
    while len(selected) < num_target_cars:
        target_number = len(selected) + 1
        try:
            coordinate = input(
                f"Coordinates for target {target_number} (x,y,yaw): "
            )
        except EOFError as error:
            raise RuntimeError(
                "Input ended before coordinates were provided for all targets"
            ) from error

        try:
            values = [float(value.strip()) for value in coordinate.split(",")]
            if len(values) != 3 or not all(
                math.isfinite(value) for value in values
            ):
                raise ValueError("Enter three finite numbers: x,y,yaw")
            x, y, yaw = values
            transform = target_spawn_transform(carla_map, x, y, yaw)
        except ValueError as error:
            print(f"Invalid target coordinates: {error}")
            continue

        selected.append(transform)
        print(
            f"Target {target_number} road-snapped spawn: "
            f"x={transform.location.x:.2f}, y={transform.location.y:.2f}, "
            f"z={transform.location.z:.2f}, yaw={transform.rotation.yaw:.2f} "
            "(yaw in degrees)"
        )
    return selected


def select_ego_spawn_point(spawn_points):
    while True:
        try:
            spawn_index = int(input("Ego spawn-point index: "))
        except ValueError:
            print("Please enter a whole-number spawn-point index.")
            continue
        except EOFError as error:
            raise RuntimeError(
                "No ego spawn point provided; use --ego-spawn-point when "
                "standard input is unavailable"
            ) from error

        if not 0 <= spawn_index < len(spawn_points):
            print(f"Choose an index between 0 and {len(spawn_points) - 1}.")
            continue

        transform = spawn_points[spawn_index]
        location = transform.location
        print(
            f"Selected ego spawn point {spawn_index}: "
            f"x={location.x:.2f}, y={location.y:.2f}, z={location.z:.2f}, "
            f"yaw={transform.rotation.yaw:.2f}"
        )
        return spawn_index


def main():
    args = parse_args()
    rng = random.Random(args.seed)

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)
    world = client.load_world(args.town)
    carla_map = world.get_map()
    original_settings = world.get_settings()
    blueprint_library = world.get_blueprint_library()
    vehicle_blueprints = [
        blueprint
        for blueprint in blueprint_library.filter("vehicle.*")
        if not blueprint.has_attribute("number_of_wheels")
        or blueprint.get_attribute("number_of_wheels").as_int() >= 4
    ]
    if not vehicle_blueprints:
        raise RuntimeError("CARLA has no vehicle blueprints to spawn")
    spawn_points = list(carla_map.get_spawn_points())
    if args.list_spawn_points:
        for index, transform in enumerate(spawn_points):
            location = transform.location
            print(
                f"{index}: x={location.x:.2f}, y={location.y:.2f}, "
                f"z={location.z:.2f}, yaw={transform.rotation.yaw:.2f}"
            )
        return
    if args.list_vehicles:
        for blueprint in sorted(vehicle_blueprints, key=lambda item: item.id):
            print(blueprint.id)
        return
    if args.ego_spawn_point is None:
        args.ego_spawn_point = select_ego_spawn_point(spawn_points)
    if not 0 <= args.ego_spawn_point < len(spawn_points):
        raise ValueError(
            f"--ego-spawn-point must be between 0 and {len(spawn_points) - 1} "
            f"for {args.town}"
        )
    if args.num_target_cars is None:
        raise ValueError("A target-car count is required")
    if args.target_coordinate is None:
        target_transforms = select_target_transforms(
            carla_map, args.num_target_cars
        )
    else:
        target_transforms = []
        for coordinate in args.target_coordinate:
            x, y, yaw = (float(value.strip()) for value in coordinate.split(","))
            target_transforms.append(
                target_spawn_transform(carla_map, x, y, yaw)
            )

    blueprints_by_id = {blueprint.id: blueprint for blueprint in vehicle_blueprints}
    if args.ego_blueprint not in blueprints_by_id:
        raise ValueError(
            f"Unknown or unsupported ego blueprint ID: {args.ego_blueprint}. "
            "Run with --list-vehicles to see valid IDs."
        )
    if args.vehicle_blueprint is not None:
        unknown_blueprints = [
            blueprint_id
            for blueprint_id in args.vehicle_blueprint
            if blueprint_id not in blueprints_by_id
        ]
        if unknown_blueprints:
            raise ValueError(
                "Unknown or unsupported vehicle blueprint ID(s): "
                + ", ".join(unknown_blueprints)
                + ". Run with --list-vehicles to see valid IDs."
            )

    vehicles = []
    records = []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = args.fixed_dt_s
        world.apply_settings(settings)

        indexed_spawn_points = list(enumerate(spawn_points))
        spawn_candidates = [
            indexed_spawn_points[args.ego_spawn_point]
        ]
        for spawn_index, spawn_transform in spawn_candidates:
            print(
                f"Ego map spawn point {spawn_index}: "
                f"x={spawn_transform.location.x:.2f}, "
                f"y={spawn_transform.location.y:.2f}, "
                f"z={spawn_transform.location.z:.2f}, "
                f"yaw={spawn_transform.rotation.yaw:.2f}"
            )
            group_vehicles = []
            group_records = []
            ego_blueprint = blueprint_library.find(args.ego_blueprint)
            ego_blueprint.set_attribute("role_name", "ego")
            ego_vehicle = world.try_spawn_actor(ego_blueprint, spawn_transform)
            if ego_vehicle is None:
                continue
            ego_vehicle.apply_control(
                carla.VehicleControl(
                    throttle=0.0,
                    brake=1.0,
                    hand_brake=True,
                )
            )
            world.tick()
            group_vehicles.append(ego_vehicle)
            vehicles.append(ego_vehicle)
            ego_transform = ego_vehicle.get_transform()
            print(
                f"Ego spawned at map spawn point {spawn_index}: "
                f"x={ego_transform.location.x:.2f}, "
                f"y={ego_transform.location.y:.2f}, "
                f"z={ego_transform.location.z:.2f}, "
                f"yaw={ego_transform.rotation.yaw:.2f}"
            )

            ego_route, ego_lane_changes = build_route(
                carla_map,
                ego_vehicle.get_transform(),
                args.route_distance_m,
                0.0,
                rng,
            )
            group_records.append(
                {
                    "vehicle": ego_vehicle,
                    "target_id": "ego",
                    "vehicle_type": args.ego_blueprint,
                    "spawn_x_m": ego_transform.location.x,
                    "spawn_y_m": ego_transform.location.y,
                    "spawn_yaw_deg": ego_transform.rotation.yaw,
                    "route_id": "route_ego",
                    "route": ego_route,
                    "lane_change_segments": ego_lane_changes,
                    "max_steer_angle": get_max_steer_angle(ego_vehicle),
                    "target_speed_kmh": 0.0,
                    "last_waypoint": None,
                    "route_index": 0,
                }
            )

            for target_index, target_transform in enumerate(target_transforms):
                if args.vehicle_blueprint is None:
                    blueprint_id = rng.choice(vehicle_blueprints).id
                else:
                    blueprint_id = args.vehicle_blueprint[target_index]
                vehicle_blueprint = blueprint_library.find(blueprint_id)
                vehicle_blueprint.set_attribute(
                    "role_name", f"target_{target_index + 1:02d}"
                )
                if vehicle_blueprint.has_attribute("color"):
                    colors = (
                        vehicle_blueprint.get_attribute("color").recommended_values
                    )
                    if colors:
                        vehicle_blueprint.set_attribute(
                            "color", rng.choice(colors)
                        )

                vehicle = world.try_spawn_actor(
                    vehicle_blueprint, target_transform
                )
                if vehicle is None:
                    print(
                        f"Cannot spawn target_{target_index + 1:02d} at "
                        f"x={target_transform.location.x:.2f}, "
                        f"y={target_transform.location.y:.2f}, "
                        f"yaw={target_transform.rotation.yaw:.2f}. "
                        "Yaw is in degrees; the location may be occupied or "
                        "otherwise not spawnable."
                    )
                    break
                group_vehicles.append(vehicle)
                vehicles.append(vehicle)
                actual_transform = vehicle.get_transform()
                print(
                    f"Target {target_index + 1} spawned at "
                    f"x={actual_transform.location.x:.2f}, "
                    f"y={actual_transform.location.y:.2f}, "
                    f"z={actual_transform.location.z:.2f}, "
                    f"yaw={actual_transform.rotation.yaw:.2f}"
                )
                route, lane_changes = build_route(
                    carla_map,
                    target_transform,
                    args.route_distance_m,
                    args.lane_change_probability,
                    rng,
                )
                group_records.append(
                    {
                        "vehicle": vehicle,
                        "target_id": f"target_{target_index + 1:02d}",
                        "vehicle_type": blueprint_id,
                        "spawn_x_m": actual_transform.location.x,
                        "spawn_y_m": actual_transform.location.y,
                        "spawn_yaw_deg": actual_transform.rotation.yaw,
                        "route_id": f"route_target_{target_index + 1:02d}",
                        "route": route,
                        "lane_change_segments": lane_changes,
                        "max_steer_angle": get_max_steer_angle(vehicle),
                        "target_speed_kmh": args.target_speed_kmh,
                        "last_waypoint": None,
                        "route_index": 0,
                    }
                )

            if len(group_records) != args.num_target_cars + 1:
                for vehicle in group_vehicles:
                    vehicle.destroy()
                    vehicles.remove(vehicle)
                continue

            records.extend(group_records)
            print(
                f"Spawned ego at map spawn point {spawn_index} and "
                f"{args.num_target_cars} target cars at the specified "
                "coordinates."
            )
            break

        if len(vehicles) != args.num_target_cars + 1:
            raise RuntimeError(
                "Could not spawn the ego and all target cars at the configured "
                "coordinates"
            )

        spectator = world.get_spectator()
        followed_vehicle = records[0]["vehicle"]
        telemetry_fields = [
            "time_s",
            "wall_time_s",
            "actor_id",
            "target_id",
            "vehicle_type",
            "spawn_x_m",
            "spawn_y_m",
            "spawn_yaw_deg",
            "route_id",
            "x_m",
            "y_m",
            "z_m",
            "v_mps",
            "vx_mps",
            "vy_mps",
            "ax_mps2",
            "ay_mps2",
            "direction_yaw_deg",
            "steering_angle_deg",
            "pitch_deg",
            "roll_deg",
            "lane_change_enabled",
            "lane_change_probability_pct",
            "lane_change_detected",
            "road_id",
            "lane_id",
            "target_speed_kmh",
        ]
        route_fields = [
            "target_id",
            "route_id",
            "waypoint_index",
            "x_m",
            "y_m",
            "z_m",
            "lane_change_segment",
        ]
        with ExitStack() as output_files:
            for record in records:
                telemetry_path = args.output_dir / f"{record['target_id']}.csv"
                routes_path = args.output_dir / f"{record['target_id']}_route.csv"
                telemetry_file = output_files.enter_context(
                    telemetry_path.open("w", newline="", encoding="utf-8")
                )
                routes_file = output_files.enter_context(
                    routes_path.open("w", newline="", encoding="utf-8")
                )
                record["telemetry_writer"] = csv.DictWriter(
                    telemetry_file, fieldnames=telemetry_fields
                )
                record["telemetry_writer"].writeheader()
                routes_writer = csv.DictWriter(
                    routes_file, fieldnames=route_fields
                )
                routes_writer.writeheader()

                for index, location in enumerate(record["route"]):
                    routes_writer.writerow(
                        {
                            "target_id": record["target_id"],
                            "route_id": record["route_id"],
                            "waypoint_index": index,
                            "x_m": location.x,
                            "y_m": location.y,
                            "z_m": location.z,
                            "lane_change_segment": record[
                                "lane_change_segments"
                            ][index],
                        }
                    )

            total_steps = max(1, int(args.sim_time_s / args.fixed_dt_s))
            wall_start = time.monotonic()
            simulation_start = (
                world.get_snapshot().timestamp.elapsed_seconds
            )
            for step in range(total_steps):
                for record in records:
                    vehicle = record["vehicle"]
                    if record["target_id"] == "ego":
                        vehicle.apply_control(
                            carla.VehicleControl(
                                throttle=0.0,
                                brake=1.0,
                                hand_brake=True,
                            )
                        )
                        continue

                    transform = vehicle.get_transform()
                    route = record["route"]
                    route_index = record["route_index"]
                    while route_index < len(route) - 1:
                        location = route[route_index]
                        distance = math.sqrt(
                            (location.x - transform.location.x) ** 2
                            + (location.y - transform.location.y) ** 2
                        )
                        if distance > 3.0:
                            break
                        route_index += 1
                    record["route_index"] = route_index
                    target_location = route[min(route_index + 1, len(route) - 1)]
                    dx = target_location.x - transform.location.x
                    dy = target_location.y - transform.location.y
                    velocity = vehicle.get_velocity()
                    speed = math.sqrt(
                        velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2
                    )
                    destination_reached = (
                        route_index == len(route) - 1
                        and math.hypot(dx, dy) <= 3.0
                    )
                    if destination_reached:
                        steer = 0.0
                        throttle = 0.0
                        brake = 1.0
                    else:
                        target_yaw = math.atan2(dy, dx)
                        vehicle_yaw = math.radians(transform.rotation.yaw)
                        yaw_error = math.atan2(
                            math.sin(target_yaw - vehicle_yaw),
                            math.cos(target_yaw - vehicle_yaw),
                        )
                        steer = clamp(1.5 * yaw_error, -1.0, 1.0)
                        speed_error = record["target_speed_kmh"] / 3.6 - speed
                        throttle = clamp(0.30 * speed_error, 0.0, 1.0)
                        brake = clamp(-0.20 * speed_error, 0.0, 1.0)
                        if speed_error >= 0.0:
                            brake = 0.0
                        else:
                            throttle = 0.0
                    vehicle.apply_control(
                        carla.VehicleControl(
                            throttle=throttle,
                            brake=brake,
                            steer=steer,
                        )
                    )
                world.tick()
                snapshot = world.get_snapshot()
                simulation_time = (
                    snapshot.timestamp.elapsed_seconds - simulation_start
                )
                wall_time = time.monotonic() - wall_start
                followed_transform = followed_vehicle.get_transform()
                forward = followed_transform.get_forward_vector()
                camera_location = (
                    followed_transform.location
                    - forward * 12.0
                    + carla.Location(z=8.0)
                )
                spectator.set_transform(
                    carla.Transform(
                        camera_location,
                        carla.Rotation(
                            pitch=-25.0,
                            yaw=followed_transform.rotation.yaw,
                        ),
                    )
                )
                for record in records:
                    vehicle = record["vehicle"]
                    transform = vehicle.get_transform()
                    velocity = vehicle.get_velocity()
                    acceleration = vehicle.get_acceleration()
                    control = vehicle.get_control()
                    waypoint = carla_map.get_waypoint(
                        transform.location,
                        project_to_road=True,
                        lane_type=carla.LaneType.Driving,
                    )
                    previous_waypoint = record["last_waypoint"]
                    lane_change_detected = (
                        waypoint is not None
                        and previous_waypoint is not None
                        and not waypoint.is_junction
                        and not previous_waypoint.is_junction
                        and waypoint.road_id == previous_waypoint.road_id
                        and waypoint.lane_id != previous_waypoint.lane_id
                    )
                    record["last_waypoint"] = waypoint
                    speed = math.sqrt(
                        velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2
                    )
                    record["telemetry_writer"].writerow(
                        {
                            "time_s": simulation_time,
                            "wall_time_s": wall_time,
                            "actor_id": vehicle.id,
                            "target_id": record["target_id"],
                            "vehicle_type": record["vehicle_type"],
                            "spawn_x_m": record["spawn_x_m"],
                            "spawn_y_m": record["spawn_y_m"],
                            "spawn_yaw_deg": record["spawn_yaw_deg"],
                            "route_id": record["route_id"],
                            "x_m": transform.location.x,
                            "y_m": transform.location.y,
                            "z_m": transform.location.z,
                            "v_mps": speed,
                            "vx_mps": velocity.x,
                            "vy_mps": velocity.y,
                            "ax_mps2": acceleration.x,
                            "ay_mps2": acceleration.y,
                            "direction_yaw_deg": transform.rotation.yaw,
                            "steering_angle_deg": (
                                control.steer * record["max_steer_angle"]
                            ),
                            "pitch_deg": transform.rotation.pitch,
                            "roll_deg": transform.rotation.roll,
                            "lane_change_enabled": any(
                                record["lane_change_segments"]
                            ),
                            "lane_change_probability_pct": (
                                args.lane_change_probability
                            ),
                            "lane_change_detected": lane_change_detected,
                            "road_id": waypoint.road_id if waypoint else "",
                            "lane_id": waypoint.lane_id if waypoint else "",
                            "target_speed_kmh": record["target_speed_kmh"],
                        }
                    )

                if step % max(1, int(1.0 / args.fixed_dt_s)) == 0:
                    print(
                        f"t={simulation_time:.1f}s | "
                        f"recorded {len(records)} target cars"
                    )
            print(
                f"Finished {simulation_time:.2f} simulation seconds in "
                f"{wall_time:.2f} wall-clock seconds"
            )
    finally:
        for vehicle in vehicles:
            if vehicle.is_alive:
                vehicle.destroy()
        world.apply_settings(original_settings)
        print("Cleanup completed")

    print("Target-car CSV files:", args.output_dir)


if __name__ == "__main__":
    main()
