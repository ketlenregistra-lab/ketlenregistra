#!/usr/bin/env python3
"""Edição de vídeos no padrão Ketlen.

Etapas (veja SKILL.md):
  transcrever  --brutos PASTA --trabalho PASTA
  montar       --plano plano.json     (tira as pausas, monta a voz e transcreve a linha do tempo final)
  renderizar   --plano plano.json --modo previa|final
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')
LUT = os.path.abspath(os.path.join(ASSETS, 'cor_ketlen.cube'))          # para brutos HDR (HLG) do iPhone
LUT_SDR = os.path.abspath(os.path.join(ASSETS, 'cor_ketlen_sdr.cube'))  # para brutos SDR (bt709)
LUT_ROSA = os.path.abspath(os.path.join(ASSETS, 'cor_rosa.cube'))       # PADRÃO desde out/2026: cenário rosa
COR_PADRAO = 'rosa'

# ---------------------------------------------------------------- estilo
W4K, H4K = 2160, 3840                     # tudo é desenhado em coordenadas 4K
LEG_Y = 2600                              # centro da legenda automática
# zona segura do Reels (em 4K): o Instagram cobre o topo (barra Reels/câmera), a base (@, legenda, música)
# e a direita (curtir/comentar/compartilhar). Todo texto/logo/camada importante fica dentro deste retângulo.
SEG_TOPO, SEG_BASE, SEG_ESQ, SEG_DIR = 527, 2920, 176, 1987   # medida do template de zona segura dela (Dia 9)
TV_OFF = 0.4                                # duração do final "tela desligada" (TV antiga apagando)
LEG_TAM, LEG_ESP, LEG_PADX, LEG_PADY = 64, 2, 40, 24
LEG_CAIXA, LEG_CAIXA_A = '&HCEBBF4&', '&HCC&'   # rosa bebê do CapCut (#F4BBCE), 20% de opacidade
DESTAQUE_COR = '&H0084FBFD'                     # amarelo manteiga da Ketlen (#FDFB84), BGR
FPS = 30
ZOOM = 0.08                                     # zoom de ênfase: 8%, leve
CARD_W, CARD_H, CARD_Y = 1170, 2060, 720        # print em tela cheia: centralizado; legenda embaixo ainda na zona segura
ROTULO_COR, ROTULO_A = '&HAD8FEE&', '&H26&'      # rótulo dos prints: rosa mais escuro (#EE8FAD), ~85% opaco
DESTAQUE_TAM, DESTAQUE_Y = 230, 1850            # destaques: uma palavra por linha, por cima do corpo
SUBIR = 0.18                                    # quanto o vídeo aproxima/sobe nos destaques
LEG_Y_PRINT = CARD_Y + CARD_H + 120             # legenda automática quando há print em tela cheia
ROTULO_TAM = 125
NITIDEZ = 'unsharp=5:5:0.35:5:5:0.0'


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ff(*args):
    sh(['ffmpeg', '-v', 'error', '-y', *args])


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True).stdout.strip())


def hdr(path):
    t = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                        '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True).stdout
    return 'arib-std-b67' in t or 'smpte2084' in t


def cor(path, nome=None):
    """HDR do iPhone -> SDR (hable) -> cor Ketlen (LUT medida da edição dela no CapCut)."""
    nome = nome or COR_PADRAO
    if nome == 'nenhuma':                  # ela já tratou a cor no CapCut: não mexe
        return 'format=yuv420p'
    luts = [os.path.join(ASSETS, f'cor_{x}.cube') for x in nome.split('+')]   # 'rosa', 'rosa_roupa', 'sala_branca+ketlen_sdr' (em sequência)
    if nome != 'antiga' and all(os.path.exists(x) for x in luts):
        pre = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=gbrp' \
            if hdr(path) else 'format=gbrp'
        cadeia = ','.join(f'lut3d={os.path.abspath(x)}:interp=tetrahedral' for x in luts)
        return f'{pre},{cadeia},{NITIDEZ},format=yuv420p'
    if hdr(path):
        return f'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=gbrp,' \
               f'lut3d={LUT}:interp=tetrahedral,{NITIDEZ},format=yuv420p'
    return f'format=gbrp,lut3d={LUT_SDR}:interp=tetrahedral,{NITIDEZ},format=yuv420p'


def ts(t):
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def wav16(path):
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def wav16_st(path):
    """Lê um wav estéreo 16 bits e devolve o canal esquerdo em float."""
    w = wave.open(path)
    return (np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768)[::w.getnchannels()]


def modelo():
    from faster_whisper import WhisperModel
    return WhisperModel('medium', device='cpu', compute_type='int8', cpu_threads=os.cpu_count() or 4)


def transcreve(m, wav, prompt=None):
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                                     capture_output=True, check=True).stdout, np.float32)
    segs, _ = m.transcribe(a, language='pt', word_timestamps=True, initial_prompt=prompt)
    return [[round(x.start, 2), round(x.end, 2), x.word.strip()] for s in segs for x in s.words]


# ---------------------------------------------------------------- 1. transcrever
def cmd_transcrever(a):
    os.makedirs(os.path.join(a.trabalho, 'audio'), exist_ok=True)
    vids = sorted(f for f in glob.glob(os.path.join(a.brutos, '*')) if f.lower().endswith(('.mov', '.mp4')))
    m = modelo(); out = {}
    for v in vids:
        n = os.path.splitext(os.path.basename(v))[0]
        w = os.path.join(a.trabalho, 'audio', n + '.wav')
        ff('-i', v, '-vn', '-ac', '1', '-ar', '16000', w)
        out[n] = transcreve(m, w)
        print(f'\n## {n} ({dur(v):.1f}s)\n' + ' '.join(f'{p}[{s}]' for s, e, p in out[n]), flush=True)
    json.dump(out, open(os.path.join(a.trabalho, 'transcricao.json'), 'w'), ensure_ascii=False, indent=0)


# ---------------------------------------------------------------- 2. montar (cortes rápidos, sem pausas)
def sem_pausas(x, inicio, fim, sr=16000, janela=0.02, min_pausa=0.18, folga=0.04, cauda=0.12):
    k = int(janela * sr); m = len(x) // k
    if m == 0:
        return [(inicio, fim)]
    r = 20 * np.log10(np.sqrt((x[:m * k].reshape(m, k) ** 2).mean(1)) + 1e-9)
    q = r < np.percentile(r, 90) - 30          # só silêncio de verdade (finais de palavra são baixinhos)
    keep, i, start = [], 0, 0.0
    while i < m:
        if q[i]:
            j = i
            while j < m and q[j]:
                j += 1
            if (j - i) * janela >= min_pausa:
                s, e = i * janela + cauda, j * janela - folga   # mantém o finzinho da palavra antes da pausa
                if s > start:
                    keep.append((start, s))
                start = e
            i = j
        else:
            i += 1
    if (fim - inicio) - start > 0.05:
        keep.append((start, fim - inicio))
    return [(inicio + s, inicio + e) for s, e in keep if e - s > 0.12]


def fps_do_plano(p):
    """Quadros por segundo do vídeo final = o dos brutos dela (24, 25 ou 30); converter duplica quadros e "trava"."""
    if p.get('fps'):
        return int(p['fps'])
    for x in sorted(glob.glob(os.path.join(p['brutos'], '*'))):
        if x.lower().endswith(('.mov', '.mp4')):
            r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate',
                                '-of', 'csv=p=0', x], capture_output=True, text=True).stdout.strip().strip(',')
            try:
                a, b = (r.split('/') + ['1'])[:2]; v = float(a) / float(b)
                return int(round(v))           # 23.976 -> 24, 25 -> 25, 29.97 -> 30
            except (ValueError, ZeroDivisionError):
                pass
    return 30


def cmd_montar(a):
    p = json.load(open(a.plano)); T = p['trabalho']
    global FPS; FPS = fps_do_plano(p)
    cache, cortes = {}, []
    for tom in p['tomadas']:
        n, i0, i1 = tom[:3]; flag = tom[3] if len(tom) > 3 else ''
        src = [x for x in glob.glob(os.path.join(p['brutos'], n + '.*')) if x.lower().endswith(('.mov', '.mp4'))]
        if src:   # nunca passa do fim da imagem (áudio às vezes é mais longo que o vídeo)
            dv = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=duration',
                                 '-of', 'csv=p=0', src[0]], capture_output=True, text=True).stdout.strip().strip(',')
            if dv and dv != 'N/A':
                i1 = min(i1, float(dv) - 1.0 / FPS)
        inteiro = flag in ('inteiro', 'tela')   # não corta pausas
        tela = flag == 'tela'                   # narração sobre gravação de tela: intocada (sem cortes e sem acelerar)
        if n not in cache:
            cache[n] = wav16(os.path.join(T, 'audio', n + '.wav'))
        x = cache[n][int(i0 * 16000):int(i1 * 16000)]
        v = 1.0 if tela else float(p.get('velocidades', {}).get(n, p.get('velocidade', 1.0)))   # rosto pode acelerar; narração sobre tela nunca
        for s, e in ([(i0, i1)] if inteiro else sem_pausas(x, i0, i1)):
            # alinha aos quadros (30 fps): a duração final (e-s)/v vira um número inteiro de quadros -> som e imagem juntos
            s = round(s * FPS) / FPS; e = s + max(1, round((e - s) / v * FPS)) / FPS * v
            cortes.append((n, round(s, 4), round(e, 6), v))
    json.dump(cortes, open(os.path.join(T, 'cortes.json'), 'w'))
    inp, f = [], []
    for i, (n, s, e, *vv) in enumerate(cortes):
        v = vv[0] if vv else 1.0
        inp += ['-i', os.path.join(T, 'audio', n + '.wav')]
        d = (e - s) / v
        tempo = f',atempo={v:.4f}' if v != 1.0 else ''          # acelera sem mudar o tom da voz
        f.append(f'[{i}:a]atrim={s:.6f}:{e:.6f},asetpts=PTS-STARTPTS{tempo},apad=whole_dur={d:.6f},atrim=duration={d:.6f},afade=t=in:d=0.015,afade=t=out:st={d - 0.02:.3f}:d=0.02[a{i}]')
    f.append(''.join(f'[a{i}]' for i in range(len(cortes))) + f'concat=n={len(cortes)}:v=0:a=1[o]')
    voz = os.path.join(T, 'voz.wav')
    ff(*inp, '-filter_complex', ';'.join(f), '-map', '[o]', voz)
    pal = transcreve(modelo(), voz, p.get('prompt'))
    json.dump(pal, open(os.path.join(T, 'palavras.json'), 'w'), ensure_ascii=False)
    print(f'{len(cortes)} cortes, {dur(voz):.1f}s\n' + ' '.join(f'{w}[{s}-{e}]' for s, e, w in pal))


# ---------------------------------------------------------------- 3. renderizar
IG_ENTRA, IG_CAUDA = 0.5, 2.6               # cartão final do Instagram: entra 0,5 s depois do preto, vídeo termina 2,6 s depois


def instagram_png(handle, W, sc, out, final=False):
    """Logo do Instagram desenhado + @ embaixo. final=True: logo grande em degradê (tela preta do fim); senão marca branca discreta."""
    from PIL import Image, ImageDraw, ImageFont
    L = int((330 if final else 110) * sc); fs = int((78 if final else 40) * sc)
    fonte = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', max(8, fs))
    txt = handle.upper(); tw = int(fonte.getlength(txt))
    w, h = max(L, tw) + 20, L + int(fs * 1.9)
    logo = Image.new('L', (L * 4, L * 4), 0); d = ImageDraw.Draw(logo); S = L * 4; e = int(S * 0.085)
    d.rounded_rectangle([e // 2, e // 2, S - e // 2, S - e // 2], int(S * 0.28), outline=255, width=e)
    r = int(S * 0.22); c = S // 2; d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=e)
    q = int(S * 0.055); d.ellipse([int(S * 0.74) - q, int(S * 0.26) - q, int(S * 0.74) + q, int(S * 0.26) + q], fill=255)
    logo = logo.resize((L, L), Image.LANCZOS)
    if final:   # degradê do Instagram (amarelo -> rosa -> roxo)
        import numpy as np
        y, x = np.mgrid[0:L, 0:L] / L; t = np.clip((x * 0.5 + (1 - y) * 0.5), 0, 1)[..., None]
        cores = np.array([[254, 218, 117], [250, 126, 30], [214, 41, 118], [150, 47, 191], [79, 91, 213]], float)
        pos = np.linspace(0, 1, len(cores)); rgb = np.stack([np.interp(t[..., 0], pos, cores[:, k]) for k in range(3)], -1)
        cor = Image.fromarray(rgb.astype('uint8'), 'RGB')
    else:
        cor = Image.new('RGB', (L, L), (255, 255, 255))
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); cor.putalpha(logo); img.paste(cor, ((w - L) // 2, 0), cor)
    ImageDraw.Draw(img).text((w // 2, L + int(fs * 0.45)), txt, font=fonte, fill=(255, 255, 255, 255), anchor='mt')
    img.save(out); return w, h


TELA_W = 1764                              # largura útil da gravação de tela do iPhone dela dentro do quadro 2160 (o resto é faixa preta)


def celular_png(W, H, sc, out):
    """Moldura de iPhone (aro rosa, cantos bem arredondados, fundo preto) com o buraco da tela transparente."""
    from PIL import Image, ImageDraw
    ch = int(3000 * sc) // 2 * 2; cw = int(ch * TELA_W / 3840) // 2 * 2   # grande (menor ficou "longe demais"); a legenda vai por cima da base dele, dentro da zona segura
    x0, y0 = (W - cw) // 2, int(440 * sc)
    b = int(52 * sc); r = int(190 * sc)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 - b, y0 - b, x0 + cw + b, y0 + ch + b], r + b, fill=(244, 187, 206, 255))      # aro rosa bebê por fora (#F4BBCE), identidade dela
    d.rounded_rectangle([x0 - b + int(6 * sc), y0 - b + int(6 * sc), x0 + cw + b - int(6 * sc), y0 + ch + b - int(6 * sc)],
                        r + b - int(6 * sc), fill=(238, 143, 173, 255))                                          # rosa mais forte no meio do aro (#EE8FAD)
    d.rounded_rectangle([x0 - int(10 * sc), y0 - int(10 * sc), x0 + cw + int(10 * sc), y0 + ch + int(10 * sc)], r + int(10 * sc), fill=(8, 8, 8, 255))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([x0, y0, x0 + cw, y0 + ch], r, fill=255)
    a = img.getchannel('A').point(lambda v: v); import PIL.ImageChops as C
    img.putalpha(C.subtract(a, m)); img.save(out); return x0, y0, cw, ch


def altura_card(c):
    from PIL import Image
    im = Image.open(c['arquivo']); return round(im.height * c.get('largura', 900) / im.width)


def arredondar(arq, lw, out, sc):
    """Print/foto redimensionado para a largura lw com cantos arredondados (PNG com transparência)."""
    from PIL import Image, ImageDraw
    im = Image.open(arq).convert('RGBA')
    im = im.resize((lw, round(im.height * lw / im.width) // 2 * 2), Image.LANCZOS)
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], int(50 * sc), fill=255)
    im.putalpha(m); im.save(out)


def garantir_assets(T):
    fontes = os.path.abspath(os.path.join(ASSETS, 'fontes'))   # A Hint of Sass: fonte dos destaques
    sfx = os.path.abspath(os.path.join(ASSETS, 'sfx'))   # click_mouse.wav e swoosh.wav (nada de "pop"/gotinha)
    from PIL import Image, ImageDraw
    mk = os.path.join(T, 'mascara_print.png')
    if not os.path.exists(mk):
        m = Image.new('L', (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, CARD_W - 1, CARD_H - 1], 50, fill=255); m.save(mk)
    return fontes, sfx, mk


MODELO_SEG = 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite'


def mascara_pessoa(T, base, t0, t1, out):
    """Silhueta dela quadro a quadro (branco = pessoa) entre t0 e t1 da base, para pôr vídeos ATRÁS dela."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    from PIL import Image, ImageFilter
    mod = os.path.join(T, 'selfie.tflite')
    if not os.path.exists(mod):
        sh(['curl', '-sSfL', '-o', mod, MODELO_SEG])
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=mod), output_confidence_masks=True))
    w, h = 540, 960
    src = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', base, '-vf',
                            f'fps={FPS},scale={w}:{h},format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    dst = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{w}x{h}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'ffv1', out], stdin=subprocess.PIPE)
    while True:
        buf = src.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        a = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(a)))
        fundo = np.squeeze(np.asarray(r.confidence_masks[0].numpy_view(), dtype=np.float32))
        m = Image.fromarray((np.clip(1 - fundo, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        dst.stdin.write(m.tobytes())
    dst.stdin.close(); dst.wait(); src.wait(); seg.close()


def seta_png(de, para, W, H, out):
    """Seta branca desenhada à mão (curva + ponta), em tela inteira transparente."""
    from PIL import Image, ImageDraw
    sc = W / W4K; (x0, y0), (x1, y1) = [(x * sc, y * sc) for x, y in (de, para)]
    dx, dy = x1 - x0, y1 - y0; L = (dx * dx + dy * dy) ** 0.5
    cx, cy = (x0 + x1) / 2 - dy * 0.25, (y0 + y1) / 2 + dx * 0.25          # curvinha
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1)
           for u in np.linspace(0, 1, 60)]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); lw = max(3, int(14 * sc))
    d.line(pts, fill=(255, 255, 255, 255), width=lw, joint='curve')
    ex, ey = pts[-1]; px, py = pts[-6]; ang = np.arctan2(ey - py, ex - px); k = 0.16 * L
    for s in (+0.5, -0.5):
        d.line([(ex, ey), (ex - k * np.cos(ang + s), ey - k * np.sin(ang + s))], fill=(255, 255, 255, 255), width=lw)
    for x, y in [pts[0], (ex, ey)]:
        d.ellipse([x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2], fill=(255, 255, 255, 255))
    im.save(out)


