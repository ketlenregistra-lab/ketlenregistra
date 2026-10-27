"""Monta a prévia do Reels (BERA) no padrão Kathileenn Bahia."""
import json, re, subprocess, sys

W, H = 1080, 1920
SRC = "../drive/para_editar.mov"
DUR = 92.96          # fim do clipe: ela fala até o último quadro
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
    if t == "P" and words[i + 1][0].startswith(".A"):
        fixed.append(["PEATE,", s, words[i + 2][2]]); i += 3; continue
    t = {"Bera,": "BERA,", "Revocados": "Evocados"}.get(t, t)
    fixed.append([t, s, e]); i += 1
words = fixed

def clean(t):
    keep = t.strip(".,?!")
    return keep if keep.isupper() and len(keep) > 1 else keep.lower()

# ---------- ênfases ----------
# caixas roxas: substituem a legenda corrida naquele trecho
boxes = [
    (13.04, 14.16, "PEATE", (895, 790)),        # onde a Ketlen marcou: na ponta do dedo, fora do rosto
    (28.54, 29.26, "testa"),
    (29.58, 31.02, "atrás dos ouvidos"),
    (33.64, 35.28, "fone pequenininho"),
    (49.72, 51.64, "cansado e com fome"),
    (69.70, 70.98, "teste da orelhinha", (540, 400)),  # acima da cabeça
    (74.42, 75.90, "internações na UTI"),
    (76.02, 77.70, "infecções ou vírus"),
    (89.34, 90.56, "me chama no direct"),
]
# palavra grande branca (Poppins) acima da cabeça
big = [
    (18.86, 20.0, "Eletrodos"),
    (86.74, 87.62, "Até em adultos"),
]
# lista que entra item a item
stack = [(41.50, "Não tem agulhas"), (42.78, "Não dói"), (43.76, "Não incomoda")]  # caixas roxas acima da cabeça
stack_end = 45.0
# palavra gigante roxa (Modern -> Poppins Black)
mega = [(45.00, 46.50, "DICA")]

# zoom: (tipo, início, fim, intensidade). suave = keyframe in/out; seco = corte para frente
zooms = [
    ("suave", 12.9, 17.6, 1.18),
    ("seco", 18.86, 20.0, 1.15),
    ("seco", 24.96, 25.92, 1.18),
    ("suave", 33.5, 39.8, 1.15),
    ("seco", 41.50, 45.0, 1.22),
    ("suave", 45.0, 54.6, 1.12),
    ("suave", 57.6, 62.5, 1.14),
    ("seco", 69.70, 72.7, 1.25),
    ("suave", 73.3, 83.4, 1.14),
    ("seco", 86.74, 87.62, 1.22),
    ("suave", 89.2, 92.9, 1.12),
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
chest = [(24.96, 25.92, "Não dói")]
# só as caixas sem posição própria ficam no lugar da legenda
replace = [b[:3] for b in boxes if len(b) == 3] + chest
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
ev.append(f"Dialogue: 2,{ts(0)},{ts(3.0)},Tit1,,0,0,0,,{{\\an1\\pos(100,452)\\fad(120,200)}}Você conhece o")
ev.append(f"Dialogue: 2,{ts(0.25)},{ts(3.0)},Tit2,,0,0,0,,{{\\an1\\pos(308,568)\\fad(80,200)}}exame BERA?")
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
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(stack_end)},Box,,0,0,0,,{{\\an5\\pos(540,{340 + n * 112}){BORDA}\\fad(0,100){pop_in}}}{txt}")
# efeito de digitação: uma letra por vez (as que faltam ficam invisíveis para não pular de lugar)
LETRA = 0.13
for t0, t1, txt in mega:
    for k in range(1, len(txt) + 1):
        a = t0 + (k - 1) * LETRA
        b = t0 + k * LETRA if k < len(txt) else t1
        vis, inv = txt[:k], txt[k:]
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Mega,,0,0,0,,{{\\pos(540,400)}}{vis}{{\\alpha&HFF&}}{inv}")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,KB Jost Light,90,&H10FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,-3,0,1,0,2,2,90,140,{LEG_MV},1
Style: Tit1,KB Jost Light,125,{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-3,0,1,0,2,5,40,40,0,1
Style: Tit2,KB Poppins Bold,185,{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-6,0,1,0,3,5,40,40,0,1
Style: Big,KB Poppins Bold,128,{BRANCO},&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,-5,0,1,0,3,5,40,40,0,1
Style: Box,KB Poppins Bold,88,{ROXO},&H000000FF,{CAIXA},{CAIXA},0,0,0,0,100,100,-4,0,3,4,0,2,90,140,{LEG_MV},1
Style: Mega,KB Poppins Black,320,{ROXO},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,-4,0,1,0,0,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
# o libass ignora o Spacing do estilo, então o espaçamento (letras juntinhas) vai como \\fsp
SP = {"Leg": -3, "Tit1": -6, "Tit2": -4, "Big": -4, "Box": -3, "Mega": -8}
def junta(line):
    if not line.startswith("Dialogue:"):
        return line
    st = line.split(",")[3]
    head, txt = line.split(",,0,0,0,,", 1)
    tag = f"\\fsp{SP[st]}"
    txt = "{" + tag + txt[1:] if txt.startswith("{") else "{" + tag + "}" + txt
    return head + ",,0,0,0,," + txt
ass = "\n".join(junta(l) for l in ass.split("\n"))
open("legendas.ass", "w").write(ass)

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
    inputs += ["-i", f"sfx/{n}.wav"]
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
       "-c:v", "libx264", "-preset", "medium", "-crf", CRF, "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT]
print(f"{len(groups)} grupos de legenda, {len(sfx)} efeitos sonoros")
subprocess.run(cmd, check=True)
