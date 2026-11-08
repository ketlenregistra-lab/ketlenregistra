"""Motor de edição: legendas, combos tipográficos, cards gráficos, zooms e SFX.
Tudo em 1080x1920, respeitando a área segura do Reels."""
import os, math, subprocess, json, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SFX_GAIN = 0.55  # efeitos sempre por baixo da voz
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('EDIT_ROOT', os.getcwd())  # pasta do projeto de edição (src/, wav/, sfx/, out/)
FONTDIR = os.path.expanduser('~/.fonts')

# Identidade Julia Roque
BLUE = (11, 60, 158)
BLUE_D = (6, 38, 105)
RED = (227, 24, 35)
WHITE = (255, 255, 255)
CREAM = (240, 236, 231)
INK = (14, 30, 72)

# Área segura (grade do Reels): nada fora disso
SAFE = dict(x0=88, x1=995, y0=262, y1=1459, x1_low=928, y_low=1070)  # grade enviada pela Ketlen
SUB_Y = 1300          # centro das legendas (peito)
TOP_Y0, TOP_Y1 = 272, 630  # faixa da parede, acima da cabeça


@functools.lru_cache(None)
def font(fam, w=400, italic=False, size=40):
    f = {'ms': 'montserrat', 'pf': 'playfair-display'}[fam]
    return ImageFont.truetype(os.path.join(FONTDIR, f"{f}-latin-{w}-{'italic' if italic else 'normal'}.ttf"), size)


def ease(x):  # easeOutCubic
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def back(x):  # easeOutBack (pop)
    x = min(max(x, 0.0), 1.0)
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def text_w(fnt, s, track=0):
    if not s:
        return 0
    return fnt.getlength(s) + track * (len(s) - 1)


def draw_text(d, xy, s, fnt, fill, track=0, anchor='ls'):
    if track == 0:
        d.text(xy, s, font=fnt, fill=fill, anchor=anchor)
        return
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=fnt, fill=fill, anchor=anchor)
        x += fnt.getlength(ch) + track


def shadowed(img, radius=10, alpha=150, offset=(0, 4)):
    """Coloca sombra suave sob um sprite RGBA."""
    pad = radius * 3
    out = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 255)); sh.putalpha(a)
    out.paste(sh, (pad + offset[0], pad + offset[1]), sh)
    out = out.filter(ImageFilter.GaussianBlur(radius))
    out.alpha_composite(img, (pad, pad))
    return out, pad


# ---------------------------------------------------------------- Rich lines
# Uma "linha rica" é uma lista de runs: (texto, estilo) onde estilo é dict
# {fam, w, it, size, color, track, upper, hl(bg color)}

def run_metrics(text, st):
    f = font(st.get('fam', 'ms'), st.get('w', 600), st.get('it', False), st['size'])
    t = text.upper() if st.get('upper') else text
    return f, t, text_w(f, t, st.get('track', 0))


def render_line(runs, gap=None):
    """Renderiza uma linha de runs mistos numa sprite RGBA (baseline comum)."""
    parts = []
    asc_max = desc_max = 0
    total = 0
    for i, (txt, st) in enumerate(runs):
        f, t, w = run_metrics(txt, st)
        asc, desc = f.getmetrics()
        asc_max = max(asc_max, asc); desc_max = max(desc_max, desc)
        sp = 0 if i == 0 else (gap if gap is not None else font(st.get('fam', 'ms'), st.get('w', 600), st.get('it', False), st['size']).getlength(' '))
        parts.append((f, t, w, st, sp))
        total += w + sp
    pad = 18
    img = Image.new('RGBA', (int(total + pad * 2), asc_max + desc_max + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad; base = pad + asc_max
    for f, t, w, st, sp in parts:
        x += sp
        if st.get('hl'):
            a, _ = f.getmetrics()
            hpad = 10
            d.rounded_rectangle([x - hpad, base - a * 0.78 - 6, x + w + hpad, base + 12], radius=6, fill=st['hl'])
        draw_text(d, (x, base), t, f, st.get('color', WHITE), st.get('track', 0))
        x += w
    return img, base  # base = baseline y inside sprite


def stack(lines, align='c', lead=0):
    """Empilha sprites (img, base) verticalmente."""
    w = max(l[0].width for l in lines)
    h = sum(l[0].height for l in lines) + lead * (len(lines) - 1)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    y = 0
    for img, _ in lines:
        x = (w - img.width) // 2 if align == 'c' else 0
        out.alpha_composite(img, (x, y)); y += img.height + lead
    return out


# ---------------------------------------------------------------- Elements
class Elem:
    """Elemento de overlay com tempo de entrada/saída."""
    layer = 1
    behind = False  # True = camada atrás da pessoa

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def active(self, t):
        return self.t0 <= t < self.t1

    def draw(self, canvas, t):
        raise NotImplementedError


def paste_anim(canvas, spr, cx, cy, t, t0, t1, mode='up', dur=0.28, out=0.18, scale_from=0.85):
    """Cola sprite centrado em (cx,cy) com animação de entrada/saída."""
    p_in = ease((t - t0) / dur) if dur else 1
    p_out = 1 - ease_io((t - (t1 - out)) / out) if out else 1
    a = min(p_in, p_out)
    if a <= 0.001:
        return
    s = spr
    dx = dy = 0
    if mode == 'up':
        dy = (1 - p_in) * 40
    elif mode == 'pop':
        k = scale_from + (1 - scale_from) * back((t - t0) / dur)
        k = max(k, 0.05)
        if abs(k - 1) > 0.004:
            s = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))), Image.BILINEAR)
    elif mode == 'left':
        dx = -(1 - p_in) * 60
    if a < 0.999:
        s = s.copy(); al = s.split()[3].point(lambda v: int(v * a)); s.putalpha(al)
    canvas.alpha_composite(s, (int(cx - s.width / 2 + dx), int(cy - s.height / 2 + dy)))


