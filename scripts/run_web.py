#!/usr/bin/env python3
"""Launch the TypeScript web dashboard (Vite) using the project Node toolchain."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def main() -> int:
    if not WEB.is_dir():
        print(f"Web app not found at {WEB}", file=sys.stderr)
        return 1

    npm = shutil.which("npm")
    if not npm:
        print("npm is required to run the web dashboard.", file=sys.stderr)
        return 1

    if not (WEB / "node_modules").is_dir():
        print("Installing web dependencies…")
        install = subprocess.run([npm, "install"], cwd=WEB, check=False)
        if install.returncode != 0:
            return install.returncode

    env = os.environ.copy()
    return subprocess.call([npm, "run", "dev", "--", "--host", "0.0.0.0"], cwd=WEB, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
