#!/bin/bash

echo "========================================"
echo "    FORGETFULINO WATCHER - SETUP"
echo "========================================"
echo ""
echo "This script starts the automatic monitoring"
echo "of your Arduino sketches."
echo ""
read -p "Press Enter to continue..."

clear
echo "[1/6] Searching for a valid Python installation..."

PYTHON_CMD=""

# Common Python paths on macOS/Linux
if command -v python3 &> /dev/null; then
    PYTHON_CMD=$(which python3)
    echo "Found Python: $PYTHON_CMD"
elif command -v python &> /dev/null; then
    PYTHON_CMD=$(which python)
    echo "Found Python: $PYTHON_CMD"
else
    echo "Python not found!"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

read -p "Press Enter to continue..."

clear
echo "[2/6] Checking pip..."
$PYTHON_CMD -m pip --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Pip not found. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    $PYTHON_CMD /tmp/get-pip.py --user
fi
echo "Pip OK"
read -p "Press Enter to continue..."

clear
echo "[3/6] Checking watchdog..."
$PYTHON_CMD -c "from watchdog.observers import Observer" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "Watchdog not found. Installing..."
    $PYTHON_CMD -m pip install watchdog --user
    if [ $? -ne 0 ]; then
        echo "ERROR: Unable to install watchdog"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo "Watchdog installed successfully!"
else
    echo "Watchdog already installed"
fi
read -p "Press Enter to continue..."

clear
echo "[4/6] Calculating sketch path..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKETCH_PATH="$(cd "$SCRIPT_DIR/../.." && pwd)"
echo "Sketch folder: $SKETCH_PATH"

if [ ! -d "$SKETCH_PATH" ]; then
    echo "ERROR: Sketch folder not found!"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "OK"
read -p "Press Enter to continue..."

clear
echo "[5/6] Checking generator..."
GENERATOR="$SCRIPT_DIR/tools/forgetfulino_generator.py"
if [ ! -f "$GENERATOR" ]; then
    echo "ERROR: Generator not found!"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "OK"
read -p "Press Enter to continue..."

clear
echo "[6/6] Starting watcher..."
echo ""
echo "========================================"
echo "    FORGETFULINO WATCHER - RUNNING"
echo "========================================"
echo ""
echo "Monitored folder: $SKETCH_PATH"
echo ""
echo "You can now edit your sketches normally."
echo "Every time you save, the .h file will be generated."
echo ""
echo "To stop, press Ctrl+C"
echo ""
echo "========================================"
echo ""

$PYTHON_CMD "$GENERATOR" --watch "$SKETCH_PATH"

echo ""
echo "Watcher stopped."
read -p "Press Enter to exit..."