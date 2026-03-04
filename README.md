# Forgetfulino

Forgetfulino is an Arduino library that embeds the original sketch source code directly inside the compiled firmware and allows retrieving it later through the Serial interface.

This allows you to recover the exact code uploaded to the board even if the original sketch file is lost.

------------------------------------------------------------

## Key Features

- Zero RAM usage, source is read directly from flash memory
- Works with sketches of any size
- PROGMEM support on AVR architectures
- Compatible with multiple platforms:
  - AVR (Arduino Uno, Mega, Nano)
  - ESP8266
  - ESP32
  - SAMD
  - RP2040
- Simple integration, include the library and call one function

------------------------------------------------------------

## How It Works

1. A generator script reads the .ino sketch file.
2. The source code is converted into a C array stored in flash memory.
3. The generated header is compiled together with the firmware.
4. At runtime the library reads the data from flash and prints it through Serial.

The source never occupies RAM and remains stored in firmware memory.

------------------------------------------------------------

# Installation

## Install from ZIP

1. Download the repository as ZIP
2. Open Arduino IDE
3. Go to:

Sketch → Include Library → Add .ZIP Library

4. Select the downloaded archive

------------------------------------------------------------

## Manual Installation

1. Clone or download the repository
2. Copy the folder:

Forgetfulino

into your Arduino libraries directory.

Typical paths:

Windows
Documents/Arduino/libraries/

macOS
~/Documents/Arduino/libraries/

Linux
~/Arduino/libraries/

3. Restart Arduino IDE

------------------------------------------------------------

# Usage

## Step 1 - Generate the source header

Before compiling the sketch, run the generator script inside the sketch folder.

Example:

python /path/to/Forgetfulino/tools/forgetfulino_generator.py

This will create the file:

forgetfulino_source_data.h

inside the sketch directory.

------------------------------------------------------------

## Step 2 - Copy the generated header

Copy the generated file into the library source folder:

Arduino/libraries/Forgetfulino/src/

This step is required only the first time or whenever the sketch changes.

------------------------------------------------------------

## Step 3 - Include the library

Add Forgetfulino to your sketch:

#include <Forgetfulino.h>

void setup()
{
  Serial.begin(115200);
  delay(2000);

  if (Forgetfulino.hasSourceData())
  {
    Serial.println("Embedded source found");
    Serial.print("Size: ");
    Serial.print(Forgetfulino.getSourceSize());
    Serial.println(" bytes");

    Forgetfulino.dumpSource();
  }
  else
  {
    Serial.println("No source data available");
    Serial.println("Run the generator before compiling");
  }
}

void loop()
{
}

------------------------------------------------------------

## Step 4 - Compile and Upload

Upload the sketch normally.

The firmware will now contain the original source code.

Opening the Serial Monitor will allow retrieving the full sketch.

------------------------------------------------------------

# Example Serial Output

+-----------------------------------------+
|      FORGETFULINO SKETCH SOURCE         |
+-----------------------------------------+

File: ExampleSketch.ino
Size: 1234 bytes

-------------------------------------------

// File: ExampleSketch.ino
// Date: 2024-01-15 14:30:45

#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
}

void loop() {
}

-------------------------------------------

------------------------------------------------------------

# API Reference

hasSourceData()

Returns true if embedded source data exists.

getSourceSize()

Returns the size of the stored source code in bytes.

getSketchName()

Returns the name of the embedded sketch file.

dumpSource()

Prints the entire stored source code to Serial.

begin()

Optional initialization function.

------------------------------------------------------------

# Requirements

- Python 3.x for the generator script
- Arduino IDE 1.8 or newer
- Any Arduino compatible board

Supported architectures include AVR, ESP8266, ESP32, ARM and RP2040.

------------------------------------------------------------

# Troubleshooting

"No source data available"

Run the generator script before compiling the sketch.

Verify that the file:

forgetfulino_source_data.h

exists inside the library src folder.

------------------------------------------------------------

Compilation errors

Check that:

- the library is installed in the correct directory
- the Arduino IDE has been restarted after installation
- no duplicate versions of the library exist

------------------------------------------------------------

# Contributing

Pull requests and improvements are welcome.

------------------------------------------------------------

# License

MIT License

Copyright (c) 2024 IamTheVector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files to deal in the Software
without restriction, including use, copy, modify, merge, publish, distribute,
sublicense, and sell copies of the Software.

The software is provided "as is", without warranty of any kind.

------------------------------------------------------------

# Author

IamTheVector

GitHub
https://github.com/IamTheVector

------------------------------------------------------------

# Support

If you find this project useful, consider starring the repository on GitHub.
