# Forgetfulino

Arduino library that automatically embeds the sketch source code into the firmware and allows retrieving it via Serial.

## Features

- Zero RAM usage - reads directly from flash
- Works with sketches of any size
- PROGMEM support for Arduino AVR
- Compatible with ESP8266, ESP32, SAMD, RP2040
- Simple - launch the python script,include the library, upload

## Installation

1. Copy the `Forgetfulino` folder to your Arduino libraries folder:
   - Windows: `Documents/Arduino/libraries/`
   - macOS: `~/Documents/Arduino/libraries/`
   - Linux: `~/Arduino/libraries/`
2. Restart Arduino IDE

## Usage

### 1. Generate the source header

For each sketch, run the generator in your sketch folder:

```bash
python /path/to/Forgetfulino/tools/forgetfulino_generator.py

2. Add to your sketch
cpp
#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  if (Forgetfulino.hasSourceData()) {
    Serial.println("Embedded source found!");
    Forgetfulino.dumpSource();
  }
}

void loop() {}


3. Copy the generated file
After generation, copy forgetfulino_source_data.h to:

text
Arduino/libraries/Forgetfulino/src/



4. Compile and upload
Output example
text
+-----------------------------------------+
|      FORGETFULINO SKETCH SOURCE         |
+-----------------------------------------+
File: YourSketch.ino
Size: 1234 bytes
-------------------------------------------

[ ... your code ... ]

-------------------------------------------


Requirements
Python 3.x for the generator

Arduino IDE 1.8.x or higher




License
MIT License

text

## 📋 **COME UPLOADARE SU GITHUB**

1. **Crea una nuova repository** su GitHub chiamata `Forgetfulino`

2. **Struttura locale prima dell'upload**:
YourLocalFolder/
└── Forgetfulino/
├── library.properties
├── README.md
├── src/
│ ├── Forgetfulino.h
│ └── Forgetfulino.cpp
└── tools/
└── forgetfulino_generator.py


