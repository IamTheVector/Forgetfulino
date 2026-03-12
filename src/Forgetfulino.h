#ifndef FORGETFULINO_H
#define FORGETFULINO_H

#include "Arduino.h"

class ForgetfulinoClass {
private:
    bool initialized;
    char readFlashChar(const char* addr);
    
public:
    ForgetfulinoClass();
    ~ForgetfulinoClass();
    
    void begin();
    bool hasSourceData();
    void dumpSource();
    size_t getSourceSize();
    const char* getSketchName();
};

extern ForgetfulinoClass Forgetfulino;

#endif