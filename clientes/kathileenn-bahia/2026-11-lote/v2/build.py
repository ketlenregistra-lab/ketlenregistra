"""Vídeo 2 — Chupeta depois dos 3 anos atrapalha a fala? Legenda fina (Montserrat)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"tubiu": "subiu", "ferra.": "serra.", "cesseio.": "ceceio."}
words = carregar_palavras("transcricao.json", FIX)
DUR = 128.76
cabeca = json.load(open("cabeca.json"))

LEG_Y = 1360
ev, ocupado, sfx = [], [], []

def em_cima(texto, perto, estilo, fs, altura, ate=None):
    tp = tempos(words, texto, perto)
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.9)
    y = acima_da_cabeca(cabeca, tp[0], fim, altura)
    ev.extend(ev_fala(tp, fim, texto, 540, y, estilo, fs))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))

def digita_em_cima(t0, t1, txt, fs, altura, cor=ROXO):
    y = acima_da_cabeca(cabeca, t0, t1, altura)
    e, teclas = ev_digitando(t0, t1, txt, 540, y, cor, fs=fs, cps=12)
    ev.extend(e); sfx.extend(("tecla", t) for t in teclas); ocupado.append((t0, t1))

# CHUPETA no centro, digitando, quando ela mostra "essa mocinha aqui"
digita_em_cima(4.96, 7.00, "CHUPETA", 150, 150)

# linhas no rosto só enquanto ela fala "ossos da face"
ev.extend(ev_linhas_rosto("rosto.json", 26.98, 28.20))
em_cima("Ossos da face", 26.98, "notif", 74, 90, ate=28.20)
em_cima("Arcadas dentárias", 28.80, "notif", 74, 90)
em_cima("Mais prolongado", 35.84, "notif", 74, 90)
# "esse esquema": tela cheia com o desenho do céu da boca, só a voz dela
ocupado.append((42.20, 48.56))
em_cima("S, X, Z", 50.16, "notif", 80, 90)
digita_em_cima(56.08, 57.05, "CECEIO", 140, 140)

# "O sapo subiu a serra": legenda fina + branca grossa, linhas próximas
tp = tempos(words, "O sapo subiu a serra", 59.30)
ev.extend(ev_linhas([tp[0], tp[2]], 62.72, ["O sapo", "subiu a serra"], 540, 1225, 92, BRANCO,
                    [80, 118], ["KB Montserrat Regular", None]))
sfx.append(("clique_caneta", tp[0])); ocupado.append((tp[0], 62.72))

em_cima("Mais fácil vai ser o desmame", 70.18, "notif", 62, 90)
em_cima("Troca inteligente", 83.66, "notif", 74, 90)
em_cima("Formato da boca", 112.98, "notif", 74, 90)
em_cima("Dentes para frente", 117.12, "notif", 74, 90)
em_cima("Conta nos comentários", 124.88, "notif", 70, 90, ate=128.70)

# imagens desenhadas, no vazio de cima
preparar_imagem("chupeta_plantada.png", "img_plantada.png", 500, raio=34, borda=0)
preparar_imagem("chupeta_baloes.png", "img_baloes.png", 470, raio=34, borda=0)
imagens = [(86.78, 93.05, "img_plantada.png", (W - 500) // 2, 275),
           (98.48, 105.05, "img_baloes.png", (W - 470) // 2, 275),
           (42.20, 48.56, "ceu_da_boca.png", 0, 0)]
sfx += [("clique_caneta", 86.78), ("clique_caneta", 98.48), ("clique_caneta", 42.20)]

zooms = [("seco", 18.90, 22.20, 1.12), ("seco", 59.30, 62.72, 1.15), ("suave", 66.7, 72.9, 1.10),
         ("seco", 83.66, 85.40, 1.12), ("suave", 119.8, 128.3, 1.10)]
for k, t0, t1, z in zooms:
    if k == "seco":
        sfx.append(("swish_capcut", t0))

card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           card="card_logo.png"))
