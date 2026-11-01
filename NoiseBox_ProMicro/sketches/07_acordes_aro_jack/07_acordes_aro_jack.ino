// Paso 7 (= paso 6 + sonido por el minijack): cada golpe toca un ACORDE (varias notas MIDI rasgueadas), el potenciómetro (A1)
// elige entre 8 acordes y SOLO se enciende el LED del aro que corresponde al acorde activo.
// Cada LED tiene el color de su zona en tools/midi_caja.html (tonos 0, 45, 90... 315 grados).
// Con cada golpe el LED destella en blanco. Además el sonido de guitarra sale por el pin 9 (PWM)
// hacia el minijack, y los acordes siguen yendo también por MIDI USB.
// Piezo en A0 (10 kΩ + 2,2 MΩ + diodos de protección). Canal MIDI 1.
#include <MIDIUSB.h>
#include <Adafruit_NeoPixel.h>

const int PIEZO = A0;
const int POT   = A1;

// --- golpe ---
const int THRESHOLD    = 25;     // ruido en reposo máx. 4; golpe suave ~60
const int PEAK_FOR_MAX = 400;    // pico que da velocity 127
const unsigned long SCAN_MS    = 8;     // ventana para medir el pico
const unsigned long LOCKOUT_MS = 50;    // tiempo muerto tras un golpe
const unsigned long NOTE_MS    = 700;   // duración de cada nota
const unsigned long GAP_SOFT   = 45;    // ms entre cuerdas, golpe suave
const unsigned long GAP_HARD   = 10;    // ms entre cuerdas, golpe fuerte
const byte CHANNEL = 0;                 // canal 1

// --- acordes: 8 posiciones del potenciómetro, de izquierda a derecha. 0 = sin nota ---
const int NCH = 8;
const byte CHORDS[NCH][6] = {
  {45, 52, 57, 60, 64, 0},   // Am
  {48, 52, 55, 60, 64, 0},   // C
  {43, 47, 50, 55, 59, 67},  // G
  {50, 57, 62, 66,  0, 0},   // D
  {40, 47, 52, 55, 59, 64},  // Em
  {41, 48, 53, 57, 60, 65},  // F
  {50, 57, 62, 65,  0, 0},   // Dm
  {40, 47, 52, 56, 59, 64}   // E
};
// color de cada LED = el tono de su zona en la página web (hsl(i*45, ...)), a máxima saturación porque en un LED lo pastel se ve blanquecino
// --- potenciómetro logarítmico: se corrige la curva para que las 8 zonas ocupen el mismo giro ---
const float TAPER_DECADES = 2.0;   // 2.0 = curva logarítmica típica. Si las zonas salen desiguales, se ajusta aquí
const float HYST = 0.02;           // 2% del giro de margen entre zonas, para que no parpadee en el borde

// --- barra de LED ---
const int LED_PIN = 10;            // dato (DI) del aro, con 220 ohm en serie, pin 10
const uint8_t BRIGHT = 80;         // 0-255. Con un solo LED encendido se puede subir sin pasar del consumo del USB
Adafruit_NeoPixel bar(NCH, LED_PIN, NEO_GRB + NEO_KHZ800);

// --- estado ---
bool inHit = false, fired = false;
unsigned long tHit = 0, lastHit = 0;
int peak = 0;
byte note_[6]; byte vel_ = 0;
unsigned long onAt[6], offAt[6];
bool pending[6], sounding[6];
bool strumDown = true;
int chordIdx = 0, shownIdx = -1, lastCC = -1;
int flash = 0;                     // 0-254, se apaga solo
unsigned long lastPot = 0, lastFlash = 0;

// ================= sintetizador por PWM (pin 9) =================
// Timer1 genera el PWM rápido (62,5 kHz) y Timer3 marca el ritmo de muestras (15625 Hz).
const uint16_t FS = 15625;
const byte OUT_SHIFT = 2;          // volumen de salida: 0 = fuerte, 1, 2 = medio, 3 = bajo (se sube o baja aquí)
int8_t wave[256];                  // un ciclo de onda con timbre de cuerda pulsada
volatile uint16_t vPhase[6], vInc[6];
volatile uint16_t vEnv[6];         // envolvente (0-32767)
volatile uint8_t vDecay[6];        // cuanto mayor, más rápido se apaga
volatile bool vOn[6];
uint8_t tick = 0;

ISR(TIMER3_COMPA_vect) {
  int16_t mix = 0;
  tick++;
  for (uint8_t i = 0; i < 6; i++) {
    if (!vOn[i]) continue;
    vPhase[i] += vInc[i];
    uint8_t e = vEnv[i] >> 8;                                   // 0-127
    mix += ((int16_t)wave[vPhase[i] >> 8] * e) >> 7;
    if ((tick & 7) == 0) {                                       // la envolvente baja cada 8 muestras
      vEnv[i] -= vEnv[i] >> vDecay[i];
      if (vEnv[i] < 64) vOn[i] = false;
    }
  }
  mix >>= OUT_SHIFT;
  if (mix > 127) mix = 127; else if (mix < -127) mix = -127;
  OCR1A = 128 + mix;
}

