#include <Forgetfulino.h>

/* Run cmd on the sketch folder
EXECUTE: The watchdog
IMPORTANT
If you leave this example in the Examples folder will be just a read only file, so the watcher will not monitor it! 
IMPORTANT
*/


void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("\nFORGETFULINO DEMO");
  Serial.println("=================");
  
  if (Forgetfulino.hasSourceData()) {
    Serial.print("Embedded source: ");
    Serial.print(Forgetfulino.getSourceSize());
    Serial.println(" bytes");
    Serial.println("\n--- SKETCH SOURCE ---");
    Forgetfulino.dumpSource();
    Serial.println("--- END SKETCH ---");
  } else {
    Serial.println("ERROR: Source not found!");
    Serial.println("Run tools/forgetfulino_generator.py before compiling");
  }
}

void loop() {}