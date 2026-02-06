"""Calibration & Validation Example using Pyglet backend.

Simple experiment:
1. Camera setup
2. Calibrate + Validate (both available, white background)
3. Show dark fixation target at screen center for 5 seconds while recording
4. End experiment
"""

import io
from pathlib import Path

import pyglet
# from jva_capture import JVACapture

import pyelink as el
from pyelink.calibration.targets import generate_target

FIXATION_DURATION = 5.0  # seconds to show fixation target

# ============================================================
# Pre-flight checks (before connecting to EyeLink)
# ============================================================
filename = input("Recording name: ").strip()
if not filename:
    raise SystemExit("No filename provided.")

edf_path = Path(f"./data/{filename}.edf")
if edf_path.exists():
    raise SystemExit(f"Recording already exists: {edf_path}")

# JVACapture.find_device()

proportion = 0.5

settings = el.Settings(
    backend="pyglet",
    fullscreen=True,
    display_index=0,
    enable_long_filenames=True,
    filename=filename,
    filepath="./data/",
    eye_tracked="BOTH",
    el_configuration="BTABLER",  # BTABLER: binocular head-fixed, "RBTABLER": binocular remote
    illumination_power=3,  # IR power: 1=100%, 2=75%, 3=50%
    n_cal_targets=9,  # calibration points: 3 (H3), 5 (HV5), 9 (HV9), 13 (HV13)
    # Screen resolution and physical measurements - critical for accurate gaze data
    screen_res=(1280, 1024),  # screen resolution in pixels (must match actual display)
    screen_width=376.0,  # display area width in mm (not including bezel)
    screen_height=301.0,  # display area height in mm (not including bezel)
    # screen_distance_top_bottom=(335, 465),  # (top, bottom) mm from eye to screen edges
    # camera_to_screen_distance=115,  # mm from camera lens to screen surface
    # camera_lens_focal_length=25,  # mm: 25, 35, or 16
    screen_distance_top_bottom=(330, 480),  # (top, bottom) mm from eye to screen edges
    camera_to_screen_distance=95,  # mm from camera lens to screen surface
    camera_lens_focal_length=16,  # mm: 25, 35, or 16
    # screen_distance_top_bottom=(457, 525),  # (top, bottom) mm from eye to screen edges
    # camera_to_screen_distance=105,  # mm from camera lens to screen surface
    # camera_lens_focal_length=35,  # mm: 25, 35, or 16
    # White background for calibration
    cal_background_color=(255, 255, 255),
    calibration_text_color=(0, 0, 0),
    calibration_text_font_size=10,
    # Calibration/validation geometry
    calibration_area_proportion=(proportion * 0.88, proportion * 0.83),
    validation_area_proportion=(proportion * 0.88, proportion * 0.83),
    # calibration_corner_scaling=0.75,
    # validation_corner_scaling=0.75,
    # Dark fixation target with transparent cross
    fixation_center_color=(0, 0, 0, 255),
    fixation_outer_color=(0, 0, 0, 255),
    fixation_cross_color=(0, 0, 0, 0),
)

# ============================================================
# Connect and setup
# ============================================================
print("Connecting to EyeLink and creating window...")
tracker = el.EyeLink(settings, record_raw_data=True)

settings_path = f"{tracker.settings.filepath}{tracker.settings.filename}_settings.json"
tracker.settings.save_to_file(settings_path)
print(f"Settings saved to {settings_path}")

# capture = JVACapture(f"{tracker.settings.filepath}{tracker.settings.filename}.mkv")
# tracker.register_cleanup(capture.stop)

# print("Starting screen capture...")
# capture.start()

# ============================================================
# Step 1: Cameera Settup, Calibrate + Validate
# ============================================================
print("\n=== Calibrate & Validate ===")
print("Press 'C' to calibrate, 'V' to validate, then Enter to accept")
tracker.calibrate(record_samples=False)

# ============================================================
# Step 2: Show fixation target at center for 5 seconds
# ============================================================
print(f"\n=== Fixation Target ({FIXATION_DURATION}s) ===")
tracker.start_recording()

# White background
pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

# Generate dark fixation target
pil_image = generate_target(tracker.settings)
buffer = io.BytesIO()
pil_image.save(buffer, format="PNG")
buffer.seek(0)
img = pyglet.image.load("target.png", file=buffer)
img.anchor_x = img.width // 2
img.anchor_y = img.height // 2
target_sprite = pyglet.sprite.Sprite(img)
target_sprite.x = tracker.window.width // 2
target_sprite.y = tracker.window.height // 2

tracker.window.clear()
target_sprite.draw()
tracker.window.flip()
tracker.wait(FIXATION_DURATION)

tracker.stop_recording()

# ============================================================
# Done
# ============================================================
print("\n=== Experiment Complete ===")
tracker.end_experiment()
