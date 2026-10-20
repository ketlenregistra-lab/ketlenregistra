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
LUT = os.path.abspath(os.path.join(ASSETS, 'cor_ketlen.cube'))

# ---------------------------------------------------------------- estilo
W4K, H4K = 2160, 3840                     # tudo é desenhado em coordenadas 4K
LEG_Y = 2600                              # centro da legenda automática
LEG_TAM, LEG_ESP, LEG_PADX, LEG_PADY = 64, 2, 40, 24
LEG_CAIXA, LEG_CAIXA_A = '&HD4C8F7&', '&HCC&'   # rosa bebê (#F7C8D4), 20% de opacidade
DESTAQUE_COR = '&H008CECF3'                     # amarelo manteiga (#F3EC8C), BGR
ZOOM = 0.08                                     # zoom de ênfase: 8%, leve
NITIDEZ = 'unsharp=5:5:0.35:5:5:0.0'
FONTE_GOCHI = 'https://raw.githubusercontent.com/google/fonts/main/ofl/gochihand/GochiHand-Regular.ttf'


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ff(*args):
    sh(['ffmpeg', '-v', 'error', '-y', *args])


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True).stdout.strip())


def hdr(path):
    t = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer',
                        '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
    return t in ('arib-std-b67', 'smpte2084')


def cor(path):
    """HDR do iPhone -> SDR (hable) -> cor Ketlen (LUT medida da edição dela no CapCut)."""
    base = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=gbrp' \
        if hdr(path) else 'format=gbrp'
    return f'{base},lut3d={LUT}:interp=tetrahedral,{NITIDEZ},format=yuv420p'


def ts(t):
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def wav16(path):
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


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
def sem_pausas(x, inicio, fim, sr=16000, janela=0.02, min_pausa=0.14, folga=0.05):
    k = int(janela * sr); m = len(x) // k
    if m == 0:
        return [(inicio, fim)]
    r = 20 * np.log10(np.sqrt((x[:m * k].reshape(m, k) ** 2).mean(1)) + 1e-9)
    q = r < np.percentile(r, 90) - 24
    keep, i, start = [], 0, 0.0
    while i < m:
        if q[i]:
            j = i
            while j < m and q[j]:
                j += 1
            if (j - i) * janela >= min_pausa:
                s, e = i * janela + folga, j * janela - folga
                if s > start:
                    keep.append((start, s))
                start = e
            i = j
        else:
            i += 1
    if (fim - inicio) - start > 0.05:
        keep.append((start, fim - inicio))
    return [(inicio + s, inicio + e) for s, e in keep if e - s > 0.12]


def cmd_montar(a):
    p = json.load(open(a.plano)); T = p['trabalho']
    cache, cortes = {}, []
    for n, i0, i1 in p['tomadas']:
        if n not in cache:
            cache[n] = wav16(os.path.join(T, 'audio', n + '.wav'))
        x = cache[n][int(i0 * 16000):int(i1 * 16000)]
        cortes += [(n, s, e) for s, e in sem_pausas(x, i0, i1)]
    json.dump(cortes, open(os.path.join(T, 'cortes.json'), 'w'))
    inp, f = [], []
    for i, (n, s, e) in enumerate(cortes):
        inp += ['-i', os.path.join(T, 'audio', n + '.wav')]
        d = e - s
        f.append(f'[{i}:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.02:.3f}:d=0.02[a{i}]')
    f.append(''.join(f'[a{i}]' for i in range(len(cortes))) + f'concat=n={len(cortes)}:v=0:a=1[o]')
    voz = os.path.join(T, 'voz.wav')
    ff(*inp, '-filter_complex', ';'.join(f), '-map', '[o]', voz)
    pal = transcreve(modelo(), voz, p.get('prompt'))
    json.dump(pal, open(os.path.join(T, 'palavras.json'), 'w'), ensure_ascii=False)
    print(f'{len(cortes)} cortes, {dur(voz):.1f}s\n' + ' '.join(f'{w}[{s}-{e}]' for s, e, w in pal))


