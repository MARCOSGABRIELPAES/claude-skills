---
name: one-page-site-builder
description: Build a complete, production-quality single-page marketing website in one shot — a landing page, "coming soon" page, product/service/rental page, or portfolio page — including AI-generated photoreal imagery (via a Higgsfield-style generate_image/generate_video MCP), mobile-first responsive CSS, a working interactive calculator (booking, pricing, quote) when relevant, and live deployment to Vercel. Use this whenever the user asks to "build a site", "criar um site", "landing page", "one page website", wants a design brief turned into a real deployed page, wants AI-generated hero/product photos for a business, or mentions deploying to Vercel for a static site. Also use it any time the deliverable is described as "self-contained", "single page", or "one-shot — no placeholders". Sempre começa colhendo referências reais em Awwwards, Dribbble, Behance, Pinterest e MotionSites AI antes de desenhar.
---

# One-page site builder

Turns a design brief (palette, type, copy, section list) into a real, deployed,
single-page site with real AI-generated imagery — not a wireframe, not
placeholder Lorem Ipsum, not a "here's the code, you run it" hand-off. The
target is: the user gets a live URL by the end of the conversation.

This skill was distilled from building "Vesper" / "MG Webdesigner", a lakeside
cabin rental page with 10 generated stills, a scroll-scrubbed hero video, and a
live booking-price calculator, deployed to Vercel. Read
`references/asset-generation.md` and `references/page-patterns.md` before
generating anything — they hold the gotchas that actually cost time.

If the brief includes a scroll-driven "walkthrough" or "flight" hero video
(camera glides through a space as the user scrolls), that's a distinct
technique — load the `flight-scroll-animation` skill for it instead of
re-deriving it here.

This project also has a stack of specialized design skills/plugins
installed. Don't re-derive judgment calls they already make — load the
relevant one at the point in the workflow below where it's called out:
`design-taste-frontend` (art direction), `image-to-code` (reference-image
briefs), `web-design-guidelines` and `visual-critique` (pre-deploy QA),
`interaction-design`/`ui-design`/`design-systems` (component and motion
detail), and `playwright` (automated verification fallback). A few more —
`design-research`, `ux-strategy`, `design-ops`, `designer-toolkit` — cover
work that goes beyond a single page; see "Beyond a single page" at the end.

## Workflow

### 0. SEMPRE colher referências reais antes de desenhar (obrigatório)

Nunca desenhe de memória. Antes do passo 1, abra os cinco sites abaixo com
as ferramentas de navegador e olhe de verdade o que está sendo premiado
hoje no nicho do cliente — este passo não é opcional e não pode ser pulado
"porque já sei como é":

- **Awwwards** — `awwwards.com/websites/<categoria>/` (real-estate,
  architecture, fashion, restaurants…). É a fonte mais confiável de padrão
  de interação e tipografia premiada.
- **Dribbble** — `dribbble.com/search/<nicho>-website`. Bom para paleta,
  cartões, chips de UI e composição de hero.
- **Behance** — `behance.net/search/projects/<nicho> website`. Bom para
  projetos completos e sistemas de marca.
- **Pinterest** — busque `<nicho> website design`. Bom para direção de
  arte editorial e combinações tipográficas.
- **MotionSites AI** — `motionsites.ai`, filtrando pela categoria do nicho
  (Hero, Landing Page, SaaS, Agency, Portfolio, 3D Website, Fintech,
  Ecommerce, Fashion, Travel, Wellness…) e pela seção **Backgrounds**. É
  diferente das outras quatro: em vez de trabalho de agência, mostra sites
  feitos com IA — então é a melhor fonte de **vocabulário de movimento**
  (hero 3D, fundo animado, vidro líquido, scroll com câmera, cursor e
  transições) e a régua mais honesta do que dá para entregar de fato.
  O texto do prompt fica atrás de "Copy full prompt"/"Go Unlimited" (pago):
  conte apenas com as prévias visuais, e nunca copie um prompt inteiro —
  extraia o padrão, igual às outras fontes.

Como fazer, na prática:
1. `navigate` para cada busca, `get_page_text` para pegar os nomes dos
   projetos e 3–4 `screenshot` rolando a página. Recuse cookies pela opção
   mais restritiva ("Reject All"); nunca aceite "Accept All".