def digitacao(a, b, txt):
    """Divide o destaque em letras ('\\N' é quebra de linha) e devolve o instante em que cada letra aparece."""
    toks = re.findall(r'\\N|.', txt)
    letras = [i for i, x in enumerate(toks) if x != '\\N']
    dt = min(0.06, 0.6 * (b - a) / max(1, len(letras)))
    tempos, k = [], 0
    for x in toks:
        tempos.append(a + k * dt)
        if x != '\\N':
            k += 1
    return toks, tempos


def dest(p):
    """Destaques como (a, b, txt); o 4º campo opcional "cima" fica em cima_(p)."""
    return [tuple(d[:3]) for d in p.get('destaques', [])]


def cima_(p):
    """Destaques marcados "cima": ficam acima da cabeça (ela aponta pra cima) e não sobem o vídeo."""
    return {(d[0], d[1]) for d in p.get('destaques', []) if len(d) > 3 and (d[3] == 'cima' or isinstance(d[3], (int, float)))}


def y_destaque(p, a, b):
    """Altura do destaque: número no 4º campo = y fixo (ex.: em cima da gravação de tela), "cima" = 430, senão no corpo."""
    for d in p.get('destaques', []):
        if (d[0], d[1]) == (a, b) and len(d) > 3:
            return max(SEG_TOPO, d[3]) if isinstance(d[3], (int, float)) else SEG_TOPO + 80
    return DESTAQUE_Y


