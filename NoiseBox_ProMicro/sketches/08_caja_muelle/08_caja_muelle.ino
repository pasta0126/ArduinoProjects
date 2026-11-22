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
// Monitor serie (115200): imprime la fuerza de cada golpe, para ajustar THRESHOLD, y la onda del piezo
// ("piezo:N", 500 por segundo) para verla en tools/osciloscopio.html mientras suena.
#include <MIDIUSB.h>

const int PIEZO = A0;
const int LED_R = 5, LED_G = 6, LED_B = 4;
const bool COMMON_ANODE = true;      // tu LED es de ánodo común: la pata larga va a VCC (5 V) por la 220 Ω

// --- golpe ---
const int THRESHOLD    = 25;         // por debajo de esto es ruido. Sube si dispara solo, baja si no detecta golpes suaves
const int PEAK_FOR_MAX = 600;        // pico que se considera golpe máximo (con el muelle casi todos dan 40-250)
const byte MIN_LOUD    = 90;         // volumen del golpe más suave (de 127): así ningún golpe detectado suena a nada
const unsigned long SCAN_MS    = 8;  // ventana para medir el pico
const unsigned long LOCKOUT_MS = 100; // tiempo muerto tras un golpe

// --- MIDI ---
const byte MIDI_NOTE = 38, CHANNEL = 9;   // caja (snare), canal 10
const unsigned long MIDI_LEN = 150;

// ================= sintetizador por PWM (pin 9) =================
// Timer1: PWM rápido de 8 bits (62,5 kHz) en el pin 9. Timer3: 15625 muestras por segundo.
const uint16_t FS = 15625;
const byte OUT_SHIFT = 0;            // volumen: 0 = fuerte (la 10 kΩ del jack ya lo baja), 1 = medio, 2 = bajo
const float RATIO[3] = {1.0, 2.0, 3.0};         // armónicos: nota, octava y quinta encima = suena afinado
const byte  SCALE[5] = {0, 3, 5, 7, 10};        // pentatónica menor (La, Do, Re, Mi, Sol): cualquier par de notas suena bien
const byte  NSTEPS   = 13;                       // notas disponibles: 2 octavas y media desde La1 (55 Hz)
const byte  LEVEL[3] = {200, 50, 20};            // casi todo nota pura (seno); octava y quinta solo dan calidez. Suma sin saturar
int8_t sine[256];
volatile uint16_t ph[3], inc[3], env[3], nEnv;
// --- envolvente con forma de tus dibujos ---
// Subida y bajada con curva en S (smoothstep 3x²-2x³): empiezan despacio, van ganando y llegan
// despacio. Nada entra ni sale de golpe. Cada parcial sube y baja por su cuenta.
enum { E_OFF, E_UP, E_DOWN, E_HOLD };   // E_HOLD: sigue al frotado, despacio
volatile uint8_t  eMode[3];          // apagado, subiendo o bajando
volatile uint16_t ePos[3], eRate[3]; // posición en la curva (0..65535) y cuánto avanza cada 0,5 ms
volatile uint16_t e0[3], tgt[3];     // subida: de e0 a tgt.  Bajada: de tgt a 0
volatile uint16_t relRate[3];        // velocidad de la bajada de este golpe
uint8_t sCurve[256];                 // curva en S precalculada (0..255)
inline uint8_t ease8(uint16_t x) { return sCurve[x >> 8]; }
inline uint16_t msToRate(uint16_t ms) { return (uint16_t)(65536UL * 512 / (ms * 1000UL)); }   // pasos de 0,512 ms
inline void startAtk(uint8_t i, uint16_t t, uint16_t rate) {   // llamar con interrupciones paradas
  e0[i] = env[i]; tgt[i] = t; ePos[i] = 0; eRate[i] = rate; eMode[i] = E_UP;
}
uint16_t atkRate = 1500;             // subida del golpe actual (la elige la serie de Fibonacci)

