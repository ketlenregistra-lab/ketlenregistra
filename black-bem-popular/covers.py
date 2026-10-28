# Gera as 3 capas (posts fixados) com logo e elementos de farmácia, e substitui em artes.html
import re

DEFS = '''<defs>
  <filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#000" flood-opacity=".55"/></filter>
  <linearGradient id="bag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3171f"/><stop offset="1" stop-color="#9c0c0d"/></linearGradient>
  <linearGradient id="foil" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f4"/><stop offset=".5" stop-color="#c9ccd1"/><stop offset="1" stop-color="#eef0f2"/></linearGradient>
  <linearGradient id="boxf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232323"/><stop offset="1" stop-color="#0b0b0b"/></linearGradient>
  <radialGradient id="glow"><stop offset="0" stop-color="#ffd200" stop-opacity=".35"/><stop offset="1" stop-color="#ffd200" stop-opacity="0"/></radialGradient>
</defs>'''

def capsule(x, y, rot, a, b, s=1.0):
    return f'''<g transform="translate({x} {y}) rotate({rot}) scale({s})" filter="url(#sh)">
  <rect x="-110" y="-42" width="220" height="84" rx="42" fill="{b}"/>
  <path d="M0 -42 H-68 A42 42 0 0 0 -68 42 H0 Z" fill="{a}"/>
  <rect x="-96" y="-30" width="180" height="16" rx="8" fill="#fff" opacity=".35"/>
</g>'''

def pill(x, y, r, c):
    return f'<g filter="url(#sh)"><circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/><rect x="{x-r*.6}" y="{y-3}" width="{r*1.2}" height="6" rx="3" fill="#000" opacity=".15"/></g>'

def tape(y, rot, text, bg='#ffd200'):
    t = (' • '.join([text] * 6))
    return f'''<g transform="rotate({rot} 540 {y})" filter="url(#sh)">
  <rect x="-200" y="{y-46}" width="1480" height="92" fill="{bg}"/>
  <rect x="-200" y="{y-46}" width="1480" height="9" fill="#0d0d0d"/><rect x="-200" y="{y+37}" width="1480" height="9" fill="#0d0d0d"/>
  <text x="-160" y="{y+14}" font-family="Montserrat" font-weight="900" font-size="40" letter-spacing="1.5" fill="#0d0d0d">{t}</text>
</g>'''

def box(x, y, w, h, d, s=1.0):
    # caixa de remédio lacrada em 3D
    return f'''<g transform="translate({x} {y}) scale({s})" filter="url(#sh)">
  <polygon points="0,0 {d},{-d*.6} {w+d},{-d*.6} {w},0" fill="#3a3a3a"/>
  <polygon points="{w},0 {w+d},{-d*.6} {w+d},{h-d*.6} {w},{h}" fill="#050505"/>
  <rect x="0" y="0" width="{w}" height="{h}" fill="url(#boxf)"/>
  <rect x="0" y="{h*.72}" width="{w}" height="{h*.1}" fill="#d3131b"/>
  <g transform="translate({w*.18} {h*.16})"><rect x="-9" y="-26" width="18" height="52" fill="#fff"/><rect x="-26" y="-9" width="52" height="18" fill="#fff"/></g>
  <text x="{w/2}" y="{h*.64}" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="{h*.5}" fill="#ffd200">?</text>
</g>'''

def blister(x, y, rot):
    wells = ''
    for r in range(2):
        for c in range(4):
            cx, cy = 90 + c * 125, 95 + r * 140
            wells += f'''<circle cx="{cx}" cy="{cy}" r="50" fill="#fff"/><circle cx="{cx}" cy="{cy}" r="50" fill="none" stroke="#aeb2b8" stroke-width="5"/>
<text x="{cx}" y="{cy+24}" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="70" fill="#d3131b">?</text>'''
    return f'''<g transform="translate({x} {y}) rotate({rot})" filter="url(#sh)">
  <rect x="0" y="0" width="555" height="330" rx="36" fill="url(#foil)"/>
  <rect x="14" y="14" width="527" height="302" rx="26" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>
  {wells}
</g>'''

def bag():
    return '''<g filter="url(#sh)">
  <!-- produtos espiando pra fora da sacola -->
  <rect x="395" y="130" width="125" height="170" rx="8" fill="#151515"/><text x="457" y="250" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="100" fill="#ffd200">?</text>
  <rect x="545" y="95" width="80" height="205" rx="30" fill="#f2f2f2"/><rect x="560" y="60" width="50" height="50" rx="8" fill="#ffd200"/>
  <text x="585" y="230" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="80" fill="#d3131b">?</text>
  <path d="M640 300 L655 140 Q690 120 715 140 L700 300 Z" fill="#ffd200"/>
  <path d="M435 280 C430 170 650 170 645 280" fill="none" stroke="#7a0909" stroke-width="22" stroke-linecap="round"/>
  <polygon points="340,270 740,270 775,610 305,610" fill="url(#bag)"/>
  <polygon points="340,270 740,270 744,310 336,310" fill="#7a0909" opacity=".55"/>
  <circle cx="540" cy="455" r="88" fill="#fff"/>
  <rect x="520" y="395" width="40" height="120" rx="6" fill="#d3131b"/><rect x="480" y="435" width="120" height="40" rx="6" fill="#d3131b"/>
</g>'''

