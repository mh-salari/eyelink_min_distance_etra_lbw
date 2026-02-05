import json
from pathlib import Path

data_dir = Path("./data")

files = [
    ("16mm", "mh", "16mm_mh_01"),
    ("16mm", "r", "16mm_r_01"),
    ("25mm", "mh", "25mm_mh_01"),
    ("25mm", "r", "25mm_r_02"),
    ("35mm", "mh", "35mm_mh_01"),
    ("35mm", "r", "35mm_r_01"),
]

print("=" * 80)
print("SETUP PARAMETERS (from settings files)")
print("=" * 80)
print(f"{'Lens':<8} {'Participant':<12} {'screen_distance_top_bottom':<30} {'camera_to_screen':<20}")
print("-" * 80)

for lens, participant, basename in files:
    settings_path = data_dir / f"{basename}_settings.json"
    with open(settings_path) as f:
        settings = json.load(f)

    dist_top_bottom = settings["screen_distance_top_bottom"]
    cam_to_screen = settings["camera_to_screen_distance"]

    print(f"{lens:<8} {participant:<12} {str(dist_top_bottom):<30} {cam_to_screen:<20}")

print()
print("=" * 80)
print("VALIDATION ACCURACY (from data files)")
print("=" * 80)
print(f"{'Lens':<8} {'Participant':<12} {'Left avg':<10} {'Left max':<10} {'Right avg':<10} {'Right max':<10}")
print("-" * 80)

results = {}
setup_params = {}

for lens, participant, basename in files:
    data_path = data_dir / f"{basename}.json"
    with open(data_path) as f:
        data = json.load(f)

    # Get last validation
    val = data["validations"][-1]
    left = val["summary_left"]
    right = val["summary_right"]

    print(f"{lens:<8} {participant:<12} {left['error_avg_deg']:<10.2f} {left['error_max_deg']:<10.2f} {right['error_avg_deg']:<10.2f} {right['error_max_deg']:<10.2f}")

    if lens not in results:
        results[lens] = []
        # Load settings once per lens (same for both participants)
        settings_path = data_dir / f"{basename}_settings.json"
        with settings_path.open() as f:
            settings = json.load(f)
        setup_params[lens] = {
            "screen_distance_top_bottom": settings["screen_distance_top_bottom"],
            "camera_to_screen": settings["camera_to_screen_distance"],
        }
    results[lens].append({
        "participant": participant,
        "left_avg": left["error_avg_deg"],
        "left_max": left["error_max_deg"],
        "right_avg": right["error_avg_deg"],
        "right_max": right["error_max_deg"],
    })

print()
print("=" * 120)
print("SUMMARY BY LENS (average of both participants)")
print("=" * 120)
print(f"{'Lens':<8} {'screen_dist_top_bottom':<25} {'cam_to_screen':<15} {'Left avg':<12} {'Left max':<12} {'Right avg':<12} {'Right max':<12} {'Both avg':<12} {'Both max':<12}")
print("-" * 120)

for lens in ["16mm", "25mm", "35mm"]:
    left_avg_list = [r["left_avg"] for r in results[lens]]
    left_max_list = [r["left_max"] for r in results[lens]]
    right_avg_list = [r["right_avg"] for r in results[lens]]
    right_max_list = [r["right_max"] for r in results[lens]]

    left_avg_mean = sum(left_avg_list) / len(left_avg_list)
    left_max_mean = sum(left_max_list) / len(left_max_list)
    right_avg_mean = sum(right_avg_list) / len(right_avg_list)
    right_max_mean = sum(right_max_list) / len(right_max_list)

    both_avg_mean = (left_avg_mean + right_avg_mean) / 2
    both_max_mean = (left_max_mean + right_max_mean) / 2

    dist = setup_params[lens]["screen_distance_top_bottom"]
    cam = setup_params[lens]["camera_to_screen"]

    print(f"{lens:<8} {dist!s:<25} {cam:<15} {left_avg_mean:<12.2f} {left_max_mean:<12.2f} {right_avg_mean:<12.2f} {right_max_mean:<12.2f} {both_avg_mean:<12.2f} {both_max_mean:<12.2f}")
