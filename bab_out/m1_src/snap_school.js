// snap_school.js - pictures of Ibb's school being let out (school.js, 29 Oct), in the game as it runs: the fights before
// it put down by hand, Yazeed put in the yard; the yard clear (padlocks, OPEN over the doors); a door opened by walking up
// to it and the class coming out; the children running for home, the first one stopped by Yazeed to wave and his line,
// his gun pointed at the ground; every class out and the teacher going after them. The game runs on its own (not stepped
// by hand) so main.js says the line; the touch input is the bot's: a few frames' walk set by hand.
// Usage: node snap_school.js <url> <out dir> [en|ar]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], LANG = process.argv[4] || 'en';
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: LANG === 'ar' ? 'ar' : 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  await page.evaluate(() => window.__m1.begin('ibb', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  const info = () => page.evaluate(() => {
    const s = window.__m1.sim(), sc = s.school;
    return { x: Math.round(s.p.x), cam: Math.round(s.cam), calm: s.calm, hush: s.hush, clear: sc && sc.clear, done: sc && sc.done,
      open: sc && sc.doors.map(d => d.open ? d.out : '-').join(','), kids: s.kids.length, wave: s.kids.filter(k => k.st === 'wave').length,
      line: (window.__m1.line() || {}).id || null, teacher: (s.props.find(o => o.k === 'detainee') || {}).st };
  });
  const snap = async (name) => {
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    console.log('picture', name, JSON.stringify(await info()));
  };
  // the fights before the school's, and the school's own, put down; the teacher freed; Yazeed in the yard, left of the first door
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    for (const g of ['E', 'E2', 'F', 'F2']) { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
    s.enemies.forEach(e => { if (e.alive && e.hostile && ['E', 'E2', 'F', 'F2'].indexOf(e.g) >= 0) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    for (const g of s.gates) if (g.id === 'alley') g.done = true;
    s.p.x = 2500; s.p.y = 184; s.p.vx = 0;
    s.cam = Math.min(2680 - Render.width() * 0.5, s.L.endRight - Render.width());
    const t = s.props.find(o => o.k === 'detainee');
    if (t) { t.st = 'freed'; t.t = 0; }
    window.__m1.frozen = false;
  });
  await page.waitForTimeout(700);
  await snap('school_1_clear');
  for (const k of ['b', 'c']) { await page.waitForTimeout(180); await snap('school_1' + k + '_clear'); }     // (OPEN blinks: one of the three has it)
  // walk up to the first door (a held right on the sim's input, for a moment)
  const walk = async (to) => {
    await page.evaluate((to) => {
      const s = window.__m1.sim();
      window.__m1.frozen = true;
      s.p.x = to; s.p.vx = 0;
      window.__m1.frozen = false;
    }, to);
  };
  await walk(2548);
  await page.waitForTimeout(450);
  await snap('school_2_open');
  await page.waitForTimeout(900);
  await snap('school_3_run');
  await page.waitForFunction(() => window.__m1.sim().kids.some(k => k.st === 'wave'), null, { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(500);
  await snap('school_4_wave');
  // the next two doors
  await page.waitForFunction(() => !window.__m1.sim().kids.length, null, { timeout: 15000 }).catch(() => {});
  await walk(2650);
  await page.waitForTimeout(1200);
  await snap('school_5_second');
  await page.waitForFunction(() => !window.__m1.sim().kids.length, null, { timeout: 15000 }).catch(() => {});
  await walk(2750);
  await page.waitForFunction(() => window.__m1.sim().school.done, null, { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(900);
  await snap('school_6_done');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
