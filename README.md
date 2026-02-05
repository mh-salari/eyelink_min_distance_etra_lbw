# EyeLink Minimum Distance Experiment

Code and data for the paper:

> **How Close Can You Get? Minimum Eye-to-Screen Distance for EyeLink 1000 Plus**
> ETRA 2026 Late-Breaking Work

## Repository Contents

- `main.py` — Experiment script used to collect calibration, validation, and fixation data with the EyeLink 1000 Plus via [PyeLink](https://github.com/mh-salari/pyelink).
- `extract_results.py` — Script to extract and summarize results from the recorded data.
- `data/` — All recorded data from the experiment (6 sessions: 3 lenses × 2 participants), including:
  - `.edf` / `.asc` — Raw and converted EyeLink data files
  - `_settings.json` — Experiment settings (distances, calibration parameters)
  - `_calibrations.txt` / `_validations.txt` / `_samples.csv` / `_metadata.txt` / `.json` / `.png` — Parsed and extracted data (generated from `.asc` using [SyeLink](https://github.com/mh-salari/syelink))

## Installation

### 1. Install uv (macOS)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install PortAudio (macOS, required by PyAudio for audio beeps)

```bash
brew install portaudio
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Install EyeLink Developers Kit

The EyeLink Developers Kit (native C libraries) must be installed on the system. Download and install it from:
https://www.sr-research.com/support/thread-13.html

### 5. Install SR Research PyLink

The `pylink` package must be installed manually (no macOS ARM wheel on PyPI):

```bash
uv pip install --index-url https://pypi.sr-support.com sr-research-pylink
```

## Usage

```bash
uv run main.py
```

Edit the settings in `main.py` to match your setup (screen dimensions, eye-to-screen distance, etc.).
