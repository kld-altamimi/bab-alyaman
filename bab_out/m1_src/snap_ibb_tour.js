// snap_ibb_tour.js - pictures along Ibb as the game draws it (29 Oct: the zones half as long again, painted as one): for
// each x given, every fight before it put down by hand, Yazeed set down there, the camera brought up, a picture. With
// --live the fights at x are left awake (their posted men in the picture).
// Usage: node snap_ibb_tour.js <url> <out dir> <x> [<x> ...] [--live] [--ar]
const { chromium } = require('playwright');
const fs = require('fs');
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const URL = args[0], OUT = args[1], XS = args.slice(2).map(Number);
const LIVE = process.argv.includes('--live'), LANG = process.argv.includes('--ar') ? 'ar' : 'en';
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
  for (const x of XS) {
    const zone = await page.evaluate((x) => { const L = (window.__m1.levels ? null : null); return 0; }, x);
    await page.evaluate(() => window.__m1.begin('ibb', 0));
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await page.waitForTimeout(300);
    await page.evaluate(({ x, live }) => {
      const s = window.__m1.sim(), L = s.L, W = Render.width();
      window.__m1.frozen = true;
      for (const g of s.gates) {
        const before = g.x < x + (live ? -40 : W * 0.5 + 30);
        if (!before) continue;
        g.done = true;
        for (const k of g.groups) { const G = s.groups[k]; G.done = true; G.pending.length = 0; G.awake = true; }
      }
      s.enemies.forEach(e => { if (e.alive && s.groups[e.g] && s.groups[e.g].done) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
      if (s.school && s.gates.find(g => g.id === 'school').done) s.school.done = true;
      if (s.rally && s.gates.find(g => g.id === 'station').done) s.rally.st = 'gone';
      for (const pr of s.props) if (pr.k === 'detainee' && pr.x < x) { pr.st = 'freed'; pr.t = 0; }
      s.p.x = x; s.p.y = Sim.groundY(L, x); s.p.vx = 0; s.p.inv = 99999; s.p.plat = -1; s.p.air = false;
      let gate = s.gates.find(g => !g.done);
      const max = gate ? Math.min(gate.x - W * 0.5, L.endRight - W) : L.endRight - W;
      s.cam = Math.max(0, Math.min(x - W * 0.35, max));
      s.zone = 0; for (let z = 0; z < L.zones.length; z++) if (x >= L.zones[z].x) s.zone = z;
      window.__m1.frozen = false;
    }, { x, live: LIVE });
    await page.waitForTimeout(LIVE ? 900 : 500);
    await page.evaluate(() => { window.__m1.sim().p.inv = 0; });
    await page.waitForTimeout(60);
    await page.screenshot({ path: OUT + '/tour_' + x + '.png' });
    const info = await page.evaluate(() => { const s = window.__m1.sim(); return { x: Math.round(s.p.x), cam: Math.round(s.cam), zone: s.zone, foes: s.enemies.filter(e => e.alive && e.hostile).length }; });
    console.log('picture', x, JSON.stringify(info));
  }
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
