#!/usr/bin/env python3
# Genera manuals/01-piezo-en-protoboard.html (SVG estático, sin JS)
import math, random

OUT = "/Users/pasta0126/arduino-projects/NoiseBox_ProMicro/manuals/01-piezo-en-protoboard.html"

P = 16
def X(c): return 56 + (c - 8) * P
ROW = {'A': 134, 'B': 150, 'C': 166, 'D': 182, 'E': 198, 'F': 246, 'G': 262, 'H': 278, 'I': 294, 'J': 310}
def H(c, r): return X(c), ROW[r]

TOP = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', '15', '14', '16', '10']
BOT = ['TX0', 'RX1', 'GND', 'GND', '2', '3', '4', '5', '6', '7', '8', '9']

BANDS = {'yellow': '#E8C000', 'brown': '#7A4A22', 'black': '#111111', 'orange': '#F08A00', 'red': '#D62828', 'green': '#2E9E44', 'gold': '#C9A227'}

# ---------- piezas de la protoboard ----------
def board_base():
    s = ['<rect x="36" y="104" width="456" height="220" rx="6" class="bb"/>',
         '<rect x="36" y="212" width="456" height="20" class="gapc"/>']
    for c in range(8, 35):
        s.append(f'<text x="{X(c)}" y="119" class="col">{c}</text>')
        for r in ROW:
            s.append(f'<circle cx="{X(c)}" cy="{ROW[r]}" r="2.3" class="hole"/>')
    for r in ROW:
        s.append(f'<text x="46" y="{ROW[r] + 3}" class="rowl">{r}</text>')
    return ''.join(s)

def promicro(ghost=False):
    x0, x1 = X(10) - 12, X(21) + 12
    g = [f'<g class="{"ghost" if ghost else "pm"}">']
    g.append(f'<rect x="{x0 - 20}" y="219" width="22" height="22" rx="2" class="usb"/>')
    g.append(f'<rect x="{x0}" y="172" width="{x1 - x0}" height="116" rx="4" class="pcb"/>')
    if not ghost:
        g.append('<rect x="130" y="212" width="36" height="36" rx="2" class="mcu"/>')
        g.append('<text x="148" y="234" class="pn">32U4</text>')
        g.append('<rect x="196" y="236" width="32" height="12" rx="2" class="mcu"/>')
        g.append('<text x="214" y="226" class="pn">PRO MICRO</text>')
    for i, c in enumerate(range(10, 22)):
        g.append(f'<rect x="{X(c) - 4}" y="178" width="8" height="8" class="pin"/>')
        g.append(f'<rect x="{X(c) - 4}" y="274" width="8" height="8" class="pin"/>')
        if not ghost:
            g.append(f'<text x="{X(c)}" y="198" class="pn">{TOP[i]}</text>')
            g.append(f'<text x="{X(c)}" y="268" class="pn">{BOT[i]}</text>')
    g.append(f'<text x="{x0 - 9}" y="256" class="lbl" text-anchor="middle">USB</text>')
    if ghost:
        g.append(f'<text x="{(x0 + x1) // 2}" y="234" class="gtxt">aquí irá la Pro Micro (al final)</text>')
    g.append('</g>')
    return ''.join(g)

def resistor(c1, c2, r, bands):
    x1, y = H(c1, r); x2, _ = H(c2, r)
    bx, bw = x1 + 12, (x2 - x1) - 24
    s = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="leg"/>',
         f'<rect x="{bx}" y="{y - 5}" width="{bw}" height="10" rx="4" class="rbody"/>']
    for i, b in enumerate(bands):
        s.append(f'<rect x="{bx + 4 + i * 5}" y="{y - 5}" width="3" height="10" fill="{BANDS[b]}"/>')
    s.append(f'<rect x="{bx + bw - 5}" y="{y - 5}" width="3" height="10" fill="{BANDS["gold"]}"/>')
    return ''.join(s)

def wire(d, color, ends):
    halo = 'wh-k' if color == 'black' else 'wh'
    s = [f'<path d="{d}" class="{halo}"/>', f'<path d="{d}" class="wc w-{color}"/>']
    for (x, y) in ends:
        s.append(f'<circle cx="{x}" cy="{y}" r="3.2" class="wend w-{color}"/>')
    return ''.join(s)

def arc(a, b, color, peak):
    (x1, y1), (x2, y2) = a, b
    d = f'M{x1},{y1} C{x1},{y1 - peak} {x2},{y2 - peak} {x2},{y2}'
    return wire(d, color, [a, b])

