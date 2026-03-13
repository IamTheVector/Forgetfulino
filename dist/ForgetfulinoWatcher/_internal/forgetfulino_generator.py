#!/usr/bin/env python3
"""
Forgetfulino Source Code Generator

This tool finds the main .ino file in a sketch folder and generates
two header files inside the Forgetfulino library `src` directory:

    - forgetfulino_source_data.h   (plain-text source in PROGMEM)
    - forgetfulino_compressed.h    (Base85-encoded source + original size)

It NEVER touches `Forgetfulino.h`. That file contains only the fixed
library class declaration.
"""

import os
import sys
import glob
import base64
from datetime import datetime


def find_sketch_file(folder: str) -> str | None:
    """Find the main .ino file in the folder."""
    ino_files = glob.glob(os.path.join(folder, "*.ino"))
    if not ino_files:
        return None

    folder_name = os.path.basename(folder)
    for path in ino_files:
        if os.path.splitext(os.path.basename(path))[0] == folder_name:
            return path
    return ino_files[0]


def collect_sketch_sources(sketch_folder: str) -> tuple[str, str]:
    """
    Collect all .ino and .cpp/.c files in the sketch folder (no subfolders, no libraries).
    Returns (full_source_with_comments, main_ino_basename).
    Main .ino is first, then other .ino alphabetically, then .cpp/.c alphabetically.
    """
    main_ino = find_sketch_file(sketch_folder)
    if not main_ino:
        return "", ""

    folder_name = os.path.basename(sketch_folder)
    main_name = os.path.basename(main_ino)
    # All .ino in folder (main first)
    ino_list = sorted(
        [p for p in glob.glob(os.path.join(sketch_folder, "*.ino"))],
        key=lambda p: (0 if os.path.basename(p) == main_name else 1, os.path.basename(p)),
    )
    # All .cpp and .c in folder (sketch tab files, not libraries)
    cpp_list = sorted(glob.glob(os.path.join(sketch_folder, "*.cpp")) + glob.glob(os.path.join(sketch_folder, "*.c")))
    # Build ordered list: main .ino first, then other .ino, then .cpp/.c
    ordered = ino_list + cpp_list
    parts = []
    for path in ordered:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        name = os.path.basename(path)
        parts.append(f"// === File: {name} ===\n")
        parts.append(content)
        if not content.endswith("\n"):
            parts.append("\n")
        parts.append("\n")
    full = "".join(parts)
    # Global header
    header = f"// Sketch: {folder_name}\n"
    header += f"// Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"// Files: {len(ordered)}\n\n"
    return header + full, main_name


def text_to_c_array(text: str, var_name: str) -> str:
    """Convert text to a C char array in PROGMEM."""
    lines: list[str] = []
    chars: list[str] = []
    total_chars = len(text)

    for index, ch in enumerate(text):
        if ch == "\n":
            chars.append("'\\n'")
        elif ch == "\r":
            chars.append("'\\r'")
        elif ch == "\t":
            chars.append("'\\t'")
        elif ch == "\\":
            chars.append("'\\\\'")
        elif ch == '"':
            chars.append("'\\\"'")
        elif ch == "'":
            chars.append("'\\''")
        else:
            chars.append(f"'{ch}'")

        if (index + 1) % 16 == 0 or index == total_chars - 1:
            lines.append("    " + ", ".join(chars))
            chars = []

    array_content = ",\n".join(lines)
    return f"const char {var_name}[] PROGMEM = {{\n{array_content}\n}};"


def to_c_string_literal(value: str, var_name: str) -> str:
    """Convert a Python string into a single C string literal with escapes."""
    escaped_chars: list[str] = []
    for ch in value:
        if ch == "\\":
            escaped_chars.append("\\\\")
        elif ch == '"':
            escaped_chars.append('\\"')
        elif ch == "\n":
            escaped_chars.append("\\n")
        elif ch == "\r":
            escaped_chars.append("\\r")
        elif ch == "\t":
            escaped_chars.append("\\t")
        else:
            escaped_chars.append(ch)

    escaped = "".join(escaped_chars)
    return f'const char {var_name}[] PROGMEM = "{escaped}";'


