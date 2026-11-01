#!/usr/bin/env python3
# Genera manuals/04-salida-jack.html (reutiliza piezas de los manuales 01-03).
import re, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'manuals', '04-salida-jack.html')
src = open(os.path.join(HERE, 'gen_manual03.py'), encoding='utf-8').read()
src = re.sub(r'\nmain\(\)\s*$', '\n', src)
G = {'__file__': os.path.join(HERE, 'gen_manual03.py')}; exec(compile(src, 'gen_manual03', 'exec'), G)
H, wire, ring, fig, step, board_fig, ALL = (G[k] for k in ('H', 'wire', 'ring', 'fig', 'step', 'board_fig', 'ALL'))
CSS = G['CSS'] + '''
.jackb{fill:#2B3040;stroke:var(--ink);stroke-width:1.5}
.lug{fill:var(--pin);stroke:var(--ink);stroke-width:.8}
'''
VB = '-210 30 630 540'
LUGS = {'S': (-84, 150), 'T': (-84, 200), 'R': (-84, 232)}
FIL = (-84, 262)

def jack():
    s = ['<rect x="-190" y="130" width="100" height="150" rx="6" class="jackb"/>',
         '<circle cx="-150" cy="205" r="18" fill="var(--paper)" stroke="var(--ink)"/>',
         '<text x="-140" y="124" class="lbl" text-anchor="middle">jack 3,5 mm</text>']
    for n, (x, y) in LUGS.items():
        s.append(f'<rect x="{x-6}" y="{y-4}" width="12" height="8" class="lug"/><text x="{x+10}" y="{y+3}" class="padt" style="text-anchor:start;fill:var(--ink)">{n}</text>')
    s.append(f'<rect x="{FIL[0]-6}" y="{FIL[1]-4}" width="12" height="8" class="lug"/>')
    s.append(f'<text x="-190" y="298" class="lbl">filtro soldado aquí</text>')
    return ''.join(s)

def w_gnd():
    x, y = H('A', 4); sx, sy = LUGS['S']
    return wire(f'M{x},{y} C{x-40},{y-30} {sx+60},{sy+10} {sx},{sy}', 'black', [(x, y), (sx, sy)])
def w_sig():
    x, y = H('A', 12); fx, fy = FIL
    return wire(f'M{x},{y} C{x-40},{y+10} {fx+60},{fy+20} {fx},{fy}', 'green', [(x, y), (fx, fy)])

def stage(now, done=()):
    items = [(ALL[k], 'old') for k in ('bar', 'relay', 'res', 'gnd', '5v', 'din')]
    items.append((jack(), 'new'))
    for k, f in (('gnd', w_gnd), ('sig', w_sig)):
        if k == now: items.append((f(), 'new'))
        elif k in done: items.append((f(), 'old'))
    return items

def schematic():
    return '''<svg viewBox="0 0 620 230" role="img" aria-label="Filtro: pin 9 a resistencia de 4,7 kilohmios; de ahí un condensador de 10 nanofaradios a masa y otro de 10 microfaradios a la punta del jack">
<text x="10" y="66" class="stxt">pin 9</text><line x1="55" y1="62" x2="130" y2="62" class="sline"/>
<rect x="130" y="50" width="86" height="24" rx="4" fill="#E3CF9C" stroke="#6B5A2E"/><text x="173" y="66" class="stxt" text-anchor="middle">4,7 kΩ</text>
<line x1="216" y1="62" x2="400" y2="62" class="sline"/><circle cx="270" cy="62" r="4" class="sdot"/>
<line x1="270" y1="62" x2="270" y2="105" class="sline"/><line x1="255" y1="105" x2="285" y2="105" class="sline"/><line x1="255" y1="115" x2="285" y2="115" class="sline"/>
<line x1="270" y1="115" x2="270" y2="190" class="sline"/><text x="282" y="114" class="stxt">10 nF</text>
<rect x="320" y="46" width="14" height="32" fill="none" stroke="var(--ink)"/><text x="327" y="40" class="stxt" text-anchor="middle">+</text><text x="327" y="96" class="stxt" text-anchor="middle" style="font-size:10px">10 µF</text>
<text x="400" y="66" class="stxt">punta (T)</text>
<line x1="20" y1="190" x2="400" y2="190" class="sline"/><text x="410" y="194" class="stxt">masa (S) = GND</text>
<text x="10" y="214" class="stxt" style="font-size:10px">el filtro quita el zumbido del PWM; el 10 µF quita la tensión continua</text></svg>'''

