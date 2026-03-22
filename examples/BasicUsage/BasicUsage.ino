#include <Forgetfulino.h>

/*WARNING 
REMOVE THIS EXAMPLE FROM EXAMPLE FOLDER
USUALLY EXAMPLE FOLDER HAS NO WRITE PERMISSIONS
WARNING*/


// Basic example:
// - prints a compressed dump once at boot
// - you can decode it from the IDE using
//   “Forgetfulino: Decode compressed dump”

void setup() {
  Serial.begin(115200);
  delay(2000);

  Forgetfulino.begin();

  // Option 1: readable plain-text source (larger in flash).
  // Uncomment to dump the full original sketch:
  //
  // Forgetfulino.dumpSource();

  // Option 2: compressed package (recommended).
  // This prints a single Base64 line that you can copy
  // and decode with the Forgetfulino IDE extension.
  Forgetfulino.dumpCompressed();
}

void loop() {
  // Nothing here – this example only dumps once in setup.
}