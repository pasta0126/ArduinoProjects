// Paso 1: lee el piezo en A0 y lo manda al Serial Plotter.
// Reposo: valores cerca de 0. Al golpear el piezo: picos que bajan solos.
// Serial Plotter a 115200 baudios.
const int PIEZO = A0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.print("piezo:");
  Serial.println(analogRead(PIEZO));
  delay(2);  // ~500 lecturas/s: el Serial Plotter muestra ~1 segundo de gráfica
}
