---
name: planta-para-3d-blender
description: Modelar um imóvel em 3D no Blender a partir de plantas de arquitetura (implantação, pavimento tipo, corte, fachada), com fidelidade verificável — escala aferida por medição, geometria vetorizada da planta por classificação de cor e morfologia, e conferência por sobreposição do contorno extraído de volta no desenho original. Use sempre que o pedido envolver planta baixa, implantação, pavimento tipo, corte, planta de condomínio ou empreendimento, maquete eletrônica, modelo 3D de imóvel, "modelar esse prédio", "fazer a planta em 3D", Blender via MCP para arquitetura, ou quando o usuário mandar imagens de projeto arquitetônico e pedir um 3D. Use também quando o pedido for de fidelidade ("igual à planta", "100% fiel", "do jeito que está no projeto") sobre um modelo já existente.
---

# Planta → 3D fiel no Blender

Modelar por leitura visual da planta não funciona. A tentação é olhar a imagem,
entender o partido e começar a construir — e o resultado erra a implantação, a
ordem dos pavimentos e a contagem de torres, de formas que só aparecem depois de
horas de trabalho. O caminho que funciona é tratar a planta como **fonte de dados
medida**, não como referência visual.

Três compromissos definem essa abordagem:

1. **Nenhuma posição vem de estimativa.** Cada polígono é extraído da planta em
   alta resolução e convertido para metros por uma escala aferida.
2. **Toda afirmação de fidelidade é verificável.** O contorno extraído volta
   sobreposto ao desenho original — dá para ver se corre em cima da borda.
3. **Ler o conjunto inteiro antes de construir.** Ordem dos pavimentos, número de
   torres e limite de laje são decisões que, se erradas, invalidam tudo que vem
   depois.

## Antes de qualquer coisa: os arquivos

Imagem colada no chat não serve — não dá para medir. Peça os arquivos originais em
disco e não comece sem eles. Se o usuário já mandou por chat, vale procurar em
`%TEMP%` e na pasta de Downloads antes de pedir: costumam estar lá.

Peça, nesta ordem de utilidade: **implantações de todos os pavimentos**, **corte**
(resolve as cotas de uma vez), **pavimento tipo**, **fachadas**.

Copie tudo para uma pasta de trabalho do projeto, com `plantas/` dentro.

## Passo 1 — Reconhecer o conjunto

Leia `references/leitura-de-plantas.md` antes de tocar em qualquer script. Ele
cobre os seis erros de leitura que custam reconstrução: ordem dos pavimentos,
pavimento esmaecido, contagem de torres por núcleo de circulação, registro entre
pranchas, rotação do desenho e escolha do elemento de referência da escala.

Confira se as pranchas têm a mesma dimensão em pixels. Se tiverem, provavelmente
estão registradas entre si e um único sistema de coordenadas serve para todas —
isso simplifica tudo o que vem depois.

## Passo 2 — Aferir a escala

Escolha um elemento **normativo e repetido** (vaga de garagem é o melhor caso) e
meça o passo por FFT em três faixas independentes:

```bash
python scripts/afere_escala.py plantas/pilotis.jpg \
  --faixa 300 600 4300 12300 --faixa 750 1000 4300 12300 --faixa 1750 2000 5200 12300 \
  --medida 2.50
```

Se as três faixas concordarem dentro de ~1%, a medida está boa. **Feche com duas
referências independentes** de outra natureza — profundidade de vaga (~5,0 m),
corredor de garagem (6,0–7,0 m), quadra de areia (16 × 8 m nominal). Se não
fecharem, você ancorou no elemento errado; volte e escolha outro.

Registre a escala, a origem e a rotação num `projeto.json` na pasta de trabalho
(veja `scripts/projeto.exemplo.json`). Todo o resto lê esse arquivo.

## Passo 3 — Extrair a laje construída de cada pavimento

```bash
python scripts/lajes.py        # -> lajes.json
python scripts/confere.py      # -> confere_lajes.png
```

**Abra `confere_lajes.png` e olhe.** É aqui que se descobre que a laje do último
pavimento não cobre o braço inteiro do lote, ou que um trecho do desenho era o
nível de baixo em transparência. Não avance com um contorno que não corre em cima
da borda desenhada.

