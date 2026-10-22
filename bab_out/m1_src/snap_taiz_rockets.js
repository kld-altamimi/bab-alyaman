// snap_taiz_rockets.js - Taiz 0.9.52: the aim stick touched without a way fires straight ahead; the rocket pod locks on
// by itself (the marker closing in, then held) and a rocket sent goes after what it locked on to; the black Apache.
// Usage: node snap_taiz_rockets.js [url]
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
  const cdp = await ctx.newCDPSession(page);
  // a thumb on the aim stick, not moved: straight ahead
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 700, y: 250, id: 3 }] });
  await page.waitForTimeout(400);
  const a = await page.evaluate(() => { const s = window.__m1.sim(); return { aiming: s.heli.aiming, gunA: +s.heli.gunA.toFixed(2), shots: s.stats.shots }; });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  note(a.aiming && Math.abs(a.gunA) < 0.25 && a.shots > 4, 'a thumb on the aim stick without a way fires straight ahead (' + JSON.stringify(a) + ')');
  await page.screenshot({ path: OUT + 'taiz52_forward.png' });
  // fly on to the first fight and wait for the pod to lock on
  await page.evaluate(() => { window.__m1.sim().u = 0; });
  await page.keyboard.down('ArrowRight');
  await page.waitForFunction(() => { const h = window.__m1.sim().heli; return h.rlock && h.rlockT > 4 && h.rlockT < 20; }, null, { timeout: 30000, polling: 16 });
  await page.keyboard.up('ArrowRight');
  await page.screenshot({ path: OUT + 'taiz52_locking.png' });
  await page.waitForFunction(() => { const h = window.__m1.sim().heli; return h.rlock && h.rlockT > Sim.F.RLOCK_T; }, null, { timeout: 10000, polling: 16 });
  await page.screenshot({ path: OUT + 'taiz52_locked.png' });
  const lockId = await page.evaluate(() => window.__m1.sim().heli.rlock);
  // ROCKETS: a tap on its button
  const b = await page.evaluate(() => { const r = document.getElementById('bBomb').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
  await page.touchscreen.tap(b[0], b[1]);
  await page.waitForTimeout(120);
  const r = await page.evaluate(() => window.__m1.sim().rockets.map(q => ({ tgt: q.tgt, gone: q.gone })));
  await page.screenshot({ path: OUT + 'taiz52_rocket.png' });
  note(r.length > 0 && r.some(q => q.tgt === lockId), 'a rocket sent while locked goes after the lock (' + JSON.stringify(r) + ', lock ' + lockId + ')');
  await page.waitForFunction(id => { const s = window.__m1.sim(); const e = s.enemies.find(q => q.id === id); return !e || !e.alive; }, lockId, { timeout: 6000, polling: 16 }).then(() => note(true, 'and it gets it'), () => note(false, 'and it gets it'));
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
