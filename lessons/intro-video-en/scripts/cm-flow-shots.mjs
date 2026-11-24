// Screens for scenes 2 and 3 of the English intro video (images/cm-a-copy … cm-g-fixed). Run from an Egatari Studio checkout (v0.6.19 used),
// placed at tools/cm-flow-shots.mjs:  CM_LANG=en CM_TITLE=<title> CM_ERR=<error text> CM_SLIDE=<slide> CM_FIRST=<slide> node tools/cm-flow-shots.mjs <folder with r0/reply.txt and r1/reply.txt> <out dir>
// The replies are real chat-AI outputs from our nightly evaluation in English (a fictional shop-app pitch): r0 has a quality-check error (a flow chart overflowing), r1 is the AI's fix.
// CM_SLIDE is the slide with the error and CM_FIRST the slide shown first; without the variables the script takes the Japanese video's values.
// CM の場面 2・3 の画面：新規作成で指示をコピー → 対話型 AI の返事（毎晩の評価の実際の回）を貼る → 作成 → 品質チェックのエラー → 修正依頼 → 直した返事を貼って置き換える
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import http from 'node:http';
import { execFileSync } from 'node:child_process'; import { fileURLToPath } from 'node:url';
import { launch } from '../kit/browser.mjs';
import { answerNew } from './test-app-llm.mjs';
import { clickDlg } from './click-retry.mjs';
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const [runDir, out] = process.argv.slice(2);
const LANG = process.env.CM_LANG || 'ja', TITLE = process.env.CM_TITLE || '需要と供給', ERR = process.env.CM_ERR || '本文が下にはみ出す', SLIDE = +(process.env.CM_SLIDE || 2), FIRST = +(process.env.CM_FIRST || 1);
fs.mkdirSync(out, { recursive: true });
const r0 = fs.readFileSync(path.join(runDir, 'r0/reply.txt'), 'utf8'), r1raw = fs.readFileSync(path.join(runDir, 'r1/reply.txt'), 'utf8');
const DIST = fs.mkdtempSync(path.join(os.tmpdir(), 'cm-dist-'));
execFileSync(process.execPath, [path.join(ROOT, 'tools/build-app.mjs'), '--out', DIST, '--no-examples'], { stdio: 'ignore' });
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.woff2': 'font/woff2', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.wasm': 'application/wasm' };
const srv = http.createServer((req, res) => { const p = decodeURIComponent(new URL(req.url, 'http://x').pathname); const f = path.join(DIST, p.endsWith('/') ? p + 'index.html' : p);
  if (!f.startsWith(DIST) || !fs.existsSync(f) || !fs.statSync(f).isFile()) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res); });
await new Promise((r) => srv.listen(0, r)); const BASE = `http://localhost:${srv.address().port}/`;
const b = await launch(); const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, locale: LANG === 'en' ? 'en-US' : 'ja-JP' });
await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(BASE).origin }).catch(() => {});
const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
const shot = (n) => p.screenshot({ path: path.join(out, n) });
const box = async (sel) => { const r = await p.locator(sel).first().boundingBox(); return r && { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; };
const boxes = {};
const goLast = async (i) => { for (const f of p.frames()) { const ok = await f.evaluate((i) => { if (!window.DECK || !DECK.go) return false; DECK.go(i, 0); DECK.go(i, DECK.state().max); return true; }, i).catch(() => false); if (ok) return true; } return false; };
await p.goto(BASE + '?lang=' + LANG); await p.waitForSelector('#drop');
await p.click('#w-new');
await answerNew(p, { cat: 'teaching', sub: 'class', title: TITLE });
await p.waitForTimeout(600);
boxes.copy = await box('#paste-copy-guide');
await p.evaluate(() => document.getElementById('paste-copy-guide').scrollIntoView({ block: 'center' })); await p.waitForTimeout(300);
boxes.copy = await box('#paste-copy-guide'); await shot('a-copy.png');
await p.click('#paste-copy-guide'); await p.waitForTimeout(800);
if (!(await p.isVisible('#paste-deck'))) await p.click('#paste-step-paste-btn');
await p.fill('#paste-deck', r0); await p.waitForTimeout(600);
await p.evaluate(() => document.getElementById('dlg-import').scrollIntoView({ block: 'center' })); await p.waitForTimeout(300);
boxes.create = await box('#dlg-import'); await shot('b-paste.png');
await clickDlg(p, '#dlg-import');
await p.waitForFunction(() => { const s = window.__APP_TEST.state(); return s.portable && s.loads > 0 && s.frameLoaded === s.loads; }, null, { timeout: 60000 });
await p.waitForSelector('#panel:not([hidden]) #panel-body .sum', { timeout: 60000 });
await p.waitForTimeout(1500); await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await goLast(FIRST); await p.waitForTimeout(2500); await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await shot('c-created.png');
// 品質チェックのエラーのあるスライドへ（板の最初のエラーを押す）
const errItem = p.locator('#panel-body').getByText(ERR).first();
if (await errItem.count()) { await errItem.click().catch(() => {}); await p.waitForTimeout(1500); }
boxes.fixreq = await box('#panel-body #b-fixreq'); boxes.err = await errItem.boundingBox().catch(() => null);
await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await goLast(SLIDE); await p.waitForTimeout(2500); await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await shot('d-error.png');
// 修正依頼 → 貼り付け
await p.click('#panel-body #b-fixreq'); await p.waitForSelector('#dlg[open] #fix-text');
await p.waitForTimeout(500); boxes.fixcopy = await box('#fix-copy'); await shot('e-fixreq.png');
const ids = await p.evaluate(() => { const f = window.__APP_TEST.files(); const d = new TextDecoder().decode(Uint8Array.from(atob(f['deck.html']), (c) => c.charCodeAt(0))); return [...d.matchAll(/<section\b[^>]*\bid="(s-[a-z0-9]+)"/g)].map((m) => m[1]); });
const old = [...new Set([...r1raw.matchAll(/<section\b[^>]*\bid="(s-[a-z0-9]+)"/g)].map((m) => m[1]))];
let r1 = r1raw; old.forEach((o, i) => { if (ids[i]) r1 = r1.split(o).join(ids[i]); });
await p.click('#dlg-paste'); await p.waitForSelector('#dlg[open] #paste-deck');
await p.fill('#paste-deck', r1); await p.waitForTimeout(600); boxes.replace = await box('#dlg-import'); await shot('f-paste-fix.png');
await clickDlg(p, '#dlg-import'); await p.waitForTimeout(4000);
const discard = await p.$('#dlg[open] #dlg-ok'); if (discard) await clickDlg(p, '#dlg-ok').catch(() => {});
await p.waitForFunction(() => { const s = window.__APP_TEST.state(); return s.frameLoaded === s.loads; }, null, { timeout: 60000 });
await p.waitForTimeout(2500); await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await goLast(SLIDE); await p.waitForTimeout(2500); await p.mouse.move(1270, 300); await p.waitForTimeout(5000);
await shot('g-fixed.png');
console.log(JSON.stringify({ ids, old, boxes, sum: await p.textContent('#panel-body .sum').catch(() => null), errs: errs.slice(0, 3) }));
await b.close(); srv.close();
