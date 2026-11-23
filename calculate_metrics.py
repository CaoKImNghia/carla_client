"""Calculate ego/target metrics from CSV files produced by target_car.py.

Distance and TTC use vehicle centers in the XY plane. Collision is left blank
because the source CSV files do not contain collision sensor events.
"""

import argparse #dùng để truyền duwxx liệu thư mục khi chạy
import csv #dùng để đọc cũng như là xuất ra file csv
import math #dùng để tính toán
from pathlib import Path # dùng để xử lý đường dẫn

#các dictionary của các cột yêu cầu và đầu ra
REQUIRED_COLUMNS = {
    "time_s", "actor_id", "x_m", "y_m", "vx_mps", "vy_mps",
}
OUTPUT_COLUMNS = [
    "time_s", "ego_id", "target_id", "center_distance_m",
    "relative_velocity_mps", "ttc_s", "acceleration_mps2",
    "jerk_mps3", "stopping_distance_m", "collision",
]


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle) #đọc file csv thành dạng dictionary
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        return list(reader)


def planar_speed(row):
    
    return math.hypot(float(row["vx_mps"]), float(row["vy_mps"]))


def ego_motion(ego_rows):
    """Return ego rows and speed-based acceleration/jerk indexed by time_s."""
    motion = {}
    previous_time = previous_speed = previous_acceleration = None

    for row in sorted(ego_rows, key=lambda item: float(item["time_s"])): # dùng cột time_s làm tiêu chí sắp xếp
        time = float(row["time_s"]) #đổi từ chuỗi csv thành float
        speed = planar_speed(row)
        acceleration = jerk = None

        if previous_time is not None:
            dt = time - previous_time
            if dt <= 0:
                raise ValueError("Ego time_s must increase without duplicates")
            acceleration = (speed - previous_speed) / dt
            if previous_acceleration is not None:
                jerk = (acceleration - previous_acceleration) / dt

        motion[row["time_s"]] = (row, speed, acceleration, jerk)
        previous_time, previous_speed = time, speed
        previous_acceleration = acceleration

    return motion


def format_number(value):
    return "" if value is None else f"{value:.6f}"


def calculate(ego, target, speed, acceleration, jerk, deceleration):
    dx = float(target["x_m"]) - float(ego["x_m"])
    dy = float(target["y_m"]) - float(ego["y_m"])
    distance = math.hypot(dx, dy)

    relative_velocity = ttc = None
    if distance > 0:
        # Positive means the separation along the line between the cars shrinks.
        relative_velocity = (
            (float(ego["vx_mps"]) - float(target["vx_mps"])) * dx
            + (float(ego["vy_mps"]) - float(target["vy_mps"])) * dy
        ) / distance
        if relative_velocity > 0:
            ttc = distance / relative_velocity

    # Assumes constant braking deceleration; reaction distance is excluded.
    stopping_distance = speed * speed / (2 * deceleration)
    #sau khi tính xong thì hàm  trả về 1 dictionary
    return {
        "time_s": ego["time_s"],
        "ego_id": ego["actor_id"],
        "target_id": target["actor_id"],
        "center_distance_m": format_number(distance),
        "relative_velocity_mps": format_number(relative_velocity),
        "ttc_s": format_number(ttc),
        "acceleration_mps2": format_number(acceleration),
        "jerk_mps3": format_number(jerk),
        "stopping_distance_m": format_number(stopping_distance),
        "collision": "",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir", type=Path,
        default=Path(__file__).resolve().parent / "results" / "clear_slow_near",
        help="Directory containing data_ego.csv and target_data.csv",
    )
    parser.add_argument(
        "--deceleration-mps2", type=float, default=6.0,
        help="Assumed constant braking deceleration (default: 6 m/s^2)",
    )
    args = parser.parse_args()
    if not math.isfinite(args.deceleration_mps2) or args.deceleration_mps2 <= 0:
        parser.error("--deceleration-mps2 must be a positive finite number")

    ego = ego_motion(read_rows(args.input_dir / "data_ego.csv"))
    targets = read_rows(args.input_dir / "target_data.csv")
    output_path = args.input_dir / "metrics.csv"
    count = 0

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for target in targets:
            time = target["time_s"]
            
            if float(time) == 0:
                continue
            if time not in ego:
                raise ValueError(f"No ego row for target time_s={time}")
            ego_row, speed, acceleration, jerk = ego[time]
            writer.writerow(calculate(
                ego_row, target, speed, acceleration, jerk,
                args.deceleration_mps2,
            ))
            count += 1

    print(f"Wrote {count} rows to {output_path}")


if __name__ == "__main__":
    main()
