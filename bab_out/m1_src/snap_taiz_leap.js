// snap_taiz_leap.js - men who have had enough, running for the edge of their roof and over it: the pilot flies from a
// checkpoint and the picture is taken every few steps from the first leap. Pictures to shots/leap/.
const { chromium } = require('playwright');
const fs = require('fs');
const ZONE = +(process.argv[2] || 0);
const URL = 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/leap/';
const SRC = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/unit_taiz.js', 'utf8');
const PILOT = SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)'));
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) fs.unlinkSync(OUT + f);
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(z => window.__m1.begin('taiz', z), ZONE);
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli && window.__m1.sim().heli.st === 'fly', null, { timeout: 30000 }).catch(() => {});
  if (ZONE === 0) { await page.keyboard.down('x'); await page.waitForTimeout(120); await page.keyboard.up('x'); await page.keyboard.down('ArrowRight'); await page.waitForFunction(() => window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 }); await page.keyboard.up('ArrowRight'); }
  await page.evaluate(src => { const X = Sim.ext.fly, F = Sim.F, VH = Render.height(); window.__pilot = eval('(' + src + ')')({ stick: true }); }, PILOT);
  const step = n => page.evaluate(n => {
    window.__m1.frozen = true;
    const s = window.__m1.sim(); let leap = null;
    for (let t = 0; t < n; t++) {
      const inp = window.__pilot(s); inp.viewW = Render.width(); inp.viewH = Render.height(); inp.lanes = window.__m1.geo().lanes;
      Sim.step(s, inp); if (s.events.length) Render.onEvents(s, s.events);
      for (const e of s.events) if (e.t === 'leap' && !leap) leap = e;
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: false, dim: 0 });
      if (leap) break;
    }
    return leap;
  }, n);
  const show = () => page.evaluate(() => new Promise(res => { window.__m1.frozen = false; requestAnimationFrame(() => requestAnimationFrame(() => { window.__m1.frozen = true; res(); })); }));
  let lp = null;
  for (let k = 0; k < 200 && !lp; k++) lp = await step(30);
  console.log('first leap', JSON.stringify(lp));
  for (let i = 0; i < 8; i++) { await show(); await page.screenshot({ path: OUT + 'leap_' + i + '.png' }); await step(6); }
  await browser.close();
})();
