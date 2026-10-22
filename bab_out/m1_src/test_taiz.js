// test_taiz.js - Taiz by Apache in a real page: it is on the map and starts, the Apache flies (FLARES and ROCKETS on the
// thumbs, in English and in Arabic), the pilot bot gets through the range at full speed with the picture drawn every
// step, a lost last life continues in the air, leaving it puts the buttons back, and nothing on the page goes wrong.
// Usage: node test_taiz.js [url]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  note(await page.evaluate(() => window.__m1.levels().indexOf('taiz') >= 0), 'Taiz is in the game (' + (await page.evaluate(() => window.__m1.levels().join(', '))) + ')');
  await page.evaluate(() => window.__m1.begin('taiz', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const st = await page.evaluate(() => { const s = window.__m1.sim(); return { mode: s.mode, heli: !!s.heli, fly: document.getElementById('app').classList.contains('is-fly'),
    jump: getComputedStyle(document.getElementById('bJump'), '::after').content, bomb: getComputedStyle(document.getElementById('bBomb'), '::after').content }; });
  note(st.mode === 'fly' && st.heli, 'it starts in the Apache');
  note(st.fly && /Flares/.test(st.jump) && /Rockets/.test(st.bomb), 'the thumbs say FLARES and ROCKETS (' + st.jump + ', ' + st.bomb + ')');
  await page.evaluate(() => window.__m1.setLang('ar'));
  const ar = await page.evaluate(() => [getComputedStyle(document.getElementById('bJump'), '::after').content, getComputedStyle(document.getElementById('bBomb'), '::after').content]);
  note(/مشاعل/.test(ar[0]) && /صواريخ/.test(ar[1]), 'and in Arabic مشاعل and صواريخ (' + ar.join(', ') + ')');
  await page.evaluate(() => window.__m1.setLang('en'));
  // the aim stick, by touch: a thumb down on the right and pushed down and back points the gun that way and fires it; FIRE is
  // not there; let go, and it stops
  {
    // (a fresh start opens on foot: X skips the show, the right arrow walks Yazeed to the Apache, and once he is in it lifts
    // off and the picture draws back)
    const foot = await page.evaluate(() => { const s = window.__m1.sim(); return { intro: !!s.intro, z: Render.zoom(), w: s.viewW }; });
    note(foot.intro && foot.z === 1, 'a fresh start opens on foot in the street, at the usual size (' + JSON.stringify(foot) + ')');
    await page.waitForTimeout(400);
    await page.keyboard.down('x'); await page.waitForTimeout(120); await page.keyboard.up('x');
    await page.waitForFunction(() => window.__m1.sim().intro && window.__m1.sim().intro.st === 'wait', null, { timeout: 4000 });
    await page.keyboard.down('ArrowRight');
    await page.waitForFunction(() => window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
    await page.keyboard.up('ArrowRight');
    note(await page.evaluate(() => Render.zoom() === 1.5 && !window.__m1.sim().intro), 'X skips to the landing; walked to, the Apache takes him and the picture draws back');
    const cdp = await ctx.newCDPSession(page);
    const fireShown = await page.evaluate(() => getComputedStyle(document.getElementById('bFire')).display !== 'none' && getComputedStyle(document.getElementById('aim')).display !== 'none');
    const shots0 = await page.evaluate(() => window.__m1.sim().stats.shots);
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 700, y: 240, id: 7 }] });
    for (let k = 1; k <= 6; k++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 700 - k * 6, y: 240 + k * 6, id: 7 }] }); await page.waitForTimeout(30); }
    await page.waitForTimeout(500);
    const g = await page.evaluate(() => { const s = window.__m1.sim(); return { aiming: s.heli.aiming, gunA: +s.heli.gunA.toFixed(2), shots: s.stats.shots, firing: document.getElementById('aim').classList.contains('firing') }; });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForTimeout(200);
    const g2 = await page.evaluate(() => { const s = window.__m1.sim(); return { aiming: s.heli.aiming, on: document.getElementById('aim').classList.contains('on') }; });
    note(!fireShown, 'in the Apache the aim stick stands where FIRE was');
    note(g.aiming && g.firing && Math.abs(g.gunA - 2.36) < 0.25 && g.shots > shots0 + 4 && !g2.aiming && !g2.on, 'the aim stick points the gun down and back and fires it, and stops when let go (' + JSON.stringify(g) + ', ' + (g.shots - shots0) + ' rounds)');
  }
  // the pilot at the controls, the game stepped and drawn by hand as fast as it goes
  await page.waitForTimeout(300);                  // (a frame drawn: the picture is zoomed out for the Apache)
  const zm = await page.evaluate(() => ({ w: Render.width(), h: Render.height(), z: Render.zoom(), hud: !!Render.hudCanvas(), sw: window.__m1.sim().viewW, sh: window.__m1.sim().viewH }));
  note(zm.z === 1.5 && zm.hud && zm.h === 324 && zm.sw === zm.w && zm.sh === zm.h, 'the picture is zoomed out for the Apache, its HUD on a canvas of its own (' + JSON.stringify(zm) + ')');
  await page.evaluate(src => { const X = Sim.ext.fly, F = Sim.F, VH = Render.height(); window.__pilot = eval('(' + src + ')')({ stick: true }); }, PILOT);
  const run = await page.evaluate(() => {
    window.__m1.frozen = true;
    let s = window.__m1.sim(), ticks = 0, zones = [], lines = {};
    const t0 = performance.now();
    while (ticks < 60 * 200 && s.status !== 'clear') {
      const inp = window.__pilot(s); inp.viewW = Render.width(); inp.viewH = Render.height(); inp.lanes = window.__m1.geo().lanes;
      Sim.step(s, inp);
      if (s.events.length) Render.onEvents(s, s.events);
      for (const e of s.events) { if (e.t === 'checkpoint') zones.push(e.zone); lines[e.t] = (lines[e.t] || 0) + 1; }
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
      if (s.status === 'over') s = Sim.continueZone(s, Render.width());
      ticks++;
    }
    const ms = performance.now() - t0;
    window.__m1.frozen = false;
    return { status: s.status, ticks, zones, ms: Math.round(ms), qanya: lines.qanya || 0, scatter: lines.scatter || 0, launches: lines.sam_launch || 0 };
  });
  note(run.status === 'clear', 'the pilot gets through the range (' + (run.ticks / 60).toFixed(0) + ' s of play, checkpoints ' + run.zones.join(', ') + ', «قنية سودا» ' + run.qanya + ' times, ' + run.scatter + ' ran for it, ' + run.launches + ' missiles)');
  note(run.ms / run.ticks < 8, 'a step and a picture take ' + (run.ms / run.ticks).toFixed(2) + ' ms here (the drawing is not heavy)');
  // a last life lost continues in the air
  await page.evaluate(() => window.__m1.begin('taiz', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.evaluate(() => { const s = window.__m1.sim(); s.p.lives = 1; s.p.plates = 1; s.p.inv = 0; Sim._.hurtPlayer(s, s.p.x, 'test'); });
  await page.waitForFunction(() => window.__m1.state() === 'over', null, { timeout: 15000 });
  await page.click('#bContinue');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const c = await page.evaluate(() => { const s = window.__m1.sim(); return { mode: s.mode, zone: s.zone, fly: document.getElementById('app').classList.contains('is-fly') }; });
  note(c.mode === 'fly' && c.zone === 2 && c.fly, 'a continue goes on in the air from the castle road');
  await page.evaluate(() => { window.__m1.pause(); });
  await page.evaluate(() => window.__m1.toMap());
  await page.waitForTimeout(800);
  note(await page.evaluate(() => !document.getElementById('app').classList.contains('is-fly')), 'back on the map, the buttons are themselves again');
  const back = await page.evaluate(() => ({ z: Render.zoom(), w: Render.width(), h: Render.height(), hud: !!Render.hudCanvas() }));
  note(back.z === 1 && back.h === 216 && !back.hud, 'and the picture is its usual size again (' + JSON.stringify(back) + ')');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
