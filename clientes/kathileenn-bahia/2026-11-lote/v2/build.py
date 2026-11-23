"""Vídeo 2 — Chupeta depois dos 3 anos atrapalha a fala? Legenda fina (Montserrat)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from destaque_helper import *

FIX = {"tubiu": "subiu", "ferra.": "serra.", "cesseio.": "ceceio."}
words = carregar_palavras("transcricao.json", FIX)
DUR = 128.76
cabeca = json.load(open("cabeca.json"))
LEG_Y = 1360
D, destaque, linhas = criar(words, cabeca, 1300)

# CHUPETA no centro, digitando, com o som de teclado (baixinho)
yc = acima_da_cabeca(cabeca, 4.96, 7.0, 150)
e_chup, _ = ev_digitando(4.96, 7.00, "CHUPETA", 540, yc, ROXO, fs=150, cps=12)
D.add(4.96, 7.00, lambda t1: e_chup, [("teclado", 4.96 - 0.075)])

destaque("ossos da face", 26.98, "notif", 74, texto="Ossos da face")
destaque("arcadas dentárias", 28.80, "notif", 74, texto="Arcadas dentárias")
destaque("mais prolongado", 35.84, "notif", 74, texto="Mais prolongado")
destaque("S X Z", 50.16, "notif", 80, texto="S, X, Z")
destaque("ceceio", 56.08, ROXO, 140, texto="CECEIO", ate=57.05)      # aparece de uma vez, com clique
linhas(["o sapo", "subiu a serra"], 59.30, BRANCO, [80, 118], 92, textos=["O sapo", "subiu a serra"],
       fontes=["KB Montserrat Regular", None], onde=1270, ate=62.72)
destaque("mais fácil vai ser o desmame", 70.18, "notif", 64, texto="Mais fácil vai ser o desmame")
destaque("troca inteligente", 83.66, "notif", 74, texto="Troca inteligente")
destaque("formato da boca", 112.98, "notif", 74, texto="Formato da boca")
destaque("dentes para frente", 117.12, "notif", 74, texto="Dentes para frente")
destaque("conta nos comentários", 124.88, "notif", 70, texto="Conta nos comentários", ate=128.70)

ev, ocupado, sfx = D.render()
# linhas no rosto só enquanto ela fala "ossos da face"
t_ossos = tempos(words, "ossos da face", 26.98)
ev.extend(ev_linhas_rosto("rosto.json", t_ossos[0], fim_fala(words, t_ossos[-1] + 0.01) + 0.2))
ocupado.append((42.20, 48.56))        # desenho do céu da boca em tela cheia, só a voz dela

preparar_imagem("chupeta_plantada.png", "img_plantada.png", 500, raio=34, borda=0)
preparar_imagem("chupeta_baloes.png", "img_baloes.png", 470, raio=34, borda=0)
imagens = [(86.78, 93.05, "img_plantada.png", (W - 500) // 2, 275),
           (98.48, 105.05, "img_baloes.png", (W - 470) // 2, 275),
           (42.20, 48.56, "ceu_da_boca.png", 0, 0)]
sfx += [("clique_caneta", 86.78), ("clique_caneta", 98.48), ("clique_caneta", 42.20)]

zooms = [("seco", 18.90, 22.20, 1.12), ("seco", 59.30, 62.72, 1.15), ("suave", 66.7, 72.9, 1.10),
         ("seco", 83.66, 85.40, 1.12), ("suave", 119.8, 128.3, 1.10)]
sfx += [("swish_capcut", t0) for k, t0, t1, z in zooms if k == "seco"]

card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           card="card_logo.png"))