# ---------- legendas palavra a palavra
SUB_STYLE = dict(fam='ms', w=600, size=52, color=WHITE)


class Subtitles(Elem):
    layer = 5

    def __init__(self, words, blocked, y=SUB_Y, maxw=760, maxwords=4):
        super().__init__(0, 1e9)
        self.y = y
        self.blocked = blocked  # lista de (t0,t1) sem legenda comum
        self.chunks = []
        cur = []
        words = [x for x in words if x['w'].strip()]
        for i, wd in enumerate(words):
            if any(a <= wd['s'] + 0.02 < b for a, b in blocked):
                if cur: self.chunks.append(cur); cur = []
                continue
            if cur:
                gap = wd['s'] - cur[-1]['e']
                txt = ' '.join(x['w'] for x in cur + [wd])
                f = font('ms', 600, False, SUB_STYLE['size'])
                if (len(cur) >= maxwords or gap > 0.45 or text_w(f, txt) > maxw
                        or cur[-1]['w'][-1:] in '.?!,:;'):
                    self.chunks.append(cur); cur = []
            cur.append(wd)
        if cur: self.chunks.append(cur)
        # janelas de exibição
        self.win = []
        for k, c in enumerate(self.chunks):
            s = c[0]['s']; e = c[-1]['e'] + 0.25
            if k + 1 < len(self.chunks):
                e = min(max(e, self.chunks[k + 1][0]['s'] - 0.02) if self.chunks[k + 1][0]['s'] - c[-1]['e'] < 0.6 else e,
                        self.chunks[k + 1][0]['s'] - 0.01)
            for a, b in blocked:  # nunca invadir um bloqueio
                if s < a < e: e = a
            self.win.append((s, e))
        self.cache = {}

    def sprite(self, k, n_on):
        key = (k, n_on)
        if key not in self.cache:
            runs = []
            for j, wd in enumerate(self.chunks[k]):
                st = dict(SUB_STYLE)
                if j >= n_on:
                    st['color'] = (255, 255, 255, 0)
                runs.append((wd['w'], st))
            img, _ = render_line(runs)
            # sombra discreta para leitura (sem caixa)
            sh, pad = shadowed(img, radius=8, alpha=170, offset=(0, 3))
            self.cache[key] = sh
        return self.cache[key]

    def draw(self, canvas, t):
        for k, (s, e) in enumerate(self.win):
            if s <= t < e:
                c = self.chunks[k]
                n_on = sum(1 for wd in c if wd['s'] <= t + 0.03)
                spr = self.sprite(k, max(1, n_on))
                # entrada leve do bloco
                p = ease((t - s) / 0.12)
                y = self.y + (1 - p) * 10
                a = p
                if a < 0.999:
                    spr = spr.copy(); spr.putalpha(spr.split()[3].point(lambda v: int(v * a)))
                canvas.alpha_composite(spr, (int(W / 2 - spr.width / 2), int(y - spr.height / 2)))
                return


# ---------- combinação tipográfica (2 fontes) sobre o vídeo
class Combo(Elem):
    """lines: lista de (t_aparece, runs). Fica centrado em cy."""
    layer = 6

    def __init__(self, t0, t1, lines, cy=SUB_Y, lead=-14, bg=None, shadow=True, maxw=800):
        super().__init__(t0, t1)
        self.lines = lines; self.cy = cy; self.lead = lead; self.shadow = shadow
        self.sprites = []
        for ln in lines:
            img, b = render_line(ln[1])
            if img.width > maxw:
                k = maxw / img.width
                img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
            self.sprites.append((img, b))
        tot = sum(s[0].height for s in self.sprites) + lead * (len(self.sprites) - 1)
        self.ys = []
        y = cy - tot / 2
        for s in self.sprites:
            self.ys.append(y + s[0].height / 2); y += s[0].height + lead
        if shadow:
            self.sprites = [(shadowed(s[0], 12, 160, (0, 4))[0], s[1]) for s in self.sprites]

    def draw(self, canvas, t):
        for k, (ln, (spr, _), y) in enumerate(zip(self.lines, self.sprites, self.ys)):
            ta = ln[0]
            opt = ln[2] if len(ln) > 2 else None
            if t < ta:
                continue
            if opt and 'type' in opt:
                # máquina de escrever: letras surgem uma a uma
                ts, te = opt['type']
                runs = ln[1]
                total = sum(len(r[0]) for r in runs)
                n = total if t >= te else int(total * max(0.0, (t - ts) / (te - ts))) + 1
                n = min(n, total)
                key = (k, n)
                cache = self.__dict__.setdefault('_tc', {})
                if key not in cache:
                    pr, left = [], n
                    for txt, st in runs:
                        if left <= 0: break
                        pr.append((txt[:left], st)); left -= len(txt)
                    img, _ = render_line(pr)
                    if self.shadow:
                        img = shadowed(img, 12, 160, (0, 4))[0]
                    cache[key] = img
                img = cache[key]
                x0 = W / 2 - spr.width / 2
                a = 1 - ease_io((t - (self.t1 - 0.18)) / 0.18)
                if a < 0.999:
                    img = img.copy(); img.putalpha(img.split()[3].point(lambda v: int(v * a)))
                canvas.alpha_composite(img, (int(x0), int(y - spr.height / 2)))
            else:
                paste_anim(canvas, spr, W / 2, y, t, ta, self.t1, mode='up', dur=0.3)