def ring(c, r, name, dx=0, dy=-13):
    x, y = H(c, r)
    return (f'<circle cx="{x}" cy="{y}" r="7" class="ring"/>'
            f'<text x="{x + dx}" y="{y + dy}" class="hn">{name}</text>')

PIEZO_C = (520, 46)

def piezo_disc():
    cx, cy = PIEZO_C
    return (f'<circle cx="{cx}" cy="{cy}" r="26" class="brass"/>'
            f'<circle cx="{cx}" cy="{cy}" r="17" class="ceramic"/>'
            f'<circle cx="{cx}" cy="{cy}" r="3" class="w-red wend"/>'
            f'<text x="{cx}" y="{cy + 42}" class="lbl" text-anchor="middle">piezo</text>')

def piezo_wires():
    red = wire('M520,46 C440,40 328,56 328,134', 'red', [(328, 134)])
    blk = wire('M520,72 C520,130 470,150 424,150', 'black', [(424, 150)])
    return red + blk

def probe(tip, color, label, dx, dy):
    x, y = tip
    x2, y2 = x + dx, y + dy
    return (f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" class="prb-{color}"/>'
            f'<circle cx="{x}" cy="{y}" r="3" class="prb-tip-{color}"/>'
            f'<text x="{x2}" y="{y2 - 6}" class="hn" style="fill:var(--ink)">{label}</text>')

def display(x, y, value, unit, scale):
    return (f'<rect x="{x}" y="{y}" width="170" height="54" rx="6" class="mm"/>'
            f'<text x="{x + 12}" y="{y + 36}" class="mmv">{value}</text>'
            f'<text x="{x + 158}" y="{y + 22}" class="mmu" text-anchor="end">{unit}</text>'
            f'<text x="{x + 158}" y="{y + 44}" class="mmu" text-anchor="end" style="font-size:8px">{scale}</text>')

# ---------- figura de protoboard acumulativa ----------
def board_svg(aria, parts, rings='', extra='', ghost=True, solid_pm=False):
    """parts: dict con claves r10,r22,green,black,piezo (True/'new'/False)"""
    def wrap(key, content):
        st = parts.get(key)
        if not st: return ''
        return content if st == 'new' else f'<g class="old">{content}</g>'
    if parts.get('black') or parts.get('piezo') or extra:
        vb = '0 0 560 340'
    elif parts.get('green'):
        vb = '0 70 560 270'
    else:
        vb = '0 92 560 248'
    s = [f'<svg viewBox="{vb}" role="img" aria-label="{aria}">', board_base()]
    s.append(promicro(ghost=False) if solid_pm else (promicro(ghost=True) if ghost else ''))
    s.append(wrap('r10', resistor(25, 28, 'C', ['brown', 'black', 'orange'])))
    s.append(wrap('r22', resistor(28, 31, 'E', ['brown', 'black', 'yellow'])))
    s.append(wrap('green', arc(H(17, 'A'), H(28, 'A'), 'green', 46)))
    s.append(wrap('black', arc(H(11, 'A'), H(31, 'A'), 'black', 100)))
    if parts.get('piezo'):
        pz = piezo_disc() + piezo_wires()
        s.append(pz if parts['piezo'] == 'new' else f'<g class="old">{pz}</g>')
    s.append(rings)
    s.append(extra)
    s.append('</svg>')
    return ''.join(s)

def fig(svg, cap):
    return f'<figure class="dia"><div class="scroll">{svg}</div><figcaption>{cap}</figcaption></figure>'

def chips(items):
    out = []
    for cls, txt in items:
        out.append(f'<span class="chip {cls}"><i></i>{txt}</span>')
    return '<div class="chips">' + ''.join(out) + '</div>'

def step(n, title, text, chip_items, figure):
    return (f'<li class="step" id="p{n}"><div class="num" aria-hidden="true">{n}</div>'
            f'<div class="sbody"><h3>{title}</h3><p>{text}</p>{chips(chip_items) if chip_items else ""}{figure}</div></li>')

# ---------- esquema del mecanismo ----------
def schematic():
    return '''<svg viewBox="0 0 560 210" role="img" aria-label="Esquema: el piezo entra por una resistencia de 10 kΩ al pin A0, y una resistencia de 100 kΩ lleva A0 a masa">
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
<text x="292" y="148" class="stxt">100 kΩ</text>
<text x="292" y="162" class="lbl">devuelve A0 a 0 V</text>
<path d="M270,166 V186" class="sline"/>
<path d="M254,186 H286 M259,192 H281 M264,198 H276" class="sline"/>
<text x="296" y="194" class="lbl">GND</text>
<path d="M60,116 V186 H270" class="sline w-black-s"/>
</svg>'''

