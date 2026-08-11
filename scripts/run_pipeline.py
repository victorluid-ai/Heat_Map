#!/usr/bin/env python3
"""Start the camera pipeline and FastAPI server."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from _venv_python import ensure_module, project_python  # noqa: E402

ensure_module("uvicorn")
import uvicorn  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Heat Map Pipeline Server")
    parser.add_argument("--config", default=None, help="Config file path (merged over settings.yaml)")
    parser.add_argument("--env", default=None, choices=["dev", "prod"],
                        help="Shortcut for settings.dev.yaml or settings.prod.yaml merge")
    parser.add_argument("--host", default=None, help="Override API host")
    parser.add_argument("--port", type=int, default=None, help="Override API port")
    parser.add_argument("--source", default=None, help="Override first camera source")
    parser.add_argument("--dry-run", action="store_true", help="Validate config and exit")
    args = parser.parse_args()

    if args.config:
        os.environ["HEAT_MAP_CONFIG_PATH"] = args.config
    elif args.env == "dev":
        os.environ["HEAT_MAP_ENV"] = "dev"
    elif args.env == "prod":
        os.environ["HEAT_MAP_ENV"] = "prod"

    if args.source:
        os.environ["HEAT_MAP_CAMERA_SOURCE"] = args.source

    from src.utils.config import load_config
    cfg = load_config()

    if args.dry_run:
        from src.storage.database import init_db
        engine, _ = init_db(cfg["storage"]["db_url"])
        print(f"Config OK. DB at {cfg['storage']['db_url']}")
        print(f"Detection model: {cfg['detection']['model']}")
        print(f"Cameras: {[c['id'] for c in cfg['cameras'] if c.get('enabled')]}")
        engine.dispose()
        return

    host = args.host or cfg["api"]["host"]
    port = args.port or cfg["api"]["port"]
    python = project_python()
    print(f"Starting Heat Map API on {host}:{port}")
    print(f"Python: {python}")
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
