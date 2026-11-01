#!/usr/bin/env python3
# Genera manuals/03-barra-de-led.html (SVG estático, sin JS).
# Reutiliza la geometría del manual 01 (gen_manual01.py) y las piezas del manual 02 (se leen de su HTML).
import re, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'manuals', '03-barra-de-led.html')
M02 = os.path.join(ROOT, 'manuals', '02-diodos-y-potenciometro.html')

# --- funciones del manual 01 (sin ejecutar su main) ---
src = open(os.path.join(HERE, 'gen_manual01.py'), encoding='utf-8').read()
src = re.sub(r'\nmain\(\)\s*$', '\n', src)
G = {}
exec(compile(src, 'gen_manual01', 'exec'), G)
H, Y, LET = G['H'], G['Y'], G['LET']
board_base, promicro, resistor, wire, ring = G['board_base'], G['promicro'], G['resistor'], G['wire'], G['ring']
fig, chips, step = G['fig'], G['chips'], G['step']

# --- piezas ya montadas (manuales 01 y 02), sacadas del diagrama completo del paso 6 del manual 02 ---
m02 = open(M02, encoding='utf-8').read()
CSS = re.search(r'<style>(.*?)</style>', m02, re.S).group(1)
svg7 = re.findall(r'<svg.*?</svg>', m02, re.S)[7]
body = svg7[svg7.find('</g>', svg7.find('<g class="pm">')) + 4:]
body = body[:body.find('<circle cx="204" cy="336" r="7" class="ring"/>')]
OLD = '<g class="old">' + body.replace('<g class="old">', '<g>') + '</g>'

CSS += '''
.wc.w-purple{stroke:#9B5DE5}.wend.w-purple{fill:#9B5DE5}
.chip.purple i{background:#9B5DE5}
.ledbar{fill:#1B1F2A;stroke:var(--ink);stroke-width:1.5}
.padg{fill:var(--pin);stroke:var(--ink);stroke-width:.8}
.padt{font-size:6.5px;fill:#EAF0FF;text-anchor:middle}
.ledtxt{font-size:8px;fill:var(--muted);text-anchor:middle}
'''

COL = ['#FF0000', '#FF5A00', '#C8C800', '#00C800', '#00DCDC', '#2A2AFF', '#8C00FF', '#FF00A0']
NAMES = ['Am', 'C', 'G', 'D', 'Em', 'F', 'Dm', 'E']

# ---------- piezas nuevas ----------
PAD = {'DI': (52, 490), 'GND': (68, 490), '5V': (84, 490)}   # pads del aro, de izquierda a derecha

def bar(x=36, y=474, w=232, h=44, leds=True):
    import math
    cx, cy, R = 190, 505, 38
    s = [f'<circle cx="{cx}" cy="{cy}" r="{R+10}" class="ledbar"/><circle cx="{cx}" cy="{cy}" r="{R-14}" class="bb" style="fill:var(--paper)"/>',
         '<rect x="40" y="480" width="76" height="22" rx="3" class="ledbar"/>']
    for n, (px, py) in PAD.items():
        s.append(f'<rect x="{px - 5}" y="{py - 4}" width="10" height="9" class="padg"/>')
        s.append(f'<text x="{px}" y="{py + 20}" class="padt">{n}</text>')
    s.append('<rect x="95" y="486" width="10" height="9" class="padg"/><text x="100" y="510" class="padt" style="fill:var(--muted)">DO</text>')
    s.append('<text x="100" y="472" class="lbl" text-anchor="middle" style="font-size:7px">sin conectar</text>')
    for k in range(8):
        a = math.radians(-90 - 45 * k)      # el LED 1 queda arriba y sigue el sentido contrario a las agujas
        lx, ly = cx + R * math.cos(a), cy + R * math.sin(a)
        s.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="7" fill="{COL[k]}" opacity=".95"/><text x="{lx:.1f}" y="{ly+2.5:.1f}" class="padt" style="fill:#111;font-weight:700">{k+1}</text>')
    s.append(f'<text x="{cx + 70}" y="{cy + 4}" class="lbl">aro de 8 LED (WS2812)</text>')
    return ''.join(s)

