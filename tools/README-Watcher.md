# Forgetfulino Watcher & Decoder

Cross-platform GUI (Windows, macOS, Linux) for:

- **Watcher** — Monitors a sketch folder and runs the generator when `.ino` files change. Keep it running (or in the system tray) so the library always has up-to-date headers.
- **Decoder** — Paste the compressed string from the Serial Monitor and click **Decompress** to view or copy the recovered source.
- **Minimize to tray** — Collapse the window to the system tray so it does not get in the way.
- **Settings** — Configure the sketch folder to watch and the UI language (auto, English, Italian).

## Install

From the library root (or any folder where `requirements-watcher.txt` is available):

```bash
pip install -r tools/requirements-watcher.txt
```

Or install dependencies manually:

```bash
pip install customtkinter watchdog pystray Pillow
```

## Run

From the **Forgetfulino library root** (so the script finds `forgetfulino_generator.py`):

```bash
python tools/forgetfulino_watcher_app.py
```

On Windows you can double-click `forgetfulino_watcher_app.py` if Python is in PATH and `.py` is associated.

## Build standalone app (no Python required to run)

To get a **standalone app** (no Python required to run), build on the platform where you need it:

| Platform | Command | Output |
|----------|---------|--------|
| **Windows** | `tools\build_app.bat` | `dist\ForgetfulinoWatcher\ForgetfulinoWatcher.exe` |
| **macOS** | `./tools/build_app.sh` | `dist/ForgetfulinoWatcher/ForgetfulinoWatcher` (executable) |
| **Linux** | `./tools/build_app.sh` | `dist/ForgetfulinoWatcher/ForgetfulinoWatcher` (executable) |

- **Windows**: double-click `build_app.bat` or run it from a terminal. Then run `ForgetfulinoWatcher.exe` from the `dist\ForgetfulinoWatcher\` folder.
- **macOS**: open Terminal, go to the library folder (`cd path/to/Forgetfulino`), run `chmod +x tools/build_app.sh` once, then `./tools/build_app.sh`. Run the app with `./dist/ForgetfulinoWatcher/ForgetfulinoWatcher` or by opening that folder in Finder and double-clicking the executable. If macOS blocks it (“unidentified developer”), right-click the executable → Open → Open.
- **Linux**: same as macOS (`chmod +x tools/build_app.sh` then `./tools/build_app.sh`). Run `./dist/ForgetfulinoWatcher/ForgetfulinoWatcher` or add it to your application menu.

The first build installs PyInstaller and dependencies; the output is a real app (no Python needed to run it). When using the standalone app, set the **Library folder** to your Forgetfulino library path (e.g. `Documents/Arduino/libraries/Forgetfulino`) so the watcher can write the generated headers there; if the library is in a standard location it is auto-detected.

## Usage

1. **Sketch path**: Click **Browse** and choose the folder that contains your `.ino` file (or type the path).
2. **Start watcher**: Click **Start watcher**. The status will show “Watcher: running”. Any change to an `.ino` in that folder (or subfolders) will trigger the generator.
3. **Minimize**: Minimize the window to send the app to the system tray. Use the tray icon to **Show** or **Quit**.
4. **Decode**: Paste the line from the Serial Monitor (with or without the timestamp, e.g. `23:29:38.524 -> 0/"G;Bl%?…`) into the left box and click **Decompress**. The right box shows the recovered source; you can copy it from there.

Config (sketch path and language) is saved automatically (e.g. under `%APPDATA%\Forgetfulino` on Windows, `~/.config`-style on macOS/Linux).

## Launch Arduino IDE with Watcher in background (recommended)

So that you **don’t have to think about the Watcher** — you only open “Arduino” and the Watcher starts automatically and stays in the tray:

1. **First time**: Open the Watcher once (e.g. `python tools/forgetfulino_watcher_app.py`), set **Sketch folder** and **Options → Arduino IDE path**, then close it.
2. **From then on**: Use the launcher as your “Arduino IDE” shortcut:
   - **Windows**: Double-click `tools\LaunchArduinoWithForgetfulino.bat` (or create a shortcut to it and name it “Arduino IDE”). No console window; the Watcher starts in the tray (already watching) and Arduino IDE opens.
   - **macOS / Linux**: Run `python tools/launch_arduino_with_forgetfulino.py` (or add a shell script that runs it). You can put this in your dock or application menu as “Arduino IDE”.

When you launch this way, the Watcher starts with watching **on** and minimizes to the tray immediately, so you never see it unless you open it from the tray icon.

## Requirements

- Python 3.10+
- customtkinter, watchdog, pystray, Pillow (see `requirements-watcher.txt`)

All UI strings and comments are in English; the interface is available in English and Italian (auto-detected from system locale, overridable in the app).
