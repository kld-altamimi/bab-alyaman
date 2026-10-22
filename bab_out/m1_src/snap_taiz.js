// snap_taiz.js - Taiz by Apache in a real page: started at each checkpoint with a pilot at the controls (the same as
// tools/unit_taiz.js's), pictures taken as it goes (shots/taiz_*.png), and any error on the page reported.
// Usage: node snap_taiz.js [url] [lang]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const LANG = process.argv[3] || 'en';
const OUT = __dirname + '/shots/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
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
  if (LANG !== 'en') await page.evaluate(l => window.__m1.setLang(l), LANG);
  await page.touchscreen.tap(422, 150);
  await page.evaluate(src => {
    const X = Sim.ext.fly, F = Sim.F;
    let VH = 324;                                  // (the pilot reads the picture's height in the world)
    window.__pilot = eval('(' + src + ')')({ stick: true });
    const orig = Input.sample;
    window.__pilotOn = true;
    Input.sample = function () { const s = window.__m1.sim(); if (window.__pilotOn && s && s.mode === 'fly' && s.heli) { VH = s.viewH; return window.__pilot(s); } return orig(); };
  }, PILOT);
  const shots = [];
  for (const [zone, waits] of [[0, [0.5, 3, 7, 11, 16, 22]], [1, [2, 5, 8, 12]], [2, [2, 5, 9, 13]], [3, [2, 5, 9, 14]]]) {
    await page.evaluate(z => window.__m1.begin('taiz', z), zone);
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    let t0 = Date.now();
    for (const w of waits) {
      const left = w * 1000 - (Date.now() - t0);
      if (left > 0) await sleep(left);
      const name = 'taiz_' + LANG + '_z' + zone + '_' + String(w).replace('.', '_') + 's.png';
      await page.screenshot({ path: OUT + name });
      const st = await page.evaluate(() => { const s = window.__m1.sim(); return { u: Math.round(s.u), zone: s.zone, status: s.status, heli: s.heli && s.heli.st, lives: s.p.lives, dark: +(s.dark || 0).toFixed(2), enemies: s.enemies.filter(e => e.alive && e.hostile).length, state: window.__m1.state() }; });
      shots.push(name + ' ' + JSON.stringify(st));
    }
  }
  console.log(shots.join('\n'));
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
