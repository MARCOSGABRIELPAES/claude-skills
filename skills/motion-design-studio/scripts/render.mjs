// render.mjs — renderizador quadro-a-quadro de filmes seek(t).
// Serve a pasta do filme, abre a página no Chromium headless, chama window.renderAt(t) para cada quadro,
// tira o screenshot e manda para o ffmpeg. Como cada quadro é função pura do tempo, o resultado é exato.
//
//   node render.mjs --root <pasta> --fps 60 --from 0 --to 8 --out out/video.mp4
//   node render.mjs --root <pasta> --stills 0.5,2.1,4.8          -> out/stills/still-<t>.png
//
// Opções:  --page film.html  --size 1080x1920  --scale 2 (desenha em 2x e reduz com lanczos)
//          --sub N --shutter .5 (motion blur: N subquadros na fração do obturador, média com tmix)
//          --workers N (páginas em paralelo)  --jpeg (rascunho ~3x mais rápido)
//
// Contrato da página: define window.ready = true quando carregou e expõe async window.renderAt(t).
// Playwright: resolvido da pasta do filme, depois do NODE_PATH, depois do npm global.
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync, execSync } from 'node:child_process';
import { createRequire } from 'node:module';

const argv = process.argv.slice(2), args = {};
for (let i = 0; i < argv.length; i++) {
  if (!argv[i].startsWith('--')) continue;
  const k = argv[i].slice(2), v = argv[i + 1];
  args[k] = v && !v.startsWith('--') ? (i++, v) : 'true';
}
const ROOT = path.resolve(args.root ?? '.'), PAGE = args.page ?? 'film.html';
const FPS = +(args.fps ?? 60), SUB = Math.max(1, +(args.sub ?? 1)), SHUTTER = +(args.shutter ?? .5);
const FROM = +(args.from ?? 0), TO = +(args.to ?? 8), SCALE = +(args.scale ?? 1);
const [W, H] = (args.size ?? '1080x1920').split('x').map(Number);
const OUT = path.resolve(ROOT, args.out ?? 'out/video.mp4');
const STILLS = args.stills ? args.stills.split(',').map(Number) : null;
const WORKERS = STILLS ? 1 : Math.max(1, +(args.workers ?? Math.min(6, Math.floor(os.cpus().length / 2) || 1)));
const FORMAT = args.jpeg && !STILLS ? 'jpeg' : 'png';

function loadPlaywright() {
  const tries = [path.join(ROOT, 'package.json'), import.meta.url];
  try { tries.push(path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'x.js')); } catch {}
  for (const base of tries) for (const name of ['playwright-core', 'playwright']) {
    try { return createRequire(base)(name); } catch {}
  }
  throw new Error('Playwright não encontrado. Rode na pasta do filme: npm i playwright-core');
}
function findChromium() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const caches = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), '.cache/ms-playwright'),
    path.join(os.homedir(), 'Library/Caches/ms-playwright'), path.join(os.homedir(), 'AppData/Local/ms-playwright')].filter(Boolean);
  const tails = ['chrome-linux/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
    'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing', 'chrome-win/chrome.exe'];
  for (const c of caches) {
    if (!fs.existsSync(c)) continue;
    const dirs = fs.readdirSync(c).filter(d => /^chromium-\d+$/.test(d)).sort((a, b) => b.split('-')[1] - a.split('-')[1]);
    for (const d of dirs) for (const t of tails) if (fs.existsSync(path.join(c, d, t))) return path.join(c, d, t);
  }
  return undefined; // deixa o Playwright usar o padrão dele
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf' };
const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] ?? 'application/octet-stream' }); res.end(data);
  });
}).listen(0);

const { chromium } = loadPlaywright();
const browser = await chromium.launch({ executablePath: findChromium(), args: ['--force-color-profile=srgb', '--hide-scrollbars'] });
async function openPage() {
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('[erro na página]', e.message));
  await page.goto(`http://localhost:${server.address().port}/${PAGE}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  const cdp = await ctx.newCDPSession(page);
  return async t => {
    await page.evaluate(t => window.renderAt(t), t);
    const { data } = await cdp.send('Page.captureScreenshot', { format: FORMAT, ...(FORMAT === 'jpeg' ? { quality: 95 } : {}), optimizeForSpeed: true });
    return Buffer.from(data, 'base64');
  };
}

let code = 0;
const partial = OUT.replace(/(\.\w+)$/, '.partial$1');
try {
  const pages = await Promise.all(Array.from({ length: WORKERS }, openPage));
  if (STILLS) {
    const dir = path.join(ROOT, 'out/stills'); fs.mkdirSync(dir, { recursive: true });
    for (const t of STILLS) fs.writeFileSync(path.join(dir, `still-${t.toFixed(2)}.png`), await pages[0](t));
    console.log(`stills -> ${dir}`);
  } else {
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    const blur = SUB > 1 ? `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB,` : '';
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-i', '-',
      '-vf', `${blur}scale=${W}:${H}:flags=lanczos,format=yuv420p`, '-r', String(FPS),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-movflags', '+faststart', partial], { stdio: ['pipe', 'inherit', 'inherit'] });
    const ffDone = new Promise(r => ff.on('close', r));
    const total = Math.round((TO - FROM) * FPS), t0 = Date.now();
    const pending = new Map(); let next = 0;
    // cada worker pega o próximo quadro; o laço principal escreve em ordem
    // cada página tem uma fila: um quadro por vez por página (renderAt + screenshot não podem intercalar)
    const queue = pages.map(() => Promise.resolve());
    const take = i => {
      if (pending.has(i)) return pending.get(i);
      const w = i % WORKERS, shot = pages[w];
      const p = queue[w].then(async () => {
        const bufs = [];
        for (let j = 0; j < SUB; j++) bufs.push(await shot(FROM + (i + (SUB > 1 ? j / SUB * SHUTTER : 0)) / FPS));
        return bufs;
      });
      queue[w] = p.catch(() => {});
      pending.set(i, p);
      return p;
    };
    for (let i = 0; i < total; i++) {
      while (next < Math.min(total, i + WORKERS * 2)) take(next++); // janela à frente, uma por página
      for (const b of await take(i)) if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r));
      pending.delete(i);
      if (i % FPS === 0) console.log(`quadro ${i}/${total}  ${((Date.now() - t0) / (i + 1) / 1000).toFixed(2)} s/quadro`);
    }
    ff.stdin.end();
    if (await ffDone !== 0) throw new Error('ffmpeg falhou');
    const got = +spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
      'stream=nb_read_packets', '-of', 'csv=p=0', partial], { encoding: 'utf8' }).stdout;
    if (got !== total) throw new Error(`codificou ${got} quadros, esperava ${total}`);
    fs.renameSync(partial, OUT);
    console.log(`vídeo -> ${OUT}  (${total} quadros, ${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  }
} catch (e) {
  code = 1; console.error('render falhou:', e.message); fs.rmSync(partial, { force: true });
} finally {
  await browser.close(); server.close();
}
process.exit(code);