// --- FM: el muelle "dobla" la onda. Un segundo seno empuja la fase de la nota; cuanto más vibra
// el muelle, más empuja, y a la onda le salen jorobas redondas. Muelle quieto = seno casi limpio.
volatile uint16_t pm = 0, pmInc = 0;  // fase y paso del modulador
volatile uint8_t fmIdx = 0;          // cuánto empuja (0 = seno puro)
int16_t fmCur = 0;                   // fmIdx suavizado dentro de la interrupción (×128)
uint16_t bias = 0;                   // centro de la onda (×256): 0 en silencio, 128 sonando
uint8_t qErr = 0;                    // resto del redondeo a 8 bits
volatile uint8_t tremG = 255;        // trémolo: volumen extra 0..255 (lo calcula loop() cada ms)
volatile uint8_t breath = 0;         // soplo: un poco de ruido suave encima de la nota (0..30)
int16_t nzLP = 0;                    // ruido filtrado (más oscuro, como aire)
byte  fmRatio = 2;                   // 1, 2 o 3 veces la nota: cambia la forma de las jorobas
const byte FM_REST  = 10;            // un poco de curva siempre (calidez)
const byte FM_SPRING = 150;          // máximo en el pico del muelle
float fmS = 0;

// --- foto de la onda para el osciloscopio: 256 muestras del sonido, una de cada 2 (33 ms) ---
const byte SNAP_DIV = 2;
volatile uint8_t snap[256];
volatile uint16_t snapIdx = 256;     // 256 = no está capturando
uint8_t snapDiv = 0;
volatile uint8_t ampOut = 0;
volatile uint16_t isrMax = 0;        // lo más que ha tardado el cuerpo de la interrupción (ciclos; el límite es 1024)         // volumen actual del sonido (0..127)
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
  uint16_t c0 = TCNT3;                           // para medir cuánto tarda (sin contar la espera)
  // LED: un color por turno; cada color reparte sus encendidos de forma uniforme (sin parpadeo)
  ledsOff();
  if (++slot == 3) slot = 0;
  acc[slot] += duty[slot];
  if (acc[slot] >= 256) { acc[slot] -= 256; ledOn(slot); }

  int16_t mixF = 0;                              // la onda, con 8 bits de decimales (cabe justo en 16 bits)
  uint8_t amp = 0;
  uint8_t tk = ++tick & 7;
  fmCur += ((int16_t)(fmIdx << 7) - fmCur) >> 6;  // las jorobas cambian muestra a muestra (~4 ms), sin escalones
  for (uint8_t i = 0; i < 3; i++) {
    uint8_t mode = eMode[i];
    if (mode == E_OFF) continue;
    uint16_t e = env[i];
    uint16_t p = (ph[i] += inc[i]);
    if (i == 0) { pm += pmInc; p += (int16_t)sine[pm >> 8] * (uint8_t)(fmCur >> 7); }   // la nota principal se dobla con el muelle
    mixF += (int16_t)sine[p >> 8] * (uint8_t)(e >> 7);   // multiplicación de 8 bits: rápida
    amp += (e >> 8) + 1;                         // un poco más que el pico real: la onda nunca se sale
    if (tk == i) {                               // cada parcial se actualiza en una muestra distinta (reparte el trabajo)
      uint16_t op = ePos[i], np = op + eRate[i];
      ePos[i] = np;
      if (mode == E_UP) {                        // subida: despacio al principio, rápida al final
        if (np < op) { e = tgt[i]; eMode[i] = E_DOWN; ePos[i] = 0; eRate[i] = relRate[i]; }
        else e = e0[i] + ((tgt[i] - e0[i]) >> 8) * ease8(np);
      } else if (mode == E_HOLD) {               // frotando: la nota sigue la energía media, sin saltos (~33 ms)
        int16_t d = (int16_t)tgt[i] - (int16_t)e;
        int16_t s7 = d >> 6;                     // ~33 ms
        e += s7 ? s7 : (d > 0 ? 1 : (d < 0 ? -1 : 0));
      } else {                                   // bajada: se sostiene y luego cae cada vez más deprisa
        if (np < op) { e = 0; eMode[i] = E_OFF; }
        else e = tgt[i] - (tgt[i] >> 8) * ease8(np);
      }
      env[i] = e;
    }
  }
  ampOut = amp > 127 ? 127 : amp;
  if (breath && amp) {                           // soplo: ruido pasado por un filtro suave
    lfsr = (lfsr >> 1) ^ (-(lfsr & 1) & 0xB400);
    nzLP += ((int8_t)(lfsr & 0xFF) - nzLP) >> 2;
    mixF += nzLP * breath;
  }
  mixF = ((int32_t)mixF * tremG) >> 8;           // trémolo

  // Centro de la onda: sube despacio (~45 ms) cuando empieza a sonar, se queda quieto mientras suena
  // y baja muy despacio (~1/4 s) al acabar. Así el centro no da golpes sordos con cada rebote.
  uint16_t bs = bias;
  if (amp > 0) { if (bs < 32640 - 48) bs += 48; else bs = 32640; }
  else if (bs > 0) bs -= bs > 8 ? 8 : bs;
  bias = bs;
  int16_t lim = bs;
  if (mixF > lim) mixF = lim; else if (mixF < -lim) mixF = -lim;
  if (snapIdx < 256 && ++snapDiv >= SNAP_DIV) { snapDiv = 0; snap[snapIdx++] = 128 + (mixF >> 8); }

  if (bs == 0) {                                 // silencio: pin 9 a 0 V fijo (sin pitido del LED)
    TCCR1A &= ~_BV(COM1A1);
    qErr = 0;
  } else {
    // 8 bits de salida con los decimales "repartidos" en las muestras siguientes (dither):
    // los sonidos bajitos y las colas salen suaves en vez de granulados.
    uint16_t v = bs + mixF + qErr;               // 0..65535
    OCR1A = v >> 8;
    qErr = v & 0xFF;
    TCCR1A |= _BV(COM1A1);
  }
  uint16_t c = TCNT3 - c0; if (c > isrMax) isrMax = c;
}

