#include <Forgetfulino.h>
/* WARNING THIS EXAMPLE WILL NOT WORK IF YOU LEAVE IT IN  
THE EXAMPLE FOLDER (No read\write permissions), YOU HAVE TO PLACE IT 
INSIDE THE SKETCH FOLDER OF ARDUINO
Run start_watcher (bat or sh) on the sketch folder

EXECUTE: python "C:\...[YOUR PATH]...\libraries\Forgetfulino\tools\forgetfulino_generator.py"
upload the code
look at serial data
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