def new_relay():  # pin 10 (J12) -> fila 14 derecha (J14)
    return wire('M236,256 C256,266 256,278 236,288', 'purple', [H('J', 12), H('J', 14)])

def new_res():    # 220 ohm cruzando el canal en la fila 14
    return resistor(H('E', 14), H('F', 14), ['red', 'red', 'brown'])

def new_gnd():    # GND del aro -> D13 (masa de la mitad izquierda)
    x, y = H('D', 13); px, py = PAD['GND']
    return wire(f'M{px},{py} C{px + 28},{py - 70} {x + 6},{y + 90} {x},{y}', 'black', [(px, py), (x, y)])

def new_5v():     # 5 V del aro -> F17
    x, y = H('F', 17); px, py = PAD['5V']
    return wire(f'M{px},{py} C{px + 40},{py - 40} {x - 60},{y + 70} {x},{y}', 'red', [(px, py), (x, y)])

def new_din():    # DI del aro -> B14
    x, y = H('B', 14); px, py = PAD['DI']
    return wire(f'M{px},{py} C{px - 30},{py - 70} {x - 40},{y + 70} {x},{y}', 'green', [(px, py), (x, y)])

def old(s): return f'<g class="old">{s}</g>'

def board_fig(aria, items, rings, vb='0 30 420 540'):
    """items: lista de (contenido, 'old'|'new')"""
    parts = ''.join(c if st == 'new' else old(c) for c, st in items)
    return (f'<svg viewBox="{vb}" role="img" aria-label="{aria}">' + board_base() + promicro() + OLD + parts + rings + '</svg>')

BAR = (bar(), None)
ALL = {'bar': bar(), 'relay': new_relay(), 'res': new_res(), 'gnd': new_gnd(), '5v': new_5v(), 'din': new_din()}

def stage(done, now):
    items = [(ALL['bar'], 'new' if 'bar' == now else 'old')]
    for k in ('relay', 'res', 'gnd', '5v', 'din'):
        if k == now: items.append((ALL[k], 'new'))
        elif k in done: items.append((ALL[k], 'old'))
    return items

# ---------- figuras sueltas ----------
def schematic():
    return '''<svg viewBox="0 0 600 220" role="img" aria-label="Esquema: el pin 10 de la Pro Micro entra por una resistencia de 220 ohmios al pin DI del aro; 5 voltios y masa alimentan el aro">
<rect x="20" y="30" width="130" height="150" class="sbox"/><text x="85" y="52" class="stxt" text-anchor="middle" font-weight="700">Pro Micro</text>
<text x="38" y="90" class="stxt">pin 10</text><text x="38" y="130" class="stxt">VCC (5 V)</text><text x="38" y="165" class="stxt">GND</text>
<line x1="150" y1="86" x2="230" y2="86" class="sline"/><circle cx="150" cy="86" r="3.5" class="sdot"/>
<rect x="230" y="74" width="70" height="24" rx="4" fill="#E3CF9C" stroke="#6B5A2E"/><text x="265" y="90" class="stxt" text-anchor="middle">220 Ω</text>
<line x1="300" y1="86" x2="410" y2="86" class="sline"/>
<line x1="150" y1="126" x2="410" y2="126" class="sline w-red-s"/><circle cx="150" cy="126" r="3.5" class="sdot"/>
<line x1="150" y1="161" x2="410" y2="161" class="sline"/><circle cx="150" cy="161" r="3.5" class="sdot"/>
<rect x="410" y="30" width="170" height="150" class="sbox"/><text x="495" y="52" class="stxt" text-anchor="middle" font-weight="700">Barra de 8 LED</text>
<text x="426" y="90" class="stxt">DI (datos)</text><text x="426" y="130" class="stxt">5V</text><text x="426" y="165" class="stxt">GND</text>
<text x="265" y="68" class="stxt" text-anchor="middle" style="font-size:10px">datos</text>
<text x="265" y="118" class="stxt" text-anchor="middle" style="font-size:10px">alimentación</text>
</svg>'''

