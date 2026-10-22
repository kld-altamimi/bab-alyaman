// snap_taiz_stage.js - Taiz: a fight set up directly (the camera at a fight, the fights before it done, its groups awake,
// the Apache placed), a moment's play, and a picture. Usage: node snap_taiz_stage.js gateId heliX heliY tag [setup-js]
const { chromium } = require('playwright');
const URL = 'http://127.0.0.1:8766/index.html?internal=1';
const [GATE, HX, HY, TAG, SETUP, WAIT] = [process.argv[2] || 'd', +process.argv[3], +process.argv[4], process.argv[5] || 'stage', process.argv[6] || '', +(process.argv[7] || 700)];
const OUT = __dirname + '/shots/';
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(g => { const L = window.__m1.levels ? null : null; const lv = LEVEL_TAIZ, gt = lv.gates.find(q => q.id === g); window.__m1.begin('taiz', lv.groups[gt.groups[0]].zone); }, GATE);
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
  const info = await page.evaluate(([g, hx, hy, setup]) => {
    const s = window.__m1.sim(), L = s.L;
    // start again at the fight: everything before it done
    let gi = L.gates.findIndex(q => q.id === g);
    for (let i = 0; i < s.gates.length; i++) {
      if (i < gi) { s.gates[i].done = true; for (const k of L.gates[i].groups) s.groups[k].done = true; }
      else { s.gates[i].done = false; }
    }
    s.u = L.gates[gi].u; s.zone = Math.max(0, L.zones.findIndex((z, k) => k + 1 >= L.zones.length || L.zones[k + 1].u > s.u));
    for (const k of L.gates[gi].groups) { const G = s.groups[k]; G.done = false; G.awake = true; G.awakeT = 0; G.afterT = -1; }
    // the men of the fight that the start of the mission placed are still where they were; (the later ones arrive as they are woken)
    s.heli.x = hx; s.heli.y = hy; s.heli.vx = 0; s.heli.vy = 0; s.p.x = hx; s.p.y = hy;
    if (setup) eval(setup);
    return { u: s.u, gates: s.gates.filter(q => !q.done).map(q => q.id).slice(0, 2) };
  }, [GATE, HX, HY, SETUP]);
  await page.waitForTimeout(WAIT);
  await page.screenshot({ path: OUT + 'stage_' + TAG + '.png' });
  const st = await page.evaluate(() => { const s = window.__m1.sim(); return s.enemies.filter(e => e.alive && e.hostile && Sim.ext.fly.inView(s, e.x, e.y, 0)).map(e => e.k + ':' + e.st).join(' '); });
  console.log(TAG, JSON.stringify(info), st);
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
