# App

This folder contains the PLC communication worker and supporting dependency modules.

## Key files
- `main.py` — worker entrypoint for MQTT listening and Vecow I/O handling
- `Dependencies/config.yaml` — default runtime configuration
- `Dependencies/loadConfig.py` — configuration loader
- `Dependencies/dio_controller.py` — digital I/O controller helper

## Configuration
Update `app/Dependencies/config.yaml` with values that match your environment.
The application expects the following keys:
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

## Notes
Ensure the configuration file contains all required keys before starting the worker.