2. Anote os **padrões que se repetem em pelo menos três projetos** — esses
   são o vocabulário atual do nicho, não gosto pessoal de um designer.
   No projeto ÁTRIO (imobiliário, ago/2026) os recorrentes foram: wordmark
   gigante em `mix-blend-mode` sobre a arquitetura, hero cinematográfico
   escuro, chips de vidro fosco com números, índice em lista com a foto
   flutuando no hover, cursor customizado, marquee e grão de filme.
3. Diga ao usuário, em uma linha, quais padrões você extraiu e de onde,
   antes de começar a construir. É isso que separa "site genérico de IA"
   de "site que parece premiado".

Se as buscas voltarem vazias ou o site pedir login, diga isso claramente e
siga com o que conseguiu ver — não invente ter olhado.

### 1. Extract the design system from the brief

Before writing any CSS, load `design-taste-frontend` — it reads the brief,
infers the design direction from vibe words and audience signals, and sets
the dials (variance, motion, density) that steer everything else in this
step. It also maps to a real design system (Fluent, Carbon, GOV.UK, etc.)
when one fits, instead of reinventing one badly. If the brief is a
reference image, screenshot, or an existing site to redesign rather than
text, load `image-to-code` first instead — it infers the palette/type
scale/spacing/radius from the reference and maps it to token tiers, which
is more reliable than eyeballing a screenshot.

