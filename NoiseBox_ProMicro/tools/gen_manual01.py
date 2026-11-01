#!/usr/bin/env python3
# Genera manuals/01-piezo-en-protoboard.html (SVG estático, sin JS)
# Versión mini protoboard de 170 puntos: filas 1-15, USB arriba, letras A-E a la izquierda y F-J a la derecha.
import math, random

OUT = "/Users/pasta0126/arduino-projects/NoiseBox_ProMicro/manuals/01-piezo-en-protoboard.html"

P = 16
LET = {'A': 60, 'B': 76, 'C': 92, 'D': 108, 'E': 124, 'F': 172, 'G': 188, 'H': 204, 'I': 220, 'J': 236}
def Y(r): return 80 + (r - 1) * P
def H(l, r): return LET[l], Y(r)

TOP = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', '15', '14', '16', '10']   # fila derecha
BOT = ['TX0', 'RX1', 'GND', 'GND', '2', '3', '4', '5', '6', '7', '8', '9']          # fila izquierda
BANDS = {'brown': '#7A4A22', 'black': '#111111', 'orange': '#F08A00', 'red': '#D62828', 'green': '#2E9E44', 'gold': '#C9A227'}
VW, VH = 420, 450

def board_base():
    s = ['<rect x="48" y="68" width="216" height="284" rx="6" class="bb"/>',
         '<rect x="134" y="68" width="28" height="284" class="gapc"/>']
    for l, x in LET.items():
        s.append(f'<text x="{x}" y="62" class="col">{l}</text>')
    for r in range(1, 18):
        y = Y(r)
        s.append(f'<text x="44" y="{y + 3}" class="rowl" text-anchor="end">{r}</text>')
        s.append(f'<text x="250" y="{y + 3}" class="rowl" text-anchor="start">{r}</text>')
        for l, x in LET.items():
            s.append(f'<circle cx="{x}" cy="{y}" r="2.3" class="hole"/>')
    return ''.join(s)

def promicro():
    g = ['<g class="pm">']
    g.append('<rect x="147" y="50" width="18" height="22" rx="2" class="usb"/>')
    g.append('<rect x="96" y="70" width="120" height="196" rx="4" class="pcb"/>')
    g.append('<rect x="140" y="150" width="32" height="32" rx="2" class="mcu"/><text x="156" y="170" class="pn" text-anchor="middle">32U4</text>')
    g.append('<rect x="146" y="200" width="20" height="10" rx="2" class="mcu"/>')
    g.append('<text x="156" y="128" class="pn" text-anchor="middle">PRO MICRO</text>')
    g.append('<text x="156" y="44" class="lbl" text-anchor="middle">USB</text>')
    for i in range(12):
        y = Y(i + 1)
        g.append(f'<rect x="104" y="{y - 4}" width="8" height="8" class="pin"/>')
        g.append(f'<rect x="200" y="{y - 4}" width="8" height="8" class="pin"/>')
        g.append(f'<text x="116" y="{y + 3}" class="pn" text-anchor="start">{BOT[i]}</text>')
        g.append(f'<text x="196" y="{y + 3}" class="pn" text-anchor="end">{TOP[i]}</text>')
    g.append('</g>')
    return ''.join(g)

def resistor(a, b, bands):
    (x1, y1), (x2, y2) = a, b
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    horiz = abs(x2 - x1) > abs(y2 - y1)
    dist = abs(x2 - x1) if horiz else abs(y2 - y1)
    L = min(dist - 8, 26)
    s = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="leg"/>']
    if horiz:
        bx = cx - L / 2
        s.append(f'<rect x="{bx}" y="{cy - 5}" width="{L}" height="10" rx="4" class="rbody"/>')
        for i, bnd in enumerate(bands):
            s.append(f'<rect x="{bx + 4 + i * 5}" y="{cy - 5}" width="3" height="10" fill="{BANDS[bnd]}"/>')
        s.append(f'<rect x="{bx + L - 5}" y="{cy - 5}" width="3" height="10" fill="{BANDS["gold"]}"/>')
    else:
        by = cy - L / 2
        s.append(f'<rect x="{cx - 5}" y="{by}" width="10" height="{L}" rx="4" class="rbody"/>')
        for i, bnd in enumerate(bands):
            s.append(f'<rect x="{cx - 5}" y="{by + 4 + i * 5}" width="10" height="3" fill="{BANDS[bnd]}"/>')
        s.append(f'<rect x="{cx - 5}" y="{by + L - 5}" width="10" height="3" fill="{BANDS["gold"]}"/>')
    return ''.join(s)

