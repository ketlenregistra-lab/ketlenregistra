"""Motor de edição de Reels no padrão Kathileenn Bahia (lote de novembro).

Cada vídeo descreve, num dicionário, o que entra (legenda, ênfases, zooms, imagens, desenhos,
efeitos, música) e `build(cfg)` monta o ASS e chama o ffmpeg. Tudo respeita a guia do Instagram:
x 88-994, y 263-1459, e abaixo de y 1070 o limite direito é 927.
"""
import json, math, os, subprocess, sys
import numpy as np

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "..", "fonts3")
SFX = os.path.join(AQUI, "..", "work", "sfx")
ROXO = "&H00BF227F"        # #7F22BF
ROXO_RGB = (127, 34, 191)
BRANCO = "&H00FFFFFF"
CAIXA_CLARA = "&H30F4F0F2"

# ---------------------------------------------------------------- utilidades
def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

def carregar_palavras(path, fixes=None, juntar_hifen=True, cortar_depois=None, remover=()):
    words = []
    for s in json.load(open(path)):
        for w in s["words"]:
            words.append([w["w"].strip(), w["s"], w["e"]])
    out = []
    for t, s, e in words:
        if cortar_depois is not None and s >= cortar_depois:
            continue
        if juntar_hifen and t.startswith("-") and out:
            out[-1] = [out[-1][0] + t, out[-1][1], e]
            continue
        out.append([t, s, e])
    fixes = fixes or {}
    res = []
    for i, (t, s, e) in enumerate(out):
        if (round(s, 2), t) in remover:
            continue
        t = fixes.get((round(s, 2), t), fixes.get(t, t))
        if t:
            res.append([t, s, e])
    return res

def limpa(t):
    w = t.strip(".,?!…")
    return w if (w.isupper() and len(w) > 1) or w in ("R", "S", "X", "Z", "WhatsApp") else w.lower()

# ---------------------------------------------------------------- estilos
def estilos(leg_font, leg_fs, leg_bold_font="KB Poppins Bold"):
    return f"""Style: Leg,{leg_font},{leg_fs},{BRANCO},&H000000FF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,0,2,2,153,153,0,1
Style: Big,KB Poppins Bold,112,{BRANCO},&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Box,KB Poppins Bold,74,{BRANCO},&H000000FF,{ROXO},{ROXO},0,0,0,0,100,100,0,0,3,4,0,5,40,40,0,1
Style: Fina,{leg_font},86,{BRANCO},&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2,5,40,40,0,1
Style: Desenho,Arial,20,{ROXO},&H000000FF,{ROXO},&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"""

SP = {"Leg": -2, "Big": -3, "Box": -2, "Fina": -3, "Desenho": 0}

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

POP = "\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)"

# ---------------------------------------------------------------- ênfases -> eventos ASS
def ev_box(t0, t1, txt, x, y, estilo="notif", fs=None):
    """notif: letra branca em caixinha roxa (cartão de notificação). claro: letra roxa em caixa clara."""
    if estilo == "notif":
        cor = f"\\1c{BRANCO}\\3c{ROXO}\\4c{ROXO}"
    else:
        cor = f"\\1c{ROXO}\\3c{CAIXA_CLARA}\\4c{CAIXA_CLARA}"
    f = f"\\fs{fs}" if fs else ""
    return f"Dialogue: 1,{ts(t0)},{ts(t1)},Box,,0,0,0,,{{\\an5\\pos({x},{y}){cor}\\xbord24\\ybord8{f}\\fad(0,80){POP}}}{txt}"

def ev_big(t0, t1, txt, x, y, cor=ROXO, fs=112, fonte=None, sombra=True):
    f = f"\\fn{fonte}" if fonte else ""
    sh = "\\shad3\\4c&H000000&\\4a&H80&" if sombra else "\\shad0"
    return f"Dialogue: 1,{ts(t0)},{ts(t1)},Big,,0,0,0,,{{\\an5\\pos({x},{y})\\1c{cor}\\fs{fs}{f}{sh}\\fad(0,80){POP}}}{txt}"

def ev_typing(t0, t1, txt, x, y, estilo="notif", fs=70, letra=None):
    """Texto que vai sendo digitado (som de teclado). Letras que faltam ficam invisíveis para não pular."""
    letra = letra or min(0.07, 1.4 / max(len(txt), 1))
    evs = []
    if estilo == "notif":
        cor = f"\\1c{BRANCO}\\3c{ROXO}\\4c{ROXO}"
        st = "Box"
        extra = "\\xbord24\\ybord8"
    else:
        cor = f"\\1c{estilo}"
        st = "Big"
        extra = "\\shad3\\4c&H000000&\\4a&H80&"
    n = len(txt)
    for k in range(1, n + 1):
        a = t0 + (k - 1) * letra
        b = t0 + k * letra if k < n else t1
        if k < n and (txt[k - 1] == " " or txt[k - 1] == "\\" or txt[k - 2:k] == "\\N"):
            continue
        # a caixa acompanha o texto digitado (alinhada à esquerda, como numa notificação)
        evs.append(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{{\\an4\\pos({x},{y}){cor}{extra}\\fs{fs}}}{txt[:k]}")
    return evs

def medir(style_line_ass, txt, leg_font, leg_fs):
    """Largura do texto renderizado (px) para centralizar coisas alinhadas à esquerda."""
    line = f"Dialogue: 0,0:00:00.00,0:00:01.00,{style_line_ass}{txt}"
    open(os.path.join(AQUI, "_m.ass"), "w").write(ass_doc([line], leg_font, leg_fs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:d=0.1",
                    "-vf", f"ass={AQUI}/_m.ass:fontsdir={FONTS}", "-frames:v", "1", f"{AQUI}/_m.png"], check=True)
    from PIL import Image
    a = np.array(Image.open(f"{AQUI}/_m.png").convert("L"))
    ys, xs = np.where(a > 60)
    return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())

