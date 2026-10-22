// snap_taiz_end.js - Taiz's end: the launcher done, dawn coming up, the Apache brought down into the courtyard, Yazeed out.
const { chromium } = require('playwright');
const URL = 'http://127.0.0.1:8766/index.html?internal=1';
const OUT = __dirname + '/shots/';
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli.st === 'fly', null, { timeout: 15000 });
  await page.evaluate(() => {
    const s = window.__m1.sim(), L = s.L;
    for (let i = 0; i < s.gates.length; i++) { s.gates[i].done = i < s.gates.length - 1; for (const k of L.gates[i].groups) if (i < s.gates.length - 1) s.groups[k].done = true; }
    s.u = L.gates[L.gates.length - 1].u;
    for (const e of s.enemies) if (e.g === 'M') { if (e.hostile) Sim._.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; }
    for (const k of ['M']) { s.groups[k].awake = true; s.groups[k].pending.length = 0; }
    s.heli.x = 7250; s.heli.y = 230;
  });
  const out = [];
  const shot = async n => { await page.screenshot({ path: OUT + 'end_' + n + '.png' }); out.push(n + ' ' + JSON.stringify(await page.evaluate(() => { const s = window.__m1.sim(); return { e: s.ending && s.ending.st, dawn: +(s.dawn || 0).toFixed(2), heli: s.heli.st, status: s.status }; }))); };
  await page.waitForTimeout(1500); await shot('a_dawn');
  await page.waitForTimeout(3500); await shot('b_dawn');
  await page.evaluate(() => { const s = window.__m1.sim(); s.heli.x = 7350; s.heli.y = 350; });
  await page.waitForTimeout(1200); await shot('c_settle');
  await page.waitForTimeout(1400); await shot('d_out');
  await page.waitForTimeout(1500); await shot('e_clear');
  console.log(out.join('\n'));
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
