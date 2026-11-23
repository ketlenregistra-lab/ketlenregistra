"""Motor de edição de Reels no padrão Kathileenn Bahia (lote de novembro, revisão 2).

Cada vídeo descreve, num `build.py` curto, o que entra; `build(cfg)` monta o ASS e chama o ffmpeg.
Regras da Ketlen embutidas aqui:
- legenda e destaques aparecem **conforme ela fala** (palavra por palavra, nunca antes);
- maiúsculas como na fala (início de frase, nomes) e destaques sempre com inicial maiúscula;
- efeitos sonoros baixinhos, de fundo, e **nunca dois sons colados** (o teclado acompanha as letras);
- tudo dentro da guia do Instagram: x 88-994, y 263-1459; abaixo de y 1070 o limite direito é 927;
- vídeo HDR (iPhone) é convertido para cor normal sem mudar o tratamento dela.
"""
import json, math, os, subprocess, sys, unicodedata
import numpy as np

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "..", "fonts3")
SFX = os.path.join(AQUI, "..", "work", "sfx")
ROXO = "&H00BF227F"        # #7F22BF
ROXO_RGB = (127, 34, 191)
BRANCO = "&H00FFFFFF"
CAIXA_CLARA = "&H10F4F0F2"
VOL = {"swish_capcut": 0.14, "clique_caneta": 0.18, "tecla": 0.20, "teclado": 0.14, "fecha_tela": 0.30, "riser": 0.22}
MANTER = {"R", "S", "X", "Z", "WhatsApp", "BERA", "PEATE", "UTI"}

# ---------------------------------------------------------------- utilidades
def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalnum() and unicodedata.category(c) != "Mn")

def carregar_palavras(path, fixes=None, cortar_depois=None):
    words = []
    for s in json.load(open(path)):
        for w in s["words"]:
            words.append([w["w"].strip(), w["s"], w["e"]])
    out = []
    for t, s, e in words:
        if cortar_depois is not None and s >= cortar_depois:
            continue
        if t.startswith("-") and out:
            out[-1] = [out[-1][0] + t, out[-1][1], e]
            continue
        out.append([t, s, e])
    fixes = fixes or {}
    res = []
    for t, s, e in out:
        t = fixes.get((round(s, 2), t), fixes.get(t, t))
        if t:
            res.append([t, s, e])
    return res

def limpa(t):
    return t.strip(".,;:…")

def tempos(words, frase, perto, janela=3.0):
    """Início de cada palavra de `frase` na fala, procurando perto do tempo `perto`."""
    alvo = [norm(x) for x in frase.replace("·", " ").replace("\\N", " ").split() if norm(x)]
    cand = [i for i, w in enumerate(words) if abs(w[1] - perto) <= janela and norm(w[0]) == alvo[0]]
    for i in sorted(cand, key=lambda i: abs(words[i][1] - perto)):
        res, j = [], i
        for a in alvo:
            while j < len(words) and j < i + len(alvo) + 4 and norm(words[j][0]) != a:
                j += 1
            if j >= len(words) or j >= i + len(alvo) + 4:
                break
            res.append(words[j][1]); j += 1
        if len(res) == len(alvo):
            return res
    # sem casamento: distribui a partir de `perto`
    return [perto + 0.3 * k for k in range(len(alvo))]

def fim_fala(words, t):
    """Fim da última palavra dita até o tempo t."""
    return max([w[2] for w in words if w[1] <= t] or [t])

# ---------------------------------------------------------------- estilos
def estilos(leg_font, leg_fs):
    return f"""Style: Leg,{leg_font},{leg_fs},{BRANCO},&H000000FF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,0,2,2,153,153,0,1
Style: Big,KB Poppins Bold,112,{BRANCO},&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Box,KB Poppins Bold,74,{BRANCO},&H000000FF,{ROXO},{ROXO},0,0,0,0,100,100,0,0,3,4,0,5,40,40,0,1
Style: Desenho,Arial,20,{ROXO},&H000000FF,{ROXO},&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"""

