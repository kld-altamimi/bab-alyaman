// snap_ibb.js - pictures of Ibb's test range (stage 2 of its plan, 24 Oct): the speakers and the screens. The game is
// stepped by hand (frozen) and drawn for each picture: the billboard at the start, the first speaker with its men
// chanting (and the hint), the speaker taken over (the men giving up), the second speaker shot, a set shot and the men
// beside it flinching, and the warehouses' sets and speakers. Yazeed comes to no harm (he is kept invulnerable).
// Usage: node snap_ibb.js <url> <out dir> [en|ar]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2];
const OUT = process.argv[3];
const LANG = process.argv[4] || 'en';
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: LANG === 'ar' ? 'ar' : 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  await page.evaluate(() => window.__m1.begin('ibb', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(600);
  // step by hand until cond(s) holds or n ticks pass; mx: Yazeed's stick; fire: the trigger; aim: 'up', 'diag' or null
  const run = (cond, n, mx, fire, aim) => page.evaluate(([c, n, mx, fire, aim]) => {
    window.__m1.frozen = true;
    const cond = c ? eval('(' + c + ')') : null;
    let s = window.__m1.sim(), t = 0;
    for (; t < n; t++) {
      if (cond && cond(s)) break;
      const inp = { mx: mx, my: aim === 'up' ? -1 : 0, fire: !!fire, viewW: Render.width(), viewH: Render.height(), lanes: window.__m1.geo().lanes };
      if (aim === 'diag') { inp.my = -1; }
      Sim.step(s, inp);
      if (s.events.length) Render.onEvents(s, s.events);
      s.p.inv = Math.max(s.p.inv, 2);
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: window.__m1.line(), overlay: false, caps: true, noHud: false, dim: 0 });
    }
    return t;
  }, [cond ? cond.toString() : null, n, mx, fire, aim || null]);
  const snap = async (name) => {
    await page.evaluate(() => { window.__m1.frozen = false; });
    await page.waitForTimeout(40);
    await page.evaluate(() => { window.__m1.frozen = true; });
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    const at = await page.evaluate(() => {
      const s = window.__m1.sim(), I = s.ibb;
      return { x: Math.round(s.p.x), cam: Math.round(s.cam), zone: s.zone, spk: I ? I.spk.map(o => o.st + ':' + o.hp) : null, scr: I ? I.scr.map(o => o.st + ':' + o.hp) : null,
               men: s.enemies.filter(e => e.alive).map(e => e.g + ':' + e.st + (e.hostile ? '' : '(down)')).join(' '), line: window.__m1.line() ? window.__m1.line().id : null };
    });
    console.log('picture', name, JSON.stringify(at));
  };
  // 1. the start: the billboard, statement C
  await run(null, 150, 0);
  await snap('i1_billboard');
  // 2. walk up to the first speaker: its men chanting, the hint
  await run(s => s.p.x >= 330, 60 * 10, 1);
  await run(null, 70, 0);
  await snap('i2_chant');
  await run(null, 12, 0);
  await snap('i2_chant_b');
  // 3. walk into the pole: taken over
  await run(s => s.ibb.spk[0].st !== 'live', 60 * 8, 1);
  await run(null, 30, 0);
  await snap('i3_hijack');
  await run(null, 60, 0);
  await snap('i3_hijack_b');
  // capture them and move on to the second speaker
  await run(s => s.p.x >= 600 || s.groups.A.done, 60 * 6, 1);
  await run(s => s.p.x >= 700, 60 * 8, 1);
  await run(null, 60, 0);
  await snap('i4_speaker2');
  // 4. shoot the second speaker (by hand: its hit points) and see it dead, and its men without their bubbles
  await page.evaluate(() => { const s = window.__m1.sim(); Sim.ext.ibb.hurtSpeaker(s, s.ibb.spk[1], 6, 'shot'); });
  await run(null, 20, 0);
  await snap('i5_speaker2_dead');
  // clear the group (put them down by hand) and walk to the stall's set
  await page.evaluate(() => { const s = window.__m1.sim(); s.enemies.forEach(e => { if (e.alive && e.hostile && (e.g === 'B' || e.g === 'A')) Sim._.killEnemy(s, e, 1, 'shot'); }); s.groups.B.pending.length = 0; });
  await run(s => s.p.x >= 960, 60 * 10, 1);
  await run(null, 90, 0);
  await snap('i6_tv');
  // 5. shoot the set: static, and the men by it flinch
  await page.evaluate(() => { const s = window.__m1.sim(); Sim.ext.ibb.hurtScreen(s, s.ibb.scr[1], 2, 'shot'); });
  await run(null, 6, 0);
  await snap('i7_tv_shot');
  await run(null, 30, 0);
  await snap('i7_tv_shot_b');
  // the warehouses (each group put down by hand once its picture is taken)
  const down = (gs) => page.evaluate((gs) => { const s = window.__m1.sim(); s.enemies.forEach(e => { if (e.alive && e.hostile && gs.indexOf(e.g) >= 0) Sim._.killEnemy(s, e, 1, 'shot'); }); gs.forEach(g => s.groups[g].pending.length = 0); }, gs);
  await down(['C']);
  await run(s => s.p.x >= 1250, 60 * 10, 1);
  await run(null, 100, 0);
  await snap('i8_warehouse_tv');
  await down(['D']);
  await run(s => s.p.x >= 1880, 60 * 12, 1);
  await run(null, 100, 0);
  await snap('i9_speaker3_tv');
  await down(['E']);
  await run(s => s.p.x >= 2150, 60 * 12, 1);
  await run(null, 100, 0);
  await snap('i10_last_speaker');
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
