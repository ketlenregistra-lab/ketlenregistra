"""Vídeo 1 — "Calo" ou "carro"? Até quando a troca de letras é normal. Legenda fina (Montserrat)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from destaque_helper import *

FIX = {"fonaudiólogas,": "fonoaudiólogas,", "consomontais": "consonantais", "afono": "fono",
       "Bill": "bio", (49.12, "um"): "uma"}
words = carregar_palavras("transcricao.json", FIX, cortar_depois=95.66)   # sem legenda no "e aí" final
DUR = 96.24          # vídeo inteiro: não corta o "que eu vou te ajudar"
cabeca = json.load(open("cabeca.json"))
LEG_Y = 1250
D, destaque, linhas = criar(words, cabeca, 1190)

# "Calo" / "Carro": próximas; quando ela termina "carro", "Calo" ganha o risco no meio
fim_carro = fim_fala(words, 5.35)
yc = acima_da_cabeca(cabeca, 3.4, 6.6, 240)
def calo_carro(t1):
    return [f"Dialogue: 1,{ts(3.42)},{ts(fim_carro)},Big,,0,0,0,,{{\\an5\\pos(540,{yc - 58})\\1c{BRANCO}{SOMBRA}\\fs118{FADE}}}Calo",
            f"Dialogue: 1,{ts(fim_carro)},{ts(t1)},Big,,0,0,0,,{{\\an5\\pos(540,{yc - 58})\\1c{BRANCO}{SOMBRA}\\fs118\\s1}}Calo",
            f"Dialogue: 1,{ts(5.34)},{ts(t1)},Big,,0,0,0,,{{\\an5\\pos(540,{yc + 58})\\1c{ROXO}{SOMBRA}\\fs126{FADE}}}Carro"]
D.add(3.42, 6.60, calo_carro, [("clique_caneta", 3.42), ("clique_caneta", 5.34)])

destaque("fonoaudiólogas", 10.14, ROXO, 96, texto="Fonoaudiólogas")
destaque("tempo certo", 15.44, "notif", 74, texto="Tempo certo")
destaque("R do carro", 17.86, "notif", 74)
destaque("até 3 anos e meio", 20.54, ROXO, 92, texto="Até 3 anos e meio")
destaque("R vibrante", 22.74, "notif", 74)
destaque("arara cadeira", 24.76, "notif", 74, texto="Arara, cadeira")
destaque("até no máximo 5 anos", 27.40, ROXO, 100, texto="Até 5 anos")
destaque("encontros consonantais", 32.14, "notif", 70, texto="Encontros consonantais")
destaque("praça", 34.80, "notif", 80, texto="Praça")
destaque("5 anos e meio", 38.28, ROXO, 104)
destaque("procurar uma fono", 48.76, ROXO, 90, texto="Procurar uma fono", ate=50.10)
destaque("dica importante", 50.20, "notif", 74, texto="Dica importante")
destaque("não precisa ficar corrigindo", 51.68, "notif", 64, texto="Não precisa ficar corrigindo")
destaque("seu modelo pode ajudar", 58.74, ROXO, 84, texto="Seu modelo pode ajudar")
destaque("vários contextos", 82.64, "notif", 74, texto="Vários contextos")
destaque("frases diferentes", 84.12, "notif", 74, texto="Frases diferentes")
destaque("WhatsApp do link da bio", 93.42, "notif", 64)

# brincando com o carrinho: frase inteira em MAIÚSCULAS, sem caixinha, com clique (sem digitação)
for fala, perto, l1, l2 in [("olha só filho", 67.90, "OLHA SÓ, FILHO,", "QUE CARRO LINDO!"),
                             ("pra onde esse carro", 71.42, "PRA ONDE ESSE", "CARRO TÁ INDO?"),
                             ("nossa você percebeu", 73.54, "NOSSA! O PNEU", "DO CARRO FUROU?"),
                             ("gente onde a gente", 77.06, "ONDE A GENTE VAI", "ABASTECER ESSE CARRO?")]:
    t0 = tempos(words, fala, perto)[0]
    D.add(t0, t0 + 3.4, (lambda l1, l2, t0: lambda t1: [
        ev_inteiro(t0, t1, l1, 540, acima_da_cabeca(cabeca, t0, t1, 160) - 40, BRANCO, 74),
        ev_inteiro(t0, t1, l2, 540, acima_da_cabeca(cabeca, t0, t1, 160) + 40, BRANCO, 74)])(l1, l2, t0),
        [("clique_caneta", t0)])

ev, ocupado, sfx = D.render()
zooms = [("seco", 10.14, 11.22, 1.15), ("suave", 20.3, 22.3, 1.12), ("seco", 27.40, 29.36, 1.15),
         ("seco", 38.28, 39.30, 1.15), ("suave", 58.6, 60.8, 1.12), ("suave", 88.6, 95.9, 1.10)]
sfx += [("swish_capcut", t0) for k, t0, t1, z in zooms if k == "seco"]

card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, card="card_logo.png"))