void synthBegin() {
  for (int i = 0; i < 256; i++) sine[i] = (int8_t)(120 * sin(2 * PI * i / 256.0));
  for (int i = 0; i < 256; i++) { float x = i / 255.0; sCurve[i] = (uint8_t)(255 * x * x * (3 - 2 * x) + 0.5); }
  pinMode(9, OUTPUT);
  TCCR1A = _BV(COM1A1) | _BV(WGM10);             // PWM rápido 8 bits en el pin 9
  TCCR1B = _BV(WGM12) | _BV(CS10);
  OCR1A = 0; digitalWrite(9, LOW);
  TCCR3A = 0; TCCR3B = _BV(WGM32) | _BV(CS30);   // Timer3 en CTC, sin divisor
  OCR3A = 16000000UL / FS - 1;
  TIMSK3 = _BV(OCIE3A);
}

float baseHz = 100;                  // tono del golpe actual
float ratioNow[3] = {1.0, 2.0, 3.0};
float glideDepth = 0.6, glideTau = 60;
unsigned long tBoing = 0;
bool boinging = false;
byte lvCur[3] = {210, 120, 70};
byte noteDeg = 0;                    // grado de la escala del último golpe (0..4): da el color del LED      // nivel de cada parcial del golpe actual

// --- seguimiento del muelle: lo que vibra después del golpe ---
const int   NOISE  = 6;              // por debajo, el piezo está quieto (en reposo lee 0-3)
const float WOBBLE = 0.015;           // cuánto sube el tono cuando el muelle empuja (el "oing-oing")
const float SUSTAIN = 0.85;          // nivel de la vibración frente al golpe
float ef = 0;                        // envolvente rápida del piezo (sigue cada rebote, ~16 ms)
float efS = 0;
// --- energía media del frotado: la media de ~0,1 s, con las puntas recortadas ---
// Las puntas sueltas (las que veías en la gráfica) no cuentan más de 3× la media: dan vida, pero no hacen "pum".
float E = 0, kE = 0;                 // energía y su valor 0..1 (escala logarítmica)
float slopeE = 0, Epred = 0;         // pendiente de la energía (por ms) y energía prevista dentro de 0,1 s
const float NOISE_E = 4, E_MAX = 150;
bool  phraseOn = false;              // se está frotando (frase en curso)
int   phraseStep = 0, phraseOff = 0; // nota de la frase
unsigned long stepSince = 0;         // desde cuándo la energía pide otra nota
float baseHzCur = 110;               // tono que suena de verdad: va hacia baseHz con un legato suave                       // la misma, redondeada (~10 ms): mueve el tono, las jorobas y el sustain sin saltos
float es = 0;                        // envolvente lenta (~80 ms): sirve para no confundir rebotes con golpes nuevos
int hitPeak = 100;