## Passo 4 — Vetorizar as superfícies e as paredes

```bash
python scripts/vetoriza.py     # -> geometria.json      (leva alguns minutos)
python scripts/filtra.py       # -> geometria_filtrada.json
```

`vetoriza.py` separa duas famílias, porque as plantas renderizadas misturam duas
linguagens gráficas:

- **Superfícies** (água, areia, vegetação, madeira, vaga) — manchas de cor,
  detectadas por regras em HSV.
- **Paredes** — linha escura fina sobre fundo de qualquer tom. Limiar de brilho
  global não funciona: perde parede clara e captura piso escuro de academia. O
  *bottom-hat* realça linha fina escura independente do fundo, e o que sobra é
  separado em parede (alongado) e mobiliário (compacto).

`filtra.py` descarta o que caiu fora da laje daquele pavimento — sem isso o modelo
herda piscinas fantasma dos níveis de baixo.

Se uma classe sair vazia ou exagerada, ajuste as regras em `vetoriza.py` e confira
amostrando a cor real da região na planta. Duas armadilhas conhecidas: lâmina
d'água com textura fotográfica de cáustica precisa ser classificada numa cópia
borrada, e vaga cinza-azulada colide com água — separe por saturação, ou desligue
a classe por pavimento no `projeto.json`.

## Passo 5 — Levantar no Blender

```python
import runpy, os
os.environ["PLANTA3D_PASTA"] = r"<pasta de trabalho>"
runpy.run_path(r"<pasta>\scripts\constroi_blender.py", run_name="__main__")
```

O namespace do Blender não persiste entre chamadas do MCP — rodar o arquivo do
disco evita esse problema e deixa o passo reexecutável. As demais armadilhas da
API estão em `references/blender-mcp.md`; vale ler antes de gastar tempo com
viewport, boolean e instanciação.

Cada pavimento vira uma coleção nomeada com a cota, o que permite isolar níveis
para conferir.

## Passo 6 — Conferir pavimento a pavimento

Gere uma vista de topo de cada nível e compare com a prancha correspondente:

```python
bpy.ops.render.opengl(write_still=True)   # respeita o sombreamento sólido, dispensa luz
```

Mostre as vistas ao usuário. Se um nível não bate, o problema está na extração —
volte ao passo 3 ou 4, não corrija na mão no Blender: correção manual quebra a
cadeia entre planta e modelo, e é exatamente isso que torna o resultado não
verificável.

## Materiais e luz

Quando o destino do modelo é render ou vídeo em outra ferramenta (Higgsfield,
por exemplo), luz e textura são feitas lá. Nesse caso não invista nisso aqui: cores
chapadas de viewport bastam para identificar os elementos, e o sombreamento sólido
do Blender já entrega imagens legíveis sem nenhuma luz na cena. Pergunte antes de
assumir o contrário.

## Torres e pavimento tipo

Implantação de embasamento não mostra as torres — elas começam acima. Para modelá-las
é preciso o **pavimento tipo**, medido pelo mesmo processo (passos 2 a 4 valem igual).
Use `scripts/empilha_torre.py` — ele levanta um pavimento e o repete com malha
compartilhada (`novo = obj.copy(); novo.data = obj.data`), o que mantém 27
pavimentos custando a memória de um só. Volumes de alturas diferentes são
declarados em `LOBULOS`, por faixa de X.

Para registrar a torre sobre o embasamento sem depender de olho: calcule a
origem em pixels de modo que o centro da placa caia no centro da laje do último
pavimento do embasamento. Se as duas pegadas baterem dentro de poucos por cento,
isso também **confirma a escala** da prancha do tipo por um caminho independente.

O número de volumes vem da contagem de núcleos de circulação, não de contar
massas numa perspectiva — numa vista oblíqua um volume recuado se esconde atrás
do da frente.

## Quando um dado não existe

Cotas de pavimento sem corte, número de andares sem quadro de áreas: declare a
estimativa explicitamente e siga. "Estimado em 3,00 m nas garagens porque não há
corte" é honesto e corrigível; um número apresentado como medido, não.
