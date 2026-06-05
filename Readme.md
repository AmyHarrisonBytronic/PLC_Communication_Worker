# PLC Communication Worker

A Python worker that listens for MQTT trigger messages and writes digital I/O values to a Vecow I/O controller.

## Requirements
- Python 3.8 or newer
- pip
- An MQTT broker accessible from the configured `ip` and `port`
- `requirements.txt`

## Setup
1. Clone the repository.
2. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Update configuration in `app/Dependencies/config.yaml`.

## Configuration
The worker reads runtime settings from `app/Dependencies/config.yaml`.
Current application code expects the following keys:
- `ip`
- `port`
- `trigger_topic`
- `image_topic`
- `dio_count`
- `message`

## Run
From the repository root:

```powershell
python app/main.py
```

## Tests
Run the test suite from the repository root:

```powershell
python -m pytest test
```

## Project layout
- `app/` — application code and runtime dependencies
- `app/Dependencies/` — configuration loader, I/O helpers, and default config
- `docs/` — documentation and license assets
- `test/` — automated test cases
- `tools/` — helper scripts

## Notes
- See `app/readme.md` for app-specific usage notes.
- License file is `docs/LISENCE`.