def fig_bar():
    import math
    cx, cy, R = 280, 86, 50
    leds = ''.join(
        f'<circle cx="{cx + R*math.cos(math.radians(-90-45*k)):.1f}" cy="{cy + R*math.sin(math.radians(-90-45*k)):.1f}" r="11" fill="{COL[k]}" opacity=".95"/>'
        f'<text x="{cx + R*math.cos(math.radians(-90-45*k)):.1f}" y="{cy + R*math.sin(math.radians(-90-45*k)) + 4:.1f}" class="stxt" text-anchor="middle" style="fill:#111;font-weight:700">{k+1}</text>' for k in range(8))
    return f'''<svg viewBox="-90 0 680 190" role="img" aria-label="Aro de 8 LED con sus cuatro cables: DI verde, 5V rojo, GND negro y DO lila, que no se usa">
<circle cx="{cx}" cy="{cy}" r="68" class="ledbar"/><circle cx="{cx}" cy="{cy}" r="30" fill="var(--paper)"/>{leds}
<line x1="215" y1="150" x2="130" y2="150" class="wc w-green" style="stroke-width:4"/><text x="124" y="154" class="stxt" text-anchor="end">DI (verde): entrada de datos</text>
<line x1="215" y1="160" x2="130" y2="168" class="wc w-red" style="stroke-width:4"/><text x="124" y="172" class="stxt" text-anchor="end">5V (rojo)</text>
<line x1="215" y1="140" x2="130" y2="132" class="wc w-black" style="stroke-width:4"/><text x="124" y="130" class="stxt" text-anchor="end">GND (negro)</text>
<line x1="345" y1="150" x2="430" y2="150" class="wc w-purple" style="stroke-width:4"/><text x="436" y="154" class="hn" text-anchor="start">DO (lila): NO se usa</text>
</svg>'''

def fig_zones():
    z = ''.join(f'<rect x="{20 + i * 66}" y="20" width="62" height="46" rx="4" fill="{COL[i]}" opacity=".9"/>'
                f'<text x="{51 + i * 66}" y="48" class="stxt" text-anchor="middle" style="fill:#111;font-weight:700">{NAMES[i]}</text>' for i in range(8))
    return f'''<svg viewBox="0 0 560 110" role="img" aria-label="Los ocho LED, de izquierda a derecha: Am, C, G, D, Em, F, Dm, E">{z}
<text x="20" y="92" class="lbl">potenciómetro a la izquierda</text><text x="540" y="92" class="lbl" text-anchor="end">potenciómetro a la derecha</text></svg>'''