def wire(d, color, ends):
    halo = 'wh-k' if color == 'black' else 'wh'
    s = [f'<path d="{d}" class="{halo}"/>', f'<path d="{d}" class="wc w-{color}"/>']
    for (x, y) in ends:
        s.append(f'<circle cx="{x}" cy="{y}" r="3.2" class="wend w-{color}"/>')
    return ''.join(s)

def jumper(a, b, color, bow):
    (x1, y1), (x2, y2) = a, b
    d = f'M{x1},{y1} C{x1 + bow},{y1 + 50} {x2 + bow},{y2 - 50} {x2},{y2}'
    return wire(d, color, [a, b])

def ring(l, r, name, dx=0, dy=-13, anchor='middle'):
    x, y = H(l, r)
    return (f'<circle cx="{x}" cy="{y}" r="7" class="ring"/>'
            f'<text x="{x + dx}" y="{y + dy}" class="hn" text-anchor="{anchor}">{name}</text>')

DISC = (190, 412)

def piezo_disc():
    cx, cy = DISC
    return (f'<circle cx="{cx}" cy="{cy}" r="26" class="brass"/>'
            f'<circle cx="{cx}" cy="{cy}" r="17" class="ceramic"/>'
            f'<circle cx="{cx}" cy="{cy}" r="3" class="w-red wend"/>'
            f'<text x="{cx}" y="{cy + 42}" class="lbl" text-anchor="middle">piezo (suelto sobre la mesa)</text>')

def piezo_wires():
    jx, jy = H('J', 15); ax, ay = H('A', 13)
    red = wire(f'M200,392 C236,380 250,340 {jx},{jy}', 'red', [(jx, jy)])
    blk = wire(f'M176,392 C110,370 34,330 {ax},{ay}', 'black', [(ax, ay)])
    return red + blk

def probe(tip, color, label, dx, dy, anchor='middle'):
    x, y = tip
    x2, y2 = x + dx, y + dy
    return (f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" class="prb-{color}"/>'
            f'<circle cx="{x}" cy="{y}" r="3" class="prb-tip-{color}"/>'
            f'<text x="{x2}" y="{y2 - 6}" class="hn" text-anchor="{anchor}" style="fill:var(--ink)">{label}</text>')

def display(x, y, value, unit, scale):
    return (f'<rect x="{x}" y="{y}" width="140" height="58" rx="6" class="mm"/>'
            f'<text x="{x + 10}" y="{y + 38}" class="mmv">{value}</text>'
            f'<text x="{x + 130}" y="{y + 22}" class="mmu" text-anchor="end">{unit}</text>'
            f'<text x="{x + 130}" y="{y + 46}" class="mmu" text-anchor="end" style="font-size:8px">{scale}</text>')

def board_svg(aria, parts, rings='', extra=''):
    def wrap(key, content):
        st = parts.get(key)
        if not st: return ''
        return content if st == 'new' else f'<g class="old">{content}</g>'
    has_pz = bool(parts.get('piezo')); has_disp = 'class="mm"' in extra
    vb = '0 30 420 430' if (has_pz and has_disp) else ('0 30 290 430' if has_pz else ('0 30 420 340' if has_disp else '24 30 250 340'))
    s = [f'<svg viewBox="{vb}" role="img" aria-label="{aria}">', board_base(), promicro()]
    s.append(wrap('r10', resistor(H('G', 13), H('G', 15), ['brown', 'black', 'orange'])))
    s.append(wrap('r22', resistor(H('E', 13), H('F', 13), ['red', 'red', 'green'])))
    s.append(wrap('green', jumper(H('J', 8), H('J', 13), 'green', 10)))
    s.append(wrap('black', jumper(H('B', 3), H('B', 13), 'black', -10)))
    if parts.get('piezo'):
        pz = piezo_disc() + piezo_wires()
        s.append(pz if parts['piezo'] == 'new' else f'<g class="old">{pz}</g>')
    s.append(rings); s.append(extra)
    s.append('</svg>')
    return ''.join(s)

def fig(svg, cap):
    return f'<figure class="dia"><div class="scroll">{svg}</div><figcaption>{cap}</figcaption></figure>'

