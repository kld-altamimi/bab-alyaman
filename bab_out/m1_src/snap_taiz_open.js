// snap_taiz_open.js - the opening, frame by frame through the lift-off and the picture drawing back, to compare its
// backdrop with the flight's. Pictures to shots/intro/.
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/intro/';
(async () => {
  for (const f of fs.readdirSync(OUT)) if (/\.png$/.test(f)) fs.unlinkSync(OUT + f);
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  let n = 0;
  const st = () => page.evaluate(() => { const s = window.__m1.sim(); return { intro: s.intro && s.intro.st, heli: s.heli && s.heli.st, zoom: +(s.zoom || 1).toFixed(2), cam: Math.round(s.cam), camY: Math.round(s.camY), vw: s.viewW, vh: s.viewH }; });
  const shot = async tag => { const nm = String(n++).padStart(2, '0') + '_' + tag + '.png'; await page.screenshot({ path: OUT + nm }); console.log(nm, JSON.stringify(await st())); };
  await page.waitForTimeout(600); await shot('start');
  await page.waitForTimeout(1800); await shot('arrive');
  await page.keyboard.down('x'); await page.waitForTimeout(120); await page.keyboard.up('x');
  await page.waitForTimeout(500); await shot('landed');
  await page.keyboard.down('ArrowRight');
  for (let i = 0; i < 16; i++) { await page.waitForTimeout(350); await shot('t' + i); }
  await page.keyboard.up('ArrowRight');
  for (let i = 0; i < 4; i++) { await page.waitForTimeout(600); await shot('fly' + i); }
  console.log(errors.length ? 'ERRORS ' + errors.join(' | ') : 'no errors');
  await browser.close();
})();
