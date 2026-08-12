# AGENTS.md

## Cursor Cloud specific instructions

This is a Python 3.10+ project (**Heat Map** — retail foot-traffic analytics). It has two
long-running services plus an embedded SQLite database. Standard commands live in
[`README.md`](README.md); the notes below only capture non-obvious, Cloud-specific caveats.

### Environment / interpreter
- Dependencies are installed into a project virtualenv at `.venv` (the startup update script
  creates it and runs `pip install`). Always run project commands with that interpreter, e.g.
  `source .venv/bin/activate` first, or call `.venv/bin/python` / `.venv/bin/pytest` directly.
- The helper `scripts/_venv_python.py` only auto-detects a **Windows** venv
  (`.venv/Scripts/python.exe`). On Linux it falls back to `sys.executable`, so the venv must be
  active (or you must invoke `.venv/bin/python`) or the run scripts will use system Python and
  fail with `No module named streamlit`.
- Creating the venv requires the system package `python3.12-venv` (already present in this
  environment). It is a system dependency, so it is intentionally not in the update script.

### Running the app (two services)
- API + CV pipeline: `python scripts/run_pipeline.py --env dev` → serves on port `8000`
  (`/health`, `/docs`). The FastAPI process also runs the camera→detect→track→heatmap pipeline.
- Web app: `python scripts/run_web.py` → Vite/React on port `5173` (proxies to the API).
  Requires Node.js/npm. Prefer this over the legacy Streamlit UI.
- Legacy dashboard: `python scripts/run_dashboard.py` → Streamlit on port `8501`.
- Start the API first, or dashboard data/login calls fail (they degrade gracefully).
- Start each service in its own persistent shell (e.g. tmux); they are foreground/long-running.

### Non-obvious gotchas
- Dev config (`config/settings.dev.yaml`) points the camera at `data/recordings/sample.mp4`.
  That path is **gitignored** and not shipped. Without it the pipeline still starts fine (the
  camera reader just fails to open and stops that thread; the API stays healthy). To get a live
  feed for demos, generate a placeholder video, e.g.:
  `mkdir -p data/recordings && .venv/bin/python -c "import cv2,numpy as np; o=cv2.VideoWriter('data/recordings/sample.mp4',cv2.VideoWriter_fourcc(*'mp4v'),20,(640,480)); [o.write(np.full((480,640,3),40,np.uint8)) for _ in range(120)]; o.release()"`
- On first pipeline start, Ultralytics downloads `yolov8n.pt` (needs network). If the download
  fails the detector logs a warning and returns empty detections — the app keeps running.
- Email validation rejects reserved TLDs like `.test`/`.local`. Use a real-looking domain
  (e.g. `@example.com`) when registering users via `/auth/register` or the dashboard.
- New registrations are always `customer` role. To reach the admin panels, promote a user:
  `.venv/bin/python scripts/promote_admin.py` or `UPDATE users SET role='admin' WHERE email='...';`.

### Lint / test
- Tests: `pytest` (config in `pyproject.toml`, 47 tests pass).
- Lint: `ruff check .` — `ruff` is configured in `pyproject.toml` but is **not** declared in
  `requirements*.txt`; the update script installs it into the venv. The repo currently has
  pre-existing ruff findings (mostly import ordering); they are unrelated to environment setup.
