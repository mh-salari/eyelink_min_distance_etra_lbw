import json
import math
import re
from pathlib import Path

data_dir = Path("./data")

# Auto-discover all data files by finding *_settings.json (excluding other_data/)
# Filename pattern: {lens}_{participant}_{number}_settings.json
entries = []
for settings_path in sorted(data_dir.glob("*_settings.json")):
    basename = settings_path.name.replace("_settings.json", "")
    json_path = data_dir / f"{basename}.json"
    if not json_path.exists():
        continue  # skip if no parsed data file

    # Parse lens and participant from filename (e.g., "16mm_mh_01" or "25mm_461_02")
    match = re.match(r"(\d+mm)_(.+?)_\d+$", basename)
    if not match:
        continue
    lens = match.group(1)
    participant = match.group(2)
    entries.append((lens, participant, basename))

# Screen parameters for visual angle calculation
SCREEN_W_PX, SCREEN_H_PX = 1280, 1024
SCREEN_W_MM, SCREEN_H_MM = 376.0, 301.0

print("=" * 80)
print("SETUP PARAMETERS (from settings files)")
print("=" * 80)
print(f"{'Lens':<8} {'Participant':<12} {'screen_distance_top_bottom':<30} {'camera_to_screen':<20}")
print("-" * 80)

for lens, participant, basename in entries:
    settings_path = data_dir / f"{basename}_settings.json"
    with open(settings_path) as f:
        settings = json.load(f)

    dist_top_bottom = settings["screen_distance_top_bottom"]
    cam_to_screen = settings["camera_to_screen_distance"]

    print(f"{lens:<8} {participant:<12} {str(dist_top_bottom):<30} {cam_to_screen:<20}")

print()
print("=" * 100)
print("VALIDATION ACCURACY — last validation per file (from data files)")
print("=" * 100)
print(
    f"{'Lens':<8} {'Participant':<12} {'#Cal':<6} {'#Val':<6} {'Left avg':<10} {'Left max':<10} {'Right avg':<10} {'Right max':<10}"
)
print("-" * 100)

results = {}
setup_params = {}

for lens, participant, basename in entries:
    data_path = data_dir / f"{basename}.json"
    with open(data_path) as f:
        data = json.load(f)

    n_cal = len(data["calibrations"])
    n_val = len(data["validations"])

    # Use last validation
    val = data["validations"][-1]
    left = val["summary_left"]
    right = val["summary_right"]

    marker = " *" if n_val > 1 else ""
    print(
        f"{lens:<8} {participant:<12} {n_cal:<6} {n_val:<6} {left['error_avg_deg']:<10.2f} {left['error_max_deg']:<10.2f} {right['error_avg_deg']:<10.2f} {right['error_max_deg']:<10.2f}{marker}"
    )

    if lens not in results:
        results[lens] = []
        settings_path = data_dir / f"{basename}_settings.json"
        with settings_path.open() as f:
            settings = json.load(f)
        setup_params[lens] = {
            "screen_distance_top_bottom": settings["screen_distance_top_bottom"],
            "camera_to_screen": settings["camera_to_screen_distance"],
            "calibration_area_proportion": settings["calibration_area_proportion"],
        }
    results[lens].append(
        {
            "participant": participant,
            "left_avg": left["error_avg_deg"],
            "left_max": left["error_max_deg"],
            "right_avg": right["error_avg_deg"],
            "right_max": right["error_max_deg"],
        }
    )

print()
print("  * = multiple calibrations/validations were performed; last validation used")

print()
print("=" * 140)
print("SUMMARY BY LENS (average across all participants)")
print("=" * 140)
print(
    f"{'Lens':<8} {'screen_dist_top_bottom':<25} {'cam_to_screen':<15} {'Left avg':<12} {'Left max':<12} {'Right avg':<12} {'Right max':<12} {'Both avg±SD':<16} {'Both max±SD':<16} {'Cal Area (H×V)':<18}"
)
print("-" * 140)

for lens in sorted(results.keys()):
    left_avg_list = [r["left_avg"] for r in results[lens]]
    left_max_list = [r["left_max"] for r in results[lens]]
    right_avg_list = [r["right_avg"] for r in results[lens]]
    right_max_list = [r["right_max"] for r in results[lens]]

    left_avg_mean = sum(left_avg_list) / len(left_avg_list)
    left_max_mean = sum(left_max_list) / len(left_max_list)
    right_avg_mean = sum(right_avg_list) / len(right_avg_list)
    right_max_mean = sum(right_max_list) / len(right_max_list)

    # Per-participant both-eyes averages
    both_avg_list = [(r["left_avg"] + r["right_avg"]) / 2 for r in results[lens]]
    both_max_list = [(r["left_max"] + r["right_max"]) / 2 for r in results[lens]]

    both_avg_mean = sum(both_avg_list) / len(both_avg_list)
    both_max_mean = sum(both_max_list) / len(both_max_list)

    both_avg_sd = math.sqrt(sum((x - both_avg_mean) ** 2 for x in both_avg_list) / (len(both_avg_list) - 1))
    both_max_sd = math.sqrt(sum((x - both_max_mean) ** 2 for x in both_max_list) / (len(both_max_list) - 1))

    dist = setup_params[lens]["screen_distance_top_bottom"]
    cam = setup_params[lens]["camera_to_screen"]
    cal_prop = setup_params[lens]["calibration_area_proportion"]

    # Compute calibration area visual angle
    cal_w_px = SCREEN_W_PX * cal_prop[0]
    cal_h_px = SCREEN_H_PX * cal_prop[1]
    cal_w_mm = cal_w_px * (SCREEN_W_MM / SCREEN_W_PX)
    cal_h_mm = cal_h_px * (SCREEN_H_MM / SCREEN_H_PX)
    d = dist[0]  # eye-to-screen-top distance
    va_h = 2 * math.degrees(math.atan(cal_w_mm / (2 * d)))
    va_v = 2 * math.degrees(math.atan(cal_h_mm / (2 * d)))

    cal_area_str = f"{va_h:.1f}° × {va_v:.1f}°"

    print(
        f"{lens:<8} {dist!s:<25} {cam:<15} {left_avg_mean:<12.2f} {left_max_mean:<12.2f} {right_avg_mean:<12.2f} {right_max_mean:<12.2f} {both_avg_mean:.2f}±{both_avg_sd:.2f}{'':>4} {both_max_mean:.2f}±{both_max_sd:.2f}{'':>4} {cal_area_str:<18}"
    )