# ---------------------------------------------------------------- 3. renderizar
def garantir_assets(T):
    fontes = os.path.join(T, 'fontes'); os.makedirs(fontes, exist_ok=True)
    g = os.path.join(fontes, 'GochiHand-Regular.ttf')
    if not os.path.exists(g):
        sh(['curl', '-sSfL', '-o', g, FONTE_GOCHI])
    sfx = os.path.join(T, 'sfx'); os.makedirs(sfx, exist_ok=True)
    sons = {
        'whoosh': ['-f', 'lavfi', '-i', 'anoisesrc=color=pink:d=0.55:a=0.9', '-af',
                   'highpass=f=400,lowpass=f=5000,bandpass=f=1800:width_type=o:w=2,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.25,volume=4'],
        'pop': ['-f', 'lavfi', '-i', "aevalsrc='0.8*sin(2*PI*(300*t+9000*t*t))*exp(-35*t)':d=0.15:s=48000"],
        'click': ['-f', 'lavfi', '-i',
                  "aevalsrc='0.9*(sin(2*PI*2400*t)*exp(-260*t)+0.6*sin(2*PI*900*t)*exp(-120*t)+0.5*(random(0)*2-1)*exp(-600*t))':d=0.12:s=48000",
                  '-af', 'highpass=f=300'],
    }
    for nome, args in sons.items():
        o = os.path.join(sfx, nome + '.wav')
        if not os.path.exists(o):
            ff(*args, '-ar', '48000', '-ac', '2', o)
    from PIL import Image, ImageDraw
    mk = os.path.join(T, 'mascara_tela.png')
    if not os.path.exists(mk):
        m = Image.new('L', (1564, 3400), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 1563, 3399], 80, fill=255); m.save(mk)
    return fontes, sfx, mk


def legendas(p, T, fontes):
    from PIL import ImageFont
    fonte = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
    f100 = ImageFont.truetype(fonte, 100); a_, d_ = f100.getmetrics(); em = LEG_TAM * 100 / (a_ + d_)
    fnt = ImageFont.truetype(fonte, max(1, round(em)))

    def caixa(t):
        w = fnt.getlength(t) + LEG_ESP * (len(t) - 1) + 2 * LEG_PADX; h = em * 0.78 + 2 * LEG_PADY; r = min(30, h / 2)
        x0, y0 = W4K / 2 - w / 2, LEG_Y - h / 2
        path = (f'm {r:.0f} 0 l {w - r:.0f} 0 b {w:.0f} 0 {w:.0f} 0 {w:.0f} {r:.0f} l {w:.0f} {h - r:.0f} '
                f'b {w:.0f} {h:.0f} {w:.0f} {h:.0f} {w - r:.0f} {h:.0f} l {r:.0f} {h:.0f} b 0 {h:.0f} 0 {h:.0f} 0 {h - r:.0f} '
                f'l 0 {r:.0f} b 0 0 0 0 {r:.0f} 0')
        return '{\\an7\\pos(%d,%d)\\bord0\\shad0\\1c%s\\1a%s\\p1}%s' % (x0, y0, LEG_CAIXA, LEG_CAIXA_A, path)

    w = json.load(open(os.path.join(T, 'palavras.json')))
    for t, errado, certo in p.get('correcoes', []):
        for x in w:
            if abs(x[0] - t) < 0.3 and x[2] == errado:
                x[2] = certo
    grupos, g = [], []
    for i, x in enumerate(w):
        g.append(x); txt = ' '.join(y[2] for y in g)
        if re.search(r'[.,?!]$', x[2]) or len(g) == 3 or len(txt) >= 16 or i == len(w) - 1:
            grupos.append(g); g = []
    ev = []
    for i, g in enumerate(grupos):
        a = g[0][0]; b = grupos[i + 1][0][0] if i + 1 < len(grupos) else g[-1][1] + 0.4
        b = min(b, g[-1][1] + 0.5)
        t = re.sub(r'[.,]', '', ' '.join(y[2] for y in g).upper())
        ev.append(f'Dialogue: 0,{ts(a)},{ts(b)},Caixa,,0,0,0,,{caixa(t)}')
        ev.append(f'Dialogue: 1,{ts(a)},{ts(b)},Leg,,0,0,0,,{{\\an5\\pos({W4K // 2},{LEG_Y})}}{t}')
    pop = r'\fad(180,180)\fscx92\fscy92\t(0,220,\fscx100\fscy100)'
    for a, b, txt in p.get('destaques', []):
        y = 950 if txt.count('\\N') >= 2 else 1000
        ev.append(f'Dialogue: 2,{ts(a)},{ts(b)},Destaque,,0,0,0,,{{\\an5\\pos({W4K // 2},{y}){pop}}}{txt}')
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W4K}
PlayResY: {H4K}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caixa,Inter SemiBold,{LEG_TAM},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Leg,Inter SemiBold,{LEG_TAM},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90623A4A,0,0,0,0,100,100,{LEG_ESP},0,1,0,3,5,0,0,0,1
Style: Destaque,Gochi Hand,190,{DESTAQUE_COR},{DESTAQUE_COR},&H00000000,&HA0000000,0,0,0,0,100,100,6,0,1,0,2,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    out = os.path.join(T, 'legendas.ass')
    open(out, 'w').write(cab + '\n'.join(ev) + '\n')
    return out


