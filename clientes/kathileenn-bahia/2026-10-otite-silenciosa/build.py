"""Monta o Reels "Otite silenciosa" no padrão Kathileenn Bahia (legenda Destino Verdadeiro, mesma do aparelho auditivo)."""
import os
import json, subprocess, sys

W, H = 1080, 1920
SRC = "bruto.mov"
DUR = 109.96         # fim do clipe (última palavra termina em ~109.6)
END = 2.2            # card do logo
OUT = sys.argv[1] if len(sys.argv) > 1 else "previa.mp4"
CRF = sys.argv[2] if len(sys.argv) > 2 else "21"
PRESET = "slow" if CRF in ("16", "17", "18") else "medium"
FONTS = "../fonts3"
SFX = "../work/sfx"

BRANCO = "&H00FFFFFF"
ROXO = "&H00BF227F"      # #7F22BF
VERMELHO = "&H002A2AD6"  # #D62A2A
AZUL = "&H00C85A1E"      # #1E5AC8
CAIXA = "&H50F2EEF0"     # fundo claro semitransparente das caixas
LEG_TOPO = 480           # legenda branca: base no vazio acima da cabeça (mesa já é carregada)
LEG_BAIXO = 1420         # quando a cabeça sobe (zoom/close): desce para abaixo do peito
PEITO = 1360             # base das ênfases (caixas) na altura do peito; zona segura: x 88-992, y 261-1461
CABECA_MIN = 500         # legenda em cima só se o topo da cabeça (com cabelo) estiver abaixo disso
cabeca = json.load(open("cabeca.json")) if os.path.exists("cabeca.json") else []   # medido numa prévia com os mesmos zooms
TOPO_Y = 400             # textos no vazio acima da cabeça
AV = 0.0

# ---------- transcrição corrigida ----------
words = []
for s in json.load(open("transcricao.json")):
    for w in s["words"]:
        words.append([w["w"].strip(), w["s"] - AV, w["e"] - AV])
fix = {"d": "debaixo_d", "'água,": "água,"}
fixed = []
for t, s, e in words:
    t = fix.get(t, t)
    if t == "água," and fixed and fixed[-1][0] == "debaixo_d":
        fixed[-1] = ["d'água,", fixed[-1][1], e]; continue
    fixed.append([t, s, e])
words = fixed

def clean(t):
    return t.strip(".,?!…").replace("...", "").lower()

# ---------- ênfases ----------
# caixa: (início, fim, texto, onde, cor). onde = "peito" (no lugar da legenda), "topo" ou (x, y)
boxes = [
    (12.58, 13.20, "líquido", "peito", ROXO),
    (13.80, 15.90, "atrás do tímpano", "peito", ROXO),
    (22.38, 23.30, "abafa o som", "peito", ROXO),
    (36.76, 37.90, "ouvido tapado", "peito", ROXO),
    (42.32, 43.60, "otites de repetição", "peito", ROXO),
    (53.64, 54.55, "E na escola?", "peito", ROXO),
    (69.42, 70.90, "atrasar na fala", "peito", ROXO),
    (77.18, 77.88, "rapidinho", "peito", ROXO),
    (82.94, 83.60, "Não dói", "peito", ROXO),
    (84.06, 85.00, "poucos minutos", "peito", ROXO),
    (92.46, 93.40, "otorrino", "peito", ROXO),
    (103.32, 104.95, "turma da otite", "peito", ROXO),
    (105.02, 106.50, "salva esse vídeo", "peito", ROXO),
    (108.32, 109.64, "agende sua avaliação", "peito", ROXO),
]
big = [(30.54, 32.20, "Debaixo d'água")]          # Poppins branca grande
mega = [(99.74, 101.40, "JUNTOS")]                # roxo gigante, digitando
imagem_dela = (-1, -1)

zooms = [
    ("seco", 30.54, 32.20, 1.15),
    ("suave", 32.3, 37.8, 1.10),
    ("suave", 45.9, 53.2, 1.12),
    ("seco", 53.64, 54.55, 1.18),
    ("seco", 56.90, 58.90, 1.15),
    ("seco", 69.42, 70.90, 1.20),
    ("suave", 89.2, 93.4, 1.10),
    ("suave", 99.2, 101.5, 1.12),
    ("suave", 101.9, 109.7, 1.10),
]

