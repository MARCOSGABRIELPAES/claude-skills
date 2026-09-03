# planta-para-3d-blender

Skill do [Claude Code](https://claude.com/claude-code) para modelar um imóvel em 3D
no Blender **a partir das plantas de arquitetura**, com fidelidade verificável.

O problema que ela resolve: modelar olhando a planta não funciona. A tentação é
entender o partido pela imagem e começar a construir — e o resultado erra a
implantação, a ordem dos pavimentos e a contagem de volumes, de formas que só
aparecem depois de horas de trabalho. Aqui a planta é tratada como **fonte de
dados medida**, não como referência visual.

## Os três compromissos

1. **Nenhuma posição vem de estimativa.** Cada polígono é extraído da planta em
   alta resolução e convertido para metros por uma escala aferida.
2. **Toda afirmação de fidelidade é verificável.** O contorno extraído volta
   sobreposto ao desenho original — dá para ver se corre em cima da borda.
3. **Ler o conjunto antes de construir.** Ordem dos pavimentos, número de volumes
   e limite de laje são decisões que, se erradas, invalidam tudo que vem depois.

## Pipeline

| Script | O que faz |
|---|---|
| `afere_escala.py` | Mede o passo de um elemento normativo repetido (vaga, degrau) por FFT em faixas independentes → px/m |
| `lajes.py` | Contorno da laje **construída** de cada pavimento, separando-a do pavimento inferior esmaecido |
| `confere.py` | Sobrepõe o contorno extraído na planta original — o passo que torna "está fiel" verificável |
| `vetoriza.py` | Superfícies por regra em HSV; paredes por *bottom-hat* (linha fina) ou limiar de escuro (poché sólido) |
| `filtra.py` | Recorta os elementos pela laje do próprio pavimento |
| `constroi_blender.py` | Levanta o modelo dentro do Blender (via MCP) |
| `empilha_torre.py` | Empilha o pavimento tipo com malha compartilhada, com alturas por volume |

## Referências

- `references/leitura-de-plantas.md` — os erros de leitura que custam reconstrução:
  ordem dos pavimentos, pavimento esmaecido, contagem de volumes por núcleo de
  circulação, registro entre pranchas, escolha da âncora de escala, as duas
  linguagens gráficas de parede, e como saber se um render é elevação ortográfica
  antes de contar pavimentos nele.
- `references/blender-mcp.md` — armadilhas da API que custam tempo: namespace que
  não persiste entre chamadas, viewport, boolean, instanciação em massa.

## Requisitos

Python com `numpy`, `scipy`, `scikit-image`, `Pillow`, `matplotlib`.
Blender 4.4+ acessível por um MCP que exponha execução de código Python.

## Instalação

Copie a pasta para `~/.claude/skills/`.

## Licença

MIT
