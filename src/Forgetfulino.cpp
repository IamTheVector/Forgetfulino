#include "Forgetfulino.h"

// Generated data headers (AUTO-GENERATED - DO NOT EDIT)
#include "forgetfulino_source_data.h"
#include "forgetfulino_compressed.h"

static const char forgetfulino_default_trigger[] = "forgetfulino";

#ifndef FORGETFULINO_DEBUG
#define FORGETFULINO_DEBUG 1
#endif

static void forgetfulino_debugPrintDecision(const char* rawTrigger, const char* normTrigger, bool isForgetfulinoParam, bool hasPassword, const char* effectiveTrigger, uint8_t targetLen, bool ignoreCase) {
#if FORGETFULINO_DEBUG
    Serial.print(F("DEBUG raw='"));
    Serial.print(rawTrigger ? rawTrigger : "<NULL>");
    Serial.print(F("' norm='"));
    Serial.print(normTrigger);
    Serial.print(F("' isForgetfulinoParam="));
    Serial.print(isForgetfulinoParam ? F("1") : F("0"));
    Serial.print(F(" hasPassword="));
    Serial.print(hasPassword ? F("1") : F("0"));
    Serial.print(F(" effective='"));
    Serial.print(effectiveTrigger);
    Serial.print(F("' len="));
    Serial.print(targetLen);
    Serial.print(F(" ignoreCase="));
    Serial.println(ignoreCase ? F("1") : F("0"));
#endif
}

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

// True when trigger is "Forgetfulino" in any case (then matching is case-insensitive).
static bool forgetfulino_trigger_is_forgetfulino(const char* trigger) {
    if (!trigger) return false;
    uint8_t i = 0;
    for (; forgetfulino_default_trigger[i] != '\0'; ++i) {
        char a = trigger[i];
        char b = forgetfulino_default_trigger[i];
        if (a == '\0') return false; // trigger shorter
        if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
        if (b >= 'A' && b <= 'Z') b = b - 'A' + 'a';
        if (a != b) return false;
    }
    // Must end exactly here (no extra chars)
    return trigger[i] == '\0';
}

// Helper: compare buffer [start..end) with trigger (length targetLen). Read trigger with FORGETFULINO_READ_TRIGGER. Case-insensitive if ignoreCase.
static bool forgetfulino_buffer_matches_trigger(const char* buffer, uint8_t start, uint8_t end, const char* trigger, uint8_t targetLen, bool ignoreCase) {
    if (end - start != targetLen) return false;
    for (uint8_t i = 0; i < targetLen; ++i) {
        char a = buffer[start + i];
        char b = trigger[i];
        if (ignoreCase) {
            if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
            if (b >= 'A' && b <= 'Z') b = b - 'A' + 'a';
        }
        if (a != b) return false;
    }
    return true;
}

