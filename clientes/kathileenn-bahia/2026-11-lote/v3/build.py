"""Vídeo 3 — Piscina, praia e ouvido. Legenda mais grossinha (Poppins)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reels_lib import *

FIX = {"Fotonete?": "Cotonete?", "Fotonete": "Cotonete", "sozinho.": "sozinha.", (77.06, "sabe"): "salva"}
words = carregar_palavras("transcricao.json", FIX)
DUR = 83.30            # inclui a menina pulando na piscina
OLHO = 82.35           # a tela fecha como um olho quando ela pula
cabeca = json.load(open("cabeca.json"))

LEG_Y = 1380
PEITO = 1310
ev, ocupado, sfx = [], [], []

def no_peito(texto, perto, fs=74, ate=None):
    tp = tempos(words, texto, perto)
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.8)
    ev.extend(ev_fala(tp, fim, texto, 540, PEITO, "notif", fs))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))

def em_cima(texto, perto, estilo, fs, altura, ate=None):
    tp = tempos(words, texto, perto)
    fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.9)
    y = acima_da_cabeca(cabeca, tp[0], fim, altura)
    ev.extend(ev_fala(tp, fim, texto, 540, y, estilo, fs))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))

def duas_linhas(l1, l2, perto, fs=76, dy=84):
    """Dica em maiúsculas, sem caixinha, duas linhas bem próximas, palavra por palavra."""
    tp = tempos(words, l1 + " " + l2, perto, janela=4)
    n1 = len(l1.split())
    fim = fim_fala(words, tp[-1] + 0.01) + 0.9
    y = acima_da_cabeca(cabeca, tp[0], fim, fs + dy)
    ev.extend(ev_fala(tp[:n1], fim, l1, 540, y - dy // 2, BRANCO, fs))
    ev.extend(ev_fala(tp[n1:], fim, l2, 540, y + dy // 2, BRANCO, fs, pop=False))
    ocupado.append((tp[0], fim)); sfx.append(("clique_caneta", tp[0]))

# abertura: ANTES DA PISCINA digitando (sem caixinha) + "Cuidados com seu ouvido" com caixinha
t_antes = tempos(words, "antes da piscina", 1.70)
y = acima_da_cabeca(cabeca, 1.7, 5.0, 200)
e, teclas = ev_digitando(t_antes[0], 5.00, "ANTES DA PISCINA", 540, y - 50, BRANCO, fs=82, cps=16)
ev.extend(e); sfx.extend(("tecla", t) for t in teclas)
tp = tempos(words, "Cuidados com seu ouvido", 3.66)
ev.extend(ev_fala(tp, 5.00, "Cuidados com seu ouvido", 540, y + 52, "notif", 62))
sfx.append(("clique_caneta", tp[0])); ocupado.append((t_antes[0], 5.00))

duas_linhas("SECA BEM A PARTE DE FORA", "DO OUVIDO COM A PONTINHA DA TOALHA", 6.46, fs=64, dy=74)
no_peito("Só a parte de fora!", 11.16)
duas_linhas("INCLINA A CABEÇA", "PARA O LADO", 16.22, fs=84, dy=92)
no_peito("Cotonete não!", 20.74, ate=22.95)
no_peito("Empurra para dentro", 23.74)
em_cima("Procure o OTORRINO", 37.50, "notif", 78, 90)
no_peito("Tampões personalizados", 49.86, fs=64, ate=52.20)
no_peito("Função dupla", 66.62)
em_cima("ABAFADOR", 68.98, BRANCO, 110, 120)
no_peito("Salva esse vídeo", 77.06)

# imagens pequenas, como camada ATRÁS da cabeça (a pessoa fica na frente)
preparar_imagem("cotonete.jpg", "img_cotonete.png", 240, raio=26, borda=7, fundo_branco=True)
preparar_imagem("tampao.jpg", "img_tampao.png", 230, raio=26, borda=7)
imagens = [(20.74, 22.95, "img_cotonete.png", 270, 330, "atras"),     # só no "Cotonete não"
           (49.86, 52.20, "img_tampao.png", 650, 300, "atras")]       # mais para a direita

zooms = [("suave", 13.06, 15.95, 1.10), ("seco", 27.06, 29.30, 1.12), ("suave", 40.78, 47.40, 1.08),
         ("seco", 64.80, 66.60, 1.12), ("suave", 70.0, 76.5, 1.08)]
for k, t0, t1, z in zooms:
    if k == "seco":
        sfx.append(("swish_capcut", t0))         # o som acompanha o zoom

ev.extend(ev_olho(OLHO, DUR))
build(dict(src="bruto.mov", dur=DUR, words=words, leg_font="KB Poppins SemiBold", leg_fs=70,
           leg_y=LEG_Y, eventos=ev, sem_legenda=ocupado, sfx=sfx, zooms=zooms, imagens=imagens,
           fim="olho", olho_inicio=OLHO))
