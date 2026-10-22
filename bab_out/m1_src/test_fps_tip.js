// test_fps_tip.js - the 30-frames tip (0.8.47): a touch screen whose browser hands the game 30 frames a second (as iOS does
// in Low Power Mode; made here by answering every frame request a frame late) gets one tip, once, after some seconds of
// play, worded for its phone (Low Power Mode on an iPhone, battery saver elsewhere) and in Arabic when the game is; it is
// remembered, so a second visit gets none; at the full 60, or with a mouse, there is none.
const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
const HALF = () => { const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = cb => raf(() => raf(cb)); };
const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  async function go(o) {
    const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, hasTouch: !!o.touch, isMobile: !!o.touch, userAgent: o.ua });
    if (o.half) await ctx.addInitScript(HALF);
    const page = await ctx.newPage(), errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const run = async (secs) => {
      await page.goto('http://127.0.0.1:8766/index.html');
      await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
      await page.evaluate(() => { window.__hints = []; const f = Render.setHint; Render.setHint = function (s) { if (s) window.__hints.push(s); return f.apply(this, arguments); }; });
      if (o.ar) await page.evaluate(() => window.__m1.setLang('ar'));
      await page.evaluate(() => window.__m1.begin('m1', 0));
      await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
      const t0 = Date.now(); let tip = null;
      while (Date.now() - t0 < secs * 1000 && !tip) {
        await sleep(500);
        tip = await page.evaluate(() => window.__hints.find(h => /Low Power|Battery saver|الطاقة المنخفضة|توفير البطارية/.test(h)) || null);
      }
      const m = await page.evaluate(() => { const x = window.__m1.meter(); return { hz: x.M.hz, snap: +x.M.snap.toFixed(2), slow: Math.round(x.P.slow) }; });
      const saved = await page.evaluate(() => { try { return JSON.parse(localStorage.getItem('strait-m1')).fpsTip; } catch (e) { return null; } });
      return { tip, secs: ((Date.now() - t0) / 1000).toFixed(1), m, saved };
    };
    return { ctx, page, errors, run };
  }
  // a touch screen at 30 frames: the tip, once
  let s = await go({ touch: true, half: true });
  let r = await s.run(25);
  note(r.tip === 'Battery saver on? Turning it off makes the game smoother', 'touch screen at 30 a second (' + JSON.stringify(r.m) + '): the tip came after ' + r.secs + ' s: ' + r.tip);
  note(r.saved === true, 'and it is remembered on the device (' + r.saved + ')');
  r = await s.run(12);
  note(!r.tip, 'the next visit at 30 a second: no tip again (' + r.tip + ')');
  note(!s.errors.length, 'no errors on the page' + (s.errors.length ? ': ' + s.errors.join(' | ') : ''));
  await s.ctx.close();
  // an iPhone at 30 frames: Low Power Mode, and in Arabic
  s = await go({ touch: true, half: true, ua: IPHONE });
  r = await s.run(25);
  note(r.tip === 'Low Power Mode on? Turning it off makes the game smoother', 'an iPhone at 30 a second: ' + r.tip);
  await s.ctx.close();
  s = await go({ touch: true, half: true, ua: IPHONE, ar: true });
  r = await s.run(25);
  note(r.tip === 'هل وضع الطاقة المنخفضة مفعّل؟ إيقافه يجعل اللعبة أنعم', 'the same in Arabic: ' + r.tip);
  await s.ctx.close();
  // the full 60 on a touch screen, and 30 with a mouse: nothing
  s = await go({ touch: true, half: false });
  r = await s.run(12);
  note(!r.tip && r.m.hz > 45, 'a touch screen at the full rate (' + JSON.stringify(r.m) + '): no tip (' + r.tip + ')');
  await s.ctx.close();
  s = await go({ touch: false, half: true });
  r = await s.run(12);
  note(!r.tip, 'a mouse and keyboard at 30 a second: no tip (' + r.tip + ')');
  await s.ctx.close();
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
