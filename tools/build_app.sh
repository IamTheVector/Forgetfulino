#!/bin/bash
# Build standalone Forgetfulino Watcher app (macOS / Linux)
# Run from library root: ./tools/build_app.sh
# Or from anywhere: /path/to/Forgetfulino/tools/build_app.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# Prefer python3 if available (typical on Linux/macOS)
if command -v python3 &>/dev/null; then
  PY=python3
  PIP=pip3
else
  PY=python
  PIP=pip
fi

echo "Building Forgetfulino Watcher (macOS/Linux)..."
$PIP install pyinstaller -q
$PIP install -r tools/requirements-watcher.txt -q

$PY -m PyInstaller tools/forgetfulino_watcher.spec

if [ $? -eq 0 ]; then
  echo ""
  echo "SUCCESS: App built at:"
  echo "  $ROOT/dist/ForgetfulinoWatcher/ForgetfulinoWatcher"
  echo ""
  echo "Run it: ./dist/ForgetfulinoWatcher/ForgetfulinoWatcher"
  echo "Or open the folder and double-click the executable."
  echo ""
  if [ -d "$ROOT/dist/ForgetfulinoWatcher" ]; then
    open "$ROOT/dist/ForgetfulinoWatcher" 2>/dev/null || xdg-open "$ROOT/dist/ForgetfulinoWatcher" 2>/dev/null || true
  fi
else
  echo "Build failed."
  exit 1
fi