SP = {"Leg": -2, "Big": -3, "Box": -2, "Desenho": 0}

def ass_doc(evs, leg_font, leg_fs):
    def junta(line):
        st = line.split(",")[3]
        head, txt = line.split(",,0,0,0,,", 1)
        tag = f"\\fsp{SP.get(st, 0)}"
        txt = "{" + tag + txt[1:] if txt.startswith("{") else "{" + tag + "}" + txt
        return head + ",,0,0,0,," + txt
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{estilos(leg_font, leg_fs)}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(junta(l) for l in evs) + "\n"

POP = "\\fscx80\\fscy80\\t(0,120,\\fscx100\\fscy100)"
SOMBRA = "\\shad3\\4c&H000000&\\4a&H80&"

def cor_tags(estilo):
    """notif: letra branca em caixinha roxa · claro: letra roxa em caixa branca · texto puro: cor."""
    if estilo == "notif":
        return "Box", f"\\1c{BRANCO}\\3c{ROXO}\\4c{ROXO}\\xbord24\\ybord8"
    if estilo == "claro":
        return "Box", f"\\1c{ROXO}\\3c{CAIXA_CLARA}\\4c{CAIXA_CLARA}\\xbord24\\ybord8"
    return "Big", f"\\1c{estilo}{SOMBRA}"