# ênfases foram marcadas no tempo do áudio original: acompanham o adiantamento
# as ênfases foram marcadas no áudio antigo; no vídeo novo o áudio foi deslocado por trechos.
# mapa_audio.json = (tempo no áudio antigo, deslocamento até o áudio novo), medido por correlação
def novo_t(t):
    return t
boxes = [(novo_t(t0), novo_t(t0) + (t1 - t0), *r) for t0, t1, *r in boxes]
big = [(novo_t(t0), novo_t(t0) + (t1 - t0), x) for t0, t1, x in big]
mega = [(novo_t(t0), novo_t(t0) + (t1 - t0), x) for t0, t1, x in mega]

sfx = [("clique_caneta", 0.0), ("clique_caneta", 0.25)]   # as duas linhas do título
for kind, t0, t1, z in zooms:
    sfx.append(("swish_capcut", max(t0 - (0.12 if kind == "suave" else 0.05), 0)))
for b in boxes:
    sfx.append(("clique_caneta", b[0]))
for t0, _, _ in big:
    sfx.append(("clique_caneta", t0))
for t0, _, _ in mega:
    sfx.append(("teclado", t0 - 0.075))
sfx.sort(key=lambda x: x[1])
teclas = [t for n, t in sfx if n == "teclado"]
sfx = [(n, t) for n, t in sfx if n == "teclado" or not any(abs(t - k) < 0.4 for k in teclas)]
dedup = []
for name, t in sfx:
    if dedup and t - dedup[-1][1] < 0.25 and name != "teclado":
        continue
    dedup.append((name, t))
sfx = dedup

# ---------- legenda corrida (frases, até 2 linhas, como no vídeo de referência) ----------
replace = [b for b in boxes if b[3] == "peito"] + [(t0, t1) for t0, t1, _ in big + mega]
breaks = sorted({b[0] for b in replace} | {b[1] for b in replace} | {3.0})
def in_box(t):
    return any(b[0] - 0.01 <= t < b[1] - 0.01 for b in replace)
def cabeca_alta(s, e):
    return any(top is not None and top < CABECA_MIN for t, top in cabeca if s - 0.2 <= t <= e)

LINHA = 32   # caracteres por linha
groups, cur = [], []
for t, s, e in words:
    txt_len = len(" ".join(clean(x[0]) for x in cur + [[t]]))
    if cur and (txt_len > 2 * LINHA or s - cur[0][1] > 3.2
                or any(cur[0][1] < b <= s + 0.001 for b in breaks)
                or in_box(s) != in_box(cur[0][1])):
        groups.append(cur); cur = []
    cur.append([t, s, e])
    if t[-1] in ".?!" or (t[-1] == "," and len(cur) >= 4):
        groups.append(cur); cur = []
if cur:
    groups.append(cur)

def quebra(txt):
    if len(txt) <= LINHA:
        return [txt]
    ws = txt.split()
    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
    return [" ".join(ws[:best]), " ".join(ws[best:])]

def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

ev = []
for gi, g in enumerate(groups):
    s = g[0][1]
    nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else DUR
    e = min(nxt, g[-1][2] + 0.5)
    txt = " ".join(clean(x[0]) for x in g).strip()
    if not txt:
        continue
    embaixo = s < 3.0 or cabeca_alta(s, e)      # título ocupa o topo nos 3 primeiros segundos
    if embaixo and in_box(s):
        continue                                # embaixo, a ênfase do peito ocupa o lugar
    y = LEG_BAIXO if embaixo else LEG_TOPO
    linhas = quebra(txt)
    for k, ln in enumerate(linhas):
        ly = y - (len(linhas) - 1 - k) * 50   # linhas bem coladas, como na referência
        ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Leg,,0,0,0,,{{\\an2\\pos(540,{ly})\\fad(60,60)}}{ln}")

