"""Reels "Dúvidas com sua fono — parte 2" no padrão Kathileenn Bahia.
Legenda Destino Verdadeiro (serifada). A Ketlen já colocou o título roxo, os cards de pergunta e o
som de escrita: aqui só entram a legenda e as ênfases (Poppins, sem caixinha roxa).
Regra deste vídeo: card de pergunta na tela -> legenda embaixo (altura do corpo);
sem card (ela respondendo) -> legenda em cima."""
import json, subprocess, sys

W, H = 1080, 1920
SRC = "bruto.mov"
DUR = 89.30          # termina logo após "pra você" (o "E aí" do final fica de fora)
END = 2.2            # card do logo
OUT = sys.argv[1] if len(sys.argv) > 1 else "previa.mp4"
CRF = sys.argv[2] if len(sys.argv) > 2 else "21"
PRESET = "slow" if CRF in ("16", "17", "18") else "medium"
FONTS = "../fonts3"

LEG_TOPO = 480       # base da legenda em cima (vazio acima da cabeça)
LEG_BAIXO = 1360     # base da legenda embaixo (altura do corpo); zona segura: x 88-994, y 263-1459
camadas = json.load(open("camadas.json"))      # medido no vídeo: quando o card / título roxo estão na tela
cards = [(a - 0.2, b) for a, b in camadas["cards"]]   # folga: o card começa a surgir um pouco antes
cabeca = json.load(open("cabeca_bruto.json"))  # topo da cabeça (com cabelo), medido no vídeo
titulo_roxo = camadas["titulo"]                # "DÚVIDAS COM SUA FONO" ocupa a parte de baixo

# ---------- transcrição corrigida ----------
words = []
for s in json.load(open("transcricao.json")):
    for w in s["words"]:
        words.append([w["w"].strip(), w["s"], w["e"]])
fixed = []
for t, s, e in words:
    if s >= DUR:
        continue
    if t == "Ketlin,":
        t = "Kathileenn,"
    if t.startswith("-") and fixed:
        fixed[-1] = [fixed[-1][0] + t, fixed[-1][1], e]; continue
    if t == "um,":       # hesitação
        continue
    fixed.append([t, s, e])
words = fixed

# falas da Ketlen (abertura e perguntas): não legendar — o título roxo e os cards já mostram
fala_ketlen = [(0.0, 4.20), (6.05, 8.70), (17.40, 19.90), (30.05, 33.75), (45.80, 48.20), (60.25, 63.50)]
words = [w for w in words if not any(a <= w[1] < b for a, b in fala_ketlen)]

NOMES = {"kathileenn": "Kathileenn", "ket": "Ket", "doutora": "doutora"}
def clean(t):
    w = t.strip(".,?!…").lower()
    return NOMES.get(w, w)

# ---------- ênfases: Poppins branca, no lugar da legenda (sem caixinha) ----------
enfases = [
    (16.30, 17.40, "Pode até lesionar"),
    (20.08, 21.46, "Muito pelo contrário"),
    (29.02, 29.95, "Sentir falta"),
    (45.04, 45.80, "Interação"),
    (49.28, 50.12, "Atrapalha"),
    (58.06, 60.10, "Gritar, de jeito nenhum"),
    (64.46, 65.45, "15 dias"),
    (69.40, 70.20, "Otorrino"),
]

def em(intervals, a, b):
    return any(x0 < b and a < x1 for x0, x1 in intervals)

# ---------- legenda corrida: frases em até 2 linhas, letras juntas ----------
breaks = sorted({x for iv in cards + titulo_roxo for x in iv} | {x for e in enfases for x in e[:2]})
def in_enfase(t):
    return any(a - 0.01 <= t < b - 0.01 for a, b, _ in enfases)

LINHA = 32
groups, cur = [], []
for t, s, e in words:
    txt_len = len(" ".join(clean(x[0]) for x in cur + [[t]]))
    if cur and (txt_len > 2 * LINHA or s - cur[0][1] > 3.2
                or any(cur[0][1] < b <= s + 0.001 for b in breaks)
                or in_enfase(s) != in_enfase(cur[0][1])):
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
    k = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
    return [" ".join(ws[:k]), " ".join(ws[k:])]

