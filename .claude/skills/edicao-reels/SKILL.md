---
name: edicao-reels
description: Edita vídeos de clientes no padrão de Reels da Ketlen — cortes secos sem pausas, legenda acompanhando a fala com ênfase nas frases-chave, título-gancho nos 3 primeiros segundos, zoom in/out com efeito sonoro e exportação pronta para o Instagram. Use sempre que a Ketlen pedir para editar vídeo, editar reels, cortar vídeo, legendar vídeo ou mandar material bruto de uma cliente.
---

# Edição de Reels — padrão Ketlen

Toda edição segue o **padrão fixo** abaixo. O que muda por cliente (fontes, cores,
título, CTA, preferências) fica na ficha `clientes/<cliente>.md`. Leia a ficha antes
de começar; se a cliente não tiver ficha, crie uma a partir de `clientes/_modelo.md`
perguntando só o que falta.

## Padrão fixo

### Formato
- Sempre Reels: vertical 9:16.
- Duração livre — normalmente de 90 s a 3 min. Nunca cortar conteúdo só para encurtar.
- Material de entrada: gravado em 4K, 30 fps, com microfone.

### Cortes
- Tirar **todas** as pausas, respirações e momentos em que a pessoa fica parada sem falar.
- Corte seco (jump cut), sem transição.
- Se a Ketlen avisar que o vídeo já veio cortado, pular esta etapa.

### Zona segura do Instagram (obrigatório)
- Todo texto/elemento fica **dentro da caixa segura**: em 1080x1920, x de 88 a 992 e y de 261 a 1461
  (~8% de cada lado, ~14% em cima, ~24% embaixo). Fora disso o Reels corta e perde credibilidade.
- Conferir quadros com a caixa desenhada (`drawbox=x=88:y=261:w=904:h=1200`) antes de entregar.

### Onde os textos podem ficar (nunca em cima do rosto)
- Só **duas posições**: no **espaço vazio de cima** (acima da cabeça, onde também entram as
  colagens/imagens) ou na **altura do peito**. Sempre deixar o rosto livre.
- Título, palavras grandes e colagens: em cima. Legenda corrida e caixas de ênfase: no peito.
- Se a pessoa subir no quadro (se inclinar, zoom forte) e o cabelo/rosto encostar no texto de
  cima, levar aquela ênfase para a altura do peito no lugar da legenda.
- **Variação (cena com mesa carregada):** legenda corrida branca vai **acima da cabeça** e só as
  ênfases (caixas, palavras diferentes) ficam no peito. Quando a cabeça sobe (zoom/close), a
  legenda desce automaticamente para abaixo do peito: `scripts/cabeca.py` mede o topo da cabeça
  quadro a quadro numa prévia (detector de rosto MediaPipe; precisa de `libegl1` e do modelo
  `blaze_face_short_range.tflite`) e o build escolhe a posição por frase.
- Zoom ancorado no alto do quadro (`y=(ih-ih/zoom)*0.22`): assim a cabeça desce ao aproximar
  e o espaço de cima continua livre para os textos.

### Legenda
- Acompanha a fala, sincronizada palavra a palavra / trecho a trecho (transcrição com
  timestamps por palavra).
- Texto corrido na fonte **base** da cliente, letras juntinhas (espaçamento negativo), longe do rosto.
  Atenção: o libass ignora o `Spacing` do estilo — aplicar o espaçamento com a tag `\fsp` em cada linha.
- Uma legenda/caixa nunca aparece por cima da outra: cada uma termina quando a próxima começa.
- Frases de extrema importância ganham **ênfase**: fonte diferente (fonte de destaque
  da cliente), maior e mais chamativa. Marcar poucas por vídeo para não perder o efeito.
- Antes de renderizar, listar as frases escolhidas para ênfase para a Ketlen aprovar.
- Revisar a transcrição (nomes, termos técnicos da área da cliente).

### Título-gancho
- Título atrativo logo no início, visível nos 3 primeiros segundos, para prender quem está rolando o feed.
- Curto e direto sobre o tema (ex.: fonoaudióloga falando do teste da orelhinha → "O TESTE DO OUVIDO").
- Sugerir 2–3 opções de título para a Ketlen escolher.

### Zoom e movimento
- Zoom nas frases importantes.
- Zoom in / zoom out marcados (vai bem para frente, depois volta), feito com keyframes —
  movimento suave, não estático.
- Também usar o "punch" repentino: a pessoa está falando e de repente o enquadramento avança.
- Como o material é 4K e a saída é 1080x1920, o zoom é feito por recorte (crop) do 4K,
  então não perde qualidade até ~2x.

### Áudio
- **Efeito sonoro em todo zoom/movimento marcado**. É o recurso mais usado:
  **swish** nos zooms e no título, **clique** quando entra caixa de ênfase.
  Usar os arquivos de SFX da Ketlen quando houver; senão, `scripts/make_sfx.py` gera substitutos.
- O encerramento (logo/card final) só entra depois que a pessoa termina a última palavra.
- Música de fundo: quase nunca. Só quando a Ketlen mandar a música; aí fica bem baixa sob a voz.
- **Não** aplicar redução de ruído (áudio vem de microfone).
- **Sincronia boca × voz:** o microfone sem fio pode chegar alguns quadros atrasado. Antes de
  exportar, conferir com um evento visível com som (tampa fechando, palma, objeto batendo):
  achar o quadro do impacto e o pico do som. Se a voz vier depois, adiantar o áudio
  (`atrim=AV:...`) e deslocar legendas/ênfases/efeitos pelo mesmo valor. No vídeo do aparelho
  auditivo foram 100 ms (3 quadros).

### Cor
- **Não** mexer em cor/filtro. A Ketlen faz isso.

### Exportação (Instagram Reels)
- 1080x1920, 30 fps, H.264 (High), `yuv420p`, `-movflags +faststart`.
- Prévias: CRF 21, preset medium (rápidas para revisar).
- Final aprovado: CRF 17, preset slow (~9–10 Mbps), áudio AAC 48 kHz 192 kbps.
- Redução de 4K para 1080 com scaler `lanczos`.
- Nome do arquivo: `<cliente>_<tema>_<AAAA-MM-DD>.mp4`.

## Referência pronta
- Primeiro vídeo aprovado: `clientes/kathileenn-bahia/2026-10-bera/build.py` — monta legenda (ASS),
  zooms (zoompan), efeitos sonoros e card final num comando só. Copiar como ponto de partida para
  o próximo vídeo e trocar transcrição, título, ênfases e zooms.

## Fluxo de trabalho

1. Ler a ficha da cliente e conferir se fontes, SFX e (se houver) música estão disponíveis.
2. Cortar pausas (se ainda não foi feito).
3. Transcrever com timestamps por palavra e revisar o texto.
4. Propor à Ketlen: opções de título + frases de ênfase + pontos de zoom com SFX.
5. Depois da aprovação, montar legenda (ASS), zooms, SFX e título; renderizar.
6. Mandar uma prévia e ajustar o que ela pedir.
7. Exportar a versão final e anotar na ficha da cliente qualquer preferência nova que surgir.