# ---------- pasos ----------
def steps_html():
    s = []
    s.append(step(1, 'Desenchufa el USB y mira el aro',
        'Trabaja siempre sin corriente. El aro tiene cuatro cables: DI (entrada de datos), 5V, GND y DO (salida de datos). El DO solo sirve para encadenar otro aro, así que aquí queda suelto: apártalo para que no toque nada.',
        [('green', 'DI: verde'), ('red', '5V: rojo'), ('black', 'GND: negro'), ('purple', 'DO: lila, sin conectar')],
        fig(fig_bar(), 'Mira el texto impreso en tu aro por si algún cable es distinto. El LED 1 es el primero tras la entrada de datos: ahí empieza Am y la luz sigue el giro del aro.')))
    s.append(step(2, 'Cable lila: lleva el pin 10 a la fila 14',
        'El pin 10 está en la fila 12, a la derecha. Un cable lila rígido corto, de J12 a J14. Así la fila 14 de la derecha es la señal del pin 10.',
        [('purple', 'Cable lila (~3 cm)'), ('', 'J12 → J14')],
        fig(board_fig('Cable lila de J12 a J14', stage([], 'relay'), ring('J', 12, 'J12', 30, 4, 'start') + ring('J', 14, 'J14', 30, 4, 'start')),
            'El cable lila da la vuelta por la derecha de la fila 13 sin tocar nada. J12 es un agujero libre de la fila del pin 10.')))
    s.append(step(3, 'Resistencia de 220 Ω: protege el pin de datos',
        'Rojo, rojo, marrón, dorado. Cruza el canal central en la fila 14: una pata en F14 (la señal del pin 10) y la otra en E14 (el lado que irá al aro).',
        [('red', '220 Ω: rojo, rojo, marrón'), ('', 'F14 ↔ E14')],
        fig(board_fig('Resistencia de 220 ohmios de E14 a F14', stage(['relay'], 'res'), ring('E', 14, 'E14', -14, 18, 'end') + ring('F', 14, 'F14', 0, 22)),
            'Igual que la de 2,2 MΩ de la fila 13: cruza el canal por encima. La resistencia evita que un pico en el cable de datos dañe el primer LED.')))
    s.append(step(4, 'Masa del aro: GND a D13',
        'El cable negro (GND) del aro va a D13. La mitad izquierda de la fila 13 ya es masa por el cable negro del manual 01.',
        [('black', 'GND del aro'), ('', 'D13')],
        fig(board_fig('GND del aro a D13', stage(['relay', 'res'], 'gnd'), ring('D', 13, 'D13', -14, 4, 'end')),
            'D13 está entre el puente negro (C13) y la resistencia de 2,2 MΩ (E13). Aprieta bien para no mover los vecinos.')))
    s.append(step(5, 'Alimentación del aro: 5V a F17',
        'El cable rojo (5V) del aro va a F17, en la última fila de la derecha, que son 5 V desde el manual 02.',
        [('red', '5V del aro'), ('', 'F17')],
        fig(board_fig('5V del aro a F17', stage(['relay', 'res', 'gnd'], '5v'), ring('F', 17, 'F17', -14, 20, 'end')),
            'F17 queda justo debajo de F16, que es masa. No los confundas: el cable rojo va a la fila 17, la última.')
        + '<div class="warn"><b>Antes de seguir:</b> el cable rojo a F17 y el negro a D13. Si los cambias, el aro se estropea.</div>'))
    s.append(step(6, 'Datos del aro: DI a B14',
        'El cable verde (DI) del aro va a B14, en la mitad izquierda de la fila 14. Ahí llega la señal del pin 10 ya pasada por la resistencia.',
        [('green', 'DI del aro'), ('', 'B14')],
        fig(board_fig('DI del aro a B14', stage(['relay', 'res', 'gnd', '5v'], 'din'), ring('B', 14, 'B14', -14, 4, 'end')),
            'El camino completo es: pin 10, J12, cable lila, J14, F14, resistencia de 220 Ω, E14, B14, DI.')))
    s.append(step(7, 'Comprueba que no hay cortocircuito (sin USB)',
        'Multímetro en continuidad. Puntas en D13 (masa) y F17 (5 V): no debe pitar. Después en J14 y D13: tampoco. Si pita, hay un cable mal puesto: revisa los pasos 4 a 6.',
        [('', 'D13 y F17: SIN pitido'), ('', 'J14 y D13: SIN pitido')],
        ''))
    s.append(step(8, 'Conecta el USB y mide 5 V',
        'Voltios de continua, escala 20 V. Punta roja en F17 y negra en D13: debe marcar entre 4,5 y 5,0 V. Si marca 0, revisa que el cable de 5V esté en la fila 17.',
        [('', 'F17 – D13: 4,5 a 5,0 V')],
        '<div class="warn"><b>Aún sin sketch:</b> con el sketch 03 cargado el aro no se enciende. Es normal: solo la maneja el sketch 04.</div>'))
    s.append(step(9, 'Sube el sketch 04 y miral aro',
        'Dime "sube el 04" y lo cargo yo. Los ocho LED son los ocho acordes: el elegido brilla fuerte, los demás quedan tenues, y con cada golpe el elegido destella en blanco. Gira el potenciómetro y la luz se desplaza.',
        [('', 'Am · C · G · D · Em · F · Dm · E de izquierda a derecha')],
        fig(fig_zones(), 'Los colores son rojo, naranja, amarillo, verde, cian, azul, violeta y magenta. En tools/midi_caja.html el marcador blanco sigue al mando.')
        + '<div class="warn"><b>Brillo bajo a propósito:</b> el aro a tope pasaría el consumo que da el USB. Si la quieres más fuerte, sube BRIGHT en el sketch poco a poco.</div>'))
    return ''.join(s)