def chips(items):
    return '<div class="chips">' + ''.join(f'<span class="chip {c}"><i></i>{t}</span>' for c, t in items) + '</div>'

def step(n, title, text, chip_items, figure):
    return (f'<li class="step" id="p{n}"><div class="num" aria-hidden="true">{n}</div>'
            f'<div class="sbody"><h3>{title}</h3><p>{text}</p>{chips(chip_items) if chip_items else ""}{figure}</div></li>')

# ---------- figuras sueltas ----------
def schematic():
    return '''<svg viewBox="0 0 560 210" role="img" aria-label="Esquema: el piezo entra por una resistencia de 10 kΩ al pin A0, y una resistencia de 2,2 MΩ lleva A0 a masa">
<circle cx="60" cy="90" r="26" class="brass"/><circle cx="60" cy="90" r="17" class="ceramic"/>
<text x="60" y="38" class="lbl" text-anchor="middle">PIEZO</text>
<path d="M86,90 H132" class="sline w-red-s"/>
<rect x="132" y="80" width="64" height="20" rx="4" class="sbox"/><text x="164" y="94" class="stxt" text-anchor="middle">10 kΩ</text>
<path d="M196,90 H300" class="sline"/>
<circle cx="270" cy="90" r="4" class="sdot"/>
<text x="164" y="66" class="lbl" text-anchor="middle">protege el pin</text>
<rect x="344" y="62" width="150" height="56" rx="6" class="spm"/>
<text x="419" y="86" class="spt" text-anchor="middle">PRO MICRO</text>
<text x="419" y="104" class="spt" text-anchor="middle">pin A0 → 0…1023</text>
<path d="M300,90 H344" class="sline"/><path d="M336,85 L344,90 L336,95" class="sline" fill="none"/>
<text x="322" y="78" class="lbl" text-anchor="middle">tensión</text>
<path d="M270,94 V122" class="sline"/>
<rect x="260" y="122" width="20" height="44" rx="4" class="sbox"/>
<text x="292" y="148" class="stxt">2,2 MΩ</text>
<text x="292" y="162" class="lbl">devuelve A0 a 0 V</text>
<path d="M270,166 V186" class="sline"/>
<path d="M254,186 H286 M259,192 H281 M264,198 H276" class="sline"/>
<text x="296" y="194" class="lbl">GND</text>
<path d="M60,116 V186 H270" class="sline w-black-s"/>
</svg>'''

def fig_parts():
    def res(x, y, bands, name, color):
        s = f'<line x1="{x}" y1="{y}" x2="{x + 120}" y2="{y}" class="leg"/><rect x="{x + 30}" y="{y - 9}" width="60" height="18" rx="7" class="rbody"/>'
        for i, b in enumerate(bands):
            s += f'<rect x="{x + 40 + i * 11}" y="{y - 9}" width="6" height="18" fill="{BANDS[b]}"/>'
        s += f'<rect x="{x + 76}" y="{y - 9}" width="5" height="18" fill="{BANDS["gold"]}"/>'
        s += f'<text x="{x + 60}" y="{y + 30}" class="stxt" text-anchor="middle">{name}</text>'
        s += f'<text x="{x + 60}" y="{y + 44}" class="lbl" text-anchor="middle">{color}</text>'
        return s
    return ('<svg viewBox="0 0 560 120" role="img" aria-label="Las dos resistencias con sus bandas de color: 10 kΩ marrón negro naranja, 2,2 MΩ rojo rojo verde">'
            + res(30, 40, ['brown', 'black', 'orange'], '10 kΩ', 'marrón · negro · naranja')
            + res(230, 40, ['red', 'red', 'green'], '2,2 MΩ', 'rojo · rojo · verde')
            + '<text x="440" y="36" class="lbl">la banda dorada</text><text x="440" y="50" class="lbl">va siempre a la derecha</text></svg>')

