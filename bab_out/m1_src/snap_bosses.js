// snap_bosses.js - pictures of Taiz's reworked end (22 Oct, Khaled's play-test): the Castle Gun warning of its sweep and
// cooling after it; the Launcher's count, the crew losing count and putting time back, nought, and the missile getting
// away; men giving up with a white vest or a sign; a crate's label and its first drone going the wrong way; the chase's
// pickups with a sofa and a goat. The game is stepped by hand with the pilot bot, then left to draw a frame for each picture.
// Usage: node snap_bosses.js [url] [out dir]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8792/index.html?internal=1';
const OUT = process.argv[3] || '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/bosses/snaps';
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  const begin = async (zone) => {
    await page.evaluate(z => window.__m1.begin('taiz', z), zone);
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await page.waitForTimeout(400);
    await page.evaluate(src => { const X = Sim.ext.fly, F = Sim.F, VH = Render.height(); window.__pilot = eval('(' + src + ')')({ stick: true }); }, PILOT);
  };
  // step by hand (the pilot flying) until cond(s) holds, or n ticks; poke(s) runs after each step
  const run = (cond, n, poke, quiet) => page.evaluate(([c, n, p, q]) => {
    window.__m1.frozen = true;
    const cond = eval('(' + c + ')'), poke = p ? eval('(' + p + ')') : null;
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      if (cond && cond(s)) break;
      const inp = window.__pilot(s); inp.viewW = Render.width(); inp.viewH = Render.height(); inp.lanes = window.__m1.geo().lanes;
      if (q) { inp.fire = false; inp.gun = false; inp.grenade = false; }
      Sim.step(s, inp);
      if (s.events.length) Render.onEvents(s, s.events);
      if (poke) poke(s);
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
    }
    return t;
  }, [cond ? cond.toString() : 'null', n, poke ? poke.toString() : null, !!quiet]);
  // let the page draw (and show) a frame of its own, then take the picture
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(60);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    console.log('picture', name);
  };

  // ---- the castle: the Castle Gun
  await begin(3);
  const t1 = await run(s => s.enemies.some(e => e.k === 'cgun' && e.alive && e.st === 'track' && !e.hidden), 60 * 120);
  console.log('to the Castle Gun:', (t1 / 60).toFixed(1), 's');
  await run(null, 1, s => { const g = s.enemies.find(e => e.k === 'cgun'); const h = s.heli; g.plan = []; g.st = 'sweep'; g.stT = 0; g.shots = 0; g.sweepDir = h.x < g.x ? -1 : 1; g.sweepFrom = g.sweepDir > 0 ? -Math.PI + Sim.BG.CG_LOW : -Sim.BG.CG_LOW; });
  await run(null, 26, null, true);
  await snap('cg_sweep_warning');
  await run(s => { const g = s.enemies.find(e => e.k === 'cgun'); return g.st === 'cool' && g.stT > 24; }, 400, null, true);
  await snap('cg_cooling');
  // men giving up: three more of them on the walls, all with their hands up (the pilot not shooting)
  await run(null, 1, s => { const L = s.L; for (const [x, look] of [[6700, 'angry'], [6745, 'qat'], [7030, 'youth'], [7075, 'worried']]) { const e = Sim._.spawnEnemy(s, { g: 'K', k: 'rifle', post: 1, look: look, plat: x < 6900 ? 'c_6610' : 'c_7000' }, x); e.ext = 'fly'; e.air = false; e.px = e.x; e.py = e.y; e.u = 0; } for (const e of s.enemies) if (e.alive && e.k === 'rifle' && Sim.ext.fly.inView(s, e.x, e.y, 0)) { e.st = 'panic'; e.stT = 0; e.face = e.x < s.heli.x ? -1 : 1; e.lit = false; Sim._.standDown(s, e); } }, true);
  await run(null, 14, null, true);
  await snap('giving_up');
  // on to the keep: the Launcher and its count
  const t2 = await run(s => s.enemies.some(e => e.k === 'launcher' && e.alive && e.st === 'count' && e.clock < Sim.BG.LN_CLOCK - 150), 60 * 150);
  console.log('to the Launcher\'s count:', (t2 / 60).toFixed(1), 's');
  await snap('ln_count');
  await page.evaluate(() => window.__m1.setLang('ar'));
  await run(null, 2);
  await snap('ln_count_ar');
  await page.evaluate(() => window.__m1.setLang('en'));
  // (the gun held off it, so the count runs down)
  const hold = s => { for (const e of s.enemies) if (e.k === 'launcher') e.hp = Math.max(e.hp, 300); };
  await run(null, 1, s => { const L = s.enemies.find(e => e.k === 'launcher'); L.clock = Sim.BG.LN_RECOUNT_AT + 20; });
  await run(s => { const L = s.enemies.find(e => e.k === 'launcher'); return L.argue > 0 && L.argue < Sim.BG.LN_ARGUE - 40; }, 300, hold);
  await snap('ln_lost_count');
  await run(s => { const L = s.enemies.find(e => e.k === 'launcher'); return L.recounted && !L.argue; }, 300, hold);
  await run(null, 12, hold);
  await snap('ln_recount');
  await run(null, 1, s => { const L = s.enemies.find(e => e.k === 'launcher'); L.clock = 40; });
  await run(s => { const L = s.enemies.find(e => e.k === 'launcher'); return L.st === 'ignite' && L.stT > 40; }, 300, hold);
  await snap('ln_ignition');
  await run(s => s.lost && s.lost.t > 50, 600, hold);
  await snap('ln_got_away');

  // ---- a crate, its label, its first drone the wrong way (the walls' crate, made to go wrong for the picture)
  await begin(3);
  await run(s => s.enemies.some(e => e.k === 'crate' && e.alive && Sim.ext.fly.inView(s, e.x, e.y, -20)), 60 * 60);
  await run(null, 1, s => { const c = s.enemies.find(e => e.k === 'crate' && e.alive); c.oops = true; c.oopsed = false; c.st = 'open'; c.stT = 0; });
  await run(s => s.enemies.some(e => e.k === 'drone' && e.st === 'oops' && e.stT > 26), 200, null, true);
  await snap('crate_oops');

  // ---- the chase: the pickups' loads
  await begin(2);
  await run(s => s.enemies.filter(e => e.k === 'truck' && e.alive && e.st === 'drive' && Sim.ext.fly.inView(s, e.x, e.y, 0)).length >= 2, 60 * 60, null, true);
  await run(null, 90, null, true);
  await snap('chase_loads');

  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