Then pull out: hex color tokens, the display/body font pairing (set up as a
Google Fonts `<link>` + CSS custom properties), spacing and radius
conventions (e.g. "20px rounded cards"), and any explicit "don't"s ("no
gradients", "no emoji", "no stock-photo clichés"). Put every token in
`:root` as a CSS custom property — the whole page should reference
`var(--teal-900)` etc., never a raw hex, so a later "make it warmer" request
is a one-line change. For naming conventions and scale decisions beyond
what the brief specifies, `design-systems` and `ui-design` carry the
reference patterns (spacing/grid systems, type scales, dark-mode specs).

### 2. Generate real imagery — don't skip to placeholders, and don't default to MCP

**Ask before generating anything through the MCP.** MCP generation always
bills the account's normal credits, even for models the user has an active
"Unlimited" pass for on the provider's own website — Unlimited access is
honored on the website only, never through MCP (confirmed directly on a
real Higgsfield account: GPT Image was on a paid 365-day Unlimited pass and
MCP still billed standard credits for every call). So before spending
anything, ask the user whether the model you need is one they have
Unlimited on — if so, the cheaper path is them generating it manually on
the website (or you doing it through their logged-in browser session, if
you have one) and handing you the finished files, not you calling
`generate_image`/`generate_video` directly. Reserve direct MCP calls for
what actually needs it: models outside their Unlimited coverage, and
anything that genuinely requires scripting — a multi-shot consistency
chain, programmatic reference-passing, batch generation — which can't be
reproduced by hand on the website anyway. Full detail, including how to
check what's covered, in `references/asset-generation.md`.

Once you and the user have settled *where* generation happens, read
`references/asset-generation.md` in full before calling any generation
tool. Short version for the MCP path: resolve named models via
`models_explore` first, check `balance` and preflight cost on anything
you're about to run 10x, generate one anchor image and feed its job_id as a
reference into every other prompt for visual consistency, and expect a low
concurrency ceiling — batch in pairs, not all at once.

Download every result locally into `assets/images/` and `assets/video/` and
re-encode for the web with ffmpeg (recipe in the reference doc). Never ship
the raw multi-MB PNG/HEVC generation output directly.

### 3. Build the page

One `index.html`, CSS and JS inline in `<style>`/`<script>` (keeps it a
genuinely single self-contained *page*), assets referenced from an external
`assets/` folder (NOT base64-inlined — a 15s 1080p video alone can be
15-20MB, which blows past artifact/data-URI size limits fast).

For micro-interaction and state detail beyond the reveal/nav basics below
(hover/focus states, loading states, form validation feedback, empty
states), load `interaction-design`.

Patterns to reuse rather than reinvent — see `references/page-patterns.md`:
- Mobile-first fluid type with `clamp()`, not fixed breakpoint font sizes.
- A fixed/transparent nav that solidifies (`backdrop-filter` + opacity) past
  a scroll threshold.
- `IntersectionObserver`-driven `.reveal` fade-ins instead of a scroll
  animation library.
- The booking/pricing calculator pattern (date math, minimum-stay
  validation, live price breakdown) if the brief has any kind of
  quote/estimate/reservation flow.
- **Any full-bleed hero image/video section needs a plain CSS
  `background-image` fallback underneath it.** If the "real" visual is a
  `<video>` that only becomes visible once JS adds a class after
  `loadedmetadata` fires, a slow network or an autoplay-policy delay leaves
  the whole hero looking blank/dark with just a floating card on top of it —
  a real bug hit and fixed in the Vesper build. The CSS background always
  renders instantly regardless of what JS does.

Write all copy in whatever language the brief specifies. Keep every brand
name reference (title, nav, footer wordmark, meta tags, any narrative copy
that explains the *meaning* of the name) consistent — if the user later
renames the brand, grep for the old name across the whole file, don't trust
memory of where it appeared. Etymological or narrative copy tied to the old
name (e.g. "X is the name of the evening star...") usually needs a rewrite,
not just a find-replace, once the name changes to something unrelated.

### 4. Verify locally before deploying

Create `.claude/launch.json` at the working directory root (one level above
the site folder) pointing a Python static server at the site directory, then
use the Browser tools to check it — `read_page` for structure,
`javascript_tool` for computed-style/behavior assertions, `resize_window`
with the `mobile`/`tablet`/`desktop` presets to check breakpoints, and
`read_console_messages` / `read_network_requests` for 404s and JS errors.

**Known limitation**: in some sessions the Browser pane never composites
(`computer` screenshots time out, `document.visibilityState` stays
`"hidden"`), which also silently disables `requestAnimationFrame` and video
seeking — not a bug in the page, a limitation of that session's preview
pane. When this happens, fall back to the `playwright` MCP plugin for
automated screenshot/interaction testing instead of losing visual
verification entirely; otherwise verify logic through `javascript_tool`
assertions (computed styles, class states, geometry), and *say so plainly*
rather than claiming a visual behavior was confirmed when it wasn't. Tell
the user to check the deployed link themselves for the final visual call.

Test the interactive calculator's actual math (not just that it renders):
dispatch real `change` events after setting input values via
`form_input`/`javascript_tool`, and check both a valid case and the
validation-error case (e.g. below minimum nights).

Before deploying, run two automated design-QA passes rather than eyeballing
the result: load `web-design-guidelines` to check the page against the
Vercel Web Interface Guidelines (layout, typography, color, motion,
accessibility), and load `visual-critique` for a hierarchy/composition/
typography/brand-consistency audit with a prioritized fix list. Fix
anything either one flags before moving to deploy.

### 5. Deploy

```bash
vercel whoami                 # confirm already logged in; don't try to auth interactively
cd <site-dir>
vercel --prod --yes           # first deploy: creates a project, aliases to <slug>.vercel.app
```

To change the project's name/slug later: delete `.vercel/project.json` (or
the whole `.vercel/` dir) to unlink, then `vercel --prod --yes --name
<new-slug>` to create a fresh project and alias. Only run
`vercel remove <old-slug> --yes` afterward if the old project is truly this
site and not something else the user cares about — ask first if unsure.

Report back the live URL. That's the deliverable, not a description of one.

## Beyond a single page

A few installed skills cover work outside this skill's default scope —
load them only when the brief actually calls for it, don't force them in:

- `design-research` — personas, interview scripts, usability testing, if
  the client wants copy/IA backed by actual user research rather than a
  brief alone.
- `ux-strategy` — information architecture, nav patterns, content
  strategy, once the "one page" grows into multiple pages/flows.
- `design-ops` — handoff specs, critique facilitation, design-debt audits,
  if collaborating with a client's own design/dev team.
- `designer-toolkit` — turning the finished site into a portfolio case
  study, client presentation, or design brief document.

## Reference files

- `references/asset-generation.md` — the generate_image/generate_video MCP
  workflow in detail: model resolution, cost preflight, the batch
  concurrency gotcha, polling, download, ffmpeg compression recipes.
- `references/page-patterns.md` — copy-pasteable CSS/JS snippets: fluid
  type scale, nav solidify, scroll-reveal, booking/price calculator.
