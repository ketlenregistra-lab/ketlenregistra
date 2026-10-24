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
| Ritmo | Cortes rápidos, **nenhuma pausa** entre frases. Vídeo nunca parado. Sem música de fundo. As partes com ela falando ficam **um pouco aceleradas** (`"velocidade": 1.15` no plano; voz sem mudar o tom) — rápido mas entendível. **A abertura (até a primeira camada/tutorial) fica em velocidade normal** — ela achou rápido demais no Dia 3: use `"velocidades": {"Video1": 1.0, ...}` para esses vídeos. **Narração sobre gravação de tela (tomada `"tela"`) nunca é acelerada nem cortada.** |
| Título (desafio) | Nos vídeos do desafio, abre com **"dia N de 20"** + tema (ex.: `dia 1 de 20\Nconfigurações\Nda câmera`), na mesma fonte e amarelo dos destaques, **surgindo com fade in** (sem digitação) e **clique de mouse**. Fica do início até a primeira camada/frase importante (~2 s). Fora do desafio, sem título. |
| Cor | **Padrão atual (desde o Dia 3): cenário com luz rosa** → `assets/cor_rosa.cube`, medida do vídeo "Filtros antes x depois" dela (mesmo trecho sem filtro × com os filtros do CapCut; erro ~1/255). É a marca dela agora — **não mexer**. Fundo rosa/magenta escuro, pele natural, roupa clara limpa. Brutos HDR são convertidos para SDR antes. **Se ela já tratou a cor no CapCut (ex.: Dia 4, vídeo de antes/depois com estalo de dedos), use `"cor": "nenhuma"`** — não mexe na cor e deixa a tomada com o efeito dela `"inteiro"`. Para vídeos antigos no cenário branco (Dias 1 e 2) use `"cor": "antiga"` no plano (`cor_ketlen.cube` p/ HDR, `cor_ketlen_sdr.cube` p/ SDR). **Nunca** deixe a pele amarelada, alaranjada ou rosada demais. Nitidez leve. |
| Legenda automática | Fonte SYSTEM (usamos Inter SemiBold), MAIÚSCULAS, branca com sombra suave, 2–3 palavras por vez sincronizadas com a fala. Tarja **rosa bebê #F4BBCE (4ª bolinha rosa do CapCut), 20% de opacidade**, cantos arredondados. Centro em y=2600 (de 3840). |
| Destaques | Frases-chave em **amarelo manteiga #FDFB84**, fonte **A Hint of Sass** (`assets/fontes/AHintofSass.ttf`, a fonte da identidade dela — não troque), **minúsculas**, **uma palavra por linha** (palavrinhas curtas juntas, ex.: "pra não"), grandes, **por cima do corpo** (logo abaixo do queixo). Aparecem **digitando letra por letra** com **som de teclado** em cada letra. Enquanto o destaque está na tela, a legenda automática some e o **vídeo sobe e aproxima (~18%)** — ela fica no alto do quadro e a frase ocupa o corpo, sem espaço vazio em cima. **Se ela aponta pra cima** na palavra (ex.: "texto", "clique"), marque `[a, b, "texto", "cima"]`: o destaque fica **acima da cabeça** e o vídeo não sobe. |
| Camadas | Print/foto/vídeo entra **só enquanto ela fala do assunto** e sai logo depois. **Print em tela cheia**: card arredondado centralizado (~54% da largura, sem cobrir tudo), **desfoque nela atrás**, **rótulo em cima** em amarelo A Hint of Sass num fundinho **rosa mais escuro #EE8FAD (~85% opaco)** (ex.: "configurações da câmera") — **só no print que mostra exatamente aquilo** (no Dia 1: só na gravação dos Ajustes, não no vídeo da câmera do 4K/exposição) — e a **legenda automática passa para baixo do print**. Card pequeno (ex.: foto de produto): flutua acima da cabeça, sem desfoque. Toda camada entra com **clique de mouse**. Opção `"fundo": {"arquivo": "video_pronto.mov", "de": 0}`: em vez de desfocar ela, toca um vídeo pronto dela desfocado atrás do print (estilo da referência do Dia 2, mostrando o resultado). |
| Vídeo atrás dela | Quando ela menciona um vídeo/conteúdo anterior ("onde eu mostrei alguns efeitos sonoros"), **um card com o vídeo pronto dela aparece ATRÁS dela** (ela recortada na frente, por segmentação), de um lado só, **sem som**, breve, entrando na palavra-chave, com clique. Use o trecho do vídeo pronto que fala exatamente do assunto. Plano: `"atras": [{"arquivo": "video_pronto.mov", "t0": 2.5, "t1": 4.75, "trechos": [0]}]`. Para mostrar o **resultado** de um tutorial (ex.: Dia 5, "esse zoom aqui"), use o fim da gravação de tela com `"recorte": "900:1600:432:530"` (só o preview do CapCut). Também aceita **imagem PNG com transparência** (ex.: logo do CapCut quando ela diz "dentro do CapCut"): `{"arquivo": "capcut_logo.png", "t0": 14.4, "t1": 15.9, "largura": 620, "x": 1380, "y": 420}`. Se a imagem vier com o xadrez de "transparente" desenhado, recorte o ícone e aplique cantos arredondados antes. Não deixe junto com o título. |
| Perguntas espalhadas | Quando ela diz que "muita gente perguntou", **a pergunta aparece em amarelo umas 4 vezes espalhada pela tela** (menor, levemente inclinada, digitando em sequência com teclado) e some quando entra o próximo destaque. Plano: `"espalhados": [{"t0": 4.8, "t1": 6.44, "textos": ["quais efeitos\\Nsonoros?", ...x4]}]`. |
| Legenda quebrada (demonstração) | **Se ela mandar a imagem da legenda quebrada (PNG sem fundo), use a dela** como camada `"tipo": "card"` acima da cabeça (`"largura": 1800, "y": 430`), entrando **no quadro exato em que ela levanta a mão** (confira olhando quadros a cada 0,1 s) — o título tem que sair antes. Caso contrário:  Quando o assunto é o bug da legenda automática do CapCut (Dia 3: "elas ficam assim?"), a **própria legenda dela aparece quebrada, acima da cabeça** (ela aponta pra cima), só o texto, sem print/camada: tudo em MAIÚSCULAS e **só as letras com acento/ç deformadas** (outra fonte, minúsculas, tamanho errado), sem a tarja rosa. **Só no instante da pergunta, quando ela levanta a mão** (começa na palavra "assim?", não antes) e **entra com clique**; nas frases seguintes a legenda volta ao normal. Use uma frase de exemplo cheia de acentos: `"legenda_quebrada": [[3.21, 4.5, "LEGENDA AUTOMÁTICA\\\\NNÃO É LEGÍVEL"]]`. Plano: `"legenda_quebrada": [[0.0, 5.3]]`. Depois volta ao normal. |
| Setas | Quando ela aponta/fala de algo do cenário ("esse vaso de planta"), **seta branca desenhada à mão** apontando para o objeto, com som de **pop** (estalo seco, não gotinha). No plano: `"setas": [{"t0":32.3,"t1":36.8,"de":[1640,1560],"para":[1900,2060]}]` (coordenadas 4K; confira o lugar do objeto num quadro). |
| Zoom de ênfase | Zoom-in **leve (8%)** centrado no rosto quando ela fala algo com ênfase ("atenção", frase de impacto). Sobe em 0,2 s, segura, volta. **Todo zoom in tem swoosh** — inclusive quando o vídeo sobe/aproxima num destaque. O swoosh é exclusivo do zoom. |
| Graça | Quando ela faz uma piada: imagem em **preto e branco** + voz de **fonógrafo** (só a voz filtrada — **sem chiado/estalos de disco**, ela não gosta). Sem eco, sem outros sons por cima. Ela costuma marcar a graça com "gente..." + risadinha. **O P&B cobre a frase inteira da piada, do começo até o fim da risada** (deixe a tomada com `"inteiro"` para não cortar a risadinha). |
| Final | Termina com **clique de mouse** e a tela **apaga** (como desligar a luz). Nada escrito. |
| Exportação | 4K (2160×3840), 30 fps. Mande também uma versão 1080p leve para ela ver no celular. |