POS_ESPALHADOS = [(560, 640, -7), (1600, 780, 6), (430, 1680, -5), (1740, 1580, 7), (1080, 520, -3), (1080, 3000, 4)]


def espalhados(p):
    """Frases curtas espalhadas pela tela (ex.: 4x "quais efeitos sonoros?"): cada uma digita em sequência e todas somem em t1."""
    out = []
    for e in p.get('espalhados', []):
        t0, t1, txts = e['t0'], e['t1'], e['textos']; gap = min(0.45, 0.7 * (t1 - t0) / len(txts))
        for i, txt in enumerate(txts):
            x, y, rot = (e.get('posicoes') or POS_ESPALHADOS)[i % len(POS_ESPALHADOS)]
            a = t0 + i * gap
            out.append((a, a + min(0.5, gap), t1, txt, x, y, rot))
    return out


ACENTOS = set('ÁÀÂÃÉÊÍÓÔÕÚÇáàâãéêíóôõúç')


def quebrada(t):
    """Imita o bug do CapCut com fonte sem português: só as letras com acento/ç caem em outra fonte, minúsculas e fora do tamanho."""
    out = []
    for w in t.split(' '):
        for i, ch in enumerate(w):
            if ch in ACENTOS:
                out.append('{\\fnDejaVu Serif\\fs118\\b0}' + ch.lower() + '{\\r}')
            else:
                out.append(ch)
        out.append(' ')
    return ''.join(out).strip()


