#!/usr/bin/env python3
# Genera manuals/caja-muelle.html: montaje completo y simple de la caja.
# Pro Micro en la protoboard de 170 puntos (USB arriba, patillas en D1-D12 y H1-H12),
# piezo + muelle en A0, sonido por el jack (pin 9), LED RGB reactivo (pines 5, 6, 4 con una sola 220 en la común). Alimentación USB.
import os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'manuals', 'caja-muelle.html')

P = 16
LET = {'A': 60, 'B': 76, 'C': 92, 'D': 108, 'E': 124, 'F': 172, 'G': 188, 'H': 204, 'I': 220, 'J': 236}
def Y(r): return 80 + (r - 1) * P
def H(l, r): return LET[l], Y(r)

LEFT  = ['TX0', 'RX1', 'GND', 'GND', '2', '3', '4', '5', '6', '7', '8', '9']          # columna D
RIGHT = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', '15', '14', '16', '10']  # columna H
BANDS = {'brown': '#7A4A22', 'black': '#111111', 'orange': '#F08A00', 'yellow': '#F2C500',
         'red': '#D62828', 'green': '#2E9E44', 'gold': '#C9A227'}
B10K, B2M, B220 = ['brown', 'black', 'orange'], ['red', 'red', 'green'], ['red', 'red', 'brown']
VB = '-180 20 520 460'

# ---------------- piezas de dibujo ----------------
def board_base():
    s = ['<rect x="48" y="68" width="216" height="284" rx="6" class="bb"/>',
         '<rect x="134" y="68" width="28" height="284" class="gapc"/>']
    for l, x in LET.items():
        s.append(f'<text x="{x}" y="62" class="col">{l}</text>')
    for r in range(1, 18):
        y = Y(r)
        s.append(f'<text x="44" y="{y + 3}" class="rowl" text-anchor="end">{r}</text>')
        s.append(f'<text x="252" y="{y + 3}" class="rowl" text-anchor="start">{r}</text>')
        for x in LET.values():
            s.append(f'<circle cx="{x}" cy="{y}" r="2.3" class="hole"/>')
    return ''.join(s)

def promicro(ghost=False):
    if ghost:
        return ('<rect x="96" y="70" width="120" height="196" rx="4" class="ghost"/>'
                '<text x="156" y="170" class="lbl" text-anchor="middle">aquí irá</text>'
                '<text x="156" y="182" class="lbl" text-anchor="middle">la Pro Micro</text>')
    g = ['<rect x="147" y="50" width="18" height="22" rx="2" class="usb"/>',
         '<rect x="96" y="70" width="120" height="196" rx="4" class="pcb"/>',
         '<rect x="140" y="150" width="32" height="32" rx="2" class="mcu"/><text x="156" y="170" class="pn" text-anchor="middle">32U4</text>',
         '<text x="156" y="128" class="pn" text-anchor="middle">PRO MICRO</text>',
         '<text x="156" y="44" class="lbl" text-anchor="middle">USB</text>']
    for i in range(12):
        y = Y(i + 1)
        g.append(f'<rect x="104" y="{y - 4}" width="8" height="8" class="pin"/>')
        g.append(f'<rect x="200" y="{y - 4}" width="8" height="8" class="pin"/>')
        g.append(f'<text x="116" y="{y + 3}" class="pn">{LEFT[i]}</text>')
        g.append(f'<text x="196" y="{y + 3}" class="pn" text-anchor="end">{RIGHT[i]}</text>')
    return ''.join(g)

def resistor(a, b, bands, L=None):
    (x1, y1), (x2, y2) = a, b
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    horiz = abs(x2 - x1) > abs(y2 - y1)
    dist = abs(x2 - x1) if horiz else abs(y2 - y1)
    L = L or min(dist - 8, 28)
    s = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="leg"/>']
    if horiz:
        bx = cx - L / 2
        s.append(f'<rect x="{bx}" y="{cy - 5}" width="{L}" height="10" rx="4" class="rbody"/>')
        for i, bnd in enumerate(bands):
            s.append(f'<rect x="{bx + 4 + i * 5}" y="{cy - 5}" width="3" height="10" fill="{BANDS[bnd]}"/>')
    else:
        by = cy - L / 2
        s.append(f'<rect x="{cx - 5}" y="{by}" width="10" height="{L}" rx="4" class="rbody"/>')
        for i, bnd in enumerate(bands):
            s.append(f'<rect x="{cx - 5}" y="{by + 3 + i * 4}" width="10" height="2.6" fill="{BANDS[bnd]}"/>')
    for (x, y) in (a, b):
        s.append(f'<circle cx="{x}" cy="{y}" r="2.6" class="legend"/>')
    return ''.join(s)

def standing(top, bot, bands):
    """resistencia de pie: el cuerpo sobre el agujero de arriba, la pata doblada baja al de abajo"""
    (x1, y1), (x2, y2) = top, bot
    s = [f'<path d="M{x1},{y1} C{x1 + 16},{y1 - 4} {x2 + 16},{y2 + 2} {x2},{y2}" class="leg" fill="none"/>',
         f'<circle cx="{x1}" cy="{y1}" r="7" class="rbody"/>']
    for i, bnd in enumerate(bands):
        s.append(f'<circle cx="{x1}" cy="{y1}" r="{6 - i * 1.8}" fill="none" stroke="{BANDS[bnd]}" stroke-width="1.4"/>')
    s.append(f'<circle cx="{x2}" cy="{y2}" r="2.6" class="legend"/>')
    return ''.join(s)

def wire(d, color, ends, hidden=False):
    halo = 'wh-k' if color == 'black' else 'wh'
    dash = ' hid' if hidden else ''
    s = [f'<path d="{d}" class="{halo}{dash}"/>', f'<path d="{d}" class="wc w-{color}{dash}"/>']
    for (x, y) in ends:
        s.append(f'<circle cx="{x}" cy="{y}" r="3.2" class="wend w-{color}"/>')
    return ''.join(s)

def ring(l, r, name, dx=0, dy=-12, anchor='middle'):
    x, y = H(l, r)
    return (f'<circle cx="{x}" cy="{y}" r="7" class="ring"/>'
            f'<text x="{x + dx}" y="{y + dy}" class="hn" text-anchor="{anchor}">{name}</text>')

# ---- cada pieza de la placa ----
def straight(a, b, color, hidden):
    return wire(f'M{a[0]},{a[1]} L{b[0]},{b[1]}', color, [a, b], hidden)
def p_gnd_under(hidden): return straight(H('F', 2), H('F', 16), 'black', hidden)
def p_a0_under(hidden): return straight(H('G', 8), H('G', 14), 'green', hidden)
def p_b_under(hidden): return straight(H('E', 7), H('E', 17), 'purple', hidden)
def p_r2m(): return resistor(H('I', 14), H('I', 16), B2M)
def p_r220(): return resistor(H('D', 15), H('G', 17), B220, L=22)
def p_vcc(): return straight(H('J', 4), H('J', 17), 'red', False)
PZ = (300, 410)
def p_piezo():
    cx, cy = PZ
    (rx, ry), (bx, by) = H('H', 14), H('H', 16)
    return (f'<circle cx="{cx}" cy="{cy}" r="26" class="brass"/><circle cx="{cx}" cy="{cy}" r="17" class="ceramic"/>'
            f'<text x="{cx}" y="{cy + 42}" class="lbl" text-anchor="middle">piezo (va en la tapa)</text>'
            + wire(f'M{cx + 4},{cy - 10} C{cx + 30},{cy - 60} {rx + 50},{ry - 10} {rx},{ry}', 'red', [(rx, ry)])
            + wire(f'M{cx - 18},{cy - 14} C{cx - 40},{cy - 50} {bx + 30},{by + 10} {bx},{by}', 'black', [(bx, by)]))
def p_led():
    x = LET['C']; y0, y1 = Y(14), Y(17)
    s = [f'<rect x="{x - 9}" y="{y0 - 10}" width="18" height="{y1 - y0 + 20}" rx="9" class="ledrgb"/>']
    for r, t in zip(range(14, 18), ['R', '−', 'G', 'B']):
        s.append(f'<circle cx="{x}" cy="{Y(r)}" r="2.6" class="legend"/>')
        s.append(f'<text x="{x - 13}" y="{Y(r) + 3}" class="ledl" text-anchor="end">{t}</text>')
    s.append(f'<text x="{x}" y="{y1 + 26}" class="lbl" text-anchor="middle">LED RGB</text>')
    return ''.join(s)
def p_wr(): return straight(H('A', 8), H('A', 14), 'red', False)
def p_wg(): return straight(H('B', 9), H('B', 16), 'green', False)
LUG_S, LUG_T = (-92, 160), (-92, 236)
def jack_body():
    return ('<rect x="-172" y="130" width="70" height="140" rx="6" class="jackb"/>'
            '<circle cx="-137" cy="200" r="16" fill="var(--paper)" stroke="var(--ink)"/>'
            '<text x="-137" y="122" class="lbl" text-anchor="middle">jack 3,5 mm</text>'
            f'<rect x="{LUG_S[0] - 10}" y="{LUG_S[1] - 4}" width="12" height="8" class="lug"/><text x="-120" y="{LUG_S[1] + 3}" class="lbl" text-anchor="end">S</text>'
            f'<rect x="{LUG_T[0] - 10}" y="{LUG_T[1] - 4}" width="12" height="8" class="lug"/><text x="-120" y="{LUG_T[1] + 3}" class="lbl" text-anchor="end">T</text>'
            '<rect x="-88" y="226" width="36" height="20" rx="3" class="sbox"/><text x="-70" y="239" class="lbl" text-anchor="middle">10 kΩ</text>'
            '<text x="-172" y="290" class="lbl">la 10 kΩ va soldada</text><text x="-172" y="302" class="lbl">en el cable (termorretráctil)</text>')
def p_jack_gnd():
    (x, y) = H('A', 3); sx, sy = LUG_S
    return wire(f'M{sx},{sy} C{sx + 60},{sy - 10} {x - 50},{y} {x},{y}', 'black', [(sx, sy), (x, y)])
def p_jack_sig():
    (x, y) = H('C', 12)
    return wire(f'M-52,236 C0,236 {x - 70},{y + 30} {x},{y}', 'green', [(-52, 236), (x, y)])

UNDER = {'gnd_u': p_gnd_under, 'a0_u': p_a0_under, 'b_u': p_b_under}
ORDER = ['gnd_u', 'a0_u', 'b_u', 'pm', 'r2m', 'piezo', 'led', 'vcc', 'r220', 'wr', 'wg', 'jack_g', 'jack_s']
FN = {'r2m': p_r2m, 'piezo': p_piezo, 'led': p_led, 'r220': p_r220, 'vcc': p_vcc, 'wr': p_wr, 'wg': p_wg,
      'jack_g': p_jack_gnd, 'jack_s': p_jack_sig}