// ---- variaciones con Fibonacci y el número áureo (φ = 1,618…) ----
// No es azar: es una serie que nunca se repite igual pero siempre "encaja", como las hojas de una planta.
const float PHI = 1.6180340;
const uint16_t FIB_UP[5]   = {89, 144, 233, 377, 610};  // subidas posibles (ms): la nota "crece"
const uint16_t FIB_DOWN[5] = {458, 740, 1198, 1938, 3136};  // 3/4 de 610, 987, 1597, 2584, 4181  // bajadas posibles (ms): la nota "se va"
uint16_t hitN = 0;                   // número de golpe
byte fa = 0, fb = 1;                 // Fibonacci módulo 3 (0,1,1,2,0,2,2,1,…): elige la forma de las jorobas
float golden(float k) { float x = hitN * k; return x - floor(x); }   // 0..1, reparto áureo

float rnd(float a) { return a * (random(-1000, 1001) / 1000.0); }   // aleatorio entre -a y +a

// Cada golpe es distinto: la fuerza cambia el tono (más de 2 octavas), el brillo (parciales agudos),
// la duración y la caída del tono; además cada golpe lleva un poco de azar para que no se repita.
uint16_t hue = 0;                    // 0..1535 (6 tramos de 256)
float tremPh = 0, tremRate = 4.8, tremDepth = 0.10;   // Hz y profundidad (0,10 = el volumen baja hasta un 10 %)
// ---- variedad: si las últimas notas se parecen mucho, salta a otra de la escala ----
int8_t hist[3] = {-9, -9, -9};       // últimas notas (pasos)
int vary(int st) {
  bool similar = abs(st - hist[0]) <= 1 && abs(hist[0] - hist[1]) <= 1;
  if (similar || random(100) < 20) {             // repetitivo, o 1 de cada 5 por sorpresa
    static const int8_t J[6] = {2, -2, 3, -3, 5, -5};   // saltos de escala; ±5 = una octava
    st += J[random(6)];
    while (st < 0) st += 5;
    while (st >= NSTEPS) st -= 5;
  }
  hist[2] = hist[1]; hist[1] = hist[0]; hist[0] = st;
  return st;
}

// color: cada nota nueva cambia un poco el timbre (forma de las jorobas y desafinado de los armónicos)
void colorNote() {
  if (random(100) < 50) fmRatio = random(1, 4);
  ratioNow[1] = RATIO[1] * (1.0 + rnd(0.008));
  ratioNow[2] = RATIO[2] * (1.0 + rnd(0.012));
  tremDepth = constrain(tremDepth + rnd(0.04), 0.05, 0.16);
}

void setNote(int step, bool instant) {   // fija la nota (paso de la escala pentatónica)
  noteDeg = step % 5;
  int semis = (step / 5) * 12 + SCALE[noteDeg];
  baseHz = 55.0 * pow(2.0, semis / 12.0);
  if (instant) baseHzCur = baseHz;
  hue = (uint16_t)noteDeg * 307;     // cada nota de la escala tiene su color
}

void boing(byte vel) {               // vel 1..127
  float v = vel / 127.0;
  // la fuerza elige la nota de la escala (más fuerte = más aguda), con un paso arriba o abajo al azar
  hitN++;
  float g1 = golden(1 / PHI), g2 = golden(1 / (PHI * PHI)), g3 = golden(1 / (PHI * PHI * PHI));
  // la fuerza elige la zona de la escala; el reparto áureo la mueve un paso arriba, abajo o nada
  int step = vary(constrain((int)(v * (NSTEPS - 1) + 0.5) + (int)(g1 * 3) - 1, 0, NSTEPS - 1));
  setNote(step, ampOut == 0);                               // si ya sonaba algo, pasa a la nota con legato
  phraseOn = true; phraseStep = step; phraseOff = 0; stepSince = 0;
  glideDepth = 0;                                           // sin caída de tono: la nota entra ya afinada (sin "ti")
  glideTau = 40 + 80 * v;                                   // fuerte: la caída dura más
  ratioNow[0] = 1.0;
  byte fc = (fa + fb) % 3; fa = fb; fb = fc;                // Fibonacci módulo 3
  fmRatio = fc + 1;                                         // forma de las jorobas: 1, 2 o 3
  // subida: los golpes suaves entran más lentos; el reparto áureo varía entre 8 y 55 ms
  atkRate = msToRate(FIB_UP[constrain((int)((1 - v) * 2.5 + g2 * 2.5), 0, 4)]);
  // bajada: los golpes fuertes duran más; entre 0,3 y 2,1 s
  uint16_t downMs = FIB_DOWN[constrain((int)(v * 2.5 + g3 * 2.5), 0, 4)];
  colorNote();
  byte loud = MIN_LOUD + (uint16_t)vel * (127 - MIN_LOUD) / 127;   // el volumen nunca baja de MIN_LOUD
  byte lv[3] = {LEVEL[0], (byte)(LEVEL[1] * (0.35 + 0.65 * v)), (byte)(LEVEL[2] * (0.15 + 0.85 * v))};  // fuerte = más brillo
  tBoing = millis(); boinging = true;
  noInterrupts();
  // sin reiniciar la fase: si aún sonaba el golpe anterior, la onda sigue sin saltos
  // los armónicos se apagan antes, en proporción áurea: octava a 0,618 y quinta a 0,382 del tiempo
  uint16_t rr[3] = {msToRate(downMs), msToRate(downMs / PHI), msToRate(downMs / (PHI * PHI))};
  for (int i = 0; i < 3; i++) {
    lvCur[i] = lv[i]; relRate[i] = rr[i];
    uint16_t t = (uint16_t)loud * lv[i];
    if (t > env[i]) startAtk(i, t, atkRate);
  }
  nEnv = 0;                                                 // sin ruido al principio: el golpe entra redondo
  interrupts();
  glide();
}

