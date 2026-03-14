#ifndef FORGETFULINO_H
#define FORGETFULINO_H

#include <Arduino.h>

class ForgetfulinoClass {
private:
    bool initialized;
    char readFlashChar(const char* addr);

public:
    ForgetfulinoClass();

    // Initialize the library (optional, kept for future use)
    void begin();

    // Dump the original sketch source over Serial
    void dumpSource();

    // Dump the Base85-compressed representation of the sketch over Serial
    void dumpCompressed();
};

extern ForgetfulinoClass Forgetfulino;

#endif