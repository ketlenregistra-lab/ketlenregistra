"""Vídeo 5 — 13º: a primeira parcela vence em novembro."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lib import *

words = fix_words(load_words(5), {'Digos,': 'Divos,', 'cargos': 'encargos'})
for i, w in enumerate(words):  # correções pontuais de transcrição
    if w['w'] == 'terço' and words[i - 1]['w'] == 'um':
        words[i - 1]['w'] = '1/12'; w['w'] = ''
    if w['w'] == 'em' and i + 1 < len(words) and words[i + 1]['w'] == 'encargos':
        w['w'] = ''
f = lambda p, a=0: find(words, p, a)
E, Z, S, B = [], [], [], []
END = 83.1

# ---- Gancho: boleto chegando
a = f('se você tem funcionário,')[0]; t_b = f('tem um boleto')[0]; t_n = f('chegando em novembro')[0]
E.append(Combo(a, f('que talvez')[0], [
    (a, [M('Se você tem funcionário,', 36)]),
    (t_b, [P('tem um boleto', 96, it=True)]),
    (t_n, [P('chegando em', 70), P('novembro.', 70, color=WHITE, it=True)]),
], cy=1330, lead=-44))
B.append((a, f('que talvez')[0])); S += [(a, 'swish', 0.4), (t_b, 'pop', 0.45)]
E.append(Sprite(t_b, 6.5, tax_img(250, label='13º SALÁRIO'), 540, 272 + 170, mode='pop', big=True))
Z.append((t_b, 6.5, 1.1, 'top', 'smooth')); S.append((t_b + 0.05, 'impact', 0.35))

# ---- o telefone toca / pergunta
a = f('Todo fim de novembro,')[0]
Z.append((a, f('Julia,')[0], 1.08, 860, 'slow'))
S.append((f('telefone')[0], 'notify', 0.5))
ta = f('Julia,')[0]; tb = f('O 13º não')[0]
E.append(Sprite(ta - 0.1, tb, question_box_img('CLIENTE, FIM DE NOVEMBRO', 'Julia, e agora, de onde eu tiro esse 13º?'), 540, 460, mode='pop'))
B.append((ta - 0.1, tb)); S += [(ta - 0.1, 'click', 0.9)]
Z.append((ta, tb, 1.12, 'top', 'punch'))

# ---- não é surpresa, tem data
a = f('O 13º não')[0]; b = f('tem data.')[1] + 0.3
E.append(Combo(a, b, [(a, [M('O 13º não é surpresa.', 38)]), (f('ele tem data.')[0], [P('Ele tem', 104, it=True), P('data.', 104, it=True)])], cy=1330, lead=-44))
B.append((a, b)); S.append((f('data.')[0], 'impact', 0.45))

# ---- calendários
t30 = f('30 de novembro.')[0]; t20 = f('20 de dezembro.')[0]
ta = f('Primeira parcela,')[0]; tm = f('Segunda parcela,')[0]; tb = f('E sobre ele')[0]
fc1, hc1 = calendar_fn(2026, 11, [(30, t30, '')], ta, w=760, ch=58, note='1ª parcela: até 30/11')
fc2, hc2 = calendar_fn(2026, 12, [(20, t20, '')], tm, w=760, ch=58, note='2ª parcela: até 20/12')
E.append(Dynamic(ta, tm, fc1, 540, 272 + hc1 / 2, mode='pop', big=True, maxh=430))
E.append(Dynamic(tm, tb, fc2, 540, 272 + hc2 / 2, mode='pop', big=True, maxh=430))
Z.append((ta, tb, 1.06, 860, 'slow'))
S += [(ta, 'pop', 0.55), (t30, 'ding', 0.45), (tm, 'swish', 0.45), (t20, 'ding', 0.45)]

# ---- encargos
ta = f('E sobre ele')[0]; tb = f('Na contabilidade,')[0]
tt = [ta + 0.1, f('FGTS')[0], f('INSS.')[0]]
fns, hs = steps_fn(['13º', '+ FGTS', '+ INSS (alguns casos)'], tt, ta, arrows=False, gapx=24, last_red=False)
E.append(Dynamic(ta, tb, fns, 540, 300 + hs / 2, mode='up'))
S += [(x, 'pop', 0.5) for x in tt]

# ---- tela preta: provisão
a = f('Na contabilidade,')[0]; t_p = f('Provisão.')[0]; b = f('Provisão.')[1] + 0.45
E.append(BlackCard(a, b, [(a, [M('Na contabilidade,', 36)]), (f('isso tem nome.')[0], [M('isso tem nome:', 36, color=RED)]), (t_p, [P('Provisão.', 150, it=True)])], cy=880, lead=-10))
B.append((a - 0.05, b)); S += [(a, 'riser', 0.25), (t_p, 'impact', 0.55)]

# ---- gráfico da provisão
ta = f('Todo mês,')[0]; tb = f('Na prática,')[0]
fnp, hp = provision_fn(ta, ta + 0.4, f('O custo é')[0], f('o pagamento')[0])
E.append(Dynamic(ta, tb, fnp, 540, 272 + hp / 2, mode='pop'))
Z.append((ta, tb, 1.08, 'top', 'smooth')); S += [(ta, 'pop', 0.5), (ta + 0.5, 'chart', 0.35), (f('o pagamento')[0], 'ding', 0.45)]
a, b = f('O custo é do ano inteiro.')
E.append(Combo(a, b + 0.3, [(a, [M('O custo é', 36)]), (f('do ano inteiro.')[0], [P('do ano inteiro.', 96, it=True)])], cy=1330, lead=-44))
B.append((a, b + 0.3))

# ---- exemplo: 2 mil -> 167
ta = f('Na prática,')[0]; tb = f('Por isso,')[0]
fnn, hn = stats_fn([(2000, 'R$ ', '', 'salário do funcionário', f('2 mil')[0]), (167, 'R$ ', '', 'por mês só de 13º', f('167')[0])], ta)
E.append(Dynamic(ta, tb, lambda tr, ta=ta: fnn(tr), 540, 272 + hn / 2, mode='pop'))
Z.append((ta, tb, 1.08, 'top', 'smooth')); S += [(f('2 mil')[0], 'chart', 0.4), (f('167')[0], 'beeps', 0.35)]
note = render_line([('FORA ENCARGOS E FÉRIAS', dict(fam='ms', w=800, size=28, track=3, color=WHITE, hl=RED))])[0]
E.append(Sprite(f('fora')[0], tb, note, 540, 272 + hn + 40, mode='pop', shadow=False))
S.append((f('fora')[0], 'pop', 0.4))

# ---- dezembro não foi ruim
a = f('Por isso,')[0]
Z.append((a, f('Foi um ano')[0], 1.08, 860, 'slow'))
a, b = f('Foi um ano inteiro sem provisão.')
E.append(Combo(a, b + 0.4, [(a, [M('Foi um', 38)]), (f('ano inteiro')[0], [P('ano inteiro', 100, it=True)]), (f('sem provisão.')[0], [P('sem provisão.', 92)])], cy=1310, lead=-44))
B.append((a, b + 0.4)); Z.append((a, b + 0.4, 1.15, 820, 'punch')); S += [(a, 'whoosh', 0.45), (f('sem provisão.')[0], 'impact', 0.4)]

# ---- o que eu oriento
ta = f('O que eu oriento?')[0]; tb = f('Para esse ano,')[0]
tt = [f('Pega esse valor')[0], f('guarda numa conta')[0], f('junto com a provisão')[0]]
fnc, hc = checklist_fn('O que eu', ['Separe o valor mensal', 'Guarde numa conta separada', 'Junto com a provisão de férias'], tt, 0, title_it=' oriento:', row=58)
E.append(Dynamic(ta, tb, lambda tr, ta=ta: fnc(tr + ta), 540, 272 + hc / 2, mode='pop'))
Z.append((ta, tb, 1.07, 'top', 'smooth')); S += [(ta, 'swish', 0.4)] + [(x, 'ding', 0.35) for x in tt]

# ---- tela preta: esse ano não dá, 2027 dá
a = f('Para esse ano,')[0]; t27 = f('Para 2027,')[0]; b = f('dá.', t27)[1] + 0.2
E.append(BlackCard(a, b, [
    (a, [M('Para esse ano,', 36)]),
    (f('não dá mais.')[0], [P('não dá mais.', 96, it=True)]),
    (t27, [M('Para', 40, color=RED), P('2027,', 120, color=RED)]),
    (f('dá.', t27)[0], [P('dá.', 130, it=True)]),
], cy=860, lead=-12))
B.append((a - 0.05, b)); S += [(a, 'impact', 0.45), (t27, 'whoosh', 0.45), (f('dá.', t27)[0], 'ding', 0.4)]

# ---- CTA: salve + amigo que liga dia 29
a = f('Salve esse vídeo')[0]; t29 = f('dia 29.')[0]; tl = f('vai me ligar')[0]
fc3, hc3 = calendar_fn(2026, 11, [(29, t29 + 0.15, '')], tl, w=760, ch=58, note='o dia que ele vai te ligar')
E.append(Dynamic(tl, END, fc3, 540, 272 + hc3 / 2, mode='pop', big=True, maxh=380))
Z.append((a, END, 1.06, 860, 'slow')); S += [(tl, 'pop', 0.5), (t29 + 0.15, 'ding', 0.45)]

E.append(Subtitles(words, B))

if __name__ == '__main__':
    main(5, 'Video5_13_salario.mp4', E, Z, S)
