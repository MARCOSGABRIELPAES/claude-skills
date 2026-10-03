---
name: motion-design-studio
description: Estúdio de motion design em código, pela rota "seek(t)" — o filme é uma página HTML com window.renderAt(t) que pinta o quadro exato de qualquer instante; Chromium headless captura quadro a quadro e o ffmpeg codifica. Zero framework: um HTML, molas em forma fechada, costuras com velocidade casada, tipografia cinética, trilha sintetizada na mesma linha do tempo, master em -15 LUFS e um loop de crítica que só entrega com nota 8+. Use quando pedirem motion design, motion graphics, vídeo promocional, reel/TikTok/Shorts animado, explainer, vinheta, end card, "vídeo de lançamento", "animação para o anúncio", ou quando quiserem criar/editar/re-renderizar um filme feito com esta skill. Use também quando o usuário pedir explicitamente a rota sem framework (seek/renderAt + Playwright + ffmpeg); se ele pedir HyperFrames ou Remotion, use essas skills.
---

# Motion Design Studio

Um filme aqui é um **programa**: `film.html` expõe `async window.renderAt(t)`, que pinta o quadro exato
do instante `t`. O `scripts/render.mjs` abre a página no Chromium headless, chama `renderAt` para cada
quadro (60 por segundo), tira o screenshot e manda para o ffmpeg. Como cada quadro é função pura do
tempo, qualquer correção é "edita + re-renderiza aquele trecho", e você pode **olhar** qualquer quadro.
**Olhar é o método**: o primeiro render nunca é o filme.

O prompt é 10% do resultado; os outros 90% são este *harness*: brief → visual → shotlist → código →
stills → crítica → som → render → master → crítica de novo.

Arquivos da skill (`SKILL=~/.claude/skills/motion-design-studio`):
- `lib/motion.js` — molas, trilhas de valor, costuras, tipografia cinética, PRNG, área segura
- `scripts/render.mjs` — stills e vídeo; `--sub` dá motion blur real; `--scale 2` desenha em 2x
- `scripts/trilha.py` — trilha sintetizada na grade de batidas (só biblioteca padrão do Python)
- `scripts/mux.sh` — junta vídeo + trilha, master em -15 LUFS / pico < -1.5 dB, e mede o entregue
- `templates/film.html` — esqueleto neutro de filme
- `references/brief.md` — o brief de diretor (esqueleto) e o shotlist. Leia no passo 1–3
- `references/doutrina.md` — como as coisas se movem. Leia antes de compor
- `references/critica.md` — o loop de crítica e as 10 notas. Leia antes de julgar um render
- `exemplo/raio-x/` — filme completo de 8 s, para copiar a estrutura
- `TUTORIAL.md` — a aula passo a passo para humanos

## Requisitos
Node 18+ (22 recomendado), ffmpeg/ffprobe, Python 3, e na pasta do filme
`npm i playwright-core @fontsource-variable/inter` (ou as fontes do guia). Chromium: o do Playwright
(`npx playwright install chromium`) ou `CHROME_PATH=/caminho/do/chrome`.

## Estrutura de um filme
```
<filme>/
  brief.md          conceito, público, verbo do produto, movimento-assinatura      (passo 1)
  style_guide.md    paleta em hex, tipografia, ritmo, direção dominante, som       (passo 2)
  shotlist.md       cada plano na grade de batidas, com cópia, movimento e som     (passo 3)
  assets/           logo, cores, fontes, prints reais da UI do produto
  lib/motion.js     copiado da skill (o filme é autocontido)
  film.html         o filme                                                        (passo 4)
  package.json      scripts: stills, rascunho, render, som, final
  out/              stills/, rascunho.mp4, video.mp4, trilha.wav, <final>.mp4, review_log.md
```

## Pipeline
1. **Brief** (`references/brief.md`). Ache o *verbo* do produto (o que ele FAZ, não o que ele É) e o
   **movimento-assinatura** que mostra esse verbo — no exemplo, a linha de scan que revela a camada
   raio-x. Confirme entregáveis (duração, formato 9:16/16:9/1:1, quantos filmes) e o idioma da cópia.
   Se puder ser lido de dois jeitos, pergunte.
