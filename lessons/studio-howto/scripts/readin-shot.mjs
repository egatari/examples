// 4 章の図「本で読む」を撮る。Egatari Studio の checkout の直下に置いて動かす（kit/browser.mjs を使う）：
//   node readin-shot.mjs "<再生専用の .play.ega.html>" <出力のフォルダ>
import { launch } from './kit/browser.mjs';
const [file, out] = process.argv.slice(2);
const b = await launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
const errs = []; p.on('pageerror', e => errs.push(String(e)));
await p.goto('file://' + file); await p.waitForFunction(() => window.DECK && DECK.state);
await p.evaluate(() => DECK.go(6, 3)); await p.mouse.move(1270, 10); await p.waitForTimeout(7000);
await p.mouse.move(640, 690); await p.waitForTimeout(600);
await p.screenshot({ path: out + '/book-readin-1280.png' });
await p.click('#deck-readin'); await p.waitForTimeout(1200);
console.log('after', JSON.stringify(await p.evaluate(() => ({ st: DECK.state(), layout: document.documentElement.dataset.deckLayout }))));
await p.mouse.move(1270, 300); await p.waitForTimeout(4000);
await p.screenshot({ path: out + '/book-readin-split-1280.png' });
console.log('back', JSON.stringify(await p.evaluate(() => { const e = document.querySelector('#deck-text .dx-back'); return e && { t: e.textContent, a: e.getAttribute('aria-label'), ti: e.title, h: e.hidden }; })));
console.log('errors', errs.length, errs.slice(0, 2)); await b.close();
