---
name: edicao-reels
description: Edita Reels (9:16) no padrão Ketlen Digital — legendas palavra a palavra, combinações de duas fontes, telas pretas de destaque, cards/gráficos na identidade do cliente (inclusive como camada ATRÁS da pessoa), zooms e efeitos sonoros de clique/pop/teclado, tudo dentro da grade segura do Instagram e nunca sobre o rosto. Use SEMPRE que a usuária pedir para editar vídeo, Reels, legendar vídeo, colocar efeito sonoro, "editar no padrão", "editar igual os da Julia", ou mandar uma pasta do Drive com vídeos + roteiros para edição.
---

# Edição de Reels — padrão Ketlen Digital

Padrão aprovado na edição dos 5 Reels da Julia Roque (contadora), novembro/2026.
O motor de edição está em `scripts/` e os 5 vídeos aprovados estão em `exemplos/` como referência
de como cada recurso foi usado. Leia um exemplo antes de escrever um vídeo novo.

## Regras de ouro (a usuária cobra isso)

1. **NÃO CORTAR NADA e NÃO MEXER NA COR.** Ela entrega os vídeos já cortados e com cor tratada.
   A duração final é exatamente a do arquivo recebido.
2. **NADA PERTO DO ROSTO OU DA BOCA.** Legendas e combinações ficam no peito (y ≈ 1300–1360);
   cards ficam na parede acima da cabeça (y 272–630) ou ATRÁS da pessoa (camada).
3. **TUDO DENTRO DA GRADE do Instagram** (`assets/grade_instagram.jpg`, em 1080×1920):
   x 88–995, y 262–1459; abaixo de y 1070 a borda direita é x 928 (botões do Reels).
   Rode `scripts/check.py` com a grade desenhada e confira antes de entregar.
4. **Sem emojis.** Nunca.
5. **Efeito sonoro nunca mais alto que a voz.** `SFX_GAIN = 0.55` global em `lib.py`;
   o loudness final deve ficar igual ao original (≈ -14 LUFS — medir com `ebur128`).
6. **Legenda acompanhando a fala em todos os vídeos**, menos onde ela pedir silêncio
   (ex.: reação/expressão da pessoa numa trend) e onde houver combo/tela preta.

## Efeitos sonoros (preferência dela)

| Situação | Som |
|---|---|
| Card / caixinha / pílula / item de lista aparecendo | `click` (ou `pop`) — **ela AMA clique/pop** |
| Cada linha de combinação de fontes surgindo | `click` |
| Texto que aparece letra por letra / caixinha digitada | `key` por caractere (`type_keys()`) — som de teclado |
| Números contando (12 anos, 200 empresas) | `count` |
| Zoom em que ela se aproxima da câmera | `swish` |
| Abertura de tela preta importante | `impact` baixo (0.4) ou `click` |
| Comentário / CTA | `notify` |

**Não usar:** som de "digitação" genérico quando o texto aparece todo de uma vez (use só `click`),
`whoosh`/`riser`/`ding` em sequência de palavras — ela achou "som de suspense". Na dúvida: `click`.

## Tipografia e combinações

- Duas fontes da marca (Julia: **Montserrat** + **Playfair Display**). Montserrat em caixa alta
  pequena com tracking (`M(...)`) + Playfair grande, normal ou itálico (`P(..., it=True)`).
- **Linhas juntas**: `lead=-44` a `-50` nos combos sobre o vídeo (ela reclamou de linhas distantes).
  Centro `cy=1320–1360`. 3 linhas → `cy≈1310–1330`.
- Ganchos (0–3s) merecem combinações mais elegantes/maiores.
- Frase que remete a algo acima/"agora" pode ir NA PAREDE acima da cabeça (`cy≈440`).
- **Cor**: texto vermelho nunca sobre roupa vermelha (fica ilegível) → use branco/itálico.
- Legenda comum: Montserrat SemiBold 52 branca com sombra suave, 2–4 palavras por bloco,
  palavra ainda não falada transparente.

## Telas pretas (BlackCard)

Frase-chave do vídeo em tela preta, linhas surgindo no tempo da fala, destaque em vermelho.
Para "começa antes"-style: animação máquina de escrever →
`(t, runs, {'type': (t_ini, t_fim)})` + `type_keys(t_ini, t_fim, 'texto', 0.5)`.

## Cards e gráficos (cores da marca: azul `BLUE`, vermelho `RED`, branco)

