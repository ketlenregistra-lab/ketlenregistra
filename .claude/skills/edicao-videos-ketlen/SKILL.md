---
name: edicao-videos-ketlen
description: Edita vídeos verticais (Reels/TikTok) da Ketlen no padrão de identidade dela — cortes rápidos sem pausas, cor Ketlen (LUT medida da edição dela no CapCut), legenda automática SYSTEM com tarja rosa bebê 20%, destaques em amarelo manteiga manuscrito, camadas (prints, fotos, gravações de tela) com desfoque atrás, zoom leve de ênfase, preto e branco + voz de fonógrafo nas piadas, efeitos sonoros em toda camada e final com clique apagando a tela. Exporta em 4K 30 fps. Use SEMPRE que a Ketlen pedir para editar um vídeo, montar um vídeo a partir de roteiro e vídeos brutos, fazer o "Dia N" de um desafio, cortar, legendar ou finalizar um vídeo dela, ou disser "edita no meu padrão".
---

# Edição de vídeos — padrão Ketlen

A Ketlen definiu este estilo como a identidade dela. **Não invente variações**: siga as regras abaixo em todo vídeo. Mudanças de estilo só quando ela pedir explicitamente (e aí atualize esta skill).

## O que pedir a ela antes de começar

1. **Roteiro** escrito (ordem das falas). Palavras trocadas na gravação ficam como ela falou.
2. **Vídeos brutos** (pasta no Google Drive, compartilhada como "qualquer pessoa com o link").
3. **Camadas**: prints, fotos, gravações de tela — e em que frase cada uma entra.
4. Momentos de **graça** (piada) e de **ênfase**, se ela já souber. Se não, proponha você e mostre na prévia.

## Regras do estilo

| Elemento | Regra |
|---|---|
| Ritmo | Cortes rápidos, **nenhuma pausa** entre frases. Vídeo nunca parado. Sem música de fundo. |
| Título (desafio) | Nos vídeos do desafio, abre com **"dia N de 20"** + tema (ex.: `dia 1 de 20\Nconfigurações\Nda câmera`), na mesma fonte e amarelo dos destaques, **surgindo com fade in** (sem digitação) e **clique de mouse**. Fica do início até a primeira camada/frase importante (~2 s). Fora do desafio, sem título. |
| Cor | **Aprovada por ela — não mexer.** `assets/cor_ketlen.cube` — medida pixel a pixel do bruto × edição dela no CapCut (Retrô americano + Bokeh + Qualidade II + 4K). Fundo sóbrio/acinzentado, pele natural. **Nunca** deixe a pele amarelada, alaranjada ou rosada demais (ela já reprovou as três). Nitidez leve. |
| Legenda automática | Fonte SYSTEM (usamos Inter SemiBold), MAIÚSCULAS, branca com sombra suave, 2–3 palavras por vez sincronizadas com a fala. Tarja **rosa bebê #F4BBCE (4ª bolinha rosa do CapCut), 20% de opacidade**, cantos arredondados. Centro em y=2600 (de 3840). |
| Destaques | Frases-chave em **amarelo manteiga #FDFB84**, fonte **A Hint of Sass** (`assets/fontes/AHintofSass.ttf`, a fonte da identidade dela — não troque), **minúsculas**, **uma palavra por linha** (palavrinhas curtas juntas, ex.: "pra não"), grandes, **por cima do corpo** (logo abaixo do queixo). Aparecem **digitando letra por letra** com **som de teclado** em cada letra. Enquanto o destaque está na tela, a legenda automática some. |
| Camadas | Print/foto/vídeo entra **só enquanto ela fala do assunto** e sai logo depois. **Print em tela cheia**: card arredondado centralizado (~54% da largura, sem cobrir tudo), **desfoque nela atrás**, **rótulo em cima** em amarelo A Hint of Sass num fundinho **rosa mais escuro #EE8FAD (~85% opaco)** (ex.: "configurações da câmera") — **só no print que mostra exatamente aquilo** (no Dia 1: só na gravação dos Ajustes, não no vídeo da câmera do 4K/exposição) — e a **legenda automática passa para baixo do print**. Card pequeno (ex.: foto de produto): flutua acima da cabeça, sem desfoque. Toda camada entra com **clique de mouse**. |
| Setas | Quando ela aponta/fala de algo do cenário ("esse vaso de planta"), **seta branca desenhada à mão** apontando para o objeto, com som de **pop** (estalo seco, não gotinha). No plano: `"setas": [{"t0":32.3,"t1":36.8,"de":[1640,1560],"para":[1900,2060]}]` (coordenadas 4K; confira o lugar do objeto num quadro). |
| Zoom de ênfase | Zoom-in **leve (8%)** centrado no rosto quando ela fala algo com ênfase ("atenção", frase de impacto). Sobe em 0,2 s, segura, volta. Sempre com **swoosh** de aproximação — o swoosh é exclusivo do zoom. |
| Graça | Quando ela faz uma piada: imagem em **preto e branco** + voz de **fonógrafo** (só esse efeito de voz). Sem eco, sem outros sons por cima. |
| Final | Termina com **clique de mouse** e a tela **apaga** (como desligar a luz). Nada escrito. |
| Exportação | 4K (2160×3840), 30 fps. Mande também uma versão 1080p leve para ela ver no celular. |

