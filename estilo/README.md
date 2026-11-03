# Estilo de edição — Be.Dent (Instagram Reels)

Padrão tirado da edição da própria Ketlen (vídeo 2, "Vídeo editado") e usado em todos os vídeos.

## Corte
- Sem pausas: cortar todo silêncio e respiração entre e dentro das frases (fala "corrida").
- Usar sempre a última tomada certa de cada frase; tirar erros, repetições e falas de bastidor.
- Zoom em todo corte, alternando zoom in (efeito `swish`) e zoom out (`swish_rev`).

## Cor
- `cor_bedent.cube`: LUT tirado da edição dela (filtros do CapCut). Aplicar no quadro inteiro,
  com vinheta leve (`vignette=angle=PI/4.5` no ffmpeg).

## Textos (sempre dentro da margem do Instagram: x 88–995, y 262–1459 em 1080x1920)
| Elemento | Fonte | Cor | Onde |
|---|---|---|---|
| Legenda que acompanha a fala (1 palavra por vez) | Poppins Bold, ~44 px | branco | altura das mãos (y ≈ 1195) |
| Título (monta palavra por palavra, com `ref_click`) | Inter SemiBold ~88 px, letras bem juntas; 2ª linha na mesma fonte, linhas coladas | branco | centralizado na altura do peito (y ≈ 930), nunca no rosto; some ~0,5 s depois da palavra |
| Destaque "amarelinho" (escreve na tela, com `chalk`) | La Belle Aurore com traço engrossado | amarelo-creme `#F1E092` | altura das mãos; é escrita **enquanto ela fala a palavra** e some logo depois (~0,25 s) |

A fonte original do destaque é a **MrSmith** do CapCut, que é paga e não está disponível para download aqui.
A La Belle Aurore é a gratuita mais parecida. Se o arquivo .ttf/.otf da MrSmith for colocado no Drive,
ela passa a ser usada no lugar.

## Efeitos sonoros (pedido da Ketlen)
- Legenda branca de baixo: **sem** efeito sonoro.
- Título / palavra importante: zoom rápido no rosto + **`ref_click.wav`** (o clique tirado da edição dela).
  O título fica **no peito**, sem cobrir o rosto, e a legenda de baixo some enquanto ele aparece.
- Letra amarela: às vezes o som de escrita (`chalk.wav`), baixinho.

## Final
- Só fechar a tela até o preto com **`ref_close.wav`** (som tirado da edição dela). **Sem logo.**

## Exportação
- 4K (2160x3840), 30 fps, HEVC (`hvc1`), ~17 Mbps, áudio AAC 256k, volume −14 LUFS
  (mesmo formato da gravação do iPhone 14 Pro).

As fontes desta pasta são do Google Fonts, sob a SIL Open Font License (arquivos `OFL-*.txt`).
