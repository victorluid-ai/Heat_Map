"""Pick the project venv interpreter when the active Python lacks dependencies."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def project_python() -> Path:
    return VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)


def ensure_module(module: str) -> None:
    if importlib.util.find_spec(module) is not None:
        return
    if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        print(f"'{module}' no está en {sys.executable}")
        print(f"Reiniciando con el venv del proyecto: {VENV_PYTHON}")
        result = subprocess.run([str(VENV_PYTHON), *sys.argv])
        raise SystemExit(result.returncode)
    print(f"Falta el módulo '{module}'. Activa el entorno virtual e instala dependencias:")
    print(r"  .\.venv\Scripts\Activate.ps1")
    print(r"  pip install -r requirements.txt")
    raise SystemExit(1)
