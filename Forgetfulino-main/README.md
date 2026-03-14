# Forgetfulino

Forgetfulino is an Arduino library and toolchain that **embeds your sketch source code into the firmware** and lets you **recover it later via Serial**.  
It is designed for the real‑world situation where the board still works, but the original `.ino` files are lost or out of sync.

This repository contains two top‑level folders:

- **Forgetfulino-main/** – the **Arduino library** folder (this is the only folder that must be installed under `Arduino/libraries`).  
- **extension build/** – the full development project for the Arduino IDE 2.x extension (TypeScript sources, config files, etc.). This **is not part of the Arduino library ZIP**.

The sections below describe how the library and the extension work together.

------------------------------------------------------------

## 1. Features

- Stores the sketch source code inside firmware flash memory (PROGMEM).
- Zero RAM usage: source is read directly from flash.
- Handles **multiple `.ino` and `.cpp` files** in the sketch folder.
- Optional **Base85 compression** to reduce flash usage.
- Optional automatic **template injection** into new sketches.
- Optional automatic **header generation on save** via the IDE extension.
- Retrieval and **decode** through the Arduino IDE 2.x extension.
- Annotates each `#include` in the recovered source with the **library version** (when available).

------------------------------------------------------------

## 2. Installation (Arduino library)

### 2.1 Arduino Library Manager (planned)

When Forgetfulino is registered in the Arduino Library Manager, the library root is:

`Forgetfulino-main`

1. Open Arduino IDE.  
2. Go to `Sketch → Include Library → Manage Libraries…`.  
3. Search for **Forgetfulino**.  
4. Click **Install**.

### 2.2 Manual Installation (ZIP)

1. Download this repository as ZIP.  
2. Extract it.  
3. Copy the `Forgetfulino-main` folder into your Arduino `libraries` folder and (optionally) rename it to `Forgetfulino`.  
4. Restart Arduino IDE.

Typical `libraries` locations:

- **Windows**: `Documents/Arduino/libraries/`  
- **macOS**: `~/Documents/Arduino/libraries/`  
- **Linux**: `~/Arduino/libraries/`

------------------------------------------------------------

## 3. Folder layout (Arduino side)

Inside `Arduino/libraries/Forgetfulino` (installed library) you will find:

- `library.properties` – library metadata (name, version, URL, etc.).  
- `src/` – Forgetfulino library sources and generated headers.  
- `examples/` – example sketches demonstrating how to use Forgetfulino.  
- `extensions/` – packaged Arduino IDE 2.x extension (`.vsix`) plus a `README-Extensions.txt` explaining how to install it.  
- `README.md` – this document.

The `.vsix` file in `extensions/` is **lightweight** and safe to ship with the library.  
The **full extension development project** (with `node_modules`, TypeScript sources, etc.) lives in the separate `extension build/` folder at the repository root and is **not** part of the Arduino library.

------------------------------------------------------------

## 4. Arduino IDE 2.x extension

The extension runs inside **Arduino IDE 2.x** (VS Code‑style extensions) and automates Forgetfulino’s workflow.

### 4.1 Install the VSIX

1. Locate the VSIX file in `extensions/`, for example:  
   `extensions/forgetfulino-arduino-ide-extension-0.0.1.vsix`  
2. Open **Arduino IDE 2.x**.  
3. Open the **Extensions** view.  
4. Choose **“Install from VSIX…”** and select the Forgetfulino `.vsix` file.  
5. Restart Arduino IDE if requested.

### 4.2 What the extension does

After installation, the Forgetfulino extension:

- can **auto‑generate headers on save** (`forgetfulino.autoGenerateOnSave`),  
- can **auto‑inject** a Forgetfulino template into new sketches (`forgetfulino.autoInjectTemplate`),  
- provides commands and **right‑click context‑menu entries** for:
  - generating headers,
  - toggling comment inclusion in the dump,
  - toggling auto‑generate and auto‑inject,
  - decoding compressed dumps,
- annotates each `#include` in the recovered source with the **library version** (when available).

You can access the commands from the **command palette** or by **right‑clicking** inside a `.ino`, `.cpp`, or `.c` file in the editor.  
In your own documentation or videos you can add screenshots of the context menu here.

------------------------------------------------------------

## 5. Using Forgetfulino from the IDE

### 5.1 Generate the headers (manual and automatic)

With the extension installed:

- **Manual generation**  
  - Right‑click inside a `.ino`, `.cpp`, or `.c` file.  
  - Choose **“Forgetfulino: Generate headers”**.  
  - The extension scans the current sketch folder, sanitizes the source, and generates:
    - `forgetfulino_source_data.h` (plain source),  
    - `forgetfulino_compressed.h` (Base85‑compressed source, split into multiple PROGMEM chunks).

- **Automatic generation on save**  
  - Toggle via the context menu:
    - **“Forgetfulino: Activate auto‑generate on save”**  
    - **“Forgetfulino: Deactivate auto‑generate on save”**  
  - When enabled, every time you save a sketch file (`.ino`, `.cpp`, `.c`) the headers are regenerated.

### 5.2 Auto‑inject template into new sketches

The extension can automatically inject a Forgetfulino‑ready template into **brand‑new sketches** (empty or default Arduino skeleton):

- Commands:
  - **“Forgetfulino: Activate auto‑inject template”**  
  - **“Forgetfulino: Deactivate auto‑inject template”**

When enabled, on the first save of a new `.ino`, the extension inserts:

- `#include <Forgetfulino.h>`  
- `Serial.begin(115200);`  
- `Forgetfulino.begin();`  
- a call to `Forgetfulino.dumpCompressed();` inside `setup()`.

This guarantees that every new project starts with Forgetfulino already wired in, reducing the risk of forgetting the include or the initialization.

### 5.3 Include or strip comments from the dump

You can choose whether comments in your sketch are embedded in the stored source:

- **“Forgetfulino: Click to include comments in dump”**  
- **“Forgetfulino: Click to strip comments from dump”**

When comments are stripped, the embedded source is smaller but still fully compilable.

### 5.4 Decode a compressed dump

When you call `Forgetfulino.dumpCompressed()` in your sketch, the library prints a long Base85 string to the Serial Monitor.

To recover the original source:

1. Select the Base85 line in the Serial Monitor (or paste it into a text editor tab inside Arduino IDE).  
2. Run **“Forgetfulino: Decode compressed dump”** from the context menu or command palette.  
3. The extension:
   - strips any Serial Monitor timestamp prefix (e.g. `HH:MM:SS.mmm ->`),  
   - decodes the Base85 string to the original UTF‑8 source,  
   - **adds a trailing comment to each `#include`** with the detected library version, when the library has a `library.properties` in the sketchbook.

The recovered code opens in a new editor tab, ready to be reviewed or saved as a new sketch.

------------------------------------------------------------

## 6. Library API (overview)

The core API is provided by the global `Forgetfulino` instance:

- **`Forgetfulino.begin()`** – optional initialization, called once in `setup()`.  
- **`Forgetfulino.dumpSource()`** – prints the embedded plain‑text source to `Serial`.  
- **`Forgetfulino.dumpCompressed()`** – prints the Base85‑compressed source to `Serial` (recommended when using the IDE decoder).  
- **`Forgetfulino.hasSourceData()`** – returns `true` if embedded source code is available.  
- **`Forgetfulino.getSourceSize()`** – returns the size (in bytes) of the embedded plain source.  
- **`Forgetfulino.getSketchName()`** – returns the stored sketch name.

The exact set may evolve; refer to the header `Forgetfulino.h` for the definitive declarations.

------------------------------------------------------------

## 7. Basic usage example

Minimal example using the compressed dump:

```cpp
#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
  delay(2000);

  Forgetfulino.begin();

  // Typical one-shot dump of the compressed source.
  // You can later decode it with the “Decode compressed dump” command.
  Forgetfulino.dumpCompressed();
}

void loop() {
  // Your application code here…
}
```

If you prefer the plain text dump, you can use `Forgetfulino.dumpSource()` instead (with the appropriate header generated).

------------------------------------------------------------

## 8. Acknowledgements

- **lunastrod (Reddit)** – for making me think about the importance of precise **library versioning**. Thanks to this, Forgetfulino now annotates each `#include` in the recovered source with the corresponding library version (when available), so you can reliably recreate the original build environment.
- **kahveciderin (Reddit)** – for suggesting a more **memory‑oriented approach** and highlighting how easily a missing `#include` or forgotten library could prevent the source from ever being shown. This led to automatic Forgetfulino injection into new Arduino sketches and a more robust, fail‑safe workflow.
- **J-M-L (Arduino community)** – for pushing for proper **multi‑file sketch support**. Forgetfulino now handles multiple `.ino` and `.cpp` files in a sketch folder, preserving their order and boundaries in the embedded source.
- **robtillaart (Arduino Forum)** – for the suggestion to use **compression**. Forgetfulino now offers an optional Base85‑compressed representation of the source, significantly reducing flash usage when needed.
- **ptillisch (Arduino Team, Arduino Forum)** – for pointing out the possibility of implementing an **IDE extension**. The dedicated Arduino IDE 2.x extension for Forgetfulino has been a real game changer for usability and automation.

------------------------------------------------------------

## 9. License

MIT License  
Copyright (c) 2024 IamTheVector

The software is provided "as is", without warranty of any kind.

Author: **IamTheVector**  
GitHub: <https://github.com/IamTheVector>

If you find this library useful, consider giving the repository a ⭐ on GitHub.

# Forgetfulino

Forgetfulino is an Arduino library that embeds the original sketch source code directly into the compiled firmware and allows retrieving it later through the Serial interface.

This makes it possible to recover the exact code uploaded to a board even if the original sketch file is lost.

------------------------------------------------------------

## Features

- Stores the sketch source code inside firmware flash memory
- Zero RAM usage (data is read directly from flash)
- Designed for small sketches and prototype projects
- Simple integration with Arduino sketches
- Retrieval through Serial interface

------------------------------------------------------------

## Installation

### Arduino Library Manager (planned)

1. Open Arduino IDE
2. Go to:

Sketch → Include Library → Manage Libraries

3. Search for **Forgetfulino**
4. Click **Install**

------------------------------------------------------------

### Manual Installation (ZIP)

1. Download this repository as ZIP
2. Open Arduino IDE
3. Go to:

Sketch → Include Library → Add .ZIP Library

4. Select the downloaded ZIP file

------------------------------------------------------------

### Manual Installation (folder)

1. Clone or download this repository
2. Copy the `Forgetfulino` folder into your Arduino libraries directory.

Typical locations:

Windows  
Documents/Arduino/libraries/

macOS  
~/Documents/Arduino/libraries/

Linux  
~/Arduino/libraries/

3. Restart Arduino IDE

------------------------------------------------------------

## Watcher & Decoder app (Windows, macOS, Linux)

A small desktop app lets you:

- **Watcher**: Monitor a sketch folder and auto-run the generator when `.ino` files change (so the library does not complain about missing headers).
- **Decoder**: Paste the compressed string from the Serial Monitor and decompress to view or copy the recovered source.
- **System tray**: Minimize to the tray so it stays out of the way.
- **Configurable** sketch path and **multilingual** interface (EN/IT, auto-detected).

Install and run:

```bash
pip install -r tools/requirements-watcher.txt
python tools/forgetfulino_watcher_app.py
```

To get a **standalone app** (no Python needed to run): **Windows** → `tools\build_app.bat` → `dist\ForgetfulinoWatcher\ForgetfulinoWatcher.exe`; **macOS / Linux** → `chmod +x tools/build_app.sh` then `./tools/build_app.sh` → `dist/ForgetfulinoWatcher/ForgetfulinoWatcher`. See `tools/README-Watcher.md` for details.

**Use "Arduino" and forget the Watcher:** run `tools\LaunchArduinoWithForgetfulino.bat` (Windows) or `python tools/launch_arduino_with_forgetfulino.py` (any OS) as your Arduino IDE shortcut — the Watcher starts in the tray (already watching) and Arduino IDE opens; you never have to open the Watcher manually.

------------------------------------------------------------

# Usage

## 1. Generate the source header

Before compiling your sketch, run the Python generator inside your sketch folder.

Example:

cd /path/to/your/sketch

python /path/to/Arduino/libraries/Forgetfulino/tools/forgetfulino_generator.py

This script reads the `.ino` file and generates the header:

forgetfulino_source_data.h

The generated file is written to:

/path/to/Arduino/libraries/Forgetfulino/src/

------------------------------------------------------------

## 2. Include the library

Add the library to your sketch:

```cpp
#include <Forgetfulino.h>

void setup() {

  Serial.begin(115200);
  delay(2000);

  if (Forgetfulino.hasSourceData()) {

    Serial.println("Embedded source found!");
    Serial.print("Size: ");
    Serial.print(Forgetfulino.getSourceSize());
    Serial.println(" bytes");

    Forgetfulino.dumpSource();

  } else {

    Serial.println("No source data found.");
    Serial.println("Run the generator before compiling.");

  }

}

void loop() {

}


3. Upload the sketch

Compile and upload the sketch normally using the Arduino IDE.

The firmware will now contain the original source code.

Example Output

Opening the Serial Monitor may show something similar to:

+-----------------------------------------+
|      FORGETFULINO SKETCH SOURCE         |
+-----------------------------------------+

File: YourSketch.ino
Size: 1234 bytes

-------------------------------------------

// File: YourSketch.ino
// Date: 2024-01-15 14:30:45

#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
}

void loop() {
}
API Reference

hasSourceData()

Returns true if embedded source code is available.

getSourceSize()

Returns the size of the embedded source code in bytes.

getSketchName()

Returns the stored sketch name.

dumpSource()

Prints the stored source code to the Serial interface.

begin()

Optional initialization function.

How It Works

The Python generator reads the .ino sketch file and converts the source code into a C array stored in flash memory.

The generator produces a header file:

forgetfulino_source_data.h

This file is compiled together with the firmware.

At runtime, the library reads the data directly from flash memory and prints it through Serial.

The source code is never copied into RAM.

File Structure
Arduino/libraries/Forgetfulino/

library.properties
src/
    Forgetfulino.h
    Forgetfulino.cpp
    forgetfulino_source_data.h (generated automatically)
tools/
    forgetfulino_generator.py
Requirements

Python 3.x for the generator script

Arduino IDE 1.8 or newer

An Arduino compatible board

Troubleshooting

"No source data available"

Run the generator before compiling.

Verify that the file:

forgetfulino_source_data.h

exists inside the library src folder.

Compilation errors

Check that:

the library is installed in the correct directory

the Arduino IDE has been restarted

no duplicate versions of the library exist

Contributing

Contributions and suggestions are welcome.

Feel free to submit issues or pull requests.

------------------------------------------------------------

## Acknowledgements

- **lunastrod (Reddit)** – For inspiring the focus on precise library versioning. Forgetfulino now annotates 
each `#include` in the recovered source with the corresponding library version (when available), so you can reliably recreate the original build environment.
- **kahveciderin (Reddit)** – For pushing toward a more memory‑oriented design and highlighting how easily a 
missing `#include` or forgotten library could prevent the source from ever being shown. This led to automatic Forgetfulino injection into new Arduino sketches and a more robust, fail‑safe workflow.
- **J-M-L (Arduino community)** – For motivating multi‑file sketch support. Forgetfulino now handles 
multiple `.ino` and `.cpp` files in a sketch folder, preserving their order and boundaries in the embedded source.
- **robtillaart (Arduino Forum)** – For suggesting the use of compression. Forgetfulino now offers an optional
 Base85‑compressed representation of the source, significantly reducing flash usage when needed.
- **ptillisch (Arduino Team, Arduino Forum)** – For pointing out the possibility of implementing an IDE 
extension. The dedicated Arduino IDE 2.x extension for Forgetfulino has been a real game changer for usability and automation.

------------------------------------------------------------

License

MIT License

Copyright (c) 2024 IamTheVector

The software is provided "as is", without warranty of any kind.

Author

IamTheVector

GitHub
https://github.com/IamTheVector

If you find this library useful, consider giving the repository a ⭐ on GitHub.