// snap_taiz_lock.js - Taiz: a missile man's lock-on as it looks and as the thumbs show it: FLARES! on the beat, the FLARES
// button pulsing, the lock line from his parapet; then flares dropped and the missile going after them.
// Usage: node snap_taiz_lock.js [url]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/';
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(src => {
    const X = Sim.ext.fly, F = Sim.F;
    let VH = 324;
    window.__pilot = eval('(' + src + ')')({ stick: true, noFlares: true });
    const orig = Input.sample;
    window.__drop = false;
    Input.sample = function () { const s = window.__m1.sim(); if (s && s.mode === 'fly' && s.heli) { VH = s.viewH; const o = window.__pilot(s); if (window.__drop) { o.jump = true; window.__drop = false; } return o; } return orig(); };
  }, PILOT);
  await page.evaluate(() => window.__m1.begin('taiz', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  // the first lock-on
  await page.waitForFunction(() => { const s = window.__m1.sim(); return s && s.locking && s.lockT > 26; }, null, { timeout: 60000, polling: 16 });
  await page.screenshot({ path: OUT + 'taiz_lock_beat.png' });
  const a = await page.evaluate(() => ({ alert: document.getElementById('bJump').classList.contains('alert'), lockT: window.__m1.sim().lockT, st: window.__m1.sim().enemies.find(e => e.id === window.__m1.sim().locking).st }));
  note(a.alert && a.st === 'lock', 'a lock-on: the FLARES button pulses, the man is down behind his parapet (' + JSON.stringify(a) + ')');
  await page.waitForFunction(() => { const s = window.__m1.sim(); return s && s.locking && s.lockT >= Sim.F.SAM_LOCK - Sim.F.SAM_SOLID + 4; }, null, { timeout: 10000, polling: 16 });
  await page.screenshot({ path: OUT + 'taiz_lock_tone.png' });
  const b = await page.evaluate(() => ({ st: window.__m1.sim().enemies.find(e => e.id === window.__m1.sim().locking).st }));
  note(b.st === 'aim', 'the long tone: up with the launcher (' + JSON.stringify(b) + ')');
  await page.evaluate(() => { window.__drop = true; });
  await page.waitForFunction(() => { const s = window.__m1.sim(); return s && s.missiles.length > 0; }, null, { timeout: 10000, polling: 16 });
  await page.waitForTimeout(250);
  await page.screenshot({ path: OUT + 'taiz_lock_flares.png' });
  const c = await page.evaluate(() => ({ decoy: window.__m1.sim().missiles.map(q => q.decoy), alert: document.getElementById('bJump').classList.contains('alert') }));
  note(c.decoy.length && c.decoy.every(Boolean) && !c.alert, 'flares dropped in the long tone: the missile goes after them, the button stops pulsing (' + JSON.stringify(c) + ')');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
