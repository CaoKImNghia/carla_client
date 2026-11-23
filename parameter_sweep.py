"""Run all CARLA TestRuns described by a CSV plan, one after another."""

import argparse
import csv 
import subprocess 
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "run_id", "target_speed_kmh", "distance_ahead_m",
    "target_speed_diff_pct", "weather", "sim_time_s", "tire_friction",
} # các cái yêu cầu cột được xuất ra file .csv hoặc là log


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="sweep_plan.csv", help="CSV test plan") #đường dẫn file kế hoạch lấy từ sweep.plan
    parser.add_argument("--results-dir", default="results") # thư mục kết quả
    return parser.parse_args()


def read_last_speed(csv_path):
    last_row = None
    with csv_path.open(newline="") as handle:
        for last_row in csv.DictReader(handle):
            pass
    return float(last_row["v_mps"]) if last_row else None


def main():
    args = parse_args()
    plan_path = Path(args.plan)
    results_dir = Path(args.results_dir)

    with plan_path.open(newline="") as handle:
        runs = list(csv.DictReader(handle))

        if not runs or not REQUIRED_COLUMNS.issubset(runs[0]):
         missing = REQUIRED_COLUMNS - set(runs[0] if runs else [])
         raise ValueError(f"Plan is empty or missing columns: {sorted(missing)}")

    results_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    runner = Path(__file__).with_name("target_car.py")

    for index, run in enumerate(runs, start=1):
        run_id = run["run_id"].strip()
        run_dir = results_dir / run_id
        if not run_id or run_dir.name != run_id:
            raise ValueError(f"Invalid run_id at row {index}: {run_id!r}")
        run_dir.mkdir(parents=True, exist_ok=True)

        with (run_dir / "parameters.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=run.keys())
            writer.writeheader()
            writer.writerow(run)

        command = [
            sys.executable, str(runner), "--run-id", run_id,
            "--target-speed-kmh", run["target_speed_kmh"],
            "--distance-ahead-m", run["distance_ahead_m"],
            "--target-speed-diff-pct", run["target_speed_diff_pct"],
            "--weather", run["weather"],
            "--sim-time-s", run["sim_time_s"],
            "--tire-friction", run["tire_friction"],
            "--output-dir", str(run_dir),
        ]
        print(f"[{index}/{len(runs)}] Running {run_id}")
        completed = subprocess.run(command, text=True)
        record = dict(run)
        record["status"] = "ok" if completed.returncode == 0 else "failed"
        record["final_ego_speed_mps"] = ""
        ego_path = run_dir / "data_ego.csv"
        if completed.returncode == 0 and ego_path.exists():
            final_speed = read_last_speed(ego_path)
            record["final_ego_speed_mps"] = "" if final_speed is None else final_speed
        summary.append(record)

    summary_path = results_dir / "summary.csv"
    fields = list(runs[0]) + ["status", "final_ego_speed_mps"]
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)
    print(f"Finished. Summary: {summary_path}")


if __name__ == "__main__":
    main()
