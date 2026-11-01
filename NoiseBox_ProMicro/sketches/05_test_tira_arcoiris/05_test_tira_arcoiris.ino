// Prueba de la tira de 8 LED (WS2812): arcoíris que se desplaza. Sin piezo ni potenciómetro.
// Dato (DIN) en el pin 10, con 220 ohm en serie. 5V y GND a la tira.
#include <Adafruit_NeoPixel.h>

const int LED_PIN = 10;
const int NLED = 8;
const uint8_t BRIGHT = 40;   // 0-255, bajo para no pasar del consumo del USB
Adafruit_NeoPixel bar(NLED, LED_PIN, NEO_GRB + NEO_KHZ800);

uint16_t offset = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);   // el LED pequeño "L" de la placa parpadea: así se ve que el programa corre
  bar.begin();
  bar.setBrightness(BRIGHT);
  bar.show();
}

void loop() {
  for (int i = 0; i < NLED; i++) {
    uint16_t hue = offset + (uint32_t)i * 65536L / NLED;    // los 8 LED reparten todo el arcoíris
    bar.setPixelColor(i, bar.gamma32(bar.ColorHSV(hue)));
  }
  bar.show();
  if ((offset >> 8) % 16 == 0) digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  offset += 256;      // velocidad del desplazamiento
  delay(20);
}
