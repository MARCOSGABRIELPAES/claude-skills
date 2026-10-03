# Aula: como criar motion design com Claude (do zero ao MP4)

Baseado no método do curso *"How to build motion design studio with Opus 5.5"* (Movez, set/2026),
reescrito em português e testado de ponta a ponta no filme `exemplo/raio-x/`.

---

## Parte 1 — A ideia que muda tudo

Ferramentas tradicionais (After Effects, Premiere) guardam **keyframes**. Aqui o filme é um **programa**:

```js
window.renderAt = async t => {
  // pinta EXATAMENTE como a tela deve estar no instante t (em segundos)
};
```

Um navegador invisível (Chromium headless) chama `renderAt(0)`, `renderAt(1/60)`, `renderAt(2/60)`...
tira um print de cada um e o ffmpeg junta tudo num MP4. 8 segundos a 60 fps = 480 prints.

Por que isso é poderoso:
- **Determinístico:** o quadro 312 sai igual toda vez. Dá para renderizar só um trecho e emendar.
- **O Claude consegue "ver" o filme:** ele renderiza stills, olha as imagens e se corrige.
- **Custo zero de software:** HTML + CSS + JS + ffmpeg. Sem licença de After Effects.
- **Reaproveitável:** trocou o texto/cor/logo → re-render. Vira template vendável.

> O prompt é 10% do vídeo. Os outros 90% são o **harness**: a biblioteca de movimento, o renderizador,
> as regras e o loop de crítica. É isso que esta skill entrega pronto.

## Parte 2 — Instalação (10 minutos)

```bash
# 1. ferramentas
node -v          # precisa 18+ (recomendo 22)
ffmpeg -version  # Windows: winget install ffmpeg | Mac: brew install ffmpeg
python3 --version

# 2. a skill
git clone https://github.com/MARCOSGABRIELPAES/claude-skills.git
cp -r claude-skills/skills/motion-design-studio ~/.claude/skills/

# 3. rodar o exemplo
cd ~/.claude/skills/motion-design-studio/exemplo/raio-x
npm install
npx playwright install chromium   # só na primeira vez
npm run stills     # 10 quadros-chave em out/stills/
npm run rascunho   # MP4 rápido a 30 fps (~20 s)
npm run render     # MP4 final a 60 fps com motion blur (~1,5 min)
npm run som        # trilha sintetizada
npm run final      # junta, masteriza em -15 LUFS e mede
```

Abra `out/raio-x-final.mp4`. Esse é o resultado que você vai aprender a fazer.

## Parte 3 — Os 5 conceitos de movimento (o que faz parecer profissional)

### 3.1 Molas, não curvas
Amador: o card vai de A até B com `ease-in-out`. Profissional: o card tem **massa** — acelera, passa um
fio do alvo e assenta.

```js
import { mola } from './lib/motion.js';
const s = mola(t - 2.0, 'base');           // 0 → 1 a partir de t = 2,0 s
card.style.transform = `translateY(${(1 - s) * 90}px)`;
```

Escolha o preset pela massa: `seca` (cursor), `ui` (chips), `base` (cards), `texto` (títulos, sem
quique), `pesada` (logo), `elastica` (mascote).

### 3.2 Cortes no meio do movimento
Amador: cena A para, corta, cena B começa parada. Profissional: A **acelera** para fora, o corte
acontece no pico de velocidade, B **já entra correndo** na mesma direção.

```js
const s = costura(t, 2.0);                  // corte em 2,0 s
cenaA.style.transform = `translateX(${-s.sai * 760}px)`;        // sai para a esquerda acelerando
cenaB.style.transform = `translateX(${(1 - s.entra) * 760}px)`; // entra pela direita desacelerando
```

Escolha **uma direção dominante** (no exemplo: esquerda). Mude de direção só com significado — para
cima = conclusão.

### 3.3 Tipografia cinética
Palavras entram uma a uma, na batida, subindo e focando de um leve desfoque:

```html
<div class="titulo" data-sai="2.2">
  <span class="p" data-em=".15">Você</span> <span class="p" data-em=".27">sabe</span>
</div>
```
```js
const titulos = ligaTitulos(document);   // uma vez
titulos(t);                              // dentro do renderAt
```

### 3.4 Um movimento-assinatura
Todo filme bom tem UM gesto que a pessoa lembra. No exemplo: a **linha de scan** desce e revela a
"camada raio-x" dos processos com o % de automação. Tecnicamente são duas camadas idênticas, e o
`clip-path` mostra uma acima da linha e outra abaixo:

```js
xray.style.clipPath   = `inset(0 0 ${1920 - y}px 0)`;  // acima da linha
normal.style.clipPath = `inset(${y}px 0 0 0)`;         // abaixo da linha
```

