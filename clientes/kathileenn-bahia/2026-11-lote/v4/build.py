"""Vídeo 4 — Janeiro Branco: ouvir mal também cansa a cabeça. Legenda Poppins, destaques em branco,
trilha suave bem baixinha."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

words = carregar_palavras("transcricao.json", {})
DUR = float(os.environ.get("DUR", "50.30"))
cabeca = json.load(open("cabeca.json"))

LEG_Y = 1330
PEITO = 1290
ev, ocupado, sfx = [], [], []

def em_cima(texto, perto, estilo, fs, altura, ate=None):
    tp = tempos(words, texto, perto)
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.9)
    y = acima_da_cabeca(cabeca, tp[0], fim, altura)
    ev.extend(ev_fala(tp, fim, texto, 540, y, estilo, fs))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))

def linhas_em_cima(linhas, perto, estilo, fs, dy, fontes=None, ate=None, clique_por_linha=True):
    """Cada linha entra quando ela começa a falar a linha, bem próximas, com clique."""
    tp = tempos(words, " ".join(linhas), perto, janela=4)
    inicio, n = [], 0
    for ln in linhas:
        inicio.append(tp[n]); n += len(ln.split())
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.9)
    alt = (len(linhas) - 1) * dy + (fs if isinstance(fs, int) else max(fs))
    y = acima_da_cabeca(cabeca, inicio[0], fim, alt)
    y0 = y - (len(linhas) - 1) * dy // 2
    ev.extend(ev_linhas(inicio, fim, linhas, 540, y0, dy, estilo, fs, fontes))
    ocupado.append((inicio[0], fim))
    sfx.extend(("clique_caneta", t) for t in (inicio if clique_por_linha else inicio[:1]))

# "Quem ouve mal / faz força o dia inteiro": letra fininha + grossa, bem próximas, clique em cada linha
linhas_em_cima(["Quem ouve mal", "faz força o dia inteiro"], 5.48, BRANCO, [66, 92], 84,
               ["KB Montserrat Regular", None])
em_cima("Cansa", 15.00, BRANCO, 130, 130)
# festas, almoços de família, telefone: letra roxa com borda, um por vez com clique
linhas_em_cima(["festas", "almoços de família", "telefone"], 18.32, "claro", 74, 104, ate=22.65)
em_cima("JANEIRO", 23.66, BRANCO, 150, 150)
em_cima("SAÚDE MENTAL", 27.86, BRANCO, 112, 120)
# "Cuidar da sua audição / também é cuidar / da sua cabeça": tudo branco, uma linha por vez
linhas_em_cima(["Cuidar da sua audição", "também é cuidar", "da sua cabeça"], 28.66, BRANCO, 84, 96, ate=32.65)
# avaliação auditiva: letra roxa com borda branca, na altura do peito
tp = tempos(words, "avaliação auditiva", 44.06)
ev.extend(ev_fala(tp, 45.40, "Avaliação auditiva", 540, PEITO, "claro", 80))
ocupado.append((tp[0], 45.40)); sfx.append(("clique_caneta", tp[0]))
em_cima("Link na bio", 49.30, BRANCO, 104, 110)

zooms = [("suave", 5.4, 8.2, 1.08), ("seco", 23.66, 24.90, 1.12), ("suave", 28.6, 32.6, 1.10),
         ("suave", 40.5, 45.3, 1.08)]
# em JANEIRO fica o clique (o swish fica guardado para os zooms em que ela pedir)

trilha_suave("trilha.wav", DUR + 5)
card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms,
           card="card_logo.png", musica="trilha.wav", musica_vol=0.018))
