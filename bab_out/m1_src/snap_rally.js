// snap_rally.js - pictures of the Spokesman's rally on the terraces' top (rally.js, 29 Oct), in the game as it runs: the
// station's fight going on, him at his podium giving statement D and his audience clapping; the station put down by hand
// and Yazeed walked up to the chairs: "Nice beret."; the jump; the dash for the pass; gone, the applause, GO.
// Usage: node snap_rally.js <url> <out dir> [en|ar]
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
  await page.evaluate(() => window.__m1.begin('ibb', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  const info = () => page.evaluate(() => {
    const s = window.__m1.sim(), r = s.rally;
    return { x: Math.round(s.p.x), cam: Math.round(s.cam), st: r && r.st, t: r && r.t, rx: r && Math.round(r.x), ry: r && Math.round(r.y),
      line: (window.__m1.line() || {}).id || null, foes: s.enemies.filter(e => e.alive && e.hostile).length };
  });
  const snap = async (name) => {
    // (he is kept from harm by a long invulnerability, which makes him blink: shown steadily for the picture)
    await page.evaluate(() => { const s = window.__m1.sim(); s.p.inv = 0; });
    await page.waitForTimeout(60);
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    await page.evaluate(() => { const s = window.__m1.sim(); s.p.inv = 99999; });
    console.log('picture', name, JSON.stringify(await info()));
  };
  // the fights before the station's put down; Yazeed brought up to the station, its men awake
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    const st = s.gates.find(g => g.id === s.L.stage.gate);
    for (const g of s.gates) {
      if (g === st || g.x > st.x) continue;
      g.done = true;
      for (const k of g.groups) { s.groups[k].done = true; s.groups[k].pending.length = 0; s.groups[k].awake = true; }
    }
    s.enemies.forEach(e => { if (e.alive && e.hostile && s.groups[e.g].done) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    s.p.x = st.x - 178; s.p.y = Sim.groundY(s.L, s.p.x); s.p.vx = 0; s.p.inv = 99999;
    s.cam = Math.min(st.x - Render.width() * 0.5, s.L.endRight - Render.width());
    window.__m1.frozen = false;
  });
  // his speech: wait for one of his lines to be the one heard, a little way into it
  await page.waitForFunction(() => { const l = window.__m1.line(); return l && l.rally; }, null, { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(900);
  await snap('rally_1_speech');
  // the clap after a line
  await page.waitForFunction(() => !window.__m1.line(), null, { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(250);
  await snap('rally_1b_clap');
  // the station put down; Yazeed walked up to the chairs
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    for (const g of ['L', 'L2']) { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
    s.enemies.forEach(e => { if (e.alive && e.hostile) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    s.bullets.length = 0; s.bombs.length = 0;
    s.p.x = s.L.stage.x0 - 64; s.p.vx = 0;
    window.__m1.frozen = false;
  });
  await page.waitForFunction(() => window.__m1.sim().rally.st === 'heard', null, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(350);
  await snap('rally_2_heard');
  await page.waitForFunction(() => { const r = window.__m1.sim().rally; return r.st === 'jump' && r.t >= 20; }, null, { timeout: 8000 }).catch(() => {});
  await snap('rally_3_jump');
  await page.waitForFunction(() => { const r = window.__m1.sim().rally; return r.st === 'run' && r.t >= 10; }, null, { timeout: 8000 }).catch(() => {});
  await snap('rally_4_run');
  await page.waitForFunction(() => window.__m1.sim().rally.st === 'gone', null, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(500);
  await snap('rally_5_gone');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
