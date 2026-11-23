
"""Run a configurable CARLA test with one ego vehicle and save its telemetry."""

import argparse
import csv
import math
from pathlib import Path

import carla


FIXED_DT = 0.025
TARGET_SPEED_KMH = 30.0
SPEED_KP = 0.35
SPEED_KI = 0.08
BRAKE_KP = 0.5
SPEED_INTEGRAL_LIMIT = 5.0
SPEED_TOLERANCE_MPS = 0.3

MAP_PATH = Path(__file__).resolve().with_name("my_road.xodr")
START_LOCATION = carla.Location(x=10.0, y=1.75, z=0.0)

# các tham số thời tiết
WEATHER = carla.WeatherParameters(
    cloudiness=80.0,
    precipitation=0.0,
    precipitation_deposits=0.0,
    wind_intensity=0.0,
    fog_density=0.0,
    wetness=0.0,
    sun_altitude_angle=70.0,
)
WEATHER_CHANGE_AT_S = 15.0
WEATHER_AFTER = carla.WeatherParameters(
    cloudiness=80.0,
    precipitation=60.0,
    precipitation_deposits=60.0,
    wind_intensity=30.0,
    fog_density=0.0,
    wetness=80.0,
    sun_altitude_angle=70.0,
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="testrun_example")
    parser.add_argument(
        "--sim-time-s",
        type=float,
        default=50.0,
        help="Simulation duration in seconds.",
    )
    parser.add_argument("--tire-friction", type=float, default=0.9)
    parser.add_argument(
        "--road-friction",
        type=float,
        default=1.0,
        help="Road friction coefficient applied by a CARLA friction trigger.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results" / "testrun_example",
        help="Directory for data_ego.csv.",
    )
    args = parser.parse_args()
    for name in ("sim_time_s", "tire_friction"):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(
                f"--{name.replace('_', '-')} must be a positive finite number"
            )
    if not math.isfinite(args.road_friction) or args.road_friction < 0:
        parser.error("--road-friction must be a finite number greater than or equal to 0")
    return args


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def main():
    args = parse_args()
    output_path = args.output_dir / "data.csv"

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(10.0)
    opendrive_data = MAP_PATH.read_text(encoding="utf-8")
    world = client.generate_opendrive_world(opendrive_data)
    original_settings = world.get_settings()
    vehicle = None

    print("Connected to CARLA")
    print("Loaded OpenDRIVE map:", MAP_PATH)
    print("Map:", world.get_map().name)
    print(
        f"TestRun {args.run_id}: target speed={TARGET_SPEED_KMH:g} km/h, "
        f"duration={args.sim_time_s:g} s, "
        f"tire friction={args.tire_friction:g}, "
        f"road friction={args.road_friction:g}"
    )

    friction_trigger = None
    try:
        world.set_weather(WEATHER)
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = FIXED_DT
        world.apply_settings(settings)

        blueprint = world.get_blueprint_library().find("vehicle.tesla.model3")
        blueprint.set_attribute("role_name", "ego")
        start_waypoint = world.get_map().get_waypoint(
            START_LOCATION,
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
        if start_waypoint is None:
            raise RuntimeError(
                f"Khong tim thay driving lane tai vi tri bat dau {START_LOCATION}"
            )
        spawn_transform = start_waypoint.transform
        spawn_transform.location.z += 0.5
        vehicle = world.try_spawn_actor(blueprint, spawn_transform)
        if vehicle is None:
            raise RuntimeError(
                f"Khong spawn duoc ego vehicle tai {spawn_transform.location}"
            )

        trigger_blueprint = world.get_blueprint_library().find(
            "static.trigger.friction"
        )
        trigger_blueprint.set_attribute("friction", str(args.road_friction))
        trigger_length = max(
            20.0,
            30.0 * args.sim_time_s + 10.0,
        )
        trigger_blueprint.set_attribute("extent_x", str(trigger_length))
        trigger_blueprint.set_attribute("extent_y", "6.0")
        trigger_blueprint.set_attribute("extent_z", "5.0")
        friction_trigger = world.spawn_actor(
            trigger_blueprint,
            vehicle.get_transform(),
        )

        physics = vehicle.get_physics_control()
        wheels = physics.wheels
        if not wheels:
            raise RuntimeError("Ego vehicle khong co thong tin banh xe")
        for wheel in wheels:
            wheel.tire_friction = args.tire_friction
        physics.wheels = wheels
        vehicle.apply_physics_control(physics)
        applied_physics = vehicle.get_physics_control()
        applied_friction = [
            wheel.tire_friction for wheel in applied_physics.wheels
        ]
        print(
            f"Requested tire friction: {args.tire_friction:g}; "
            f"applied per wheel: {applied_friction}"
        )
        if any(
            not math.isclose(friction, args.tire_friction, rel_tol=1e-5, abs_tol=1e-5)
            for friction in applied_friction
        ):
            raise RuntimeError(
                "CARLA did not apply the requested tire friction "
                f"{args.tire_friction:g}; read back {applied_friction}"
            )
        max_steer_angle = max(
            (wheel.max_steer_angle for wheel in applied_physics.wheels),
            default=0.0,
        )

        args.output_dir.mkdir(parents=True, exist_ok=True)
        spectator = world.get_spectator()
        total_steps = int(args.sim_time_s / FIXED_DT)
        weather_change_pending = True
        target_speed_mps = TARGET_SPEED_KMH / 3.6
        speed_error_integral = 0.0

        with output_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
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
                    "roll_deg",
                    "phase",
                    "target_speed_mps",
                    "speed_error_mps",
                    "throttle",
                    "brake",
                ]
            )

            for step in range(total_steps):
                elapsed_s = step * FIXED_DT
                if weather_change_pending and elapsed_s >= WEATHER_CHANGE_AT_S:
                    world.set_weather(WEATHER_AFTER)
                    print(
                        f"Weather changed at t = {elapsed_s:.2f} s"
                    )
                    weather_change_pending = False

                transform = vehicle.get_transform()
                velocity = vehicle.get_velocity()
                acceleration = vehicle.get_acceleration()
                speed = math.sqrt(
                    velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2
                )
                speed_error = target_speed_mps - speed
                if speed_error >= 0:
                    speed_error_integral = clamp(
                        speed_error_integral + speed_error * FIXED_DT,
                        0.0,
                        SPEED_INTEGRAL_LIMIT,
                    )
                    throttle = clamp(
                        SPEED_KP * speed_error
                        + SPEED_KI * speed_error_integral,
                        0.0,
                        1.0,
                    )
                    brake = 0.0
                else:
                    throttle = 0.0
                    brake = clamp(BRAKE_KP * -speed_error, 0.0, 1.0)
                    speed_error_integral = 0.0

                if speed < target_speed_mps - SPEED_TOLERANCE_MPS:
                    phase = "accelerating"
                elif speed > target_speed_mps + SPEED_TOLERANCE_MPS:
                    phase = "slowing"
                else:
                    phase = "cruising"

                waypoint = world.get_map().get_waypoint(
                    transform.location,
                    project_to_road=True,
                )
                steer = 0.0
                if waypoint is not None:
                    next_waypoints = waypoint.next(3.0)
                    if next_waypoints:
                        target_location = next_waypoints[0].transform.location
                        dx = target_location.x - transform.location.x
                        dy = target_location.y - transform.location.y
                        target_yaw = math.atan2(dy, dx)
                        vehicle_yaw = math.radians(transform.rotation.yaw)
                        yaw_error = math.atan2(
                            math.sin(target_yaw - vehicle_yaw),
                            math.cos(target_yaw - vehicle_yaw),
                        )
                        steer = clamp(1.5 * yaw_error, -1.0, 1.0)

                vehicle.apply_control(
                    carla.VehicleControl(
                        throttle=throttle,
                        brake=brake,
                        steer=steer,
                    )
                )
                writer.writerow(
                    [
                        step * FIXED_DT,
                        transform.location.x,
                        transform.location.y,
                        speed,
                        velocity.x,
                        velocity.y,
                        acceleration.x,
                        acceleration.y,
                        steer,
                        steer * max_steer_angle,
                        transform.rotation.pitch,
                        transform.rotation.roll,
                        phase,
                        target_speed_mps,
                        speed_error,
                        throttle,
                        brake,
                    ]
                )

                forward = transform.get_forward_vector()
                spectator.set_transform(
                    carla.Transform(
                        transform.location
                        - forward * 8.0
                        + carla.Location(z=4.0),
                        carla.Rotation(
                            pitch=-15.0,
                            yaw=transform.rotation.yaw,
                        ),
                    )
                )
                world.tick()

                if step % int(1.0 / FIXED_DT) == 0:
                    print(
                        f"t = {elapsed_s:.1f} s | phase = {phase} | "
                        f"speed = {speed:.2f} m/s "
                        f"({speed * 3.6:.1f} km/h) | "
                        f"steer = {steer:.3f}"
                    )
    finally:
        if friction_trigger is not None:
            friction_trigger.destroy()
        if vehicle is not None:
            vehicle.destroy()
        world.apply_settings(original_settings)
        print("Cleanup completed")

    print("TestRun completed")
    print("Ego CSV:", output_path)


if __name__ == "__main__":
    main()
