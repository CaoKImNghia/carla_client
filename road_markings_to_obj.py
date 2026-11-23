"""Export OpenDRIVE road markings as an Unreal-ready OBJ mesh.

The output uses CARLA/Unreal coordinates in centimeters, with the OpenDRIVE
Y axis flipped. Import the OBJ into the CARLA Unreal project at world origin.
"""

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path


SAMPLE_STEP_M = 0.5
DEFAULT_DASH_M = 3.0
MARKING_Z_CM = 2.0
CM_PER_M = 100.0

MATERIALS = {
    "white": (1.0, 1.0, 1.0),
    "yellow": (1.0, 0.8, 0.0),
    "red": (1.0, 0.0, 0.0),
    "blue": (0.0, 0.3, 1.0),
    "green": (0.0, 0.8, 0.0),
}


def polynomial(element, distance):
    return sum(
        float(element.get(coefficient, "0")) * distance ** power
        for power, coefficient in enumerate(("a", "b", "c", "d"))
    )


def active_record(records, distance, offset_attribute):
    eligible = [
        record for record in records
        if float(record.get(offset_attribute, "0")) <= distance + 1e-9
    ]
    return max(eligible, key=lambda record: float(record.get(offset_attribute, "0"))) if eligible else None


def road_position(geometries, distance):
    geometry = next(
        (
            item for item in geometries
            if float(item.get("s")) - 1e-9
            <= distance
            <= float(item.get("s")) + float(item.get("length")) + 1e-9
        ),
        geometries[-1],
    )
    start_s = float(geometry.get("s"))
    offset = min(max(distance - start_s, 0.0), float(geometry.get("length")))
    x = float(geometry.get("x"))
    y = float(geometry.get("y"))
    heading = float(geometry.get("hdg"))
    line = geometry.find("line")
    arc = geometry.find("arc")

    if line is not None:
        x += offset * math.cos(heading)
        y += offset * math.sin(heading)
    elif arc is not None:
        curvature = float(arc.get("curvature"))
        if abs(curvature) < 1e-12:
            x += offset * math.cos(heading)
            y += offset * math.sin(heading)
        else:
            end_heading = heading + curvature * offset
            x += (math.sin(end_heading) - math.sin(heading)) / curvature
            y += (math.cos(heading) - math.cos(end_heading)) / curvature
            heading = end_heading
    else:
        raise ValueError("This exporter supports OpenDRIVE line and arc geometry only")

    return x, y, heading


def lane_width(lane, section_s, distance):
    widths = lane.findall("width")
    record = active_record(widths, distance - section_s, "sOffset")
    if record is None:
        return 0.0
    return polynomial(record, distance - section_s - float(record.get("sOffset", "0")))


def lane_offset(lanes, distance):
    records = lanes.findall("laneOffset")
    record = active_record(records, distance, "s")
    if record is None:
        return 0.0
    return polynomial(record, distance - float(record.get("s")))


def lane_boundary_t(section, lane, lanes_element, distance):
    section_s = float(section.get("s", "0"))
    lane_offset_value = lane_offset(lanes_element, distance)
    lane_id = int(lane.get("id"))
    if lane_id == 0:
        return lane_offset_value

    side = section.find("left" if lane_id > 0 else "right")
    lane_nodes = [] if side is None else side.findall("lane")
    if lane_id > 0:
        lane_nodes.sort(key=lambda item: int(item.get("id")))
        outward_lanes = [item for item in lane_nodes if 0 < int(item.get("id")) <= lane_id]
        sign = 1.0
    else:
        lane_nodes.sort(key=lambda item: int(item.get("id")), reverse=True)
        outward_lanes = [item for item in lane_nodes if lane_id <= int(item.get("id")) < 0]
        sign = -1.0

    return lane_offset_value + sign * sum(
        lane_width(item, section_s, distance) for item in outward_lanes
    )


def marking_intervals(marking, start_s, end_s):
    kind = marking.get("type", "none").lower()
    if kind == "none":
        return []
    if kind not in {"solid", "broken", "dashed"}:
        return []
    if kind == "solid":
        return [(start_s, end_s)]

    dash_length = DEFAULT_DASH_M
    gap_length = DEFAULT_DASH_M
    line = marking.find("type/line")
    if line is not None:
        dash_length = float(line.get("length", dash_length))
        gap_length = float(line.get("space", gap_length))
    if dash_length <= 0 or gap_length < 0:
        raise ValueError("Dashed road-mark lengths must be positive")

    intervals = []
    cursor = start_s
    while cursor < end_s:
        dash_end = min(cursor + dash_length, end_s)
        if dash_end > cursor:
            intervals.append((cursor, dash_end))
        cursor += dash_length + gap_length
    return intervals


def sample_stations(start_s, end_s):
    count = max(1, math.ceil((end_s - start_s) / SAMPLE_STEP_M))
    return [start_s + (end_s - start_s) * index / count for index in range(count + 1)]


