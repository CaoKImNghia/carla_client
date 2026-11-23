"""Drive a CARLA vehicle along my_road.xodr at a steady target speed.

Examples:
    python drive_my_road.py
    python drive_my_road.py --host 172.29.240.1 --speed-kmh 12 --turn right
"""

import argparse
import math
from pathlib import Path

import carla


ROUTES = {
    "straight": (1, 2, 3, 30, 4),
    "right": (1, 2, 3, 31, 5),
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="CARLA server host")
    parser.add_argument("--port", type=int, default=2000, help="CARLA server port")
    parser.add_argument(
        "--speed-kmh", type=float, default=12.0,
        help="Target speed in km/h (default: 12)",
    )
    parser.add_argument(
        "--turn", choices=ROUTES, default="straight",
        help="Route at the junction (default: straight)",
    )
    parser.add_argument(
        "--waypoint-step-m", type=float, default=2.0,
        help="Distance between route waypoints in meters",
    )
    args = parser.parse_args()
    if not math.isfinite(args.speed_kmh) or args.speed_kmh <= 0:
        parser.error("--speed-kmh must be a positive finite number")
    if not math.isfinite(args.waypoint_step_m) or args.waypoint_step_m <= 0:
        parser.error("--waypoint-step-m must be a positive finite number")
    return args


def build_route(start, road_ids, step_m):
    """Follow the selected OpenDRIVE road sequence using lane waypoints."""
    route = [start]
    road_index = road_ids.index(start.road_id)
    waypoint = start

    for _ in range(1000):
        candidates = waypoint.next(step_m)
        if not candidates:
            if road_index == len(road_ids) - 1:
                return route
            raise RuntimeError(
                f"Road {waypoint.road_id} ended before route road "
                f"{road_ids[road_index + 1]}"
            )

        next_road_id = road_ids[min(road_index + 1, len(road_ids) - 1)]
        candidates = [
            item for item in candidates
            if item.road_id in (waypoint.road_id, next_road_id)
        ]
        if not candidates:
            raise RuntimeError(
                f"No waypoint follows road {waypoint.road_id}, "
                f"lane {waypoint.lane_id}, along route {road_ids}"
            )

        waypoint = candidates[0]
        if waypoint.road_id == next_road_id and next_road_id != road_ids[road_index]:
            road_index += 1
        route.append(waypoint)

    raise RuntimeError("Route generation exceeded 1000 waypoints")


def speed_mps(vehicle):
    velocity = vehicle.get_velocity()
    return math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)


def clamp(value, lower, upper):
    return max(lower, min(value, upper))


def main():
    args = parse_args()
    xodr_path = Path(__file__).resolve().with_name("my_road.xodr")
    if not xodr_path.is_file():
        raise FileNotFoundError(f"OpenDRIVE map not found: {xodr_path}")

    client = carla.Client(args.host, args.port)
    client.set_timeout(20.0)
    client.generate_opendrive_world(xodr_path.read_text(encoding="utf-8"))
    world = client.get_world()
    carla_map = world.get_map()

    original_settings = world.get_settings()
    vehicle = None
    settings_changed = False
    try:
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)
        settings_changed = True

        road_ids = ROUTES[args.turn]
        start_candidates = sorted(
            (
                waypoint for waypoint in carla_map.generate_waypoints(2.0)
                if waypoint.road_id == road_ids[0]
                and waypoint.lane_id == -1
                and waypoint.s >= 3.0
            ),
            key=lambda waypoint: waypoint.s,
        )
        if not start_candidates:
            raise RuntimeError(
                "Could not find driving lane -1 on road 1 in the generated map"
            )

        blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
        blueprint.set_attribute("role_name", "stable_speed_vehicle")
        start = None
        for waypoint in start_candidates:
            transform = waypoint.transform
            transform.location.z += 0.5
            vehicle = world.try_spawn_actor(blueprint, transform)
            if vehicle is not None:
                start = waypoint
                break
        if vehicle is None or start is None:
            raise RuntimeError("Could not spawn vehicle on road 1, lane -1")

        route = build_route(start, road_ids, args.waypoint_step_m)
        if len(route) < 2:
            raise RuntimeError("Generated route is too short to drive")

        physics = vehicle.get_physics_control()
        max_steer = max(wheel.max_steer_angle for wheel in physics.wheels)
        max_steer_rad = math.radians(max_steer)
        target_speed = args.speed_kmh / 3.6
        speed_integral = 0.0
        progress = 0

        print(f"CARLA map: {carla_map.name}")
        print(f"Route: {' -> '.join(map(str, road_ids))}")
        print(f"Target speed: {args.speed_kmh:.1f} km/h; vehicle id: {vehicle.id}")
        print("Press Ctrl+C to stop.")

        while True:
            world.tick()
            location = vehicle.get_location()

            search_end = min(progress + 12, len(route))
            progress = min(
                range(progress, search_end),
                key=lambda index: location.distance(route[index].transform.location),
            )
            final_location = route[-1].transform.location
            remaining = location.distance(final_location)
            current_speed = speed_mps(vehicle)

            if remaining < 0.8 and current_speed < 0.15:
                break

            target_index = min(progress + 3, len(route) - 1)
            target_location = route[target_index].transform.location
            dx = target_location.x - location.x
            dy = target_location.y - location.y
            yaw = math.radians(vehicle.get_transform().rotation.yaw)
            local_x = math.cos(yaw) * dx + math.sin(yaw) * dy
            local_y = -math.sin(yaw) * dx + math.cos(yaw) * dy
            lookahead = max(math.hypot(local_x, local_y), 1.0)
            alpha = math.atan2(local_y, local_x)
            curvature = 2.0 * math.sin(alpha) / lookahead
            steer = math.atan(2.8 * curvature) / max_steer_rad

            desired_speed = min(target_speed, math.sqrt(2.0 * 1.2 * remaining))
            error = desired_speed - current_speed
            speed_integral = clamp(speed_integral + error * 0.05, -5.0, 5.0)
            throttle = clamp(0.12 * error + 0.015 * speed_integral, 0.0, 0.65)
            brake = clamp(-0.25 * error, 0.0, 0.6)

            control = carla.VehicleControl(
                throttle=throttle,
                brake=brake,
                steer=clamp(steer, -1.0, 1.0),
                hand_brake=False,
                manual_gear_shift=False,
            )
            vehicle.apply_control(control)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        if vehicle is not None and vehicle.is_alive:
            vehicle.destroy()
        if settings_changed:
            world.apply_settings(original_settings)

    print("Route complete; vehicle stopped and removed.")


if __name__ == "__main__":
    main()