Efeitos sonoros que ela usa no CapCut (referência de timbre): cliques (mouse, caneta, botão), swish/whoosh, vento curto, clique de câmera, papel rasgando, brilho/mágica, glitch, teclado, estalo de dedo. Sons da skill: `assets/sfx/swoosh.wav` e `assets/sfx/teclado.wav` foram **recortados do CapCut dela** (swoosh só no zoom; `teclado.wav` é o trecho contínuo de digitação, tocado enquanto as letras aparecem — **não** recorte em batidas soltas por letra: rápido demais soa como dinheiro sendo contado); `assets/sfx/click_mouse.wav` (camadas e final) foi aprovado por ela; `assets/sfx/pop.wav` só nas setas. **Nunca use "pop"/gotinha** — ela não gosta. Se ela mandar os arquivos de áudio dela, prefira os dela.

## Fluxo de trabalho

Tudo em `scripts/editar.py`. Use uma pasta de trabalho no scratchpad.

1. **Baixar** os brutos e camadas do Drive (`https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t`).
2. **Transcrever** cada bruto (palavra por palavra, com tempo):
   `python3 scripts/editar.py transcrever --brutos BRUTOS --trabalho TRAB`
3. **Escolher as tomadas**: compare as transcrições com o roteiro e escolha a melhor tomada de cada frase (corte repetições, erros e frases fora do roteiro — confirme com ela se uma frase fora do roteiro parecer importante). Escreva `TRAB/plano.json`:
   ```json
   {"brutos": "BRUTOS", "trabalho": "TRAB", "saida": "Dia2_Tema",
    "prompt": "iPhone 17, 4K, 30 fps.",
    "tomadas": [["IMG_2577", 3.75, 11.45], ["IMG_2578", 1.65, 5.85],
                ["Camada", 0.0, 106.4, "tela"]]}
   ```
   Se um trecho tiver tropeço no meio, transcreva só aquela janela de novo para achar o corte exato.
   Tutorial narrado sobre gravação de tela (ex.: Dia 2): ponha a gravação na pasta dos brutos, use a tomada com `"tela"` (sem cortar pausas e sem acelerar, para tela e voz não se separarem; `"inteiro"` só não corta pausas, ex.: trecho com risada) e, no plano, uma camada `tela_cheia` com o mesmo arquivo, `de`=início, `ate`=fim, `t0`/`t1` = posição dela na linha do tempo, mais `fundo` com o vídeo pronto dela.
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
   Depois gere a **versão de entrega 4K leve, com no máximo ~40 MB** (arquivos de 75+ MB não baixam no celular dela): encode em 2 passadas com bitrate = 40 MB ÷ duração (≈ `2300k` para 2 min, `3500k` para 1 min 30), ex.: `ffmpeg -i SAIDA_4K.mp4 -c:v libx264 -preset medium -b:v 2300k -pass 1 -an -f null /dev/null && ffmpeg -i SAIDA_4K.mp4 -c:v libx264 -preset medium -b:v 2300k -maxrate 5M -bufsize 10M -pass 2 -profile:v high -level 5.1 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart SAIDA_4K_leve.mp4`, e a cópia 1080p; envie as duas pela conversa (o conector do Drive não sobe arquivos grandes).