def make_ribbon_vertices(geometries, section, lane, lanes_element, start_s, end_s, width_m):
    points = []
    for distance in sample_stations(start_s, end_s):
        x, y, heading = road_position(geometries, distance)
        t = lane_boundary_t(section, lane, lanes_element, distance)
        center_x = x - math.sin(heading) * t
        center_y = y + math.cos(heading) * t
        left_x = center_x - math.sin(heading) * width_m / 2.0
        left_y = center_y + math.cos(heading) * width_m / 2.0
        right_x = center_x + math.sin(heading) * width_m / 2.0
        right_y = center_y - math.cos(heading) * width_m / 2.0

        # CARLA uses the opposite Y direction from OpenDRIVE in Unreal space.
        points.append(
            (
                (left_x * CM_PER_M, -left_y * CM_PER_M, MARKING_Z_CM),
                (right_x * CM_PER_M, -right_y * CM_PER_M, MARKING_Z_CM),
            )
        )
    return points


def collect_markings(root):
    strips = []
    for road in root.findall("road"):
        geometries = road.findall("planView/geometry")
        lane_sections = road.findall("lanes/laneSection")
        lanes_element = road.find("lanes")
        for section_index, section in enumerate(lane_sections):
            section_start = float(section.get("s", "0"))
            section_end = (
                float(lane_sections[section_index + 1].get("s"))
                if section_index + 1 < len(lane_sections)
                else section_start + float(road.get("length"))
            )
            for side_name in ("left", "center", "right"):
                side = section.find(side_name)
                if side is None:
                    continue
                for lane in side.findall("lane"):
                    lane_id = int(lane.get("id"))
                    marks = sorted(
                        lane.findall("roadMark"),
                        key=lambda item: float(item.get("sOffset", "0")),
                    )
                    for mark_index, mark in enumerate(marks):
                        mark_start = section_start + float(mark.get("sOffset", "0"))
                        mark_end = (
                            section_start + float(marks[mark_index + 1].get("sOffset"))
                            if mark_index + 1 < len(marks)
                            else section_end
                        )
                        mark_start = max(mark_start, section_start)
                        mark_end = min(mark_end, section_end)
                        width_m = float(mark.get("width", "0.13"))
                        color = mark.get("color", "standard").lower()
                        color = "white" if color in {"standard", ""} else color
                        if color not in MATERIALS:
                            color = "white"
                        for interval_start, interval_end in marking_intervals(
                            mark, mark_start, mark_end
                        ):
                            if interval_end - interval_start < 1e-5:
                                continue
                            vertices = make_ribbon_vertices(
                                geometries,
                                section,
                                lane,
                                lanes_element,
                                interval_start,
                                interval_end,
                                width_m,
                            )
                            strips.append(
                                {
                                    "road_id": road.get("id"),
                                    "lane_id": lane_id,
                                    "color": color,
                                    "vertices": vertices,
                                }
                            )
    return strips


def write_mtl(path):
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for name, color in MATERIALS.items():
            handle.write(f"newmtl {name}\n")
            handle.write(f"Kd {color[0]:.4f} {color[1]:.4f} {color[2]:.4f}\n")
            handle.write("Ka 0.0000 0.0000 0.0000\n")
            handle.write("illum 1\n\n")


def write_obj(path, mtl_path, strips):
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write("# Generated from OpenDRIVE roadMark records\n")
        handle.write(f"mtllib {mtl_path.name}\n")
        vertex_index = 1
        for strip_index, strip in enumerate(strips):
            handle.write(
                f"o road_{strip['road_id']}_lane_{strip['lane_id']}_mark_{strip_index}\n"
            )
            handle.write(f"usemtl {strip['color']}\n")
            for left, right in strip["vertices"]:
                for x, y, z in (left, right):
                    handle.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            for point_index in range(len(strip["vertices"]) - 1):
                first = vertex_index + point_index * 2
                # Winding gives the mesh an upward-facing normal in Unreal space.
                handle.write(
                    f"f {first} {first + 2} {first + 3} {first + 1}\n"
                )
            vertex_index += len(strip["vertices"]) * 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xodr",
        type=Path,
        default=Path(__file__).resolve().with_name("my_road.xodr"),
        help="Input OpenDRIVE file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent
        / "assets"
        / "road_markings"
        / "my_road_markings.obj",
        help="Output OBJ file",
    )
    args = parser.parse_args()
    if not args.xodr.is_file():
        parser.error(f"OpenDRIVE file does not exist: {args.xodr}")

    root = ET.parse(args.xodr).getroot()
    strips = collect_markings(root)
    if not strips:
        raise RuntimeError(f"No supported road markings found in {args.xodr}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mtl_path = args.output.with_suffix(".mtl")
    write_mtl(mtl_path)
    write_obj(args.output, mtl_path, strips)
    print(f"Exported {len(strips)} marking mesh strips")
    print(f"OBJ: {args.output}")
    print(f"MTL: {mtl_path}")


if __name__ == "__main__":
    main()
