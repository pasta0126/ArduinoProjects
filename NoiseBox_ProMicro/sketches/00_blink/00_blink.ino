// Test Pro Micro: 3 parpadeos rápidos y luego fijo 1 s, en bucle.
// La Pro Micro no tiene LED en el pin 13: usamos el LED RX (pin 17, activo en LOW).
const int LED = 17;

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);  // apagado
}

void on()  { digitalWrite(LED, LOW); }
void off() { digitalWrite(LED, HIGH); }

void loop() {
  for (int i = 0; i < 3; i++) {
    on();  delay(100);
    off(); delay(100);
  }
  on();  delay(1000);
  off(); delay(300);
}
