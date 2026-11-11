// snap_dhamar.js - pictures of Dhamar's test build (zones 1-3, 11 Nov) as the game runs it in a browser: the highway on
// wheels (the convoy, a checkpoint, its barrier, the notes), the city (the recruiting office, its doors, the Leader's
// screen, the poster, the teacher as sergeant, the children out with Yazeed's gun down), the gas torch on some of their
// men, and the vote at Hammam Ali (him talking, the laugh, Yazeed's word, the motion denied, the gathering drafted).
// Usage: node snap_dhamar.js <url> <out dir> [en|ar]
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
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  const info = () => page.evaluate(() => {
    const s = window.__m1.sim();
    return { zone: s.zone, x: Math.round(s.p.x), cam: Math.round(s.cam), mode: s.mode, car: s.car && s.car.st, cx: s.car && Math.round(s.car.x), line: (window.__m1.line() || {}).id || null,
      cps: s.dham && s.dham.cps.map(c => c.st).join(','), notes: s.dham && s.dham.notes.length, wages: s.stats.wages, rally: s.rally && s.rally.st, weapon: s.p.weapon, kids: s.kids && s.kids.length, status: s.status };
  });
  const snap = async (name) => { await page.screenshot({ path: OUT + '/' + name + '.png' }); console.log('picture', name, JSON.stringify(await info())); };
  const god = () => page.evaluate(() => { const s = window.__m1.sim(); s.p.plates = 99; s.p.lives = 9; });
  // ---- zone 1, on wheels
  await page.evaluate(() => window.__m1.begin('dhamar', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 20000 });
  await god();
  await page.waitForTimeout(2200); await snap('d1_start');
  await page.waitForFunction(() => { const s = window.__m1.sim(); return s.dham && s.dham.cps[0].st === 'laugh'; }, null, { timeout: 20000 });
  await page.waitForTimeout(500); await snap('d1_checkpoint');
  await page.waitForTimeout(700); await snap('d1_checkpoint_b');
  await page.waitForFunction(() => { const s = window.__m1.sim(); return s.props.some(o => o.k === 'barrier' && o.st === 'broken'); }, null, { timeout: 20000 });
  await page.waitForTimeout(150); await snap('d1_barrier');
  // ---- zone 2, the city
  await page.evaluate(() => window.__m1.begin('dhamar', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 20000 });
  await god();
  await page.waitForTimeout(1500); await snap('d2_gate');
  // the fights up to the school put down; Yazeed in the yard
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    const gs = ['G', 'G2', 'S', 'S2', 'A', 'A2', 'F', 'F2'];
    for (const g of gs) { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
    s.enemies.forEach(e => { if (e.alive && e.hostile && gs.indexOf(e.g) >= 0) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    for (const g of s.gates) if (['gatefight', 'souq', 'alley'].indexOf(g.id) >= 0) g.done = true;
    s.p.x = 7470; s.p.y = 184; s.p.vx = 0; s.p.plat = -1;
    s.cam = Math.min(7560 - s.viewW * 0.5, s.L.endRight - s.viewW);
    window.__m1.frozen = false;
  });
  await page.waitForTimeout(900); await snap('d2_office');
  await page.evaluate(() => { const s = window.__m1.sim(); s.p.x = 7520; });
  await page.waitForTimeout(1300); await snap('d2_class');
  await page.waitForTimeout(1500); await snap('d2_kids');
  await page.evaluate(() => { const s = window.__m1.sim(); s.p.x = 7628; });
  await page.waitForTimeout(2600); await snap('d2_teacher');
  // ---- the torch: a group of theirs in front of him, and the torch in his hands
  await page.evaluate(() => window.__m1.begin('dhamar', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 20000 });
  await god();
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    s.p.x = 6640; s.p.y = 184; s.p.weapon = 'flame'; s.p.ammo = 200; s.p.face = 1;
    s.cam = 6640 - s.viewW * 0.32;
    window.__m1.frozen = false;
  });
  await page.waitForTimeout(400); await snap('d2_torch_hold');
  await page.evaluate(() => { window.__flame = setInterval(() => { const b = document.getElementById('bFire'); }, 100); });
  // hold FIRE with the keyboard
  await page.keyboard.down('KeyJ').catch(() => {});
  await page.waitForTimeout(500); await snap('d2_torch_fire');
  await page.waitForTimeout(700); await snap('d2_torch_fire_b');
  await page.keyboard.up('KeyJ').catch(() => {});
  // ---- zone 3, the vote
  await page.evaluate(() => window.__m1.begin('dhamar', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 20000 });
  await god();
  await page.waitForTimeout(800); await snap('d3_springs');
  await page.evaluate(() => {
    const s = window.__m1.sim();
    window.__m1.frozen = true;
    const gs = ['V', 'V2', 'W', 'W2', 'P', 'P2', 'B', 'B2', 'C', 'C2'];
    for (const g of gs) { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
    s.enemies.forEach(e => { if (e.alive && e.hostile && gs.indexOf(e.g) >= 0) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    for (const g of s.gates) if (g.id !== 'vote') g.done = true;
    s.p.x = 10150; s.p.y = 184; s.p.vx = 0;
    s.cam = s.L.endRight - s.viewW;
    window.__m1.frozen = false;
  });
  for (let k = 0; k < 13; k++) { await page.waitForTimeout(1400); await snap('d3_vote_' + k); }
  await page.evaluate(() => { const s = window.__m1.sim(); s.p.x = 10220; });
  for (let k = 0; k < 12; k++) { await page.waitForTimeout(1300); await snap('d3_end_' + k); }
  console.log('errors:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})();