def type_keys(t0, t1, text, vol=0.35):
    """Lista de SFX de tecla, uma por caractere visível."""
    chars = [c for c in text if c != ' ']
    n = max(len(text), 1)
    out = []
    for i, c in enumerate(text):
        if c == ' ':
            continue
        out.append((t0 + (t1 - t0) * i / n, 'key', vol))
    return out


# ---------- tela preta com foco no texto
class BlackCard(Elem):
    layer = 0  # substitui o vídeo

    def __init__(self, t0, t1, lines, color=(0, 0, 0), lead=-10, cy=None):
        super().__init__(t0, t1)
        self.color = color
        self.combo = Combo(t0, t1, lines, cy=cy or 900, lead=lead, shadow=False)

    def draw(self, canvas, t):
        # fade rápido de/para preto
        a = min(ease((t - self.t0) / 0.12), 1 - ease_io((t - (self.t1 - 0.1)) / 0.1))
        if a > 0:
            ov = Image.new('RGBA', (W, H), self.color + (int(255 * a),))
            canvas.alpha_composite(ov)
        self.combo.draw(canvas, t)


# ---------- cards gráficos (faixa da parede, acima da cabeça)
def card_base(w, h, fill=BLUE, radius=30, tag=True):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill)
    if tag:
        f = font('ms', 700, False, 17)
        s1, s2 = 'JULIA ROQUE', ' // CONTADORA'
        tw = text_w(f, s1, 2) + text_w(f, s2, 2)
        x = (w - tw) / 2
        draw_text(d, (x, 40), s1, f, (255, 120, 120) if fill != WHITE else RED, 2)
        draw_text(d, (x + text_w(f, s1, 2) + 2, 40), s2, f, (205, 215, 240) if fill != WHITE else BLUE, 2)
    return img, d


MAXH = 350  # altura máxima de card no topo: nunca desce até a cabeça


MAXH_BIG = 540  # calendários/ilustrações atrás dela podem ser maiores


def is_top(img, cy):
    return cy - img.height / 2 < 360


def fit_top(img, cy, maxh=MAXH):
    """Se o card está ancorado no topo e é alto demais, reduz mantendo o topo em 272."""
    if cy - img.height / 2 < 300 and img.height > maxh:
        k = maxh / img.height
        img = img.resize((int(img.width * k), maxh), Image.LANCZOS)
        cy = TOP_Y0 + maxh / 2
    return img, cy


class Sprite(Elem):
    """Sprite estático com animação de entrada (pop/up)."""
    layer = 3

    def __init__(self, t0, t1, img, cx, cy, mode='pop', shadow=True, big=False, behind=None):
        super().__init__(t0, t1)
        if big and is_top(img, cy):
            k = min(MAXH_BIG / img.height, 1.35, (SAFE['x1'] - SAFE['x0'] - 20) / img.width)
            img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
            cy = TOP_Y0 + img.height / 2
        self.behind = (big and is_top(img, cy)) if behind is None else behind
        img, cy = fit_top(img, cy, MAXH_BIG if big else MAXH)
        self.img = shadowed(img, 16, 120, (0, 8))[0] if shadow else img
        self.cx, self.cy, self.mode = cx, cy, mode

    def draw(self, canvas, t):
        paste_anim(canvas, self.img, self.cx, self.cy, t, self.t0, self.t1, mode=self.mode, dur=0.35)