2. **Visual → `style_guide.md`.** Com referência (vídeo, frame, conta, estilo): extraia quadros
   (`ffmpeg -i ref.mp4 -vf fps=2 refs/%03d.png`), estude e escreva a **gramática**: paleta em hex,
   tipografia, duração dos planos, transições, câmera, textura. Pegue a gramática, **nunca o conteúdo**
   (logo, personagem, texto). Sem referência, raciocine o visual a partir do público e escreva o porquê.
3. **Shotlist → `shotlist.md`** na grade (120 BPM = 0,5 s por batida): tempo, imagem, cópia,
   movimento, transição, som. Com o usuário presente, mostre guia + shotlist e peça OK **antes** do
   código — rejeição muda o shotlist, não o código.
4. **Compor `film.html`** a partir de `templates/film.html` + `lib/motion.js`, seguindo a doutrina:
   molas em vez de curvas, uma direção dominante, costuras no meio do movimento, algo sempre viajando,
   profundidade e luz, texto na área segura centrado em x = 540.
5. **Stills primeiro.** `node $SKILL/scripts/render.mjs --root . --stills 0.6,1.2,…` em cada batida
   importante; monte a folha de contato e rode a crítica (`references/critica.md`). Depois um
   rascunho rápido (`--fps 30 --jpeg`) e **tiras de quadros em volta de cada corte**. Registre notas e
   os 3 piores problemas em `out/review_log.md`; corrija; repita.
6. **Som.** `python3 $SKILL/scripts/trilha.py --bpm 120 --dur <s> --hits <contatos> --whoosh <cortes>
   --silencio <a:b>` — impactos nos quadros de contato (antecipados 0,03 s), sopros terminando nos
   cortes, vácuo antes do clímax. Trilha licenciada substitui quando o projeto pedir.
7. **Render final.** Motion graphics puro: `--fps 60 --sub 2` (e `--scale 2` quando houver texto fino
   ou linhas de 1 px). Filme sobre vídeo gerado: siga o fps da filmagem (24) com `--sub 4`.
8. **Master.** `bash $SKILL/scripts/mux.sh out/video.mp4 out/trilha.wav out/<nome>.mp4` — ele mede o
   arquivo entregue e falha se ficou fora de -15 ± 1 LUFS ou com pico acima de -1,5 dB.
9. **Crítica do final** e entrega só com **todas as notas 8+**.

## Inegociáveis
- **Função pura do tempo.** Nada de `Math.random` (use `rng`/`hash`), `setTimeout`, transições CSS,
  animações CSS ou estado entre quadros. `renderAt(t)` precisa dar o mesmo quadro sempre.
- **Esconder cena = `display: none`**, nunca `visibility` (um filho com `visibility: visible` vaza).
- **Camadas recortadas (`clip-path`) precisam de tamanho** (`position: absolute; inset: 0`).
- **Fontes carregadas antes de `window.ready = true`** (`document.fonts.load(...)`).
- **Molas em tudo que se move** (presets em `MOLA`); UI pode passar um fio do alvo, texto nunca.
- **Um movimento-assinatura por filme.** O resto serve a ele.
- **Área segura 9:16:** texto entre y 250 e 1440; na faixa dos botões (y 880–1600) entre x 190 e 890.
- **UI real, tamanho real.** Interface do produto vem de print ou reconstrução fiel, nunca inventada.
  Números ilustrativos são ditos como ilustrativos.
- **Olhe antes de entregar.** Folha de contato, tiras nos cortes, versão tamanho-celular.
- **Entrega honesta.** Diga o que foi medido (LUFS, pico, quadros) e o que não foi (você não ouviu).

## Entrega
Nesta ordem: onde está o arquivo e as specs (resolução, fps, duração, LUFS); o que mudou em relação ao
shotlist; o que o usuário precisa conferir no olho/ouvido; onde ficam fonte, guia e comandos de rebuild.

## Créditos
Método aprendido no curso **"How to build motion design studio with Opus 5.5 (Full-course)"** de Movez
(@0xMovez), set/2026 — https://x.com/0xMovez/status/2104216919033192746 — e na implementação aberta
`witcharon/claude-reel-skills` (MIT), que credita o mesmo curso. Código e texto desta skill são
próprios, escritos em português para este repositório.