# título escalonado: linha fina (serifada) à esquerda + linha grossa (Poppins) deslocada à direita
TIT1, TIT2 = "Otite sem dor", "prejudica a audição?"   # mesmo estilo do título do aparelho auditivo
ev.append(f"Dialogue: 2,{ts(0)},{ts(3.0)},Tit1,,0,0,0,,{{\\an1\\pos(100,{{T1Y}})\\fad(120,200)}}{TIT1}")
ev.append(f"Dialogue: 2,{ts(0.25)},{ts(3.0)},Tit2,,0,0,0,,{{\\an1\\pos({{T2X}},{{T2Y}})\\fad(80,200)}}{TIT2}")

pop_in = "\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)"
BORDA = "\\xbord22\\ybord3"
for t0, t1, txt, onde, cor in boxes:
    if onde == "peito":
        pos = f"\\an2\\pos(540,{PEITO})"
    elif onde == "topo":
        pos = f"\\an5\\pos(540,{TOPO_Y})"
    else:
        pos = f"\\an5\\pos({onde[0]},{onde[1]})"
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Box,,0,0,0,,{{{pos}\\1c{cor}{BORDA}\\fad(0,80){pop_in}}}{txt}")
for t0, t1, txt in big:
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Big,,0,0,0,,{{\\an2\\pos(540,{PEITO})\\fad(0,80){pop_in}}}{txt}")
LETRA = 0.11
for t0, t1, txt in mega:
    for k in range(1, len(txt) + 1):
        a = t0 + (k - 1) * LETRA
        b = t0 + k * LETRA if k < len(txt) else t1
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Mega,,0,0,0,,{{\\an2\\pos(540,{PEITO + 40})}}{txt[:k]}{{\\alpha&HFF&}}{txt[k:]}")

TIT1_FS, TIT2_FS = 120, 140
def styles():
    return f"""Style: Leg,KB Cormorant SemiBold,74,{BRANCO},&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2,2,60,60,0,1
Style: Tit1,KB Cormorant SemiBold,{TIT1_FS},{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,2,5,40,40,0,1
Style: Tit2,KB Poppins Bold,{TIT2_FS},{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Big,KB Poppins Bold,120,{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Box,KB Poppins Bold,80,{ROXO},&H000000FF,{CAIXA},{CAIXA},0,0,0,0,100,100,0,0,3,4,0,2,60,60,0,1
Style: Mega,KB Poppins Black,240,{ROXO},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,20,20,0,1"""
# o libass ignora o Spacing do estilo: letras juntinhas via \fsp
SP = {"Leg": -3, "Tit1": -5, "Tit2": -6, "Big": -4, "Box": -3, "Mega": -8}

def ass_doc(events):
    def junta(line):
        st = line.split(",")[3]
        head, txt = line.split(",,0,0,0,,", 1)
        txt = "{" + f"\\fsp{SP[st]}" + txt[1:] if txt.startswith("{") else "{" + f"\\fsp{SP[st]}" + "}" + txt
        return head + ",,0,0,0,," + txt
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles()}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(junta(l) for l in events) + "\n"

def medir(style, txt):
    """Renderiza o texto sozinho e devolve a caixa da tinta (x0, x1, topo, base) relativa ao \\pos com \\an1."""
    line = f"Dialogue: 0,0:00:00.00,0:00:01.00,{style},,0,0,0,,{{\\an1\\pos(0,1500)}}{txt}"
    open("_medir.ass", "w").write(ass_doc([line]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:d=0.1",
                    "-vf", f"ass=_medir.ass:fontsdir={FONTS}", "-frames:v", "1", "_medir.png"], check=True)
    from PIL import Image
    import numpy as np
    a = np.array(Image.open("_medir.png").convert("L"))
    ys, xs = np.where(a > 100)
    return xs.min(), xs.max(), ys.min() - 1500, ys.max() - 1500