class Dynamic(Elem):
    """Card cujo conteúdo muda no tempo: fn(t_rel) -> RGBA (cacheado por estado)."""
    layer = 3

    def __init__(self, t0, t1, fn, cx, cy, mode='pop', qstep=1 / 30, big=False, behind=None, hint_h=None, maxh=None):
        super().__init__(t0, t1)
        self.fn, self.cx, self.cy, self.mode, self.q = fn, cx, cy, mode, qstep
        self.big = big
        self.maxh = maxh or (MAXH_BIG if big else MAXH)
        self.behind = (big and is_top(fn(0.0), cy)) if behind is None else behind
        self.cache = {}

    def draw(self, canvas, t):
        tr = round((t - self.t0) / self.q) * self.q
        key = round(tr, 3)
        if key not in self.cache:
            img = self.fn(tr)
            if self.big and is_top(img, self.cy):
                k = min(self.maxh / img.height, (SAFE['x1'] - SAFE['x0'] - 20) / img.width)
                img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
            img, self.cy_fit = fit_top(img, self.cy, self.maxh)
            self.cache = {key: shadowed(img, 16, 120, (0, 8))[0]}
        paste_anim(canvas, self.cache[key], self.cx, self.cy_fit, t, self.t0, self.t1, mode=self.mode, dur=0.35)