def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

def posicao(s, e):
    """Card de pergunta em cima -> legenda embaixo; título roxo embaixo -> legenda em cima."""
    meio = (s + e) / 2
    if any(a <= meio <= b for a, b in cards):
        return LEG_BAIXO
    return LEG_TOPO

ev = []
for gi, g in enumerate(groups):
    s = g[0][1]
    nxt = groups[gi + 1][0][1] if gi + 1 < len(groups) else DUR
    e = min(nxt, g[-1][2] + 0.5)
    if in_enfase(s):
        continue                       # a ênfase aparece no lugar (sem palavra repetida)
    if any(a <= (s + e) / 2 <= b for a, b in cards):
        continue                       # card de pergunta na tela: sem legenda
    txt = " ".join(clean(x[0]) for x in g).strip()
    if not txt:
        continue
    y = posicao(s, e)
    if y == LEG_TOPO:
        # só aparece depois que o card sai, some antes do próximo entrar e fica acima da cabeça
        s = max([s] + [b + 0.05 for a, b in cards if a <= s < b])
        e = min([e] + [a for a, b in cards if a > s])
        tops = [c for t, c in cabeca if s - 0.2 <= t <= e and c]
        if tops:
            y = int(max(263 + 110, min(LEG_TOPO, min(tops) - 35)))
    linhas = quebra(txt)
    for k, ln in enumerate(linhas):
        ly = y - (len(linhas) - 1 - k) * 50
        ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Leg,,0,0,0,,{{\\an2\\pos(540,{ly})\\fad(60,60)}}{ln}")

pop_in = "\\fscx70\\fscy70\\t(0,140,\\fscx100\\fscy100)"
for t0, t1, txt in enfases:
    y = posicao(t0, t1)
    if y == LEG_TOPO:
        t0 = max([t0] + [b + 0.05 for a, b in cards if a <= t0 < b])
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Big,,0,0,0,,{{\\an2\\pos(540,{y})\\fad(0,80){pop_in}}}{txt}")

# contorno escuro suave: a camisa dela é branca, sem isso a legenda some embaixo
SOMBRA = ""   # a Ketlen prefere só o branco, sem contorno
SP = {"Leg": -3, "Big": -4}
def junta(line):
    st = line.split(",")[3]
    head, txt = line.split(",,0,0,0,,", 1)
    tag = f"\\fsp{SP[st]}{SOMBRA}"
    txt = "{" + tag + txt[1:] if txt.startswith("{") else "{" + tag + "}" + txt
    return head + ",,0,0,0,," + txt

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,KB Cormorant SemiBold,74,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,0,2,153,153,0,1
Style: Big,KB Poppins Bold,100,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,0,2,153,153,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(junta(l) for l in ev) + "\n"
open("legendas.ass", "w").write(ass)

# ---------- ffmpeg (sem zoom e sem efeitos novos: a Ketlen já colocou os sons) ----------
fc = [
    f"[0:v]trim=0:{DUR},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,"
    f"ass=legendas.ass:fontsdir={FONTS},format=yuv420p,settb=1/30,setpts=N/TB/30[base]",
    f"[1:v]fps=30,scale={W}:{H},format=yuv420p,settb=1/30,setpts=N/TB/30[logo]",
    f"[base]tpad=stop_mode=clone:stop_duration=0.4[basep]",
    f"[basep][logo]xfade=transition=fade:duration=0.35:offset={DUR + 0.05}[v]",
    f"[0:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,aresample=48000,afade=out:st={DUR - 0.15}:d=0.15,apad=pad_dur={END}[a]",
]
cmd = ["ffmpeg", "-y", "-v", "error", "-i", SRC, "-loop", "1", "-t", str(END + 0.5), "-i", "logo_card.png",
       "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(DUR + END),
       "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT]
print(f"{len(groups)} grupos de legenda, {len(enfases)} ênfases")
if "--so-legenda" not in sys.argv:
    subprocess.run(cmd, check=True)
