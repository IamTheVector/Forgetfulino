#include "Forgetfulino.h"

// The generated file must be in the same folder as this .cpp
#include "forgetfulino_source_data.h"

// Data references (defined in the generated file)
extern const char forgetfulino_source_data[];
extern const unsigned int forgetfulino_source_size;
extern const char forgetfulino_sketch_name[];

ForgetfulinoClass::ForgetfulinoClass() : initialized(false) {
}

ForgetfulinoClass::~ForgetfulinoClass() {
}

void ForgetfulinoClass::begin() {
    if (!initialized) {
        initialized = true;
    }
}

bool ForgetfulinoClass::hasSourceData() {
    return forgetfulino_source_size > 0;
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
    if (!hasSourceData()) {
        Serial.println(F("ERROR: No source data available"));
        return;
    }
    
    // Print header
    Serial.println(F("\n+-----------------------------------------+"));
    Serial.println(F("|      FORGETFULINO SKETCH SOURCE         |"));
    Serial.println(F("+-----------------------------------------+"));
    
    // Print filename
    Serial.print(F("File: "));
    for (int i = 0; i < 64; i++) {
        char c = readFlashChar(&forgetfulino_sketch_name[i]);
        if (c == '\0') break;
        Serial.print(c);
    }
    Serial.println();
    
    // Print size
    Serial.print(F("Size: "));
    Serial.print(forgetfulino_source_size);
    Serial.println(F(" bytes"));
    
    // Separator line
    Serial.println(F("-------------------------------------------"));
    Serial.println();
    
    // Print source directly from flash, one character at a time
    for (unsigned int i = 0; i < forgetfulino_source_size; i++) {
        char c = readFlashChar(&forgetfulino_source_data[i]);
        Serial.print(c);
        
        // Small delay to avoid overwhelming the serial buffer
        if (i % 100 == 0) {
            delay(1);
        }
    }
    
    // Final line
    Serial.println();
    Serial.println(F("-------------------------------------------"));
}

size_t ForgetfulinoClass::getSourceSize() {
    return forgetfulino_source_size;
}

const char* ForgetfulinoClass::getSketchName() {
    // Static version for compatibility
    static char sketchName[64];
    
    for (int i = 0; i < 63; i++) {
        sketchName[i] = readFlashChar(&forgetfulino_sketch_name[i]);
        if (sketchName[i] == '\0') break;
    }
    sketchName[63] = '\0';
    
    return sketchName;
}

// Global library instance
ForgetfulinoClass Forgetfulino;