def steps_html():
    s = []
    s.append(step(1, 'Sin USB: identifica las tres patillas del jack',
        'Con el multímetro en continuidad, enchufa un cable de audio en el jack. Toca la parte larga metálica del conector (el manguito) con cada patilla: la que pite es la masa (S). Toca ahora la punta del conector: la que pite es la punta (T). La que queda es el anillo (R).',
        [('', 'manguito → S (masa)'), ('', 'punta → T'), ('', 'tercera → R')],
        fig(board_fig('Jack con tres patillas', [(jack(), 'new')], '', VB),
            'Si tu jack tiene otra disposición, usa lo que marque el multímetro. Si la tercera patilla es de contacto y no pita con ninguna parte, déjala libre.')))
    s.append(step(2, 'Suelda el filtro en el jack',
        'Resistencia de 4,7 kΩ (amarillo, violeta, rojo). Una pata queda libre para el cable verde; la otra va al nodo central. Del nodo salen el condensador de 10 nF (marcado 103) hacia S y el electrolítico de 10 µF con el + hacia el nodo y el − hacia T. Si la tercera patilla es el anillo (R), únela con T para oír por los dos lados.',
        [('red', 'R 4,7 kΩ'), ('', '10 nF nodo→S'), ('', '10 µF +nodo, −T')],
        fig(schematic(), 'El electrolítico tiene una banda en el lado negativo. Si lo pones al revés no suena bien y puede calentarse.')))
    s.append(step(3, 'Cable negro: GND de la placa al jack',
        'Suelda un cable negro rígido a la patilla S del jack y el otro extremo va a A4, en la fila del pin GND, a la izquierda.',
        [('black', 'S → A4')],
        fig(board_fig('GND a A4', stage('gnd'), ring('A', 4, 'A4', -14, 4, 'end'), VB), 'A4 es la fila del pin GND, a la izquierda de la Pro Micro.')))
    s.append(step(4, 'Cable verde: pin 9 a la entrada del filtro',
        'Suelda un cable verde a la pata libre de la resistencia. El otro extremo va a A12, en la fila del pin 9.',
        [('green', 'resistencia → A12')],
        fig(board_fig('Pin 9 a A12', stage('sig', ['gnd']), ring('A', 12, 'A12', -14, 4, 'end'), VB), 'A12 es la fila del pin 9. No uses la del pin 10, que es la del aro.')
        + '<div class="warn"><b>Revisa antes de conectar:</b> verde en A12 y negro en A4. Con los dos cambiados el sonido no sale.</div>'))
    s.append(step(5, 'Enchufa el USB y toca',
        'El sketch 07 ya está cargado. Conecta un cable al jack, sube un poco el volumen del ampli o la KO II y golpea el piezo. Suena una guitarra con el acorde que marca el aro.',
        [('', 'Sketch 07_acordes_aro_jack')],
        '<div class="warn"><b>Con auriculares:</b> empieza con el volumen muy bajo. La salida es fuerte para unos auriculares.</div>'))
    return ''.join(s)

def main():
    h = ['<title>Salida de audio jack</title>', '<meta charset="utf-8"><meta name="claude:viewport-fit-sides" content="cover">',
         '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;600&display=swap">',
         f'<style>{CSS}</style>', '<main class="wrap">',
         '<header><div class="eyebrow">Noise Box · Pro Micro · Manual 04 · jack</div><h1>Salida de audio jack</h1>'
         '<p class="lead">La caja suena por un jack de 3,5 mm hacia un ampli, unos auriculares o la KO II. La placa saca la guitarra por el pin 9 y un pequeño filtro la limpia.</p>'
         '<div class="meta"><span>30–40 min</span><span>hay que soldar</span><span>2 cables a la placa: A4 y A12</span></div></header>',
         '<section><h2>Qué vamos a añadir</h2>' + fig(schematic(), 'El filtro va soldado en el jack y a la placa solo llegan dos cables.') + '</section>',
         '<section><h2>Material</h2><p>Jack hembra de 3,5 mm con 3 patillas, resistencia de 4,7 kΩ, condensador cerámico de 10 nF (103), electrolítico de 10 µF, cable rígido verde y negro, soldador y multímetro. Sketch 07 cargado.</p></section>',
         '<section><h2>Montaje</h2><ol class="steps">' + steps_html() + '</ol></section>',
         '<section><h2>Si algo falla</h2><div class="tscroll"><table><thead><tr><th>Lo que ves</th><th>Causa probable</th><th>Qué hacer</th></tr></thead><tbody>'
         '<tr><td>No suena nada</td><td>Cable en la fila equivocada o jack mal identificado</td><td>Revisa A12, A4 y las patillas S y T</td></tr>'
         '<tr><td>Zumbido o ruido agudo</td><td>Falta el condensador de 10 nF o masa floja</td><td>Revisa la soldadura a S</td></tr>'
         '<tr><td>Suena muy bajo</td><td>Volumen del equipo</td><td>Sube el volumen o baja OUT_SHIFT en el sketch</td></tr>'
         '<tr><td>Suena solo por un lado</td><td>T y R sin unir</td><td>Une las patillas T y R</td></tr>'
         '<tr><td>Clic leve al golpear</td><td>El aro actualiza sus LED</td><td>Dímelo y lo suavizo en el sketch</td></tr>'
         '</tbody></table></div></section>', '</main>']
    open(OUT, 'w', encoding='utf-8').write('\n'.join(h)); print('ok', OUT)
main()