def board_svg(aria, upto, rings='', extra=''):
    """upto: clave de la pieza nueva; las anteriores en ORDER salen atenuadas. upto=None: todo montado."""
    idx = ORDER.index(upto) if upto else len(ORDER)
    have = set(ORDER[:idx + 1]) if upto else set(ORDER)
    pm_on = 'pm' in have
    left = -180 if 'jack_g' in have else -30
    right = 410 if 'class="mm"' in extra else (380 if 'piezo' in have else 345)
    bottom = 465 if 'piezo' in have else 385
    s = [f'<svg viewBox="{left} 20 {right - left} {bottom - 20}" role="img" aria-label="{aria}">', board_base()]
    def is_new(k): return upto is None or k == upto or (upto == 'jack_s' and k == 'jack_g')
    def put(k, content):
        if k not in have: return
        s.append(content if is_new(k) else f'<g class="old">{content}</g>')
    if not pm_on:
        s.append(promicro(ghost=True))
    else:
        put('pm', promicro())
    for k, f in UNDER.items(): put(k, f(pm_on))
    put('jack_g', jack_body())
    for k in ORDER:
        if k in FN: put(k, FN[k]())
    s.append(rings); s.append(extra); s.append('</svg>')
    return ''.join(s)

def fig(svg, cap):
    return f'<figure class="dia"><div class="scroll">{svg}</div><figcaption>{cap}</figcaption></figure>'
def chips(items):
    return '<div class="chips">' + ''.join(f'<span class="chip {c}"><i></i>{t}</span>' for c, t in items) + '</div>'
def step(n, title, text, chip_items, body=''):
    return (f'<li class="step" id="p{n}"><div class="num" aria-hidden="true">{n}</div>'
            f'<div class="sbody"><h3>{title}</h3><p>{text}</p>{chips(chip_items) if chip_items else ""}{body}</div></li>')
def warn(t): return f'<div class="warn">{t}</div>'

def probe(tip, color, label, dx, dy, anchor='middle'):
    x, y = tip
    return (f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y + dy}" class="prb-{color}"/>'
            f'<circle cx="{x}" cy="{y}" r="3" class="prb-tip-{color}"/>'
            f'<text x="{x + dx}" y="{y + dy + 14}" class="hn" text-anchor="{anchor}" style="fill:var(--ink)">{label}</text>')
def meter(x, y, value, scale):
    return (f'<rect x="{x}" y="{y}" width="130" height="56" rx="6" class="mm"/>'
            f'<text x="{x + 10}" y="{y + 37}" class="mmv">{value}</text>'
            f'<text x="{x + 122}" y="{y + 48}" class="mmu" text-anchor="end">{scale}</text>')

# ---------------- figuras sueltas ----------------
def overview():
    return '''<svg viewBox="0 0 620 300" role="img" aria-label="Esquema general: el muelle golpea el piezo, que entra directo por A0 a la Pro Micro; el pin 9 saca el sonido por el jack a través de 10 kΩ; los pines 5, 6 y 4 encienden el LED RGB, con una resistencia de 220 Ω de la pata común a 5 V; el USB da la corriente">
<rect x="230" y="70" width="160" height="150" rx="8" class="spm"/>
<text x="310" y="100" class="spt" text-anchor="middle">PRO MICRO</text>
<text x="310" y="140" class="spt" text-anchor="middle">A0 ← piezo</text>
<text x="310" y="160" class="spt" text-anchor="middle">9 → sonido</text>
<text x="310" y="180" class="spt" text-anchor="middle">5 · 6 · 4 → LED</text>
<rect x="290" y="20" width="40" height="22" rx="3" class="usb"/><line x1="310" y1="42" x2="310" y2="70" class="sline"/>
<text x="340" y="36" class="stxt">USB: corriente (y MIDI al Mac)</text>
<path d="M30,120 q10,-14 20,0 t20,0 t20,0 t20,0" class="sline"/><text x="30" y="100" class="stxt">muelle</text>
<circle cx="80" cy="160" r="22" class="brass"/><circle cx="80" cy="160" r="14" class="ceramic"/><text x="80" y="204" class="stxt" text-anchor="middle">piezo</text>
<line x1="80" y1="128" x2="80" y2="136" class="sline"/>
<line x1="104" y1="160" x2="130" y2="160" class="sline"/>
<line x1="130" y1="160" x2="180" y2="160" class="sline"/>
<line x1="180" y1="160" x2="230" y2="160" class="sline"/><circle cx="205" cy="160" r="3.5" class="sdot"/>
<line x1="205" y1="160" x2="205" y2="196" class="sline"/><rect x="196" y="196" width="18" height="40" rx="4" class="sbox"/>
<text x="188" y="222" class="stxt" text-anchor="end">2,2 MΩ</text>
<line x1="205" y1="236" x2="205" y2="256" class="sline"/><path d="M193,256 H217 M197,262 H213 M201,268 H209" class="sline"/>
<line x1="390" y1="160" x2="470" y2="160" class="sline"/><rect x="470" y="148" width="50" height="24" rx="4" class="sbox"/><text x="495" y="164" class="stxt" text-anchor="middle">10 kΩ</text>
<line x1="520" y1="160" x2="545" y2="160" class="sline"/><rect x="545" y="140" width="40" height="40" rx="5" class="jackb"/><text x="565" y="200" class="stxt" text-anchor="middle">jack</text>
<line x1="390" y1="196" x2="550" y2="200" class="sline"/><line x1="390" y1="206" x2="549" y2="206" class="sline"/><line x1="390" y1="216" x2="550" y2="212" class="sline"/>
<text x="470" y="190" class="stxt" text-anchor="middle">5 · 6 · 4</text>
<circle cx="565" cy="206" r="16" class="ledrgb"/><text x="590" y="200" class="stxt">LED</text>
<line x1="565" y1="222" x2="565" y2="234" class="sline"/><rect x="556" y="234" width="18" height="30" rx="4" class="sbox"/><text x="548" y="254" class="stxt" text-anchor="end">220 Ω</text>
<line x1="565" y1="264" x2="565" y2="274" class="sline"/><text x="565" y="290" class="stxt" text-anchor="middle">5 V</text>
</svg>'''

def fig_res():
    def res(x, bands, name, colors):
        s = f'<line x1="{x}" y1="40" x2="{x + 130}" y2="40" class="leg"/><rect x="{x + 35}" y="31" width="60" height="18" rx="7" class="rbody"/>'
        for i, b in enumerate(bands):
            s += f'<rect x="{x + 45 + i * 11}" y="31" width="6" height="18" fill="{BANDS[b]}"/>'
        s += f'<rect x="{x + 81}" y="31" width="5" height="18" fill="{BANDS["gold"]}"/>'
        s += f'<text x="{x + 65}" y="74" class="stxt" text-anchor="middle">{name}</text><text x="{x + 65}" y="90" class="lbl" text-anchor="middle">{colors}</text>'
        return s
    return ('<svg viewBox="0 0 620 110" role="img" aria-label="Las tres resistencias: 10 kΩ marrón negro naranja, 2,2 MΩ rojo rojo verde, 220 Ω rojo rojo marrón">'
            + res(10, B10K, '10 kΩ', 'marrón · negro · naranja') + res(220, B2M, '2,2 MΩ', 'rojo · rojo · verde')
            + res(430, B220, '220 Ω', 'rojo · rojo · marrón') + '</svg>')

def fig_led_id():
    legs = [(240, 'R', 90), (260, '−  (la más larga)', 120), (280, 'G', 90), (300, 'B', 90)]
    s = ['<svg viewBox="0 -30 620 260" role="img" aria-label="LED RGB de 4 patas: la segunda pata es la más larga y es la común. Con el multímetro en modo diodo, punta negra en la larga y roja en la pata R: si se enciende en rojo es de cátodo común">',
         '<path d="M222,30 a48,48 0 0 1 96,0 v40 h-96 z" class="ledrgb"/><rect x="216" y="70" width="108" height="10" rx="2" class="ledrgb"/>']
    for x, t, L in legs:
        s.append(f'<line x1="{x}" y1="80" x2="{x}" y2="{80 + L}" class="leg"/>')
    s.append('<text x="240" y="186" class="stxt" text-anchor="middle">R</text><text x="260" y="216" class="stxt" text-anchor="middle">−</text>'
             '<text x="280" y="186" class="stxt" text-anchor="middle">G</text><text x="300" y="186" class="stxt" text-anchor="middle">B</text>')
    s.append('<text x="200" y="212" class="lbl" text-anchor="end">pata larga = común</text>')
    s.append('<line x1="260" y1="200" x2="150" y2="150" class="prb-red"/><circle cx="260" cy="200" r="3" class="prb-tip-red"/>')
    s.append('<line x1="240" y1="170" x2="150" y2="110" class="prb-black"/><circle cx="240" cy="170" r="3" class="prb-tip-black"/>')
    s.append(meter(10, 100, '→|', 'modo diodo'))
    s.append('<text x="360" y="60" class="stxt">Roja en la larga, negra en R:</text>'
             '<text x="360" y="82" class="stxt">· se enciende roja → ánodo común ✔</text>'
             '<text x="360" y="104" class="stxt">  (es el tuyo: comprobado)</text>'
             '<text x="360" y="126" class="stxt">· prueba también G y B</text>'
             '<text x="360" y="148" class="lbl">(con la negra en cada una)</text>')
    s.append('</svg>')
    return ''.join(s)

def fig_piezo_prep():
    def stage(x, label, kind):
        s = f'<g transform="translate({x},20)"><rect x="0" y="22" width="70" height="14" rx="6" class="ins"/>'
        if kind == 1: s += '<rect x="70" y="25" width="26" height="8" class="strand"/>'
        elif kind == 2: s += '<rect x="70" y="25" width="26" height="8" class="tinned"/><rect x="96" y="22" width="60" height="14" rx="6" class="ins"/>'
        else: s += '<rect x="58" y="18" width="50" height="22" rx="4" class="shrink"/><rect x="108" y="22" width="48" height="14" rx="6" class="ins"/><rect x="156" y="25" width="18" height="8" class="tinned"/>'
        return s + f'<text x="80" y="66" class="stxt" text-anchor="middle">{label}</text></g>'
    return ('<svg viewBox="0 0 620 100" role="img" aria-label="Preparar los cables del piezo: pelar y estañar, soldar a un trozo de cable rígido, tapar con termorretráctil">'
            + stage(0, '1 pela 5 mm y estaña', 1) + stage(200, '2 suelda a cable rígido', 2) + stage(420, '3 termorretráctil + calor', 3) + '</svg>')