// Helper to check for a trigger word on Serial.
// Step 1: sanitize password parameter:
//   - nullptr, "" or any case-variant of "forgetfulino" => treated as NO PASSWORD.
// Step 2:
//   - NO PASSWORD: only match "forgetfulino" (case-insensitive, trimmed), no cooldown/block/prints.
//   - PASSWORD (any other non-empty string): match that string (case-sensitive), with cooldown+block.
static bool forgetfulino_checkSerialTrigger(const char* trigger) {
    static char buffer[16];
    static uint8_t index = 0;
    static uint8_t wrongAttempts = 0;
    static unsigned long lastWrongAttemptMillis = 0;
    static unsigned long blockedUntilMillis = 0;

    const unsigned long now = millis();

    // Sanitize password: forgetfulino (any case, with leading/trailing spaces ignored) == no password.
    bool isForgetfulinoParam = false;
    char normTrigger[16];
    normTrigger[0] = '\0';
    if (trigger != nullptr) {
        // Copy up to 15 chars, trim, lowercase, then compare to "forgetfulino".
        char tmp[16];
        uint8_t len = 0;
        while (trigger[len] != '\0' && len < 15) {
            tmp[len] = trigger[len];
            ++len;
        }
        tmp[len] = '\0';

        // Trim spaces/tabs/CR/LF.
        uint8_t start = 0;
        while (start < len && (tmp[start] == ' ' || tmp[start] == '\t' || tmp[start] == '\r' || tmp[start] == '\n')) ++start;
        uint8_t end = len;
        while (end > start && (tmp[end - 1] == ' ' || tmp[end - 1] == '\t' || tmp[end - 1] == '\r' || tmp[end - 1] == '\n')) --end;

        uint8_t normLen = end > start ? (end - start) : 0;
        // Build normalized (trimmed + lowercase) string for debug.
        for (uint8_t i = 0; i < normLen && i < 15; ++i) {
            char a = tmp[start + i];
            if (a >= 'A' && a <= 'Z') a = a - 'A' + 'a';
            normTrigger[i] = a;
        }
        normTrigger[normLen < 15 ? normLen : 15] = '\0';
        // If sanitized string equals "forgetfulino" then treat as no password.
        isForgetfulinoParam = (strcmp(normTrigger, "forgetfulino") == 0);
    }

    // FORCE: if sanitized == "forgetfulino" then treat as NO PASSWORD.
    // (This guarantees no password mode even if isForgetfulinoParam logic fails.)
    bool hasPassword = (trigger != nullptr &&
                        trigger[0] != '\0' &&
                        !isForgetfulinoParam);
    if (!hasPassword) {
        // already no-password
    } else if (strcmp(normTrigger, "forgetfulino") == 0) {
        hasPassword = false;
        isForgetfulinoParam = true;
    }

    const char* effectiveTrigger = hasPassword ? trigger : forgetfulino_default_trigger;
    const uint8_t targetLen = (uint8_t)strlen(effectiveTrigger);
    const bool ignoreCase = hasPassword ? false : true;

    forgetfulino_debugPrintDecision(trigger, normTrigger, isForgetfulinoParam, hasPassword, effectiveTrigger, targetLen, ignoreCase);

    if (hasPassword && wrongAttempts >= 3 && blockedUntilMillis != 0) {
        if (now < blockedUntilMillis) {
            while (Serial.available() > 0) Serial.read();
            return false;
        }
        wrongAttempts = 0;
        blockedUntilMillis = 0;
        lastWrongAttemptMillis = 0;
    }

    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            if (index == 0) continue;
            buffer[index] = '\0';
            uint8_t start = 0;
            while (buffer[start] == ' ' || buffer[start] == '\t') ++start;
            uint8_t end = index;
            while (end > start && (buffer[end - 1] == ' ' || buffer[end - 1] == '\t')) --end;

            bool match = forgetfulino_buffer_matches_trigger(buffer, start, end, effectiveTrigger, targetLen, ignoreCase);
            index = 0;
            if (match) {
                if (hasPassword) {
                    wrongAttempts = 0;
                    lastWrongAttemptMillis = 0;
                    blockedUntilMillis = 0;
                }
                return true;
            }
            if (!hasPassword) return false;  // no punishment
            if (lastWrongAttemptMillis != 0 && (now - lastWrongAttemptMillis) < 5000UL) return false;
            wrongAttempts++;
            lastWrongAttemptMillis = now;
            Serial.println(F("Wrong password. Next attempt in 5 seconds."));
            if (wrongAttempts >= 3) {
                blockedUntilMillis = now + 300000UL;
                Serial.println(F("Too many wrong attempts. Wait 5 minutes."));
            }
            return false;
        }

        if (index < sizeof(buffer) - 1) buffer[index++] = c;

        if (index == targetLen && targetLen > 0) {
            buffer[targetLen] = '\0';
            uint8_t start = 0;
            while (buffer[start] == ' ' || buffer[start] == '\t') ++start;
            uint8_t end = targetLen;
            while (end > start && (buffer[end - 1] == ' ' || buffer[end - 1] == '\t')) --end;

            bool match = forgetfulino_buffer_matches_trigger(buffer, start, end, effectiveTrigger, targetLen, ignoreCase);
            index = 0;
            if (match) {
                if (hasPassword) {
                    wrongAttempts = 0;
                    lastWrongAttemptMillis = 0;
                    blockedUntilMillis = 0;
                }
                return true;
            }
            if (!hasPassword) return false;
            if (lastWrongAttemptMillis != 0 && (now - lastWrongAttemptMillis) < 5000UL) return false;
            wrongAttempts++;
            lastWrongAttemptMillis = now;
            Serial.println(F("Wrong password. Next attempt in 5 seconds."));
            if (wrongAttempts >= 3) {
                blockedUntilMillis = now + 300000UL;
                Serial.println(F("Too many wrong attempts. Wait 5 minutes."));
            }
            return false;
        }
    }
    return false;
}

void ForgetfulinoClass::dumpSource_OnDemand(const char* trigger) {
    // OnDemand must be in loop(): setup() runs once, so we only get one "pass" there.
    // First call: print check. Second call (only if in loop): print OK and then run trigger.
    static uint8_t passCount = 0;
    if (passCount == 0) {
        Serial.println(F("Internal Check: Forgetfulino OnDemand should be in Loop only."));
        passCount = 1;
        return;
    }
    if (passCount == 1) {
        Serial.println(F("Check OK: Forgetfulino OnDemand is in Loop, Forgetfulino is here."));
        // "Password protected" only when a custom non-empty trigger is used (not "forgetfulino").
        if (trigger && trigger[0] != '\0' && !forgetfulino_trigger_is_forgetfulino(trigger)) {
            Serial.println(F("Password protected"));
        }
        passCount = 2;
    }

    if (forgetfulino_checkSerialTrigger(trigger)) {
        dumpSource();
    }
}

void ForgetfulinoClass::dumpSource_OnDemand() {
    dumpSource_OnDemand(nullptr);
}

void ForgetfulinoClass::dumpCompressed_OnDemand(const char* trigger) {
    // OnDemand must be in loop(): setup() runs once, so we only get one "pass" there.
    static uint8_t passCount = 0;
    if (passCount == 0) {
        Serial.println(F("Internal Check: Forgetfulino OnDemand should be in Loop only."));
        passCount = 1;
        return;
    }
    if (passCount == 1) {
        Serial.println(F("Check OK: Forgetfulino OnDemand is in Loop, Forgetfulino is here."));
        // "Password protected" only when a custom non-empty trigger is used (not "forgetfulino").
        if (trigger && trigger[0] != '\0' && !forgetfulino_trigger_is_forgetfulino(trigger)) {
            Serial.println(F("Password protected"));
        }
        passCount = 2;
    }

    if (forgetfulino_checkSerialTrigger(trigger)) {
        dumpCompressed();
    }
}

void ForgetfulinoClass::dumpCompressed_OnDemand() {
    dumpCompressed_OnDemand(nullptr);
}

// Global library instance
ForgetfulinoClass Forgetfulino;
