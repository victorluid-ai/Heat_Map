# Heat Map System — Architecture

## Overview

A real-time people-tracking and heat map system for retail stores. Cameras feed into a
detection and tracking pipeline; the output is a live heat map visualising foot traffic,
plus historical analytics accessible through a Streamlit dashboard.

---

## Component Diagram

```
Camera (USB / RTSP / file)
  │
  ▼
CameraReader ──[ring buffer]──► FrameBuffer
                                     │
                                     ▼
                               Detector (YOLOv8n)
                                     │ detections
                                     ▼
                               PersonTracker (IoU)
                                     │ confirmed tracks
                          ┌──────────┴──────────┐
                          ▼                     ▼
                  HeatmapAccumulator     Repository (batch)
                  (float32 + Gaussian)    SQLite / PostgreSQL
                          │                     │
                   FastAPI /heatmap/live    /analytics/*
                          │                     │
                   Streamlit live_view    historical / analytics pages
```

---

## Module Responsibilities

| Module | Purpose |
|--------|---------|
| `src/ingestion/` | Read frames from cameras; ring buffer with lock-free latest-frame access |
| `src/detection/` | YOLOv8 person detection; graceful fallback when model absent |
| `src/tracking/` | IoU-based track assignment; dwell time accumulation |
| `src/heatmap/` | Live Gaussian-blur accumulator; historical KDE renderer |
| `src/storage/` | SQLAlchemy ORM (Camera, TrackingEvent, DwellRecord); batch write repository |
| `src/pipeline/` | Per-camera runner threads; batched DB writer; coordinator lifecycle |
| `src/api/` | FastAPI: MJPEG stream, live/historical PNG, analytics JSON |
| `src/dashboard/` | Streamlit: live view, historical heat map, analytics charts |
| `src/utils/` | Logging setup, coordinate transform (homography), image byte conversion |

---

## Data Flow

### Live pipeline (per camera, ~25 fps on CPU)

```
CameraReader.read_latest()
  → Detector.detect(frame)       # list[Detection]
  → PersonTracker.update(dets)   # list[_Track] (confirmed hits ≥ min_hits)
  → HeatmapAccumulator.add_point(cx, cy)
  → EventBus.put(PipelineEvent("track", TrackUpdate(...)))
  → [db-writer thread] bulk_insert_tracking_events() every 1 s / 500 events
```

### Live heat map request

```
GET /heatmap/live?camera_id=cam_0
  → HeatmapAccumulator.get_heatmap_image()
      = GaussianBlur(heat_matrix) → COLORMAP_JET → alpha-blend over floor plan
  → Response(PNG bytes)
```

### Historical heat map request

```
GET /heatmap/historical?start=<ts>&end=<ts>
  → get_xy_points(session, start, end)   # SQL query
  → KDERenderer.render(points)
      = accumulate to density grid → GaussianBlur → COLORMAP_JET → blend
  → Response(PNG bytes)
```

---

## Key Design Decisions

**YOLOv8n**: Chosen for CPU viability (~20-30 FPS) without GPU. The `Detector` class
falls back silently if `ultralytics` is not installed, so tests and dry-runs work without
the full ML stack.

**IoU tracker (no ReID)**: ByteTrack/DeepSORT need a re-identification network. For a
fixed-overhead camera in a retail store, simple centroid/IoU matching is sufficient and
removes the GPU dependency.

**Gaussian accumulator for live**: O(1) per-frame update (just add weight at pixel).
The blur and normalisation happen only when a frame is requested.

**SQLite + WAL mode**: Zero-setup for development; WAL pragma allows concurrent reads
during batch writes. One config-file line switches to PostgreSQL.

**StaticPool in tests**: In-memory SQLite creates an empty database per connection.
`StaticPool` forces all sessions to share one connection, so schema created by `init_db`
is visible to subsequent sessions.

---

## Configuration

All runtime settings live in `config/settings.yaml`. Key sections:

```yaml
cameras:          # list of {id, name, source, enabled}
detection:        # model path, confidence, device
tracking:         # max_age (frames), min_hits (confirmed threshold)
heatmap:          # floor_plan_path, resolution, blur_kernel_size, decay_factor
storage:          # db_url, batch_write_interval_seconds, batch_write_max_events
api:              # host, port
dashboard:        # api_base_url, refresh_interval_ms
```

Override for dev: `config/settings.dev.yaml`; for prod: `config/settings.prod.yaml`.

---

## Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Start pipeline + API (FastAPI on :8000)
python scripts/run_pipeline.py

# Start dashboard (Streamlit on :8501)
python scripts/run_dashboard.py

# Process a recorded video
python scripts/ingest_recording.py path/to/video.mp4

# Generate a historical heat map PNG
python scripts/generate_historical_heatmap.py --out data/heatmaps/output.png

# Camera calibration (pick 4 floor-plan correspondence points)
python scripts/calibrate_camera.py
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Coordinator status |
| GET | `/stream/{camera_id}` | MJPEG live stream |
| GET | `/heatmap/live` | Live heat map PNG |
| GET | `/heatmap/historical` | Historical KDE heat map PNG |
| GET | `/analytics/traffic` | Hourly event counts |
| GET | `/analytics/dwell` | Zone dwell summary |
| GET | `/docs` | Swagger UI |
