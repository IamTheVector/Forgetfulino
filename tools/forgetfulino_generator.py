#!/usr/bin/env python3
"""
Forgetfulino Source Code Generator
Generates header file with sketch source code
"""

import os
import sys
import glob
from datetime import datetime

def find_sketch_file(folder):
    """Find the main .ino file in the folder"""
    ino_files = glob.glob(os.path.join(folder, "*.ino"))
    if not ino_files:
        return None
    
    folder_name = os.path.basename(folder)
    for f in ino_files:
        if os.path.splitext(os.path.basename(f))[0] == folder_name:
            return f
    return ino_files[0]

def text_to_c_array(text, var_name):
    """Convert text to C character array"""
    lines = []
    chars = []
    total_chars = len(text)
    
    for i, c in enumerate(text):
        if c == '\n':
            chars.append("'\\n'")
        elif c == '\r':
            chars.append("'\\r'")
        elif c == '\t':
            chars.append("'\\t'")
        elif c == '\\':
            chars.append("'\\\\'")
        elif c == '"':
            chars.append("'\\\"'")
        elif c == "'":
            chars.append("'\\''")
        else:
            chars.append(f"'{c}'")
        
        if (i + 1) % 16 == 0 or i == total_chars - 1:
            lines.append('    ' + ', '.join(chars))
            chars = []
    
    array_content = ',\n'.join(lines)
    return f'const char {var_name}[] PROGMEM = {{\n{array_content}\n}};'

def main():
    if len(sys.argv) > 1:
        sketch_folder = sys.argv[1]
    else:
        sketch_folder = os.getcwd()
    
    print("\nFORGETFULINO GENERATOR")
    print("======================")
    print(f"Folder: {sketch_folder}")
    
    ino_file = find_sketch_file(sketch_folder)
    if not ino_file:
        print("\nERROR: No .ino file found!")
        sys.exit(1)
    
    print(f"Sketch: {os.path.basename(ino_file)}")
    
    try:
        with open(ino_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    
    header = f"// File: {os.path.basename(ino_file)}\n"
    header += f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    full_source = header + source_code
    
    print(f"Size: {len(full_source)} bytes")
    
    header_content = f"""// Forgetfulino generated source data
// AUTO-GENERATED - DO NOT EDIT

#ifndef FORGETFULINO_SOURCE_DATA_H
#define FORGETFULINO_SOURCE_DATA_H

#include <Arduino.h>

// Platform-specific PROGMEM
#if defined(ARDUINO_ARCH_AVR)
    #include <avr/pgmspace.h>
#elif defined(ESP8266) || defined(ESP32)
    #undef PROGMEM
    #define PROGMEM
#endif

// Sketch source code
{text_to_c_array(full_source, 'forgetfulino_source_data')}

// Metadata
const unsigned int forgetfulino_source_size = {len(full_source)};
const char forgetfulino_sketch_name[] PROGMEM = "{os.path.basename(ino_file)}";

#endif
"""
    
    # Save in sketch folder
    sketch_output = os.path.join(sketch_folder, "forgetfulino_source_data.h")
    try:
        with open(sketch_output, 'w', encoding='utf-8') as f:
            f.write(header_content)
        print(f"File generated: {sketch_output}")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    
    print("\nOPERATION COMPLETED")
    print("Now you can compile and upload your sketch!")
    print("\nNext steps:")
    print("1. Copy the generated file to your library folder:")
    print(f"   cp {sketch_output} /path/to/Arduino/libraries/Forgetfulino/src/")
    print("2. Open Arduino IDE")
    print("3. Compile and upload your sketch")
    print("4. Call Forgetfulino.dumpSource() to see the embedded code")

if __name__ == "__main__":
    main()