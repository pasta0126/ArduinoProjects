#!/usr/bin/env python3
# Genera manuals/test-tira-led.html: prueba de la tira de 8 LED con la Arduino Micro en protoboard grande.
import re, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'manuals', 'test-tira-led.html')
src = re.sub(r'\nmain\(\)\s*$', '\n', open(os.path.join(HERE, 'gen_manual01.py'), encoding='utf-8').read())
G = {}; exec(compile(src, 'g1', 'exec'), G)
wire, resistor = G['wire'], G['resistor']
m02 = open(os.path.join(ROOT, 'manuals', '02-diodos-y-potenciometro.html'), encoding='utf-8').read()
CSS = re.search(r'<style>(.*?)</style>', m02, re.S).group(1) + '''
.wc.w-purple{stroke:#9B5DE5}.wend.w-purple{fill:#9B5DE5}
.chip.purple i{background:#9B5DE5}
.ledbar{fill:#1B1F2A;stroke:var(--ink);stroke-width:1.5}
.padg{fill:var(--pin);stroke:var(--ink);stroke-width:.8}
.padt{font-size:7px;fill:#EAF0FF;text-anchor:middle}
.big text{font-family:var(--mono)}
.dia svg.big{max-width:none;min-width:780px;width:100%}
.rn{font-size:6.5px;fill:var(--muted);text-anchor:middle}
.pl{font-size:7px;fill:#EAF0FF;text-anchor:middle}
.hl{fill:none;stroke:var(--accent);stroke-width:2}
.pinhi{fill:var(--accent)}
'''
X0 = 100; DX = 20
def X(r): return X0 + (64 - r) * DX
ROWY = {'A': 60, 'B': 80, 'C': 100, 'D': 120, 'E': 140, 'F': 190, 'G': 210, 'H': 230, 'I': 250, 'J': 270}
def P(l, r): return X(r), ROWY[l]
TOPL = ['12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'GND', 'RST', 'RX0', 'TX1']
BOTL = ['13', '3V3', 'AREF', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', '', '', '5V', '', '', '']
COL = ['#FF0000', '#FF5A00', '#C8C800', '#00C800', '#00DCDC', '#2A2AFF', '#8C00FF', '#FF00A0']

def board():
    s = []
    s.append(f'<rect x="{X(64)-14}" y="42" width="{X(36)-X(64)+28}" height="244" rx="6" class="bb"/>')
    s.append(f'<rect x="{X(64)-14}" y="156" width="{X(36)-X(64)+28}" height="22" class="gapc"/>')
    for r in range(64, 35, -1):
        if r % 2 == 0 or r in (61, 52): s.append(f'<text x="{X(r)}" y="34" class="rn">{r}</text>')
        for l, y in ROWY.items(): s.append(f'<circle cx="{X(r)}" cy="{y}" r="2" class="hole"/>')
    for l, y in ROWY.items(): s.append(f'<text x="{X(64)-24}" y="{y+3}" class="rn" text-anchor="end">{l}</text>')
    return ''.join(s)

def micro():
    s = [f'<rect x="{X(64)-52}" y="106" width="42" height="64" rx="3" class="usb"/><text x="{X(64)-31}" y="142" class="lbl" text-anchor="middle" style="font-size:8px">USB</text>']
    s.append(f'<rect x="{X(64)-12}" y="68" width="{X(44)-X(64)+34}" height="154" rx="4" class="pcb"/>')
    s.append(f'<text x="{X(56)}" y="148" class="pl" style="font-size:11px">ARDUINO MICRO</text>')
    for i in range(15):
        r = 63 - i
        for (l, lab, dy) in (('B', TOPL[i], 18), ('G', BOTL[i], -9)):
            x, y = P(l, r); hi = (l == 'B' and lab in ('10', 'GND')) or (l == 'G' and lab == '5V')
            s.append(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" class="{"pinhi" if hi else "pin"}"/>')
            if lab:
                sty = ' style="font-weight:700"' if hi else ''
                s.append(f'<text x="{x}" y="{y+dy}" class="pl"{sty}>{lab}</text>')
    return ''.join(s)

def ring(l, r, name, dx=0, dy=-14, anchor='middle'):
    x, y = P(l, r)
    return f'<circle cx="{x}" cy="{y}" r="7" class="ring"/><text x="{x+dx}" y="{y+dy}" class="hn" text-anchor="{anchor}">{name}</text>'

def strip():
    s = ['<rect x="420" y="296" width="290" height="40" rx="4" class="ledbar"/>']
    pads = {'5V': (440, 304), 'GND': (458, 304), 'DIN': (476, 304)}
    for n, (x, y) in pads.items():
        s.append(f'<rect x="{x-5}" y="{y-4}" width="10" height="9" class="padg"/><text x="{x}" y="{y+17}" class="padt">{n}</text>')
    for i in range(8): s.append(f'<rect x="{510+i*24}" y="306" width="18" height="20" rx="2" fill="{COL[i]}" opacity=".9"/>')
    s.append('<text x="565" y="352" class="lbl" text-anchor="middle">tira de 8 LED (usa el extremo DIN)</text>')
    return ''.join(s), pads

def diagram():
    st, pads = strip()
    a62, a42 = P('A', 61), P('A', 44)
    lila = wire(f'M{a62[0]},{a62[1]} C{a62[0]},4 {a42[0]},4 {a42[0]},{a42[1]}', 'purple', [a62, a42])
    res = resistor(P('C', 44), P('C', 41), ['red', 'red', 'brown'])
    d38 = P('D', 41); a53 = P('A', 52); h53 = P('H', 52)
    gx, gy = pads['GND']; fx, fy = pads['5V']; dx_, dy_ = pads['DIN']
    green = wire(f'M{dx_},{dy_} C{dx_},{dy_-30} {d38[0]+20},{d38[1]+120} {d38[0]},{d38[1]}', 'green', [(dx_, dy_), d38])
    black = wire(f'M{gx},{gy} C{gx},{gy+40} 740,330 730,200 C720,60 700,44 640,44 L{a53[0]},44 L{a53[0]},{a53[1]}', 'black', [(gx, gy), a53])
    red = wire(f'M{fx},{fy} C{fx},{fy-30} {h53[0]+40},{h53[1]+40} {h53[0]},{h53[1]}', 'red', [(fx, fy), h53])
    rings = (ring('A', 61, 'A61', 0, -12) + ring('A', 52, 'A52', 0, -26) + ring('H', 52, 'H52', 0, 20) + ring('A', 44, 'A44', 0, -12) + ring('D', 41, 'D41', 18, 4, 'start'))
    return ('<svg viewBox="0 0 760 360" role="img" class="big" aria-label="Arduino Micro en protoboard grande con la tira de LED: GND a A52, 5V a H52, pin 10 por la resistencia a DIN">'
            + board() + micro() + st + lila + res + green + black + red + rings + '</svg>')

def fig(svg, cap): return f'<figure class="dia"><div class="scroll">{svg}</div><figcaption>{cap}</figcaption></figure>'
def chips(items): return '<div class="chips">' + ''.join(f'<span class="chip {c}"><i></i>{t}</span>' for c, t in items) + '</div>'
def step(n, t, p, c): return f'<li class="step"><div class="num" aria-hidden="true">{n}</div><div class="sbody"><h3>{t}</h3><p>{p}</p>{chips(c)}</div></li>'

h = ['<title>Test de la tira</title>', '<meta charset="utf-8"><meta name="claude:viewport-fit-sides" content="cover">',
     '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">',
     f'<style>{CSS}</style>', '<main class="wrap">',
     '<header><div class="eyebrow">Noise Box · Arduino Micro · prueba de la tira</div><h1>Test de la tira de LED</h1>'
     '<p class="lead">Arcoíris que se desplaza por los 8 LED, solo para comprobar que la tira funciona. Sin piezo ni potenciómetro, sobre tu protoboard grande con la Arduino Micro.</p>'
     '<div class="meta"><span>10 min</span><span>5 cables y 1 resistencia</span><span>sketch 05_test_tira_arcoiris</span></div></header>',
     '<section><h2>Qué conectar y dónde</h2>' + fig(diagram(),
        'Vista desde arriba con el USB a la izquierda. Los números son las filas de tu protoboard. En naranja, los tres pines de la placa que usamos: pin 10 y GND arriba, 5V abajo.') + '</section>',
     '<section><h2>Tabla de conexiones</h2><div class="tscroll"><table><thead><tr><th>Cable</th><th>De</th><th>A</th></tr></thead><tbody>'
     '<tr><td>Negro (GND de la tira)</td><td>tira</td><td><b>A52</b> (fila del pin GND, arriba)</td></tr>'
     '<tr><td>Rojo (5V de la tira)</td><td>tira</td><td><b>H52</b> (fila del pin 5V, abajo)</td></tr>'
     '<tr><td>Lila</td><td><b>A61</b> (fila del pin 10)</td><td><b>A44</b></td></tr>'
     '<tr><td>Resistencia 220 Ω (rojo, rojo, marrón)</td><td><b>C44</b></td><td><b>C41</b></td></tr>'
     '<tr><td>Verde (DIN de la tira)</td><td>tira</td><td><b>D41</b></td></tr>'
     '</tbody></table></div></section>',
     '<section><h2>Pasos</h2><ol class="steps">',
     step(1, 'Mira las etiquetas de tu placa', 'Antes de conectar, lee el texto impreso junto a los pines. El pin <b>10</b> es el tercero empezando por el USB en la fila de arriba. <b>GND</b> está en la misma fila de arriba, junto a RST. <b>5V</b> está en la fila de abajo. Si no coincide con la tabla, guíate por el texto de tu placa y la fila de ese pin.', [('', 'pin 10: tercero desde el USB'), ('', 'GND: arriba, junto a RST'), ('', '5V: abajo, fila 52')]),
     step(2, 'Con el USB desenchufado, monta el camino de datos', 'Un cable lila de A61 a A44. La resistencia de 220 Ω de C44 a C41. El cable verde de la tira (DIN) a D41.', [('purple', 'A61 → A44'), ('red', '220 Ω: C44 → C41'), ('green', 'DIN → D41')]),
     step(3, 'Alimenta la tira', 'El cable negro de GND a A52 y el cable rojo de 5V a H52. No los cambies: la tira se estropea.', [('black', 'GND → A52'), ('red', '5V → H52')]),
     step(4, 'Enchufa el USB', 'Con el sketch 05 cargado, los 8 LED deben mostrar un arcoíris que se desplaza solo. Si no se enciende nada, desenchufa y revisa que DIN va al extremo de entrada de la tira y que 5V y GND no están cambiados.', []),
     '</ol></section>',
     '<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Qué hacer</th></tr></thead><tbody>'
     '<tr><td>Nada se enciende</td><td>Revisa que el cable verde esté en el extremo DIN de la tira (no en DOUT) y que A61 → A44 estén bien metidos</td></tr>'
     '<tr><td>Colores al azar o parpadeo</td><td>Falta masa: revisa A52 y que la resistencia esté en C44 y C41</td></tr>'
     '<tr><td>Solo luce el primer LED</td><td>Los datos entran bien pero no pasan: cambia la tira de extremo</td></tr>'
     '<tr><td>Los colores salen cambiados</td><td>En el sketch cambia NEO_GRB por NEO_RGB</td></tr>'
     '<tr><td>Muy apagados</td><td>Mira que el rojo esté en el pin 5V y no en el 3V3 (segundo pin de abajo)</td></tr>'
     '</tbody></table></div></section></main>']
open(OUT, 'w', encoding='utf-8').write('\n'.join(h)); print('ok', OUT)
