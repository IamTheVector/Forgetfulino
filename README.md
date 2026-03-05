# Forgetfulino

Forgetfulino is an Arduino library that embeds the original sketch source code directly into the compiled firmware and allows retrieving it later through the Serial interface.

This makes it possible to recover the exact code uploaded to a board even if the original sketch file is lost.

------------------------------------------------------------

## Features

- Stores the sketch source code inside firmware flash memory
- Zero RAM usage (data is read directly from flash)
- Designed for small sketches and prototype projects
- Simple integration with Arduino sketches
- Automatic source generation using a file watcher
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

# Usage

## 1. Start the Forgetfulino watcher

Forgetfulino includes a **watcher script** that automatically generates the source header every time your `.ino` file changes.

This avoids running the generator manually before every compilation.

### Windows

Run:


tools\watcher.bat


### Linux / macOS

Run:


./tools/watcher.sh


The watcher will monitor your sketch and automatically regenerate:


forgetfulino_source_data.h


whenever the `.ino` file is modified.

Keep the watcher running while you develop your sketch.

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
    Serial.println("Make sure the watcher is running.");

  }

}

void loop() {

}
```



3. Compile and upload

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

The Forgetfulino watcher monitors your .ino file.

When the sketch changes:

The watcher reads the .ino source file

The source code is converted into a C array

The array is stored in a generated header file:

forgetfulino_source_data.h

This file is compiled together with the firmware.

At runtime the library reads the source code directly from flash memory and streams it to the Serial interface.

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
    watcher.bat
    watcher.sh
Requirements

Python 3.x (required by the watcher)

Arduino IDE 1.8 or newer

An Arduino compatible board

Troubleshooting
"No source data available"

Make sure the watcher is running.

Verify that the file:

forgetfulino_source_data.h

exists inside the src folder.

Compilation errors

Check that:

the library is installed in the correct directory

Arduino IDE has been restarted

there are no duplicate library installations

Contributing

Contributions and suggestions are welcome.

Feel free to open issues or submit pull requests.

License

MIT License

Copyright (c) 2024 IamTheVector

The software is provided "as is", without warranty of any kind.

Author

IamTheVector

GitHub
https://github.com/IamTheVector

If you find this library useful, consider giving the repository a ⭐ on GitHub.
