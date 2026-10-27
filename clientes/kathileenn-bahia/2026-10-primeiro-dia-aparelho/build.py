"""Reels "Primeiro dia de aparelho auditivo" no padrão Kathileenn Bahia (legenda Russolo + Poppins, como o BERA)."""
import json, re, subprocess, sys

W, H = 1080, 1920
SRC = "bruto.mov"
DUR = 95.0           # fim do clipe (última palavra termina em ~94.5)
END = 2.2            # card do logo
OUT = sys.argv[1] if len(sys.argv) > 1 else "previa.mp4"
CRF = sys.argv[2] if len(sys.argv) > 2 else "20"

ROXO = "&H00BF227F"  # #7F22BF em BGR
CAIXA = "&H50F2EEF0"  # fundo claro semitransparente das caixas
LEG_MV = 590          # legenda termina em y=1330; zona segura do Reels: x 88-992, y 261-1461
TIT_Y = 500           # base do título: no vazio acima da cabeça, dentro da zona segura

from PIL import ImageFont
def text_width(font, fs, txt, spacing):
    # libass: tamanho = altura da linha (ascent+descent); Poppins tem 1.4 em
    f = ImageFont.truetype(font, round(fs / 1.4))
    return f.getlength(txt) + spacing * (len(txt) - 1)
BRANCO = "&H00FFFFFF"

# ---------- transcrição corrigida ----------
words = []
for s in json.load(open("transcricao.json")):
    for w in s["words"]:
        words.append([w["w"].strip(), w["s"], w["e"]])
fixed = []
i = 0
while i < len(words):
    t, s, e = words[i]
    if t == "Música":
        i += 1; continue
    if i + 1 < len(words) and words[i + 1][0] in ("-se", "-los"):
        fixed.append([t + words[i + 1][0], s, words[i + 1][2]]); i += 2; continue
    fixed.append([t, s, e]); i += 1
words = fixed

def clean(t):
    keep = t.strip(".,?!")
    return keep if keep.isupper() and len(keep) > 1 else keep.lower()

# ---------- ênfases ----------
# caixas roxas: substituem a legenda corrida naquele trecho (com posição própria: ficam onde indicado)
boxes = [
    (9.46, 10.50, "ótimo sinal"),
    (12.24, 13.06, "frequências"),
    (13.30, 14.55, "esquecidas"),
    (30.58, 31.55, "reaprender"),
    (38.12, 39.55, "primeira semana"),
    (41.18, 42.25, "bastante natural"),
    (46.42, 47.45, "bem próxima"),
    (53.00, 53.90, "regulando"),
    (55.56, 56.85, "confortável"),
    (60.74, 62.30, "usar todos os dias"),
    (63.52, 65.30, "variedade de ambientes"),
    (68.12, 69.75, "ambientes tranquilos"),
    (81.02, 82.10, "com a sua cara"),
    (91.16, 92.40, "manda esse vídeo"),
]
# palavra grande branca (Poppins), primeira letra maiúscula, no vazio de cima
big = [
    (17.64, 18.40, "Cérebro"),
    (58.96, 60.50, "O que ajuda?"),
    (85.34, 87.75, "Nada de gaveta"),
]
# lista que entra item a item, em caixas roxas acima da cabeça
stack = [(22.16, "Ar-condicionado"), (23.52, "Geladeira"), (24.72, "Passos no chão"), (28.00, "Pássaros")]
stack_end = 29.40
# palavra gigante roxa digitando (som de teclado), no vazio de cima
mega = [(7.86, 8.40, "TROVÃO")]   # deslocado à direita para não cair sobre o logo roxo da parede

# zoom: (tipo, início, fim, intensidade). suave = keyframe in/out; seco = corte para frente
zooms = [
    ("seco", 7.86, 8.40, 1.15),
    ("suave", 8.5, 15.9, 1.10),
    ("seco", 17.64, 18.40, 1.18),
    ("suave", 29.5, 37.6, 1.10),
    ("seco", 41.18, 42.25, 1.15),
    ("suave", 42.4, 53.9, 1.10),
    ("seco", 58.96, 60.50, 1.18),
    ("suave", 60.7, 69.1, 1.10),
    ("seco", 73.90, 75.70, 1.15),
    ("suave", 75.9, 83.5, 1.10),
    ("seco", 85.34, 87.75, 1.20),
    ("suave", 87.9, 94.3, 1.10),
]

sfx = [("clique_caneta", 0.0), ("clique_caneta", 0.25)]   # as duas linhas do título
for kind, t0, t1, z in zooms:
    sfx.append(("swish_capcut", max(t0 - (0.12 if kind == "suave" else 0.05), 0)))
for b in boxes:
    sfx.append(("clique_caneta", b[0]))
for t0, _ in stack:
    sfx.append(("clique_caneta", t0))
for t0, _, _ in mega:
    sfx.append(("teclado", t0 - 0.075))   # 1ª tecla do arquivo cai junto com a 1ª letra
