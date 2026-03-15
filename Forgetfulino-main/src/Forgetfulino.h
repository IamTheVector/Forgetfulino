#ifndef FORGETFULINO_H
#define FORGETFULINO_H

#include <Arduino.h>

class ForgetfulinoClass {
private:
    bool initialized;
    char readFlashChar(const char* addr);

public:
    ForgetfulinoClass();

    // Initialize the library and announce on Serial
    void begin();

    // Dump the original sketch source over Serial immediately
    void dumpSource();

    // Dump the compressed representation of the sketch over Serial immediately
    void dumpCompressed();

    // Poll Serial and, when the keyword "forgetfulino" (any case) is received,
    // dump the original sketch source. Intended to be called from loop().
    void dumpSource_OnDemand();

    // Poll Serial and, when the keyword "forgetfulino" (any case) is received,
    // dump the compressed sketch. Intended to be called from loop().
    void dumpCompressed_OnDemand();
};

extern ForgetfulinoClass Forgetfulino;

#endif