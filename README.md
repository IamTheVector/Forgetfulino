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

**Use “Arduino” and forget the Watcher:** run `tools\LaunchArduinoWithForgetfulino.bat` (Windows) or `python tools/launch_arduino_with_forgetfulino.py` (any OS) as your Arduino IDE shortcut — the Watcher starts in the tray (already watching) and Arduino IDE opens; you never have to open the Watcher manually.

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

License

MIT License

Copyright (c) 2024 IamTheVector

The software is provided "as is", without warranty of any kind.

Author

IamTheVector

GitHub
https://github.com/IamTheVector

If you find this library useful, consider giving the repository a ⭐ on GitHub.