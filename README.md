# Claude Skills

Coleção de *skills* do [Claude Code](https://claude.com/claude-code) que uso no dia a dia —
produção de vídeo, direção de anúncios, construção de sites, modelagem 3D a partir de plantas
de arquitetura e aquisição paga (Google Ads + SEO).

Uma skill é uma pasta com um `SKILL.md` (roteador + regras) e, quando o assunto é grande,
arquivos de referência carregados sob demanda. O Claude lê a descrição do `SKILL.md` para
decidir sozinho quando a skill se aplica.

## Instalação

Clone e copie para a pasta de skills do Claude Code:

```bash
git clone https://github.com/MARCOSGABRIELPAES/claude-skills.git
cp -r claude-skills/skills/* ~/.claude/skills/
```

No Windows, a pasta é `C:\Users\<usuário>\.claude\skills\`.
Reinicie o Claude Code e as skills aparecem na lista de skills disponíveis.

## As skills

### Autoria própria

| Skill | O que faz |
|---|---|
| [`google-ads-seo-growth`](skills/google-ads-seo-growth) | Estrategista de aquisição para o mercado brasileiro: diagnóstico de conta, plano de medição (GA4/GTM/conversões offline), estrutura de campanhas, mineração de negativas, SEO técnico e local, prospecção de ICP, precificação em BRL e a camada de automação via MCP do Google Ads. |
| [`one-page-site-builder`](skills/one-page-site-builder) | Site de uma página completo em uma tacada: referências de design (Awwwards, Dribbble, Behance), imagens fotorrealistas geradas por IA, CSS mobile-first, calculadora interativa quando cabe, e deploy na Vercel. |
| [`flight-scroll-animation`](skills/flight-scroll-animation) | Hero de vídeo com scrub por rolagem — a posição do vídeo segue o scroll, criando um voo de câmera pelo espaço. Decide o comportamento no mobile antes de construir e traz a receita de ffmpeg para o loop ping-pong. |
| [`motion-design-studio`](skills/motion-design-studio) | Estúdio de motion design em código pela rota `seek(t)`: o filme é um HTML com `renderAt(t)`, renderizado quadro a quadro no Chromium headless + ffmpeg a 60 fps, com molas, costuras de velocidade casada, trilha sintetizada, master em -15 LUFS e loop de crítica 8+. Traz [tutorial](skills/motion-design-studio/TUTORIAL.md) e um filme de exemplo. |
| [`planta-para-3d-blender`](skills/planta-para-3d-blender) | Modela um imóvel em 3D no Blender a partir das plantas de arquitetura, com fidelidade verificável: escala aferida por medição, geometria vetorizada por classificação de cor e conferência por sobreposição do contorno no desenho original. |

### Direção de publicidade

| Skill | O que faz |
|---|---|
| [`ad-director`](skills/ad-director) | Transforma a descrição de um anúncio em beat sheet timecodado e depois em um prompt de vídeo pronto para gerar, shot a shot, sobre uma espinha travada de 17 campos. |
| [`ad-assets`](skills/ad-assets) | Diretor de prompts de imagem: trava o rosto do personagem, monta o figurino, gera a folha de personagem, a placa de cena e a leitura do produto — nessa ordem. |

### Cadeia HyperFrames (vídeo a partir de HTML)

| Skill | O que faz |
|---|---|
| [`hyperframes`](skills/hyperframes) | Porta de entrada obrigatória para qualquer pedido de vídeo, animação ou motion graphic. |
| [`hyperframes-core`](skills/hyperframes-core) | O contrato de composição: estrutura, atributos `data-*` de timing, tracks, subcomposições, regras de render determinístico. |
| [`hyperframes-animation`](skills/hyperframes-animation) | Regras atômicas de movimento, blueprints de cena, transições e os sete adaptadores de runtime (GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU). |
| [`hyperframes-keyframes`](skills/hyperframes-keyframes) | Punch-in, zoom, Ken Burns, movimentos de câmera e keyframes 2D/3D seguros para seek. |
| [`hyperframes-creative`](skills/hyperframes-creative) | Direção criativa não-animada: paleta, tipografia, narração, planejamento de beats, marca e estilo. |
| [`hyperframes-audio`](skills/hyperframes-audio) | Mixagem do áudio já posicionado: fades, crossfade, ducking, efeitos, envelopes de automação e barramentos. |
| [`hyperframes-cli`](skills/hyperframes-cli) | O loop de desenvolvimento da CLI: init, add, check, preview, render, publish, cloud, Lambda, doctor. |
| [`hyperframes-registry`](skills/hyperframes-registry) | Instala e conecta blocos e componentes do registry na composição. |
| [`general-video`](skills/general-video) | Composição livre quando nenhum workflow específico serve: peças multi-cena, reels de marca, montagens, cartelas estáticas. |
| [`media-use`](skills/media-use) | Resolve toda necessidade de mídia — BGM, SFX, imagem, ícone, logo, voz, LUT — em arquivo local congelado, gerando por IA quando o catálogo não tem. |

## Origem e crédito

As skills de **autoria própria** foram escritas por mim. As de **direção de publicidade** e a
**cadeia HyperFrames** vieram instaladas com o toolchain do HyperFrames e estão aqui como parte
do meu ambiente de trabalho — o crédito de autoria é dos seus criadores originais.

## Licença

O conteúdo de autoria própria é publicado como referência. Para as skills de terceiros listadas
acima, valem os termos dos seus autores originais.