Disponíveis em `lib.py`: `checklist_fn` (vai marcando no tempo da fala), `bars_fn` (gráfico de barras),
`calendar_fn` (calendário com dias circulados), `calculator_img`, `question_box_img` (caixinha estilo
pergunta do Instagram, aceita `nchars` para digitar), `comment_img`, `input_bar_img`, `tax_img`,
`steps_fn` (pílulas / linha do tempo), `tag_list_fn` (lista com etiqueta URGENTE), `stats_fn`
(números contando), `provision_fn`, `bigline_card`.

- **Camada atrás da pessoa** (recorte MODNet em `matte.py`): use `behind=True` (ou `big=True` para
  calendário/ilustração). Ela adorou o calendário atrás da cabeça. Mantenha visível o que importa
  (dia circulado, número). Tamanho: calendário `maxh≈380–430` (ela pediu menores que 540).
- Card com TEXTO para ler atrás da cabeça: reduza (`maxh 255–320`) e, se a cabeça ainda tapar,
  zoom `'top'` 1.1–1.15 para descer a pessoa. Confira no check.
- Tag "JULIA ROQUE // CONTADORA": ela pediu para TIRAR nos cards de número (`tag=False`) e deixar
  os cards compactos (sem espaço sobrando em volta do título).
- Mostre o elemento no MOMENTO em que a pessoa fala dele (ex.: calendário do CTA só em
  "vai me ligar dia 29"), nunca antes.
- Valores de gráfico inventados = avisar a usuária que são ilustrativos.

## Zooms

`Zooms([(t0, t1, escala, foco_y | 'top', tipo)])`: `'punch'` (corte seco, reação/frase forte),
`'smooth'` (entra/sai em 0.3s), `'slow'` (cresce durante o trecho). `'top'` ancora no topo e
DESCE a pessoa (abre espaço para card acima da cabeça).

## Fluxo de trabalho

1. **Baixar do Drive** (pasta com subpastas Vídeo 1..N, `roteiro` (print), referências, PDF da marca):
   listar com o conector do Google Drive (`search_files` com `parentId = '<id>'`) e baixar cada arquivo com
   `curl -L -o src/vN.mov "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`.
   Ler os roteiros (imagens) — "Tela:"/"Texto na tela" indica o que destacar.
2. **Ambiente** (uma vez por máquina): `bash scripts/setup.sh` — instala faster-whisper, onnxruntime
   e as fontes (via npm fontsource, pois o GitHub é bloqueado) em `~/.fonts`.
   Pastas do projeto (definir `EDIT_ROOT` ou rodar a partir dela): `src/ wav/ sfx/ out/`.
3. **Efeitos**: `python3 scripts/sfx.py && python3 scripts/sfx2.py` (o segundo gera click/key/count finais).
4. **Transcrever**: extrair `wav/vN.wav` (mono 16k) e `python3 scripts/transcribe.py medium 1 2 3`
   → `wav/vN.json` (palavras com tempo). Corrigir erros com `fix_words` (ex.: "Digos"→"Divos",
   "desfoto"→"discuto"; checar contas — "um terço" era 1/12).
5. **Mapear o rosto**: tirar 1 quadro por vídeo com grade de y para saber onde ficam cabeça/boca.
6. **Escrever `vN.py`** copiando a estrutura de `exemplos/` (Combo, BlackCard, Sprite/Dynamic,
   Zooms, lista S de SFX, `Subtitles(words, bloqueios)`).
   **Cuidado com `find()`**: sempre passe `after` quando a palavra se repete
   (ex.: "quatro coisas" no gancho × "Quatro," no tópico; "agora" aparece 2 vezes).
7. **Preview** de um trecho: `python3 vN.py 15 18` → `out/preview_vN.mp4`.
8. **Render** completo: `python3 vN.py` (1080×1920, 30fps, H.264 CRF 17, AAC 192k).
9. **Conferir**: `python3 scripts/check.py out/X.mp4 out/c.jpg 1 4.5 9 ...` e OLHAR a imagem:
   grade, rosto livre, textos legíveis, nada cortado pela cabeça.
10. **Entregar** os MP4 e listar o que precisa de confirmação dela (valores ilustrativos,
    correções de transcrição, quem fala cada fala em trends).

## Trend / POV com perguntas em off

Pergunta da voz de fundo → caixinha (`question_box_img`) no topo com **só um clique** ao aparecer;
a reação da pessoa fica SEM legenda (expressão) com zoom lento/punch. Elementos de apoio
(calendário, calculadora) do lado oposto ao que ela segura o celular.
