"""Vídeo 2 — Chupeta depois dos 3 anos atrapalha a fala? Legenda fina (Montserrat)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"tubiu": "subiu", "ferra.": "serra.", "cesseio.": "ceceio."}
words = carregar_palavras("transcricao.json", FIX)
DUR = 128.76

LEG_Y = 1360
PEITO = 1300
TOPO = 520

ev, ocupado, sfx = [], [], []
def box(t0, t1, txt, y=PEITO, fs=None):
    ev.append(ev_box(t0, t1, txt, 540, y, "notif", fs)); ocupado.append((t0, t1)); sfx.append(("clique_caneta", t0))

# CHUPETA em destaque, digitando, quando ela mostra "essa mocinha aqui"
ev.extend(ev_typing(4.96, 7.0, "CHUPETA", 235, TOPO, ROXO, fs=150, letra=0.09))
sfx.append(("teclado", 4.96 - 0.075)); ocupado.append((4.96, 7.0))

# ossos da face e arcadas: linhas pontilhadas roxas no rosto + caixinhas
ev.extend(ev_linhas_rosto("rosto.json", 26.98, 30.30))
box(26.98, 28.20, "ossos da face")
box(28.22, 30.30, "arcadas dentárias")

box(34.96, 36.98, "uso prolongado")
# "esse esquema": tela cheia com o desenho do céu da boca, só a voz dela
ocupado.append((42.20, 48.56))
box(50.16, 52.24, "S · X · Z")
box(55.86, 57.00, "ceceio")

# "O sapo subiu a serra": combinação legenda fina + branca grossa
ev.append(ev_big(59.30, 62.72, "O sapo", 540, 1215, BRANCO, 80, "KB Montserrat Regular"))
ev.append(ev_big(60.56, 62.72, "subiu a serra", 540, 1320, BRANCO, 118))
sfx.append(("clique_caneta", 59.30)); ocupado.append((59.30, 62.72))

box(70.18, 72.96, "mais fácil o desmame", fs=64)
box(83.18, 85.40, "troca inteligente")
box(112.98, 114.90, "formato da boca")
box(117.12, 118.20, "dentes para frente")
box(124.88, 128.40, "Conta nos comentários!", fs=64)

# imagens desenhadas, no vazio de cima
preparar_imagem("chupeta_plantada.png", "img_plantada.png", 500, raio=34, borda=0)
preparar_imagem("chupeta_baloes.png", "img_baloes.png", 470, raio=34, borda=0)
imagens = [(86.78, 93.05, "img_plantada.png", (W - 500) // 2, 275),
           (98.48, 105.05, "img_baloes.png", (W - 470) // 2, 275),
           (42.20, 48.56, "ceu_da_boca.png", 0, 0)]
sfx += [("clique_caneta", 86.78), ("clique_caneta", 98.48), ("clique_caneta", 42.20)]

zooms = [("seco", 18.90, 22.20, 1.12), ("seco", 59.30, 62.72, 1.15), ("suave", 66.7, 72.9, 1.10),
         ("seco", 83.18, 85.40, 1.12), ("suave", 119.8, 128.3, 1.10)]
for k, t0, t1, z in zooms:
    if k == "seco" and not any(abs(t - t0) < 0.4 for _, t in sfx):
        sfx.append(("swish_capcut", t0 - 0.05))

card_final("card_final.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           card="card_final.png"))
