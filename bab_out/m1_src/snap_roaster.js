// snap_roaster.js - pictures of the Big Roaster at the old lighthouse (24 Oct: Khaled's five small look edits, and its
// phase banners in Arabic): the machine whole and smoking, the chimney going (with its banner), the stub, the drum
// cracking (with its banner), the cracked drum, and what is left of it; then the two banners again in Arabic. The game
// is stepped by hand (frozen), Yazeed walking up to wake it and then standing back, and left to draw a frame for each
// picture. Run it on the live build and on the test build to get before and after.
// Usage: node snap_roaster.js <url> <out dir>
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2];
const OUT = process.argv[3];
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.setLang('en'));
  await page.evaluate(() => window.__m1.begin('mocha', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  // step by hand until cond(s) holds or n ticks pass; mx: Yazeed's stick (1 walks on, 0 stands)
  const run = (cond, n, mx) => page.evaluate(([c, n, mx]) => {
    window.__m1.frozen = true;
    const cond = c ? eval('(' + c + ')') : null;
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      if (cond && cond(s)) break;
      const inp = { mx: mx, my: 0, viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes };
      Sim.step(s, inp);
      if (s.events.length) Render.onEvents(s, s.events);
      s.p.inv = Math.max(s.p.inv, 2);                 // (the pictures are of the machine: Yazeed comes to no harm)
      if (s.boss && s.boss.kind === 'roaster' && s.boss.st !== 'intro' && s.boss.st !== 'stun' && s.boss.st !== 'dying' && s.boss.st !== 'dead') { s.boss.st = 'idle'; s.boss.cd = 9999; }   // (it sits still for its portrait)
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
    }
    return t;
  }, [cond ? cond.toString() : null, n, mx]);
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(40);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    const at = await page.evaluate(() => { const s = window.__m1.sim(), b = s.boss; return b ? { x: Math.round(b.x - s.cam), y: Math.round(b.y), phase: b.phase, st: b.st, hp: b.hp, cam: Math.round(s.cam), vw: s.viewW, vh: s.viewH, cw: Render.width(), ch: Render.height() } : null; });
    console.log('picture', name, JSON.stringify(at));
  };
  const hurtTo = (hp) => page.evaluate((hp) => { const s = window.__m1.sim(), b = s.boss; Sim.ext.roaster.hurt(s, b.hp - hp); }, hp);

  // walk up until it wakes and rolls in, then stand back while it settles
  let t = await run(s => s.boss && s.boss.kind === 'roaster', 60 * 40, 1);
  console.log('woke after', (t / 60).toFixed(1), 's');
  t = await run(s => s.boss.st !== 'intro', 60 * 6, 0);
  await run(null, 90, -1);
  await run(null, 40, 0);
  await snap('r1_whole');
  // the chimney goes
  await hurtTo(199);
  await run(s => s.boss.st === 'stun', 10, 0);
  await run(null, 14, 0);
  await snap('r2_chimney_goes');
  await run(null, 120, 0);
  await snap('r3_stub');
  // the drum cracks
  await hurtTo(99);
  await run(s => s.boss.st === 'stun', 10, 0);
  await run(null, 14, 0);
  await snap('r4_drum_cracks');
  await run(null, 120, 0);
  await snap('r5_cracked');
  // in Arabic: the two banners again, on a fresh start
  await page.evaluate(() => window.__m1.setLang('ar'));
  await page.evaluate(() => { window.__m1.frozen = false; window.__m1.begin('mocha', 3); });
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  await run(s => s.boss && s.boss.kind === 'roaster', 60 * 40, 1);
  await run(s => s.boss.st !== 'intro', 60 * 6, 0);
  await run(null, 90, -1);
  await hurtTo(199);
  await run(s => s.boss.st === 'stun', 10, 0);
  await run(null, 14, 0);
  await snap('r6_chimney_goes_ar');
  await run(null, 120, 0);
  await hurtTo(99);
  await run(s => s.boss.st === 'stun', 10, 0);
  await run(null, 14, 0);
  await snap('r7_drum_cracks_ar');
  // what is left of it
  await page.evaluate(() => window.__m1.setLang('en'));
  await hurtTo(0);
  await run(s => s.boss.st === 'dead', 60 * 6, 0);
  await run(null, 30, 0);
  await snap('r8_wreck');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
