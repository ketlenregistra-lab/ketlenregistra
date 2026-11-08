"""Vídeo 3 — Saber não é a mesma coisa que fazer."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lib import *

words = fix_words(load_words(3), {'rega': 'regra', 'pró': 'pró-labore,', '-labore,': ''})
f = lambda p, a=0: find(words, p, a)
E, Z, S, B = [], [], [], []
END = 72.07

# ---- Gancho
a = 0.0; t_v = f('aí eu virei uma')[0]
E.append(Combo(a, f('e descobri')[0], [
    (a, [M('Eu passava o dia orientando', 34)]),
    (a + 0.6, [P('empresários.', 100, it=True)]),
    (t_v, [M('Aí eu virei', 34, w=600), P('uma.', 78, it=True, color=WHITE)]),
], cy=1320, lead=-46))
B.append((0, f('e descobri')[0]))
Z.append((t_v, f('e descobri')[0], 1.1, 860, 'punch'))
# tela preta: saber ≠ fazer
a = f('e descobri')[0]; b = f('fazer.')[1] + 0.35
t_s = f('saber não é')[0]; t_f = f('que fazer.')[0]
E.append(BlackCard(a, b, [
    (a, [M('E descobri que', 36)]),
    (t_s, [P('saber', 140, it=True)]),
    (t_s + 0.45, [M('não é a mesma coisa que', 34, color=RED)]),
    (t_f, [P('fazer.', 140)]),
], cy=860, lead=-16))
B.append((a - 0.05, b)); S += [(a, 'click', 0.9), (t_s, 'click', 0.9), (t_s + 0.45, 'click', 0.9), (t_f, 'click', 0.9)]

# ---- O que ela falava pros clientes (checklist)
ta = f('Por anos')[0]; tb = f('Aí eu abri')[0] - 0.05
tt = [f('separe as contas,')[0], f('define um')[0], f('olhe sempre')[0]]
fn, h = checklist_fn('O que eu falava', ['Separe as contas', 'Defina um pró-labore', 'Olhe os números toda semana'], tt, 0, title_it=' pros clientes:', row=56)
E.append(Dynamic(ta, tb, lambda tr, ta=ta: fn(tr + ta), 540, 272 + h / 2, mode='pop'))
Z.append((ta, tb, 1.07, 'top', 'smooth')); S += [(ta, 'click', 0.9)] + [(x, 'click', 0.9) for x in tt]

# ---- "quem estava deixando as planilhas para depois? Eu."
a = f('Aí eu abri')[0]; t_eu = f('Eu.', a)[0]
Z.append((a, t_eu, 1.1, 860, 'slow'))
E.append(Combo(t_eu, f('Quando a empresa')[0] - 0.05, [(t_eu, [P('Eu.', 170, it=True)])], cy=1330))
B.append((t_eu, f('Quando a empresa')[0])); Z.append((t_eu, f('Quando a empresa')[0], 1.2, 820, 'punch'))
S += [(t_eu, 'impact', 0.55)]

# ---- tudo vira urgente
a = f('Quando a empresa é sua,')[0]; t_u = f('urgente.')[0]; b = f('urgente.')[1] + 0.2
E.append(Combo(a, b, [(a, [M('Quando a empresa é sua,', 36)]), (f('tudo vira')[0], [P('tudo vira', 84, it=True), P('urgente.', 84, color=RED)])], cy=1340, lead=-46))
B.append((a, b))
ta = f('Cliente,')[0]; tb = f('A organização')[0] + 0.1
tt = [ta, f('equipe,')[0], f('propostas')[0], f('contas a pagar.')[0]]
fn2, h2 = tag_list_fn('Tudo vira', ['Cliente', 'Equipe', 'Propostas', 'Contas a pagar'], tt, ta, title_it=' urgente', w=820)
# atrás da cabeça dela (camada)
E.append(Dynamic(ta - 0.2, tb, lambda tr, ta=ta: fn2(tr - 0.2), 540, 272 + h2 / 2, mode='pop', behind=True, maxh=320))
S += [(ta - 0.2, 'click', 0.9)] + [(x, 'click', 0.9) for x in tt]
# organização pode esperar
a, b = f('A organização sempre parece que pode esperar.')
E.append(Combo(a, b + 0.4, [(a, [M('A organização', 38)]), (f('sempre parece')[0], [P('sempre parece que', 70, it=True)]), (f('pode esperar.')[0], [P('pode esperar.', 96)])], cy=1330, lead=-46))
B.append((a, b + 0.4)); Z.append((a, b + 0.4, 1.08, 860, 'slow'))

# ---- virada
a = f('Foi aí que eu entendi')[0]
Z.append((a, f('funcionária.')[1], 1.1, 860, 'smooth')); S.append((a, 'swish', 0.3))
a, b = f('apagando incêndio o dia inteiro.')
E.append(Combo(a, b + 0.35, [(a, [M('Ele só está', 36)]), (f('apagando')[0], [P('apagando incêndio', 86, it=True)]), (f('o dia inteiro.')[0], [P('o dia inteiro.', 76)])], cy=1330, lead=-46))
B.append((f('ele só')[0], b + 0.35)); Z.append((a, b + 0.35, 1.14, 820, 'punch'))

# ---- a regra
a, b = f('Então eu criei uma regra')
E.append(Combo(a, b + 0.3, [(a, [M('Então eu criei', 38)]), (f('uma regra')[0], [P('uma regra', 118, it=True)])], cy=1340, lead=-48))
B.append((a, b + 0.3))
ta = f('30 minutos')[0]; tb = f('Quanto entrou,')[0] - 0.05
card = bigline_card([[('30', dict(fam='pf', w=700, size=150, color=WHITE)), ('min', dict(fam='pf', w=500, it=True, size=80, color=(255, 160, 160)))],
                     [('POR SEMANA · SEMPRE NO MESMO DIA', dict(fam='ms', w=700, size=26, track=2, color=(205, 215, 240)))]], w=780)
E.append(Sprite(ta, tb, card, 540, 272 + card.height / 2, mode='pop', behind=True))
S += [(ta, 'click', 0.9)]
ta2 = tb; tb2 = f('Não precisa ser perfeito,')[0] - 0.05
tt = [f('Quanto entrou,')[0], f('quanto saiu')[0], f('o que vai vencer.')[0]]
fn3, h3 = checklist_fn('3 números', ['Quanto entrou', 'Quanto saiu', 'O que vai vencer'], tt, 0, title_it=' toda semana:', row=58)
E.append(Dynamic(ta2, tb2, lambda tr, ta=ta2: fn3(tr + ta), 540, 272 + h3 / 2, mode='pop', behind=True, maxh=255))
Z.append((ta2, tb2, 1.15, 'top', 'smooth'))
S += [(ta2, 'click', 0.9)] + [(x, 'click', 0.9) for x in tt]

# tela preta: perfeito x toda semana
a = f('Não precisa ser perfeito,')[0]; b = f('toda semana.', a)[1] + 0.4
E.append(BlackCard(a, b, [
    (a, [M('Não precisa ser', 36)]),
    (f('perfeito,', a)[0], [P('perfeito.', 110, it=True)]),
    (f('mas precisa', a)[0], [M('Precisa ser', 36, color=RED)]),
    (f('toda semana.', a)[0], [P('toda semana.', 110)]),
], cy=860, lead=-14))
B.append((a - 0.05, b)); S += [(a, 'click', 0.9), (f('perfeito,', a)[0], 'click', 0.9), (f('mas precisa', a)[0], 'click', 0.9), (f('toda semana.', a)[0], 'click', 0.9)]

a = f('Quando eu cobro')[0]
Z.append((a, f('funciona.')[1], 1.1, 860, 'smooth')); S.append((a, 'swish', 0.3))

# ---- CTA
a = f('E me conta,')[0]
E.append(Sprite(a, END, input_bar_img(), 540, 272 + 60, mode='up'))
Z.append((a, END, 1.06, 860, 'slow')); S.append((a, 'notify', 0.5))

# clique a cada linha das combinações de fonte que vão surgindo
for e in E:
    if type(e).__name__ == 'Combo':
        S.extend((ln[0], 'click', 0.9) for ln in e.lines)
E.append(Subtitles(words, B))

if __name__ == '__main__':
    main(3, 'Video3_saber_nao_e_fazer.mp4', E, Z, S)
