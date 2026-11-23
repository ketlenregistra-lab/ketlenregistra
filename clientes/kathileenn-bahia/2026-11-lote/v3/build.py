"""Vídeo 3 — Piscina, praia e ouvido. Legenda mais grossinha (Poppins)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"Fotonete?": "Cotonete?", "Fotonete": "Cotonete", "sozinho.": "sozinha.", (77.06, "sabe"): "salva"}
words = carregar_palavras("transcricao.json", FIX)
DUR = float(os.environ.get("DUR", "81.70"))

LEG_Y = 1380
PEITO = 1310
TOPO = 470

ev, ocupado, sfx = [], [], []
def box(t0, t1, txt, y=PEITO, fs=None, cobre=True):
    ev.append(ev_box(t0, t1, txt, 540, y, "notif", fs)); sfx.append(("clique_caneta", t0))
    if cobre: ocupado.append((t0, t1))

# frases de abertura no vazio de cima
box(1.34, 4.95, "Antes da piscina", y=TOPO - 50, fs=70, cobre=False)
box(2.88, 4.95, "olha esses cuidados com o ouvido", y=TOPO + 50, fs=56, cobre=False)
ocupado.append((1.34, 4.95))
# dicas em destaque
box(6.46, 10.75, "Seca bem a parte de fora\\Ndo ouvido com a toalha", y=TOPO, fs=74, cobre=False)
ocupado.append((6.46, 10.75))
box(11.16, 12.95, "Só a parte de fora!")
box(16.22, 18.48, "Inclina a cabeça\\Npara o lado", y=TOPO, fs=84, cobre=False)
ocupado.append((16.22, 18.48))
box(20.74, 22.95, "Cotonete não!")
box(23.74, 26.40, "empurra para dentro")
box(37.50, 40.70, "Procure o OTORRINO", y=TOPO, fs=78, cobre=False)
ocupado.append((37.50, 40.70))
box(49.86, 52.20, "tampões personalizados", fs=64)
box(66.62, 67.50, "função dupla")
box(68.24, 69.95, "ABAFADOR", y=TOPO, fs=96, cobre=False)
ocupado.append((68.24, 69.95))
box(76.82, 81.40, "Salve para as férias!", fs=66)

# imagens pequenas no vazio de cima
preparar_imagem("cotonete.jpg", "img_cotonete.png", 300, raio=28, borda=8, fundo_branco=True)
preparar_imagem("tampao.jpg", "img_tampao.png", 300, raio=28, borda=8)
from PIL import Image
hc = Image.open("img_cotonete.png").height
ht = Image.open("img_tampao.png").height
imagens = [(20.74, 26.40, "img_cotonete.png", (W - 316) // 2, 290),
           (49.86, 56.90, "img_tampao.png", (W - 316) // 2, 290)]

zooms = [("suave", 13.06, 15.95, 1.10), ("seco", 27.06, 29.30, 1.12), ("suave", 40.78, 47.40, 1.08),
         ("seco", 64.80, 66.60, 1.12), ("suave", 70.0, 76.5, 1.08)]
for k, t0, t1, z in zooms:
    if not any(abs(t - t0) < 0.4 for _, t in sfx):
        sfx.append(("swish_capcut", t0 - 0.05))

card_final("card_final.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           card="card_final.png"))