# ---------- figuras previas ----------
def fig_pins():
    return '''<svg viewBox="0 0 560 150" role="img" aria-label="Vista lateral: a la izquierda una placa con pines metálicos por debajo; a la derecha una placa con solo agujeros">
<g transform="translate(40,10)">
<rect x="0" y="30" width="220" height="14" rx="3" class="pcb"/>
<rect x="8" y="14" width="26" height="16" rx="2" class="usb"/>
''' + ''.join(f'<rect x="{12 + i * 17}" y="44" width="4" height="26" class="pin"/>' for i in range(12)) + '''
<text x="110" y="100" class="stxt" text-anchor="middle">SÍ: pines metálicos por debajo</text>
<text x="110" y="118" class="lbl" text-anchor="middle">entra en la protoboard</text>
</g>
<g transform="translate(300,10)">
<rect x="0" y="30" width="220" height="14" rx="3" class="pcb"/>
<rect x="8" y="14" width="26" height="16" rx="2" class="usb"/>
''' + ''.join(f'<circle cx="{14 + i * 17}" cy="37" r="3" class="hole"/>' for i in range(12)) + '''
<text x="110" y="100" class="stxt" text-anchor="middle">NO: solo agujeros</text>
<text x="110" y="118" class="lbl" text-anchor="middle">hay que soldar pines primero</text>
</g></svg>'''

def fig_parts():
    def res(x, y, bands, name, color):
        s = f'<line x1="{x}" y1="{y}" x2="{x + 120}" y2="{y}" class="leg"/><rect x="{x + 30}" y="{y - 9}" width="60" height="18" rx="7" class="rbody"/>'
        for i, b in enumerate(bands):
            s += f'<rect x="{x + 40 + i * 11}" y="{y - 9}" width="6" height="18" fill="{BANDS[b]}"/>'
        s += f'<rect x="{x + 76}" y="{y - 9}" width="5" height="18" fill="{BANDS["gold"]}"/>'
        s += f'<text x="{x + 60}" y="{y + 30}" class="stxt" text-anchor="middle">{name}</text>'
        s += f'<text x="{x + 60}" y="{y + 44}" class="lbl" text-anchor="middle">{color}</text>'
        return s
    return ('<svg viewBox="0 0 560 120" role="img" aria-label="Las dos resistencias con sus bandas de color: 10 kΩ marrón negro naranja, 100 kΩ marrón negro amarillo">'
            + res(30, 40, ['brown', 'black', 'orange'], '10 kΩ', 'marrón · negro · naranja')
            + res(230, 40, ['brown', 'black', 'yellow'], '100 kΩ', 'marrón · negro · amarillo')
            + '<text x="440" y="36" class="lbl">la banda dorada</text><text x="440" y="50" class="lbl">va siempre a la derecha</text></svg>')

def fig_tin():
    def stage(x, label, kind):
        s = f'<g transform="translate({x},20)"><rect x="0" y="22" width="70" height="16" rx="6" class="ins"/>'
        if kind == 1:
            s += '<rect x="70" y="26" width="30" height="8" class="strand"/>'
        elif kind == 2:
            s += '<rect x="70" y="27" width="30" height="6" rx="3" class="strand"/>'
        else:
            s += '<rect x="70" y="27" width="30" height="6" rx="3" class="tinned"/>'
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
        pts = []
        rnd = random.Random(7)
        for px in range(10, w - 6):
            if kind == 'ok':
                y = 0
                for (hx, amp) in [(24, 70), (80, 52), (122, 30)]:
                    t = px - hx
                    if t >= 0:
                        y += amp * math.exp(-t / 9) * max(0, math.sin(t * 0.55))
                yy = base - y
            elif kind == 'high':
                yy = top + 8 + rnd.random() * 2
            else:
                yy = base - 18 - rnd.random() * 60
            pts.append(f'{x0 + px},{yy:.1f}')
        g += f'<polyline points="{" ".join(pts)}" class="trace"/>'
        g += f'<text x="{x0 + w / 2}" y="{top + h + 16}" class="stxt" text-anchor="middle">{title}</text>'
        return g
    return ('<svg viewBox="0 0 560 150" role="img" aria-label="Tres gráficas: bien, reposo en cero con picos al golpear; mal, línea pegada arriba; mal, ruido continuo">'
            + panel(8, 'BIEN', 'ok') + panel(196, 'MAL: pegada arriba', 'high') + panel(384, 'MAL: ruido sin tocar', 'noise') + '</svg>')