Efeitos sonoros que ela usa no CapCut (referência de timbre): cliques (mouse, caneta, botão), swish/whoosh, vento curto, clique de câmera, papel rasgando, brilho/mágica, glitch, teclado, estalo de dedo. Sons da skill: `assets/sfx/swoosh.wav` e `assets/sfx/tecla1-10.wav` foram **recortados do CapCut dela** (swoosh só no zoom; teclas na digitação dos destaques); `assets/sfx/click_mouse.wav` (camadas e final) foi aprovado por ela; `assets/sfx/pop.wav` só nas setas. **Nunca use "pop"/gotinha** — ela não gosta. Se ela mandar os arquivos de áudio dela, prefira os dela.

## Fluxo de trabalho

Tudo em `scripts/editar.py`. Use uma pasta de trabalho no scratchpad.

1. **Baixar** os brutos e camadas do Drive (`https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t`).
2. **Transcrever** cada bruto (palavra por palavra, com tempo):
   `python3 scripts/editar.py transcrever --brutos BRUTOS --trabalho TRAB`
3. **Escolher as tomadas**: compare as transcrições com o roteiro e escolha a melhor tomada de cada frase (corte repetições, erros e frases fora do roteiro — confirme com ela se uma frase fora do roteiro parecer importante). Escreva `TRAB/plano.json`:
   ```json
   {"brutos": "BRUTOS", "trabalho": "TRAB", "saida": "Dia2_Tema",
    "prompt": "iPhone 17, 4K, 30 fps.",
    "tomadas": [["IMG_2577", 3.75, 11.45], ["IMG_2578", 1.65, 5.85]]}
   ```
   Se um trecho tiver tropeço no meio, transcreva só aquela janela de novo para achar o corte exato.
4. **Montar** (tira todas as pausas e transcreve a linha do tempo final):
   `python3 scripts/editar.py montar --plano TRAB/plano.json`
   Use os tempos impressos para preencher o resto do plano:
   ```json
   "titulo": [0.1, 2.1, "dia 1 de 20\\Nconfigurações\\Nda câmera"],
   "correcoes": [[6.66, "Em", "E"]],
   "destaques": [[26.94, 28.3, "tem que\\Nter luz"]],
   "camadas":  [{"arquivo": "foto.png", "tipo": "card", "t0": 2.1, "t1": 3.3},
                {"arquivo": "tela.mp4", "t0": 7.4, "t1": 16.6, "de": 0, "ate": 13.6, "rotulo": "configurações da câmera"}],
   "setas":    [{"t0": 32.3, "t1": 36.8, "de": [1640, 1560], "para": [1900, 2060]}],
   "zooms":    [[3.6, 6.5]],
   "gracas":   [[41.95, 44.75]]   (piada: P&B + fonógrafo — use só se ela quiser; no Dia 1 ela pediu para cortar o trecho)
   ```
   (`tipo` padrão é `tela_cheia`; `de`/`ate` é o trecho do vídeo da camada, acelerado para caber em t0–t1.)
5. **Prévia** 1080p (~5 min) → mande para ela e espere aprovação:
   `python3 scripts/editar.py renderizar --plano TRAB/plano.json --modo previa`
6. **Final** 4K (~30–40 min, corte por corte para não estourar memória):
   `python3 scripts/editar.py renderizar --plano TRAB/plano.json --modo final`
   Gere a cópia 1080p a partir do 4K e envie os dois. Arquivos > ~50 MB não sobem pelo conector do Drive: entregue pela conversa.

## Cuidados que já aprendemos

- Os brutos do iPhone são **HDR (HLG)**; o script converte para SDR antes da LUT. Não use a conversão `mobius` (deixa amarelada).
- Mostre a cor em quadros **4K reais** e em momentos em que ela está bonita (olho aberto, sorrindo) — quadro no meio da fala parece "deformado".
- Antes de mudar a cor, confira com ela num quadro; não faça exportação longa com cor não aprovada.
- Não rode prévia e 4K ao mesmo tempo (falta memória).
- Rede necessária no ambiente: `drive.usercontent.google.com`, `drive.google.com`, `docs.google.com`, `huggingface.co`, `cdn-lfs.huggingface.co`, `cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`, `us.aws.cdn.hf.co` (modelo de transcrição) e Dependências: `pip install faster-whisper`, ffmpeg com libass/zscale.
- A tarja de 20% fica fraca por cima de telas brancas (prints de Ajustes). Ela aceitou assim; se reclamar, aumente a opacidade só nesses trechos.
