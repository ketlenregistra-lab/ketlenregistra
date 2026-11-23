"""Vídeo 1 — "Calo" ou "carro"? Até quando a troca de letras é normal. Legenda fina (Montserrat)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"fonaudiólogas,": "fonoaudiólogas,", "consomontais": "consonantais", "afono": "fono",
       "Bill": "bio", (49.12, "um"): "uma"}
words = carregar_palavras("transcricao.json", FIX)
DUR = 96.24          # vídeo inteiro: não corta o "que eu vou te ajudar"
cabeca = json.load(open("cabeca.json"))

LEG_Y = 1250         # altura do peito/braços (abaixo é a calça branca)
ev, ocupado, sfx = [], [], []

def em_cima(texto, perto, estilo, fs, altura, ate=None, fonte=None):
    """Destaque por cima da cabeça, surgindo palavra por palavra conforme a fala."""
    tp = tempos(words, texto, perto)
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.9)
    y = acima_da_cabeca(cabeca, tp[0], fim, altura)
    ev.extend(ev_fala(tp, fim, texto, 540, y, estilo, fs, fonte))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))
    return tp, fim

# "Calo" / "Carro": as duas palavras próximas; quando ela termina "carro", "Calo" ganha o risco
y = acima_da_cabeca(cabeca, 3.4, 6.6, 250)
fim_carro = fim_fala(words, 5.35)
ev.append(f"Dialogue: 1,{ts(3.42)},{ts(fim_carro)},Big,,0,0,0,,{{\\an5\\pos(540,{y - 62})\\1c{BRANCO}{SOMBRA}\\fs120{POP}}}Calo")
ev.append(f"Dialogue: 1,{ts(fim_carro)},{ts(6.60)},Big,,0,0,0,,{{\\an5\\pos(540,{y - 62})\\1c{BRANCO}{SOMBRA}\\fs120\\s1}}Calo")
ev.append(f"Dialogue: 1,{ts(5.34)},{ts(6.60)},Big,,0,0,0,,{{\\an5\\pos(540,{y + 62})\\1c{ROXO}{SOMBRA}\\fs130{POP}}}Carro")
ocupado.append((3.42, 6.60)); sfx += [("clique_caneta", 3.42), ("clique_caneta", 5.34)]

# destaques roxos grandes
em_cima("Fonoaudiólogas", 10.14, ROXO, 96, 110)
em_cima("Tempo certo", 15.44, "notif", 74, 90)
em_cima("R do carro", 17.86, "notif", 74, 90)
em_cima("Até 3 anos e meio", 20.54, ROXO, 92, 110)
em_cima("R vibrante", 22.74, "notif", 74, 90)
em_cima("Arara, cadeira", 24.76, "notif", 74, 90)
em_cima("Até 5 anos", 27.40, ROXO, 104, 120)
em_cima("Encontros consonantais", 32.14, "notif", 66, 90)
em_cima("Praça", 34.80, "notif", 80, 90)
em_cima("5 anos e meio", 38.28, ROXO, 104, 120)
em_cima("Procurar uma fono", 48.76, ROXO, 90, 110, ate=50.15)      # fica mais tempo na tela
em_cima("Dica importante", 50.20, "notif", 74, 90)
em_cima("Não precisa ficar corrigindo", 51.68, "notif", 62, 90)
em_cima("Seu modelo pode ajudar", 58.74, ROXO, 84, 110)
em_cima("Vários contextos", 82.64, "notif", 74, 90)
em_cima("Frases diferentes", 84.12, "notif", 74, 90)
em_cima("WhatsApp do link da bio", 93.42, "notif", 64, 90)

# brincando com o carrinho: frases em maiúsculas, sem caixinha, digitando com som de teclado
for t0, t1, txt in [(67.90, 71.40, "OLHA SÓ, FILHO,\\NQUE CARRO LINDO!"),
                    (71.42, 73.52, "PRA ONDE ESSE\\NCARRO TÁ INDO?"),
                    (73.54, 77.04, "NOSSA! O PNEU\\NDO CARRO FUROU?"),
                    (77.06, 80.46, "ONDE A GENTE VAI\\NABASTECER ESSE CARRO?")]:
    y = acima_da_cabeca(cabeca, t0, t1, 190)
    e, teclas = ev_digitando(t0, t1, txt, 540, y, BRANCO, fs=74, cps=20)
    ev.extend(e); sfx += [("tecla", t) for t in teclas]
    ocupado.append((t0, t1))

zooms = [("seco", 10.14, 11.22, 1.15), ("suave", 20.3, 22.3, 1.12), ("seco", 27.40, 29.36, 1.15),
         ("seco", 38.28, 39.30, 1.15), ("suave", 58.6, 60.8, 1.12), ("suave", 88.6, 95.9, 1.10)]
for k, t0, t1, z in zooms:
    if k == "seco":
        sfx.append(("swish_capcut", t0))

card_logo_branco("card_logo.png", os.path.join(AQUI, "..", "work", "logo_card_seguro.png"))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Montserrat Light", leg_fs=74,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, card="card_logo.png"))