7. **Legenda estratégica do post** — SEMPRE, junto com a entrega final (ela quer crescer o Instagram e passar confiança). **Use o formato dela, curto** (legenda longa ninguém lê):
   ```
   🎬 DIA N/20 — Desafio da edição!

   [1 linha que prende: afirmação/contradição sobre o tema] 👀💗

   [1–2 frases: o que o vídeo ensina, com as palavras-chave escritas — CapCut, nome dos filtros/recursos]

   Salva essa dica pra [benefício concreto]! 💗

   #DicasDeEdição #CapCut #[TemaDoDia] #EdiçãoDeVídeo #Videomaker
   ```
   Regras da skill `legenda-instagram`: gancho sem pergunta óbvia nem "você sabia que"; CTA direto (salvar); 5 hashtags do nicho em CamelCase. Explique em 1–2 linhas o porquê das escolhas.

## Cuidados que já aprendemos

- **Revise a legenda inteira antes de mandar a prévia** (liste o texto de todas as legendas): a transcrição erra ("-usear", "consegui" no lugar de "conseguia", "para me saber") e vícios como "mano" devem sair (`"correcoes": [[t, "mano", ""]]` remove a palavra). Na transcrição nova a cada `montar` os erros podem mudar.
- Não invente camadas que ela não pediu (no Dia 5 ela pediu para tirar um vídeo atrás dela no gancho).

- **Não coma palavras**: defina início/fim de cada tomada pelo **fim real da última palavra** na transcrição (campo `end`, não o início da palavra) + ~0,2 s de folga. O corte de pausas só considera silêncio o que está 30 dB abaixo da fala e mantém 0,12 s de cauda depois de cada palavra. Depois de montar, confira os finais de frase.

- Os brutos do iPhone são **HDR (HLG)**; o script converte para SDR antes da LUT. Não use a conversão `mobius` (deixa amarelada).
- Mostre a cor em quadros **4K reais** e em momentos em que ela está bonita (olho aberto, sorrindo) — quadro no meio da fala parece "deformado".
- Antes de mudar a cor, confira com ela num quadro; não faça exportação longa com cor não aprovada.
- Não rode prévia e 4K ao mesmo tempo (falta memória).
- Rede necessária no ambiente: `drive.usercontent.google.com`, `drive.google.com`, `docs.google.com`, `huggingface.co`, `cdn-lfs.huggingface.co`, `cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`, `us.aws.cdn.hf.co` (modelo de transcrição) e Dependências: `pip install faster-whisper`, ffmpeg com libass/zscale.
- A tarja de 20% fica fraca por cima de telas brancas (prints de Ajustes). Ela aceitou assim; se reclamar, aumente a opacidade só nesses trechos.
