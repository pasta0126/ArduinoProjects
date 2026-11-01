// Paso 3: cada golpe toca un ACORDE (varias notas MIDI rasgueadas).
// El potenciómetro (A1) elige el acorde. Piezo en A0 (10 kΩ + 2,2 MΩ + diodos de protección).
// Canal MIDI 1 (instrumentos). Para la caja de batería usa el sketch 02.
#include <MIDIUSB.h>

const int PIEZO = A0;
const int POT   = A1;

const int THRESHOLD    = 25;     // ruido en reposo máx. 4; golpe suave ~60
const int PEAK_FOR_MAX = 400;    // pico que da velocity 127
const unsigned long SCAN_MS    = 8;     // ventana para medir el pico
const unsigned long LOCKOUT_MS = 50;    // tiempo muerto tras un golpe
const unsigned long NOTE_MS    = 700;   // duración de cada nota
const unsigned long GAP_SOFT   = 45;    // ms entre cuerdas, golpe suave
const unsigned long GAP_HARD   = 10;    // ms entre cuerdas, golpe fuerte
const byte CHANNEL = 0;                 // canal 1

// 6 acordes (de izquierda a derecha del potenciómetro). 0 = sin nota.
const byte CHORDS[6][6] = {
  {45, 52, 57, 60, 64, 0},   // Am
  {48, 52, 55, 60, 64, 0},   // C
  {43, 47, 50, 55, 59, 67},  // G
  {50, 57, 62, 66,  0, 0},   // D
  {40, 47, 52, 55, 59, 64},  // Em
  {41, 48, 53, 57, 60, 65}   // F
};

// estado del golpe
bool inHit = false, fired = false;
unsigned long tHit = 0, lastHit = 0;
int peak = 0;

// notas pendientes y sonando (rasgueo)
byte note_[6]; byte vel_ = 0;
unsigned long onAt[6], offAt[6];
bool pending[6], sounding[6];
bool strumDown = true;

int chordIdx = 0;
unsigned long lastPot = 0;

void send(bool on, byte note, byte vel) {
  midiEventPacket_t p = { (byte)(on ? 0x09 : 0x08), (byte)((on ? 0x90 : 0x80) | CHANNEL), note, vel };
  MidiUSB.sendMIDI(p);
  MidiUSB.flush();
}

void readPot() {
  long sum = 0;
  for (int i = 0; i < 8; i++) sum += analogRead(POT);
  int v = sum / 8;
  int lo = chordIdx * 1024 / 6, hi = (chordIdx + 1) * 1024 / 6;
  if (v < lo - 12 || v >= hi + 12) chordIdx = constrain(v * 6 / 1024, 0, 5);   // histéresis: evita saltos en el borde
  analogRead(PIEZO);   // lectura de descarte tras cambiar de canal
}

void cutAll() {
  for (int i = 0; i < 6; i++) {
    if (sounding[i]) { send(false, note_[i], 0); sounding[i] = false; }
    pending[i] = false;
  }
}

void startChord(byte vel, unsigned long now) {
  cutAll();
  unsigned long gap = GAP_SOFT - (GAP_SOFT - GAP_HARD) * (unsigned long)vel / 127;
  int n = 0;
  for (int i = 0; i < 6; i++) if (CHORDS[chordIdx][i]) n++;
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
}

void serviceNotes(unsigned long now) {
  for (int i = 0; i < 6; i++) {
    if (pending[i] && now >= onAt[i]) { send(true, note_[i], vel_); pending[i] = false; sounding[i] = true; }
    if (sounding[i] && now >= offAt[i]) { send(false, note_[i], 0); sounding[i] = false; }
  }
}

void setup() {}

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
  if (now - lastPot >= 25 && !inHit) { lastPot = now; readPot(); }
}