# ---------- pasos ----------
def steps_html():
    st = []
    st.append(step(1, 'Prepara las puntas del piezo',
        'Las puntas de los cables son de hilo fino y no se clavan bien en la protoboard. Pela 5 mm, retuerce los hilos y cúbrelos con un poco de estaño.',
        [('red', 'Cable rojo (centro del disco)'), ('black', 'Cable negro (latón)')], fig(fig_tin(), 'Cada punta debe quedar plateada y rígida.')))

    ghost_only = {}
    s2 = board_svg('Protoboard con la resistencia de 10 kΩ entre C25 y C28', {'r10': 'new'},
                   ring(25, 'C', 'C25', -4, 22) + ring(28, 'C', 'C28', 4, 22))
    st.append(step(2, 'Resistencia de 10 kΩ',
        'Colócala en horizontal, en la fila C, de la columna 25 a la 28. No importa qué pata va en cada agujero.',
        [('', '10 kΩ · marrón-negro-naranja'), ('', 'C25 ↔ C28')], fig(s2, 'La protoboard está girada con las letras A–E arriba. El recuadro punteado es el sitio de la Pro Micro, que se pone al final.')))

    s3 = board_svg('Se añade la resistencia de 100 kΩ entre E28 y E31', {'r10': True, 'r22': 'new'},
                   ring(28, 'E', 'E28', -4, 22) + ring(31, 'E', 'E31', 4, 22))
    st.append(step(3, 'Resistencia de 100 kΩ',
        'Fila E, de la columna 28 a la 31. Así queda unida a la resistencia anterior por la columna 28.',
        [('', '100 kΩ · marrón-negro-amarillo'), ('', 'E28 ↔ E31')], fig(s3, 'La columna 28 une las dos resistencias. Ese punto será el pin A0.')))

    s4 = board_svg('Cable verde de A17 a A28', {'r10': True, 'r22': True, 'green': 'new'},
                   ring(17, 'A', 'A17', 0, -13) + ring(28, 'A', 'A28', 0, -13))
    st.append(step(4, 'Cable verde: hacia el pin A0',
        'Un extremo en A17 (la columna donde quedará el pin A0 de la placa). El otro en A28, la columna que une las dos resistencias.',
        [('green', 'Cable verde'), ('', 'A17 → A28')], fig(s4, 'Si la Pro Micro entra con RAW en la columna 10, el pin A0 cae en la columna 17.')))

    s5 = board_svg('Cable negro de A11 a A31', {'r10': True, 'r22': True, 'green': True, 'black': 'new'},
                   ring(11, 'A', 'A11', 0, -13) + ring(31, 'A', 'A31', 14, -13))
    st.append(step(5, 'Cable negro: hacia GND',
        'Un extremo en A11 (columna del pin GND). El otro en A31, donde acaba la resistencia de 100 kΩ.',
        [('black', 'Cable negro'), ('', 'A11 → A31')], fig(s5, 'Este cable lleva la masa de la placa hasta el final de la resistencia de 100 kΩ.')))

    s6 = board_svg('Piezo: cable rojo en A25, cable negro en B31', {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': 'new'},
                   ring(25, 'A', 'A25', -14, -13) + ring(31, 'B', 'B31', 22, 4))
    st.append(step(6, 'Conecta el piezo',
        'El cable rojo va a A25, junto a la resistencia de 10 kΩ. El cable negro va a B31, en la columna de GND. Deja el disco suelto sobre la mesa.',
        [('red', 'Piezo rojo → A25'), ('black', 'Piezo negro → B31')], fig(s6, 'Todavía no hay corriente: la placa aún no está puesta.')))

    pr = probe(H(17, 'B'), 'red', 'rojo (VΩ)', -52, -62) + probe(H(11, 'B'), 'black', 'negro (COM)', -30, -70)
    s7a = board_svg('Medida de 100 kiloohmios entre B17 y B11',
                    {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': True},
                    ring(17, 'B', 'B17', 22, 5) + ring(11, 'B', 'B11', 22, 5) + pr + display(300, 252, '100', 'kΩ', 'escala 200k'))
    pr2 = probe(H(25, 'B'), 'red', 'rojo (VΩ)', -30, -62) + probe(H(28, 'B'), 'black', 'negro (COM)', 28, -62)
    s7b = board_svg('Medida de 10 kiloohmios entre B25 y B28',
                    {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': True},
                    ring(25, 'B', 'B25', -22, 5) + ring(28, 'B', 'B28', 22, 5) + pr2 + display(300, 252, '10.0', 'kΩ', 'escala 200k'))
    st.append(step(7, 'Mide con el multímetro (sin la placa)',
        'Gira el selector a ohmios (Ω). No toques las puntas metálicas con los dedos. Si un valor no sale, repasa el paso indicado antes de seguir.',
        [('', 'Medida A: B17 y B11 → 100 kΩ (95–105)'), ('', 'Medida B: B25 y B28 → 10 kΩ (9,5–10,5)')],
        fig(s7a, 'Medida A, escala 200k: mide la resistencia de 100 kΩ a través de los cables verde y negro. Si marca "1" o "OL", falta un cable (pasos 3, 4 o 5).')
        + fig(s7b, 'Medida B, escala 200k: mide solo la resistencia de 10 kΩ. Si no sale ~10, repasa el paso 2.')))

    sp = board_svg('Pro Micro insertada en la protoboard con el USB a la izquierda',
                   {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': True},
                   ring(10, 'D', 'RAW · col. 10', 12, -34) + ring(17, 'D', 'A0', 0, -34) + ring(11, 'D', 'GND', 6, -22),
                   ghost=False, solid_pm=True)
    st.append(step(8, 'Inserta la Pro Micro',
        'USB a la izquierda. El pin RAW queda en la columna 10, en la fila de arriba. Presiona por los dos bordes a la vez, nunca sobre el chip ni el conector USB.',
        [('', 'RAW en col. 10'), ('', 'GND (arriba) en col. 11'), ('', 'A0 en col. 17')],
        fig(sp, 'Comprueba que el pin A0 queda en la columna del cable verde y el pin GND en la del cable negro.')))

    pr3 = probe(H(17, 'B'), 'red', 'rojo (VΩ)', -52, -62) + probe(H(11, 'B'), 'black', 'negro (COM)', -30, -70)
    cable = '<path d="M58,230 H16" class="usbline"/><text x="8" y="222" class="lbl">USB al Mac</text>'
    s9 = board_svg('Medida de tensión continua entre B17 y B11 con el USB conectado',
                   {'r10': True, 'r22': True, 'green': True, 'black': True, 'piezo': True},
                   ring(17, 'B', 'B17', 22, 5) + ring(11, 'B', 'B11', 22, 5) + pr3 + cable + display(300, 252, '0.00', 'V', 'escala 20 V DC'),
                   ghost=False, solid_pm=True)
    st.append(step(9, 'Conecta el USB y mide la tensión',
        'Selector en voltios de continua (V con línea recta) en la escala de 20 V. Las puntas van en los mismos agujeros que en la medida A. El piezo debe estar quieto.',
        [('', 'Esperado: 0,00 a 0,05 V')],
        fig(s9, 'En reposo, A0 está a 0 V gracias a la resistencia de 100 kΩ. Si marca 5 V o 2,5 V, apaga y repasa los cables verde y negro.')))

    st.append(step(10, 'Abre el Serial Plotter y golpea',
        'El sketch del paso 1 ya está subido. En Arduino IDE: Herramientas → Placa → Arduino Micro, el puerto usbmodem, Herramientas → Serial Plotter, y 115200 baudios. Toca el disco con la yema del dedo.',
        [('', 'Suave: picos de 20 a 300'), ('', 'Fuerte con el dedo: hasta ~800')],
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
.dia svg{display:block;width:100%;min-width:560px;height:auto}
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
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:20px}
.card{border:1.5px solid var(--ink);border-radius:4px;padding:16px;display:flex;flex-direction:column;gap:10px;min-width:0}
.card h3{margin:0;font-size:18px}
.card .dia{margin-top:4px}
.warn{border:1.5px solid var(--accent);border-left-width:6px;padding:12px 14px;border-radius:4px;max-width:70ch}
.warn b{color:var(--accent)}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--ink)}
.tscroll{overflow-x:auto}
.tscroll table{min-width:560px}
/* svg */
.dia text{font-family:var(--mono)}
.bb{fill:var(--bb);stroke:var(--ink);stroke-width:1.2}
.gapc{fill:var(--gapc)}
.hole{fill:var(--hole)}
.col{font-size:7px;fill:var(--muted);text-anchor:middle}
.rowl{font-size:8px;fill:var(--muted);text-anchor:middle}
.lbl{font-size:9px;fill:var(--muted)}
.pcb{fill:var(--pcb);stroke:var(--ink);stroke-width:1}
.usb{fill:#B8C0C8;stroke:var(--ink);stroke-width:1}
.pin{fill:var(--pin)}
.pn{font-size:7px;fill:#EAF0FF;text-anchor:middle}

.mcu{fill:#0E1220;stroke:#5A6A9A;stroke-width:1}
.ghost .pcb{fill:none;stroke:var(--muted);stroke-dasharray:5 4}
.ghost .usb{fill:none;stroke:var(--muted);stroke-dasharray:4 3}
.ghost .pin{fill:var(--muted);opacity:.5}
.gtxt{font-size:9px;fill:var(--muted);text-anchor:middle}
.old{opacity:.5}
.leg{stroke:var(--ink);stroke-width:1.6}
.rbody{fill:#E3CF9C;stroke:#6B5A2E;stroke-width:1}
.ring{fill:none;stroke:var(--accent);stroke-width:2}
.hn{font-size:9px;font-weight:700;fill:var(--accent);text-anchor:middle;paint-order:stroke;stroke:var(--paper);stroke-width:3px;stroke-linejoin:round}
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
    html = []
    html.append('<title>Piezo en protoboard</title>')
    html.append('<meta charset="utf-8"><meta name="claude:viewport-fit-sides" content="cover">')
    html.append('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    html.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">')
    html.append(f'<style>{CSS}</style>')
    html.append('<main class="wrap">')
    html.append('<header><div class="eyebrow">Noise Box · Pro Micro · Manual 01</div><h1>Piezo en la protoboard</h1>'
                '<p class="lead">Al terminar verás en el ordenador cada golpe que des al piezo, dibujado como un pico en una gráfica.</p>'
                '<div class="meta"><span>30–40 min</span><span>soldar solo las puntas del piezo</span><span>5 V · USB</span></div></header>')

    html.append('<section><h2>Qué vamos a montar</h2>' + fig(schematic(),
        'El golpe genera un pico de tensión en el piezo. La resistencia de 10 kΩ protege el pin y la de 100 kΩ mantiene A0 en 0 V cuando no hay golpe.') + '</section>')

    html.append('<section><h2>Antes de empezar</h2><div class="cards">'
        '<div class="card"><h3>A. ¿Tu Pro Micro tiene pines?</h3>' + fig(fig_pins(), 'Mira la placa de lado.') +
        '<div class="warn"><b>En tu foto solo se ven agujeros.</b> Sin pines la placa no se clava en la protoboard. Si es tu caso, hacen falta 2 tiras de 12 pines macho (unos 1 €) y soldarlas. Dímelo y preparo ese manual primero.</div></div>'
        '<div class="card"><h3>B. Material de este manual</h3>' + fig(fig_parts(), 'Comprueba los colores antes de usarlas.') +
        '<p>Protoboard, Pro Micro, piezo, cable rígido verde (unos 12 cm) y negro (unos 25 cm), soldador con estaño, multímetro y cable USB.</p></div>'
        '</div></section>')

    html.append('<section><h2>Montaje</h2><ol class="steps">' + steps_html() + '</ol></section>')

    html.append('<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Causa probable</th><th>Qué hacer</th></tr></thead><tbody>'
        '<tr><td>Línea pegada arriba (~1023)</td><td>A0 no llega a masa por la 100 kΩ</td><td>Repite la medida A del paso 7</td></tr>'
        '<tr><td>Ruido continuo sin tocar nada</td><td>Cable verde o 100 kΩ flojos</td><td>Aprieta E28, E31 y A28; mide de nuevo</td></tr>'
        '<tr><td>Línea en 0 y no sube al golpear</td><td>Punta del piezo floja</td><td>Revisa A25 y B31; golpea el propio disco</td></tr>'
        '<tr><td>No hay gráfica</td><td>Placa o puerto mal elegidos</td><td>Placa Arduino Micro, puerto usbmodem, 115200</td></tr>'
        '</tbody></table></div></section>')

    html.append('<section><h2>Siguiente manual</h2><p>Manual 02: convertir cada golpe en una nota MIDI con velocity. Se reutiliza este montaje tal cual.</p></section>')
    html.append('</main>')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    print('ok', OUT)

main()
