// Kontakt sayfası: node tools/preview/contact.mjs [filtre] [çıktı.png] [hücre boyu, varsayılan 320]
// game/assets/models altındaki .glb dosyalarını tek bir PNG'de gösterir.
import { createServer } from 'node:http';
import { readFile, readdir, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const filtre = process.argv[2] || '';
const out = path.resolve(process.argv[3] || path.join(here, 'out', `sayfa${filtre ? '_' + filtre : ''}.png`));
const models = (await readdir(path.join(root, 'game/assets/models')))
  .filter(f => f.endsWith('.glb') && f.includes(filtre)).map(f => f.slice(0, -4)).sort();

const types = { '.html': 'text/html', '.js': 'text/javascript', '.glb': 'model/gltf-binary' };
const server = createServer(async (req, res) => {
  const p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  try { res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' }); res.end(await readFile(p)); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;

const cols = Math.min(4, models.length);
const cell = Number(process.argv[4] || 320);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: cols * cell, height: Math.ceil(models.length / cols) * cell } });
page.on('console', m => { if (m.type() === 'error') console.error('sayfa:', m.text()); });
await page.goto(`http://localhost:${port}/tools/preview/preview.html?cols=${cols}&cell=${cell}&files=${models.join(',')}`);
await page.waitForFunction(() => window.__done === true, null, { timeout: 120000 });
await mkdir(path.dirname(out), { recursive: true });
await page.screenshot({ path: out, fullPage: true });
await browser.close();
server.close();
console.log(`${models.length} model -> ${path.relative(process.cwd(), out)}`);
