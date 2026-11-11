// run_dhamar_full.js - Dhamar's test build (zones 1-3) start to finish in the page, the bot playing and every frame drawn
// (the highway, the city, the torch, the school, the vote): the mission must clear with no page errors, at both fire settings.
// Usage: node run_dhamar_full.js <url>
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
    await page.evaluate(() => window.__m1.begin('dhamar', 0));
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
          for (const e of s.events) if (/^(cp_|bar_|note_|rally_|class_|kid_|school|freed|pickup|weapon_|checkpoint|clear)/.test(e.t)) seen[e.t] = (seen[e.t] || 0) + 1;
          Render.onEvents(s, s.events);
          Render.draw(s, ui);
        }
      } catch (e) { err = String(e && e.stack || e).slice(0, 300); }
      window.__m1.frozen = false;
      return { status: s.status, k, t: s.time.toFixed(0), deaths: s.stats.deaths, err, seen };
    }, auto);
    console.log((auto ? 'auto fire' : 'hold fire') + ':', JSON.stringify(r));
  }
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
