// snap_taiz_foes.js - Taiz's enemies in a real page: from a checkpoint, the pilot flying but holding its fire (so they act),
// pictures at given moments. Usage: node snap_taiz_foes.js zone seconds,seconds,... [tag]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = 'http://127.0.0.1:8766/index.html?internal=1';
const ZONE = +process.argv[2] || 0, WAITS = (process.argv[3] || '3,6,9').split(',').map(Number), TAG = process.argv[4] || 'z' + ZONE, HOLD_U = +(process.argv[5] || 0);
const OUT = __dirname + '/shots/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(src => {
    const X = Sim.ext.fly, F = Sim.F; let VH = 324;
    window.__pilot = eval('(' + src + ')')({ stick: true });
    const orig = Input.sample;
    Input.sample = function () { const s = window.__m1.sim(); if (s && s.intro) return { mx: 1, ax: 1, jump: s.intro.st === 'show' && s.intro.t % 20 === 15 }; if (s && s.mode === 'fly' && s.heli && s.heli.st === 'fly') { VH = s.viewH; const o = window.__pilot(s); if (window.__hold && s.u >= window.__holdU) { o.gun = false; o.fire = false; o.grenade = false; } return o; } return orig(); };
  }, PILOT);
  await page.evaluate(u => { window.__hold = true; window.__holdU = u; }, HOLD_U);
  await page.evaluate(z => window.__m1.begin('taiz', z), ZONE);
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const t0 = Date.now(), out = [];
  for (const w of WAITS) {
    const left = w * 1000 - (Date.now() - t0); if (left > 0) await sleep(left);
    const name = 'foe_' + TAG + '_' + String(w).replace('.', '_') + 's.png';
    await page.screenshot({ path: OUT + name });
    const st = await page.evaluate(() => { const s = window.__m1.sim(); return { u: Math.round(s.u), hold: s.holdU && Math.round(s.holdU), chase: s.chaseOn, spot: s.spotT, kinds: s.enemies.filter(e => e.alive && e.hostile).map(e => e.k + ':' + e.st).join(' ') }; });
    out.push(name + ' ' + JSON.stringify(st));
  }
  console.log(out.join('\n'));
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
