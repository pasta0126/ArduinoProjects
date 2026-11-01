// Paso 2: cada golpe al piezo = una nota MIDI con velocity según la fuerza.
// Piezo en A0 (10 kΩ en serie + 2,2 MΩ a GND). Placa: Arduino Micro / Pro Micro (ATmega32U4).
// Valores sacados de las pruebas: ruido en reposo máx. 4, golpe suave ~60, golpe firme ~490.
#include <MIDIUSB.h>

const int  PIEZO         = A0;
const int  THRESHOLD     = 25;    // por encima de esto empieza un golpe
const int  PEAK_FOR_MAX  = 400;   // pico que da velocity 127 (más bajo = más sensible)
const unsigned long SCAN_MS    = 8;    // ventana para medir el pico antes de disparar
const unsigned long LOCKOUT_MS = 50;   // tiempo muerto tras un golpe
const unsigned long NOTE_MS    = 80;   // duración de la nota
const byte CHANNEL = 9;                // canal 10 (se cuenta desde 0)
const byte NOTE    = 38;               // 38 = caja (snare) en el kit estándar

bool inHit = false, fired = false, noteIsOn = false;
unsigned long tHit = 0, lastHit = 0, noteOffAt = 0;
int peak = 0;

void sendNote(bool on, byte vel) {
  midiEventPacket_t p = { (byte)(on ? 0x09 : 0x08), (byte)((on ? 0x90 : 0x80) | CHANNEL), NOTE, vel };
  MidiUSB.sendMIDI(p);
  MidiUSB.flush();
}

void setup() {}

void loop() {
  int v = analogRead(PIEZO);
  unsigned long now = millis();

  if (!inHit) {
    if (v >= THRESHOLD && now - lastHit >= LOCKOUT_MS) {
      inHit = true; fired = false; peak = v; tHit = now;
    }
  } else {
    if (v > peak) peak = v;
    if (!fired && now - tHit >= SCAN_MS) {
      fired = true;
      byte vel = constrain(map(peak, THRESHOLD, PEAK_FOR_MAX, 1, 127), 1, 127);
      if (noteIsOn) sendNote(false, 0);
      sendNote(true, vel);
      noteIsOn = true; noteOffAt = now + NOTE_MS;
    }
    if (v < THRESHOLD / 2) { inHit = false; lastHit = now; }   // se rearma al bajar la señal
  }

  if (noteIsOn && now >= noteOffAt) { sendNote(false, 0); noteIsOn = false; }
}
