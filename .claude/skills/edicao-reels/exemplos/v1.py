"""Vídeo 1 — POV: é novembro num escritório de contabilidade (trend)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lib import *

words = fix_words(load_words(1), {})
f = lambda p, a=0: find(words, p, a)
E, Z, S = [], [], []
END = 39.84

# ---- Gancho: POV (2 tipografias) no peito, enquanto a pergunta aparece na caixinha
E.append(Combo(0.0, 5.3, [
    (0.0, [M('POV:', 38, w=800, color=(255, 255, 255)), M('é novembro', 38, w=500, upper=False, track=0)]),
    (0.15, [P('num escritório de', 74, it=True)]),
    (0.3, [P('contabilidade', 92)]),
], cy=1320, lead=-46))
S += [(0.0, 'swish', 0.6)]

# ---- Perguntas do cliente (voz de fundo) em caixinha
def qbox(t0, t1, label, text):
    E.append(Sprite(t0, t1, question_box_img(label, text), 540, 452, mode='pop'))
    S.append((t0, 'click', 0.9))

qbox(0.0, 5.3, 'CLIENTE, DIA 28', 'Julia, esse tal de 13º é esse mês?')
# reação dela: zoom lento (expressão)
Z.append((2.6, 5.4, 1.13, 860, 'slow'))
S.append((2.7, 'riser', 0.25))

qbox(5.4, 8.45, 'CLIENTE', 'Quero pagar menos imposto esse ano.')
# Julia: "Agora, em novembro?" — sem legenda, punch-in na expressão
a, b = f('Agora, em novembro?')
Z.append((a, 9.3, 1.18, 820, 'punch')); S.append((a, 'whoosh', 0.55))
# calendário quando ela mostra o celular (celular fica à esquerda, card à direita/topo)
fn, h = calendar_fn(2026, 11, [(28, 9.35, ''), (29, 9.55, ''), (30, 9.75, '')], 9.2, w=760, ch=58, note='o ano já está acabando')
E.append(Dynamic(9.2, 10.55, fn, 560, 272 + h / 2, mode='pop', big=True, maxh=400))
S += [(9.2, 'pop', 0.6), (9.35, 'click', 0.5), (9.55, 'click', 0.5), (9.75, 'ding', 0.35)]

qbox(10.55, 13.95, 'CLIENTE', 'Vou fazer Black Friday com 70% off em tudo.')
Z.append((12.3, 13.95, 1.08, 860, 'smooth')); S.append((12.3, 'swish', 0.35))
qbox(13.95, 16.6, 'O MESMO CLIENTE, EM DEZEMBRO', 'Por que não sobrou nada?')
Z.append((14.0, 16.6, 1.12, 860, 'slow'))
# calculadora (ela mostra a do celular à esquerda; ilustração no topo direito)
E.append(Sprite(16.6, 18.05, calculator_img('0,00', w=250), 760, 272 + 178, mode='pop', big=True))
S += [(16.6, 'pop', 0.6), (16.85, 'beeps', 0.4)]

# ---- Virada: Julia séria para a câmera (legenda volta)
a, b = f('Divos,')
S.append((a, 'whoosh_down', 0.5))

# tela preta com a frase principal
a, _ = f('Depois de 31 de dezembro')
_, b = f('vira só apuração.')
t_pl, _ = f('planejamento tributário')
t_vi, _ = f('vira só apuração.')
E.append(BlackCard(a, b + 0.55, [
    (a, [M('Depois de 31/12,', 40, w=700)]),
    (t_pl, [P('planejamento', 104, it=True)]),
    (t_pl + 0.3, [P('tributário', 104, it=True)]),
    (t_vi, [P('vira só', 88), P('apuração.', 88, color=RED)]),
], cy=860, lead=-18))
S += [(a - 0.9, 'riser', 0.25), (a, 'impact', 0.45), (t_vi, 'click', 0.9)]

a, b = f('O ano fechou,')
Z.append((a, f('é calcular.')[1] + 0.2, 1.1, 860, 'smooth')); S.append((a, 'swish', 0.35))
a, b = f('calcular.')
E.append(Sprite(a, f('Planejar')[0] - 0.05, calculator_img('0,00', w=220), 760, 272 + 160, mode='pop', big=True))
S.append((a, 'beeps', 0.3))

# "Planejar é agora." — combo + punch
a, b = f('Planejar é agora.')
t_ag = f('agora.', a)[0]
# acima da cabeça (na parede), longe do rosto
E.append(Combo(a, b + 0.45, [(a, [M('Planejar', 44, w=800)]), (t_ag, [P('é agora.', 128, it=True, color=WHITE)])], cy=440, lead=-48))
Z.append((a, b + 0.45, 1.1, 'top', 'punch')); S += [(a, 'click', 0.9), (t_ag, 'click', 0.9)]

# CTA: marcação (comentário)
a, b = f('Marca aquele cliente')
E.append(Sprite(a, END, comment_img('voce', '@aquelecliente olha você aqui de novo', w=800), 540, 272 + 105, mode='up'))
S.append((a, 'notify', 0.5))

pa, pb = f('Planejar é agora.')
blocked = [(0, 18.05), (f('Depois de')[0] - 0.05, f('apuração.')[1] + 0.55), (pa - 0.05, pb + 0.45)]
E.append(Subtitles(words, blocked))

if __name__ == '__main__':
    pv = tuple(map(float, sys.argv[1:3])) if len(sys.argv) > 2 else None
    out = os.path.join(ROOT, 'out', 'Video1_POV_novembro.mp4' if not pv else 'preview_v1.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render('v1', os.path.join(ROOT, 'src', 'v1.mov'), E, Zooms(Z), S, out, preview=pv)
    print(out)
