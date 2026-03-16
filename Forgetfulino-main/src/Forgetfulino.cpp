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
        Serial.println(F("Forgetfulino is here"));
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
    // We keep it on a single logical line (no '\n' inside the loop) to make copy/paste easier),
    // with only a light delay to avoid overwhelming the serial buffer.
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

        // Avoid overwhelming Serial: pause periodically, but keep the transfer fast.
        groupCount++;
        if (groupCount % 19UL == 0UL) { // about every 76 characters
            delay(1);
        }
    }

    Serial.println();
    Serial.println(F("-------------------------------------------"));
}

// Helper to check for a trigger word on Serial.
// If trigger == "forgetfulino" (exact case), matching is case-insensitive.
// Otherwise matching is case-sensitive.
// Returns true when a full command has been received and consumed.
static bool forgetfulino_checkSerialTrigger(const char* trigger) {
    static char buffer[16];
    static uint8_t index = 0;

    // Default trigger: if user leaves () OR passes an empty string.
    if (!trigger || trigger[0] == '\0') {
        trigger = "forgetfulino";
    }
    const uint8_t targetLen = static_cast<uint8_t>(strlen(trigger));
    const bool ignoreCase =
        (targetLen == 11 && strcmp(trigger, "forgetfulino") == 0);

    while (Serial.available() > 0) {
        char c = Serial.read();

        // Treat newline or carriage return as end of command
        if (c == '\n' || c == '\r') {
            if (index == 0) {
                continue;
            }
            buffer[index] = '\0';

            // Trim leading and trailing spaces/tabs
            uint8_t start = 0;
            while (buffer[start] == ' ' || buffer[start] == '\t') {
                ++start;
            }
            uint8_t end = index;
            while (end > start && (buffer[end - 1] == ' ' || buffer[end - 1] == '\t')) {
                --end;
            }

            // Compare with trigger (optionally case-insensitive)
            bool match = true;

            // First, lengths must match
            if (end - start != targetLen) {
                match = false;
            } else {
                for (uint8_t i = 0; i < targetLen; ++i) {
                    char a = buffer[start + i];
                    char b = trigger[i];
                    if (ignoreCase) {
                        if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
                        if (b >= 'A' && b <= 'Z') b = b - 'A' + 'a';
                    }
                    if (a != b) {
                        match = false;
                        break;
                    }
                }
            }

            index = 0;
            return match;
        }

        // Build up the command word (we will trim whitespace at the end)
        if (index < sizeof(buffer) - 1) {
            buffer[index++] = c;
        }

        // Trigger even without newline: e.g. Serial Monitor "No line ending"
        // sends only the N characters (length of trigger word).
        if (index == targetLen && targetLen > 0) {
            buffer[targetLen] = '\0';
            uint8_t start = 0;
            while (buffer[start] == ' ' || buffer[start] == '\t') {
                ++start;
            }
            uint8_t end = targetLen;
            while (end > start && (buffer[end - 1] == ' ' || buffer[end - 1] == '\t')) {
                --end;
            }
            bool match = (end - start == targetLen);
            if (match) {
                for (uint8_t i = 0; i < targetLen; ++i) {
                    char a = buffer[start + i];
                    char b = trigger[i];
                    if (ignoreCase) {
                        if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
                        if (b >= 'A' && b <= 'Z') b = b - 'A' + 'a';
                    }
                    if (a != b) {
                        match = false;
                        break;
                    }
                }
            }
            if (match) {
                index = 0;
                return true;
            }
        }
    }

    return false;
}

void ForgetfulinoClass::dumpSource_OnDemand(const char* trigger) {
    // No need to require begin(): respond whenever the trigger word is received.
    if (forgetfulino_checkSerialTrigger(trigger)) {
        dumpSource();
    }
}

void ForgetfulinoClass::dumpCompressed_OnDemand(const char* trigger) {
    // No need to require begin(): respond whenever the trigger word is received.
    if (forgetfulino_checkSerialTrigger(trigger)) {
        dumpCompressed();
    }
}

// Global library instance
ForgetfulinoClass Forgetfulino;