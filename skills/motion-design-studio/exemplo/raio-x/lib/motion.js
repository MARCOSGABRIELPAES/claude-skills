// motion.js — vocabulário de movimento para filmes seek(t).
// Regra de ouro: toda função aqui é PURA no tempo. Nada de timers, transições CSS, Math.random
// ou estado guardado entre quadros. Assim qualquer quadro pode ser renderizado sozinho, em qualquer ordem.

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
/** Progresso 0..1 de t dentro da janela [t0, t0 + dur]. */
export const prog = (t, t0, dur) => clamp((t - t0) / dur);

export const ease = {
  out3: k => 1 - (1 - clamp(k)) ** 3,
  in3: k => clamp(k) ** 3,
  inOut3: k => ((k = clamp(k)) < .5 ? 4 * k ** 3 : 1 - (-2 * k + 2) ** 3 / 2),
  in4: k => clamp(k) ** 4,            // lado de SAÍDA de uma costura (acelera para o corte)
  out4: k => 1 - (1 - clamp(k)) ** 4, // lado de ENTRADA (sai do corte já em velocidade)
};

// ------------------------------------------------------------------ molas
/**
 * Mola amortecida em forma fechada, de 0 a 1, `t` segundos depois de disparar.
 * Não é simulação: é a solução analítica, então o quadro N não depende do N-1.
 * k = rigidez, d = amortecimento.
 */
export function spring(t, k = 170, d = 26) {
  if (t <= 0) return 0;
  const w0 = Math.sqrt(k), z = d / (2 * w0);
  if (z < 1) { // subamortecida: passa um pouco do alvo e volta
    const wd = w0 * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
  }
  return 1 - Math.exp(-w0 * t) * (1 + w0 * t); // criticamente amortecida: chega sem passar
}

/** Presets por "massa" do que se move. UI pode passar um fio do alvo; tipografia nunca passa. */
export const MOLA = {
  seca: [320, 30],     // cursor, toggle, borda que lidera
  ui: [220, 24],       // chips, notificações, pílulas
  base: [170, 26],     // cards, containers, câmera
  texto: [150, 26],    // tipografia grande, sem overshoot
  pesada: [90, 20],    // logo, palavra gigante pousando
  elastica: [260, 14], // adesivo, mascote (quique visível)
};
export const mola = (t, preset = 'base') => spring(t, ...MOLA[preset]);

/**
 * Um valor com vários alvos no tempo: [[t0, v0], [t1, v1], ...].
 * Cada mudança soma a própria mola a partir do seu instante — nunca "reinicia" a animação.
 */
export function trilha(t, chaves, preset = 'base') {
  let v = chaves[0][1];
  for (let i = 1; i < chaves.length; i++) v += (chaves[i][1] - chaves[i - 1][1]) * mola(t - chaves[i][0], preset);
  return v;
}

/** Estalo e pausa: a mudança acontece em ~2 quadros e fica parada. Lê como decisão, não como slide. */
export const estalo = (t, t0, dur = .07) => ease.out4((t - t0) / dur);

/** Atraso do i-ésimo item de uma cascata. */
export const escalonar = (i, passo = .08) => i * passo;

// ------------------------------------------------------------------ tipografia cinética
/** Entrada de uma palavra: sobe na mola de texto, desfoca -> foca. Devolve números de estilo. */
export function palavraEntra(t, em, { preset = 'texto', sobe = 46, deEscala = 1.15, blur = 14 } = {}) {
  const s = mola(t - em, preset);
  return { opacity: prog(t, em, .12), y: (1 - s) * sobe, scale: lerp(deEscala, 1, s), blur: (1 - clamp(s * 1.25)) * blur };
}
/** Saída: acelera para longe (in4), para o corte seguinte cair no pico de velocidade. */
export function palavraSai(t, em, { dur = .16, y = -34, escala = 1.06, blur = 12 } = {}) {
  const p = ease.in4((t - em) / dur);
  return { opacity: 1 - p, y: p * y, scale: lerp(1, escala, p), blur: p * blur };
}
/** Converte números de estilo em CSS e aplica. */
export function aplica(el, { opacity = 1, x = 0, y = 0, scale = 1, rot = 0, blur = 0 }) {
  el.style.opacity = opacity;
  el.style.transform = `translate(${x}px,${y}px) scale(${scale}) rotate(${rot}deg)`;
  el.style.filter = blur > .05 ? `blur(${blur}px)` : 'none';
}

/**
 * Liga todos os `.titulo` dentro de root. Marcação:
 *   <div class="titulo" data-sai="2.2"><span class="p" data-em=".3">Sua</span> <span class="p" data-em=".45">empresa</span></div>
 * (separe as palavras com espaço real, nunca com margin). Devolve desenha(t).
 */
export function ligaTitulos(root = document) {
  const titulos = [...root.querySelectorAll('.titulo')].map(el => ({
    el, sai: +(el.dataset.sai ?? 1e9), preset: el.dataset.preset || 'texto',
    palavras: [...el.querySelectorAll('.p')].map(p => ({ el: p, em: +p.dataset.em })),
  }));
  return t => {
    for (const ti of titulos) {
      const visivel = t >= ti.palavras[0].em - .01 && t < ti.sai + .2;
      ti.el.style.visibility = visivel ? 'visible' : 'hidden';
      if (!visivel) continue;
      aplica(ti.el, t >= ti.sai ? palavraSai(t, ti.sai) : {});
      for (const p of ti.palavras) aplica(p.el, palavraEntra(t, p.em, { preset: ti.preset }));
    }
  };
}

// ------------------------------------------------------------------ costuras (transições)
/**
 * Costura com velocidade casada: a cena A sai com in4 e a B entra com out4, mesma distância e duração.
 * O corte acontece NO MEIO do movimento dos dois lados. Devolve { sai, entra } em 0..1.
 */
export const costura = (t, corte, dur = .24) => ({ sai: ease.in4((t - (corte - dur)) / dur), entra: ease.out4((t - corte) / dur) });

/** Empurrão de grupo sem corte: lento-rápido-lento (10% / 65% / 25%). */
export function empurrao(t, t0, dur) {
  const p = prog(t, t0, dur);
  if (p < .1) return .03 * ease.in3(p / .1);
  if (p < .75) return .03 + .87 * ((p - .1) / .65);
  return .9 + .1 * ease.out3((p - .75) / .25);
}

// ------------------------------------------------------------------ utilidades
/** PRNG com semente (mulberry32). Num filme, nunca Math.random. */
export function rng(seed) {
  return () => {
    seed = (seed + 0x6D2B79F5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
/** Hash determinístico de um número para 0..1. */
export const hash = s => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

/** Tremor de câmera a partir de impactos [[t, força px, decaimento s], ...]. */
export function tremor(t, impactos, fps = 30) {
  let x = 0, y = 0;
  for (const [ti, a, d] of impactos) {
    if (t < ti || t > ti + 6 * d) continue;
    const k = Math.exp(-(t - ti) / d) * a, f = Math.floor(t * fps * 2);
    x += (hash(f + ti) - .5) * 2 * k; y += (hash(f * 1.7 + ti) - .5) * 2 * k;
  }
  return { x, y };
}

/** Área segura de Reels/TikTok em 1080x1920. Texto fica dentro; centralize em x = 540. */
export const SEGURO = { topo: 250, base: 1440, faixaBotoes: [880, 1600], esq: 190, dir: 890, cx: 540 };

/** Grade de batidas: 120 BPM -> 0.5 s por batida. b(4) = início da 4ª batida. */
export const grade = (bpm = 120) => n => n * 60 / bpm;
