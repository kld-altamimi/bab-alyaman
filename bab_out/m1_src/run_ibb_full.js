// run_ibb_full.js - Ibb start to finish in the page, the bot playing and every frame drawn (the opening, the fight, the
// reveal, the plateau): the mission must clear with no page errors. Then, live, that Yazeed says nothing at the mosque in
// Jibla (the line was taken out on 30 Oct).
// Usage: node run_ibb_full.js <url>
const { chromium } = require('playwright');
const fs = require('fs');
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const URL = process.argv[2];
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.touchscreen.tap(422, 150);
  await page.evaluate(BOT);
  for (const auto of [false, true]) {
    await page.evaluate(() => window.__m1.begin('ibb', 0));
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    const r = await page.evaluate((auto) => {
      window.__m1.frozen = true;
      const W = window.__m1.width(), s = window.__m1.sim(), bot = window.__mkBot({ auto: auto });
      const ui = { paused: false, fps: 60, lock: false, auto: auto, sub: null, caps: true, noHud: false, dim: 0 };
      const seen = {}; let k = 0, err = null;
      try {
        for (; k < 60 * 600 && s.status === 'play'; k++) {
          const i = bot(s); i.viewW = W;
          Sim.step(s, i);
          for (const e of s.events) if (/^(op_|spk_|boss_|van_|tech_|checkpoint|clear)/.test(e.t)) seen[e.t] = (seen[e.t] || 0) + 1;
          Render.onEvents(s, s.events);
          Render.draw(s, ui);
        }
      } catch (e) { err = String(e && e.stack || e).slice(0, 300); }
      window.__m1.frozen = false;
      return { status: s.status, k, t: s.time.toFixed(0), deaths: s.stats.deaths, err, seen };
    }, auto);
    console.log((auto ? 'auto fire' : 'hold fire') + ':', JSON.stringify(r));
  }
  // live: Yazeed's word at the mosque
  await page.evaluate(() => window.__m1.begin('ibb', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    const s = window.__m1.sim(), L = s.L, W = Render.width();
    window.__m1.frozen = true;
    for (const g of s.gates) { if (g.x > 3200) continue; g.done = true; for (const k of g.groups) { const G = s.groups[k]; G.done = true; G.pending.length = 0; G.awake = true; } }
    s.enemies.forEach(e => { if (e.alive && e.x < 3300) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
    if (s.school) s.school.done = true;
    for (const pr of s.props) if (pr.k === 'detainee') { pr.st = 'freed'; pr.t = 0; }
    s.p.x = 3036; s.p.y = Sim.groundY(L, 3036); s.p.inv = 9999; s.p.air = false; s.p.plat = -1;
    s.cam = 3036 - W * 0.32;
    window.__m1.frozen = false;
  });
  await page.keyboard.down('ArrowRight'); await page.waitForTimeout(300); await page.keyboard.up('ArrowRight');
  let said = null;
  for (let i = 0; i < 40 && !said; i++) { await page.waitForTimeout(250); said = await page.evaluate(() => { const l = window.__m1.line(); return l && l.id === 'yazeed_mosque' ? l.text : null; }); }
  await page.screenshot({ path: '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s12/pics/mosque_line.png' });
  console.log('mosque line (removed 30 Oct, Khaled):', said ? 'STILL PLAYS: ' + said : 'none, as it should be', 'x', await page.evaluate(() => Math.round(window.__m1.sim().p.x)));
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
