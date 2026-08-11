#!/usr/bin/env python3
"""Process a pre-recorded video file through the pipeline."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Ingest a recorded video file")
    parser.add_argument("--file", required=True, help="Path to video file")
    parser.add_argument("--camera-id", default="recording", help="Camera ID to use")
    parser.add_argument("--config", default=None, help="Config file path")
    parser.add_argument("--env", default=None, choices=["dev", "prod"])
    args = parser.parse_args()

    if args.config:
        os.environ["HEAT_MAP_CONFIG_PATH"] = args.config
    elif args.env:
        os.environ["HEAT_MAP_ENV"] = args.env

    from src.utils.config import load_config
    cfg = load_config()

    from src.storage.database import init_db, get_session
    from src.storage.repository import upsert_camera, bulk_insert_tracking_events
    from src.detection.detector import Detector
    from src.tracking.tracker import PersonTracker
    from src.ingestion.camera_reader import CameraReader
    from src.utils.logging_config import setup_logging
    import time

    setup_logging()
    _, session_factory = init_db(cfg["storage"]["db_url"])

    with get_session(session_factory) as session:
        upsert_camera(session, args.camera_id, f"Recording: {args.file}", args.file)

    reader = CameraReader(args.camera_id, args.file)
    detector = Detector.from_config_dict(cfg["detection"])
    tracker = PersonTracker.from_config_dict(cfg["tracking"])
    reader.start()

    print(f"Processing {args.file}...")
    batch, frame_count = [], 0
    import time as time_mod
    time_mod.sleep(0.5)
    while True:
        result = reader.get_frame()
        if result is None:
            break
        ts, frame = result
        frame_count += 1
        if frame_count % 3 != 0:
            continue
        det = detector.detect(frame, args.camera_id, ts)
        tracks = tracker.update(det)
        batch.extend(tracks)
        if len(batch) >= 500:
            with get_session(session_factory) as session:
                bulk_insert_tracking_events(session, batch)
            batch.clear()
            print(f"  Processed {frame_count} frames...", end="\r")
        time_mod.sleep(0.001)

    if batch:
        with get_session(session_factory) as session:
            bulk_insert_tracking_events(session, batch)
    reader.stop()
    print(f"\nDone. Processed {frame_count} frames from {args.file}.")


if __name__ == "__main__":
    main()