def get_library_src_path() -> str:
    """Get the library src path. Uses FORGETFULINO_LIBRARY_ROOT if set (e.g. when run from standalone app)."""
    env_root = os.environ.get("FORGETFULINO_LIBRARY_ROOT", "").strip()
    if env_root and os.path.isdir(env_root):
        return os.path.join(env_root, "src")
    generator_path = os.path.dirname(os.path.abspath(__file__))
    library_root = os.path.dirname(generator_path)  # tools parent = library root
    return os.path.join(library_root, "src")


def generate_source_header(full_source: str, ino_file: str) -> str:
    """Generate the content for forgetfulino_source_data.h."""
    return f"""// Forgetfulino generated source data
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
{text_to_c_array(full_source, "forgetfulino_source_data")}

// Metadata
const unsigned int forgetfulino_source_size = {len(full_source)};
const char forgetfulino_sketch_name[] PROGMEM = "{os.path.basename(ino_file)}";

#endif
"""


def generate_compressed_header(full_source: str) -> str:
    """Generate the content for forgetfulino_compressed.h with Base85 data."""
    # Base85 encode the UTF-8 bytes of the full source.
    encoded_bytes = base64.a85encode(full_source.encode("utf-8"))
    encoded_str = encoded_bytes.decode("ascii")

    compressed_literal = to_c_string_literal(
        encoded_str, "forgetfulino_compressed_data"
    )

    return f"""// Forgetfulino generated compressed data
// AUTO-GENERATED - DO NOT EDIT

#ifndef FORGETFULINO_COMPRESSED_H
#define FORGETFULINO_COMPRESSED_H

#include <Arduino.h>

// Platform-specific PROGMEM
#if defined(ARDUINO_ARCH_AVR)
    #include <avr/pgmspace.h>
#elif defined(ESP8266) || defined(ESP32)
    #undef PROGMEM
    #define PROGMEM
#endif

// Base85-compressed sketch source (null-terminated string)
{compressed_literal}

// Original uncompressed source size in bytes
const unsigned int forgetfulino_original_size = {len(full_source)};

#endif
"""


def main() -> None:
    if len(sys.argv) > 1:
        sketch_folder = sys.argv[1]
    else:
        sketch_folder = os.getcwd()

    print("\nFORGETFULINO GENERATOR")
    print("======================")
    print(f"Sketch folder: {sketch_folder}")

    full_source, main_name = collect_sketch_sources(sketch_folder)
    if not full_source:
        print("\nERROR: No .ino file found!")
        sys.exit(1)

    print(f"Sketch: {main_name}")

    print(f"Size: {len(full_source)} bytes")

    # Build header contents (main_name is the main .ino basename for metadata)
    source_header = generate_source_header(full_source, main_name)
    compressed_header = generate_compressed_header(full_source)

    # Save into the library src folder
    lib_src_path = get_library_src_path()
    source_header_path = os.path.join(lib_src_path, "forgetfulino_source_data.h")
    compressed_header_path = os.path.join(lib_src_path, "forgetfulino_compressed.h")

    try:
        with open(source_header_path, "w", encoding="utf-8") as handle:
            handle.write(source_header)
        print(f"Generated: {source_header_path}")

        with open(compressed_header_path, "w", encoding="utf-8") as handle:
            handle.write(compressed_header)
        print(f"Generated: {compressed_header_path}")
    except Exception as exc:
        print(f"\nERROR writing headers: {exc}")
        sys.exit(1)

    print("\nOPERATION COMPLETED")
    print("Now you can compile and upload your sketch with Forgetfulino.")


if __name__ == "__main__":
    main()