void synthBegin() {
  for (int i = 0; i < 256; i++) {                                // fundamental + armónicos que se apagan = cuerda
    float a = 2.0 * PI * i / 256.0;
    float v = sin(a) + 0.55 * sin(2 * a) + 0.35 * sin(3 * a) + 0.2 * sin(4 * a) + 0.1 * sin(5 * a);
    wave[i] = (int8_t)(v * 50);
  }
  pinMode(9, OUTPUT);
  TCCR1A = _BV(COM1A1) | _BV(WGM10);                             // PWM rápido de 8 bits en el pin 9
  TCCR1B = _BV(WGM12) | _BV(CS10);
  OCR1A = 128;
  TCCR3A = 0; TCCR3B = _BV(WGM32) | _BV(CS30);                   // Timer3 en CTC, sin divisor
  OCR3A = 16000000UL / FS - 1;
  TIMSK3 = _BV(OCIE3A);
}

void synthOn(byte slot, byte note, byte vel) {
  float f = 440.0 * pow(2.0, (note - 69) / 12.0);
  noInterrupts();
  vInc[slot] = (uint16_t)(f * 65536.0 / FS);
  vPhase[slot] = 0;
  vEnv[slot] = (uint16_t)vel * 256;
  vDecay[slot] = 9;                                              // sostenido de guitarra
  vOn[slot] = true;
  interrupts();
}

void synthOff(byte slot) { vDecay[slot] = 5; }                   // al soltar la nota se apaga rápido

void drawBar() {
  shownIdx = chordIdx;
  for (int i = 0; i < NCH; i++) {
    if (i != chordIdx) { bar.setPixelColor(i, 0); continue; }                         // solo luce el acorde activo
    uint32_t c = bar.gamma32(bar.ColorHSV((uint32_t)i * 65536L / NCH));               // tono = 45 grados por zona
    int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
    bar.setPixelColor(i, bar.Color(min(255, r + flash), min(255, g + flash), min(255, b + flash)));   // destello del golpe
  }
  bar.show();
}

void send(bool on, byte note, byte vel) {
  midiEventPacket_t p = { (byte)(on ? 0x09 : 0x08), (byte)((on ? 0x90 : 0x80) | CHANNEL), note, vel };
  MidiUSB.sendMIDI(p);
  MidiUSB.flush();
}

float turn(int v) {   // posición del mando (0..1) a partir de la lectura, deshaciendo la curva logarítmica
  return log10(1.0 + (pow(10.0, TAPER_DECADES) - 1.0) * v / 1023.0) / TAPER_DECADES;
}

void readPot() {
  long sum = 0;
  for (int i = 0; i < 8; i++) sum += analogRead(POT);
  float x = turn(sum / 8);
  float lo = (float)chordIdx / NCH - HYST, hi = (float)(chordIdx + 1) / NCH + HYST;
  if (x < lo || x >= hi) chordIdx = constrain((int)(x * NCH), 0, NCH - 1);
  int cc = (int)(x * 127.0 + 0.5);                   // posición del mando para la página MIDI
  if (cc != lastCC) {
    midiEventPacket_t p = { 0x0B, (byte)(0xB0 | CHANNEL), 20, (byte)cc };
    MidiUSB.sendMIDI(p); MidiUSB.flush();
    lastCC = cc;
  }
  analogRead(PIEZO);   // lectura de descarte tras cambiar de canal
}

void cutAll() {
  for (int i = 0; i < 6; i++) {
    if (sounding[i]) { send(false, note_[i], 0); synthOff(i); sounding[i] = false; }
    pending[i] = false;
  }
}

void startChord(byte vel, unsigned long now) {
  cutAll();
  unsigned long gap = GAP_SOFT - (GAP_SOFT - GAP_HARD) * (unsigned long)vel / 127;
  int k = 0;
  for (int i = 0; i < 6; i++) {
    int src = strumDown ? i : 5 - i;                 // abajo y arriba alternados
    byte nt = CHORDS[chordIdx][src];
    if (!nt) continue;
    note_[k] = nt; onAt[k] = now + k * gap; offAt[k] = onAt[k] + NOTE_MS;
    pending[k] = true; sounding[k] = false; k++;
  }
  vel_ = vel;
  strumDown = !strumDown;
  flash = vel * 2;
  drawBar();
}

void serviceNotes(unsigned long now) {
  for (int i = 0; i < 6; i++) {
    if (pending[i] && now >= onAt[i]) { send(true, note_[i], vel_); synthOn(i, note_[i], vel_); pending[i] = false; sounding[i] = true; }
    if (sounding[i] && now >= offAt[i]) { send(false, note_[i], 0); synthOff(i); sounding[i] = false; }
  }
}

void setup() {
  synthBegin();
  bar.begin();
  bar.setBrightness(BRIGHT);
  drawBar();
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
      startChord(vel, now);
    }
    if (v < THRESHOLD / 2) { inHit = false; lastHit = now; }
  }

  serviceNotes(now);
  if (now - lastPot >= 25 && !inHit) { lastPot = now; readPot(); if (chordIdx != shownIdx) drawBar(); }
  if (flash > 0 && !inHit && now - lastFlash >= 20) {   // el destello se apaga en ~100 ms
    lastFlash = now; flash = flash > 40 ? flash - 40 : 0; drawBar();
  }
}
