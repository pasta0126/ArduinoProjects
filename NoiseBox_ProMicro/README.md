# Noise Box con Pro Micro

Spring Noise Box: lata metálica + muelle + piezo, leído por una Pro Micro (ATmega32U4, 5 V)
que lo convierte en notas MIDI por USB. Se avanza "de menos a más": primero que suene, luego mejoras.

## Fases
1. **Piezo → gráfica en pantalla** ✔ hecho (10 kΩ + 2,2 MΩ, umbral orientativo 25, tiempo muerto 50 ms)
2. Piezo → nota MIDI  ← siguiente con velocity (MIDIUSB, canal 10, nota 38)
3. Potenciómetro de sensibilidad + diodos de protección
4. Modos / elegir nota
5. Sonido propio por el jack

## Carpetas
- `manuals/`  manuales visuales paso a paso (HTML, se abren en el navegador)
- `sketches/` un sketch por paso (carpeta y .ino con el mismo nombre)
- `tools/osciloscopio.html` gráfica en vivo del piezo (abrir en Chrome, botón Conectar placa)
- `tools/gen_manual01.py` genera el manual 01 (editar aquí y volver a ejecutar)

## Subir un sketch (placa: Arduino Micro)
```
arduino-cli compile --fqbn arduino:avr:micro sketches/01_piezo_plotter
arduino-cli upload  -p /dev/cu.usbmodem2101 --fqbn arduino:avr:micro sketches/01_piezo_plotter
```