# ---------------------------------------------------------------- linhas pontilhadas (desenho no rosto)
def tracejado(pontos, dash=14, gap=10, larg=4):
    """Converte uma polilinha em quadradinhos de traço (desenho ASS \\p1)."""
    pts = np.array(pontos, float)
    segs = []
    acc = 0.0
    on = True
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
                a = p + d * pos
                b = p + d * (pos + step)
                segs.append((a, b, nrm))
            pos += step
            acc += step
            if acc >= lim - 1e-6:
                acc = 0.0
                on = not on
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
    """Linhas pontilhadas roxas marcando ossos da face e arcadas, acompanhando o rosto (10 amostras/s)."""
    det = json.load(open(rosto_json))
    det = [d for d in det if t0 - 0.05 <= d["t"] <= t1 + 0.05]
    # suaviza
    kp = np.array([d["kp"] for d in det])
    from numpy import convolve
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
        baixo = np.array([-(orE - orD)[1], (orE - orD)[0]]) / larg      # aponta para baixo do rosto
        queixo = boca + baixo * larg * 0.42
        mand = curva(orD + baixo * larg * 0.10, queixo + (orD - orE) * 0.55, queixo, 20) + \
               curva(queixo, queixo + (orE - orD) * 0.55, orE + baixo * larg * 0.10, 20)[1:]
        zigD = curva(orD - baixo * larg * 0.02, oD + baixo * larg * 0.28, nariz + (orD - nariz) * 0.25 + baixo * larg * 0.06, 14)
        zigE = curva(orE - baixo * larg * 0.02, oE + baixo * larg * 0.28, nariz + (orE - nariz) * 0.25 + baixo * larg * 0.06, 14)
        cima = boca - baixo * larg * 0.13
        arcS = curva(cima + (orD - orE) * 0.20, cima - baixo * larg * 0.05, cima + (orE - orD) * 0.20, 14)
        bx = boca + baixo * larg * 0.13
        arcI = curva(bx + (orD - orE) * 0.18, bx + baixo * larg * 0.06, bx + (orE - orD) * 0.18, 14)
        segs = []
        for pl in (mand, zigD, zigE, arcS, arcI):
            segs += tracejado(pl, dash=13, gap=9, larg=5)
        frac = min(1.0, (a - t0) / 0.7 + 0.08)        # vai se desenhando nos primeiros 0,7 s
        evs.append(f"Dialogue: 3,{ts(a)},{ts(b)},Desenho,,0,0,0,,{{\\an7\\pos(0,0)\\1c{cor}\\bord0\\shad0\\p1}}{desenho_ass(segs, frac)}")
    return evs

# ---------------------------------------------------------------- imagens (colagens)
def preparar_imagem(src, dst, largura, raio=34, borda=8, fundo_branco=False):
    from PIL import Image, ImageDraw, ImageOps
    im = Image.open(src).convert("RGBA")
    if fundo_branco:
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
    h = round(im.height * largura / im.width)
    im = im.resize((largura, h), Image.LANCZOS)
    tot = Image.new("RGBA", (largura + 2 * borda, h + 2 * borda), (0, 0, 0, 0))
    m = Image.new("L", tot.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tot.width - 1, tot.height - 1], raio + borda, fill=255)
    branco = Image.new("RGBA", tot.size, (255, 255, 255, 255))
    tot.paste(branco, (0, 0), m)
    mi = Image.new("L", (largura, h), 0)
    ImageDraw.Draw(mi).rounded_rectangle([0, 0, largura - 1, h - 1], raio, fill=255)
    tot.paste(im, (borda, borda), mi)
    tot.save(dst)
    return tot.size

