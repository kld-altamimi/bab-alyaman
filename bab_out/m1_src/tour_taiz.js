// tour_taiz.js - a picture of Taiz every couple of seconds of play, from the opening to the courtyard, flown by the unit
// test's pilot (stick) with the game stepped and drawn by hand, for looking the whole level over. Pictures to shots/tour/.
// Usage: node tour_taiz.js [every-ticks] [url] [zone] [max-pictures] (from a later zone there is no opening)
const { chromium } = require('playwright');
const fs = require('fs');
const EVERY = +(process.argv[2] || 150);
const URL = process.argv[3] || 'http://127.0.0.1:8766/index.html?internal=1';
const ZONE = +(process.argv[4] || 0), MAX = +(process.argv[5] || 120);
const OUT = __dirname + '/shots/tour/';
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) if (/\.(png|txt)$/.test(f)) fs.unlinkSync(OUT + f);
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(z => window.__m1.begin('taiz', z), ZONE);
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  let n = 0;
  const shot = async tag => { const nm = String(n++).padStart(3, '0') + '_' + tag + '.png'; await page.screenshot({ path: OUT + nm }); return nm; };
  if (ZONE > 0) await page.waitForFunction(() => window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
  else {
  await page.waitForTimeout(1200); await shot('open_arrive');
  await page.waitForTimeout(1500); await shot('open_scare');
  await page.keyboard.down('x'); await page.waitForTimeout(120); await page.keyboard.up('x');
  await page.waitForFunction(() => window.__m1.sim().intro && window.__m1.sim().intro.st === 'wait', null, { timeout: 6000 }).catch(() => {});
  await shot('open_wait');
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(900); await shot('open_walk');
  await page.waitForFunction(() => window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
  await page.keyboard.up('ArrowRight');
  await page.waitForTimeout(400); await shot('open_fly');
  }
  await page.evaluate(src => { const X = Sim.ext.fly, F = Sim.F, VH = Render.height(); window.__pilot = eval('(' + src + ')')({ stick: true }); }, PILOT);
  const log = [];
  for (let k = 0; k < MAX; k++) {
    const r = await page.evaluate(every => {
      window.__m1.frozen = true;
      let s = window.__m1.sim(), ev = {};
      for (let t = 0; t < every && s.status !== 'clear'; t++) {
        const inp = window.__pilot(s); inp.viewW = Render.width(); inp.viewH = Render.height(); inp.lanes = window.__m1.geo().lanes;
        Sim.step(s, inp);
        if (s.events.length) Render.onEvents(s, s.events);
        for (const e of s.events) if (['checkpoint', 'life_lost', 'boss_intro', 'boss_dead', 'chase', 'dawn', 'touchdown', 'clear', 'failsafe', 'go'].indexOf(e.t) >= 0) ev[e.t + (e.gate ? ':' + e.gate : '') + (e.k ? ':' + e.k : '') + (e.why ? ':' + e.why : '')] = 1;
        Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
        if (s.status === 'over') s = Sim.continueZone(s, Render.width());
      }
      return { t: (s.tick / 60).toFixed(1), zone: s.zone, u: Math.round(s.u), gate: s.gateNow && s.gateNow.id, hx: Math.round(s.heli.x), hy: Math.round(s.heli.y), status: s.status, ev: Object.keys(ev).join(' ') };
    }, EVERY);
    // (the frame is drawn to the small canvas; the page puts it on the screen in its own loop, so let one frame through)
    await page.evaluate(() => new Promise(res => { window.__m1.frozen = false; requestAnimationFrame(() => requestAnimationFrame(() => { window.__m1.frozen = true; res(); })); }));
    const nm = await shot('z' + r.zone + (r.gate ? '_' + r.gate : ''));
    log.push(nm + ' ' + JSON.stringify(r));
    if (r.status === 'clear') { for (let j = 0; j < 3; j++) { await page.evaluate(() => { window.__m1.frozen = false; }); await page.waitForTimeout(1200); await shot('clear'); } break; }
  }
  await page.evaluate(() => { window.__m1.frozen = false; });
  fs.writeFileSync(OUT + 'log.txt', log.join('\n') + '\n');
  console.log(log.join('\n'));
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