def fig_tin():
    def stage(x, label, kind):
        s = f'<g transform="translate({x},20)"><rect x="0" y="22" width="70" height="16" rx="6" class="ins"/>'
        if kind == 1: s += '<rect x="70" y="26" width="30" height="8" class="strand"/>'
        elif kind == 2: s += '<rect x="70" y="27" width="30" height="6" rx="3" class="strand"/>'
        else: s += '<rect x="70" y="27" width="30" height="6" rx="3" class="tinned"/>'
        s += f'<text x="50" y="70" class="stxt" text-anchor="middle">{label}</text></g>'
        return s
    return ('<svg viewBox="0 0 560 120" role="img" aria-label="Tres pasos: pelar 5 milímetros, retorcer los hilos, estañar la punta">'
            + stage(10, '1 pela 5 mm', 1) + stage(195, '2 retuerce', 2) + stage(380, '3 estaña 2 s', 3)
            + '<text x="400" y="106" class="lbl">punta plateada y rígida</text></svg>')

def fig_waves():
    def panel(x0, title, kind):
        w, h, top = 170, 100, 14
        base = top + h - 6
        g = f'<rect x="{x0}" y="{top}" width="{w}" height="{h}" rx="4" class="plotbg"/>'
        g += f'<text x="{x0 + 6}" y="{top + 11}" class="lbl">1023</text><text x="{x0 + 6}" y="{base - 3}" class="lbl">0</text>'
        pts = []; rnd = random.Random(7)
        for px in range(10, w - 6):
            if kind == 'ok':
                y = 0
                for (hx, amp) in [(24, 70), (80, 52), (122, 30)]:
                    t = px - hx
                    if t >= 0: y += amp * math.exp(-t / 9) * max(0, math.sin(t * 0.55))
                yy = base - y
            elif kind == 'high': yy = top + 8 + rnd.random() * 2
            else: yy = base - 18 - rnd.random() * 60
            pts.append(f'{x0 + px},{yy:.1f}')
        g += f'<polyline points="{" ".join(pts)}" class="trace"/>'
        g += f'<text x="{x0 + w / 2}" y="{top + h + 16}" class="stxt" text-anchor="middle">{title}</text>'
        return g
    return ('<svg viewBox="0 0 560 150" role="img" aria-label="Tres gráficas: bien, reposo en cero con picos al golpear; mal, línea pegada arriba; mal, ruido continuo">'
            + panel(8, 'BIEN', 'ok') + panel(196, 'MAL: pegada arriba', 'high') + panel(384, 'MAL: ruido sin tocar', 'noise') + '</svg>')