def legendas(p, T, fontes):
    from PIL import ImageFont
    fonte = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
    f100 = ImageFont.truetype(fonte, 100); a_, d_ = f100.getmetrics(); em = LEG_TAM * 100 / (a_ + d_)
    fnt = ImageFont.truetype(fonte, max(1, round(em)))

    def caixa(t, fnt=fnt, em=em, esp=LEG_ESP, cy=LEG_Y, cor=None, alfa=None, padx=LEG_PADX, pady=LEG_PADY):
        w = fnt.getlength(t) + esp * (len(t) - 1) + 2 * padx; h = em * 0.78 + 2 * pady; r = min(30, h / 2)
        x0, y0 = W4K / 2 - w / 2, cy - h / 2
        path = (f'm {r:.0f} 0 l {w - r:.0f} 0 b {w:.0f} 0 {w:.0f} 0 {w:.0f} {r:.0f} l {w:.0f} {h - r:.0f} '
                f'b {w:.0f} {h:.0f} {w:.0f} {h:.0f} {w - r:.0f} {h:.0f} l {r:.0f} {h:.0f} b 0 {h:.0f} 0 {h:.0f} 0 {h - r:.0f} '
                f'l 0 {r:.0f} b 0 0 0 0 {r:.0f} 0')
        return '{\\an7\\pos(%d,%d)\\bord0\\shad0\\1c%s\\1a%s\\p1}%s' % (x0, y0, cor or LEG_CAIXA, alfa or LEG_CAIXA_A, path)

    w = json.load(open(os.path.join(T, 'palavras.json')))
    for t, errado, certo in p.get('correcoes', []):
        for x in w:
            if abs(x[0] - t) < 0.3 and x[2] == errado:
                x[2] = certo
    w = [x for x in w if x[2]]                 # correção vazia = palavra removida (ex.: vício de linguagem)
    # destaque com altura fixa (em cima da gravação de tela) não divide espaço com a legenda: ela continua
    janelas = [(a, b) for a, b, _ in dest(p) if not isinstance(y_destaque(p, a, b), (int, float)) or y_destaque(p, a, b) == DESTAQUE_Y
               or (a, b) in {(d[0], d[1]) for d in p.get('destaques', []) if len(d) > 3 and d[3] == 'cima'}]
    if p.get('titulo_corpo') and p.get('titulo'):   # título no corpo (vídeo sobe): sem legenda branca nesse trecho
        janelas.append(tuple(p['titulo'][:2]))
    dentro = lambda t: any(x - 0.05 <= t < y for x, y in janelas)
    grupos, g = [], []
    for i, x in enumerate(w):
        if dentro(x[0]):                       # palavra já aparece no destaque amarelo
            if g: grupos.append(g); g = []
            continue
        g.append(x); txt = ' '.join(y[2] for y in g)
        prox_dentro = i + 1 < len(w) and dentro(w[i + 1][0])   # fecha o grupo antes do destaque: nenhuma palavra some
        if re.search(r'[.,?!]$', x[2]) or len(g) == 3 or len(txt) >= 16 or i == len(w) - 1 or prox_dentro:
            grupos.append(g); g = []
    ev = []
    cheias = [c for c in p.get('camadas', []) if c.get('tipo', 'tela_cheia') == 'tela_cheia']
    for i, g in enumerate(grupos):
        a = g[0][0]; b = grupos[i + 1][0][0] if i + 1 < len(grupos) else g[-1][1] + 0.4
        b = min(b, g[-1][1] + 0.5)
        b = min([b] + [x for x, y in janelas if a < x])   # sai quando o destaque amarelo entra
        if any(a < y and b > x for x, y in janelas):   # durante o destaque amarelo, sem legenda automática
            continue
        cy = LEG_Y_PRINT if any(a < c['t1'] and b > c['t0'] for c in cheias) else LEG_Y   # com print: legenda embaixo dele
        for x0, x1, y_ in p.get('legenda_y', []):   # ex.: gravação de tela em tela cheia -> legenda na faixa preta de baixo
            if x0 <= a < x1:
                cy = y_
        for c in p.get('camadas', []):         # card no peito que cobre a altura da legenda: legenda vai para baixo dele
            if c.get('tipo') == 'card' and a < c['t1'] and b > c['t0']:
                topo = c.get('y', 300); base_ = topo + altura_card(c)
                if topo - 60 < cy < base_ + 60:
                    cy = base_ + 120
        t = re.sub(r'(?<!\d)[.,]|[.,](?!\d)', '', ' '.join(y[2] for y in g).upper())
        if any(a < y and b > x for x, y, *_ in p.get('legenda_quebrada', [])):   # na demonstração, só a legenda quebrada
            continue
        ev.append(f'Dialogue: 0,{ts(a)},{ts(b)},Caixa,,0,0,0,,{caixa(t, cy=cy)}')
        ev.append(f'Dialogue: 1,{ts(a)},{ts(b)},Leg,,0,0,0,,{{\\an5\\pos({W4K // 2},{cy})}}{t}')
    for qa, qb, *qt in p.get('legenda_quebrada', []):   # demonstração do erro do CapCut, acima da cabeça
        ev.append(f'Dialogue: 1,{ts(qa)},{ts(qb)},Quebrada,,0,0,0,,{{\\an5\\pos({W4K // 2},{SEG_TOPO + 100})}}{quebrada(qt[0] if qt else "")}')
    if p.get('titulo'):                        # abertura do desafio: surge com fade (sem digitação)
        a, b, txt = p['titulo']
        ev.append(f'Dialogue: 2,{ts(a)},{ts(b)},Destaque,,0,0,0,,{{\\an5\\pos({W4K // 2},{DESTAQUE_Y if p.get('titulo_corpo') else 950}){chr(92) + 'fs160' if p.get('titulo_corpo') else ''}\\fad(250,200)}}{txt}')
    fs = ImageFont.truetype(os.path.join(fontes, 'AHintofSass.ttf'), 100); a_, d_ = fs.getmetrics(); em_r = ROTULO_TAM * 100 / (a_ + d_)
    fr = ImageFont.truetype(os.path.join(fontes, 'AHintofSass.ttf'), max(1, round(em_r)))
    for c in p.get('camadas', []):             # rótulo amarelo em fundinho rosa em cima do print
        if c.get('rotulo'):
            cy = (c.get('y', 300) - 95 if c.get('tipo', 'tela_cheia') != 'tela_cheia' else CARD_Y - 95); a, b = c['t0'], c['t1']
            ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Caixa,,0,0,0,,{{\\fad(150,150)}}"
                      + caixa(c['rotulo'], fr, em_r, 4, cy, ROTULO_COR, ROTULO_A, 44, 22))
            ev.append(f"Dialogue: 4,{ts(a)},{ts(b)},Rotulo,,0,0,0,,{{\\an5\\pos({W4K // 2},{cy})\\fad(150,150)}}{c['rotulo']}")
    for a, b_dig, b, txt, x, y, rot in espalhados(p):
        toks, tempos = digitacao(a, b_dig, txt)
        for i, t0 in enumerate(tempos):
            t1 = tempos[i + 1] if i + 1 < len(tempos) else b
            vis = ''.join(toks[:i + 1]); resto = ''.join(toks[i + 1:])
            fad = r'\fad(0,150)' if i + 1 == len(tempos) else ''
            ev.append(f'Dialogue: 2,{ts(t0)},{ts(t1)},Destaque,,0,0,0,,{{\\an5\\fs120\\frz{rot}\\pos({x},{y}){fad}}}{vis}'
                      + (f'{{\\alpha&HFF&}}{resto}' if resto else ''))
    for a, b, txt in dest(p):   # uma palavra por linha, por cima do corpo, digitando
        pal, linhas = txt.replace('\\N', ' ').split(), []
        for x in pal:                          # junta palavrinhas curtas ("pra não", "um")
            if linhas and len(linhas[-1]) + 1 + len(x) <= 7:
                linhas[-1] += ' ' + x
            else:
                linhas.append(x)
        txt = '\\N'.join(linhas); y = y_destaque(p, a, b)
        toks, tempos = digitacao(a, b, txt)
        for i, t0 in enumerate(tempos):
            t1 = tempos[i + 1] if i + 1 < len(tempos) else b
            vis = ''.join(toks[:i + 1]); resto = ''.join(toks[i + 1:])
            fad = r'\fad(0,180)' if i + 1 == len(tempos) else ''
            ev.append(f'Dialogue: 2,{ts(t0)},{ts(t1)},Destaque,,0,0,0,,{{\\an8\\fs{DESTAQUE_TAM}\\pos({W4K // 2},{y}){fad}}}{vis}'
                      + (f'{{\\alpha&HFF&}}{resto}' if resto else ''))
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W4K}
PlayResY: {H4K}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caixa,Inter SemiBold,{LEG_TAM},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Leg,Inter SemiBold,{LEG_TAM},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90623A4A,0,0,0,0,100,100,{LEG_ESP},0,1,0,3,5,0,0,0,1
Style: Destaque,AHintofSass,200,{DESTAQUE_COR},{DESTAQUE_COR},&H00000000,&HA0000000,0,0,0,0,100,100,6,0,1,0,2,5,80,80,0,1
Style: Quebrada,DejaVu Sans,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,0,0,0,1
Style: Rotulo,AHintofSass,{ROTULO_TAM},{DESTAQUE_COR},{DESTAQUE_COR},&H00000000,&H60000000,0,0,0,0,100,100,4,0,1,0,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    out = os.path.join(T, 'legendas.ass')
    open(out, 'w').write(cab + '\n'.join(ev) + '\n')
    return out