sfx.sort(key=lambda x: x[1])
# evita dois efeitos colados
# digitação manda: tira o swish de zoom que cair junto do teclado
teclas = [t for n, t in sfx if n == "teclado"]
sfx = [(n, t) for n, t in sfx if n == "teclado" or not any(abs(t - k) < 0.4 for k in teclas)]
dedup = []
for name, t in sfx:
    if dedup and t - dedup[-1][1] < 0.25 and name != "teclado":
        continue
    dedup.append((name, t))
sfx = dedup

# ---------- legenda corrida ----------
# palavra grande na altura do peito (quando a pessoa sobe no quadro e não sobra espaço em cima)
chest = []
# palavra com ênfase aparece uma vez só: enquanto qualquer ênfase está na tela, a legenda some
replace = ([b[:3] for b in boxes] + chest + big + [(t0, t0 + 0.01, "") for t0, _ in stack]
           + [(stack[0][0], stack_end, "")] + mega)
breaks = sorted({b[0] for b in replace} | {b[1] for b in replace})
def in_box(t):
    return any(b0 - 0.01 <= t < b1 - 0.01 for b0, b1, _ in replace)

groups, cur = [], []
for k, (t, s, e) in enumerate(words):
    if cur and (len(cur) >= 3 or sum(len(x[0]) for x in cur) + len(t) > 16
                or any(cur[0][1] < b <= s + 0.001 for b in breaks)
                or in_box(s) != in_box(cur[0][1])):
        groups.append(cur); cur = []
    cur.append([t, s, e])
    if t[-1] in ".,?!":
        groups.append(cur); cur = []
if cur:
    groups.append(cur)

def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

ev = []
for gi, g in enumerate(groups):
    s = g[0][1]
    nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else DUR
    e = min(nxt, g[-1][2] + 0.6)
    if in_box(s) or s < 3.0:   # título ocupa os 3 primeiros segundos
        continue
    txt = " ".join(clean(x[0]) for x in g)
    ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Leg,,0,0,0,,{{\\fad(60,60)}}{txt}")

# título: linha fina + linha grande
# título escalonado como no exemplo da Ketlen: linha fina à esquerda, linha grossa deslocada
# para a direita e colada logo embaixo (medidas tiradas renderizando o texto)
TIT1, TIT2 = "Primeiro dia com", "aparelho auditivo"
ev.append(f"Dialogue: 2,{ts(0)},{ts(3.0)},Tit1,,0,0,0,,{{\\an1\\pos({{T1X}},{{T1Y}})\\fad(120,200)}}{TIT1}")
ev.append(f"Dialogue: 2,{ts(0.25)},{ts(3.0)},Tit2,,0,0,0,,{{\\an1\\pos({{T2X}},{{T2Y}})\\fad(80,200)}}{TIT2}")
# legenda corrida durante o título fica embaixo, como no resto
for g in groups:
    if g[0][1] < 3.0:
        nxt = next((h[0][1] for h in groups if h[0][1] > g[0][1]), DUR)
        ev.append(f"Dialogue: 0,{ts(g[0][1])},{ts(min(nxt, g[-1][2] + 0.6))},Leg,,0,0,0,,{{\\fad(60,60)}}"
                  + " ".join(clean(x[0]) for x in g))

pop_in = "\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)"
BORDA = "\\xbord22\\ybord3"   # borda fina da caixa, como no '90 decibéis'
for b in boxes:
    t0, t1, txt = b[:3]
    pos = f"\\an5\\pos({b[3][0]},{b[3][1]})" if len(b) == 4 else ""
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Box,,0,0,0,,{{{pos}{BORDA}\\fad(0,80){pop_in}}}{txt}")
for t0, t1, txt in chest:
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1 + 0.2)},Big,,0,0,0,,{{\\an2\\pos(540,1330)\\fad(0,80){pop_in}}}{txt}")
for t0, t1, txt in big:
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Big,,0,0,0,,{{\\pos(540,380)\\fad(0,80){pop_in}}}{txt}")
for n, (t0, txt) in enumerate(stack):
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(stack_end)},Box,,0,0,0,,{{\\an5\\pos(540,{330 + n * 108}){BORDA}\\fad(0,100){pop_in}}}{txt}")
# efeito de digitação: uma letra por vez (as que faltam ficam invisíveis para não pular de lugar)
LETRA = 0.09
for t0, t1, txt in mega:
    for k in range(1, len(txt) + 1):
        a = t0 + (k - 1) * LETRA
        b = t0 + k * LETRA if k < len(txt) else t1
        vis, inv = txt[:k], txt[k:]
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Mega,,0,0,0,,{{\\pos(650,420)}}{vis}{{\\alpha&HFF&}}{inv}")

