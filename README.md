# Forgetfulino

Arduino library that automatically embeds the sketch source code into the firmware and allows retrieving it via Serial.

## Features

- Zero RAM usage - reads directly from flash memory
- Works with sketches of any size - no memory limitations
- PROGMEM support for Arduino AVR
- Compatible with multiple architectures: AVR, ESP8266, ESP32, SAMD, RP2040
- Simple to use - just include the library and call one function

## Installation


### Manual Installation
1. Download this repository as ZIP
2. In Arduino IDE: Sketch -> Include Library -> Add .ZIP Library
3. Select the downloaded ZIP file

### Manual Installation (alternative)
1. Clone or download this repository
2. Copy the `Forgetfulino` folder to your Arduino libraries folder:
   - Windows: `Documents/Arduino/libraries/`
   - macOS: `~/Documents/Arduino/libraries/`
   - Linux: `~/Arduino/libraries/`
3. Restart Arduino IDE

## Usage

### 1. Generate the source header

Before compiling your sketch, run the Python generator in your sketch folder:
cd /path/to/your/sketch/folder
python /path/to/Forgetfulino/tools/forgetfulino_generator.py

text

This creates `forgetfulino_source_data.h` in your sketch folder.

### 2. Copy to library (first time only)
cp forgetfulino_source_data.h /path/to/Arduino/libraries/Forgetfulino/src/

text

### 3. Add to your sketch


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
4. Compile and upload
The source code is now embedded in your firmware!

Example Output
When you open the Serial Monitor, you'll see:

text
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
  // ... rest of your code ...
}

void loop() {
  // ... your code ...
}

-------------------------------------------
API Reference
Method	Description
hasSourceData()	Returns true if source code is embedded
getSourceSize()	Returns the size of the embedded source in bytes
getSketchName()	Returns the sketch filename
dumpSource()	Prints the entire source code to Serial
begin()	Initializes the library (optional)
How It Works
The Python generator reads your .ino sketch file

It converts the source code into a C array stored in PROGMEM (flash memory)

The generated header file is included in the library

At runtime, dumpSource() reads directly from flash and prints to Serial

No RAM is used - the source stays in flash memory

Requirements
Python 3.x for the generator script

Arduino IDE 1.8.x or higher

Any Arduino-compatible board (AVR, ESP, ARM, etc.)

Troubleshooting
"No source data available" error
Run the generator before compiling

Make sure forgetfulino_source_data.h is in the library src folder

Check that the file was generated correctly

Compilation errors
Verify that the library is installed in the correct folder

Restart Arduino IDE after installation

Check for multiple versions of the library

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
MIT License

Copyright (c) 2024 IamTheVector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author
IamTheVector
GitHub: @IamTheVector

Support
If you find this library useful, please give it a star on GitHub!
