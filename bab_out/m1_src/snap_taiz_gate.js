// snap_taiz_gate.js - the launcher coming out of the keep: everything before gate m marked done, the Apache put near the
// keep, the game stepped by hand, a picture every few steps while it is shut in, while the leaves swing in and as it rolls
// out; then the launcher killed and dawn run on, for the gate in dawn colours. Pictures to shots/gate/.
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/gate/';
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(OUT + f);
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli && window.__m1.sim().heli.st === 'fly', null, { timeout: 20000 });
  await page.evaluate(() => {
    const s = window.__m1.sim(), L = s.L;
    let gi = -1;
    for (let i = 0; i < L.gates.length; i++) if (L.gates[i].id === 'm') gi = i;
    for (let i = 0; i < gi; i++) { s.gates[i].done = true; for (const k of L.gates[i].groups) { s.groups[k].done = true; s.groups[k].pending.length = 0; s.groups[k].awake = true; } }
    for (const e of s.enemies) if (e.alive && e.hostile && e.g !== 'M') { Sim._.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; }
    s.p.inv = 99999;
  });
  // hold the Apache still a little way short of the keep, the keep in the picture
  const step = (n, tgt) => page.evaluate(([n, tgt]) => {
    window.__m1.frozen = true;
    const s = window.__m1.sim();
    for (let t = 0; t < n; t++) {
      const h = s.heli, dx = tgt[0] - h.x, dy = tgt[1] - h.y;
      const inp = { mx: 0, my: 0, ax: Math.max(-1, Math.min(1, dx / 40)), ay: Math.max(-1, Math.min(1, dy / 40)), fire: false, gun: false, jump: false, grenade: false, auto: false,
        viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes };
      Sim.step(s, inp);
      if (s.events.length) Render.onEvents(s, s.events);
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
    }
    const L = s.enemies.find(e => e.k === 'launcher');
    return { t: (s.tick / 60).toFixed(1), u: Math.round(s.u), gate: s.gateNow && s.gateNow.id, hx: Math.round(s.heli.x), hy: Math.round(s.heli.y), cam: Math.round(s.cam),
      L: L ? { st: L.st, x: Math.round(L.x), door: +(L.door || 0).toFixed(2), alive: L.alive, dieT: L.dieT } : null, dawn: +(s.dawn || 0).toFixed(2), status: s.status };
  }, [n, tgt]);
  const show = () => page.evaluate(() => new Promise(res => { window.__m1.frozen = false; requestAnimationFrame(() => requestAnimationFrame(() => { window.__m1.frozen = true; res(); })); }));
  let n = 0;
  const shot = async (tag, r) => { await show(); const nm = String(n++).padStart(2, '0') + '_' + tag + '.png'; await page.screenshot({ path: OUT + nm }); console.log(nm, JSON.stringify(r)); };
  const TGT = [7500, 180];
  let r = await step(1, TGT), k = 0;
  // fly to the keep until the launcher is there and shut in
  while (k++ < 200 && !(r.L && r.hx > 7200)) r = await step(20, TGT);
  await shot('shut', r);
  let last = '';
  for (k = 0; k < 120; k++) {
    r = await step(8, TGT);
    const tag = r.L ? r.L.st : 'none';
    if (r.L && (r.L.st === 'open' || r.L.st === 'roll' || (tag !== last && k < 100))) await shot(tag, r);
    last = tag;
    if (r.L && r.L.st !== 'hide' && r.L.st !== 'open' && r.L.st !== 'roll' && r.L.st !== 'wait') { await shot('out', r); break; }
  }
  // its missile going up; then it is killed with the missile on the rail, which cooks off
  for (k = 0; k < 150; k++) {
    r = await step(10, TGT);
    const up = await page.evaluate(() => { const L = window.__m1.sim().enemies.find(e => e.k === 'launcher'); return L ? L.raise || 0 : 0; });
    if (up > 0.8) break;
  }
  await shot('raised', r);
  await page.evaluate(() => { const s = window.__m1.sim(); for (const e of s.enemies) if (e.k === 'launcher') { Sim._.standDown(s, e); e.hp = 0; e.alive = false; } });
  for (const d of [8, 14, 14, 14, 14, 14]) { r = await step(d, TGT); await shot('dying', r); }
  // the launcher done: dawn comes up over the gate
  r = await step(30, TGT);
  // (and the men on the walls with it, so the fight is over)
  await page.evaluate(() => { const s = window.__m1.sim(); for (const e of s.enemies) if (e.alive && e.hostile && e.g === 'M') { Sim._.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; } s.groups.M.pending.length = 0; });
  for (k = 0; k < 60; k++) {
    r = await step(30, TGT);
    if (k % 6 === 5 || r.dawn >= 1) await shot('after', r);
    if (r.dawn >= 1) break;
  }
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
