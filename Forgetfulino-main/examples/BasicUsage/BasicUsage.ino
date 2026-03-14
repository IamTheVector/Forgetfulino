#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
  delay(2000);

  Forgetfulino.begin();

  // SCELTA 1: vuoi il codice sorgente leggibile subito (ma pesante in flash)?
  // Scommenta la riga sotto per stampare tutto lo sketch originale:
  //
  // Forgetfulino.dumpSource();

  // SCELTA 2: vuoi il pacchetto compresso Base85?
  // Questo stampa una sola stringa, che puoi copiare e decomprimere
  // offline con lo script fornito (batch / forgetfulino.cc, ecc.).
  Forgetfulino.dumpCompressed();
}

void loop() {
  // Non facciamo nulla nel loop.
}




