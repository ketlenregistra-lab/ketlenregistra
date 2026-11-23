"""Vídeo 4 — Janeiro Branco: ouvir mal também cansa a cabeça. Legenda Poppins, destaques em branco,
trilha suave bem baixinha."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

words = carregar_palavras("transcricao.json", {})
DUR = float(os.environ.get("DUR", "50.40"))

LEG_Y = 1330
TOPO = 460

ev, ocupado, sfx = [], [], []
def big(t0, t1, txt, y=TOPO, fs=104, cobre=True):
    ev.append(ev_big(t0, t1, txt, 540, y, BRANCO, fs))
    if cobre: ocupado.append((t0, t1))

# título (texto na tela do roteiro)
ev.append(ev_big(0.0, 4.95, "Ouvir mal também", 540, TOPO - 50, BRANCO, 64, "KB Poppins Medium"))
ev.append(ev_big(0.25, 4.95, "cansa a cabeça", 540, TOPO + 45, BRANCO, 112))
big(6.38, 8.20, "faz força o dia inteiro", fs=84)
big(15.00, 15.95, "cansa", fs=130)
# o que a pessoa começa a evitar: entra um por vez
ev.append(ev_big(18.10, 22.65, "festas", 540, TOPO - 90, BRANCO, 78))
ev.append(ev_big(19.38, 22.65, "almoços de família", 540, TOPO, BRANCO, 78))
ev.append(ev_big(21.02, 22.65, "telefone", 540, TOPO + 90, BRANCO, 78))
ocupado.append((18.10, 22.65))
big(23.52, 24.90, "JANEIRO", fs=150)
big(27.86, 28.62, "saúde mental", fs=104)
# "cuidar da sua audição também é cuidar da sua cabeça": letra roxa com borda branca
ev.append(ev_box(28.66, 32.65, "Cuidar da sua audição\\Ntambém é cuidar\\Nda sua cabeça", 540, TOPO, "claro", 70))
ocupado.append((28.66, 32.65)); sfx.append(("clique_caneta", 28.66))
big(44.06, 45.30, "avaliação auditiva", fs=92)
big(48.68, 50.00, "link na bio", fs=104)

zooms = [("suave", 5.4, 8.2, 1.08), ("seco", 23.52, 24.90, 1.12), ("suave", 28.6, 32.6, 1.10),
         ("suave", 40.5, 45.3, 1.08)]
sfx.append(("swish_capcut", 23.47))

trilha_suave("trilha.wav", DUR + 4)
card_final("card_final.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms,
           card="card_final.png", musica="trilha.wav", musica_vol=0.018))