float human = 1.0;                   // toque humano: multiplica el tono (lo calcula humanize())
void glide() {                       // el tono cae como un muelle: empieza más agudo y baja
  float t = (millis() - tBoing) / glideTau;
  float w = kE;                      // el tono se mueve (muy poco) con la energía media
  baseHzCur += (baseHz - baseHzCur) * 0.04;   // legato: ~50 ms para pasar de una nota a otra
  // respiración: dos ondas lentas de 2 s y 2·φ = 3,24 s. Como su relación es φ, nunca coinciden igual
  float ms = millis();
  float lfo = 0.5 * sin(ms * (2 * PI / 2000.0)) + 0.5 * sin(ms * (2 * PI / (2000.0 * PHI)));
  float g = (1.0 + glideDepth * exp(-t)) * (1.0 + WOBBLE * w) * (1.0 + 0.004 * lfo) * human;
  if (t > 6 && E < NOISE_E && ampOut == 0) boinging = false;
  for (int i = 0; i < 3; i++) {
    uint16_t v = (uint16_t)(baseHzCur * g * ratioNow[i] * 65536.0 / FS);
    noInterrupts(); inc[i] = v; if (i == 0) pmInc = v * fmRatio; interrupts();
  }
}

// Mientras el muelle sigue vibrando, le da energía al sonido: no se apaga hasta que el muelle para.
// Las vibraciones pequeñas suenan bajito; las grandes, fuerte.
void sustain() {
  if (Epred < NOISE_E) {             // se dejó de frotar (o se prevé que en 0,1 s ya no habrá energía): lo que seguía al frotado se despide con su bajada
    noInterrupts();
    for (int i = 0; i < 3; i++) if (eMode[i] == E_HOLD) { tgt[i] = env[i]; ePos[i] = 0; eRate[i] = relRate[i]; eMode[i] = E_DOWN; }
    interrupts();
    return;
  }
  float a = kE * 127 * SUSTAIN;
  for (int i = 0; i < 3; i++) {
    uint16_t target = (uint16_t)(a * lvCur[i]);
    noInterrupts();
    if (eMode[i] == E_HOLD) tgt[i] = target;
    else if (eMode[i] != E_UP && target > env[i] + 256) { tgt[i] = target; eMode[i] = E_HOLD; }   // engancha sin saltos
    interrupts();
  }
  boinging = true;
}

// ---- toque humano: trémolo y pequeñas imperfecciones ----
// Como una voz o un violín: el trémolo no empieza con la nota, aparece poco a poco (~0,4 s),
// y su velocidad y profundidad cambian solas, despacio y al azar. El tono también deriva un pelín.
float drift = 0;                     // deriva lenta del tono (±0,3 % ≈ ±5 cents)
void humanize(unsigned long now) {
  tremRate  = constrain(tremRate  + rnd(0.03),  3.5, 6.5);
  tremDepth = constrain(tremDepth + rnd(0.002), 0.05, 0.16);
  drift     = constrain(drift     + rnd(0.00006), -0.003, 0.003);
  tremPh += 2 * PI * tremRate / 1000.0;
  if (tremPh > 2 * PI) tremPh -= 2 * PI;
  float onset = min(1.0, (now - tBoing) / 400.0);
  float sn = sin(tremPh);
  tremG = (uint8_t)(255 * (1 - tremDepth * onset * (0.5 + 0.5 * sn)));
  human = 1 + drift + 0.0012 * onset * sn;           // un vibrato muy leve, a la vez que el trémolo
}