def fig_jack_wiring():
    return '''<svg viewBox="0 0 620 200" role="img" aria-label="Cableado del jack: las patillas de punta y anillo se unen; de ahí una resistencia de 10 kΩ soldada en el cable hasta la fila del pin 9; el manguito va a GND">
<rect x="20" y="40" width="90" height="120" rx="8" class="jackb"/><text x="65" y="30" class="stxt" text-anchor="middle">jack</text>
<rect x="104" y="62" width="14" height="10" class="lug"/><text x="96" y="71" class="lbl" text-anchor="end" style="fill:#EAF0FF">T</text>
<rect x="104" y="92" width="14" height="10" class="lug"/><text x="96" y="101" class="lbl" text-anchor="end" style="fill:#EAF0FF">R</text><text x="128" y="132" class="lbl">negro</text>
<rect x="104" y="132" width="14" height="10" class="lug"/><text x="96" y="141" class="lbl" text-anchor="end" style="fill:#EAF0FF">S</text>
<path d="M118,67 H160 V97 H118" class="sline"/><circle cx="160" cy="82" r="4" class="sdot"/>
<line x1="160" y1="82" x2="220" y2="82" class="sline"/>
<rect x="220" y="70" width="80" height="24" rx="8" class="rbody"/><rect x="236" y="70" width="6" height="24" fill="#7A4A22"/><rect x="248" y="70" width="6" height="24" fill="#111"/><rect x="260" y="70" width="6" height="24" fill="#F08A00"/>
<rect x="210" y="64" width="100" height="36" rx="6" class="shrinkbox"/>
<text x="260" y="122" class="stxt" text-anchor="middle">10 kΩ + termorretráctil</text>
<line x1="300" y1="82" x2="420" y2="82" class="sline"/><text x="430" y="86" class="stxt">pata → C12 (pin 9)</text>
<line x1="118" y1="137" x2="420" y2="137" class="sline"/><text x="430" y="141" class="stxt">→ A3 (GND)</text>
<text x="170" y="60" class="lbl">morado + verde (T y R) unidos</text>
<text x="20" y="188" class="lbl">la resistencia protege el pin: sin ella unos auriculares le pedirían demasiada corriente</text></svg>'''

