#!/usr/bin/env bash
# Prepara a máquina para editar: pacotes Python + fontes Montserrat/Playfair em ~/.fonts
set -e
pip install -q faster-whisper onnxruntime fonttools brotli
TMP=$(mktemp -d); cd "$TMP"
npm pack -s @fontsource/montserrat @fontsource/playfair-display >/dev/null
for t in *.tgz; do mkdir -p x; tar xzf "$t" -C x; mv x/package "x/${t%%-[0-9]*}"; done
python3 - <<'P'
import glob, os
from fontTools.ttLib import TTFont
out = os.path.expanduser('~/.fonts'); os.makedirs(out, exist_ok=True)
for fam in ['montserrat', 'playfair-display']:
    for f in glob.glob(f'x/fontsource-{fam}/files/{fam}-latin-*-*.woff2'):
        if 'ext' in f: continue
        t = TTFont(f); t.flavor = None
        t.save(os.path.join(out, os.path.basename(f).replace('.woff2', '.ttf')))
print('fontes ok')
P
fc-cache -f >/dev/null 2>&1 || true
echo "pronto"