Para o seu cliente, pergunte: **qual é o verbo do produto?** (revela, responde, organiza, agenda...).
A assinatura é esse verbo virando imagem.

### 3.5 Silêncio antes do clímax
Antes do momento grande, **pare tudo** por 0,2–0,5 s (imagem e som). No exemplo: o scan termina em
4,45 s, tudo segura parado até 5,1 s, e aí "Mapa claro." pousa com um impacto grave.

## Parte 4 — O fluxo de trabalho (o que você pede ao Claude)

Com a skill instalada, no Claude Code:

```
Use a skill motion-design-studio. Quero um reel 9:16 de 10 s para a [Clínica X].
Produto: agendamento por WhatsApp com IA. Público: donos de clínica no Instagram, sem som.
Cores da marca: #0E7C66 e #F4F1EA. Logo em assets/logo.svg.
Referência de estilo: [link ou print]. CTA: "Teste grátis 7 dias".
Me mostre o style_guide e o shotlist antes de codar.
```

O Claude vai seguir 9 passos:

| # | Passo | O que você faz |
|---|---|---|
| 1 | **Brief** — verbo do produto + movimento-assinatura | confirma |
| 2 | **style_guide.md** — paleta, tipo, ritmo, direção | aprova ou ajusta |
| 3 | **shotlist.md** — cada plano na grade de 0,5 s | **aprova antes do código** (mais barato mudar aqui) |
| 4 | **film.html** — o código | — |
| 5 | **Stills + crítica** — ele olha os quadros e dá nota | olha a folha de contato |
| 6 | **Som** — trilha na mesma grade | — |
| 7 | **Render 60 fps** | — |
| 8 | **Master -15 LUFS** | ouve! (ele não ouve) |
| 9 | **Crítica final, tudo 8+** | aprova |

## Parte 5 — O loop de crítica (o segredo da qualidade)

O primeiro render **nunca** é o filme. No exemplo deste repositório, a crítica pegou 3 problemas reais:

1. **Cards invisíveis** — a camada com `clip-path` não tinha tamanho, então recortava tudo.
   Correção: `.camada { position: absolute; inset: 0 }`.
2. **Texto da cena 1 vazando nas cenas 2 e 3** — `visibility: visible` no filho vence o `hidden` do
   pai. Correção: esconder cena com `display: none`.
3. **3 quadros quase vazios logo depois do corte** — os cards só começavam a aparecer no corte; a
   costura ficou sem portador. Correção: a cascata começa 0,08 s **antes** do corte.

E um no áudio: a primeira master saiu em -15,9 LUFS com pico de -1,2 dB (fora do alvo). Correção:
ganho calculado + limitador com oversampling → -15,3 LUFS, pico -1,9 dB.

Nenhum desses dá pra ver lendo o código — só **olhando** os quadros. Por isso sempre peça:
"renderize os stills, monte a folha de contato e tiras nos cortes, dê nota de 1 a 10 e corrija os 3
piores antes do render final".

## Parte 6 — Exercícios (faça nesta ordem)

1. **Troque a cópia** do exemplo para um cliente seu e re-renderize. (Aprende o ciclo.)
2. **Troque a paleta** em `:root` e as fontes. (Aprende o style guide.)
3. **Mude a direção dominante** para cima e ajuste as duas costuras. (Aprende a lei do vetor.)
4. **Adicione um 4º card** e um contador. (Aprende `trilha`/`mola` com dados.)
5. **Crie uma assinatura nova**: um cursor gigante que clica num botão e o clique causa a próxima
   cena. (Aprende movimento causal.)
6. **Do zero**: copie `templates/film.html`, escreva brief + shotlist e faça um filme de 6 s.

## Parte 7 — Como transformar em dinheiro

- **Vinheta/reel de lançamento** para clientes de landing page: entregue o site + um reel de 8–15 s
  com o mesmo visual. Upsell natural.
- **Templates por nicho** (clínica, imobiliária, advocacia): o mesmo `film.html` com dados trocados —
  render em minutos, preço de peça única.
- **Raio-X de IA**: use o filme do exemplo como peça do seu próprio funil.
- **Vídeo de dados**: relatórios mensais animados (números do cliente entram via JSON → `trilha()`).

## Rotas alternativas (quando usar outra coisa)
- **Remotion (React):** séries, templates com muitos dados, quando o time já é React.
- **HyperFrames (HTML + GSAP):** quando você pensa em páginas web e quer o ecossistema de blocos — já
  está neste repositório (`skills/hyperframes*`).
- **Vídeo gerado por IA (Seedance etc.):** movimento orgânico difícil de codar (mãos, pessoas). Combine:
  o modelo gera a filmagem, o código põe por cima a camada de UI, texto e marca.
