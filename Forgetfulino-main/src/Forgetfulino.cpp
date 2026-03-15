#include "Forgetfulino.h"

// Generated data headers (AUTO-GENERATED - DO NOT EDIT)
#include "forgetfulino_source_data.h"
#include "forgetfulino_compressed.h"

ForgetfulinoClass::ForgetfulinoClass()
    : initialized(false) {
}

void ForgetfulinoClass::begin() {
    if (!initialized) {
        initialized = true;
    }
}

char ForgetfulinoClass::readFlashChar(const char* addr) {
#if defined(ARDUINO_ARCH_AVR)
    return pgm_read_byte(addr);
#elif defined(ESP8266) || defined(ESP32)
    return *addr;
#else
    return *addr;
#endif
}

void ForgetfulinoClass::dumpSource() {
    // `forgetfulino_source_size`, `forgetfulino_source_data` and
    // `forgetfulino_sketch_name` are defined in forgetfulino_source_data.h
    if (forgetfulino_source_size == 0) {
        Serial.println(F("ERROR: No source data available"));
        return;
    }

    // Header
    Serial.println(F("\n+-----------------------------------------+"));
    Serial.println(F("|      FORGETFULINO SKETCH SOURCE         |"));
    Serial.println(F("+-----------------------------------------+"));

    // Filename
    Serial.print(F("File: "));
    for (int i = 0; i < 64; i++) {
        char c = readFlashChar(&forgetfulino_sketch_name[i]);
        if (c == '\0') {
            break;
        }
        Serial.print(c);
    }
    Serial.println();

    // Size
    Serial.print(F("Size: "));
    Serial.print(forgetfulino_source_size);
    Serial.println(F(" bytes"));

    Serial.println(F("-------------------------------------------"));
    Serial.println();

    // Source content from PROGMEM
    for (unsigned int i = 0; i < forgetfulino_source_size; i++) {
        char c = readFlashChar(&forgetfulino_source_data[i]);
        Serial.print(c);

        // Small delay to avoid overwhelming the serial buffer
        if (i % 100 == 0) {
            delay(1);
        }
    }

    Serial.println();
    Serial.println(F("-------------------------------------------"));
}

static uint8_t readFlashByte(const uint8_t* addr) {
#if defined(ARDUINO_ARCH_AVR)
    return pgm_read_byte(addr);
#else
    return *addr;
#endif
}

// Simple Base64 alphabet used to dump compressed bytes as text.
static const char FORGETFULINO_B64_ALPHABET[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";

void ForgetfulinoClass::dumpCompressed() {
    if (forgetfulino_original_size == 0) {
        Serial.println(F("ERROR: No compressed data available"));
        return;
    }

    Serial.println(F("\n+-----------------------------------------+"));
    Serial.println(F("|   FORGETFULINO COMPRESSED SKETCH DATA   |"));
    Serial.println(F("+-----------------------------------------+"));

    Serial.print(F("Original size: "));
    Serial.print(forgetfulino_original_size);
    Serial.println(F(" bytes"));

    const unsigned long compressedSize = forgetfulino_compressed_size;

    Serial.print(F("Compressed size: "));
    Serial.print(compressedSize);
    Serial.println(F(" bytes"));

    // Base64 output length for reference (4 chars for every 3 bytes, padded).
    const unsigned long base64Length = ((compressedSize + 2UL) / 3UL) * 4UL;

    Serial.print(F("Base64 length: "));
    Serial.print(base64Length);
    Serial.println(F(" chars"));

    Serial.println(F("-------------------------------------------"));
    Serial.println();

    // Dump compressed bytes as Base64 so they can be easily copied and decoded on the PC.
    unsigned long groupCount = 0;
    for (unsigned long i = 0; i < compressedSize; i += 3) {
        const uint8_t b0 = readFlashByte(&forgetfulino_compressed_data[i]);
        const uint8_t b1 = (i + 1 < compressedSize) ? readFlashByte(&forgetfulino_compressed_data[i + 1]) : 0;
        const uint8_t b2 = (i + 2 < compressedSize) ? readFlashByte(&forgetfulino_compressed_data[i + 2]) : 0;

        const uint8_t o0 = (b0 >> 2) & 0x3F;
        const uint8_t o1 = ((b0 & 0x03) << 4) | ((b1 >> 4) & 0x0F);
        const uint8_t o2 = ((b1 & 0x0F) << 2) | ((b2 >> 6) & 0x03);
        const uint8_t o3 = b2 & 0x3F;

        Serial.print(FORGETFULINO_B64_ALPHABET[o0]);
        Serial.print(FORGETFULINO_B64_ALPHABET[o1]);

        if (i + 1 < compressedSize) {
            Serial.print(FORGETFULINO_B64_ALPHABET[o2]);
        } else {
            Serial.print('=');
        }

        if (i + 2 < compressedSize) {
            Serial.print(FORGETFULINO_B64_ALPHABET[o3]);
        } else {
            Serial.print('=');
        }

        // Avoid overwhelming Serial: break line and pause periodically.
        groupCount++;
        if (groupCount % 19UL == 0UL) {
            Serial.println();
            delay(1);
        }
    }

    Serial.println();
    Serial.println(F("-------------------------------------------"));
}

// Global library instance
ForgetfulinoClass Forgetfulino;