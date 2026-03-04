# Forgetfulino

Forgetfulino is an Arduino library that embeds the original sketch source code directly into the compiled firmware and allows retrieving it later through the Serial interface.

This makes it possible to recover the exact code uploaded to a board even if the original sketch file is lost.

------------------------------------------------------------

## Features

- Zero RAM usage, reads directly from flash memory
- PROGMEM support for Arduino AVR
- Compatible with multiple architectures:
  - AVR
  - ESP8266
  - ESP32
  - SAMD
  - RP2040
- Simple integration, include the library and call one function

------------------------------------------------------------

## Installation

### Via Arduino Library Manager (soon)

1. Open Arduino IDE
2. Go to:

Sketch → Include Library → Manage Libraries

3. Search for "Forgetfulino"
4. Click Install

------------------------------------------------------------

### Manual Installation

1. Download this repository as ZIP
2. In Arduino IDE go to:

Sketch → Include Library → Add .ZIP Library

3. Select the downloaded ZIP file

------------------------------------------------------------

### Manual Installation (alternative)

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

# Usage

## 1. Generate the source header

Before compiling your sketch, run the Python generator inside your sketch folder.

Example:

cd /path/to/your/sketch

python /path/to/Arduino/libraries/Forgetfulino/tools/forgetfulino_generator.py

This will generate the file:

forgetfulino_source_data.h

directly inside the library source folder:

/path/to/Arduino/libraries/Forgetfulino/src/forgetfulino_source_data.h

------------------------------------------------------------

## 2. Add the library to your sketch

Include the library in your Arduino sketch.

#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
  delay(2000);

  if (Forgetfulino.hasSourceData()) {
    Serial.println("Embedded source found!");
    Serial.print("Size: ");
    Serial.print(Forgetfulino.getSourceSize());
    Serial.println(" bytes");

    // Dump the entire source code
    Forgetfulino.dumpSource();
  } else {
    Serial.println("No source data found!");
    Serial.println("Run the generator before compiling.");
  }
}

void loop() {
  // Your code here
}


3. Compile and upload

Upload the sketch normally.

The firmware will now contain the original source code.


Example Output

When opening the Serial Monitor you will see something similar to:

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

-------------------------------------------
API Reference

hasSourceData()

Returns true if embedded source code is available.

getSourceSize()

Returns the size of the embedded source code in bytes.

getSketchName()

Returns the name of the stored sketch.

dumpSource()

Prints the entire stored source code to Serial.

begin()

Optional initialization function.

How It Works

The Python generator reads the .ino sketch file.

The source code is converted into a C array stored in flash memory.

The generated header file is saved inside the library src folder.

At runtime, dumpSource() reads directly from flash memory and prints the code through Serial.

No RAM is used, the source remains stored entirely in flash memory.

File Structure

Arduino/libraries/Forgetfulino/

├── library.properties
├── src/
│ ├── Forgetfulino.h
│ ├── Forgetfulino.cpp
│ └── forgetfulino_source_data.h (generated automatically)
└── tools/
└── forgetfulino_generator.py

Requirements

Python 3.x for the generator script

Arduino IDE 1.8 or newer

Any Arduino compatible board

Supported architectures include AVR, ESP8266, ESP32, ARM and RP2040.

Troubleshooting

"No source data available"

Run the generator before compiling.

Make sure the generator completed successfully.

Verify that the file:

forgetfulino_source_data.h

exists inside the library src folder.

Compilation errors

Check that:

the library is installed in the correct directory

the Arduino IDE has been restarted

no duplicate versions of the library exist

Contributing

Contributions are welcome. Feel free to submit a Pull Request.

License

MIT License

Copyright (c) 2024 IamTheVector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files to deal in the Software
without restriction, including use, copy, modify, merge, publish, distribute,
sublicense, and sell copies of the Software.

The software is provided "as is", without warranty of any kind.

Author

IamTheVector

GitHub: @IamTheVector

Support

If you find this library useful, consider giving the repository a star on GitHub.
