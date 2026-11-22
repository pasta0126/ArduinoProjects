// Paso 8: la caja completa y simple. Alimentada por el USB.
//   Piezo (con el muelle)  -> A0 directo (2,2 MΩ a GND, como el ejemplo Knock de Arduino)
//   Sonido de muelle       -> pin 9 (PWM) -> 10 kΩ soldada en el cable -> punta y anillo del jack
//   LED RGB de 4 patas (ánodo común) -> pines 5 (rojo), 6 (verde), 4 (azul) directos; UNA sola 220 Ω de la pata común a VCC
// Con una sola resistencia, los tres colores no se encienden a la vez: la interrupción de audio
// los enciende por turnos (uno cada 1/15625 s) y así cada color tiene su corriente completa.
// Al arrancar el LED enciende ROJO, VERDE y AZUL (prueba de cableado).
// En reposo el LED "respira" despacio recorriendo el arcoíris: así sabes que está en marcha.
// Cada golpe: suena un "boing" metálico (más agudo cuanto más fuerte), el arcoíris salta
// hacia delante según la fuerza y el LED destella. También manda una nota MIDI por USB.
// Monitor serie (115200): imprime la fuerza de cada golpe, para ajustar THRESHOLD.
#include <MIDIUSB.h>

const int PIEZO = A0;
const int LED_R = 5, LED_G = 6, LED_B = 4;
const bool COMMON_ANODE = true;      // tu LED es de ánodo común: la pata larga va a VCC (5 V) por la 220 Ω

// --- golpe ---
const int THRESHOLD    = 25;         // por debajo de esto es ruido. Sube si dispara solo, baja si no detecta golpes suaves
const int PEAK_FOR_MAX = 700;        // pico que se considera golpe máximo
const unsigned long SCAN_MS    = 8;  // ventana para medir el pico
const unsigned long LOCKOUT_MS = 50; // tiempo muerto tras un golpe

// --- MIDI ---
const byte MIDI_NOTE = 38, CHANNEL = 9;   // caja (snare), canal 10
const unsigned long MIDI_LEN = 150;

// ================= sintetizador por PWM (pin 9) =================
// Timer1: PWM rápido de 8 bits (62,5 kHz) en el pin 9. Timer3: 15625 muestras por segundo.
const uint16_t FS = 15625;
const byte OUT_SHIFT = 0;            // volumen: 0 = fuerte (la 10 kΩ del jack ya lo baja), 1 = medio, 2 = bajo
const float RATIO[3] = {1.0, 2.76, 5.40};       // parciales inarmónicos = sonido metálico
const byte  DECAY[3] = {10, 9, 7};               // cuanto menor, antes se apaga ese parcial
const byte  LEVEL[3] = {170, 100, 60};           // volumen relativo de cada parcial
int8_t sine[256];
volatile uint16_t ph[3], inc[3], env[3], nEnv;
volatile uint16_t lfsr = 0xACE1;
uint8_t tick = 0;

// --- LED multiplexado: brillo 0..255 de cada color, lo escribe loop() y lo usa la interrupción ---
volatile uint8_t duty[3];
uint16_t acc[3];
uint8_t slot = 0;
volatile uint8_t *ledPort[3]; uint8_t ledMask[3];

inline void ledsOff() {
  for (uint8_t i = 0; i < 3; i++) {
    if (COMMON_ANODE) *ledPort[i] |= ledMask[i]; else *ledPort[i] &= ~ledMask[i];
  }
}
inline void ledOn(uint8_t i) {
  if (COMMON_ANODE) *ledPort[i] &= ~ledMask[i]; else *ledPort[i] |= ledMask[i];
}

ISR(TIMER3_COMPA_vect) {
  // LED: un color por turno; cada color reparte sus encendidos de forma uniforme (sin parpadeo)
  ledsOff();
  if (++slot == 3) slot = 0;
  acc[slot] += duty[slot];
  if (acc[slot] >= 256) { acc[slot] -= 256; ledOn(slot); }

  int16_t mix = 0, amp = 0;
  bool upd = ((++tick & 7) == 0);                // las envolventes bajan cada 8 muestras
  for (uint8_t i = 0; i < 3; i++) {
    if (env[i] < 64) continue;
    ph[i] += inc[i];
    mix += ((int16_t)sine[ph[i] >> 8] * (env[i] >> 8)) >> 7;
    amp += (int16_t)(env[i] >> 8) * 120 >> 7;    // amplitud máxima de este parcial
    if (upd) env[i] -= env[i] >> DECAY[i];
  }
  if (nEnv > 64) {                               // chasquido corto de ruido al principio del golpe
    lfsr = (lfsr >> 1) ^ (-(lfsr & 1) & 0xB400);
    mix += ((int16_t)(int8_t)(lfsr & 0xFF) * (nEnv >> 8)) >> 8;
    amp += (nEnv >> 8) >> 1;
    if (upd) nEnv -= nEnv >> 4;
  }
  mix >>= OUT_SHIFT; amp >>= OUT_SHIFT;
  if (amp > 127) amp = 127;
  if (mix > amp) mix = amp; else if (mix < -amp) mix = -amp;
  // En silencio la salida se queda a 0 V fija (sin PWM): así el parpadeo del LED no se cuela
  // en el jack como un pitido. Al sonar, el centro de la onda sube y baja con la envolvente.
  if (amp == 0) {
    TCCR1A &= ~_BV(COM1A1);                      // pin 9 deja el PWM y queda en LOW
  } else {
    OCR1A = amp + mix;                           // 0..254
    TCCR1A |= _BV(COM1A1);
  }
}

