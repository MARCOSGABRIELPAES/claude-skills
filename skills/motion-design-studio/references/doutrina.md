# Doutrina de movimento

Como as coisas devem se mover. Cada regra tem a função de `lib/motion.js` que a implementa.

## 1. Massa — molas, não curvas
Uma curva fixa de A até B parece barata. Uma mola acelera, (talvez) passa do alvo e assenta — parece
ter peso. `mola(t - t0, preset)` devolve 0→1:

| Preset | k, d | Para quê | Overshoot |
|---|---|---|---|
| `seca` | 320, 30 | cursor, toggle, borda que lidera | mínimo |
| `ui` | 220, 24 | chips, notificações, contadores | um fio |
| `base` | 170, 26 | cards, containers, câmera | leve |
| `texto` | 150, 26 | tipografia grande | nenhum |
| `pesada` | 90, 20 | logo, palavra gigante pousando | nenhum, lenta |
| `elastica` | 260, 14 | adesivo, mascote | quique visível |

- **Vários alvos, um valor:** barra que vai 18 → 34 → 100 usa `trilha(t, [[t0,18],[t1,34],[t2,100]])`
  — uma mola por mudança, nunca "reiniciar" a animação.
- **Estalo e pausa:** mudança de estado em ~0,07 s e depois parada (`estalo`) lê como decisão;
  esticar por 0,5 s lê como slide.
- **Antecipação e sobreposição:** um pequeno recuo antes do soco; partes chegam em tempos
  diferentes (corpo primeiro, detalhes 2–3 quadros depois).

## 2. Costuras — transições
- **Lei do vetor:** como a cena A sai decide como a B entra — mesmo eixo, mesma direção, velocidade
  casada, e o corte cai **no meio do movimento** dos dois lados. Saída com `in4`, entrada com `out4`,
  mesma distância e duração (`costura(t, corte)`). Parar antes do corte = beat morto.
- **Uma correnteza:** escolha UMA direção dominante para transições comuns. As outras são reservadas
  e significam algo: para cima = revelação/conclusão; avançar em Z = mais fundo na mesma ideia;
  recuar em Z = chegada; explosão = sair de um mundo.
- **Portadores:** o olho segue objetos. A melhor costura passa uma coisa concreta pelo corte na
  mesma posição e velocidade (um cursor, um card que vira o próximo layout, uma palavra). Crossfade
  não tem portador. **No primeiro quadro depois do corte já tem que haver algo visível.**
- **Movimento causal:** clique → amassa → mola → impacto → revelação. O efeito começa no quadro que
  o causou.

## 3. Performance
- **Sem balanço ocioso.** Entre entrada e saída a cena performa (algo novo a cada 2–4 s) ou fica
  perfeitamente parada. Flutuar/respirar em UI é enchimento.
- **Silêncio antes do clímax.** Congele, esvazie ou cale 0,1–0,5 s antes do grande momento. É a
  ferramenta mais forte para fazer um impacto pousar (no som: `--silencio a:b`).
- **Algo sempre viajando.** Câmera empurrando devagar, paralaxe da grade, gradiente derivando. Corte
  seco para plano estático + outro corte seco = slideshow.

## 4. Tipografia
- Palavras entram uma a uma na batida: sobem na mola `texto` e focam a partir de um blur
  (`palavraEntra`); saem acelerando (`palavraSai`) para o corte seguinte pegar a velocidade máxima.
- Cascata: `escalonar(i, .06–.14)`. Nunca todas as palavras de uma vez.
- No máximo 3 momentos de texto gigante por filme. Texto pequeno também tem força.
- Tracking apertado em display: grotesk −0,045 a −0,05em; serifa −0,02 a −0,03em.
- Separe palavras com **espaço real**, nunca com margin.
- Contraste antes de estilo. **Meça** a centralização, não confie no olho.

## 5. Acabamento — o que faz parecer caro
- **60 fps** para motion graphics puro (a 24 fps ou fica parado ou pula). `--sub 2` para blur leve;
  `--scale 2` para texto fino nítido.
- **Motion blur é julgamento:** subquadros (`--sub N`) só leem como blur enquanto as cópias estão
  próximas. Movimento muito rápido → blur real no elemento (CSS `filter: blur`) ou quadros nítidos.
- **Profundidade:** luz vem de algum lugar — sombra de contato, sombra longa e suave sob cards,
  gradiente com direção, vidro (backdrop blur + realce de 1 px). Forma chapada sem sombra = clipart.
- **Cor como família:** um acento só, valores compartilhados, contraste deliberado.
- **Dispositivos (notebook, celular) em 3D real** com three.js, não caixas CSS empilhadas.

## 6. Catálogo de movimentos
| Movimento | O quê | Quando |
|---|---|---|
| Zoom-through | Empurra num elemento até encher o quadro, corta no pico para a próxima cena já avançando | Mais fundo na mesma ideia |
| Zoom inverso | A cena chega de longe e pousa | Chegada, resultado, logo |
| Corte por desfoque | Blur sobe até o corte (~18 px) e desce depois | Troca calma de assunto |
| Cachoeira | Título chega em cascata de palavras/letras | Abertura, end card |
| Empurrão | Grupo desliza lento-rápido-lento (`empurrao`) para novo layout, sem corte | Re-layouts |
| Fenda | A imagem abre a partir de uma linha (~0,3 s) | Cortes no escuro |
| Cursor gigante | Ponteiro ~7% da largura entra, clica, e o clique causa o próximo beat | Filmes de UI |
| Scan/revelação | Uma linha varre e revela a camada "por baixo" (`clip-path`) | Diagnóstico, antes/depois |

## 7. Padrões proibidos
Visual que ninguém escolheu (o do template); título centralizado sobre gradiente e só; tudo entrando
com fade; bordas e rótulos de canto como decoração; glow em UI; explosão genérica de partículas;
texto de UI gigante; `will-change` em algo que a câmera escala (texto borrado); beat morto; balanço
senoidal em UI; a mesma transição em todos os cortes; motion graphics a 24 fps.