# ---------------------------------------------------------------- destaque que aparece conforme a fala
def ev_fala(t_palavras, t1, txt, x, y, estilo=ROXO, fs=100, fonte=None, an=5, pop=True):
    """Texto (pode ter \\N) cujas palavras surgem nos tempos `t_palavras`; as que faltam ficam invisíveis."""
    st, tags = cor_tags(estilo)
    f = f"\\fn{fonte}" if fonte else ""
    tokens = txt.replace("\\N", " \\N ").split(" ")
    palavras = [k for k, tk in enumerate(tokens) if tk and tk != "\\N"]
    assert len(palavras) == len(t_palavras), (txt, len(palavras), len(t_palavras))
    evs = []
    for n, k in enumerate(palavras):
        a = t_palavras[n]
        b = t_palavras[n + 1] if n + 1 < len(palavras) else t1
        if b <= a:
            continue
        vis = " ".join(tokens[:k + 1]).replace(" \\N ", "\\N")
        resto = " ".join(tokens[k + 1:]).replace(" \\N ", "\\N").replace("\\N ", "\\N")
        sep = "" if not resto else (" " if not tokens[k + 1] == "\\N" else "")
        p = POP if (pop and n == 0) else ""
        inv = "{\\alpha&HFF&}" + sep + resto if resto else ""
        if st == "Box":
            inv = ""          # caixinha cresce centralizada junto com as palavras
        evs.append(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{{\\an{an}\\pos({x},{y}){tags}\\fs{fs}{f}{p}}}{vis}{inv}")
    return evs

def ev_digitando(t0, t1, txt, x, y, estilo=BRANCO, fs=86, fonte=None, cps=16):
    """Texto digitando letra a letra (centralizado; letras que faltam ficam invisíveis).
    Devolve (eventos, tempos das teclas) — cada letra ganha um toque de teclado bem baixinho."""
    st, tags = cor_tags(estilo)
    f = f"\\fn{fonte}" if fonte else ""
    letras = [k for k, c in enumerate(txt) if c not in " " and not (c == "N" and k > 0 and txt[k - 1] == "\\") and c != "\\"]
    dt = min(1.0 / cps, (t1 - t0) * 0.6 / max(len(letras), 1))
    evs, teclas = [], []
    for n, k in enumerate(letras):
        a = t0 + n * dt
        b = t0 + (n + 1) * dt if n + 1 < len(letras) else t1
        vis, resto = txt[:k + 1], txt[k + 1:]
        inv = "{\\alpha&HFF&}" + resto if resto else ""
        evs.append(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{{\\an5\\pos({x},{y}){tags}\\fs{fs}{f}}}{vis}{inv}")
        teclas.append(a)
    return evs, teclas

def ev_linhas(t_linhas, t1, linhas, x, y0, dy, estilo=BRANCO, fs=90, fontes=None, pops=True):
    """Linhas que entram uma por vez (cada uma no tempo da fala), bem próximas (dy)."""
    evs = []
    for k, (t, ln) in enumerate(zip(t_linhas, linhas)):
        st, tags = cor_tags(estilo[k] if isinstance(estilo, list) else estilo)
        f = f"\\fn{fontes[k]}" if fontes and fontes[k] else ""
        tam = fs[k] if isinstance(fs, list) else fs
        evs.append(f"Dialogue: 1,{ts(t)},{ts(t1)},{st},,0,0,0,,{{\\an5\\pos({x},{y0 + k * dy}){tags}\\fs{tam}{f}{POP if pops else ''}}}{ln}")
    return evs

# ---------------------------------------------------------------- destaques inteiros (revisão 3)
FADE = "\\fad(150,100)"

def largura_texto(txt, fs, fonte="KBPoppinsBold.ttf", esp=-2):
    from PIL import ImageFont
    f = ImageFont.truetype(os.path.join(FONTS, fonte), max(8, round(fs / 1.4)))
    return f.getlength(txt) + esp * (len(txt) - 1)

def caber(txt, fs, y, caixa=True, fonte="KBPoppinsBold.ttf"):
    """Diminui a fonte até caber numa linha só dentro da guia (caixinha nunca quebra em duas)."""
    lim = (927 - 540) * 2 if y + fs / 2 > 1070 else (994 - 540) * 2
    lim -= 60 if caixa else 20
    while fs > 40 and largura_texto(txt, fs, fonte) > lim:
        fs -= 2
    return fs

def ev_inteiro(t0, t1, txt, x, y, estilo=ROXO, fs=100, fonte=None, layer=1):
    """O destaque aparece de uma vez (fade-in curto), numa linha só."""
    st, tags = cor_tags(estilo)
    fs = caber(txt, fs, y, st == "Box", (fonte or "KB Poppins Bold").replace(" ", "") + ".ttf")
    f = f"\\fn{fonte}" if fonte else ""
    return f"Dialogue: {layer},{ts(t0)},{ts(t1)},{st},,0,0,0,,{{\\an5\\pos({x},{y}){tags}\\fs{fs}{f}{FADE}}}{txt}"

class Destaques:
    """Junta os destaques e garante que um nunca fica por cima do outro: cada um sai quando o
    próximo entra. Cada item: (t0, t1, função(t1) -> eventos, sons)."""
    def __init__(self):
        self.itens = []
    def add(self, t0, t1, fazer, sons=()):
        self.itens.append([t0, t1, fazer, list(sons)])
    def render(self):
        self.itens.sort(key=lambda x: x[0])
        evs, ocupado, sfx = [], [], []
        for i, (t0, t1, fazer, sons) in enumerate(self.itens):
            if i + 1 < len(self.itens):
                t1 = min(t1, self.itens[i + 1][0] - 0.04)
            evs.extend(fazer(t1)); ocupado.append((t0, t1)); sfx.extend(sons)
        return evs, ocupado, sfx

# ---------------------------------------------------------------- linhas pontilhadas (desenho no rosto)
def tracejado(pontos, dash=14, gap=10, larg=4):
    pts = np.array(pontos, float)
    segs, acc, on = [], 0.0, True
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        L = np.linalg.norm(q - p)
        if L == 0:
            continue
        d = (q - p) / L
        nrm = np.array([-d[1], d[0]]) * larg / 2
        pos = 0.0
        while pos < L:
            lim = dash if on else gap
            step = min(lim - acc, L - pos)
            if on:
                segs.append((p + d * pos, p + d * (pos + step), nrm))
            pos += step; acc += step
            if acc >= lim - 1e-6:
                acc = 0.0; on = not on
    return segs

def curva(p0, p1, p2, n=24):
    p0, p1, p2 = map(np.array, (p0, p1, p2))
    return [tuple((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2) for t in np.linspace(0, 1, n)]

def desenho_ass(segs, frac=1.0):
    k = max(1, int(len(segs) * frac))
    cmds = []
    for a, b, nrm in segs[:k]:
        c = [a + nrm, b + nrm, b - nrm, a - nrm]
        cmds.append("m {:.0f} {:.0f} l {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}".format(*c[0], *c[1], *c[2], *c[3]))
    return " ".join(cmds)

def ev_linhas_rosto(rosto_json, t0, t1, cor=ROXO):
    det = [d for d in json.load(open(rosto_json)) if t0 - 0.05 <= d["t"] <= t1 + 0.05]
    kp = np.array([d["kp"] for d in det])
    for j in range(kp.shape[1]):
        for c in range(2):
            kp[:, j, c] = np.convolve(np.pad(kp[:, j, c], 2, mode="edge"), np.ones(5) / 5, mode="valid")
    evs = []
    for i, d in enumerate(det):
        a = d["t"]
        b = det[i + 1]["t"] if i + 1 < len(det) else t1
        if b <= t0 or a >= t1:
            continue
        a, b = max(a, t0), min(b, t1)
        oD, oE, nariz, boca, orD, orE = kp[i]
        larg = np.linalg.norm(orE - orD)
        baixo = np.array([-(orE - orD)[1], (orE - orD)[0]]) / larg
        queixo = boca + baixo * larg * 0.42
        mand = curva(orD + baixo * larg * 0.10, queixo + (orD - orE) * 0.55, queixo, 20) + \
               curva(queixo, queixo + (orE - orD) * 0.55, orE + baixo * larg * 0.10, 20)[1:]
        zigD = curva(orD - baixo * larg * 0.02, oD + baixo * larg * 0.28, nariz + (orD - nariz) * 0.25 + baixo * larg * 0.06, 14)
        zigE = curva(orE - baixo * larg * 0.02, oE + baixo * larg * 0.28, nariz + (orE - nariz) * 0.25 + baixo * larg * 0.06, 14)
        segs = []
        for pl in (mand, zigD, zigE):
            segs += tracejado(pl, dash=13, gap=9, larg=5)
        frac = min(1.0, (a - t0) / 0.6 + 0.08)
        evs.append(f"Dialogue: 3,{ts(a)},{ts(b)},Desenho,,0,0,0,,{{\\an7\\pos(0,0)\\1c{cor}\\bord0\\shad0\\p1}}{desenho_ass(segs, frac)}")
    return evs

# ---------------------------------------------------------------- posição "por cima da cabeça"
def acima_da_cabeca(cabeca, t0, t1, altura, folga=45, padrao=520):
    """Centro y logo acima do topo da cabeça (nem colado no limite de cima, nem na cabeça)."""
    tops = [y for t, y in cabeca if t0 - 0.3 <= t <= t1 + 0.3 and y]
    topo = min(tops) if tops else padrao + altura / 2 + folga
    y = topo - folga - altura / 2
    return int(max(263 + 25 + altura / 2, min(y, 640)))

# ---------------------------------------------------------------- imagens
def preparar_imagem(src, dst, largura, raio=34, borda=8, fundo_branco=False):
    from PIL import Image, ImageDraw
    im = Image.open(src).convert("RGBA")
    if fundo_branco:
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    h = round(im.height * largura / im.width)
    im = im.resize((largura, h), Image.LANCZOS)
    tot = Image.new("RGBA", (largura + 2 * borda, h + 2 * borda), (0, 0, 0, 0))
    m = Image.new("L", tot.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tot.width - 1, tot.height - 1], raio + borda, fill=255)
    tot.paste(Image.new("RGBA", tot.size, (255, 255, 255, 255)), (0, 0), m)
    mi = Image.new("L", (largura, h), 0)
    ImageDraw.Draw(mi).rounded_rectangle([0, 0, largura - 1, h - 1], raio, fill=255)
    tot.paste(im, (borda, borda), mi)
    tot.save(dst)
    return tot.size

def card_logo_branco(dst, logo_card):
    """Só a logomarca, em fundo branco (como nos vídeos anteriores, sem cartãozinho)."""
    from PIL import Image
    src = Image.open(logo_card).convert("RGB")
    a = np.array(src).astype(int)
    bgc = np.median(a[:200, :200].reshape(-1, 3), axis=0)
    m = np.abs(a - bgc).sum(axis=2) > 60
    ys, xs = np.where(m)
    logo = src.crop((xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10))
    la = np.array(logo).astype(float)
    # troca o fundo lilás claro do logo por branco
    dist = np.abs(la - bgc).sum(axis=2)
    alpha = np.clip((dist - 20) / 60, 0, 1)[..., None]
    la = la * alpha + 255 * (1 - alpha)
    logo = Image.fromarray(la.astype(np.uint8))
    lw = 720
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    card = Image.new("RGB", (W, H), (255, 255, 255))
    x0, y0 = (W - lw) // 2, (H - logo.height) // 2 - 40
    card.paste(logo, (x0, y0))
    card.save(dst)
    assert 88 <= x0 and x0 + lw <= 927 and 263 <= y0 and y0 + logo.height <= 1459

# ---------------------------------------------------------------- recorte da pessoa (imagem "atrás" dela)
def mascara_pessoa(src, janelas, dst, base_vf, dur):
    """Vídeo de máscara (pessoa = branco) com a duração inteira; só as janelas são calculadas,
    o resto fica preto. Alinhado quadro a quadro com o vídeo final (mesmo zoom)."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(AQUI, "selfie.tflite")), output_confidence_masks=True))
    n_total = int(round(dur * 30))
    q = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", "540x960",
                          "-r", "30", "-i", "-", "-vf", f"scale={W}:{H},gblur=sigma=2", "-c:v", "ffv1", dst],
                         stdin=subprocess.PIPE)
    zero = bytes(540 * 960)
    n = 0
    for t0, t1 in sorted(janelas):
        f0, f1 = int(round(t0 * 30)), int(round(t1 * 30))
        while n < f0:
            q.stdin.write(zero); n += 1
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf",
                              f"{base_vf},trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS,scale=540:960",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        while n < f1:
            b = p.stdout.read(540 * 960 * 3)
            if len(b) < 540 * 960 * 3: break
            fr = np.frombuffer(b, np.uint8).reshape(960, 540, 3)
            r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)))
            m = r.confidence_masks[0].numpy_view()
            q.stdin.write((np.clip((m - 0.35) / 0.3, 0, 1) * 255).astype(np.uint8).tobytes()); n += 1
        p.stdout.close(); p.wait()
    while n < n_total:
        q.stdin.write(zero); n += 1
    q.stdin.close(); q.wait()
    return dst

def ev_olho(t0, t1):
    """Tela fechando devagar, como pálpebras (cima e baixo, borda curva), quadro a quadro."""
    evs = []
    n = int((t1 - t0) * 30)
    for i in range(n + 1):
        p = min(1.0, i / n)
        e = p * p * (3 - 2 * p)
        a = t0 + i / 30
        b = a + 1 / 30 if i < n else t1 + 2
        aberto = (1 - e) * (H / 2 + 220)          # meia-abertura no centro
        cmds = []
        for sinal in (-1, 1):
            pts = []
            for k in range(41):
                x = W * k / 40
                curv = ((x - W / 2) / (W / 2)) ** 2 * 220 * (1 - e * 0.6)
                y = H / 2 + sinal * max(aberto - curv, 0)
                pts.append((x, y))
            borda = 0 if sinal < 0 else H
            poly = [(0, borda)] + pts + [(W, borda)]
            cmds.append("m " + " l ".join(f"{x:.0f} {y:.0f}" for x, y in poly))
        evs.append(f"Dialogue: 9,{ts(a)},{ts(b)},Desenho,,0,0,0,,{{\\an7\\pos(0,0)\\1c&H000000&\\bord0\\shad0\\p1}}{' '.join(cmds)}")
    return evs

# ---------------------------------------------------------------- música
def trilha_suave(dst, dur, sr=48000):
    t = np.arange(int(dur * sr)) / sr
    acordes = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (164.81, 207.65, 246.94)]
    y = np.zeros_like(t)
    per = 4.0
    for i, ac in enumerate(acordes * int(dur // (per * 4) + 2)):
        a = i * per
        if a > dur: break
        seg = (t >= a) & (t < a + per + 1.5)
        tt = t[seg] - a
        env = np.minimum(tt / 1.2, 1) * np.exp(-np.maximum(tt - per, 0) / 0.6)
        for f in ac:
            y[seg] += env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 1)) / len(ac)
    mel = [659.25, 587.33, 523.25, 493.88, 523.25, 587.33, 523.25, 440.0]
    for i in range(int(dur / 2)):
        a = i * 2.0 + 0.5
        seg = (t >= a) & (t < a + 2.5)
        tt = t[seg] - a
        y[seg] += 0.35 * np.exp(-tt * 1.8) * np.sin(2 * np.pi * mel[i % len(mel)] * tt) * np.minimum(tt / 0.01, 1)
    rev = np.zeros_like(y)
    for d, g in ((0.031, 0.5), (0.053, 0.4), (0.079, 0.3), (0.113, 0.25), (0.167, 0.2)):
        k = int(d * sr); rev[k:] += g * y[:-k]
    y = (y + rev) * np.minimum(1, t / 2) * np.minimum(1, (dur - t) / 2)
    y = y / np.abs(y).max() * 0.9
    import wave
    st = (np.stack([y, y], 1) * 32767).astype(np.int16)
    w = wave.open(dst, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes()); w.close()

# ---------------------------------------------------------------- efeitos sonoros: sem sobreposição
def limpar_sfx(sfx, gap=0.7):
    """Teclas ficam (são o teclado); qualquer outro som que caia colado em outro é descartado."""
    sfx = sorted(sfx, key=lambda x: x[1])
    teclas = [t for n, t in sfx if n == "tecla"]
    out = []
    for n, t in sfx:
        if n != "tecla":
            if any(t - 0.4 <= k <= t + gap for k in teclas):
                continue
            if any(abs(t - u) < gap for m, u in out if m != "tecla"):
                continue
        out.append((n, t))
    return out

def hdr(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    return r.strip(",") in ("arib-std-b67", "smpte2084")

# ---------------------------------------------------------------- montagem
def build(cfg):
    out = sys.argv[1] if len(sys.argv) > 1 else "previa.mp4"
    crf = sys.argv[2] if len(sys.argv) > 2 else "21"
    preset = "slow" if crf in ("16", "17", "18") else "medium"
    words = cfg["words"]
    DUR = cfg["dur"]
    leg_font, leg_fs = cfg["leg_font"], cfg["leg_fs"]
    leg_y = cfg["leg_y"]
    ev = list(cfg.get("eventos", []))
    ocupado = cfg.get("sem_legenda", [])

    # ----- legenda corrida: até 3 palavras, cada palavra aparece quando ela fala
    def livre(s):
        return not any(a - 0.01 <= s < b - 0.01 for a, b in ocupado)
    breaks = sorted({x for iv in ocupado for x in iv})
    groups, cur = [], []
    for t, s, e in words:
        if cur and (len(cur) >= 3 or sum(len(x[0]) for x in cur) + len(t) > 17
                    or any(cur[0][1] < b <= s + 0.001 for b in breaks)
                    or livre(s) != livre(cur[0][1])):
            groups.append(cur); cur = []
        cur.append([t, s, e])
        if t[-1] in ".,?!":
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    for gi, g in enumerate(groups):
        if not livre(g[0][1]):
            continue
        nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else DUR
        fim = min(nxt, g[-1][2] + 0.5)
        y = leg_y(g[0][1]) if callable(leg_y) else leg_y
        toks = []
        for x in g:
            tk = limpa(x[0])
            if not (x[1] == words[0][1] or tk in MANTER or (tk.isupper() and len(tk) > 1)):
                tk = tk.lower()
            toks.append(tk)
        for k, (t, s, e) in enumerate(g):
            a = s
            b = g[k + 1][1] if k + 1 < len(g) else fim
            if b <= a:
                continue
            vis = " ".join(toks[:k + 1])
            resto = " ".join(toks[k + 1:])
            inv = "{\\alpha&HFF&} " + resto if resto else ""
            ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Leg,,0,0,0,,{{\\an2\\pos(540,{y})}}{vis}{inv}")
    doc = ass_doc(ev, leg_font, leg_fs)
    if hdr(cfg["src"]):
        # em HDR, branco 100% vira luz de destaque (ofusca): textos no "branco de referência" (~75%)
        import re
        def esc(m):
            a, b, g, r = m.group(1), *[int(m.group(i), 16) for i in (2, 3, 4)]
            return "&H%s%02X%02X%02X" % (a, round(b * 0.82), round(g * 0.82), round(r * 0.82))
        doc = re.sub(r"&H([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})", esc, doc)
    open("legendas.ass", "w").write(doc)

    # ----- zoom
    R = 0.35
    terms = []
    for kind, t0, t1, z in cfg.get("zooms", []):
        a = z - 1
        if kind == "seco":
            terms.append(f"{a}*between(it,{t0},{t1})")
        else:
            u = f"clip((it-{t0})/{R},0,1)"
            v = f"clip(({t1}-it)/{R},0,1)"
            terms.append(f"{a}*min({u}*{u}*(3-2*{u}),{v}*{v}*(3-2*{v}))")
    zexpr = "1+" + ("+".join(terms) if terms else "0")
    HDR = hdr(cfg["src"])
    cor = ""     # nunca mexe na cor: vídeo HDR continua HDR (HLG), igual ao que ela vê no iPhone
    base_vf = (f"{cor}trim=0:{DUR},setpts=PTS-STARTPTS,"
               f"zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.22':d=1:s={W}x{H}:fps=30")

    inputs = ["-i", cfg["src"]]
    fc = [f"[0:v]{base_vf},format=yuva420p[z0]"]
    cur_v = "z0"
    idx = 1
    # imagens atrás da pessoa: precisam de máscara
    atras = [im for im in cfg.get("imagens", []) if len(im) > 5 and im[5] == "atras"]
    if atras and "--so-legenda" not in sys.argv:
        inputs += ["-i", mascara_pessoa(cfg["src"], [(im[0], im[1]) for im in atras], "mascara.mkv", base_vf, DUR)]
        mask_idx = idx; idx += 1
        fc.append(f"[{mask_idx}:v]format=gray,split={len(atras)}" + "".join(f"[mk{j}]" for j in range(len(atras))))
    for k, im in enumerate(cfg.get("imagens", [])):
        t0, t1, png, x, y = im[:5]
        inputs += ["-loop", "1", "-t", str(DUR), "-i", png]
        fc.append(f"[{idx}:v]format=rgba,fade=in:st={t0}:d=0.25:alpha=1,fade=out:st={t1 - 0.25}:d=0.25:alpha=1[im{k}]")
        idx += 1
        if len(im) > 5 and im[5] == "atras":
            j = atras.index(im)
            fc.append(f"[{cur_v}]split[bg{k}][pe{k}]")
            fc.append(f"[bg{k}][im{k}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[bi{k}]")
            fc.append(f"[pe{k}][mk{j}]alphamerge[pm{k}]")
            fc.append(f"[bi{k}][pm{k}]overlay=0:0:enable='between(t,{t0},{t1})'[ov{k}]")
        else:
            fc.append(f"[{cur_v}][im{k}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[ov{k}]")
        cur_v = f"ov{k}"
    fc.append(f"[{cur_v}]ass=legendas.ass:fontsdir={FONTS},format=yuv420p,settb=1/30,setpts=N/TB/30[base]")

    sfx = list(cfg.get("sfx", []))
    fim = cfg.get("fim", "logo")
    if fim == "logo":
        END = 2.5 + 0.7
        inputs += ["-loop", "1", "-t", "3.5", "-i", cfg["card"]]
        lut = "lutrgb=r=val*0.75:g=val*0.75:b=val*0.75," if HDR else ""
        fc.append(f"[{idx}:v]fps=30,scale={W}:{H},{lut}format=yuv420p,settb=1/30,setpts=N/TB/30[card]")
        fc.append("[base]tpad=stop_mode=clone:stop_duration=0.7[basep]")
        fc.append(f"[basep][card]xfade=transition=circleclose:duration=0.7:offset={DUR}[v]")
        idx += 1
    else:   # "olho": a tela vai fechando devagar, como pálpebras (desenhado no ASS), sem card
        END = 0.5
        fc.append("[base]tpad=stop_mode=clone:stop_duration=0.5[v]")
        sfx.append(("riser", cfg["olho_inicio"] - 0.15))

    # ----- áudio
    sfx = limpar_sfx(sfx)
    names = sorted({n for n, _ in sfx})
    sidx = {}
    for n in names:
        inputs += ["-i", os.path.join(SFX, f"{n}.wav")]
        sidx[n] = idx; idx += 1
    fc.append(f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,afade=out:st={DUR - 0.05}:d=0.05,apad=pad_dur={END}[voz]")
    mix = ["[voz]"]
    for n in names:
        cnt = sum(1 for m, _ in sfx if m == n)
        fc.append(f"[{sidx[n]}:a]asplit={cnt}" + "".join(f"[{n}{k}]" for k in range(cnt)))
    usados = {n: 0 for n in names}
    for k, (n, t) in enumerate(sfx):
        lab = f"{n}{usados[n]}"; usados[n] += 1
        ms = int(max(t, 0) * 1000)
        fc.append(f"[{lab}]adelay={ms}|{ms},volume={VOL[n]}[s{k}]")
        mix.append(f"[s{k}]")
    if cfg.get("musica"):
        inputs += ["-i", cfg["musica"]]
        fc.append(f"[{idx}:a]volume={cfg.get('musica_vol', 0.018)},atrim=0:{DUR + END},afade=out:st={DUR + END - 1.5}:d=1.5[mus]")
        mix.append("[mus]"); idx += 1
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first[a]")

    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[v]", "-map", "[a]", "-t", str(DUR + END),
           *(["-c:v", "libx265", "-preset", "medium", "-crf", str(int(crf) + 1), "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1",
               "-x265-params", "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:log-level=error",
               "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc"] if HDR else
             ["-c:v", "libx264", "-preset", preset, "-crf", crf, "-profile:v", "high", "-pix_fmt", "yuv420p",
              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]),
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    print(f"{len(groups)} grupos de legenda, {len(sfx)} efeitos ({sum(1 for n, _ in sfx if n != 'tecla')} fora o teclado)")
    if "--so-legenda" not in sys.argv:
        subprocess.run(cmd, check=True)