def card_final(dst, logo_card):
    """Fundo roxo da marca com o logo numa plaquinha clara arredondada (tudo dentro da guia)."""
    from PIL import Image, ImageDraw
    src = Image.open(logo_card).convert("RGB")
    a = np.array(src).astype(int)
    bgc = np.median(a[:200, :200].reshape(-1, 3), axis=0)
    m = np.abs(a - bgc).sum(axis=2) > 60
    ys, xs = np.where(m)
    logo = src.crop((xs.min() - 20, ys.min() - 20, xs.max() + 20, ys.max() + 20))
    card = Image.new("RGB", (W, H), ROXO_RGB)
    lw = 660
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    pw, ph = lw + 80, logo.height + 80
    x0, y0 = (W - pw) // 2, (H - ph) // 2 - 60
    plate = Image.new("RGB", (pw, ph), tuple(int(c) for c in bgc))
    mk = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, pw - 1, ph - 1], 40, fill=255)
    card.paste(plate, (x0, y0), mk)
    card.paste(logo, (x0 + 40, y0 + 40))
    card.save(dst)
    assert 88 <= x0 and x0 + pw <= 927 and 263 <= y0 and y0 + ph <= 1459, "card fora da guia"

# ---------------------------------------------------------------- música (trilha suave sintetizada)
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
    # notas suaves tipo piano por cima
    mel = [659.25, 587.33, 523.25, 493.88, 523.25, 587.33, 523.25, 440.0]
    for i in range(int(dur / 2)):
        a = i * 2.0 + 0.5
        f = mel[i % len(mel)]
        seg = (t >= a) & (t < a + 2.5)
        tt = t[seg] - a
        y[seg] += 0.35 * np.exp(-tt * 1.8) * np.sin(2 * np.pi * f * tt) * np.minimum(tt / 0.01, 1)
    # reverb simples
    rev = np.zeros_like(y)
    for d, g in ((0.031, 0.5), (0.053, 0.4), (0.079, 0.3), (0.113, 0.25), (0.167, 0.2)):
        k = int(d * sr); rev[k:] += g * y[:-k]
    y = y + rev
    y *= np.minimum(1, t / 2) * np.minimum(1, (dur - t) / 2)
    y = y / np.abs(y).max() * 0.9
    import wave
    st = (np.stack([y, y], 1) * 32767).astype(np.int16)
    w = wave.open(dst, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes()); w.close()

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
    ocupado = cfg.get("sem_legenda", [])          # intervalos em que a legenda corrida some

    # ----- legenda corrida: 1 a 3 palavras por vez, embaixo
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
        s = g[0][1]
        nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else DUR
        e = min(nxt, g[-1][2] + 0.5)
        if not livre(s):
            continue
        y = leg_y(s) if callable(leg_y) else leg_y
        txt = " ".join(limpa(x[0]) for x in g)
        ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Leg,,0,0,0,,{{\\an2\\pos(540,{y})\\fad(60,60)}}{txt}")
    open("legendas.ass", "w").write(ass_doc(ev, leg_font, leg_fs))

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

    # ----- entradas
    inputs = ["-i", cfg["src"]]
    fc = [f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,"
          f"zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.22':d=1:s={W}x{H}:fps=30,format=yuva420p[z0]"]
    cur_v = "z0"
    idx = 1
    for k, (t0, t1, png, x, y) in enumerate(cfg.get("imagens", [])):
        inputs += ["-loop", "1", "-t", str(DUR), "-i", png]
        fc.append(f"[{idx}:v]format=rgba,fade=in:st={t0}:d=0.25:alpha=1,fade=out:st={t1 - 0.25}:d=0.25:alpha=1[im{k}]")
        fc.append(f"[{cur_v}][im{k}]overlay={x}:{y}:enable='between(t,{t0},{t1})'[ov{k}]")
        cur_v = f"ov{k}"; idx += 1
    fc.append(f"[{cur_v}]ass=legendas.ass:fontsdir={FONTS},format=yuv420p,settb=1/30,setpts=N/TB/30[base]")
    inputs += ["-loop", "1", "-t", str(cfg.get("fim", 2.5) + 1), "-i", cfg["card"]]
    card_idx = idx; idx += 1
    fc.append(f"[{card_idx}:v]fps=30,scale={W}:{H},format=yuv420p,settb=1/30,setpts=N/TB/30[card]")
    fc.append("[base]tpad=stop_mode=clone:stop_duration=0.7[basep]")
    fc.append(f"[basep][card]xfade=transition=circleclose:duration=0.7:offset={DUR}[v]")   # tela fechando

    # ----- áudio
    END = cfg.get("fim", 2.5) + 0.7
    sfx = sorted(cfg.get("sfx", []), key=lambda x: x[1])
    vol = {"swish_capcut": 0.45, "clique_caneta": 0.45, "teclado": 0.40}
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
        fc.append(f"[{lab}]adelay={ms}|{ms},volume={vol[n]}[s{k}]")
        mix.append(f"[s{k}]")
    if cfg.get("musica"):
        inputs += ["-i", cfg["musica"]]
        fc.append(f"[{idx}:a]volume={cfg.get('musica_vol', 0.06)},atrim=0:{DUR + END},afade=out:st={DUR + END - 1.5}:d=1.5[mus]")
        mix.append("[mus]"); idx += 1
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first[a]")

    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[v]", "-map", "[a]", "-t", str(DUR + END),
           "-c:v", "libx264", "-preset", preset, "-crf", crf, "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    print(f"{len(groups)} grupos de legenda, {len(sfx)} efeitos")
    if "--so-legenda" not in sys.argv:
        subprocess.run(cmd, check=True)