// ================= LED RGB =================
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

// manda la foto como "onda:" + 256 valores en hexadecimal (2 letras cada uno), en trozos de 64
bool snapPending = false;
unsigned long tSnap = 0;
void sendSnap() {
  if (!Serial) return;
  const char *H = "0123456789ABCDEF";
  char b[64];
  Serial.print("onda:");
  for (int i = 0; i < 256; i += 32) {
    for (int j = 0; j < 32; j++) { uint8_t v = snap[i + j]; b[2 * j] = H[v >> 4]; b[2 * j + 1] = H[v & 15]; }
    Serial.write(b, 64);
  }
  Serial.println();
}

// ================= principal =================
bool inHit = false, fired = false, noteOn = false;
unsigned long tHit = 0, lastHit = 0, tNote = 0, lastLed = 0, lastGlide = 0, tFollow = 0, tScope = 0;
int scopeMax = 0;                    // pico de los últimos 2 ms, para tools/osciloscopio.html
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
  randomSeed(analogRead(A1) ^ micros());
  ledTest();
}

void loop() {
  unsigned long now = millis();
  int v = analogRead(PIEZO);

  if (!inHit) {
    // golpe nuevo: tiene que pasar el umbral Y destacar sobre lo que ya vibraba (si no, es un rebote)
    // golpe de verdad: muy por encima de la energía media del frotado (las puntas del frotado no llegan)
    if (v >= THRESHOLD && now - lastHit >= LOCKOUT_MS && v > 2.5 * E + 40) { inHit = true; fired = false; peak = v; tHit = now; }
  } else {
    if (v > peak) peak = v;
    if (!fired && now - tHit >= SCAN_MS) {
      fired = true;
      // escala logarítmica: los picos van de 30 a 1000, y así los suaves y los medios se distinguen
      float k = log((float)peak / THRESHOLD) / log((float)PEAK_FOR_MAX / THRESHOLD);
      byte vel = constrain((int)(1 + 126 * k), 1, 127);
      boing(vel); hitPeak = peak;
      flash = 60 + vel * 3 / 2;                  // hasta 250
      if (noteOn) midi(false, 0);
      midi(true, vel); noteOn = true; tNote = now;
      Serial.print("golpe "); Serial.print(peak); Serial.print("  vel "); Serial.print(vel); Serial.print("  nota "); Serial.print(noteDeg); Serial.print("  hz "); Serial.println((int)baseHz);
    }
    if (v < THRESHOLD / 2) { inHit = false; lastHit = now; }
  }

  // osciloscopio: manda la onda 500 veces por segundo ("piezo:N"). Solo escribe si hay hueco en el USB,
  // así el sonido no se corta aunque nadie esté leyendo el puerto.
  if (v > scopeMax) scopeMax = v;
  if (now - tScope >= 2) {
    tScope = now;
    if (Serial && Serial.availableForWrite() >= 20) {
      // una sola escritura por línea (cada print suelto es un paquete USB y frena todo)
      char b[36] = "piezo:";
      itoa(scopeMax, b + 6, 10);
      strcat(b, " son:");
      itoa(ampOut, b + strlen(b), 10);
      static unsigned long tIsr = 0;
      if (now - tIsr >= 500) { tIsr = now; strcat(b, " isr:"); noInterrupts(); uint16_t m = isrMax; isrMax = 0; interrupts(); itoa(m, b + strlen(b), 10); }
      strcat(b, "\r\n");
      Serial.write(b, strlen(b));
    }
    scopeMax = 0;
  }

  // seguimiento del muelle, 1000 veces por segundo
  if (v > ef) ef = v;
  if (now != tFollow) {
    tFollow = now;
    ef -= ef * 0.06;                 // ~16 ms
    es += (ef - es) * 0.0125;        // ~80 ms
    // FM: sigue los picos del muelle, suavizado ~6 ms para que las jorobas entren y salgan redondas
    efS += (ef - efS) * 0.1;         // ~10 ms
    humanize(now);
    // energía media: puntas recortadas a 2× la media, y media de ~0,1 s
    float in = min(ef, 3 * E + 30);              // término medio: las puntas cuentan algo más que antes
    float Eold = E;
    E += (in - E) * (in < E ? 0.014 : 0.01);     // media de ~0,1 s; al bajar, algo más rápida
    // predicción de caída: si la energía va bajando, se mira 0,1 s hacia delante (E + pendiente × 100 ms)
    // y se usa ese valor: el sonido baja antes y llega antes al silencio
    slopeE += ((E - Eold) - slopeE) * 0.05;
    float Ep = slopeE < 0 ? max(0.0, E + slopeE * 60) : E;   // mira 60 ms adelante
    kE = Ep > NOISE_E ? min(1.0, log(Ep / NOISE_E) / log(E_MAX / NOISE_E)) : 0;
    Epred = Ep;
    // la nota del frotado: se elige al empezar y solo cambia si la energía pide otra durante 0,2 s seguidos
    if (E > NOISE_E) {
      int st = constrain((int)(kE * (NSTEPS - 1) + 0.5) + phraseOff, 0, NSTEPS - 1);
      if (!phraseOn) {
        phraseOn = true; hitN++;
        phraseOff = (int)(golden(1 / PHI) * 3) - 1;     // el reparto áureo elige un paso arriba, abajo o nada
        st = constrain((int)(kE * (NSTEPS - 1) + 0.5) + phraseOff, 0, NSTEPS - 1);
        phraseStep = st; setNote(vary(st), ampOut == 0); colorNote();
        lvCur[0] = LEVEL[0]; lvCur[1] = LEVEL[1] * (0.35 + 0.65 * kE); lvCur[2] = LEVEL[2] * (0.15 + 0.85 * kE);
        uint16_t downMs = FIB_DOWN[constrain((int)(kE * 2.5 + golden(1 / (PHI * PHI)) * 2.5), 0, 4)];
        noInterrupts();
        relRate[0] = msToRate(downMs); relRate[1] = msToRate(downMs / PHI); relRate[2] = msToRate(downMs / (PHI * PHI));
        interrupts();
        tBoing = now; boinging = true;
      } else if (st != phraseStep && E > 2 * NOISE_E) {
        if (!stepSince) stepSince = now;
        else if (now - stepSince > 200) { phraseStep = st; setNote(vary(st), false); colorNote(); stepSince = 0; }
      } else stepSince = 0;
    } else if (E < NOISE_E * 0.6) phraseOn = false;
    float w = kE;
    static float bw = 0.5;                       // el soplo también varía solo, despacio
    bw = constrain(bw + rnd(0.01), 0.2, 1.0);
    breath = (uint8_t)(4 + 22 * kE * bw);
    float lfo2 = sin(now * (2 * PI / (1000.0 * PHI * PHI)));   // las jorobas también respiran (2,6 s)
    fmS += (FM_REST + 8 * lfo2 + FM_SPRING * w - fmS) * 0.012;   // las jorobas aparecen y se van en ~1/10 s
    if (fmS < 0) fmS = 0;
    fmIdx = (uint8_t)fmS;
    sustain();
  }

  if (noteOn && now - tNote >= MIDI_LEN) { midi(false, 0); noteOn = false; }
  if (boinging && now - lastGlide >= 2) { lastGlide = now; glide(); }

  // foto de la onda: mientras suena, una cada 150 ms (así se ve cómo se apaga)
  noInterrupts(); uint16_t si = snapIdx; interrupts();
  if (snapPending && si >= 256) { snapPending = false; sendSnap(); }
  else if (!snapPending && ampOut > 0 && now - tSnap >= 150 && now - tBoing >= 20) {
    tSnap = now; snapPending = true; snapDiv = 0;
    noInterrupts(); snapIdx = 0; interrupts();
  }
  if (now - lastLed >= 15) {
    lastLed = now;
    if (flash > 0) flash = flash > 8 ? flash - 8 : 0;   // el destello se apaga en ~0,4 s
    int wob = (int)(kE * 200);                           // el LED brilla con la energía del frotado
    if (E > NOISE_E && wob > flash) flash = wob;
    else hue = (hue + 1) % 1536;                         // en reposo el color avanza despacio (~23 s la vuelta)
    showLed(now);
  }
}
