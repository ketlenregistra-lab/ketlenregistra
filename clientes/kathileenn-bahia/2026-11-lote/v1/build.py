"""Vídeo 1 — "Calo" ou "carro"? Até quando a troca de letras é normal. Legenda fina (Montserrat)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"fonaudiólogas,": "fonoaudiólogas,", "consomontais": "consonantais", "afono": "fono",
       "Bill": "bio", (49.12, "um"): "uma"}
words = carregar_palavras("transcricao.json", FIX, cortar_depois=95.65)   # "E aí" do final fica de fora
DUR = 95.62

LEG_Y = 1250        # na altura do peito/braços (abaixo disso é a calça branca)
TOPO = 500          # vazio de cima (parede), acima da cabeça
PEITO = 1190

ev, ocupado, sfx = [], [], []
def big(t0, t1, txt, y=TOPO, fs=112, cor=ROXO):
    ev.append(ev_big(t0, t1, txt, 540, y, cor, fs)); ocupado.append((t0, t1)); sfx.append(("clique_caneta", t0))
def box(t0, t1, txt, y=PEITO, fs=None):
    ev.append(ev_box(t0, t1, txt, 540, y, "notif", fs)); ocupado.append((t0, t1)); sfx.append(("clique_caneta", t0))
def digita(t0, t1, linhas, y=TOPO):
    txt = "\\N".join(linhas)
    ev.extend(ev_typing(t0, t1, txt, 140, y, "notif", fs=74, letra=min(0.05, 1.2 / len(txt))))
    sfx.append(("teclado", t0 - 0.075))

# "calo" × "carro": as duas combinações para a pessoa entender
ev.append(ev_big(3.42, 6.05, "{\\s1}calo", 540, TOPO - 40, BRANCO, 120)); sfx.append(("clique_caneta", 3.42))
ev.append(ev_big(5.34, 6.05, "carro", 540, TOPO + 100, ROXO, 130)); sfx.append(("clique_caneta", 5.34))
ocupado.append((3.42, 6.05))

big(10.14, 11.22, "Fonoaudiólogas", fs=96)
box(15.44, 16.78, "tempo certo")
box(17.86, 19.0, "R do carro")
big(20.54, 22.26, "até 3 anos e meio", fs=92)
box(22.74, 24.16, "R vibrante")
box(24.76, 26.48, "arara · cadeira")
big(27.40, 29.36, "até 5 anos", fs=104)
box(32.14, 33.50, "encontros consonantais", fs=62)
box(34.80, 35.62, "praça")
big(37.94, 39.30, "5 anos e meio", fs=104)
big(48.76, 49.64, "procure uma fono", fs=88)
box(49.66, 50.90, "Dica importante")
box(51.68, 53.52, "não precisa corrigir")
big(58.74, 60.78, "Seu modelo ajuda", fs=92)
box(82.12, 83.66, "vários contextos")
box(84.12, 84.90, "frases diferentes")
box(92.34, 94.76, "WhatsApp · link da bio", fs=64)

# brincando com o carrinho: frases aparecem digitando, no vazio de cima
digita(67.90, 71.40, ["Olha só, filho,", "que carro lindo!"])
digita(71.42, 73.52, ["Pra onde esse carro", "tá indo?"])
digita(73.54, 77.04, ["Nossa! O pneu", "do carro furou?"])
digita(77.06, 80.46, ["Onde a gente vai", "abastecer esse carro?"])
ocupado.append((67.90, 80.46))

zooms = [("seco", 10.14, 11.22, 1.15), ("suave", 20.3, 22.3, 1.12), ("seco", 27.40, 29.36, 1.15),
         ("seco", 37.94, 39.30, 1.15), ("seco", 48.76, 49.64, 1.18), ("suave", 58.6, 60.8, 1.12),
         ("suave", 88.6, 95.5, 1.10)]
for k, t0, t1, z in zooms:
    if k == "seco" and not any(abs(t - t0) < 0.4 for _, t in sfx):
        sfx.append(("swish_capcut", t0 - 0.05))

card_final("card_final.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, card="card_final.png"))