def fig_solder_steps():
    """6 viñetas con los colores reales del jack: morado y verde = punta y anillo, negro = masa"""
    PU, GR, BK = '#8E4FD8', 'var(--w-green)', 'var(--w-black)'
    def ins(x1, x2, y, col, h=10):
        return f'<rect x="{x1}" y="{y - h/2}" width="{x2 - x1}" height="{h}" rx="4" fill="{col}" stroke="var(--ink)" stroke-width=".8"/>'
    def bare(x1, x2, y): return f'<rect x="{x1}" y="{y - 2.5}" width="{x2 - x1}" height="5" rx="2" class="tinned"/>'
    def blob(x, y): return f'<ellipse cx="{x}" cy="{y}" rx="9" ry="7" class="solder"/>'
    def res(x1, x2, y):
        c = (x1 + x2) / 2
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="leg"/>'
                f'<rect x="{c - 22}" y="{y - 8}" width="44" height="16" rx="6" class="rbody"/>'
                f'<rect x="{c - 14}" y="{y - 8}" width="5" height="16" fill="#7A4A22"/><rect x="{c - 5}" y="{y - 8}" width="5" height="16" fill="#111"/>'
                f'<rect x="{c + 4}" y="{y - 8}" width="5" height="16" fill="#F08A00"/>')
    def shrink(x1, x2, y, h=20, done=False):
        op = '.85' if done else '.30'
        dash = '' if done else ' stroke-dasharray="4 3"'
        return f'<rect x="{x1}" y="{y - h/2}" width="{x2 - x1}" height="{h}" rx="5" fill="#2A2A2A" fill-opacity="{op}" stroke="var(--ink)"{dash}/>'
    def jack(y):
        return f'<rect x="8" y="{y - 30}" width="34" height="60" rx="5" class="jackb"/><text x="25" y="{y + 44}" class="lbl" text-anchor="middle">jack</text>'
    def twist(x, y1, y2, xm, ym):
        return f'<path d="M{x},{y1} Q{xm - 12},{y1} {xm},{ym} M{x},{y2} Q{xm - 12},{y2} {xm},{ym}" class="leg" fill="none" style="stroke-width:3"/>'
    def three(xend, with_black=True):   # los tres cables saliendo del jack
        g = ins(42, xend, 64, PU) + ins(42, xend, 82, GR)
        if with_black: g += ins(42, 120, 102, BK)
        return g
    panels = []
    # 1 comprobar
    g = jack(80) + three(150) + bare(150, 162, 64) + bare(150, 162, 82) + bare(120, 132, 102)
    g += ('<rect x="180" y="40" width="110" height="80" rx="6" class="mm"/><text x="235" y="72" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#1B2418">♪ pita</text>'
          '<text x="235" y="92" text-anchor="middle" class="mmu">negro ↔ manguito</text><text x="235" y="106" text-anchor="middle" class="mmu">del conector</text>'
          '<line x1="132" y1="102" x2="180" y2="102" class="prb-black"/>')
    panels.append(('Comprueba: el negro es la masa', g))
    # 2 termorretráctil
    g = jack(80) + three(150) + bare(150, 162, 64) + bare(150, 162, 82) + shrink(70, 125, 73, 38)
    g += '<text x="170" y="67" class="lbl">morado</text><text x="170" y="86" class="lbl">verde</text><text x="60" y="122" class="lbl">termorretráctil 4 cm</text><text x="60" y="134" class="lbl">por los dos, ANTES</text>'
    panels.append(('Mete el termorretráctil grande', g))
    # 3 retorcer
    g = jack(80) + three(130) + twist(130, 64, 82, 160, 73) + bare(158, 178, 73) + shrink(70, 125, 73, 38)
    g += '<text x="186" y="70" class="lbl">morado + verde</text><text x="186" y="82" class="lbl">retorcidos y estañados</text>'
    panels.append(('Retuerce morado y verde juntos', g))
    # 4 resistencia
    g = jack(80) + three(130) + twist(130, 64, 82, 160, 73) + res(160, 290, 73) + blob(166, 73) + shrink(70, 125, 73, 38)
    g += '<text x="166" y="98" class="lbl" text-anchor="middle">soldadura</text><text x="240" y="52" class="lbl" text-anchor="middle">10 kΩ</text><text x="290" y="98" class="lbl" text-anchor="end">esta pata, 1 cm</text>'
    panels.append(('Suelda la 10 kΩ al empalme', g))
    # 5 calentar
    g = jack(80) + ins(42, 100, 64, PU) + ins(42, 100, 82, GR) + ins(42, 120, 102, BK) + shrink(96, 250, 73, 26, True) + '<line x1="250" y1="73" x2="285" y2="73" class="leg" style="stroke-width:2.4"/>'
    g += '<text x="173" y="77" class="lbl" text-anchor="middle" style="fill:#EAF0FF">10 kΩ tapada</text><text x="285" y="62" class="lbl" text-anchor="end">pata al aire</text><text x="268" y="98" class="lbl" text-anchor="middle">→ C12</text>'
    panels.append(('Baja el termorretráctil y calienta', g))
    # 6 negro
    g = jack(80) + ins(42, 100, 64, PU) + ins(42, 100, 82, GR) + shrink(96, 150, 73, 26, True) + ins(42, 140, 106, BK) + blob(146, 106) + ins(150, 270, 106, BK) + shrink(132, 164, 106, 18, True) + bare(270, 282, 106)
    g += '<text x="210" y="96" class="lbl" text-anchor="middle">cable rígido negro</text><text x="282" y="126" class="lbl" text-anchor="end">→ A3</text>'
    panels.append(('Negro: empalma un cable rígido', g))
    out = ['<svg viewBox="0 0 620 510" role="img" aria-label="Seis viñetas con los colores del jack: comprobar que el negro es masa, unir morado y verde, soldar la 10 kΩ, cubrir con termorretráctil y empalmar el negro a un cable rígido">']
    for k, (title, body) in enumerate(panels):
        x, y = (k % 2) * 312, (k // 2) * 170
        out.append(f'<g transform="translate({x},{y})"><rect x="2" y="2" width="304" height="160" rx="6" fill="var(--soft)" stroke="var(--rule)"/>'
                   f'<circle cx="20" cy="20" r="11" fill="var(--ink)"/><text x="20" y="24" text-anchor="middle" style="font-size:11px;font-weight:700;fill:var(--paper)">{k + 1}</text>'
                   f'<text x="38" y="24" class="stxt" style="font-weight:700">{title}</text><g transform="translate(0,22)">{body}</g></g>')
    out.append('</svg>')
    return ''.join(out)

# ---------------- montaje en la lata ----------------
def panels(items, aria, cols=2, ph=160):
    """viñetas numeradas de 304 x ph"""
    rows = (len(items) + cols - 1) // cols
    out = [f'<svg viewBox="0 0 {cols * 312 - 4} {rows * (ph + 10) - 4}" role="img" aria-label="{aria}">']
    for k, (title, body) in enumerate(items):
        x, y = (k % cols) * 312, (k // cols) * (ph + 10)
        out.append(f'<g transform="translate({x},{y})"><rect x="2" y="2" width="304" height="{ph}" rx="6" fill="var(--soft)" stroke="var(--rule)"/>'
                   f'<circle cx="20" cy="20" r="11" fill="var(--ink)"/><text x="20" y="24" text-anchor="middle" style="font-size:11px;font-weight:700;fill:var(--paper)">{k + 1}</text>'
                   f'<text x="38" y="24" class="stxt" style="font-weight:700">{title}</text><g transform="translate(0,22)">{body}</g></g>')
    out.append('</svg>')
    return ''.join(out)

def dim(x1, y1, x2, y2, label, lx, ly, anchor='middle'):
    """cota con topes en los extremos"""
    if y1 == y2:
        t = f'<line x1="{x1}" y1="{y1 - 5}" x2="{x1}" y2="{y1 + 5}" class="sline" style="stroke-width:1.4"/><line x1="{x2}" y1="{y2 - 5}" x2="{x2}" y2="{y2 + 5}" class="sline" style="stroke-width:1.4"/>'
    else:
        t = f'<line x1="{x1 - 5}" y1="{y1}" x2="{x1 + 5}" y2="{y1}" class="sline" style="stroke-width:1.4"/><line x1="{x2 - 5}" y1="{y2}" x2="{x2 + 5}" y2="{y2}" class="sline" style="stroke-width:1.4"/>'
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke:var(--accent);stroke-width:1.6"/>{t}'
            f'<text x="{lx}" y="{ly}" class="hn" text-anchor="{anchor}">{label}</text>')

def fig_plan():
    return '''<svg viewBox="0 0 620 400" role="img" aria-label="Vista desde arriba de la lata abierta: la protoboard abajo con el USB contra la pared de abajo, el jack a su derecha en la misma pared, el LED cerca de la parte de arriba de la protoboard y una zona libre arriba donde caerá el piezo de la tapa">
<text x="20" y="20" class="stxt" style="font-weight:700">LA LATA DESDE ARRIBA (fondo)</text>
<rect x="40" y="34" width="210" height="322" rx="22" class="tin"/>
<rect x="48" y="42" width="194" height="306" rx="16" fill="var(--paper)" fill-opacity=".35" stroke="var(--rule)"/>
<line x1="256" y1="80" x2="256" y2="310" style="stroke:var(--muted);stroke-width:5;stroke-dasharray:14 6"/>
<text x="268" y="380" class="lbl">la línea gruesa de la derecha = bisagra</text>
<circle cx="145" cy="110" r="47" class="ghost"/><text x="145" y="106" class="lbl" text-anchor="middle" style="fill:#1B1F24">zona libre:</text><text x="145" y="118" class="lbl" text-anchor="middle" style="fill:#1B1F24">aquí cae el piezo</text>
<rect x="62" y="186" width="122" height="160" rx="3" class="bbside"/>
<rect x="91" y="226" width="63" height="114" rx="3" class="spm"/>
<rect x="110" y="336" width="26" height="12" class="usb"/>
<circle cx="150" cy="204" r="10" class="ledrgb"/>
<rect x="198" y="300" width="28" height="48" rx="4" class="jackb"/>
<rect x="105" y="350" width="36" height="9" fill="var(--accent)"/><rect x="200" y="350" width="24" height="9" fill="var(--accent)"/>
<text x="145" y="392" class="hn" text-anchor="middle" style="font-size:11px">PARED DEL USB Y EL JACK</text>
<line x1="192" y1="110" x2="290" y2="110" class="sline" style="stroke-width:1"/><text x="296" y="106" class="stxt">④ piezo pegado en la tapa, sobre la zona libre</text><text x="296" y="121" class="lbl">el muelle va por fuera, justo encima</text>
<line x1="160" y1="204" x2="290" y2="204" class="sline" style="stroke-width:1"/><text x="296" y="200" class="stxt">③ LED: agujero Ø 5 en la tapa (opcional)</text><text x="296" y="215" class="lbl">sin agujero el brillo queda dentro: también vale</text>
<line x1="184" y1="262" x2="290" y2="262" class="sline" style="stroke-width:1"/><text x="296" y="258" class="stxt">① protoboard pegada al fondo</text><text x="296" y="273" class="lbl">USB a 1–2 mm de la pared</text>
<line x1="226" y1="322" x2="290" y2="322" class="sline" style="stroke-width:1"/><text x="296" y="318" class="stxt">② jack en la misma pared, al lado</text><text x="296" y="333" class="lbl">que su cuerpo no toque la protoboard</text>
<text x="296" y="356" class="lbl">naranja = agujeros en la pared</text>
</svg>'''

def fig_insulate():
    p1 = ('<rect x="30" y="18" width="244" height="112" rx="14" class="tin"/>'
          + ''.join(f'<rect x="38" y="{24 + i * 20}" width="228" height="24" fill="#3A3F45" fill-opacity=".85" stroke="var(--ink)" stroke-width=".6"/>' for i in range(5))
          + '<text x="152" y="138" class="lbl" text-anchor="middle">tiras de cinta aislante (o Kapton) solapadas 3-4 mm</text>')
    p2 = ('<path d="M30,120 H274" class="sline" style="stroke-width:3"/><path d="M40,30 V120" class="sline" style="stroke-width:3"/>'
          '<path d="M44,70 V115 H270" style="stroke:#3A3F45;stroke-width:5;fill:none"/>'
          '<rect x="90" y="84" width="130" height="28" rx="3" class="bbside"/><text x="155" y="102" class="lbl" text-anchor="middle" style="fill:#1B1F24">protoboard</text>'
          '<rect x="90" y="112" width="130" height="3" fill="#E8E2D0"/>'
          + dim(56, 70, 56, 115, '1 cm', 60, 96, 'start') +
          '<text x="44" y="138" class="lbl">pared</text><text x="270" y="138" class="lbl" text-anchor="end">fondo de la lata</text>'
          '<text x="230" y="82" class="lbl">su adhesivo</text><text x="230" y="94" class="lbl">va ENCIMA</text><text x="230" y="106" class="lbl">de la cinta</text>')
    return panels([('Cubre todo el fondo', p1), ('Sube 1 cm por las paredes', p2)],
                  'Dos viñetas: tiras de cinta aislante solapadas cubriendo el fondo; corte lateral con la cinta subiendo un centímetro por la pared y la protoboard pegada encima')

def fig_usb_measure():
    return '''<svg viewBox="0 0 620 380" role="img" aria-label="La pared del USB vista desde fuera, con cotas: distancia desde el borde izquierdo hasta el centro del USB, altura desde el fondo, tamaño del rectángulo, separación al jack y franja de arriba que no se taladra. Debajo, la variante de muesca abierta si el USB queda demasiado alto">
<text x="20" y="20" class="stxt" style="font-weight:700">PARED DEL USB VISTA DESDE FUERA (escala ≈ 7:1)</text>
<rect x="40" y="56" width="420" height="140" rx="6" class="tin"/>
<rect x="40" y="56" width="420" height="30" fill="var(--accent)" fill-opacity=".18"/><text x="250" y="75" class="lbl" text-anchor="middle" style="fill:var(--ink)">4-5 mm de arriba: aquí encaja la tapa. No taladres aquí</text>
<rect x="221" y="98" width="70" height="46" rx="3" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/><text x="256" y="125" class="lbl" text-anchor="middle">USB</text>
<circle cx="256" cy="121" r="2.5" class="sdot"/>
<circle cx="400" cy="138" r="21" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/><circle cx="400" cy="138" r="2.5" class="sdot"/><text x="400" y="110" class="lbl" text-anchor="middle" style="fill:#1B1F24">jack Ø 6</text>
''' + dim(40, 216, 256, 216, 'X = borde → centro USB', 148, 232) + dim(476, 121, 476, 196, 'Y', 482, 162, 'start') + \
    dim(221, 90, 291, 90, '', 0, 0) + '<text x="256" y="52" class="hn" text-anchor="middle">ancho = clavija + 2 mm</text>' + \
    dim(205, 98, 205, 144, 'alto', 200, 125, 'end') + dim(256, 250, 400, 250, '≥ 14 mm entre centros', 328, 266) + \
    dim(400, 196, 400, 158, '', 0, 0) + '<text x="408" y="186" class="hn">Y jack ≈ 8-10</text>' + \
    '''<text x="500" y="110" class="stxt">Y = del fondo de</text><text x="500" y="124" class="stxt">la lata al centro</text><text x="500" y="138" class="stxt">del conector, con</text><text x="500" y="152" class="stxt">la placa ya puesta</text><text x="500" y="166" class="stxt">sobre la cinta</text>
<text x="20" y="298" class="stxt" style="font-weight:700">¿EL RECTÁNGULO SE METE EN LA FRANJA?</text>
<text x="20" y="316" class="lbl">Entonces haz una muesca abierta por arriba</text><text x="20" y="330" class="lbl">y otra igual en el borde de la tapa:</text><text x="20" y="344" class="lbl">al cerrar, las dos forman el agujero.</text>
<path d="M310,290 H372 V330 H408 V290 H470 V350 H310 Z" class="tin"/><text x="390" y="366" class="lbl" text-anchor="middle">muesca en la pared</text>
<path d="M490,300 H536 V316 H572 V300 H612" class="sline"/><text x="552" y="334" class="lbl" text-anchor="middle">muesca en la tapa</text>
</svg>'''

def fig_marks():
    p1 = ('<path d="M30,128 H274" class="sline" style="stroke-width:3"/>'
          '<rect x="60" y="92" width="180" height="34" rx="3" class="bbside"/>'
          '<line x1="146" y1="92" x2="146" y2="70" class="leg"/><line x1="154" y1="92" x2="154" y2="70" class="leg"/>'
          '<path d="M138,72 V56 a12,12 0 0 1 24,0 V72 Z" class="ledrgb"/>'
          '<ellipse cx="150" cy="38" rx="14" ry="8" fill="#5BA4E6" stroke="var(--ink)"/><text x="174" y="38" class="lbl">bolita de Blu-Tack</text>'
          '<path d="M30,22 H274" class="sline" style="stroke-dasharray:6 4"/><text x="270" y="16" class="lbl" text-anchor="end">la tapa baja aquí</text>')
    p2 = ('<rect x="40" y="14" width="224" height="120" rx="14" class="tin"/>'
          '<ellipse cx="160" cy="62" rx="10" ry="5" fill="#5BA4E6" fill-opacity=".7"/>'
          '<circle cx="160" cy="62" r="13" fill="none" style="stroke:var(--accent);stroke-width:2;stroke-dasharray:3 3"/>'
          '<line x1="148" y1="62" x2="172" y2="62" style="stroke:var(--accent)"/><line x1="160" y1="50" x2="160" y2="74" style="stroke:var(--accent)"/>'
          '<text x="160" y="96" class="lbl" text-anchor="middle">la marca en la tapa = centro</text><text x="160" y="108" class="lbl" text-anchor="middle">del agujero de Ø 5 mm</text>'
          '<text x="52" y="128" class="lbl">tapa por dentro</text>')
    return panels([('Blu-Tack encima del LED', p1), ('Cierra, abre y marca', p2)],
                  'Dos viñetas: una bolita de Blu-Tack sobre la cúpula del LED; al cerrar y abrir la tapa queda una marca que indica el centro del agujero')

def fig_drill():
    tape = '<rect x="40" y="40" width="224" height="60" fill="#E8D9A8" stroke="#A8945A"/>'
    p1 = ('<rect x="30" y="30" width="244" height="80" rx="6" class="tin"/>' + tape +
          '<path d="M90,60 l10,10 m0,-10 l-10,10 M220,62 l10,10 m0,-10 l-10,10" class="sline"/>'
          '<text x="152" y="128" class="lbl" text-anchor="middle">cinta de carrocero + cruces con rotulador</text>')
    p2 = ('<path d="M60,20 V130" class="sline" style="stroke-width:3"/><text x="56" y="140" class="lbl" text-anchor="middle">pared</text>'
          '<rect x="64" y="30" width="90" height="90" fill="#D8B27A" stroke="#7A5A2A"/><text x="109" y="80" class="lbl" text-anchor="middle" style="fill:#1B1F24">taco</text><text x="109" y="92" class="lbl" text-anchor="middle" style="fill:#1B1F24">de madera</text>'
          '<path d="M20,40 H40 V110 H20 M154,40 H200 V110 H154" style="stroke:var(--muted);stroke-width:5;fill:none"/><text x="220" y="64" class="lbl">sargento</text><text x="220" y="78" class="lbl">(o tornillo de</text><text x="220" y="92" class="lbl">banco)</text>'
          '<text x="14" y="30" class="lbl">fuera</text>')
    p3 = ('<rect x="30" y="80" width="244" height="12" class="tin"/>'
          '<path d="M80,78 l-8,-50 h16 Z" fill="#8A939A" stroke="var(--ink)"/><text x="96" y="40" class="lbl">punzón:</text><text x="96" y="52" class="lbl">toque suave</text>'
          '<path d="M220,78 v-44" style="stroke:#8A939A;stroke-width:4"/><text x="230" y="52" class="lbl">broca</text><text x="230" y="64" class="lbl">2 mm</text>'
          '<text x="152" y="118" class="lbl" text-anchor="middle">Dremel a velocidad media, sin apretar</text><text x="152" y="130" class="lbl" text-anchor="middle">deja que la broca trabaje</text>')
    p4 = ('<rect x="30" y="20" width="244" height="100" rx="6" class="tin"/>'
          '<circle cx="90" cy="70" r="6" fill="var(--paper)" stroke="var(--ink)"/><text x="90" y="104" class="lbl" text-anchor="middle">2 mm</text>'
          '<circle cx="152" cy="70" r="12" fill="var(--paper)" stroke="var(--ink)"/><text x="152" y="104" class="lbl" text-anchor="middle">4 mm</text>'
          '<circle cx="220" cy="70" r="18" fill="var(--paper)" stroke="var(--ink)"/><text x="220" y="104" class="lbl" text-anchor="middle">6 mm jack</text>'
          '<path d="M108,70 h20 M172,70 h20" class="sline" style="stroke-width:1.4"/>'
          '<text x="152" y="132" class="lbl" text-anchor="middle">LED en la tapa: hasta 5 mm</text>')
    return panels([('Marca sobre cinta de carrocero', p1), ('Apoya la pared por dentro', p2),
                   ('Punzón y broca fina', p3), ('Agranda poco a poco', p4)],
                  'Cuatro viñetas: marcar sobre cinta de carrocero, apoyar la pared con un taco de madera y un sargento, punzón y broca de 2 mm, y agrandar a 4 y 6 mm')

def fig_usb_cut():
    R = '<rect x="102" y="40" width="100" height="60" fill="none" style="stroke:var(--accent);stroke-width:1.6;stroke-dasharray:5 3"/>'
    base = '<rect x="30" y="20" width="244" height="100" rx="6" class="tin"/>'
    holes = ''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="var(--paper)" stroke="var(--ink)"/>' for x, y in ((110, 48), (194, 48), (110, 92), (194, 92)))
    p1 = base + R + '<text x="152" y="134" class="lbl" text-anchor="middle">rectángulo dibujado con las medidas X, Y</text>'
    p2 = base + R + holes + '<text x="152" y="134" class="lbl" text-anchor="middle">4 agujeros de 2-3 mm por DENTRO de las esquinas</text>'
    p3 = (base + R + holes + '<path d="M116,48 H188 M116,92 H188 M110,54 V86 M194,54 V86" style="stroke:var(--ink);stroke-width:5"/>'
           '<text x="152" y="134" class="lbl" text-anchor="middle">une con el disco de corte o con más agujeros</text>')
    p4 = (base + '<rect x="102" y="40" width="100" height="60" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"/>'
          '<path d="M200,30 l40,-14" style="stroke:#8A939A;stroke-width:6;stroke-linecap:round"/><text x="244" y="30" class="lbl">lima</text>'
          '<text x="152" y="74" class="lbl" text-anchor="middle">prueba la clavija</text><text x="152" y="134" class="lbl" text-anchor="middle">cuadra con lima de aguja, poco a poco</text>')
    return panels([('Dibuja el rectángulo', p1), ('Agujero en cada esquina', p2), ('Une los agujeros', p3), ('Lima hasta que entre la clavija', p4)],
                  'Cuatro viñetas para el agujero del USB: dibujar el rectángulo, taladrar un agujero en cada esquina, unirlos con el disco de corte y limar hasta que entre la clavija')

def fig_lid():
    return '''<svg viewBox="0 0 620 260" role="img" aria-label="Corte de la tapa: por fuera el muelle pegado con epoxi; por dentro, justo debajo, el piezo con el latón pegado al metal y una tira de cinta tapando la cara blanca y la soldadura del cable rojo">
<text x="20" y="20" class="stxt" style="font-weight:700">TAPA EN CORTE (cerrada, vista de lado)</text>
<rect x="40" y="120" width="440" height="10" class="tin"/><text x="40" y="112" class="lbl">metal de la tapa</text>
<path d="M260,118 v-12 q14,-8 0,-14 q-14,-6 0,-14 q14,-8 0,-14 q-14,-6 0,-14 q14,-8 0,-14" class="spring"/>
<rect x="244" y="110" width="32" height="8" rx="2" fill="#B9B08C" stroke="var(--ink)"/><text x="290" y="48" class="stxt">muelle POR FUERA</text><text x="290" y="64" class="lbl">base pegada con epoxi, justo encima del piezo</text>
<rect x="200" y="131" width="120" height="5" class="brass"/><rect x="226" y="136" width="68" height="5" class="ceramic"/>
<rect x="196" y="141" width="128" height="6" fill="#3A3F45"/>
<path d="M250,147 C250,180 200,190 160,200" class="wc w-red" style="stroke-width:2"/><path d="M205,136 C190,170 170,190 150,206" class="wc w-black" style="stroke-width:2"/>
<text x="330" y="138" class="lbl">① latón pegado al metal con pegamento instantáneo</text>
<text x="330" y="152" class="lbl">② cinta encima de la cara blanca y la soldadura roja</text>
<text x="40" y="222" class="lbl">cables con holgura hacia la bisagra:</text><text x="40" y="236" class="lbl">que la tapa abra del todo sin tirar de ellos</text>
<text x="330" y="196" class="stxt">El latón es GND, igual que la lata:</text><text x="330" y="212" class="stxt">pueden tocarse. La cara blanca NO.</text>
</svg>'''

def fig_mount():
    p1 = ('<path d="M150,14 V136" class="sline" style="stroke-width:3"/><text x="150" y="150" class="lbl" text-anchor="middle">pared</text>'
          '<rect x="70" y="56" width="76" height="40" rx="4" class="jackb"/><text x="108" y="50" class="lbl" text-anchor="middle">dentro</text>'
          '<rect x="146" y="68" width="40" height="16" fill="#B8C0C8" stroke="var(--ink)"/>'
          '<rect x="158" y="58" width="10" height="36" rx="2" fill="#8A939A" stroke="var(--ink)"/><text x="196" y="50" class="lbl">fuera:</text><text x="196" y="64" class="lbl">tuerca</text>')
    p2 = ('<path d="M270,14 V136" class="sline" style="stroke-width:3"/><path d="M30,130 H270" class="sline" style="stroke-width:3"/>'
          '<rect x="90" y="96" width="160" height="30" rx="3" class="bbside"/><rect x="120" y="86" width="110" height="10" class="pcbside"/>'
          '<rect x="226" y="86" width="22" height="10" class="usb"/>'
          '<path d="M180,72 l40,0 m-10,-8 l10,8 l-10,8" class="sline"/><text x="100" y="22" class="lbl">1º desliza hacia la pared</text><text x="100" y="34" class="lbl">hasta que el USB quede</text><text x="100" y="46" class="lbl">frente al agujero</text>'
          '<path d="M60,78 v14 m-6,-6 l6,6 l6,-6" class="sline"/><text x="34" y="74" class="lbl">2º aprieta</text>')
    p3 = ('<path d="M150,14 V96" class="sline" style="stroke-width:3"/>'
          '<rect x="60" y="62" width="90" height="16" class="pcbside"/><rect x="128" y="60" width="20" height="20" class="usb"/>'
          '<rect x="152" y="62" width="14" height="16" fill="#8A939A"/><rect x="166" y="58" width="60" height="24" rx="4" fill="#2A2A2A"/><path d="M226,70 H290" style="stroke:#2A2A2A;stroke-width:6"/>'
          '<text x="152" y="114" class="lbl" text-anchor="middle">la clavija entra sin forzar y</text><text x="152" y="126" class="lbl" text-anchor="middle">la placa no se mueve al enchufar</text>')
    p4 = ('<rect x="30" y="40" width="110" height="80" rx="8" class="tin"/><text x="85" y="134" class="lbl" text-anchor="middle">fondo</text>'
          '<rect x="164" y="40" width="110" height="80" rx="8" class="tin"/><text x="219" y="134" class="lbl" text-anchor="middle">tapa</text>'
          '<circle cx="219" cy="80" r="18" class="brass"/>'
          '<path d="M201,80 C170,80 172,40 152,40 C132,40 150,90 110,96" class="wc w-red" style="stroke-width:2;fill:none"/>'
          '<text x="152" y="22" class="lbl" text-anchor="middle">bucle de holgura</text>')
    return panels([('Atornilla el jack', p1), ('Pega la protoboard', p2), ('Prueba el USB', p3), ('Cables del piezo con holgura', p4)],
                  'Cuatro viñetas: atornillar el jack con la tuerca por fuera, deslizar la protoboard hacia la pared y pegarla, probar que la clavija USB entra sin mover la placa y dejar un bucle de holgura en los cables del piezo')

def fig_short():
    tin = '<rect x="40" y="30" width="120" height="96" rx="10" class="tin"/><rect x="70" y="60" width="56" height="50" class="bbside"/>'
    p1 = (tin + '<circle cx="48" cy="80" r="4" fill="var(--paper)" stroke="var(--ink)"/>'
          + probe((48, 80), 'black', 'lata', -22, 28) + probe((98, 72), 'red', 'J4', 30, -34) + meter(168, 40, 'OL', 'silencio ✔'))
    p2 = (tin + '<circle cx="48" cy="80" r="4" fill="var(--paper)" stroke="var(--ink)"/>'
          + probe((48, 80), 'black', 'lata', -22, 28) + probe((98, 72), 'red', 'J2', 30, -34) + meter(168, 40, '♪ 000', 'pita ✔'))
    return panels([('Lata ↔ J4 (5 V): NO pita', p1), ('Lata ↔ J2 (GND): pita', p2)],
                  'Dos viñetas con el multímetro en continuidad: entre la lata y J4 no debe pitar; entre la lata y J2 sí pita, por el jack')

# ---------------- pasos ----------------
def steps():
    s = []
    n = 0
    def add(title, text, ch, body=''):
        nonlocal n; n += 1; s.append(step(n, title, text, ch, body))
    def under(key, title, text, a, b, color, chip, cap):
        add(title, text, [(color, chip)],
            fig(board_svg(title, key, ring(a[0], a[1], f'{a[0]}{a[1]}', 14, 4, 'start') + ring(b[0], b[1], f'{b[0]}{b[1]}', 14, 4, 'start')), cap))

    add('Saca la Pro Micro de la protoboard',
        'Haz palanca suave por los dos extremos a la vez con un destornillador plano, sin doblar patillas. Primero van tres cables que pasan <b>por debajo</b> de la placa, y luego no se pueden poner.',
        [('', 'protoboard vacía')],
        fig(f'<svg viewBox="-30 20 375 365" role="img" aria-label="Protoboard vacía con la silueta de la Pro Micro">' + board_base() + promicro(ghost=True) + '</svg>',
            'Silueta discontinua = dónde volverá la Pro Micro: patillas en las columnas D y H, filas 1 a 12.'))

    under('gnd_u', 'Cable negro por debajo: F2 → F16',
          'Corta 6 cm de cable negro rígido, pela 5 mm en cada punta y dobla las puntas en ángulo recto para que el cable quede <b>plano</b> contra la protoboard. Una punta en F2 (la fila del GND derecho de la Pro Micro) y la otra en F16. Toda la fila 16 derecha pasa a ser GND.',
          ('F', 2), ('F', 16), 'black', 'F2 → F16',
          'Va por la columna F, que quedará tapada por la placa. Tiene que ir plano para que la Pro Micro encaje encima.')
    under('a0_u', 'Cable verde por debajo: G8 → G14',
          'Igual, con 4 cm de cable verde, pegado al negro: de G8 (la fila del pin A0) a G14. La fila 14 derecha será la entrada del piezo.',
          ('G', 8), ('G', 14), 'green', 'G8 → G14',
          'No lo confundas con la columna H: ahí irán las patillas de la placa.')
    under('b_u', 'Cable morado por debajo: E7 → E17',
          'Con 5 cm de cable morado: de E7 (la fila del pin 4) a E17. Este cable encenderá el azul del LED.',
          ('E', 7), ('E', 17), 'purple', 'E7 → E17',
          'Es el único cable morado: así sabes siempre que es el del azul.')

    add('Vuelve a poner la Pro Micro',
        'USB hacia arriba, la fila de TX0 en D1 y la de RAW en H1. Cuenta: a la izquierda de las patillas quedan 3 agujeros libres (A, B, C) y a la derecha 2 (I, J). Aprieta hasta que baje del todo sin pisar los cables de debajo.',
        [('', 'TX0 → D1'), ('', 'RAW → H1')],
        fig(board_svg('Pro Micro colocada encima de los tres cables', 'pm', ring('D', 1, 'D1', -14, 4, 'end') + ring('H', 1, 'H1', 14, 4, 'start')),
            'Los cables de debajo salen en línea discontinua: ya no se ven, pero siguen ahí. Solo asoman sus puntas en E17, F16 y G14.'))

    add('Mide los cables de debajo (sin USB)',
        'Multímetro en continuidad (el pitido). Tienen que pitar J2 con J16, J8 con J14 y A7 con A17. Y <b>no</b> debe pitar J14 con J16.',
        [('', 'J2–J16 pita'), ('', 'J8–J14 pita'), ('', 'A7–A17 pita'), ('', 'J14–J16 no pita')],
        fig(board_svg('Comprobación con el multímetro', 'pm', probe(H('J', 2), 'black', 'J2', 60, -10) + probe(H('J', 16), 'red', 'J16', 60, 10)
                      + probe(H('A', 7), 'black', 'A7', -60, -10) + probe(H('A', 17), 'red', 'A17', -60, 10)),
            'Si algo no pita, un cable de debajo se ha salido: saca la placa y vuelve a meterlo.'))

    s.append('<li class="phase">Piezo</li>')
    add('Resistencia de 2,2 MΩ: I14 → I16',
        'Rojo · rojo · verde. Tumbada por la columna I, de I14 a I16 (salta la fila 15). Descarga el piezo después de cada golpe.',
        [('', '2,2 MΩ'), ('', 'I14 · I16')],
        fig(board_svg('Resistencia de 2,2 MΩ entre I14 y I16', 'r2m', ring('I', 14, 'I14', 12, -6, 'start') + ring('I', 16, 'I16', 12, 14, 'start')),
            'La fila 15 queda debajo de la resistencia sin tocarla.'))

    add('Prepara y conecta el piezo: rojo H14, negro H16',
        'Los cables del piezo son finos y no aguantan en la protoboard. Suelda a cada uno 3 cm de cable rígido del mismo color y tapa la soldadura con termorretráctil. Deja cable largo: el piezo irá en la tapa y tiene que poder abrirse. Rojo en H14 (fila de A0, por el cable verde de debajo), negro en H16 (GND). La columna J queda libre para el cable de 5 V.',
        [('red', 'piezo rojo → H14'), ('black', 'piezo negro → H16')],
        warn('<b>Si montaste la versión anterior del manual:</b> quita la 10 kΩ que estaba de pie en H14–H15 (ahora va en el jack) y pasa el rojo del piezo de G15 a H14.') +
        fig(fig_piezo_prep(), 'Deja unos 15 cm entre el piezo y la protoboard para que la tapa abra del todo.')
        + fig(board_svg('Piezo conectado en H14 y H16', 'piezo', ring('H', 14, 'H14', 12, -8, 'start') + ring('H', 16, 'H16', 12, 16, 'start')),
              'El piezo va directo a A0, como en el ejemplo Knock de Arduino: la 2,2 MΩ lo descarga y el chip tiene diodos de protección internos.'))

    s.append('<li class="phase">LED RGB</li>')
    add('Identifica las patas del LED RGB',
        'La pata más larga es la común. Mirando el LED con esa pata en segundo lugar, el orden es R, común, G, B. Tu LED es de <b>ánodo común</b>: la pata larga va a 5 V y cada color se enciende cuando su pin baja a 0 V.',
        [('', 'R · − · G · B')],
        fig(fig_led_id(), 'Ya comprobado: roja en la larga y negra en R, se enciende. El sketch 08 ya tiene COMMON_ANODE = true.'))

    add('Pon el LED: C14 a C17, pata larga en C15',
        'Abre un poco las patas para que entren en 4 agujeros seguidos de la columna C: R en C14, la larga en C15, G en C16 y B en C17. B ya queda conectado: el cable morado de debajo sale en E17. Deja el LED alto si quieres que asome por un agujero de la tapa.',
        [('', 'R C14'), ('red', 'común C15'), ('', 'G C16'), ('purple', 'B C17')],
        fig(board_svg('LED RGB en la columna C, filas 14 a 17', 'led', ring('C', 15, 'C15', 16, 4, 'start')),
            'La fila 17 izquierda ya lleva el pin 4 por el cable morado de debajo.'))

    add('Cable rojo de 5 V: J4 → J17',
        'Cable rojo rígido tumbado por la columna J, de J4 (fila del pin VCC = 5 V) a J17. Toda la fila 17 derecha pasa a tener 5 V para alimentar el LED.',
        [('red', 'J4 → J17 · VCC')],
        fig(board_svg('Cable rojo de J4 a J17', 'vcc', ring('J', 4, 'J4 = VCC', 12, 4, 'start') + ring('J', 17, 'J17', 12, 4, 'start')),
            'No lo metas en ningún agujero intermedio: solo J4 y J17.'))

    add('Resistencia de 220 Ω cruzando el canal: D15 → G17',
        'Rojo · rojo · marrón. Va de D15 (pata común del LED) a G17 (fila de 5 V), pasando por encima del canal central. Es la única resistencia del LED: protege los tres colores.',
        [('', '220 Ω'), ('', 'D15 → G17')],
        fig(board_svg('Resistencia de 220 Ω entre D15 y G17', 'r220', ring('D', 15, 'D15', -12, 4, 'end') + ring('G', 17, 'G17', 0, 22)),
            'El sketch enciende los colores por turnos muy rápido, así que nunca pasan dos a la vez por esta resistencia.'))

    add('Cable rojo: A8 → A14',
        'Cable rojo rígido, tumbado por la columna A: de A8 (fila del pin 5) a A14 (pata R).',
        [('red', 'A8 → A14 · pin 5')],
        fig(board_svg('Cable rojo de A8 a A14', 'wr', ring('A', 8, 'A8 = pin 5', -12, 4, 'end') + ring('A', 14, 'A14', -12, 4, 'end')),
            'Color del cable = color del LED que enciende.'))

    add('Cable verde: B9 → B16',
        'Cable verde rígido por la columna B: de B9 (fila del pin 6) a B16 (pata G). Va paralelo al rojo.',
        [('green', 'B9 → B16 · pin 6')],
        fig(board_svg('Cable verde de B9 a B16', 'wg', ring('B', 9, 'B9 = pin 6', -28, 4, 'end') + ring('B', 16, 'B16', -28, 4, 'end')),
            'Pasa por encima de A y C sin meterse en ningún agujero intermedio.'))

    s.append('<li class="phase">Jack</li>')
    add('Comprueba los 3 cables del jack',
        'Tu jack tiene morado, negro y verde. Enchufa un cable de audio, pon el multímetro en continuidad y toca con una punta la parte larga metálica del conector (el manguito) y con la otra el cable <b>negro</b>: tiene que pitar. Ese es la masa (S). Morado y verde son la punta y el anillo: como los vamos a unir, da igual cuál es cuál.',
        [('black', 'negro = masa S'), ('purple', 'morado'), ('green', 'verde → se unen')],
        warn('<b>Si el negro no pita con el manguito:</b> prueba morado y verde y dime cuál pita. No los unas hasta saberlo.'))

    add('Suelda la 10 kΩ al morado y al verde',
        'Sigue las 6 viñetas. Morado y verde se retuercen juntos y ahí se suelda una pata de la 10 kΩ (marrón · negro · naranja). La otra pata queda al aire, de 1 cm, y se pincha directamente en la protoboard. Al negro se le empalma un trozo de cable rígido negro para que entre bien en el agujero.',
        [('purple', '+'), ('green', '→ 10 kΩ → C12'), ('black', 'negro → A3')],
        fig(fig_solder_steps(), 'El termorretráctil siempre se mete <b>antes</b> de soldar: después ya no entra. Para calentarlo vale el lateral del soldador, sin tocarlo, o un mechero de lejos.')
        + fig(fig_jack_wiring(), 'Así queda: punta y anillo unidos (morado y verde), la 10 kΩ en medio y su pata libre a C12.'))

    add('Jack: negro a A3, pata de la 10 kΩ a C12',
        'El cable negro (masa) va a A3, fila GND. La pata libre de la 10 kΩ se pincha en C12, la fila del pin 9.',
        [('black', 'negro → A3'), ('', 'pata 10 kΩ → C12 · pin 9')],
        fig(board_svg('Jack conectado: negro en A3 y verde en C12', 'jack_s', ring('A', 3, 'A3', -12, -4, 'end') + ring('C', 12, 'C12', 14, -6, 'start')),
            'A12 y B12 quedan tapados por los cables rojo y verde; por eso la señal entra por C12.')
        + warn('<b>Con auriculares:</b> la 10 kΩ deja el volumen bajito pero seguro. En la KO II suena bien. Si más adelante compras 1 kΩ, 10 nF y 10 µF, cambiamos esto por un filtro y sonará más fuerte y limpio.'))

    s.append('<li class="phase">Programa y prueba</li>')
    add('Sube el sketch 08 y mira el LED',
        'Conecta el USB y sube <code>sketches/08_caja_muelle</code>. Al arrancar el LED enciende <b>rojo, verde y azul</b>, medio segundo cada uno. Luego respira despacio cambiando de color: eso indica que está en marcha.',
        [('', 'rojo → verde → azul'), ('', 'luego respira')],
        '<pre><code>arduino-cli compile --fqbn arduino:avr:micro sketches/08_caja_muelle\narduino-cli upload  -p /dev/cu.usbmodem2101 --fqbn arduino:avr:micro sketches/08_caja_muelle</code></pre>'
        + warn('<b>Colores en otro orden:</b> no pasa nada. Cambia los números de LED_R, LED_G y LED_B en el sketch.'))

    add('Golpea el piezo y escucha',
        'Conecta auriculares o un ampli al jack con el volumen <b>bajo</b>. Da golpecitos al piezo: suena un "boing" metálico, más agudo cuanto más fuerte, y el LED destella y salta de color. Para ver la fuerza de cada golpe abre el monitor serie:',
        [('', 'boing por el jack'), ('', 'destello de color')],
        '<pre><code>arduino-cli monitor -p /dev/cu.usbmodem2101 -c baudrate=115200</code></pre>'
        '<p>Salen líneas como <code>golpe 180  vel 63</code>. Si dispara sin tocarlo, sube <code>THRESHOLD</code>; si los golpes suaves no suenan, bájalo.</p>')

    s.append('<li class="phase">Dentro de la caja</li>')
    add('Decide dónde va cada cosa',
        'Pon la protoboard (todavía sin pegar) en el fondo con el USB mirando a una de las paredes cortas, y que <b>no sea</b> la de la bisagra. El jack va en esa misma pared, a la derecha de la protoboard. Arriba queda una zona libre: ahí caerá el piezo cuando cierres la tapa.',
        [('', 'USB + jack: la misma pared'), ('', 'piezo: zona libre')],
        fig(fig_plan(), 'Así sale todo el cableado por un solo lado. El piezo no puede caer encima de la placa ni del LED: la tapa los aplastaría al cerrar.'))
    add('Aísla el fondo',
        'La lata es de metal y conduce: si una patilla la toca, hay cortocircuito. Cubre <b>todo</b> el fondo con tiras de cinta aislante (o Kapton) solapadas y súbelas 1 cm por las paredes cercanas a la protoboard. Hazlo ahora, antes de medir: la cinta levanta un poco la placa y cambia la altura del USB.',
        [('', 'cinta aislante'), ('', 'tiras solapadas')],
        fig(fig_insulate(), 'Una cartulina o un trozo de plástico de blíster recortado a medida también sirve, encima o en lugar de la cinta.'))
    add('Mide el agujero del USB y el del jack',
        'Pon la protoboard sobre la cinta, con el USB a 1-2 mm de la pared. Con una regla o un calibre mide <b>X</b> (del borde exterior izquierdo de la pared al centro del conector) e <b>Y</b> (del fondo al centro del conector). El tamaño lo da la parte de plástico de la clavija de tu cable: mídela y suma 1 mm por cada lado (suele salir unos 12 × 8 mm). El jack va a la derecha, con su centro a unos 8-10 mm del fondo y donde su cuerpo no toque la protoboard. Su agujero es del diámetro de la rosca (normalmente 6 mm). Apunta todas las medidas.',
        [('', 'X · Y del USB'), ('', 'clavija + 2 mm'), ('', 'jack Ø rosca')],
        fig(fig_usb_measure(), 'La pared es muy fina: medir por dentro o por fuera da igual. Deja al menos 10 mm entre el jack y la esquina para que la tuerca apoye en plano.'))
    add('Marca el LED y el piezo en la tapa',
        'Pon una bolita de Blu-Tack encima del LED, cierra la tapa con suavidad y ábrela: la marca que queda en la tapa es el centro del agujero de 5 mm. Haz lo mismo con una bolita grande en el centro de la zona libre: esa marca es donde irá el centro del piezo (y el muelle encima, por fuera). El agujero del LED es opcional: sin él, la luz se queda dentro.',
        [('', 'Blu-Tack'), ('', 'LED Ø 5 mm (opcional)')],
        fig(fig_marks(), 'La tapa se cierra dando la vuelta: por eso es mejor marcar así que medir, porque el lado izquierdo y el derecho se invierten.'))
    add('Vacía la lata y taladra los agujeros redondos',
        'Saca <b>toda</b> la electrónica: las virutas de metal en la protoboard dan cortocircuitos. Ponte gafas. Pega cinta de carrocero en la zona, pasa a ella las medidas y marca los centros con una cruz. Apoya la pared por dentro con un taco de madera sujeto con un sargento (la chapa se dobla con nada). Un toque suave de punzón, broca de 2 mm a velocidad media, y agranda a 4 y 6 mm para el jack (5 mm para el LED en la tapa). Una broca escalonada va de lujo.',
        [('', 'gafas'), ('', 'cinta de carrocero'), ('', '2 → 4 → 6 mm')],
        fig(fig_drill(), 'Sin el taco de madera la broca abolla la pared en lugar de cortarla.') +
        warn('<b>Cuidado:</b> los bordes recién cortados de la lata cortan como una cuchilla. Usa guantes al limar y no pases el dedo por el agujero.'))
    add('Recorta el agujero del USB',
        'Dibuja el rectángulo con tus medidas. Taladra un agujero de 2-3 mm en cada esquina, por dentro del rectángulo. Únelos con el disco de corte de la Dremel o con más agujeros seguidos, y cuadra con una lima de aguja. Prueba la clavija a menudo: es mejor quedarse corto y seguir limando que pasarse. Si el rectángulo se mete en la franja de arriba, hazlo como muesca abierta y lima otra igual en el borde de la tapa.',
        [('', 'disco de corte'), ('', 'lima de aguja')],
        fig(fig_usb_cut(), 'Con el disco de corte, gafas siempre: si el disco se rompe, salta.'))
    add('Quita rebabas y limpia',
        'Lima las rebabas por dentro y por fuera de cada agujero (o pasa la lija de tambor de la Dremel) hasta que el borde no corte al tocarlo con cuidado. Recoge las virutas con un imán envuelto en cinta, lava la lata con agua y jabón y sécala del todo. Si la cinta del fondo se ha llenado de virutas, cámbiala.',
        [('', 'sin rebabas'), ('', 'sin virutas')])
    add('Tapa: piezo por dentro, muelle por fuera',
        'En la marca del piezo, pega el disco con el <b>latón contra el metal</b>, con unas gotas de pegamento instantáneo (la silicona caliente amortigua el golpe y suena menos). Tapa con cinta aislante la cara blanca y la soldadura del cable rojo. Por fuera, justo encima, pega la base del muelle con epoxi y deja que endurezca el tiempo que diga el envase.',
        [('', 'latón contra la tapa'), ('', 'cinta en la cara blanca'), ('', 'muelle con epoxi')],
        fig(fig_lid(), 'El latón del piezo y la lata son los dos GND, así que pueden tocarse. La cara blanca es la señal: si toca el metal, el piezo deja de funcionar.'))
    add('Monta todo dentro',
        'Pasa el jack desde dentro y aprieta la tuerca por fuera. Quita el papel del adhesivo de la protoboard, deslízala hasta que el USB quede frente a su agujero y aprieta contra el fondo. Prueba a enchufar el cable: tiene que entrar sin forzar y la placa no se debe mover. Deja un bucle de holgura en los cables del piezo hacia la bisagra.',
        [('', 'tuerca por fuera'), ('', 'USB frente al agujero'), ('red', 'holgura en el piezo')],
        fig(fig_mount(), 'Si la placa se mueve al enchufar, pon un taco de espuma o cinta de doble cara gruesa detrás de la protoboard, en el lado contrario a la pared.'))
    add('Comprueba que no hay cortos',
        'Sin el USB conectado, multímetro en continuidad. Toca la lata en un punto sin pintura (el borde de un agujero sirve) y J4: <b>no debe pitar</b>. Luego lata y J2: <b>sí pita</b>, porque el jack une la lata con GND.',
        [('', 'lata ↔ J4: silencio'), ('', 'lata ↔ J2: pita')],
        fig(fig_short(), 'Si lata y J4 pitan, no conectes el USB: algo de 5 V toca el metal. Busca una patilla o un cable pelado contra la pared o la tapa.'))
    add('Cierra y prueba',
        'Cierra la tapa despacio, mirando que nada empuje la Pro Micro ni el LED. Conecta el USB: el LED hace rojo, verde, azul. Golpea el muelle y escucha. Dentro de la lata el golpe llega distinto: abre el monitor serie y ajusta <code>THRESHOLD</code> y <code>PEAK_FOR_MAX</code> si hace falta.',
        [('', 'rojo · verde · azul'), ('', 'boing por el jack')],
        '<pre><code>arduino-cli monitor -p /dev/cu.usbmodem2101 -c baudrate=115200</code></pre>'
        '<p>Si al mover la caja o golpear la mesa salen golpes que no has dado, sube <code>THRESHOLD</code>. Si los golpes fuertes no llegan al máximo, baja <code>PEAK_FOR_MAX</code>.</p>')
    return ''.join(s)


def hole_table():
    rows = [('Cable negro (debajo)', 'F2 → F16', 'GND a la fila 16 derecha'),
            ('Cable verde (debajo)', 'G8 → G14', 'A0 a la fila 14 derecha'),
            ('Cable morado (debajo)', 'E7 → E17', 'pin 4 → azul del LED'),
            ('Pro Micro', 'D1–D12 · H1–H12', 'USB arriba'),
                        ('2,2 MΩ', 'I14 · I16', 'descarga el piezo'),
            ('Piezo', 'rojo H14 · negro H16', 'directo a A0'),
            ('Cable rojo 5 V', 'J4 → J17', 'VCC a la fila 17 derecha'),
            ('LED RGB', 'C14 R · C15 común · C16 G · C17 B', ''),
            ('220 Ω', 'D15 → G17', 'pata común a 5 V'),
            ('Cable rojo', 'A8 → A14', 'pin 5 → rojo'),
            ('Cable verde', 'B9 → B16', 'pin 6 → verde'),
            ('Jack', 'S → A3 · T+R → 10 kΩ → C12', 'pin 9; la 10 kΩ soldada en el cable')]
    t = ''.join(f'<tr><td>{a}</td><td><code>{b}</code></td><td>{c}</td></tr>' for a, b, c in rows)
    return f'<div class="tscroll"><table><thead><tr><th>Pieza</th><th>Agujeros</th><th>Para qué</th></tr></thead><tbody>{t}</tbody></table></div>'

CSS = '''
:root{
  --paper:#FCFCFB; --ink:#16181B; --muted:#5C646B; --rule:#D5D9DC; --soft:#F0F2F3;
  --bb:#F4E6C0; --gapc:#E6D6A8; --hole:#8E7F58; --pcb:#233A6B; --pin:#C9A227;
  --accent:#D9480F; --halo:#FCFCFB; --halo-k:#FCFCFB;
  --w-red:#D62828; --w-green:#2E9E44; --w-black:#1A1A1A; --w-purple:#8E4FD8;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --sans:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  --disp:'Archivo','Helvetica Neue',Arial,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#101214; --ink:#ECEEF0; --muted:#9AA2A9; --rule:#2B3136; --soft:#181B1E;
  --bb:#3A3424; --gapc:#2A2519; --hole:#7D7254; --pcb:#2E4A86;
  --accent:#FF8A5B; --halo:#101214; --halo-k:#C9CED3; --w-black:#0A0A0A; color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#101214; --ink:#ECEEF0; --muted:#9AA2A9; --rule:#2B3136; --soft:#181B1E;
  --bb:#3A3424; --gapc:#2A2519; --hole:#7D7254; --pcb:#2E4A86;
  --accent:#FF8A5B; --halo:#101214; --halo-k:#C9CED3; --w-black:#0A0A0A; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.5;
  padding-block:32px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:44px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(34px,7vw,56px);line-height:1.02;margin:8px 0 12px;letter-spacing:-.01em;text-wrap:balance}
.lead{font-size:18px;max-width:60ch;margin:0}
.meta{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:16px;font-family:var(--mono);font-size:13px;color:var(--muted)}
h2{font-family:var(--disp);font-weight:800;font-size:26px;margin:0 0 14px;text-wrap:balance}
section{display:flex;flex-direction:column;gap:12px}
p{margin:0}
code{font-family:var(--mono);font-size:.92em}
pre{margin:0;background:var(--soft);border:1px solid var(--rule);border-radius:4px;padding:12px 14px;overflow-x:auto;font-size:13px}
.dia{margin:6px 0 0;border:1.5px solid var(--ink);border-radius:4px;background:var(--paper)}
.dia figcaption{font-size:14px;color:var(--muted);padding:10px 14px;border-top:1px solid var(--rule);max-width:70ch}
.scroll{overflow-x:auto}
.dia svg{display:block;width:100%;height:auto;min-width:340px;max-width:620px;max-height:640px;margin:0 auto}
.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:40px}
.phase{font-family:var(--mono);font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:-24px;padding-top:12px}
.step{display:grid;grid-template-columns:76px minmax(0,1fr);gap:16px;padding-top:28px;border-top:3px solid var(--ink)}
.num{font-family:var(--disp);font-weight:800;font-size:64px;line-height:.9;letter-spacing:-.02em}
.sbody{min-width:0;display:flex;flex-direction:column;gap:10px}
.step h3{font-size:21px;margin:4px 0 0;font-weight:600;text-wrap:balance}
.step p{max-width:62ch}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:13px;font-weight:500;border:1.5px solid var(--ink);border-radius:4px;padding:3px 9px;background:var(--soft)}
.chip i{width:11px;height:11px;border-radius:50%;background:var(--muted);flex:none}
.chip.red i{background:var(--w-red)}.chip.green i{background:var(--w-green)}.chip.purple i{background:var(--w-purple)}
.chip.black i{background:var(--w-black);outline:1.5px solid var(--halo-k)}
.warn{border:1.5px solid var(--accent);border-left-width:6px;padding:12px 14px;border-radius:4px;max-width:70ch}
.warn b{color:var(--accent)}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--ink)}
.tscroll{overflow-x:auto}.tscroll table{min-width:520px}
ul.mat{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px}
.dia text{font-family:var(--mono)}
.bb{fill:var(--bb);stroke:var(--ink);stroke-width:1.2}
.gapc{fill:var(--gapc)}
.hole{fill:var(--hole)}
.col{font-size:8px;fill:var(--muted);text-anchor:middle}
.rowl{font-size:7px;fill:var(--muted)}
.lbl{font-size:9px;fill:var(--muted)}
.pcb{fill:var(--pcb);stroke:var(--ink);stroke-width:1}
.ghost{fill:none;stroke:var(--muted);stroke-width:1.4;stroke-dasharray:5 4}
.usb{fill:#B8C0C8;stroke:var(--ink);stroke-width:1}
.pin{fill:var(--pin)}
.pn{font-size:6.5px;fill:#EAF0FF}
.mcu{fill:#0E1220;stroke:#5A6A9A;stroke-width:1}
.old{opacity:.45}
.leg{stroke:#8A939A;stroke-width:1.8}
.legend{fill:#8A939A}
.rbody{fill:#E3CF9C;stroke:#6B5A2E;stroke-width:1}
.ring{fill:none;stroke:var(--accent);stroke-width:2}
.hn{font-size:9px;font-weight:700;fill:var(--accent);paint-order:stroke;stroke:var(--paper);stroke-width:3px;stroke-linejoin:round}
.wh{fill:none;stroke:var(--halo);stroke-width:7;stroke-linecap:round}
.wh-k{fill:none;stroke:var(--halo-k);stroke-width:7;stroke-linecap:round}
.wc{fill:none;stroke-width:3.4;stroke-linecap:round}
.hid{stroke-dasharray:6 5}
.wc.w-red{stroke:var(--w-red)}.wc.w-green{stroke:var(--w-green)}.wc.w-black{stroke:var(--w-black)}.wc.w-purple{stroke:var(--w-purple)}
.wend.w-red{fill:var(--w-red)}.wend.w-green{fill:var(--w-green)}.wend.w-purple{fill:var(--w-purple)}
.wend.w-black{fill:var(--w-black);stroke:var(--halo-k);stroke-width:1}
.brass{fill:#C9A24A;stroke:var(--ink);stroke-width:1.2}
.ceramic{fill:#EDE6D2;stroke:#7A6A3A;stroke-width:1}
.ledrgb{fill:#EEF3F7;fill-opacity:.85;stroke:var(--ink);stroke-width:1.3}
.ledl{font-size:7px;font-weight:700;fill:var(--ink)}
.jackb{fill:#2B3040;stroke:var(--ink);stroke-width:1.5}
.lug{fill:var(--pin);stroke:var(--ink);stroke-width:.8}
.prb-red{stroke:var(--w-red);stroke-width:4;stroke-linecap:round}
.prb-black{stroke:var(--ink);stroke-width:4;stroke-linecap:round}
.prb-tip-red{fill:var(--w-red)}.prb-tip-black{fill:var(--ink)}
.mm{fill:#C5D3B8;stroke:var(--ink);stroke-width:1.5}
.mmv{font-size:28px;font-weight:700;fill:#1B2418}
.mmu{font-size:10px;fill:#1B2418}
.sline{stroke:var(--ink);stroke-width:2;fill:none}
.sbox{fill:var(--soft);stroke:var(--ink);stroke-width:1.6}
.stxt{font-size:11px;fill:var(--ink)}
.sdot{fill:var(--ink)}
.spm{fill:var(--pcb);stroke:var(--ink);stroke-width:1.2}
.spt{font-size:11px;fill:#EAF0FF}
.ins{fill:var(--w-red)}
.strand{fill:#B87333}
.tinned{fill:#CDD3D8;stroke:#8A939A;stroke-width:1}
.shrink{fill:#2A2A2A;stroke:var(--ink)}
.solder{fill:#CDD3D8;stroke:#6E767D;stroke-width:1}
.shrinkbox{fill:#2A2A2A;fill-opacity:.35;stroke:var(--ink);stroke-dasharray:4 3}
.tin{fill:#C8CDD2;stroke:var(--ink);stroke-width:1.5}
.bbside{fill:#E9C77A;stroke:var(--ink)}
.pcbside{fill:var(--pcb)}
.spring{fill:none;stroke:#8A939A;stroke-width:3}
.tape{stroke:#3A3F45;stroke-width:3;stroke-dasharray:10 4}
@media (max-width:560px){.step{grid-template-columns:1fr;gap:6px}.num{font-size:48px}}
'''

def main():
    final = board_svg('Protoboard terminada con todas las piezas', None)
    h = ['<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Caja de muelle</title>',
         '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">',
         f'<style>{CSS}</style></head><body><main class="wrap">',
         '<header><div class="eyebrow">Noise Box · Pro Micro · montaje completo</div><h1>Caja de muelle</h1>'
         '<p class="lead">Una lata con un muelle por fuera y un piezo por dentro. Cada golpe suena por el jack como un "boing" metálico y un LED RGB cambia de color con la fuerza. Todo en la mini protoboard, alimentado por el USB.</p>'
         '<div class="meta"><span>1,5–2 h</span><span>hay que soldar (piezo y jack)</span><span>sketch 08_caja_muelle</span></div></header>',
         '<section><h2>Qué vamos a montar</h2>' + fig(overview(), 'Tres partes: el piezo entra por A0, el sonido sale por el pin 9 y el LED usa los pines 5, 6 y 4. El USB da la corriente; al desenchufarlo se apaga.') + '</section>',
         '<section><h2>Material</h2><ul class="mat">'
         '<li>Pro Micro (5 V) y protoboard de 170 puntos</li><li>Piezo de disco y un muelle</li>'
         '<li>Jack hembra 3,5 mm con sus 3 cables</li><li>LED RGB de 4 patas</li>'
         '<li>Tres resistencias: 10 kΩ, 2,2 MΩ y 220 Ω</li><li>Cable rígido negro, verde, rojo y morado; termorretráctil</li>'
         '<li>Caja metálica, cinta aislante (o Kapton), cinta de carrocero, Blu-Tack, pegamento instantáneo y epoxi</li>'
         '<li>Herramientas: pelacables, soldador, multímetro, Dremel con brocas de 2, 4 y 6 mm (o escalonada) y disco de corte, punzón, limas de aguja, sargento y taco de madera, gafas y guantes</li></ul>'
         + fig(fig_res(), 'La banda dorada (tolerancia) va siempre a la derecha cuando lees los colores.') + '</section>',
         '<section><h2>Así queda la protoboard</h2>' + fig(final, 'Todo montado. Las líneas discontinuas son los tres cables que van por debajo de la Pro Micro.') + hole_table() + '</section>',
         '<section><h2>Montaje</h2><ol class="steps">' + steps() + '</ol></section>',
         '<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Causa probable</th><th>Qué hacer</th></tr></thead><tbody>'
         '<tr><td>El LED no se enciende al arrancar</td><td>Pata larga fuera de C15, la 220 Ω o el cable rojo de 5 V sueltos</td><td>Revisa D15–G17 y J4–J17</td></tr>'
         '<tr><td>Falta un color</td><td>Su cable no toca la fila correcta</td><td>Revisa rojo A8–A14, verde B9–B16 y morado de debajo E7–E17</td></tr>'
         '<tr><td>Suena y destella sin tocar nada</td><td>Umbral bajo o la de 2,2 MΩ suelta</td><td>Revisa I14–I16; sube THRESHOLD</td></tr>'
         '<tr><td>Los golpes no hacen nada</td><td>Cable verde de debajo suelto o piezo al revés</td><td>Rojo del piezo en H14, negro en H16; mide de la patilla A0 a H14</td></tr>'
         '<tr><td>Luz bien pero no suena</td><td>Jack en la fila equivocada o T/R mal identificados</td><td>Verde en C12, negro en A3; repite la prueba de los cables del jack</td></tr>'
         '<tr><td>Muy bajo con auriculares</td><td>Es la 10 kΩ de protección</td><td>Normal por ahora: el sketch ya va al máximo. Con el filtro (1 kΩ, 10 nF, 10 µF) sonará más</td></tr>'
         '<tr><td>La placa no encaja al ponerla</td><td>Los cables de debajo no van planos</td><td>Aplánalos o pásalos más pegados</td></tr>'
         '</tbody></table></div></section>',
         '</main></body></html>']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(h)); print('ok', OUT)

main()