def cross(x, y, s, c='#ffd200', op=.9):
    return f'<g transform="translate({x} {y}) scale({s})" opacity="{op}"><rect x="-12" y="-36" width="24" height="72" rx="5" fill="{c}"/><rect x="-36" y="-12" width="72" height="24" rx="5" fill="{c}"/></g>'

def svg(inner):
    return f'<svg class="hero" width="1080" height="660" viewBox="0 0 1080 660">{DEFS}<ellipse cx="540" cy="360" rx="420" ry="300" fill="url(#glow)"/>{inner}</svg>'

hero1 = svg(
    capsule(150, 150, -30, '#d3131b', '#ffd200') + capsule(930, 120, 28, '#ffffff', '#d3131b', .8)
    + capsule(960, 500, -18, '#ffd200', '#ffffff', .75) + capsule(120, 520, 40, '#d3131b', '#ffffff', .7)
    + pill(250, 330, 30, '#ffd200') + pill(840, 330, 26, '#fff') + cross(240, 60, .8) + cross(860, 610, .7, '#fff', .6)
    + bag() + tape(400, -8, 'CONFIDENCIAL • SEGREDO') + tape(520, 6, 'BLACK SECRETA • NÃO ABRIR', '#ffffff'))

hero2 = svg(
    capsule(140, 120, 30, '#ffd200', '#d3131b', .85) + capsule(950, 160, -25, '#ffffff', '#ffd200', .8)
    + capsule(100, 560, -15, '#d3131b', '#ffffff', .7) + pill(980, 520, 30, '#ffd200') + pill(190, 400, 24, '#fff')
    + cross(900, 60, .8) + cross(170, 270, .6, '#fff', .6)
    + box(560, 240, 270, 340, 70) + box(240, 330, 260, 250, 60) + box(285, 140, 190, 170, 50)
    + tape(360, 9, 'LACRADO • NÃO ABRIR', '#ffffff') + tape(470, -7, 'PROIBIDO CONTAR • SEGREDO'))

hero3 = svg(
    capsule(160, 110, -35, '#d3131b', '#ffffff', .85) + capsule(930, 100, 20, '#ffd200', '#d3131b', .8)
    + capsule(960, 560, -30, '#ffffff', '#ffd200', .75) + capsule(130, 560, 25, '#ffd200', '#d3131b', .7)
    + pill(230, 330, 28, '#fff') + pill(880, 340, 30, '#ffd200') + cross(870, 250, .6, '#fff', .6) + cross(200, 230, .7)
    + blister(262, 170, -7) + tape(470, -6, 'CONFIDENCIAL • SEGREDO') + tape(580, 5, 'BLACK SECRETA • NÃO ABRIR', '#ffffff'))

LOGO = '<img class="logo" src="logo.png" alt="Drogarias Bem Popular">'
DATE = '<div class="chip">05/11 <span>•</span> ÀS 17H</div>'

covers = {
    'f1-01': f'''<section class="slide cover" id="f1-01">
  {LOGO}{hero1}
  <div class="h xl one">A MAIOR</div>
  <div class="s">black do ano está chegando</div>
  {DATE}
</section>''',
    'f2-capa-reels': f'''<section class="slide cover" id="f2-capa-reels">
  {LOGO}{hero2}
  <div class="h xl one white">BLACK</div>
  <div class="h" style="font-size:80px;margin-top:22px">Estamos <span class="box">proibidos</span></div>
  <div class="s" style="margin-top:14px;font-size:56px">de contar até o dia <b style="color:var(--yellow);font-weight:800">05/11</b> 🤐</div>
</section>''',
    'f3-01': f'''<section class="slide cover" id="f3-01">
  {LOGO}{hero3}
  <div class="h xl one">DO ANO</div>
  <div class="s">tudo que você precisa saber<br>(sem estragar a surpresa)</div>
  <div class="chips"><div class="chip">DIA 05/11</div><div class="chip">⏰ 17H</div><div class="chip">🛒 COMPRA NA HORA</div></div>
</section>''',
}

CSS = '''
  /* capas dos fixados */
  .slide.cover { padding-bottom: 110px; }
  .cover .logo { position: absolute; top: 48px; left: 50%; transform: translateX(-50%); width: 270px; filter: drop-shadow(0 8px 18px rgba(0,0,0,.5)); z-index: 2; }
  .cover .hero { position: absolute; top: 200px; left: 0; }
  .h.xl.one { font-size: 196px; white-space: nowrap; letter-spacing: -0.055em; position: relative; text-shadow: 0 10px 30px rgba(0,0,0,.35); }
  .cover .s { position: relative; }
  .chip { display: inline-block; margin-top: 34px; background: var(--yellow); color: var(--black); font-weight: 900; font-size: 46px; letter-spacing: -0.02em; padding: 10px 30px; position: relative; }
  .chip span { color: var(--red); }
  .chips { display: flex; gap: 18px; justify-content: center; position: relative; }
  .chips .chip { font-size: 34px; padding: 10px 22px; }
'''

p = 'artes.html'
s = open(p, encoding='utf-8').read()
for cid, html in covers.items():
    s, n = re.subn(r'<section class="slide[^"]*" id="%s">.*?</section>' % re.escape(cid), lambda m: html, s, flags=re.S)
    assert n == 1, cid
if '/* capas dos fixados */' not in s:
    s = s.replace('</style>', CSS + '</style>')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