def audio_final(p, T, sfx, fim):
    voz = os.path.join(T, 'voz.wav')
    ev = []
    for c in p.get('camadas', []):
        ev += [('whoosh', c['t0'] - 0.15, 0.5), ('pop', c['t0'], 0.5)]
    for a, b, _ in p.get('destaques', []):
        ev.append(('click', a, 0.8))
    for a, b in p.get('zooms', []):
        ev.append(('whoosh', a - 0.1, 0.25))
    ev.append(('click', fim - 0.15, 0.9))
    gr = p.get('gracas', [])
    inp = ['-i', voz]; f = []
    mute = '+'.join(f'between(t,{a},{b})' for a, b in gr) or '0'
    f.append(f"[0]aresample=48000,volume=0:enable='{mute}',apad=pad_dur=1[m]")
    k = 1; mix = ['[m]']
    for j, (a, b) in enumerate(gr):          # voz de fonógrafo nos momentos de graça
        d = b - a
        inp += ['-i', voz, '-f', 'lavfi', '-t', f'{d}', '-i', "aevalsrc='0.5*if(lt(random(0),0.0012),random(1)*2-1,0)':s=48000"]
        f.append(f'[{k}]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,highpass=f=500,lowpass=f=2800,'
                 f'equalizer=f=1400:t=q:w=1.2:g=7,asoftclip=type=atan,volume=1.1[v{j}];[{k + 1}]highpass=f=1500,lowpass=f=7000[c{j}];'
                 f'[v{j}][c{j}]amix=inputs=2:normalize=0,afade=t=in:d=0.03,afade=t=out:st={d - 0.04:.2f}:d=0.04,'
                 f'adelay={int(a * 1000)}|{int(a * 1000)}[g{j}]')
        mix.append(f'[g{j}]'); k += 2
    for i, (n, t, v) in enumerate(ev):
        inp += ['-i', os.path.join(sfx, n + '.wav')]; ms = max(0, int(t * 1000))
        f.append(f'[{k}]volume={v},adelay={ms}|{ms}[s{i}]'); mix.append(f'[s{i}]'); k += 1
    f.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95[o]')
    out = os.path.join(T, 'audio_final.wav')
    ff(*inp, '-filter_complex', ';'.join(f), '-map', '[o]', '-ac', '2', out)
    return out


