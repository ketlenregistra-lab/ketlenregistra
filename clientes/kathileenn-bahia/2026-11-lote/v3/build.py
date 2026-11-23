"""Vídeo 3 — Piscina, praia e ouvido. Legenda mais grossinha (Poppins)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from destaque_helper import *

FIX = {"Fotonete?": "Cotonete?", "Fotonete": "Cotonete", "sozinho.": "sozinha.", (77.06, "sabe"): "salva"}
words = carregar_palavras("transcricao.json", FIX)
DUR = 83.30            # inclui a menina pulando na piscina; o fechamento vem depois do pulo
cabeca = json.load(open("cabeca.json"))
LEG_Y = 1380
D, destaque, linhas = criar(words, cabeca, 1310)

# abertura: ANTES DA PISCINA (sem caixinha) e "Cuidados com seu ouvido" (caixinha), cada um inteiro + clique
linhas(["antes da piscina", "cuidados com seu ouvido"], 1.70, [BRANCO, "notif"], [82, 60], 96,
       textos=["ANTES DA PISCINA", "Cuidados com seu ouvido"], ate=5.00)
# dicas em MAIÚSCULAS, sem caixinha, duas linhas juntinhas; cada linha entra inteira
linhas(["seca bem a parte de fora", "do ouvido com a pontinha da toalha"], 6.46, BRANCO, 64, 70,
       textos=["SECA BEM A PARTE DE FORA", "DO OUVIDO COM A PONTINHA DA TOALHA"])
destaque("só a parte de fora", 11.16, "notif", 74, texto="Só a parte de fora!", onde="peito")
linhas(["inclina a cabeça", "para o lado"], 16.22, BRANCO, 84, 88, textos=["INCLINA A CABEÇA", "PARA O LADO"])
destaque("cotonete não", 20.74, "notif", 74, texto="Cotonete não!", onde="peito", ate=22.95)
destaque("empurra a água", 23.74, "notif", 74, texto="Empurra para dentro", onde="peito",
         ate=fim_fala(words, 26.0) + 0.4)
# "Procure o otorrino" entra inteiro quando ela chega no "o otorrino"
destaque("o otorrino", 39.44, "notif", 78, texto="Procure o OTORRINO")
destaque("tampões personalizados", 49.86, "notif", 64, texto="Tampões personalizados", onde="peito", ate=52.20)
destaque("função dupla", 66.62, "notif", 74, texto="Função dupla", onde="peito")
destaque("abafador", 68.98, BRANCO, 110, texto="ABAFADOR")
destaque("salva esse vídeo", 77.06, "notif", 74, texto="Salva esse vídeo", onde="peito")

ev, ocupado, sfx = D.render()

# imagens pequenas, como camada ATRÁS da cabeça (a pessoa fica na frente)
preparar_imagem("cotonete.jpg", "img_cotonete.png", 230, raio=26, borda=7, fundo_branco=True)
preparar_imagem("tampao.jpg", "img_tampao.png", 230, raio=26, borda=7)
imagens = [(20.74, 22.95, "img_cotonete.png", 600, 400, "atras"),     # na cabeça da menina, não da doutora
           (49.86, 52.20, "img_tampao.png", 650, 300, "atras")]

zooms = [("suave", 13.06, 15.95, 1.10), ("suave", 40.78, 47.40, 1.08),
         ("seco", 64.80, 66.60, 1.12), ("suave", 70.0, 76.5, 1.08)]
sfx += [("swish_capcut", t0) for k, t0, t1, z in zooms if k == "seco"]   # som só junto do zoom

card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           card="card_logo.png"))
