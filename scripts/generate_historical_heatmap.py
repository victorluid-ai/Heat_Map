#!/usr/bin/env python3
"""Generate a high-quality KDE heat map from the database for a given time range."""
import argparse
import os
import sys
import time
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Generate historical heat map from DB")
    parser.add_argument("--start", type=float, default=None, help="Start timestamp (unix)")
    parser.add_argument("--end", type=float, default=None, help="End timestamp (unix)")
    parser.add_argument("--camera-id", default=None)
    parser.add_argument("--output", default="data/heatmaps/output.png")
    parser.add_argument("--config", default=None, help="Config file path")
    parser.add_argument("--env", default=None, choices=["dev", "prod"])
    args = parser.parse_args()

    if args.config:
        os.environ["HEAT_MAP_CONFIG_PATH"] = args.config
    elif args.env:
        os.environ["HEAT_MAP_ENV"] = args.env

    from src.utils.config import load_config
    cfg = load_config()

    now = time.time()
    start = args.start or (now - 86400)
    end = args.end or now

    from src.storage.database import init_db, get_session
    from src.storage.repository import get_xy_points
    from src.heatmap.floor_plan import FloorPlan
    from src.heatmap.kde_renderer import KDERenderer

    _, session_factory = init_db(cfg["storage"]["db_url"])
    with get_session(session_factory) as session:
        points = get_xy_points(session, start, end, args.camera_id)

    print(f"Got {len(points)} tracking points")
    floor = FloorPlan(cfg["heatmap"]["floor_plan_path"], tuple(cfg["heatmap"]["resolution"]))
    renderer = KDERenderer(floor)
    image = renderer.render(points)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(args.output, image)
    print(f"Heat map saved to {args.output}")


if __name__ == "__main__":
    main()