def audio_final(p, T, sfx, fim):
    voz = os.path.join(T, 'voz.wav')
    ev = []
    for qa, *_ in p.get('legenda_quebrada', []):   # legenda quebrada surge com clique
        ev.append(('click_mouse', qa, 0.8))
    for c in p.get('atras', []):             # vídeos atrás dela: clique ao surgir
        ev.append(('click_mouse', c['t0'], 0.8))
    for c in p.get('camadas', []):           # camadas: só clique de mouse
        ev.append(('click_mouse', c['t0'], 0.8))
    for s in p.get('setas', []):             # seta apontando algo do cenário: pop
        ev.append(('pop', s['t0'], 0.8))
    if p.get('titulo'):                      # título: clique quando surge
        ev.append(('click_mouse', p['titulo'][0], 0.8))
    for t in p.get('cliques', []):           # cliques avulsos: entrada/saída da gravação de tela já montada por ela
        ev.append(('click_mouse', t, 0.8))
    for a, b in p.get('zooms', []):          # swoosh do CapCut dela: pico logo no início do zoom
        ev.append(('swoosh', a - 0.05, 1.0))
    for a, b, _ in dest(p):                  # destaque também é zoom in: swoosh
        if (a, b) not in cima_(p):
            ev.append(('swoosh', a - 0.05, 1.0))
    if p.get('fechamento', True):
        ev.append(('click_mouse', fim - TV_OFF, 0.9))     # clique quando a tela "desliga"
    if p.get('instagram'):                   # cartão final com o @ (estilo referência do Dia 7): clique quando surge
        ev.append(('click_mouse', fim + IG_ENTRA, 0.7))
    # teclado: trecho contínuo de digitação gravado do CapCut dela, tocando enquanto as letras aparecem
    sr = 48000; tec = wav16_st(os.path.join(sfx, 'teclado.wav'))
    trilha = np.zeros(int((fim + 4) * sr))
    for a, b, txt in dest(p) + [(a, bd, txt) for a, bd, _, txt, *_ in espalhados(p)]:
        toks, tempos = digitacao(a, b, txt)
        n = int((tempos[-1] - a + 0.12) * sr)
        s = np.tile(tec, n // len(tec) + 1)[:n] * 0.8
        f_ = min(n, int(0.04 * sr)); s[-f_:] *= np.linspace(1, 0, f_)
        i = int(a * sr); trilha[i:i + n] += s[:len(trilha) - i]
    tw = os.path.join(T, 'teclado.wav'); wv = wave.open(tw, 'w'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(trilha, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
    gr = p.get('gracas', [])
    inp = ['-i', voz]; f = []
    mute = '+'.join(f'between(t,{a},{b})' for a, b in gr) or '0'
    f.append(f"[0]aresample=48000,volume=0:enable='{mute}',apad=pad_dur=3[m]")   # sobra para o preto/cartão final
    inp += ['-i', tw]; f.append('[1]aresample=48000[tk]')
    k = 2; mix = ['[m]', '[tk]']
    for j, (a, b) in enumerate(gr):          # voz de fonógrafo nos momentos de graça
        d = b - a
        inp += ['-i', voz]
        f.append(f'[{k}]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,highpass=f=500,lowpass=f=2800,'
                 f'equalizer=f=1400:t=q:w=1.2:g=7,asoftclip=type=atan,volume=1.1,afade=t=in:d=0.03,afade=t=out:st={d - 0.04:.2f}:d=0.04,'
                 f'adelay={int(a * 1000)}|{int(a * 1000)}[g{j}]')
        mix.append(f'[g{j}]'); k += 1
    for i, (n, t, v) in enumerate(ev):
        inp += ['-i', os.path.join(sfx, n + '.wav')]; ms = max(0, int(t * 1000))
        f.append(f'[{k}]volume={v},adelay={ms}|{ms}[s{i}]'); mix.append(f'[s{i}]'); k += 1
    f.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95[o]')
    out = os.path.join(T, 'audio_final.wav')
    ff(*inp, '-filter_complex', ';'.join(f), '-map', '[o]', '-ac', '2', out)
    return out


def cmd_renderizar(a):
    p = json.load(open(a.plano)); T = p['trabalho']; final = a.modo == 'final'
    global FPS; FPS = fps_do_plano(p)
    global COR_PADRAO; COR_PADRAO = p.get('cor', 'rosa')   # 'antiga' = cenário branco (Dias 1 e 2)
    W, H = (W4K, H4K) if final else (1080, 1920); sc = W / W4K
    fontes, sfx, mk = garantir_assets(T)
    cortes = json.load(open(os.path.join(T, 'cortes.json')))
    # 1) cada corte separado com cor (pouca memória; reaproveita se já existir)
    pasta = os.path.join(T, f'cortes_{a.modo}'); os.makedirs(pasta, exist_ok=True)
    lista = []
    for i, (n, s, e, *vv) in enumerate(cortes):
        v = vv[0] if vv else 1.0
        src = [x for x in glob.glob(os.path.join(p['brutos'], n + '.*')) if x.lower().endswith(('.mov', '.mp4'))][0]
        # gravação de tela que já está no vídeo (tomada "tela"): sem filtro de cor, a interface do CapCut fica como é
        meio = (s + e) / 2                     # pelo meio do corte: nas emendas o início cai a 1 ms da tomada anterior
        tela = any(t[0] == n and len(t) > 3 and t[3] == 'tela' and t[1] <= meio < t[2] for t in p['tomadas'])
        # cor por tomada (índice em "tomadas"): ex. Dia 7, abertura que ela já filtrou = "nenhuma", final sem filtro = "sala_branca"
        nome = next((p.get('cor_tomadas', {}).get(str(q)) for q, t in enumerate(p['tomadas'])
                     if t[0] == n and t[1] <= meio < t[2]), None) or COR_PADRAO
        cor_ = 'format=yuv420p' if tela else cor(src, nome)
        o = os.path.join(pasta, hashlib.md5(f'{n}{s}{e}{W}{v}{nome}{tela}{FPS}'.encode()).hexdigest()[:12] + '.mp4')
        if not os.path.exists(o):
            acel = f'setpts=PTS/{v:.4f},' if v != 1.0 else ''
            ff('-threads', '4', '-ss', f'{s:.4f}', '-i', src, '-vf', f'{acel}fps={FPS},scale={W}:{H},{cor_}',
               '-frames:v', str(round((e - s) / v * FPS)), '-an', '-c:v', 'libx264', '-preset', 'fast',
               '-crf', '12' if final else '18', '-pix_fmt', 'yuv420p', o + '.tmp.mp4')
            os.rename(o + '.tmp.mp4', o)
        lista.append(o); print(f'corte {i + 1}/{len(cortes)}', flush=True)
    open(os.path.join(pasta, 'lista.txt'), 'w').write(''.join(f"file '{x}'\n" for x in lista))
    base = os.path.join(pasta, 'base.mp4')
    ff('-f', 'concat', '-safe', '0', '-i', os.path.join(pasta, 'lista.txt'), '-c', 'copy', base)
    voz_d = dur(os.path.join(T, 'voz.wav')); fim = voz_d
    ass = legendas(p, T, fontes)
    aud = audio_final(p, T, sfx, fim)
    # 2) efeitos na linha do tempo
    inp = ['-i', base, '-i', aud]; f = []; k = 2
    zs = '+'.join(f'clip((it-{z0})/0.2,0,1)*clip(({z1}-it)/0.15,0,1)' for z0, z1 in p.get('zooms', [])) or '0'
    # durante os destaques amarelos o vídeo sobe e aproxima (ela fica no alto, a frase ocupa o corpo)
    zd = '+'.join(f'clip((it-{a})/0.25,0,1)*clip(({b}-it)/0.25,0,1)' for a, b in [(a, b) for a, b, _ in dest(p) if (a, b) not in cima_(p)]
                   + [(c['t0'], c['t1']) for c in p.get('camadas', []) if c.get('subir')]   # card no peito: ela sobe junto
                   + ([tuple(p['titulo'][:2])] if p.get('titulo_corpo') and p.get('titulo') else [])) or '0'   # título no corpo: sobe também
    cheias = [c for c in p.get('camadas', []) if c.get('tipo', 'tela_cheia') == 'tela_cheia']
    blur = '+'.join(f"between(t,{c['t0']},{c['t1']})" for c in cheias) or '0'
    gr = '+'.join(f'between(t,{x},{y})' for x, y in p.get('gracas', [])) or '0'
    pre = '0:v'
    for j, c in enumerate(p.get('atras', [])):   # vídeos pronto dela ATRÁS dela (ela recortada na frente), sem som
        t0, t1 = c['t0'], c['t1']; mpes = os.path.join(T, f'mascara_atras{j}.mkv')
        mascara_pessoa(T, base, t0, t1, mpes)
        trechos = c.get('trechos', [0]); cw, ch = int(820 * sc) // 2 * 2, int(1458 * sc) // 2 * 2
        xs = [int(200 * sc), int(1140 * sc)] if len(trechos) > 1 else [int(1140 * sc)]
        f.append(f'[{pre}]split=2[pa{j}][pb{j}]'); cur_a = f'pa{j}'
        for q, (de, x) in enumerate(zip(trechos, xs)):
            fd_a = f'setpts=PTS-STARTPTS+{t0}/TB,fade=t=in:st={t0}:d=0.2:alpha=1,fade=t=out:st={t1 - 0.2:.2f}:d=0.2:alpha=1[ac{j}{q}]'
            if c['arquivo'].lower().endswith('.png'):   # imagem com transparência (ex.: logo): quadrada, sem máscara
                lw = int(c.get('largura', 700) * sc) // 2 * 2
                inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', c['arquivo']]
                f.append(f'[{k}:v]fps={FPS},format=rgba,scale={lw}:-2,{fd_a}')
                f.append(f"[{cur_a}][ac{j}{q}]overlay={int(min(c.get('x', 1250), SEG_DIR - c.get('largura', 700)) * sc)}:{int(max(c.get('y', 380), SEG_TOPO) * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[ao{j}{q}]")
                cur_a = f'ao{j}{q}'; k += 1
                continue
            inp += ['-ss', str(de), '-t', str(t1 - t0 + 0.5), '-an', '-i', c['arquivo']]
            inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', mk]
            rec = f"crop={c['recorte']}," if c.get('recorte') else ''   # ex.: só o preview do CapCut numa gravação de tela
            f.append(f'[{k}:v]setpts=PTS-STARTPTS,fps={FPS},{rec}scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},format=rgba[av{j}{q}];'
                     f'[{k + 1}:v]fps={FPS},format=gray,scale={cw}:{ch},setpts=PTS-STARTPTS[am{j}{q}];[av{j}{q}][am{j}{q}]alphamerge,{fd_a}')
            f.append(f"[{cur_a}][ac{j}{q}]overlay={x}:{int(450 * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[ao{j}{q}]")
            cur_a = f'ao{j}{q}'; k += 2
        inp += ['-i', mpes]
        f.append(f'[{k}:v]scale={W}:{H},format=gray,setpts=PTS-STARTPTS+{t0}/TB[mp{j}];[pb{j}]format=rgba[pr{j}];'
                 f'[pr{j}][mp{j}]alphamerge[pp{j}];[{cur_a}][pp{j}]overlay=0:0:enable=\'between(t,{t0},{t1})\':eof_action=pass,format=yuv420p[pre{j}]')
        pre = f'pre{j}'; k += 1
    f.append(f"[{pre}]setpts=PTS-STARTPTS,zoompan=z='1+{ZOOM}*({zs})+{SUBIR}*({zd})':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*(0.42+0.58*({zd}))':d=1:s={W}x{H}:fps={FPS},"
             f"gblur=sigma={30 * sc:.0f}:enable='{blur}',"
             f"drawbox=x=0:y=0:w=iw:h=ih:color=black@0.35:t=fill:enable='{blur}',hue=s=0:enable='{gr}'[b0]")
    cur = 'b0'
    for j, c in enumerate(p.get('camadas', [])):
        t0, t1 = c['t0'], c['t1']; arq = c['arquivo']
        video = arq.lower().endswith(('.mov', '.mp4'))
        fd = f'fade=t=in:st={t0}:d=0.15:alpha=1,fade=t=out:st={t1 - 0.15:.2f}:d=0.15:alpha=1'
        if c.get('tipo', 'tela_cheia') == 'tela_cheia':
            CW, CH = int(CARD_W * sc) // 2 * 2, int(CARD_H * sc) // 2 * 2
            if c.get('fundo'):             # vídeo pronto dela tocando desfocado atrás do print (estilo referência)
                fu = c['fundo']; inp += ['-ss', str(fu.get('de', 0)), '-t', str(t1 - t0 + 0.5), '-i', fu['arquivo']]
                f.append(f'[{k}:v]setpts=PTS-STARTPTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},'
                         f'gblur=sigma={14 * sc:.0f},eq=brightness=-0.08,format=yuv420p,setpts=PTS-STARTPTS+{t0}/TB[fu{j}]')
                f.append(f"[{cur}][fu{j}]overlay=0:0:enable='between(t,{t0},{t1})':eof_action=pass[cf{j}]"); cur = f'cf{j}'; k += 1
            if video:
                de, ate = c.get('de', 0), c.get('ate', dur(arq)); vel = (ate - de) / (t1 - t0)
                inp += ['-ss', str(de), '-t', str(ate - de), '-i', arq]
                f.append(f'[{k}:v]setpts=(PTS-STARTPTS)/{vel:.4f},fps={FPS},scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},format=rgba[tv{j}]')
            elif c.get('inteira'):   # print largo (ex.: cards de filtros): inteiro, sem cortar, cantos arredondados, no topo do card
                lw = int(c.get('largura', 1800) * sc) // 2 * 2; png = os.path.join(T, f'inteira{j}_{W}.png'); arredondar(arq, lw, png, sc)
                inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', png]
                f.append(f'[{k}:v]fps={FPS},format=rgba,setpts=PTS-STARTPTS+{t0}/TB,{fd}[tc{j}]')
                f.append(f"[{cur}][tc{j}]overlay={(W - lw) // 2}:{int(CARD_Y * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[c{j}]")
                k += 1; cur = f'c{j}'
                continue
            else:
                inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', arq]
                f.append(f'[{k}:v]fps={FPS},scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},format=rgba[tv{j}]')
            inp += ['-loop', '1', '-t', str(t1 - t0 + 1), '-i', mk]
            f.append(f'[{k + 1}:v]fps={FPS},format=gray,scale={CW}:{CH},setpts=PTS-STARTPTS[tm{j}];[tv{j}][tm{j}]alphamerge,'
                     f'setpts=PTS-STARTPTS+{t0}/TB,{fd}[tc{j}]')
            f.append(f"[{cur}][tc{j}]overlay={(W - CW) // 2}:{int(CARD_Y * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[c{j}]")
            k += 2
        else:   # card flutuando acima da cabeça
            cw = int(c.get('largura', 900) * sc) // 2 * 2
            if not arq.lower().endswith('.png'):   # print/foto sem transparência: cantos arredondados (ex.: filtros no peito, Dia 6)
                png = os.path.join(T, f'card{j}_{W}.png'); arredondar(arq, cw, png, sc); arq = png
            inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', arq]
            f.append(f'[{k}:v]fps={FPS},format=rgba,scale={cw}:-1,setpts=PTS-STARTPTS+{t0}/TB,{fd}[tc{j}]')
            f.append(f"[{cur}][tc{j}]overlay={(W - cw) // 2}:{int(c.get('y', 300) * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[c{j}]")
            k += 1
        cur = f'c{j}'
    for j, s in enumerate(p.get('setas', [])):   # setas desenhadas
        png = os.path.join(T, f'seta{j}_{W}.png'); seta_png(s['de'], s['para'], W, H, png)
        inp += ['-loop', '1', '-t', str(s['t1'] - s['t0'] + 0.5), '-i', png]; t0, t1 = s['t0'], s['t1']
        f.append(f'[{k}:v]fps={FPS},format=rgba,setpts=PTS-STARTPTS+{t0}/TB,fade=t=in:st={t0}:d=0.15:alpha=1,'
                 f'fade=t=out:st={t1 - 0.15:.2f}:d=0.15:alpha=1[sa{j}]')
        f.append(f"[{cur}][sa{j}]overlay=0:0:enable='between(t,{t0},{t1})':eof_action=pass[s{j}]"); cur = f's{j}'; k += 1
    for j, (c0, c1) in enumerate(p.get('celular', [])):   # gravação de tela dentro de um iPhone sobre fundo preto (referência do Dia 8)
        png = os.path.join(T, f'celular_{W}.png'); x0, y0, cw, ch = celular_png(W, H, sc, png)
        inp += ['-loop', '1', '-t', f'{c1 + 1:.2f}', '-i', png]
        f.append(f'[{cur}]split[ce{j}a][ce{j}b];[ce{j}b]crop={int(TELA_W * sc) // 2 * 2}:{H}:{(W - int(TELA_W * sc) // 2 * 2) // 2}:0,'
                 f'scale={cw}:{ch},pad={W}:{H}:{x0}:{y0}:black[ce{j}c];[{k}:v]fps={FPS},format=rgba[ce{j}m];'
                 f"[ce{j}c][ce{j}m]overlay=0:0:eof_action=pass[ce{j}d];[ce{j}a][ce{j}d]overlay=0:0:enable='between(t,{c0},{c1})':eof_action=pass[ce{j}]")
        cur = f'ce{j}'; k += 1
    ig = p.get('instagram'); cauda = IG_CAUDA if ig else 0.8
    fecha = p.get('fechamento', True)          # false: termina com ela falando, sem "tela desligada" nem preto (Dia 10)
    if not fecha:
        cauda = 0
    # final "tela desligada" (TV antiga): a imagem achata numa linha brilhante, vira um pontinho e apaga
    t0 = fim - TV_OFF if fecha else fim
    if not fecha:
        f.append(f'[{cur}]format=yuv420p,ass={ass}:fontsdir={fontes},setpts=N/{FPS}/TB[vf]'); cur = 'vf'
    else:
        f.append(f'[{cur}]format=yuv420p,ass={ass}:fontsdir={fontes},setpts=N/{FPS}/TB,split[tvm][tvt];'
                 f'[tvm]trim=end={t0:.3f},setpts=PTS-STARTPTS[tva];'
                 f"[tvt]trim=start={t0:.3f}:end={fim:.3f},setpts=PTS-STARTPTS,eq=brightness='min(0.45,t*1.6)':contrast=1.1:eval=frame,"
                 f"scale=w='if(lt(t,0.24),{W},max(8,2*trunc({W}*(1-(t-0.24)/0.16)/2)))':h='max(8,2*trunc({H}*pow(max(0,1-t/0.24),3)/2))':eval=frame,"
                 f'format=yuva420p[tvs];color=black:s={W}x{H}:r={FPS}:d={TV_OFF:.3f}[tvk];'
                 f"[tvk][tvs]overlay=x='(W-w)/2':y='(H-h)/2':eval=frame:eof_action=pass,setsar=1,format=yuv420p[tvb];"
                 f'[tva][tvb]concat=n=2:v=1:a=0,tpad=stop_mode=add:stop_duration={cauda}:color=black[vf]'); cur = 'vf'
    if ig:   # @ discreto no canto (marca d'água) e cartão final com logo em degradê na tela preta
        m1 = os.path.join(T, f'ig_marca_{W}.png'); mw, mh = instagram_png(ig, W, sc, m1)
        m2 = os.path.join(T, f'ig_final_{W}.png'); fw, fh = instagram_png(ig, W, sc, m2, final=True)
        inp += ['-loop', '1', '-t', f'{fim + cauda:.2f}', '-i', m1, '-loop', '1', '-t', f'{fim + cauda:.2f}', '-i', m2]
        f.append(f'[{k}:v]fps={FPS},format=rgba,colorchannelmixer=aa=0.85[igm];[{k + 1}:v]fps={FPS},format=rgba,'
                 f'fade=t=in:st={fim + IG_ENTRA:.2f}:d=0.35:alpha=1[igf]')
        f.append(f"[{cur}][igm]overlay={W - mw - int(110 * sc)}:{int(560 * sc)}:enable='lt(t,{fim:.2f})':eof_action=pass[vm];"
                 f"[vm][igf]overlay={(W - fw) // 2}:{(H - fh) // 2}:enable='gte(t,{fim + IG_ENTRA:.2f})':eof_action=pass,format=yuv420p[v]")
        k += 2
    else:
        f.append(f'[{cur}]null[v]')
    saida = os.path.join(T, p.get('saida', 'video') + ('_4K.mp4' if final else '_previa.mp4'))
    enc = ['-preset', 'medium', '-crf', '16', '-profile:v', 'high', '-level', '5.1'] if final else ['-preset', 'veryfast', '-crf', '20']
    ff('-threads', '4', *inp, '-filter_complex', ';'.join(f), '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', *enc, '-r', str(FPS),
       '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k',
       '-t', f'{fim + cauda:.2f}', '-movflags', '+faststart', saida)
    print('PRONTO', saida)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('transcrever'); s.add_argument('--brutos', required=True); s.add_argument('--trabalho', required=True)
    s = sub.add_parser('montar'); s.add_argument('--plano', required=True)
    s = sub.add_parser('renderizar'); s.add_argument('--plano', required=True); s.add_argument('--modo', choices=['previa', 'final'], default='previa')
    a = ap.parse_args()
    {'transcrever': cmd_transcrever, 'montar': cmd_montar, 'renderizar': cmd_renderizar}[a.cmd](a)
