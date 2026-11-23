// Play the SCORM package of this lesson with a stand-in LMS (window.API, SCORM 1.2) and print what it records.
// right: answer both questions correctly → lesson_status completed, score 100. wrong: miss question 2 → no completed, score 50.
// Run from an Egatari Studio v0.6.19 checkout (uses kit/browser.mjs), on the unzipped package:
//   node scorm_check.mjs <unzipped>/index.html right|wrong
import { launch } from './kit/browser.mjs';
const [file, mode] = process.argv.slice(2);   // mode: right | wrong
const b = await launch(); const ctx = await b.newContext({ viewport: { width: 1280, height: 720 } });
await ctx.addInitScript(() => {
  window.__calls = []; const store = {}; const log = (x) => window.__calls.push(x);
  window.API = { LMSInitialize: () => 'true', LMSGetValue: (k) => store[k] || '', LMSSetValue: (k, x) => { log([k, x]); store[k] = x; return 'true'; },
    LMSCommit: () => 'true', LMSFinish: () => { log(['finish']); return 'true'; }, LMSGetLastError: () => '0', LMSGetErrorString: () => '', LMSGetDiagnostic: () => '' };
});
const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
await p.goto('file://' + file); await p.waitForFunction(() => window.DECK && DECK.state);
const n = await p.evaluate(() => DECK.slides ? DECK.slides.length : document.querySelectorAll('section.slide').length);
const ANS = { 2: 0, 4: 1 };   // slide index (0-based) → correct choice
await p.evaluate(() => document.addEventListener('deck:answer', (e) => (window.__ans = window.__ans || []).push(e.detail)));
await p.click('#stage', { position: { x: 1200, y: 100 } });
for (let guard = 0; guard < 80; guard++) {
  const st = await p.evaluate(() => DECK.state());
  const i = st.slide - 1;
  if (i in ANS && st.step === 1) {
    const pick = mode === 'wrong' && i === 4 ? 2 : ANS[i];
    await p.click(`m-predict .pd-pick >> nth=${pick}`, { timeout: 5000 }).catch(async () => { await p.locator('section.slide').nth(i).locator('m-predict .pd-pick').nth(pick).click(); });
    await p.evaluate(() => document.activeElement && document.activeElement.blur());
  }
  if (st.slide === n && st.step === st.max) break;
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(250);
}
console.log('answers', JSON.stringify(await p.evaluate(() => window.__ans)));
await p.waitForTimeout(800);
await p.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: false })));
const calls = await p.evaluate(() => window.__calls);
const last = (k) => { const c = calls.filter((x) => x[0] === k); return c.length ? c[c.length - 1][1] : null; };
console.log('calls', calls.length, JSON.stringify(calls.slice(0, 12)), await p.evaluate(() => DECK.trackingAdapter && DECK.trackingAdapter()));
console.log('last suspend', last('cmi.suspend_data'), 'keys', [...new Set(calls.map(c => c[0]))].join(' '));
console.log(mode, 'slides', n, '| lesson_status', last('cmi.core.lesson_status'), '| score.raw', last('cmi.core.score.raw'), '| min/max', last('cmi.core.score.min'), last('cmi.core.score.max'), '| errors', errs.length, errs.slice(0, 2));
await b.close();
