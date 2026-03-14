#include "Forgetfulino.h"

// Generated data headers (AUTO-GENERATED - DO NOT EDIT)
// These files are produced by tools/forgetfulino_generator.py
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

#if defined(FORGETFULINO_USE_CHUNKS)
// Read pointer from PROGMEM (AVR) or use directly (ESP/other)
static const char* getChunkPtr(unsigned int chunkIndex) {
#if defined(ARDUINO_ARCH_AVR)
    return (const char*)pgm_read_ptr(&forgetfulino_compressed_chunks[chunkIndex]);
#else
    return forgetfulino_compressed_chunks[chunkIndex];
#endif
}
#endif

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

#if defined(FORGETFULINO_USE_CHUNKS)
    const unsigned long encodedLength = forgetfulino_compressed_total_len;
#else
    unsigned long encodedLength = 0;
    while (readFlashChar(&forgetfulino_compressed_data[encodedLength]) != '\0') {
        encodedLength++;
    }
#endif

    Serial.print(F("Base85 length: "));
    Serial.print(encodedLength);
    Serial.println(F(" chars"));

    Serial.println(F("-------------------------------------------"));
    Serial.println();

#if defined(FORGETFULINO_USE_CHUNKS)
    for (unsigned long i = 0; i < encodedLength; i++) {
        unsigned int chunkIdx = (unsigned int)(i / FORGETFULINO_COMPRESSED_CHUNK_SIZE);
        unsigned int offset = (unsigned int)(i % FORGETFULINO_COMPRESSED_CHUNK_SIZE);
        const char* chunk = getChunkPtr(chunkIdx);
        char c = readFlashChar(chunk + offset);
        Serial.print(c);
        if (i % 200 == 0) {
            delay(1);
        }
    }
#else
    for (unsigned long i = 0; i < encodedLength; i++) {
        char c = readFlashChar(&forgetfulino_compressed_data[i]);
        Serial.print(c);
        if (i % 200 == 0) {
            delay(1);
        }
    }
#endif

    Serial.println();
    Serial.println(F("-------------------------------------------"));
}

// Global library instance
ForgetfulinoClass Forgetfulino;