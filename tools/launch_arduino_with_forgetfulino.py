#!/usr/bin/env python3
"""
Launcher: avvia il Watcher Forgetfulino in background (tray, già attivo) e poi Arduino IDE.
L'utente può usare questo script come "Arduino IDE": un solo clic apre l'IDE e il Watcher
è già attivo in tray senza doverci pensare.

Uso: python launch_arduino_with_forgetfulino.py
     oppure (Windows senza console): LaunchArduinoWithForgetfulino.bat
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def _config_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    else:
        base = Path(os.path.expanduser("~"))
    return base / "Forgetfulino" / "watcher_config.json"


def _load_config() -> dict:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main() -> int:
    tools_dir = Path(__file__).resolve().parent
    watcher_script = tools_dir / "forgetfulino_watcher_app.py"
    if not watcher_script.exists():
        sys.stderr.write(f"Watcher script not found: {watcher_script}\n")
        return 1

    config = _load_config()
    ide_path = (config.get("arduino_ide_path") or "").strip()

    # 1) Avvia il Watcher con --start-watching e --minimize (va in tray, già attivo)
    try:
        subprocess.Popen(
            [sys.executable, str(watcher_script), "--start-watching", "--minimize"],
            cwd=tools_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception as e:
        sys.stderr.write(f"Failed to start Watcher: {e}\n")
        # Continua comunque con l'IDE se possibile

    time.sleep(1.5)

    # 2) Avvia Arduino IDE
    if ide_path and os.path.isfile(ide_path):
        try:
            subprocess.Popen(
                [ide_path],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
        except Exception as e:
            sys.stderr.write(f"Failed to start Arduino IDE: {e}\n")
            return 1
    else:
        sys.stderr.write(
            "Arduino IDE path not set or invalid. Open Forgetfulino Watcher once, set the path in Options, then use this launcher.\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
