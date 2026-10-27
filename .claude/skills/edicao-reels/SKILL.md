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

### Legenda
- Acompanha a fala, sincronizada palavra a palavra / trecho a trecho (transcrição com
  timestamps por palavra).
- Texto corrido na fonte **base** da cliente.
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
- **Efeito sonoro em todo zoom/movimento marcado** (whoosh, pop, impacto…). É o recurso
  mais usado — usar os arquivos de SFX da pasta da cliente/Ketlen.
- Música de fundo: quase nunca. Só quando a Ketlen mandar a música; aí fica bem baixa sob a voz.
- **Não** aplicar redução de ruído (áudio vem de microfone).

### Cor
- **Não** mexer em cor/filtro. A Ketlen faz isso.

### Exportação (Instagram Reels)
- 1080x1920, 30 fps, H.264 (High), `yuv420p`, `-movflags +faststart`.
- Vídeo com qualidade alta (CRF ~18 / ~15–20 Mbps), áudio AAC 48 kHz 192 kbps.
- Redução de 4K para 1080 com scaler `lanczos`.
- Nome do arquivo: `<cliente>_<tema>_<AAAA-MM-DD>.mp4`.

## Fluxo de trabalho

1. Ler a ficha da cliente e conferir se fontes, SFX e (se houver) música estão disponíveis.
2. Cortar pausas (se ainda não foi feito).
3. Transcrever com timestamps por palavra e revisar o texto.
4. Propor à Ketlen: opções de título + frases de ênfase + pontos de zoom com SFX.
5. Depois da aprovação, montar legenda (ASS), zooms, SFX e título; renderizar.
6. Mandar uma prévia e ajustar o que ela pedir.
7. Exportar a versão final e anotar na ficha da cliente qualquer preferência nova que surgir.
