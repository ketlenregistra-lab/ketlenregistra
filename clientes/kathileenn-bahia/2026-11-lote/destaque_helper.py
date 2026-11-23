"""Atalhos comuns aos builds do lote (revisão 3): destaque inteiro, sem sobreposição."""
from reels_lib import *

def criar(words, cabeca, peito):
    D = Destaques()

    def y_de(onde, t0, t1, altura):
        if onde == "cima":
            return acima_da_cabeca(cabeca, t0, t1, altura)
        if onde == "peito":
            return peito
        return onde

    def destaque(fala, perto, estilo, fs, altura=None, texto=None, ate=None, onde="cima", som="clique_caneta",
                 inicio=None, fonte=None):
        """Aparece inteiro quando ela começa a falar a frase (ou em `inicio`), some 0,4 s depois que
        ela termina (ou quando entra o próximo destaque)."""
        tp = tempos(words, fala, perto)
        t0 = inicio if inicio is not None else tp[0]
        fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.4)
        y = y_de(onde, t0, fim, altura or fs)
        txt = texto or fala
        D.add(t0, fim, lambda t1: [ev_inteiro(t0, t1, txt, 540, y, estilo, fs, fonte)],
              [(som, t0)] if som else [])

    def linhas(falas, perto, estilo, fs, dy, textos=None, fontes=None, ate=None, onde="cima"):
        """Várias linhas bem próximas; cada linha entra inteira quando ela começa a falar a linha."""
        tp = tempos(words, " ".join(falas), perto, janela=4)
        inicio, n = [], 0
        for ln in falas:
            inicio.append(tp[n]); n += len(ln.split())
        fim = ate or (fim_fala(words, tp[-1] + 0.01) + 0.4)
        fss = fs if isinstance(fs, list) else [fs] * len(falas)
        est = estilo if isinstance(estilo, list) else [estilo] * len(falas)
        alt = (len(falas) - 1) * dy + max(fss)
        yc = y_de(onde, inicio[0], fim, alt)
        y0 = yc - (len(falas) - 1) * dy // 2
        txts = textos or falas

        def fazer(t1):
            return [ev_inteiro(inicio[k], t1, txts[k], 540, y0 + k * dy, est[k], fss[k],
                               fontes[k] if fontes else None) for k in range(len(falas))]
        D.add(inicio[0], fim, fazer, [("clique_caneta", t) for t in inicio])

    return D, destaque, linhas
