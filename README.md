# Heat Map — Retail foot-traffic analytics

Real-time people tracking and heat maps for retail stores. Cameras feed a YOLOv8 + IoU tracking pipeline; results are stored in SQLite (or PostgreSQL/Supabase) and exposed via **FastAPI** with a **TypeScript** web app (Vite + React).

## Requirements

- Python 3.10+
- Webcam, RTSP stream, or sample video file
- Optional: NVIDIA GPU + CUDA for faster detection (`HEAT_MAP_ENV=prod`)

## Quick start

```powershell
cd Heat_Map
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Important:** Use the project venv (activate it first, or use `.\.venv\Scripts\python.exe`).
> Running plain `python` uses the system Python and will fail with `No module named streamlit`.

**Terminal 1 — API and pipeline (port 8000):**

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/run_pipeline.py
# or: .\run_pipeline.bat
```

**Terminal 2 — Web app (port 5173):**

```powershell
python scripts/run_web.py
# requires Node.js / npm; installs web deps on first run
```

The legacy Streamlit UI remains available via `python scripts/run_dashboard.py` (port 8501).

Open http://localhost:5173, register a user, rename your shops/cameras under **Mis tiendas**, and explore Live / Historical / Analytics.

- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

## Configuration

Base settings: [`config/settings.yaml`](config/settings.yaml).

| Method | Example |
|--------|---------|
| Dev profile (video file + separate DB) | `$env:HEAT_MAP_ENV="dev"; python scripts/run_pipeline.py` |
| Or | `python scripts/run_pipeline.py --env dev` |
| Prod profile (larger YOLO + GPU) | `python scripts/run_pipeline.py --env prod` |
| Custom YAML | `python scripts/run_pipeline.py --config config/settings.dev.yaml` |
| Override camera | `python scripts/run_pipeline.py --source data/recordings/sample.mp4` |

Environment variables (see [`.env.example`](.env.example)):

| Variable | Purpose |
|----------|---------|
| `DB_URL` | Database connection string |
| `HEAT_MAP_ENV` | `dev` or `prod` — merge overlay YAML |
| `HEAT_MAP_CONFIG_PATH` | Explicit config file path |
| `HEAT_MAP_CAMERA_SOURCE` | Override first camera source |
| `AUTH_SECRET_KEY` | JWT signing secret |
| `API_BASE_URL` | Dashboard → API URL |
| `DETECTION_DEVICE` | e.g. `cuda:0` or `cpu` |

## Database

- **Default:** SQLite at `data/heatmap.db` (created automatically, WAL mode).
- **Production / cloud:** PostgreSQL or [Supabase](docs/supabase.md) — set `DB_URL` to a `postgresql+psycopg2://...` URL.
- Schema is created on startup via SQLAlchemy; SQL reference: [`src/storage/migrations/`](src/storage/migrations/).

## Other commands

```powershell
# Validate config without starting the server
python scripts/run_pipeline.py --dry-run

# Process a recorded video into the database
python scripts/ingest_recording.py --file data/recordings/sample.mp4 --env dev

# Export historical heat map PNG
python scripts/generate_historical_heatmap.py --output data/heatmaps/output.png

# Run tests
pip install -r requirements-dev.txt
pytest
```

## First-time admin access

Registration creates **customer** users only. To use the admin panel (Users / Shops / Cameras), set `role = 'admin'` on your user in the database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Dashboard cannot connect to API | Start `run_pipeline.py` first; check `dashboard.api_base_url` |
| No live camera feed | No webcam at index `0` — use `--env dev` or `--source path/to/video.mp4` |
| `No module named streamlit` | Activate venv: `.\.venv\Scripts\Activate.ps1` or use `.\run_dashboard.bat` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the venv |
| `pip` WinError 5 on `cv2.pyd` | Stop API/dashboard processes, then reinstall |
| Empty dwell analytics | Ensure pipeline is running; dwell is written when tracks leave the frame |
| PostgreSQL connection errors | Install deps and set `DB_URL`; see [docs/supabase.md](docs/supabase.md) |

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for module layout and data flow.

## Project layout

```
src/           Application code (API, pipeline, legacy Streamlit dashboard, storage)
web/           TypeScript + React web app (Vite)
scripts/       CLI entry points
config/        YAML settings
tests/         Pytest suite
data/          Runtime DB, recordings, heatmap exports (gitignored)
```