def wrap(text, fnt, maxw):
    out, cur = [], ''
    for w in text.split():
        trial = (cur + ' ' + w).strip()
        if fnt.getlength(trial) <= maxw:
            cur = trial
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def check_icon(d, cx, cy, r, p, color=RED, ring=WHITE):
    """Círculo + check desenhado progressivamente (p 0..1)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring, width=4)
    if p <= 0:
        return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    pts = [(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)]
    seg1 = min(p * 2, 1); seg2 = max(0, p * 2 - 1)
    a, b, c = pts
    m1 = (a[0] + (b[0] - a[0]) * seg1, a[1] + (b[1] - a[1]) * seg1)
    d.line([a, m1], fill=WHITE, width=7)
    if seg2 > 0:
        m2 = (b[0] + (c[0] - b[0]) * seg2, b[1] + (c[1] - b[1]) * seg2)
        d.line([b, m2], fill=WHITE, width=7)


def checklist_fn(title, items, times, t0, w=860, title_it=None, numbered=False, row=62):
    """Card de checklist: itens aparecem/checam nos tempos absolutos `times`."""
    rel = [x - t0 for x in times]
    fT = font('pf', 600, False, 50); fTi = font('pf', 500, True, 50)
    fI = font('ms', 600, False, 33)
    h = 112 + row * len(items) + 30

    def fn(tr):
        img, d = card_base(w, h)
        # título com 2 fontes
        runs = [(title, dict(fam='pf', w=600, size=50, color=WHITE))]
        if title_it:
            runs.append((title_it, dict(fam='pf', w=500, it=True, size=50, color=WHITE)))
        ln, _ = render_line(runs)
        img.alpha_composite(ln, ((w - ln.width) // 2, 44))
        y = 128
        for k, (it, r) in enumerate(zip(items, rel)):
            vis = ease((tr - r + 0.6) / 0.25) if numbered is False else ease((tr - r + 0.6) / 0.25)
            on = tr >= r
            p = ease((tr - r) / 0.25) if on else 0
            alpha = 255 if tr >= r - 0.6 else 90
            cy = y + k * row + row // 2
            check_icon(d, 74, cy, 21, p)
            col = WHITE if on else (190, 202, 232)
            label = f"{k + 1}. {it}" if numbered else it
            d.text((116, cy + 12), label, font=fI, fill=col, anchor='ls')
            if on and p >= 1 and False:
                pass
        return img
    return fn, h


def bars_fn(title, labels, values, t0, w=860, colors=None, unit='', subtitle=None, show_vals=None):
    fT = font('pf', 600, False, 46)
    fL = font('ms', 600, False, 24)
    fV = font('ms', 800, False, 28)
    h = 380
    vmax = max(values)
    colors = colors or [WHITE] * len(values)

    def fn(tr):
        img, d = card_base(w, h)
        d.text((w / 2, 104), title, font=fT, fill=WHITE, anchor='ms')
        if subtitle:
            d.text((w / 2, 140), subtitle, font=font('ms', 500, False, 22), fill=(200, 210, 238), anchor='ms')
        n = len(values); bw = 120; gap = (w - 120 - n * bw) / max(n - 1, 1)
        base = h - 62; top = 175
        d.line([(50, base), (w - 50, base)], fill=(150, 170, 220), width=2)
        for k, (lab, v, c) in enumerate(zip(labels, values, colors)):
            p = ease((tr - 0.25 - k * 0.22) / 0.55)
            x = 60 + k * (bw + gap)
            bh = (base - top) * (v / vmax) * p
            if bh > 1:
                d.rounded_rectangle([x, base - bh, x + bw, base], radius=10, fill=c)
            d.text((x + bw / 2, base + 34), lab, font=fL, fill=WHITE, anchor='ms')
            if p > 0.6 and show_vals:
                d.text((x + bw / 2, base - bh - 12), show_vals[k], font=fV, fill=WHITE, anchor='ms')
        return img
    return fn, h


MESES = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']


def calendar_fn(year, month, marks, t0, w=600, note=None, subtitle=None, ch=50, label=None):
    """marks: lista de (dia, t_abs, rótulo_curto). Desenha círculo vermelho animado."""
    import calendar as cal
    weeks = cal.Calendar(firstweekday=6).monthdayscalendar(year, month)
    fM = font('pf', 600, False, 46); fD = font('ms', 600, False, 26); fW = font('ms', 700, False, 17)
    cw = (w - 60) / 7
    off = 46 if note else 0
    h = 168 + off + ch * len(weeks) + 22

    def fn(tr):
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=28, fill=WHITE)
        d.rounded_rectangle([0, 0, w - 1, 96], radius=28, fill=BLUE)
        d.rectangle([0, 60, w - 1, 96], fill=BLUE)
        title = label or f"{MESES[month - 1].capitalize()}"
        ln, _ = render_line([(title, dict(fam='pf', w=600, size=44, color=WHITE)), (str(year), dict(fam='pf', w=500, it=True, size=44, color=(255, 170, 170)))])
        img.alpha_composite(ln, ((w - ln.width) // 2, 8))
        for k, wd in enumerate('DSTQQSS'):
            d.text((30 + cw * k + cw / 2, 136 + off), wd, font=fW, fill=BLUE if k not in (0,) else RED, anchor='ms')
        for r, wk in enumerate(weeks):
            for k, day in enumerate(wk):
                if not day: continue
                cx = 30 + cw * k + cw / 2; cy = 168 + off + r * ch + ch / 2 - 6
                mk = [m for m in marks if m[0] == day]
                col = INK
                if mk:
                    p = ease((tr - (mk[0][1] - t0)) / 0.45)
                    if p > 0:
                        rr = 23
                        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(RED[0], RED[1], RED[2], int(255 * min(1, p * 1.5))))
                        col = WHITE
                d.text((cx, cy + 9), str(day), font=fD, fill=col, anchor='ms')
        if note:
            d.text((w / 2, 134), note.upper(), font=font('ms', 800, False, 22), fill=RED, anchor='ms')
        return img
    return fn, h


def calculator_img(display='0,00', w=300):
    h = int(w * 1.42)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=BLUE_D)
    d.rounded_rectangle([22, 24, w - 22, 112], radius=16, fill=(226, 232, 245))
    f = font('ms', 700, False, 46)
    d.text((w - 40, 90), display, font=f, fill=INK, anchor='rs')
    keys = ['7', '8', '9', '÷', '4', '5', '6', '×', '1', '2', '3', '−', '0', ',', '=', '+']
    kw = (w - 44 - 3 * 12) / 4; kh = (h - 140 - 22 - 3 * 12) / 4
    fk = font('ms', 700, False, 30)
    for i, k in enumerate(keys):
        r, c = divmod(i, 4)
        x = 22 + c * (kw + 12); y = 132 + r * (kh + 12)
        fill = RED if k in '=' else (WHITE if k.isdigit() or k == ',' else (64, 104, 196))
        d.rounded_rectangle([x, y, x + kw, y + kh], radius=14, fill=fill)
        d.text((x + kw / 2, y + kh / 2 + 11), k, font=fk, fill=INK if fill == WHITE else WHITE, anchor='ms')
    return img


def question_box_img(label, text, w=820, nchars=None):
    """Caixinha de pergunta (estilo sticker de perguntas), sem emoji."""
    fQ = font('pf', 600, False, 52); fQi = font('pf', 500, True, 52)
    lines = wrap(text, fQ, w - 90)
    h = 116 + 66 * len(lines) + 30
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=34, fill=WHITE)
    d.rounded_rectangle([0, 0, w - 1, 92], radius=34, fill=BLUE)
    d.rectangle([0, 50, w - 1, 92], fill=BLUE)
    f = font('ms', 800, False, 26)
    draw_text(d, ((w - text_w(f, label, 5)) / 2, 60), label, f, WHITE, 5)
    y = 160
    left = 10 ** 6 if nchars is None else nchars
    for ln in lines:
        x0 = w / 2 - fQ.getlength(ln) / 2
        part = ln[:max(left, 0)]
        if part:
            d.text((x0, y), part, font=fQ, fill=INK, anchor='ls')
        if nchars is not None and 0 <= left < len(ln):
            cx = x0 + fQ.getlength(part) + 4
            d.rectangle([cx, y - 44, cx + 4, y + 6], fill=BLUE)  # cursor
        left -= len(ln) + 1
        y += 66
    return img


def comment_img(user, text, w=820):
    fU = font('ms', 700, False, 32); fT = font('ms', 500, False, 40)
    lines = wrap(text, fT, w - 200)
    h = 74 + 54 * len(lines) + 74
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill=WHITE)
    d.ellipse([30, 34, 100, 104], fill=BLUE)
    d.text((65, 81), user[0].upper(), font=font('pf', 600, False, 36), fill=WHITE, anchor='ms')
    d.text((124, 62), user, font=fU, fill=INK, anchor='ls')
    d.text((124 + fU.getlength(user) + 14, 62), 'agora', font=font('ms', 500, False, 22), fill=(140, 150, 170), anchor='ls')
    y = 118
    for ln in lines:
        d.text((124, y), ln, font=fT, fill=INK, anchor='ls'); y += 54
    d.text((124, y + 6), 'Responder', font=font('ms', 600, False, 22), fill=(140, 150, 170), anchor='ls')
    # coração desenhado (contorno)
    hx, hy, s = w - 60, 78, 15
    d.ellipse([hx - s, hy - s, hx, hy], outline=RED, width=4)
    d.ellipse([hx, hy - s, hx + s, hy], outline=RED, width=4)
    d.polygon([(hx - s - 1, hy - s / 2 + 2), (hx + s + 1, hy - s / 2 + 2), (hx, hy + s + 4)], fill=WHITE)
    d.line([(hx - s, hy - s / 2 + 3), (hx, hy + s + 3), (hx + s, hy - s / 2 + 3)], fill=RED, width=4)
    return img


def tax_img(w=300, label='IMPOSTO'):
    """Guia/boleto com % (símbolo de imposto)."""
    h = 340
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    # papel com borda serrilhada embaixo
    pts = [(0, 18), (18, 0), (w - 18, 0), (w, 18), (w, h - 24)]
    zz = 12; x = w
    while x > 0:
        pts += [(x, h - 24), (x - zz / 2, h - 8)]; x -= zz
    pts += [(0, h - 24)]
    d.polygon(pts, fill=WHITE)
    d.rectangle([0, 0, w, 66], fill=RED)
    f = font('ms', 800, False, 26)
    draw_text(d, ((w - text_w(f, label, 4)) / 2, 45), label, f, WHITE, 4)
    d.text((w / 2, 200), '%', font=font('pf', 700, False, 140), fill=BLUE, anchor='ms')
    for i, yy in enumerate([232, 256, 280]):
        d.rounded_rectangle([40, yy, w - 40 - i * 40, yy + 10], radius=5, fill=(205, 212, 230))
    return img


def steps_fn(items, times, t0, w=880, arrows=True, gapx=50, last_red=True):
    """Linha do tempo em pílulas (recepção → ... ). Itens aparecem nos tempos."""
    f = font('ms', 700, False, 34)
    rows = []
    # distribui em linhas de até w
    cur, cw = [], 0
    for i, it in enumerate(items):
        iw = text_w(f, it.upper(), 2) + 56
        if cur and cw + iw + gapx > w - 40:
            rows.append(cur); cur, cw = [], 0
        cur.append((i, it, iw)); cw += iw + (gapx if cw else 0)
    rows.append(cur)
    h = 40 + len(rows) * 100

    def fn(tr):
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        for r, row in enumerate(rows):
            tot = sum(x[2] for x in row) + gapx * (len(row) - 1)
            x = (w - tot) / 2; y = 30 + r * 100
            for j, (i, it, iw) in enumerate(row):
                p = ease((tr - (times[i] - t0)) / 0.3)
                if p > 0:
                    a = int(255 * p)
                    last = last_red and i == len(items) - 1
                    d.rounded_rectangle([x, y + (1 - p) * 20, x + iw, y + 72 + (1 - p) * 20], radius=36, fill=(RED if last else BLUE) + (a,))
                    draw_text(d, (x + 28, y + 49 + (1 - p) * 20), it.upper(), f, (255, 255, 255, a), 2)
                    if j > 0 or r > 0:
                        pass
                if arrows and j < len(row) - 1:
                    p2 = ease((tr - (times[i + 1] - t0)) / 0.3)
                    if p2 > 0:
                        ax = x + iw + 8
                        d.line([(ax, y + 36), (ax + 34 * p2, y + 36)], fill=WHITE, width=4)
                        if p2 > 0.9:
                            d.polygon([(ax + 34, y + 28), (ax + 44, y + 36), (ax + 34, y + 44)], fill=WHITE)
                x += iw + gapx
        return img
    return fn, h


# ---------------------------------------------------------------- Zoom
class Zooms:
    """Lista de (t0, t1, escala, centro_y, kind). kind: 'smooth' | 'punch'."""

    def __init__(self, segs):
        self.segs = segs

    def at(self, t):
        """Retorna (escala, foco). Zooms suaves entram/saem em 0.3s; 'punch' é corte seco;
        'slow' cresce devagar durante o trecho."""
        for t0, t1, sc, cy, kind in self.segs:
            if t0 <= t < t1:
                if kind == 'punch':
                    p = 1.0
                elif kind == 'slow':
                    p = ease_io((t - t0) / (t1 - t0))
                else:
                    p = min(ease((t - t0) / 0.3), 1 - ease_io((t - (t1 - 0.3)) / 0.3))
                return 1 + (sc - 1) * p, cy
        return 1.0, 860


# ---------------------------------------------------------------- Render
def render(name, src, elems, zooms, sfx, out, dur=None, preview=None, music=None):
    """Lê vídeo, aplica zoom + overlays, mixa SFX. preview=(t0,t1) para teste."""
    t_start = preview[0] if preview else 0
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', src]))
    total = float(probe['format']['duration'])
    t_end = preview[1] if preview else total
    nfr = int(round((t_end - t_start) * FPS))
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(t_start), '-t', str(t_end - t_start), '-i', src,
                            '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                           stdout=subprocess.PIPE)
    tmpv = out + '.v.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium' if not preview else 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p',
                            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', tmpv], stdin=subprocess.PIPE)
    elems = sorted(elems, key=lambda e: e.layer)
    fb = W * H * 3
    for i in range(nfr):
        raw = dec.stdout.read(fb)
        if len(raw) < fb:
            break
        t = t_start + i / FPS
        fr = Image.frombuffer('RGB', (W, H), raw)
        s, cy = zooms.at(t)
        if s > 1.001:
            cw, ch = W / s, H / s
            y0 = 0.0 if cy == 'top' else min(max(cy - ch * (cy / H), 0), H - ch)
            x0 = (W - cw) / 2
            fr = fr.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        canvas = fr.convert('RGBA')
        act = [e for e in elems if e.active(t)]
        if any(e.behind for e in act) and not any(isinstance(e, BlackCard) for e in act):
            from matte import matte
            for e in act:
                if e.behind:
                    e.draw(canvas, t)
            person = canvas.copy() if False else fr.convert('RGBA')
            person.putalpha(matte(fr))
            canvas.alpha_composite(person)
            for e in act:
                if not e.behind:
                    e.draw(canvas, t)
        else:
            for e in act:
                e.draw(canvas, t)
        enc.stdin.write(canvas.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    # áudio: original + SFX
    inputs = ['-ss', str(t_start), '-t', str(t_end - t_start), '-i', src]
    filt = ['[0:a]aresample=48000,volume=1.0[a0]']
    labels = ['[a0]']
    k = 1
    for (t, name_, vol) in sfx:
        if not (t_start <= t < t_end):
            continue
        inputs += ['-i', os.path.join(ROOT, 'sfx', name_ + '.wav')]
        ms = int((t - t_start) * 1000)
        filt.append(f'[{k}:a]aresample=48000,volume={vol * SFX_GAIN:.3f},adelay={ms}|{ms}[s{k}]')
        labels.append(f'[s{k}]'); k += 1
    filt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.95[aout]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-i', tmpv, '-filter_complex', ';'.join(filt),
                    '-map', f'{k}:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', out], check=True)
    os.remove(tmpv)


# ---------------------------------------------------------------- helpers de roteiro
import re, unicodedata


def _norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9%º]', '', s)


def load_words(i):
    return json.load(open(os.path.join(ROOT, 'wav', f'v{i}.json')))


def find(words, phrase, after=0.0):
    """Tempo (início, fim) da primeira ocorrência de `phrase` depois de `after`."""
    target = [_norm(x) for x in phrase.split() if _norm(x)]
    nw = [_norm(w['w']) for w in words]
    for i in range(len(words)):
        if words[i]['s'] < after - 0.01:
            continue
        if nw[i:i + len(target)] == target:
            return words[i]['s'], words[i + len(target) - 1]['e']
    raise KeyError(f'não achei: {phrase!r} depois de {after}')


def fix_words(words, repl):
    """Corrige palavras transcritas: repl = {('antiga', aprox_t): 'nova'} ou {'antiga': 'nova'}."""
    for w in words:
        k = w['w']
        if k in repl:
            w['w'] = repl[k]
    return words


def M(txt, size=40, w=700, track=3, color=WHITE, upper=True, **kw):
    return (txt, dict(fam='ms', w=w, size=size, track=track, color=color, upper=upper, **kw))


def P(txt, size=96, it=False, w=None, color=WHITE, **kw):
    return (txt, dict(fam='pf', w=w or (500 if it else 600), it=it, size=size, color=color, **kw))


def input_bar_img(w=820, text='Adicione um comentário...'):
    h = 120
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=60, fill=WHITE)
    d.ellipse([22, 22, 98, 98], fill=BLUE)
    d.text((60, 74), 'J', font=font('pf', 600, False, 42), fill=WHITE, anchor='ms')
    d.text((124, 74), text, font=font('ms', 500, False, 34), fill=(120, 130, 150), anchor='ls')
    d.text((w - 40, 74), 'Publicar', font=font('ms', 700, False, 30), fill=BLUE, anchor='rs')
    return img


def tag_list_fn(title, items, times, t0, tag='URGENTE', w=860, title_it=None):
    """Lista que empilha itens, cada um com etiqueta vermelha."""
    fI = font('ms', 700, False, 36); fG = font('ms', 800, False, 20)
    row = 64
    h = 124 + row * len(items) + 20

    def fn(tr):
        img, d = card_base(w, h)
        runs = [(title, dict(fam='pf', w=600, size=50, color=WHITE))]
        if title_it:
            runs.append((title_it, dict(fam='pf', w=500, it=True, size=50, color=(255, 170, 170))))
        ln, _ = render_line(runs)
        img.alpha_composite(ln, ((w - ln.width) // 2, 44))
        for k, (it, r) in enumerate(zip(items, times)):
            p = ease((tr - (r - t0)) / 0.25)
            if p <= 0:
                continue
            a = int(255 * p); y = 136 + k * row + (1 - p) * 16
            d.text((70, y + 36), it.upper(), font=fI, fill=(255, 255, 255, a), anchor='ls')
            tw = text_w(fG, tag, 3) + 30; x = w - 70 - tw
            d.rounded_rectangle([x, y + 6, x + tw, y + 46], radius=8, fill=RED + (a,))
            draw_text(d, (x + 15, y + 34), tag, fG, (255, 255, 255, a), 3)
        return img
    return fn, h


def stats_fn(stats, t0, w=860, title=None, tag=True):
    """stats: lista de (valor_num, prefixo, sufixo, rótulo, t_abs). Conta de 0 até o valor."""
    h = (300 if not title else 360) - (0 if tag else 46)
    n = len(stats)

    def fn(tr):
        img, d = card_base(w, h, tag=tag)
        y0 = 70 if tag else 24
        if title:
            d.text((w / 2, 112), title, font=font('pf', 600, False, 46), fill=WHITE, anchor='ms'); y0 = 130
        colw = w / n
        for k, (val, pre, suf, lab, ta) in enumerate(stats):
            p = ease((tr - (ta - t0)) / 0.9)
            if tr < ta - t0 - 0.0:
                p = 0
            cx = colw * k + colw / 2
            v = val * p
            s = f"{pre}{int(round(v)):,}{suf}".replace(',', '.')
            full = f"{pre}{val:,}{suf}".replace(',', '.')
            sz = 110
            while text_w(font('pf', 700, False, sz), full) > colw - 50 and sz > 50:
                sz -= 4
            ln, _ = render_line([(s, dict(fam='pf', w=700, size=sz, color=WHITE if k % 2 == 0 else (255, 150, 150)))])
            img.alpha_composite(ln, (int(cx - ln.width / 2), y0))
            for j, part in enumerate(wrap(lab, font('ms', 600, False, 28), colw - 40)):
                d.text((cx, y0 + 175 + j * 36), part.upper(), font=font('ms', 700, False, 24), fill=(205, 215, 240), anchor='ms')
            if k > 0:
                d.line([(colw * k, y0 + 30), (colw * k, h - 40)], fill=(80, 110, 190), width=2)
        return img
    return fn, h


def provision_fn(t0, t_fill0, t_fill1, t_pay, w=860):
    """12 barras iguais (1/12 por mês) que vão se acumulando; pagamento no fim."""
    h = 380
    labs = 'JFMAMJJASOND'

    def fn(tr):
        img, d = card_base(w, h)
        ln, _ = render_line([('Provisão do', dict(fam='pf', w=600, size=48, color=WHITE)), ('13º', dict(fam='pf', w=500, it=True, size=48, color=(255, 160, 160)))])
        img.alpha_composite(ln, ((w - ln.width) // 2, 44))
        d.text((w / 2, 160), '1/12 DO 13º VIRA CUSTO TODO MÊS', font=font('ms', 700, False, 21), fill=(205, 215, 240), anchor='ms')
        base = h - 62; bw = 46; gap = (w - 100 - 12 * bw) / 11
        span = (t_fill1 - t_fill0)
        for k in range(12):
            p = ease((tr - (t_fill0 - t0) - k * span / 12) / 0.3)
            x = 50 + k * (bw + gap)
            hh = 120 * p
            if hh > 1:
                d.rounded_rectangle([x, base - hh, x + bw, base], radius=8, fill=WHITE)
            d.text((x + bw / 2, base + 32), labs[k], font=font('ms', 700, False, 22), fill=WHITE, anchor='ms')
        pp = ease((tr - (t_pay - t0)) / 0.35)
        if pp > 0:
            x = 50 + 10 * (bw + gap) - 8; x2 = 50 + 11 * (bw + gap) + bw + 8
            d.rounded_rectangle([x, base - 170, x2, base + 4], radius=12, outline=RED + (int(255 * pp),), width=5)
            d.rounded_rectangle([x - 14, base - 214, x2 + 14, base - 176], radius=10, fill=RED + (int(255 * pp),))
            draw_text(d, (x - 2, base - 186), 'PAGAMENTO', font('ms', 800, False, 18), (255, 255, 255, int(255 * pp)), 2)
        return img
    return fn, h


def bigline_card(runs_lines, w=860, pad=60, tag=True, top=66):
    """Card azul com linhas ricas centralizadas (para números/regras)."""
    sprites = [render_line(r) for r in runs_lines]
    hh = sum(s[0].height for s in sprites) - 18 * (len(sprites) - 1)
    h = hh + pad + top + 4
    img, d = card_base(w, h, tag=tag)
    y = top
    for s, _ in sprites:
        img.alpha_composite(s, ((w - s.width) // 2, int(y))); y += s.height - 18
    return img


def main(num, fname, E, Z, S):
    import sys
    pv = tuple(map(float, sys.argv[1:3])) if len(sys.argv) > 2 else None
    out = os.path.join(ROOT, 'out', fname if not pv else f'preview_v{num}.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render(f'v{num}', os.path.join(ROOT, 'src', f'v{num}.mov'), E, Zooms(Z), S, out, preview=pv)
    print(out)
