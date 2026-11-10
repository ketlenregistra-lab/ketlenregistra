"""Elementos animados do Dia 14 (gráficos rosa estilo referência) + plano completo.
Gera clipes .mov com transparência em escala 4K e grava o plano final."""
import json, os, subprocess, sys, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(S, 'trab'); FX = os.path.join(T, 'fx'); os.makedirs(FX, exist_ok=True)
FPS = 30
ROSA = (245, 127, 160)            # #f57fa0, cor dela
ROSA_CLARO = (251, 214, 225)
BEGE = (244, 240, 232)            # bege Claude
CINZA = (205, 196, 186)
MONO = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-SemiBold.ttf'
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
for f in (MONO, INTER_B):
    if not os.path.exists(f):
        r = subprocess.run(['fc-match', '-f', '%{file}', 'JetBrains Mono:semibold' if f == MONO else 'Inter:bold'], capture_output=True, text=True).stdout
        if f == MONO: MONO = r
        else: INTER_B = r

w = json.load(open(os.path.join(T, 'palavras.json')))
cortes = json.load(open(os.path.join(T, 'cortes.json')))
fim = w[-1][1]


def t_de(palavra, depois=0.0, n=1):
    """Início da n-ésima palavra (sem pontuação, minúsculas) a partir do instante `depois`."""
    k = 0
    for a, b, x in w:
        if a >= depois and x.strip('.,?!').lower() == palavra:
            k += 1
            if k == n:
                return a, b
    raise SystemExit(f'palavra não achada: {palavra} depois de {depois}')


def escrever(nome, frames_fn, n, size):
    out = os.path.join(FX, nome + '.mov')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{size[0]}x{size[1]}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'qtrle', '-pix_fmt', 'argb', out], stdin=subprocess.PIPE)
    vazio = None
    for i in range(n):
        im = frames_fn(i / FPS)
        if im is None:
            if vazio is None:
                vazio = Image.new('RGBA', size, (0, 0, 0, 0)).tobytes()
            p.stdin.write(vazio)
        else:
            p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return out


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def pop(x):
    """0 -> 1.12 -> 1 (entrada com mola)."""
    x = max(0.0, min(1.0, x))
    return 1.12 * ease(x / 0.7) if x < 0.7 else 1.12 - 0.12 * ease((x - 0.7) / 0.3)


def com_alpha(im, a):
    if a >= 0.999:
        return im
    r, g, b, al = im.split(); al = al.point(lambda v: int(v * a)); return Image.merge('RGBA', (r, g, b, al))


