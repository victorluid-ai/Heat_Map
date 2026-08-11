#!/usr/bin/env python3
"""Start the Streamlit dashboard."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _venv_python import ensure_module, project_python  # noqa: E402


def main():
    ensure_module("streamlit")
    dashboard_path = Path(__file__).parent.parent / "streamlit_app.py"
    python = str(project_python())
    cmd = [python, "-m", "streamlit", "run", str(dashboard_path),
           "--server.headless", "true", "--server.port", "8501"]
    print("Starting Streamlit dashboard...")
    print(f"Python: {python}")
    raise SystemExit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