# título como na referência: serifada grande à esquerda (x 100-750) e Poppins colada logo abaixo,
# deslocada para a direita até a margem (x ~272-988); ascendentes da Poppins sobem até a serifada
def ajusta(style, txt, alvo):
    global TIT1_FS, TIT2_FS
    for _ in range(3):
        x0, x1, _, _ = medir(style, txt)
        fator = alvo / (x1 - x0)
        if style == "Tit1": TIT1_FS = round(TIT1_FS * fator)
        else: TIT2_FS = round(TIT2_FS * fator)
ajusta("Tit1", TIT1, 650)
ajusta("Tit2", TIT2, 716)
a0, a1, atop, abot = medir("Tit1", TIT1)
b0, b1, btop, bbot = medir("Tit2", TIT2)
_, _, xtop, _ = medir("Tit2", "a")          # topo da altura-x da Poppins
T1Y = 340 - atop                            # topo da serifada em y=340
T1X = 100 - a0
T2X = 988 - b1
T2Y = (T1Y + abot) + 22 - xtop              # altura-x da Poppins começa 22 px abaixo da base da serifada
ev = [l.replace("pos(100,{T1Y})", f"pos({T1X},{T1Y})").replace("{T1Y}", str(T1Y)).replace("{T2X}", str(T2X)).replace("{T2Y}", str(T2Y)) for l in ev]
print(f"título: fs {TIT1_FS}/{TIT2_FS}; serifada x {T1X + a0}-{T1X + a1}, Poppins x {T2X + b0}-{T2X + b1}, y {T1Y + atop}-{T2Y + bbot}")
open("legendas.ass", "w").write(ass_doc(ev))

# ---------- zoom ----------
R = 0.35
terms = []
for kind, t0, t1, z in zooms:
    a = z - 1
    if kind == "seco":
        terms.append(f"{a}*between(it,{t0},{t1})")
    else:
        u = f"clip((it-{t0})/{R},0,1)"
        v = f"clip(({t1}-it)/{R},0,1)"
        terms.append(f"{a}*min({u}*{u}*(3-2*{u}),{v}*{v}*(3-2*{v}))")
zexpr = "1+" + "+".join(terms)

# ---------- ffmpeg ----------
names = sorted({n for n, _ in sfx})
inputs = ["-i", SRC, "-loop", "1", "-t", str(END + 0.5), "-i", "../work/logo_card.png"]
for n in names:
    inputs += ["-i", f"{SFX}/{n}.wav"]
idx = {n: 2 + k for k, n in enumerate(names)}
vol = {"swish_capcut": 0.45, "clique_caneta": 0.45, "teclado": 0.45}

fc = [
    f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,"
    f"zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.22':d=1:s={W}x{H}:fps=30,"
    f"ass=legendas.ass:fontsdir={FONTS},format=yuv420p,settb=1/30,setpts=N/TB/30[base]",
    f"[1:v]fps=30,scale={W}:{H},format=yuv420p,settb=1/30,setpts=N/TB/30[logo]",
    f"[base]tpad=stop_mode=clone:stop_duration=0.4[basep]",
    f"[basep][logo]xfade=transition=fade:duration=0.35:offset={DUR + 0.05}[v]",
]
splits = {}
for n in names:
    cnt = sum(1 for m, _ in sfx if m == n)
    fc.append(f"[{idx[n]}:a]asplit={cnt}" + "".join(f"[{n}{k}]" for k in range(cnt)))
    splits[n] = 0
mix = ["[voz]"]
fc.append(f"[0:a]atrim={AV}:{DUR + AV},asetpts=PTS-STARTPTS,aresample=48000,afade=out:st={DUR - 0.03}:d=0.03,apad=pad_dur={END}[voz]")
for k, (n, t) in enumerate(sfx):
    lab = f"{n}{splits[n]}"; splits[n] += 1
    ms = int(t * 1000)
    fc.append(f"[{lab}]adelay={ms}|{ms},volume={vol[n]}[s{k}]")
    mix.append(f"[s{k}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first[a]")

cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
       "-map", "[v]", "-map", "[a]", "-t", str(DUR + END),
       "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT]
print(f"{len(groups)} grupos de legenda, {len(sfx)} efeitos sonoros")
if "--so-legenda" not in sys.argv:
    subprocess.run(cmd, check=True)
