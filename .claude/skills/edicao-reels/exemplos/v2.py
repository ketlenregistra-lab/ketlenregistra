"""Vídeo 2 — O que eu olho antes de uma reunião com cliente."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lib import *

words = load_words(2)
f = lambda p, a=0: find(words, p, a)
E, Z, S, B = [], [], [], []
END = 56.56

# ---- Gancho (combinação de 2 tipografias)
a, b = f('Antes de sentar com um cliente,')
t_sei = f('eu já sei')[0]; t_4 = f('quatro coisas')[0]
E.append(Combo(a, 4.4, [
    (a, [M('Antes de sentar com um cliente,', 36)]),
    (t_sei, [P('eu já sei', 96, it=True)]),
    (t_4, [P('4 coisas', 118, color=WHITE), P('sobre a empresa', 54, it=True)]),
], cy=1320, lead=-46))
B.append((a, 4.4))
Z.append((t_4, 4.4, 1.12, 860, 'punch')); S += [(a, 'swish', 0.4), (t_4, 'impact', 0.45)]

# ---- Checklist das 4 coisas (aparece a cada tópico, vai marcando)
items = ['Faturamento x mês anterior x ano passado', 'Imposto coerente?', 'O que vence nos próximos dias', 'A pergunta que você ainda não fez']
t1 = f('Primeira coisa,')[0]; t2 = f('Dois,')[0]; t3 = f('Três,')[0]; t4 = f('Quatro, aquela')[0]
times = [t1, t2, t3, t4]
fn, h = checklist_fn('Antes da reunião', items, times, 0, title_it=' eu já sei:', row=56)
def show_check(ta, tb, tick):
    E.append(Dynamic(ta, tb, lambda tr, ta=ta: fn(tr + ta), 540, 272 + h / 2, mode='pop'))
    Z.append((ta, tb, 1.07, 'top', 'smooth'))
    S.extend([(ta, 'swish', 0.4), (tick, 'ding', 0.4)])
show_check(4.45, f('Comparado')[0] - 0.05, t1)

# gráfico: faturamento comparado
ta = f('Comparado')[0]; tb = f('Comparar com')[0]
fnb, hb = bars_fn('Faturamento', ['Mesmo mês 2025', 'Mês anterior', 'Este mês'], [78, 60, 92], 0, colors=[(150, 175, 230), (150, 175, 230), RED], show_vals=['R$ 78 mil', 'R$ 60 mil', 'R$ 92 mil'])
E.append(Dynamic(ta, tb, lambda tr, ta=ta: fnb(tr), 540, 272 + hb / 2, mode='pop'))
Z.append((ta, tb, 1.07, 'top', 'smooth')); S += [(ta, 'pop', 0.5), (ta + 0.25, 'chart', 0.45)]

# sazonalidade (combo)
a, b = f('pode enganar por causa da sazonalidade.')
E.append(Combo(a, b + 0.3, [(a, [M('Pode enganar por causa da', 34)]), (f('sazonalidade.')[0], [P('sazonalidade.', 104, it=True)])], cy=1340, lead=-46))
B.append((a, b + 0.3)); Z.append((a, b + 0.3, 1.1, 860, 'smooth')); S.append((f('sazonalidade.')[0], 'click', 0.9))

show_check(t2 - 0.05, f('pago')[0] + 0.6, t2)
# imposto: guia com %
ta = f('pago')[0] + 0.6; tb = t3 - 0.05
E.append(Sprite(ta, tb, tax_img(270), 540, 272 + 175, mode='pop', big=True))
Z.append((ta, tb, 1.07, 'top', 'smooth')); S.append((ta, 'pop', 0.55))
a, b = f('Quando não bate, tem coisa para investigar.')
E.append(Combo(a, b + 0.25, [(a, [M('Quando não bate,', 36)]), (f('tem coisa')[0], [P('tem coisa pra', 80, it=True)]), (f('investigar.')[0], [P('investigar.', 104, color=WHITE), ])], cy=1340, lead=-50))
B.append((a, b + 0.25)); S += [(a, 'click', 0.9), (f('tem coisa')[0], 'click', 0.9), (f('investigar.')[0], 'click', 0.9)]

show_check(t3 - 0.05, f('Obrigações,')[0] - 0.05, t3)
# vencimentos: pílulas
ta = f('Obrigações,')[0]; tb = t4 - 0.05
tt = [ta, f('parcelamento,')[0], f('folha de pagamento.')[0]]
fns, hs = steps_fn(['Obrigações', 'Parcelamentos', 'Folha de pagamento'], tt, ta, arrows=False, gapx=24)
E.append(Dynamic(ta, tb, fns, 540, 300 + hs / 2, mode='up'))
S += [(x, 'click', 0.9) for x in tt]

show_check(t4 - 0.05, f('aquela pergunta')[1] + 0.6, t4)
a, b = f('ainda não sabe que precisa fazer.')
E.append(Combo(a, b + 0.3, [(a, [M('que o cliente', 36)]), (a, [P('ainda não sabe', 86, it=True)]), (f('que precisa fazer.', a)[0], [P('que precisa fazer.', 70)])], cy=1340, lead=-48))
B.append((f('aquela pergunta')[0], b + 0.3))

# ---- Virada: tela preta
a = f('Na gerência,')[0]; _, b = f('começa bem antes.')
t_r = f('uma reunião boa')[0]; t_h = f('na hora marcada,')[0]; t_c = f('começa bem antes.')[0]
E.append(BlackCard(a, b + 0.5, [
    (a, [M('Na gerência eu aprendi:', 36)]),
    (t_r, [P('reunião boa não começa', 70)]),
    (t_h, [P('na hora marcada.', 70, it=True)]),
    (t_c, [P('Começa', 100), P('antes.', 100, it=True, color=RED)], {'type': (t_c, b)}),
], cy=860, lead=-14))
B.append((a - 0.05, b + 0.5)); S += [(a, 'impact', 0.4)] + type_keys(t_c, b, 'Começa antes.', 0.5)

a, b = f('E se um empresário')
Z.append((a, f('serviu para nada.')[1], 1.1, 860, 'smooth')); S.append((a, 'swish', 0.3))
a, b = f('O meu trabalho é traduzir.')
t_t = f('traduzir.')[0]
E.append(Combo(a, b + 0.35, [(a, [M('O meu trabalho é', 40)]), (t_t, [P('traduzir.', 132, it=True)])], cy=1340, lead=-48))
B.append((a - 0.05, b + 0.35)); Z.append((a, b + 0.35, 1.16, 820, 'smooth')); S += [(a, 'swish', 0.6)]

# ---- CTA: comentários
a = f('Você sabe o que')[0]
Z.append((a, END, 1.06, 860, 'slow'))
t_c = f('nos comentários.')[0] if True else a
E.append(Sprite(f('Me conta')[0], END, input_bar_img(), 540, 272 + 60, mode='up'))
S.append((f('Me conta')[0], 'notify', 0.5))

E.append(Subtitles(words, B))

if __name__ == '__main__':
    main(2, 'Video2_antes_da_reuniao.mp4', E, Z, S)
