// snap_ibb.js - pictures of Ibb's test range (stage 2 of its plan): the billboard at the start, and each shop's set with
// the men by it. The game is stepped by hand (frozen) and drawn for each picture; Yazeed comes to no harm, and the men
// of each fight already passed are put down by hand to get on. Usage: node snap_ibb.js <url> <out dir> [en|ar]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], LANG = process.argv[4] || 'en';
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: LANG === 'ar' ? 'ar' : 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  await page.evaluate(() => window.__m1.begin('ibb', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  const run = (cond, n, mx) => page.evaluate(([c, n, mx]) => {
    window.__m1.frozen = true;
    const cond = c ? eval('(' + c + ')') : null;
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      if (cond && cond(s)) break;
      Sim.step(s, { mx: mx, my: 0, viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes });
      if (s.events.length) Render.onEvents(s, s.events);
      s.p.inv = Math.max(s.p.inv, 2);
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: window.__m1.line(), overlay: false, caps: true, noHud: false, dim: 0 });
    }
    return t;
  }, [cond ? cond.toString() : null, n, mx]);
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(40);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    console.log('picture', name, JSON.stringify(await page.evaluate(() => { const s = window.__m1.sim(); return { x: Math.round(s.p.x), zone: s.zone, men: s.enemies.filter(e => e.alive).length }; })));
  };
  const down = (gs) => page.evaluate((gs) => { const s = window.__m1.sim(); s.enemies.forEach(e => { if (e.alive && e.hostile && gs.indexOf(e.g) >= 0) Sim._.killEnemy(s, e, 1, 'shot'); }); gs.forEach(g => s.groups[g].pending.length = 0); }, gs);
  await run(null, 150, 0); await snap('i1_billboard');
  for (const [gs, x, name] of [[['A', 'B'], 960, 'i2_stall_set'], [['C'], 1250, 'i3_warehouse_set'], [['D'], 1880, 'i4_gallery_set'], [['E'], 2200, 'i5_last_set']]) {
    await down(gs);
    await run('s => s.p.x >= ' + x, 60 * 14, 1);
    await run(null, 90, 0);
    await snap(name);
  }
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
