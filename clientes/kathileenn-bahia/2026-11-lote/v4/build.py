"""Vídeo 4 — Janeiro Branco: ouvir mal também cansa a cabeça. Legenda Poppins, destaques em branco,
trilha suave bem baixinha."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from destaque_helper import *

words = carregar_palavras("transcricao.json", {})
DUR = float(os.environ.get("DUR", "50.30"))
cabeca = json.load(open("cabeca.json"))
LEG_Y = 1330
D, destaque, linhas = criar(words, cabeca, 1290)

# fininha + grossa, bem juntinhas, clique em cada linha
linhas(["quem ouve mal", "faz força o dia inteiro"], 5.48, BRANCO, [66, 92], 70,
       textos=["Quem ouve mal", "faz força o dia inteiro"], fontes=["KB Montserrat Regular", None])
destaque("cansa", 15.00, BRANCO, 130, texto="Cansa")
# festas / almoços de família / telefone: letra roxa com borda, um por vez, com clique
linhas(["festas", "almoços de família", "telefone"], 18.32, "claro", 72, 90,
       textos=["Festas", "Almoços de família", "Telefone"], ate=22.65)
destaque("janeiro", 23.66, BRANCO, 150, texto="JANEIRO")
# SAÚDE MENTAL fica mais tempo: entra no "da saúde mental" e sai antes da próxima frase
destaque("da saúde mental", 27.56, BRANCO, 112, texto="SAÚDE MENTAL", ate=29.55)
# "Cuidar da sua audição / também é cuidar / da sua cabeça": roxo com borda branca, linha a linha
linhas(["da sua audição", "também é cuidar", "da sua cabeça"], 29.64, "claro", 70, 88,
       textos=["Cuidar da sua audição", "também é cuidar", "da sua cabeça"], ate=32.65)
destaque("avaliação auditiva", 44.06, "claro", 80, texto="Avaliação auditiva", onde="peito")
destaque("link na bio", 49.30, BRANCO, 104, texto="Link na bio", ate=50.30)

ev, ocupado, sfx = D.render()
zooms = [("suave", 5.4, 8.2, 1.08), ("seco", 23.66, 24.90, 1.12), ("suave", 28.6, 32.6, 1.10),
         ("suave", 40.5, 45.3, 1.08)]
# em JANEIRO fica só o clique (sem swish)

trilha_suave("trilha.wav", DUR + 5)
card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms,
           card="card_logo.png", musica="trilha.wav", musica_vol=0.018))