void synthBegin() {
  for (int i = 0; i < 256; i++) sine[i] = (int8_t)(120 * sin(2 * PI * i / 256.0));
  pinMode(9, OUTPUT);
  TCCR1A = _BV(COM1A1) | _BV(WGM10);             // PWM rápido 8 bits en el pin 9
  TCCR1B = _BV(WGM12) | _BV(CS10);
  OCR1A = 0; digitalWrite(9, LOW);
  TCCR3A = 0; TCCR3B = _BV(WGM32) | _BV(CS30);   // Timer3 en CTC, sin divisor
  OCR3A = 16000000UL / FS - 1;
  TIMSK3 = _BV(OCIE3A);
}

float baseHz = 100;                  // tono del golpe actual
unsigned long tBoing = 0;
bool boinging = false;

void boing(byte vel) {               // vel 1..127
  baseHz = 70 + vel * 1.1;           // suave ~70 Hz, fuerte ~210 Hz
  tBoing = millis(); boinging = true;
  noInterrupts();
  for (int i = 0; i < 3; i++) { ph[i] = 0; env[i] = (uint16_t)vel * LEVEL[i]; }
  nEnv = (uint16_t)vel * 140;
  interrupts();
  glide();
}

void glide() {                       // el tono cae como un muelle: empieza 1,6 veces más agudo y baja en ~0,1 s
  float t = (millis() - tBoing) / 60.0;
  float g = 1.0 + 0.6 * exp(-t);
  if (t > 6) boinging = false;
  for (int i = 0; i < 3; i++) {
    uint16_t v = (uint16_t)(baseHz * g * RATIO[i] * 65536.0 / FS);
    noInterrupts(); inc[i] = v; interrupts();
  }
}

// ================= LED RGB =================
uint16_t hue = 0;                    // 0..1535 (6 tramos de 256)
int flash = 0;                       // 0..255, destello del golpe

void ledSet(int r, int g, int b) {   // 0..255; por debajo de 4 se apaga para que no parpadee
  duty[0] = r < 4 ? 0 : r; duty[1] = g < 4 ? 0 : g; duty[2] = b < 4 ? 0 : b;
}

void showLed(unsigned long now) {
  // reposo: respira entre 6 y 40 cada 3 s
  float b = 6 + 34 * (0.5 - 0.5 * cos(2 * PI * (now % 3000) / 3000.0));
  int bright = max((int)b, flash);
  int seg = hue >> 8, f = hue & 255, r, g, bl;
  switch (seg) {
    case 0:  r = 255;     g = f;       bl = 0;       break;
    case 1:  r = 255 - f; g = 255;     bl = 0;       break;
    case 2:  r = 0;       g = 255;     bl = f;       break;
    case 3:  r = 0;       g = 255 - f; bl = 255;     break;
    case 4:  r = f;       g = 0;       bl = 255;     break;
    default: r = 255;     g = 0;       bl = 255 - f; break;
  }
  // brillo con curva cuadrática (el ojo ve el brillo así)
  long k = (long)bright * bright / 255;
  ledSet(r * k / 255, g * k / 255, bl * k / 255);
}

void ledTest() {                     // rojo, verde, azul medio segundo cada uno
  ledSet(255, 0, 0); delay(500);
  ledSet(0, 255, 0); delay(500);
  ledSet(0, 0, 255); delay(500);
  ledSet(0, 0, 0);
}

// ================= MIDI =================
void midi(bool on, byte vel) {
  midiEventPacket_t p = { (byte)(on ? 0x09 : 0x08), (byte)((on ? 0x90 : 0x80) | CHANNEL), MIDI_NOTE, vel };
  MidiUSB.sendMIDI(p);
  MidiUSB.flush();
}

// ================= principal =================
bool inHit = false, fired = false, noteOn = false;
unsigned long tHit = 0, lastHit = 0, tNote = 0, lastLed = 0, lastGlide = 0;
int peak = 0;

void setup() {
  Serial.begin(115200);
  int pins[3] = {LED_R, LED_G, LED_B};
  for (int i = 0; i < 3; i++) {
    pinMode(pins[i], OUTPUT);
    ledPort[i] = portOutputRegister(digitalPinToPort(pins[i]));
    ledMask[i] = digitalPinToBitMask(pins[i]);
  }
  ledsOff();
  synthBegin();                      // arranca también el multiplexado del LED
  ledTest();
}

void loop() {
  unsigned long now = millis();
  int v = analogRead(PIEZO);

  if (!inHit) {
    if (v >= THRESHOLD && now - lastHit >= LOCKOUT_MS) { inHit = true; fired = false; peak = v; tHit = now; }
  } else {
    if (v > peak) peak = v;
    if (!fired && now - tHit >= SCAN_MS) {
      fired = true;
      byte vel = constrain(map(peak, THRESHOLD, PEAK_FOR_MAX, 1, 127), 1, 127);
      boing(vel);
      hue = (hue + 64 + vel * 3) % 1536;         // el arcoíris salta más cuanto más fuerte
      flash = 60 + vel * 3 / 2;                  // hasta 250
      if (noteOn) midi(false, 0);
      midi(true, vel); noteOn = true; tNote = now;
      Serial.print("golpe "); Serial.print(peak); Serial.print("  vel "); Serial.println(vel);
    }
    if (v < THRESHOLD / 2) { inHit = false; lastHit = now; }
  }

  if (noteOn && now - tNote >= MIDI_LEN) { midi(false, 0); noteOn = false; }
  if (boinging && now - lastGlide >= 2) { lastGlide = now; glide(); }
  if (now - lastLed >= 15) {
    lastLed = now;
    if (flash > 0) flash = flash > 8 ? flash - 8 : 0;   // el destello se apaga en ~0,4 s
    else hue = (hue + 1) % 1536;                         // en reposo el color avanza despacio (~23 s la vuelta)
    showLed(now);
  }
}
