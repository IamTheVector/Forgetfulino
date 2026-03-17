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

    // OnDemand without password: only reacts to "forgetfulino" (case-insensitive, trimmed).
    // Intended to be called from loop().
    void dumpSource_OnDemand();

    // OnDemand with password: reacts only to the provided trigger.
    // Special-case: if trigger is "forgetfulino" (any case), matching is case-insensitive.
    // For other triggers matching is case-sensitive.
    void dumpSource_OnDemand(const char* trigger);

    // OnDemand without password: only reacts to "forgetfulino" (case-insensitive, trimmed).
    // Intended to be called from loop().
    void dumpCompressed_OnDemand();

    // OnDemand with password: reacts only to the provided trigger.
    // Special-case: if trigger is "forgetfulino" (any case), matching is case-insensitive.
    // For other triggers matching is case-sensitive.
    void dumpCompressed_OnDemand(const char* trigger);
};

extern ForgetfulinoClass Forgetfulino;

#endif