TIT1_FS, TIT2_FS = 125, 150
def monta(evs):
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,KB Jost Light,90,&H10FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,-3,0,1,0,2,2,90,140,{LEG_MV},1
Style: Tit1,KB Jost Light,{TIT1_FS},{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-3,0,1,0,2,5,40,40,0,1
Style: Tit2,KB Poppins Bold,{TIT2_FS},{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-6,0,1,0,3,5,40,40,0,1
Style: Big,KB Poppins Bold,128,{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-5,0,1,0,3,5,40,40,0,1
Style: Box,KB Poppins Bold,88,{ROXO},&H000000FF,{CAIXA},{CAIXA},0,0,0,0,100,100,-4,0,3,4,0,2,90,140,{LEG_MV},1
Style: Mega,KB Poppins Black,240,{ROXO},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,-4,0,1,0,0,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(evs) + "\n"
# o libass ignora o Spacing do estilo, então o espaçamento (letras juntinhas) vai como \\fsp
SP = {"Leg": -3, "Tit1": -6, "Tit2": -5, "Big": -4, "Box": -3, "Mega": -8}
def junta(line):
    if not line.startswith("Dialogue:"):
        return line
    st = line.split(",")[3]
    head, txt = line.split(",,0,0,0,,", 1)
    tag = f"\\fsp{SP[st]}"
    txt = "{" + tag + txt[1:] if txt.startswith("{") else "{" + tag + "}" + txt
    return head + ",,0,0,0,," + txt
def ass_doc(evs):
    return "\n".join(junta(l) for l in monta(evs).split("\n"))
def medir(style, txt):
    line = f"Dialogue: 0,0:00:00.00,0:00:01.00,{style},,0,0,0,,{{\\an1\\pos(0,1500)}}{txt}"
    open("_medir.ass", "w").write(ass_doc([line]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:d=0.1",
                    "-vf", "ass=_medir.ass:fontsdir=../fonts3", "-frames:v", "1", "_medir.png"], check=True)
    from PIL import Image
    import numpy as np
    a = np.array(Image.open("_medir.png").convert("L")); ys, xs = np.where(a > 100)
    return xs.min(), xs.max(), ys.min() - 1500, ys.max() - 1500
# título como o do BERA: fina à esquerda (x 100-~610), Poppins deslocada à direita até a margem
for _ in range(3):
    x0, x1, _, _ = medir("Tit1", TIT1); TIT1_FS = round(TIT1_FS * 560 / (x1 - x0))
    x0, x1, _, _ = medir("Tit2", TIT2); TIT2_FS = round(TIT2_FS * 700 / (x1 - x0))
a0, a1, atop, abot = medir("Tit1", TIT1)
b0, b1, btop, bbot = medir("Tit2", TIT2)
T1X, T1Y = 100 - a0, 360 - atop
T2X, T2Y = 988 - b1, T1Y + abot + 4 - btop
ev = [l.replace("{T1X}", str(T1X)).replace("{T1Y}", str(T1Y)).replace("{T2X}", str(T2X)).replace("{T2Y}", str(T2Y)) for l in ev]
print(f"título fs {TIT1_FS}/{TIT2_FS}: fina x {T1X + a0}-{T1X + a1}, Poppins x {T2X + b0}-{T2X + b1}, y {T1Y + atop}-{T2Y + bbot}")
open("legendas.ass", "w").write(ass_doc(ev))

# ---------- zoom (expressão do zoompan) ----------
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
inputs = ["-i", SRC, "-loop", "1", "-t", str(END + 0.5), "-i", "logo_card.png"]
for n in names:
    inputs += ["-i", f"../work/sfx/{n}.wav"]
idx = {n: 2 + k for k, n in enumerate(names)}
vol = {"swish_capcut": 0.45, "clique_caneta": 0.45, "teclado": 0.45}

fc = [
    f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,"
    f"zoompan=z='{zexpr}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.22':d=1:s={W}x{H}:fps=30,"
    f"ass=legendas.ass:fontsdir=../fonts3,format=yuv420p,settb=1/30,setpts=N/TB/30[base]",
    f"[1:v]fps=30,scale={W}:{H},format=yuv420p,settb=1/30,setpts=N/TB/30[logo]",
    f"[base]tpad=stop_mode=clone:stop_duration=0.4[basep]",
    f"[basep][logo]xfade=transition=fade:duration=0.35:offset={DUR + 0.05}[v]",   # logo só depois da última palavra
]
splits = {}
for n in names:
    cnt = sum(1 for m, _ in sfx if m == n)
    fc.append(f"[{idx[n]}:a]asplit={cnt}" + "".join(f"[{n}{k}]" for k in range(cnt)))
    splits[n] = 0
mix = ["[voz]"]
fc.append(f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,afade=out:st={DUR - 0.03}:d=0.03,apad=pad_dur={END}[voz]")
for k, (n, t) in enumerate(sfx):
    lab = f"{n}{splits[n]}"; splits[n] += 1
    ms = int(t * 1000)
    fc.append(f"[{lab}]adelay={ms}|{ms},volume={vol[n]}[s{k}]")
    mix.append(f"[s{k}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first[a]")

cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
       "-map", "[v]", "-map", "[a]", "-t", str(DUR + END),
       "-c:v", "libx264", "-preset", ("slow" if CRF in ("16", "17", "18") else "medium"), "-crf", CRF, "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT]
print(f"{len(groups)} grupos de legenda, {len(sfx)} efeitos sonoros")
if "--so-legenda" not in sys.argv:
    subprocess.run(cmd, check=True)
