"""Vídeo 4 — O responsável era eu."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from lib import *

words = fix_words(load_words(4), {'desfoto.': 'discuto.'})
f = lambda p, a=0: find(words, p, a)
E, Z, S, B = [], [], [], []
END = 65.27

# ---- Gancho elegante (2 tipografias + caixinha)
a = 0.0; t_r = f('O responsável era eu.')[0]; t_eu = f('era eu.')[0]
E.append(Sprite(0.0, t_r, question_box_img('CLIENTE', 'Posso falar com o responsável?'), 540, 452, mode='pop'))
S += [(0.0, 'click', 0.9)]
E.append(Combo(0.0, t_r, [(0.0, [M('Já me pediram pra falar', 36)]), (f('com o responsável.')[0], [P('com o', 92, it=True), P('responsável.', 92)])], cy=1340, lead=-46))
E.append(Combo(t_r, f('Eu comecei')[0] - 0.05, [(t_r, [M('O responsável', 40)]), (t_eu, [P('era', 140, it=True), P('eu.', 140, color=RED)])], cy=1340, lead=-50))
B.append((0, f('Eu comecei')[0] - 0.05))
Z.append((t_eu, f('Eu comecei')[0] - 0.05, 1.16, 820, 'punch')); S += [(f('com o responsável.')[0], 'click', 0.9), (t_r, 'click', 0.9), (t_eu, 'click', 0.9)]

# ---- 17 anos
ta = f('aos 17 anos.')[0]; tb = f('Clientes explicando')[0] - 0.05
card = bigline_card([[('17', dict(fam='pf', w=700, size=120, color=WHITE)), ('anos', dict(fam='pf', w=500, it=True, size=64, color=(255, 160, 160)))],
                     [('QUANDO COMECEI NA CONTABILIDADE', dict(fam='ms', w=700, size=24, track=2, color=(205, 215, 240)))]], w=640, pad=14, tag=False, top=10)
E.append(Sprite(ta, tb, card, 540, 272 + card.height / 2, mode='pop'))
Z.append((ta, tb, 1.08, 'top', 'smooth')); S += [(ta, 'click', 0.9)]
a, b = f('eu era a mais nova da sala.')
E.append(Combo(a, b + 0.3, [(a, [M('Eu era', 36)]), (f('a mais nova')[0], [P('a mais nova', 96, it=True)]), (f('da sala.')[0], [P('da sala.', 80)])], cy=1360, lead=-48))
B.append((a, b + 0.3))

# ---- clientes / pergunta
a = f('Clientes explicando')[0]
Z.append((a, f('Gente perguntando.')[1], 1.08, 860, 'slow'))
ta = f('Mas e o contador?')[0]; tb = f('Quando eu abri')[0]
QTXT = 'Mas e o contador? Ele vem quando?'
te = f('vem quando?')[1]
def qfn(tr, ta=ta, te=te):
    n = len(QTXT) if tr + ta - 0.15 >= te else int(len(QTXT) * max(0.0, (tr - 0.15) / (te - ta)))
    return question_box_img('CLIENTE', QTXT, nchars=n)
E.append(Dynamic(ta - 0.15, tb, qfn, 540, 452, mode='pop', behind=False))
S += [(ta - 0.15, 'click', 0.9)] + type_keys(ta, te, QTXT, 0.55)
B.append((ta - 0.15, tb)); Z.append((ta, tb, 1.12, 860, 'punch'))

# ---- jovem, mulher, começando do zero
ta = f('Jovem,')[0]; tb = f('Só que tem')[0]
tt = [ta, f('mulher,')[0], f('começando do zero.')[0]]
fns, hs = steps_fn(['Jovem', 'Mulher', 'Começando do zero'], tt, ta, arrows=False, gapx=24)
E.append(Dynamic(ta, tb, fns, 540, 300 + hs / 2, mode='up'))
S += [(x, 'click', 0.9) for x in tt]
a = f('Quando eu abri')[0]
Z.append((a, ta, 1.08, 860, 'smooth'))

# ---- de todos os lados
a = f('Só que tem')[0]
Z.append((a, f('Eu já tinha')[0], 1.1, 860, 'slow')); S.append((a, 'riser', 0.25))
a, b = f('de todos os lados.')
E.append(Combo(f('um escritório')[0], b + 0.35, [(f('um escritório')[0], [M('Eu já tinha visto um escritório', 32)]), (a, [P('de todos', 100, it=True), P('os lados.', 100)])], cy=1340, lead=-46))
B.append((f('um escritório')[0], b + 0.35)); S.append((a, 'impact', 0.45))

# ---- linha do tempo da carreira
ta = f('Na recepção,')[0]; tb = f('Já são 12')[0] - 0.05
tt = [ta, f('Como auxiliar,')[0], f('Na gestão,')[0], f('Como gerente,')[0], f('pelo resultado.')[1] + 0.1]
fnt, ht = steps_fn(['Recepção', 'Auxiliar', 'Gestão', 'Gerente', 'Minha empresa'], tt, ta, arrows=True, gapx=50)
E.append(Dynamic(ta, tb, fnt, 540, 290 + ht / 2, mode='up'))
Z.append((ta, tb, 1.05, 'top', 'smooth'))
S += [(x, 'click', 0.9) for x in tt]

# ---- números
ta = f('Já são 12')[0]; tb = f('Idade não é')[0] - 0.05
fnn, hn = stats_fn([(12, '', '', 'anos de contabilidade', f('12')[0]), (200, '', '+', 'empresas atendidas', f('200')[0])], ta, w=760, tag=False)
E.append(Dynamic(ta, tb, lambda tr, ta=ta: fnn(tr), 540, 272 + hn / 2, mode='pop'))
Z.append((ta, tb, 1.08, 'top', 'smooth')); S += [(f('12')[0], 'count', 0.7), (f('200')[0], 'count', 0.7)]

# ---- tela preta: idade x experiência
a = f('Idade não é')[0]; b = f('experiência é.')[1] + 0.45
E.append(BlackCard(a, b, [
    (a, [P('Idade', 110), M('não é currículo.', 34)]),
    (f('experiência é.')[0], [P('Experiência', 116, it=True, color=RED), P('é.', 116)]),
], cy=880, lead=-6))
B.append((a - 0.05, b)); S += [(a, 'click', 0.9), (f('experiência é.')[0], 'click', 0.9)]

# ---- eu explico
a, b = f('Eu explico.')
E.append(Combo(a, b + 0.3, [(a, [P('Eu', 120), P('explico.', 120, it=True)])], cy=1340))
B.append((a, b + 0.3)); Z.append((a, b + 0.3, 1.15, 820, 'punch')); S.append((a, 'whoosh', 0.45))
a, b = f('a minha contadora.')
E.append(Combo(f('E na segunda')[0], b + 0.4, [(f('E na segunda')[0], [M('Na segunda reunião:', 36)]), (a, [P('“a minha contadora”', 92, it=True)])], cy=1340, lead=-46))
B.append((f('E na segunda')[0], b + 0.4)); S.append((a, 'pop', 0.45))

# ---- CTA: comenta "fui eu"
a = f('Se já te')[0]; t_f = f('Fui eu.')[0]
Z.append((a, END, 1.06, 860, 'slow'))
E.append(Sprite(t_f - 0.2, END, comment_img('voce', 'fui eu', w=640), 540, 272 + 105, mode='pop'))
S.append((t_f - 0.2, 'notify', 0.55))

E.append(Subtitles(words, B))

if __name__ == '__main__':
    main(4, 'Video4_o_responsavel_era_eu.mp4', E, Z, S)
