// snap_captives.js - pictures of Taiz's three captives (22 Oct, Khaled: "there aren't any hostages to save in Taiz"; he chose
// a rescue from the air): the first one on his roof by his lantern, the hint, the rope coming down as the Apache holds over
// him, him going up it, the FREED count, each of the other two, the hint in Arabic, and the end in the courtyard with the
// three of them out after Yazeed. The game is stepped by hand with the pilot bot (which goes for them), then left to draw a
// frame for each picture.
// Usage: node snap_captives.js [url] [out dir]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8792/index.html?internal=1';
const OUT = process.argv[3] || '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/hostages/snaps';
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
  const begin = async (zone, opt) => {
    await page.evaluate(z => window.__m1.begin('taiz', z), zone);
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await page.waitForTimeout(400);
    await page.evaluate(([src, o]) => { const X = Sim.ext.fly, F = Sim.F, VH = Render.height(); window.__pilot = eval('(' + src + ')')(o); }, [PILOT, opt || { stick: true }]);
  };
  // step by hand (the pilot flying) until cond(s) holds, or n ticks; poke(s) runs after each step; quiet: no shooting
  const run = (cond, n, poke, quiet) => page.evaluate(([c, n, p, q]) => {
    window.__m1.frozen = true;
    const cond = eval('(' + c + ')'), poke = p ? eval('(' + p + ')') : null;
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      if (cond && cond(s)) break;
      if (s.intro) { const inp = { mx: 1, viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes }; Sim.step(s, inp); }
      else {
        const inp = window.__pilot(s); inp.viewW = Render.width(); inp.viewH = Render.height(); inp.lanes = window.__m1.geo().lanes;
        if (q) { inp.fire = false; inp.gun = false; inp.grenade = false; }
        Sim.step(s, inp);
      }
      if (s.events.length) Render.onEvents(s, s.events);
      if (poke) poke(s);
      s.p.inv = Math.max(s.p.inv, 2);             // (the pictures are of the rescue: no Apache lost on the way)
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
    }
    return t;
  }, [cond ? cond.toString() : 'null', n, poke ? poke.toString() : null, !!quiet]);
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(60);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    console.log('picture', name);
  };
  const cap = (i) => `s => { const o = s.props.filter(q => q.k === 'detainee')[${i}]; return o; }`;

  // ---- from the start: the opening, lift-off, the first fight, and the first of them
  await begin(0);
  await run(s => !s.intro, 60 * 30);
  // (the game itself sets the Apache's picture size once the opening is over: let it run a moment to do that)
  await page.evaluate(() => { window.__m1.frozen = false; });
  await page.waitForTimeout(700);
  console.log('picture after the opening:', await page.evaluate(() => { const s = window.__m1.sim(); return s.viewW + 'x' + s.viewH + ' (canvas ' + Render.width() + 'x' + Render.height() + ')'; }));
  let t = await run(s => !s.intro && s.props.some(q => q.k === 'detainee' && q.seen), 60 * 90);
  console.log('first in sight after', (t / 60).toFixed(1), 's');
  await run(null, 30, null, true);
  await page.evaluate(() => Render.setHint(T('Somebody is tied up on that roof! Hover low over him to lift him out'), 200));
  await snap('c1_seen');
  await run(s => s.props.some(q => q.k === 'detainee' && q.rope > 0.45), 60 * 30);
  await snap('c1_rope');
  await run(s => s.props.some(q => q.k === 'detainee' && q.st === 'lift' && q.t >= 14), 60 * 10);
  await snap('c1_lift');
  await run(null, 30);
  await snap('c1_after');
  // ---- the second, by the old city's gate
  t = await run(s => s.props.some(q => q.k === 'detainee' && q.st === 'tied' && q.rope > 0.6), 60 * 120);
  console.log('second: rope down after', (t / 60).toFixed(1), 's more; freed', await page.evaluate(() => window.__m1.sim().stats.freed));
  await snap('c2_rope');
  // ---- the third, in the village
  t = await run(s => s.stats.freed >= 2 && s.props.some(q => q.k === 'detainee' && q.st === 'tied' && Sim.ext.fly.inView(s, q.x, q.y - 30, -20)), 60 * 150);
  await run(null, 20);
  await page.evaluate(() => window.__m1.setLang('ar'));
  await page.evaluate(() => Render.setHint(T('Somebody is tied up on that roof! Hover low over him to lift him out'), 200));
  await run(null, 2);
  await snap('c3_seen_ar');
  await page.evaluate(() => window.__m1.setLang('en'));
  await run(s => s.stats.freed >= 3, 60 * 40);
  await run(null, 8);
  await snap('c3_freed');
  // ---- on to the end: the courtyard at dawn, the three out after Yazeed
  t = await run(s => s.ending && s.ending.st === 'out' && s.ending.t2 > 330, 60 * 240);
  console.log('to the landing after', (t / 60).toFixed(1), 's more; freed', await page.evaluate(() => window.__m1.sim().stats.freed + ' of ' + window.__m1.sim().stats.detainees));
  await snap('end_out');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
