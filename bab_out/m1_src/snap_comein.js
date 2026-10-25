// snap_comein.js - pictures of men coming in shooting (25 Oct: no guard at the edges; a rifleman fires one round as he
// steps in, a bomber comes in with his stick lit): the Strait from its start, stepped by hand (frozen) with Yazeed walking
// on and firing, a picture the moment a rifleman's entry round is fired and one when a bomber comes in lit; and the page's
// errors. Usage: node snap_comein.js <url> <out dir> [mission] [zone]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], MIS = process.argv[4] || 'm1', ZONE = +(process.argv[5] || 0);
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(([m, z]) => window.__m1.begin(m, z), [MIS, ZONE]);
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  // step until cond(s) holds (Yazeed walking on, firing ahead), then draw
  const run = (cond, n) => page.evaluate(([c, n]) => {
    window.__m1.frozen = true;
    const cond = eval('(' + c + ')');
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      const mx = 1;
      Sim.step(s, { mx: mx, my: 0, fire: (t >> 3) % 3 !== 0, viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes });
      if (s.events.length) Render.onEvents(s, s.events);
      s.p.inv = Math.max(s.p.inv, 2);
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: window.__m1.line(), overlay: false, caps: true, noHud: false, dim: 0 });
      if (cond(s)) break;
    }
    return { t, x: Math.round(s.p.x), cam: Math.round(s.cam) };
  }, [cond.toString(), n]);
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(30);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    console.log('picture', name);
  };
  let r = await run(s => s.enemies.some(e => e.k === 'rifle' && e.snapT === 2), 60 * 60);
  console.log('rifleman in shooting after', r.t, 'ticks', JSON.stringify(r));
  await snap('comein_rifle');
  r = await run(s => s.enemies.some(e => e.k === 'bomber' && e.st === 'wind' && e.alive && !Sim.staged(s, e)), 60 * 120);
  console.log('bomber in lit after', r.t, 'ticks', JSON.stringify(r));
  await snap('comein_bomber');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