def sombra(im, raio=18, op=90, desl=(0, 10)):
    W_, H_ = im.size; pad = raio * 3
    base = Image.new('RGBA', (W_ + 2 * pad, H_ + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0)); a = im.split()[3].point(lambda v: v * op // 255)
    sh.paste((60, 20, 35, 255), (pad + desl[0], pad + desl[1]), a); sh = sh.filter(ImageFilter.GaussianBlur(raio))
    base.alpha_composite(sh); base.alpha_composite(im, (pad, pad)); return base, pad


def animar_estatico(nome, img, dur, entra=0.35, sai=0.3, escala_pop=True):
    """Clipe de uma imagem parada que entra com 'pop' e sai com fade."""
    img, pad = sombra(img, 16, 70, (0, 8))
    W_, H_ = img.size

    def fr(t):
        e = pop(t / entra) if escala_pop else 1.0
        a = min(1.0, t / 0.15) * (1.0 if t < dur - sai else max(0.0, (dur - t) / sai))
        if a <= 0:
            return None
        if abs(e - 1) < 0.003:
            return com_alpha(img, a)
        s = max(0.02, e); im2 = img.resize((max(1, int(W_ * s)), max(1, int(H_ * s))), Image.LANCZOS)
        c = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); c.alpha_composite(im2, ((W_ - im2.width) // 2, (H_ - im2.height) // 2))
        return com_alpha(c, a)
    return escrever(nome, fr, int(dur * FPS), (W_, H_)), pad


# ---------------------------------------------------------------- peças
def chip(texto):
    fn = ImageFont.truetype(MONO, 62); fb = ImageFont.truetype(MONO, 62)
    num, resto = texto.split('|')
    wn = fb.getlength(num); wr = fn.getlength(resto); h = 112; padx = 44
    im = Image.new('RGBA', (int(wn + wr + padx * 2 + 34), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, h - 1], h // 2, fill=ROSA + (245,))
    d.text((padx, h // 2), num, font=fb, fill=(255, 255, 255, 255), anchor='lm')
    d.text((padx + wn + 34, h // 2), resto, font=fn, fill=(255, 255, 255, 255), anchor='lm')
    return im


def emoji(ch, tam):
    f = ImageFont.truetype(EMOJI, 109)        # Noto Color Emoji só tem esse tamanho
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); return im.resize((tam, int(tam * im.height / im.width)), Image.LANCZOS)


def icone_sem_fundo(arq, tam):
    im = Image.open(arq).convert('RGB'); a = np.asarray(im).astype(int)
    fundo = (a.min(axis=2) > 246)                 # branco puro do fundo (o ícone tem borda/sombra levemente cinza)
    ys, xs = np.where(~fundo); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    im = im.crop((x0, y0, x1 + 1, y1 + 1)); W_, H_ = im.size
    m = Image.new('L', (W_ * 4, H_ * 4), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, W_ * 4 - 1, H_ * 4 - 1], int(W_ * 4 * 0.225), fill=255)
    im = im.convert('RGBA'); im.putalpha(m.resize((W_, H_), Image.LANCZOS))
    return im.resize((tam, tam), Image.LANCZOS)


def coracao(tam, cor=ROSA):
    S4 = tam * 4; im = Image.new('RGBA', (S4, S4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for k in range(200):
        t = 2 * math.pi * k / 200
        x = 16 * math.sin(t) ** 3; y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((S4 / 2 + x * S4 / 36, S4 / 2.15 - y * S4 / 36))
    d.polygon(pts, fill=cor + (255,))
    # brilho suave
    d.ellipse([S4 * 0.27, S4 * 0.22, S4 * 0.42, S4 * 0.34], fill=(255, 255, 255, 110))
    return im.resize((tam, tam), Image.LANCZOS)


def card_corte(dur):
    """Janela bege (cor do Claude) com letras rosa: o áudio bruto, as pausas marcadas e o vídeo encolhendo."""
    W_, H_ = 1520, 470
    # envelope real da voz no bruto
    wv = wave.open(os.path.join(T, 'audio', 'Video01.wav')); sr = wv.getframerate()
    x = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(float) / 32768
    if wv.getnchannels() > 1: x = x.reshape(-1, wv.getnchannels()).mean(1)
    total = len(x) / sr; N = 96; seg = len(x) // N
    env = np.array([np.sqrt(np.mean(x[i * seg:(i + 1) * seg] ** 2)) for i in range(N)]); env = env / env.max()
    keep = np.zeros(N)
    for n, s, e, *_ in cortes:
        for i in range(N):
            a, b = i * total / N, (i + 1) * total / N
            keep[i] += max(0, min(b, e) - max(a, s)) / (b - a)
    corta = keep < 0.55
    dfim = sum((e - s) / (v[0] if v else 1) for n, s, e, *v in cortes)
    fm = ImageFont.truetype(MONO, 40); fb = ImageFont.truetype(INTER_B, 132); fs = ImageFont.truetype(MONO, 46)
    mmss = lambda t: f'{int(t // 60)}:{int(round(t % 60)):02d}' if round(t % 60) < 60 else f'{int(t // 60) + 1}:00'

    def fr(t):
        if t > dur:
            return None
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, W_ - 1, H_ - 1], 44, fill=BEGE + (250,))
        for k, c in enumerate([(240, 110, 120), (246, 180, 90), (140, 200, 120)]):
            d.ellipse([40 + k * 50, 36, 72 + k * 50, 68], fill=c + (255,))
        d.text((W_ // 2, 54), 'corte_automatico.mp4', font=fm, fill=(190, 140, 155, 255), anchor='mm')
        d.line([0, 100, W_, 100], fill=(230, 220, 210, 255), width=3)
        # fases: 0.5-2.6 varredura | 2.6-4.4 pausas somem e o tempo cai | depois: segura
        scan = ease((t - 0.5) / 2.1); cola = ease((t - 2.6) / 1.8)
        tempo = total + (dfim - total) * cola
        d.text((48, 190), 'bruto', font=fs, fill=(190, 140, 155, 255), anchor='lm')
        d.text((48, 250), mmss(total), font=fs, fill=ROSA + (255,), anchor='lm')
        d.text((W_ - 48, 214), mmss(tempo), font=fb, fill=ROSA + (255,), anchor='rm')
        n_cortes = int(round(corta.sum() * min(1.0, scan)))
        d.text((W_ // 2 - 40, 214), f'{n_cortes} pausas e erros' if t < 2.6 else 'cortado ✓' if cola >= 1 else 'cortando…',
               font=fs, fill=(190, 140, 155, 255), anchor='mm')
        # barras
        x0, x1, yb, hmax = 48, W_ - 48, 395, 95
        larg = (x1 - x0) / N; xs = x0
        for i in range(N):
            lw = larg * (1 - cola) if corta[i] else larg
            if lw < 0.5:
                continue
            h = max(10, env[i] * hmax)
            if corta[i] and (i + 0.5) / N <= scan:
                cor = CINZA + (int(255 * (1 - cola)),)
            else:
                cor = ROSA + (255,)
            d.rounded_rectangle([xs + lw * 0.18, yb - h / 2, xs + lw * 0.82, yb + h / 2], int(min(lw * 0.3, 6)), fill=cor)
            xs += lw
        if 0.5 < t < 2.6:   # linha de varredura
            sx = x0 + (x1 - x0) * scan; d.line([sx, yb - 70, sx, yb + 70], fill=(120, 80, 95, 255), width=5)
        a = min(1.0, t / 0.2) * (1.0 if t < dur - 0.3 else max(0.0, (dur - t) / 0.3))
        im, _ = sombra(im, 20, 80, (0, 12))
        e = pop(t / 0.35)
        if abs(e - 1) > 0.003:
            im2 = im.resize((max(1, int(im.width * e)), max(1, int(im.height * e))), Image.LANCZOS)
            c = Image.new('RGBA', im.size, (0, 0, 0, 0)); c.alpha_composite(im2, ((im.width - im2.width) // 2, (im.height - im2.height) // 2)); im = c
        return com_alpha(im, a)
    tam = sombra(Image.new('RGBA', (W_, H_)), 20)[0].size
    return escrever('card_corte', fr, int(dur * FPS), tam), sombra(Image.new('RGBA', (W_, H_)), 20)[1]


def coracoes(dur):
    W_, H_ = 1700, 1500    # quadro cobrindo em volta dela
    pos = [(170, 520, 190, -12), (1460, 380, 230, 10), (60, 1080, 150, -6), (1540, 1040, 170, 14), (760, 120, 140, 4)]
    cs = [coracao(s) for *_, s, _r in pos]

    def fr(t):
        im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); vis = False
        for k, ((x, y, s, r), c) in enumerate(zip(pos, cs)):
            tk = t - k * 0.22
            if tk <= 0:
                continue
            e = pop(tk / 0.35); a = 1.0 if t < dur - 0.4 else max(0.0, (dur - t) / 0.4)
            if a <= 0:
                continue
            fl = -40 * ease(tk / 2.5)
            cc = c.rotate(r + 6 * math.sin(tk * 3), resample=Image.BICUBIC, expand=True)
            cc = cc.resize((max(1, int(cc.width * e)), max(1, int(cc.height * e))), Image.LANCZOS)
            im.alpha_composite(com_alpha(cc, a), (int(x + (s - cc.width) / 2), int(y + fl + (s - cc.height) / 2))); vis = True
        return im if vis else None
    return escrever('coracoes', fr, int(dur * FPS), (W_, H_))


def flutuante(nome, img, dur):
    """Emoji/ícone que entra com pop e balança de leve."""
    img, pad = sombra(img, 14, 60, (0, 8)); W_, H_ = img.size

    def fr(t):
        if t > dur:
            return None
        e = pop(t / 0.35) * (1 + 0.03 * math.sin(t * 5)); a = min(1.0, t / 0.12) * (1.0 if t < dur - 0.3 else max(0.0, (dur - t) / 0.3))
        im2 = img.rotate(4 * math.sin(t * 4), resample=Image.BICUBIC)
        im2 = im2.resize((max(1, int(W_ * e)), max(1, int(H_ * e))), Image.LANCZOS)
        c = Image.new('RGBA', (int(W_ * 1.2), int(H_ * 1.2)), (0, 0, 0, 0))
        c.alpha_composite(im2, ((c.width - im2.width) // 2, (c.height - im2.height) // 2)); return com_alpha(c, a)
    return escrever(nome, fr, int(dur * FPS), (int(W_ * 1.2), int(H_ * 1.2))), pad + int(W_ * 0.1)


# ---------------------------------------------------------------- linha do tempo (nova, depois dos cortes)
sob = []
n1 = t_de('número')[0]; n2 = t_de('número', 5)[0]; n3 = t_de('número', n2 + 1)[0]
q4 = t_de('4')[0]; n5 = t_de('número', q4 + 1)[0]; cuid = t_de('cuidado', n5 + 20)[0]
com = t_de('comenta')[0]
secoes = [(n1, n2, 'nº 01|corte automático'), (n2, n3, 'nº 02|legenda palavra por palavra'), (n3, q4, 'nº 03|palavra em destaque'),
          (q4, n5, 'nº 04|efeito sonoro'), (n5, cuid, 'nº 05|zoom com intenção'), (cuid, com - 0.2, 'atenção|cara de IA')]
for j, (a, b, txt) in enumerate(secoes):
    arq, pad = animar_estatico(f'chip{j}', chip(txt), b - a, entra=0.3)
    sob.append({'arquivo': arq, 't0': round(a, 3), 'x': 196 - pad, 'y': 560 - pad})

# card do corte automático (acima da cabeça, enquanto ela explica)
c0 = t_de('corte', 1.5)[0]; c1 = n2 - 0.1
arq, pad = card_corte(c1 - c0)
sob.append({'arquivo': arq, 't0': round(c0, 3), 'x': (2160 - 1520) // 2 - pad, 'y': 720 - pad, 'som': 'click_mouse', 'vol': 0.6})

# corações no "queridinho"
qa = max(t_de('esse', q4)[0], t_de('sonoro', q4)[1] + 0.5); qb = t_de('queridinho')[1] + 0.9
sob.append({'arquivo': coracoes(qb - qa), 't0': round(qa, 3), 'x': 230, 'y': 760})

# robô no "cara de IA"
ra = t_de('cara', cuid)[0]
arq, pad = flutuante('robo', emoji('🤖', 300), 2.6); sob.append({'arquivo': arq, 't0': round(ra, 3), 'x': 1530 - pad, 'y': 1150 - pad})

# ícone do Claude quando ela fala "Claude"
ic = icone_sem_fundo(os.path.join(S, 'in', 'claude.jpg'), 250); ult = -9
for a, b, x in w:
    if x.strip('.,?!').lower() in ('claude', 'cloud') and a - ult > 4:
        arq, pad = flutuante(f'claude_{int(a)}', ic, 1.5); sob.append({'arquivo': arq, 't0': round(a, 3), 'x': 1560 - pad, 'y': 1180 - pad}); ult = a

# presente
pa = t_de('presentinho')[0]
arq, pad = flutuante('presente', emoji('🎁', 300), 2.0); sob.append({'arquivo': arq, 't0': round(pa, 3), 'x': 1520 - pad, 'y': 1850 - pad})

# ---------------------------------------------------------------- legendas especiais (ASS, coordenadas 4K)
def ts(t):
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'

extra = []; sem_leg = []
# palavra por palavra, onde a mão dela está (sem tarja)
pp = [x for x in w if t_de('palavras', n2)[0] - 0.01 <= x[0] <= t_de('palavras', n2, 2)[1] + 0.01]
for i, (a, b, x) in enumerate(pp):
    fimw = pp[i + 1][0] if i + 1 < len(pp) else b + 0.35
    extra.append(f'Dialogue: 5,{ts(a)},{ts(fimw)},Leg,,0,0,0,,{{\\an5\\pos(820,2700)\\fs150\\bord0\\shad6\\4c&H50000000&\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}}{x.strip(".,").upper()}')
sem_leg.append([pp[0][0] - 0.05, pp[-1][1] + 0.35])
# palavra grande manuscrita acima da cabeça
ga = t_de('destaque', n3)[0] - 0.45; gb = ga + 2.2
extra.append(f'Dialogue: 6,{ts(ga)},{ts(gb)},Destaque,,0,0,0,,{{\\an5\\pos(1180,850)\\fnKaushan Script\\fs300\\c&HA07FF5&\\bord6\\3c&HFFFFFF&\\shad5\\4c&H60000000&'
             f'\\fscx40\\fscy40\\t(0,180,\\fscx108\\fscy108)\\t(180,300,\\fscx100\\fscy100)\\fad(0,250)}}destaque')
# "edita" entre aspas, rosa
ea, eb = t_de('edita', com - 1); eb = ea + 1.4
extra.append(f'Dialogue: 6,{ts(ea)},{ts(eb)},Destaque,,0,0,0,,{{\\an5\\pos(1080,2250)\\fs280\\c&HA07FF5&\\bord5\\3c&HFFFFFF&\\shad4\\4c&H60000000&'
             f'\\fscx50\\fscy50\\t(0,160,\\fscx106\\fscy106)\\t(160,260,\\fscx100\\fscy100)\\fad(0,200)}}“edita”')
sem_leg.append([ea - 0.05, eb])

# ---------------------------------------------------------------- correções da transcrição
cor = []
for a, b, x in w:
    k = x.strip('.,?!'); suf = x[len(k):] if x.startswith(k) else ''
    if k.lower() == 'cloud': cor.append([a, x, 'Claude' + suf])
    if k.lower() == 'iá': cor.append([a, x, 'IA' + suf])
    if x == '4,': cor.append([a, x, 'número 4,'])

# ---------------------------------------------------------------- destaques amarelos e zoom
dest = [[t_de('corte')[0], t_de('automático')[1] + 0.05, 'corte automático'],
        [t_de('legendas')[0], t_de('legendas')[1] + 0.1, 'legendas'],
        [t_de('efeito', q4)[0], t_de('sonoro', q4)[1] + 0.05, 'efeito sonoro'],
        [t_de('efeito', n5)[0], t_de('zoom', n5)[1] + 0.25, 'efeito\\Nde zoom'],
        [t_de('cuidado', n5 + 20)[0], t_de('iá', n5 + 20)[1] + 0.2, 'cuidado com\\Na cara de IA']]
z0 = t_de('zoom', n5)[1]; zoom = [[round(z0 - 0.1, 3), round(z0 + 3.6, 3), 0.22]]
trans = [[round(t_de('sonoro', q4)[1] + 0.06, 3), 0.42]]

p = json.load(open(os.path.join(T, 'plano.json')))
p.update({'sobreposicoes': sob, 'ass_extra': extra, 'sem_legenda': sem_leg, 'correcoes': cor, 'destaques': dest,
          'zooms': zoom, 'fechar_abrir': trans})
json.dump(p, open(os.path.join(T, 'plano.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: p[k] for k in ('destaques', 'zooms', 'fechar_abrir', 'sem_legenda')}, ensure_ascii=False))
print(len(sob), 'sobreposições')