def main():
    h = []
    h.append('<title>Aro de LED</title>')
    h.append('<meta charset="utf-8"><meta name="claude:viewport-fit-sides" content="cover">')
    h.append('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    h.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">')
    h.append(f'<style>{CSS}</style>')
    h.append('<main class="wrap">')
    h.append('<header><div class="eyebrow">Noise Box · Pro Micro · Manual 03 · mini protoboard</div><h1>Aro de LED</h1>'
             '<p class="lead">Una aro de 8 LED te dice qué acorde has elegido con el potenciómetro y destella con cada golpe. Se añade al montaje del manual 02 sin quitar nada.</p>'
             '<div class="meta"><span>20–30 min</span><span>sin soldar la placa</span><span>usa el pin 10 y las filas 12 a 17</span></div></header>')
    h.append('<section><h2>Qué vamos a añadir</h2>' + fig(schematic(),
        'El pin 10 manda los datos al aro a través de una resistencia de 220 Ω. El aro toma los 5 V y la masa de la placa. Cada LED recibe su color por el mismo cable de datos.') + '</section>')
    h.append('<section><h2>Dónde va cada cosa</h2><div class="map">'
             '<div><b>Fila 12, derecha</b>pin 10 de la Pro Micro: de J12 sale el cable lila</div>'
             '<div><b>Fila 14</b>derecha = señal del pin 10, izquierda = hacia DI. La separa la resistencia de 220 Ω, que cruza el canal</div>'
             '<div><b>D13</b>masa (GND): llega el cable GND del aro</div>'
             '<div><b>F17</b>5 V: llega el cable 5V del aro</div>'
             '</div></section>')
    h.append('<section><h2>Material</h2><p>Aro de 8 LED WS2812 con 4 cables, resistencia de 220 Ω (rojo, rojo, marrón), cable rígido lila (~3 cm), multímetro y cable USB. El montaje del manual 02 debe estar terminado y funcionando. En Arduino hace falta la librería Adafruit NeoPixel.</p></section>')
    h.append('<section><h2>Montaje</h2><ol class="steps">' + steps_html() + '</ol></section>')
    h.append('<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Causa probable</th><th>Qué hacer</th></tr></thead><tbody>'
             '<tr><td>Ningún LED se enciende</td><td>Sketch 03 cargado, o el verde en el cable DO en vez del DI</td><td>Sube el 04 y pasa el verde al cable DI del aro</td></tr>'
             '<tr><td>Colores al azar o parpadeo</td><td>Falta masa o la resistencia está floja</td><td>Revisa D13, F14 y E14</td></tr>'
             '<tr><td>Solo luce el primer LED</td><td>Datos que no llegan al resto</td><td>Revisa que el verde sea el DI y no el DO</td></tr>'
             '<tr><td>Los colores salen cambiados (rojo por verde)</td><td>Tu barra usa otro orden de color</td><td>En el sketch cambia NEO_GRB por NEO_RGB</td></tr>'
             '<tr><td>La luz no sigue al potenciómetro</td><td>El cursor no llega a A1</td><td>Revisa I7, como en el manual 02</td></tr>'
             '<tr><td>El USB se desconecta al golpear</td><td>El aro gasta demasiado</td><td>Baja BRIGHT en el sketch</td></tr>'
             '<tr><td>Pitido en D13 – F17 sin USB</td><td>Cortocircuito masa–5 V</td><td>Quita los cables del aro y revisa uno a uno</td></tr>'
             '</tbody></table></div></section>')
    h.append('<section><h2>Siguiente manual</h2><p>Manual 04: pasar todo a la mini protoboard, fijar el piezo a la lata y colocar el muelle.</p></section>')
    h.append('</main>')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(h))
    print('ok', OUT)

main()