# ---------- pasos ----------
ALL = {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': True}

def steps_html():
    st = []
    s1 = board_svg('Pro Micro con el USB arriba y el pin RAW en la fila 1', {},
                   ring('H', 1, 'RAW', 28, 4, 'start') + ring('D', 1, 'TX0', -28, 4, 'end'))
    st.append(step(1, 'Pro Micro: USB arriba, patillas en la fila 1',
        'Gira la protoboard con las letras A–E a la izquierda y los números hacia abajo. La Pro Micro entra con el USB arriba y el pin RAW en la fila 1. Presiona por los bordes, nunca sobre el chip ni el USB. Si ya la tienes puesta, comprueba que RAW está en la fila 1.',
        [('', 'Fila derecha: RAW, GND, RST, VCC, A3, A2, A1, A0…'), ('', 'Fila izquierda: TX0, RX1, GND, GND, 2…')],
        fig(s1, 'En la protoboard grande, de aquí en adelante usa solo las filas 1 a 15. En la mini de 170 puntos entra justo.')))

    st.append(step(2, 'Prepara las puntas del piezo',
        'Las puntas de los cables son de hilo fino y no se clavan bien en la protoboard. Pela 5 mm, retuerce los hilos y cúbrelos con un poco de estaño.',
        [('red', 'Cable rojo (centro del disco)'), ('black', 'Cable negro (latón)')], fig(fig_tin(), 'Cada punta debe quedar plateada y rígida.')))

    s3 = board_svg('Resistencia de 10 kΩ entre G13 y G15', {'r10': 'new'},
                   ring('G', 13, 'G13', 12, 4, 'start') + ring('G', 15, 'G15', 12, 4, 'start'))
    st.append(step(3, 'Resistencia de 10 kΩ',
        'En vertical, en la mitad derecha: de G13 a G15. No importa qué pata va en cada agujero.',
        [('', '10 kΩ · marrón-negro-naranja'), ('', 'G13 ↔ G15')], fig(s3, 'La fila 13 será el punto A0, y la fila 15 es donde llegará el cable rojo del piezo.')))

    s4 = board_svg('Resistencia de 2,2 MΩ cruzando el canal entre E13 y F13', {'r10': True, 'r22': 'new'},
                   ring('E', 13, 'E13', 0, 20) + ring('F', 13, 'F13', 0, 20))
    st.append(step(4, 'Resistencia de 2,2 MΩ, cruzando el canal',
        'En horizontal, cruzando el canal central: de E13 a F13. El canal separa las dos mitades, y esta resistencia es el único puente entre ellas.',
        [('', '2,2 MΩ · rojo-rojo-verde'), ('', 'E13 ↔ F13')], fig(s4, 'A la izquierda de la fila 13 estará GND; a la derecha, A0.')))

    s5 = board_svg('Cable verde de J8 a J13', {'r10': True, 'r22': True, 'green': 'new'},
                   ring('J', 8, 'J8', 14, -10, 'start') + ring('J', 13, 'J13', 14, 14, 'start'))
    st.append(step(5, 'Cable verde: del pin A0 al punto A0',
        'Un extremo en J8, un agujero libre de la fila del pin A0 (fila 8, a la derecha). El otro en J13, en la fila de las resistencias.',
        [('green', 'Cable verde (~5 cm)'), ('', 'J8 → J13')], fig(s5, 'Cuenta bien las filas: el pin A0 es el octavo de la fila derecha, contando RAW como el primero.')))

    s6 = board_svg('Cable negro de B3 a B13', {'r10': True, 'r22': True, 'green': True, 'black': 'new'},
                   ring('B', 3, 'B3', -14, -10, 'end') + ring('B', 13, 'B13', -14, 14, 'end'))
    st.append(step(6, 'Cable negro: del pin GND a la fila 13',
        'Un extremo en B3, un agujero libre de la fila del pin GND de la izquierda (fila 3). El otro en B13, en la mitad izquierda de la fila 13.',
        [('black', 'Cable negro (~6 cm)'), ('', 'B3 → B13')],
        fig(s6, 'Usa el GND de la fila izquierda. En la fila derecha, el primer pin es RAW y NO es masa.')
        + '<div class="warn"><b>Ojo con RAW.</b> Si el cable negro acaba en la fila 1 de la derecha (RAW) en lugar de en GND, A0 marca ~850 en reposo en vez de 0. Es un fallo que ya nos pasó.</div>'))

    s7 = board_svg('Piezo: cable rojo en J15, cable negro en A13', {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': 'new'},
                   ring('J', 15, 'J15', 14, 14, 'start') + ring('A', 13, 'A13', -14, 14, 'end'))
    st.append(step(7, 'Conecta el piezo',
        'El cable rojo va a J15, la fila donde acaba la resistencia de 10 kΩ. El cable negro va a A13, en la mitad izquierda, la de GND. Deja el disco suelto sobre la mesa.',
        [('red', 'Piezo rojo → J15'), ('black', 'Piezo negro → A13')], fig(s7, 'Todavía sin USB. Antes de enchufar, medimos.')))

    prA = probe(H('H', 13), 'red', 'rojo (VΩ)', 60, 30, 'start') + probe(H('C', 13), 'black', 'negro (COM)', -8, 40, 'end')
    s8a = board_svg('Medida entre H13 y C13 con el multímetro', ALL,
                    ring('H', 13, 'H13', 24, -10, 'start') + ring('C', 13, 'C13', -14, 14, 'end') + prA
                    + display(272, 150, '1', 'MΩ', 'escala 2M: sale 1'))
    prB = probe(H('H', 13), 'red', 'rojo (VΩ)', 60, 30, 'start') + probe(H('H', 15), 'black', 'negro (COM)', 60, -10, 'start')
    s8b = board_svg('Medida de 10 kiloohmios entre H13 y H15', ALL,
                    ring('H', 13, 'H13', 24, -10, 'start') + ring('H', 15, 'H15', 24, 14, 'start') + prB
                    + display(272, 150, '10.0', 'kΩ', 'escala 200k'))
    st.append(step(8, 'Mide con el multímetro (sin USB)',
        'Selector en ohmios (Ω). No toques las puntas metálicas con los dedos. En la medida A tu multímetro, que llega a 2 MΩ, marca 1 (fuera de escala) porque 2,2 MΩ es mayor. Lo importante es que NO marque un valor bajo.',
        [('', 'A: H13 y C13 → 1 (fuera de escala)'), ('', 'B: H13 y H15 → 10 kΩ (9,5–10,5)')],
        fig(s8a, 'Medida A, escala 2M. Si marca un valor bajo (por ejemplo 0.0x), hay un cortocircuito: revisa los cables verde y negro.')
        + fig(s8b, 'Medida B, escala 200k: solo la resistencia de 10 kΩ. Si no sale ~10, repasa el paso 3.')))

    pr9 = probe(H('H', 13), 'red', 'rojo (V)', 60, 30, 'start') + probe(H('C', 13), 'black', 'negro (COM)', -8, 40, 'end')
    s9 = board_svg('Medida de tensión continua entre H13 y C13 con el USB conectado', ALL,
                   ring('H', 13, 'H13', 24, -10, 'start') + ring('C', 13, 'C13', -14, 14, 'end') + pr9
                   + '<path d="M156,50 V18" class="usbline"/><text x="162" y="22" class="lbl">USB al Mac</text>'
                   + display(272, 150, '0.00', 'V', 'escala 20 V DC'))
    st.append(step(9, 'Conecta el USB y mide la tensión',
        'Selector en voltios de continua (V con línea recta), escala 20 V. Las puntas van en los mismos agujeros. El piezo debe estar quieto.',
        [('', 'Esperado: 0,00 a 0,05 V')],
        fig(s9, 'En reposo, A0 está a 0 V gracias a la resistencia de 2,2 MΩ. Si marca ~4 V, el cable negro está en RAW; si marca 5 V, apaga y repasa los cables.')))

    st.append(step(10, 'Mira la señal y golpea',
        'Carga el sketch 01_piezo_plotter y abre tools/osciloscopio.html en Chrome. Pulsa Conectar placa, elige usbmodem y toca el disco con la yema del dedo.',
        [('', 'Reposo: 0 a 5'), ('', 'Golpe suave: ~60 · firme: hasta ~490')],
        fig(fig_waves(), 'Una gráfica sana vive en 0 y sube con cada golpe; el pico decae solo en medio segundo.')))
    return ''.join(st)

CSS = '''
:root{
  --paper:#FCFCFB; --ink:#16181B; --muted:#5C646B; --rule:#D5D9DC; --soft:#F0F2F3;
  --bb:#ECEFF1; --gapc:#D9DEE1; --hole:#8E979E; --pcb:#233A6B; --pin:#C9A227;
  --accent:#D9480F; --halo:#FCFCFB; --halo-k:#FCFCFB;
  --w-red:#D62828; --w-green:#2E9E44; --w-black:#1A1A1A;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  --disp:'Archivo','Helvetica Neue',Arial,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#101214; --ink:#ECEEF0; --muted:#9AA2A9; --rule:#2B3136; --soft:#181B1E;
  --bb:#1D2226; --gapc:#14171A; --hole:#4C555C; --pcb:#2E4A86;
  --accent:#FF8A5B; --halo:#101214; --halo-k:#C9CED3; --w-black:#0A0A0A; color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#101214; --ink:#ECEEF0; --muted:#9AA2A9; --rule:#2B3136; --soft:#181B1E;
  --bb:#1D2226; --gapc:#14171A; --hole:#4C555C; --pcb:#2E4A86;
  --accent:#FF8A5B; --halo:#101214; --halo-k:#C9CED3; --w-black:#0A0A0A; color-scheme:dark}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.5;
  padding-block:32px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:44px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(34px,7vw,56px);line-height:1.02;margin:8px 0 12px;letter-spacing:-.01em;text-wrap:balance}
.lead{font-size:18px;max-width:60ch;margin:0;color:var(--ink)}
.meta{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:16px;font-family:var(--mono);font-size:13px;color:var(--muted)}
h2{font-family:var(--disp);font-weight:800;font-size:26px;margin:0 0 14px;text-wrap:balance}
section{display:flex;flex-direction:column}
p{margin:0}
.dia{margin:14px 0 0;border:1.5px solid var(--ink);border-radius:4px;background:var(--paper)}
.dia figcaption{font-size:14px;color:var(--muted);padding:10px 14px;border-top:1px solid var(--rule);max-width:70ch}
.scroll{overflow-x:auto}
.dia svg{display:block;width:100%;height:auto;min-width:340px;max-width:560px;margin:0 auto}
.dia svg[viewBox^="0 0 560"]{max-width:none;min-width:560px}
.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:40px}
.step{display:grid;grid-template-columns:76px minmax(0,1fr);gap:16px;padding-top:28px;border-top:3px solid var(--ink)}
.num{font-family:var(--disp);font-weight:800;font-size:64px;line-height:.9;letter-spacing:-.02em}
.sbody{min-width:0;display:flex;flex-direction:column;gap:10px}
.step h3{font-size:21px;margin:4px 0 0;font-weight:600;text-wrap:balance}
.step p{max-width:62ch}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:13px;font-weight:500;border:1.5px solid var(--ink);border-radius:4px;padding:3px 9px;background:var(--soft)}
.chip i{width:11px;height:11px;border-radius:50%;background:var(--muted);flex:none}
.chip.red i{background:var(--w-red)}.chip.green i{background:var(--w-green)}.chip.black i{background:var(--w-black);outline:1.5px solid var(--halo-k)}
.warn{border:1.5px solid var(--accent);border-left-width:6px;padding:12px 14px;border-radius:4px;max-width:70ch}
.warn b{color:var(--accent)}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--ink)}
.tscroll{overflow-x:auto}
.tscroll table{min-width:560px}
.map{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}
.map div{border:1.5px solid var(--ink);border-radius:4px;padding:10px 12px;background:var(--soft);font-size:14px}
.map b{display:block;font-family:var(--mono);font-size:13px;margin-bottom:2px}
.dia text{font-family:var(--mono)}
.bb{fill:var(--bb);stroke:var(--ink);stroke-width:1.2}
.gapc{fill:var(--gapc)}
.hole{fill:var(--hole)}
.col{font-size:8px;fill:var(--muted);text-anchor:middle}
.rowl{font-size:7px;fill:var(--muted)}
.lbl{font-size:9px;fill:var(--muted)}
.pcb{fill:var(--pcb);stroke:var(--ink);stroke-width:1}
.usb{fill:#B8C0C8;stroke:var(--ink);stroke-width:1}
.pin{fill:var(--pin)}
.pn{font-size:6.5px;fill:#EAF0FF}
.mcu{fill:#0E1220;stroke:#5A6A9A;stroke-width:1}
.old{opacity:.5}
.leg{stroke:var(--ink);stroke-width:1.6}
.rbody{fill:#E3CF9C;stroke:#6B5A2E;stroke-width:1}
.ring{fill:none;stroke:var(--accent);stroke-width:2}
.hn{font-size:9px;font-weight:700;fill:var(--accent);paint-order:stroke;stroke:var(--paper);stroke-width:3px;stroke-linejoin:round}
.wh{fill:none;stroke:var(--halo);stroke-width:7;stroke-linecap:round}
.wh-k{fill:none;stroke:var(--halo-k);stroke-width:7;stroke-linecap:round}
.wc{fill:none;stroke-width:3.4;stroke-linecap:round}
.wc.w-red{stroke:var(--w-red)}.wc.w-green{stroke:var(--w-green)}.wc.w-black{stroke:var(--w-black)}
.wend.w-red{fill:var(--w-red)}.wend.w-green{fill:var(--w-green)}.wend.w-black{fill:var(--w-black);stroke:var(--halo-k);stroke-width:1}
.brass{fill:#C9A24A;stroke:var(--ink);stroke-width:1.2}
.ceramic{fill:#EDE6D2;stroke:#7A6A3A;stroke-width:1}
.prb-red{stroke:var(--w-red);stroke-width:4;stroke-linecap:round}
.prb-black{stroke:var(--ink);stroke-width:4;stroke-linecap:round}
.prb-tip-red{fill:var(--w-red)}.prb-tip-black{fill:var(--ink)}
.mm{fill:#C5D3B8;stroke:var(--ink);stroke-width:1.5}
.mmv{font-size:30px;font-weight:700;fill:#1B2418}
.mmu{font-size:11px;fill:#1B2418}
.usbline{stroke:var(--ink);stroke-width:3;fill:none;stroke-linecap:round}
.sline{stroke:var(--ink);stroke-width:2;fill:none}
.w-red-s{stroke:var(--w-red)}.w-black-s{stroke:var(--ink)}
.sbox{fill:var(--soft);stroke:var(--ink);stroke-width:1.6}
.stxt{font-size:11px;fill:var(--ink)}
.sdot{fill:var(--ink)}
.spm{fill:var(--pcb);stroke:var(--ink);stroke-width:1.2}
.spt{font-size:10px;fill:#EAF0FF}
.ins{fill:var(--w-red)}
.strand{fill:#B87333}
.tinned{fill:#CDD3D8;stroke:#8A939A;stroke-width:1}
.plotbg{fill:var(--soft);stroke:var(--ink);stroke-width:1.2}
.trace{fill:none;stroke:var(--accent);stroke-width:1.8;stroke-linejoin:round}
@media (max-width:560px){
  .step{grid-template-columns:1fr;gap:6px}
  .num{font-size:48px}
}
'''

def main():
    h = []
    h.append('<title>Piezo en protoboard</title>')
    h.append('<meta charset="utf-8"><meta name="claude:viewport-fit-sides" content="cover">')
    h.append('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    h.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">')
    h.append(f'<style>{CSS}</style>')
    h.append('<main class="wrap">')
    h.append('<header><div class="eyebrow">Noise Box · Pro Micro · Manual 01 · versión mini protoboard</div><h1>Piezo en la protoboard</h1>'
             '<p class="lead">Al terminar verás en el ordenador cada golpe que des al piezo. El montaje ocupa solo las filas 1 a 15, así que sirve igual para la protoboard grande y para la mini de 170 puntos que irá dentro de la lata.</p>'
             '<div class="meta"><span>30–40 min</span><span>soldar solo las puntas del piezo</span><span>5 V · USB</span></div></header>')
    h.append('<section><h2>Qué vamos a montar</h2>' + fig(schematic(),
        'El golpe genera un pico de tensión en el piezo. La resistencia de 10 kΩ protege el pin y la de 2,2 MΩ mantiene A0 en 0 V cuando no hay golpe.') + '</section>')
    h.append('<section><h2>Dónde va cada cosa</h2><div class="map">'
             '<div><b>Fila 8, derecha</b>pin A0 de la Pro Micro</div>'
             '<div><b>Fila 3, izquierda</b>pin GND de la Pro Micro</div>'
             '<div><b>Fila 13</b>izquierda = GND, derecha = A0. Las separa el canal central, y la 2,2 MΩ cruza por encima.</div>'
             '<div><b>Fila 15, derecha</b>llegada del cable rojo del piezo, tras la resistencia de 10 kΩ</div>'
             '</div></section>')
    h.append('<section><h2>Material</h2>' + fig(fig_parts(), 'Comprueba los colores antes de usarlas. La tercera banda es la que las distingue de las de 100 kΩ y 220 Ω.') +
             '<p style="margin-top:12px">Protoboard (mini de 170 puntos, o la grande usando solo las filas 1–15), Pro Micro con pines, piezo, cable rígido verde (~5 cm) y negro (~6 cm), soldador con estaño, multímetro y cable USB.</p></section>')
    h.append('<section><h2>Montaje</h2><ol class="steps">' + steps_html() + '</ol></section>')
    h.append('<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Causa probable</th><th>Qué hacer</th></tr></thead><tbody>'
             '<tr><td>A0 marca ~850 en reposo</td><td>Cable negro en RAW en vez de GND</td><td>Muévelo a la fila 3 de la izquierda (GND)</td></tr>'
             '<tr><td>Línea pegada arriba (~1023)</td><td>A0 no llega a masa por la 2,2 MΩ</td><td>Revisa E13, F13 y el cable negro B3 → B13</td></tr>'
             '<tr><td>Ruido continuo sin tocar nada</td><td>Cable verde o 2,2 MΩ flojos</td><td>Aprieta J8, J13, E13 y F13</td></tr>'
             '<tr><td>Línea en 0 y no sube al golpear</td><td>Punta del piezo floja</td><td>Revisa J15 y A13; golpea el propio disco</td></tr>'
             '<tr><td>No hay gráfica</td><td>Sketch MIDI cargado, o puerto ocupado</td><td>Sube 01_piezo_plotter y cierra otros programas que usen el USB</td></tr>'
             '</tbody></table></div></section>')
    h.append('<section><h2>Siguiente manual</h2><p>Manual 02: cada golpe como nota MIDI con velocity. Se reutiliza este montaje tal cual.</p></section>')
    h.append('</main>')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(h))
    print('ok', OUT)

main()