def cmd_renderizar(a):
    p = json.load(open(a.plano)); T = p['trabalho']; final = a.modo == 'final'
    W, H = (W4K, H4K) if final else (1080, 1920); sc = W / W4K
    fontes, sfx, mk = garantir_assets(T)
    cortes = json.load(open(os.path.join(T, 'cortes.json')))
    # 1) cada corte separado com cor (pouca memória; reaproveita se já existir)
    pasta = os.path.join(T, f'cortes_{a.modo}'); os.makedirs(pasta, exist_ok=True)
    lista = []
    for i, (n, s, e) in enumerate(cortes):
        src = [x for x in glob.glob(os.path.join(p['brutos'], n + '.*')) if x.lower().endswith(('.mov', '.mp4'))][0]
        o = os.path.join(pasta, hashlib.md5(f'{n}{s}{e}{W}'.encode()).hexdigest()[:12] + '.mp4')
        if not os.path.exists(o):
            ff('-threads', '4', '-ss', f'{s:.3f}', '-t', f'{e - s:.3f}', '-i', src, '-vf',
               f'fps=30,trim=duration={e - s:.3f},scale={W}:{H},{cor(src)}', '-an', '-c:v', 'libx264', '-preset', 'fast',
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
    zs = '+'.join(f'clip((t-{z0})/0.2,0,1)*clip(({z1}-t)/0.15,0,1)' for z0, z1 in p.get('zooms', [])) or '0'
    cheias = [c for c in p.get('camadas', []) if c.get('tipo', 'tela_cheia') == 'tela_cheia']
    blur = '+'.join(f"between(t,{c['t0']},{c['t1']})" for c in cheias) or '0'
    gr = '+'.join(f'between(t,{x},{y})' for x, y in p.get('gracas', [])) or '0'
    f.append(f"[0:v]setpts=PTS-STARTPTS,scale=w='trunc({W}*(1+{ZOOM}*({zs}))/2)*2':h=-2:eval=frame,"
             f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.42,gblur=sigma={30 * sc:.0f}:enable='{blur}',"
             f"drawbox=x=0:y=0:w=iw:h=ih:color=black@0.35:t=fill:enable='{blur}',hue=s=0:enable='{gr}'[b0]")
    cur = 'b0'
    for j, c in enumerate(p.get('camadas', [])):
        t0, t1 = c['t0'], c['t1']; arq = c['arquivo']
        video = arq.lower().endswith(('.mov', '.mp4'))
        fd = f'fade=t=in:st={t0}:d=0.15:alpha=1,fade=t=out:st={t1 - 0.15:.2f}:d=0.15:alpha=1'
        if c.get('tipo', 'tela_cheia') == 'tela_cheia':
            CW, CH = int(1564 * sc) // 2 * 2, int(3400 * sc) // 2 * 2
            if video:
                de, ate = c.get('de', 0), c.get('ate', dur(arq)); vel = (ate - de) / (t1 - t0)
                inp += ['-ss', str(de), '-t', str(ate - de), '-i', arq]
                f.append(f'[{k}:v]setpts=(PTS-STARTPTS)/{vel:.4f},fps=30,scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},format=rgba[tv{j}]')
            else:
                inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', arq]
                f.append(f'[{k}:v]fps=30,scale={CW}:{CH}:force_original_aspect_ratio=increase,crop={CW}:{CH},format=rgba[tv{j}]')
            inp += ['-loop', '1', '-t', str(t1 - t0 + 1), '-i', mk]
            f.append(f'[{k + 1}:v]fps=30,format=gray,scale={CW}:{CH},setpts=PTS-STARTPTS[tm{j}];[tv{j}][tm{j}]alphamerge,'
                     f'setpts=PTS-STARTPTS+{t0}/TB,{fd}[tc{j}]')
            f.append(f"[{cur}][tc{j}]overlay={(W - CW) // 2}:{int(220 * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[c{j}]")
            k += 2
        else:   # card flutuando acima da cabeça
            inp += ['-loop', '1', '-t', str(t1 - t0 + 0.5), '-i', arq]
            cw = int(c.get('largura', 900) * sc)
            f.append(f'[{k}:v]fps=30,format=rgba,scale={cw}:-1,setpts=PTS-STARTPTS+{t0}/TB,{fd}[tc{j}]')
            f.append(f"[{cur}][tc{j}]overlay={(W - cw) // 2}:{int(c.get('y', 300) * sc)}:enable='between(t,{t0},{t1})':eof_action=pass[c{j}]")
            k += 1
        cur = f'c{j}'
    f.append(f'[{cur}]format=yuv420p,ass={ass}:fontsdir={fontes},tpad=stop_mode=add:stop_duration=0.8:color=black,'
             f'fade=t=out:st={fim + 0.05:.2f}:d=0.08[v]')
    saida = os.path.join(T, p.get('saida', 'video') + ('_4K.mp4' if final else '_previa.mp4'))
    enc = ['-preset', 'medium', '-crf', '16', '-profile:v', 'high', '-level', '5.1'] if final else ['-preset', 'veryfast', '-crf', '20']
    ff('-threads', '4', *inp, '-filter_complex', ';'.join(f), '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', *enc, '-r', '30',
       '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k',
       '-t', f'{fim + 0.8:.2f}', '-movflags', '+faststart', saida)
    print('PRONTO', saida)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('transcrever'); s.add_argument('--brutos', required=True); s.add_argument('--trabalho', required=True)
    s = sub.add_parser('montar'); s.add_argument('--plano', required=True)
    s = sub.add_parser('renderizar'); s.add_argument('--plano', required=True); s.add_argument('--modo', choices=['previa', 'final'], default='previa')
    a = ap.parse_args()
    {'transcrever': cmd_transcrever, 'montar': cmd_montar, 'renderizar': cmd_renderizar}[a.cmd](a)
