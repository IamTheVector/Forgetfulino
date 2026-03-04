#!/usr/bin/env python3
"""
Forgetfulino Source Code Generator
Generates header file directly in the library folder
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

def get_library_src_path():
    """Get the library src path based on the generator location"""
    # The generator is in tools/forgetfulino_generator.py
    # So library src is ../src/
    generator_path = os.path.dirname(os.path.abspath(__file__))
    library_root = os.path.dirname(generator_path)  # tools parent = library root
    src_path = os.path.join(library_root, "src")
    return src_path

def main():
    if len(sys.argv) > 1:
        sketch_folder = sys.argv[1]
    else:
        sketch_folder = os.getcwd()
    
    print("\nFORGETFULINO GENERATOR")
    print("======================")
    print(f"Sketch folder: {sketch_folder}")
    
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
    
    # Save DIRECTLY to library src folder
    lib_src_path = get_library_src_path()
    output_file = os.path.join(lib_src_path, "forgetfulino_source_data.h")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header_content)
        print(f"File generated directly in library: {output_file}")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    
    print("\nOPERATION COMPLETED")
    print("Now you can compile and upload your sketch!")

if __name__ == "__main__":
    main()
