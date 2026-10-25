// bench_ibb.js - drawing time per frame in Ibb's painted zones against Taiz's first zone (live on phones), with the bot
// playing: begin() loads each mission's pictures, then the game is stepped by hand and timed. Software drawing here, so
// a ceiling and a comparison, not a forecast. Usage: node bench_ibb.js <url>
const { chromium } = require('playwright');
const fs = require('fs');
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const URL = process.argv[2];
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  for (const [label, vp] of [['phone on its side, 3x', [844, 390, 3]], ['phone upright, 3x', [390, 760, 3]]]) {
    for (const [mis, zone, until] of [['taiz', 0, 1300], ['ibb', 0, 1280], ['ibb', 1, 2640]]) {
      const ctx = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: vp[2], hasTouch: true, isMobile: true });
      const page = await ctx.newPage();
      await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
      await page.goto(URL);
      await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
      await page.evaluate(BOT);
      await page.evaluate(([m, z]) => window.__m1.begin(m, z), [mis, zone]);
      await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
      await page.waitForTimeout(1500);
      const r = await page.evaluate((until) => {
        window.__m1.frozen = true;
        const W = window.__m1.width(), lo = document.getElementById('lo'), hi = document.getElementById('hi'), hx = hi.getContext('2d');
        hx.imageSmoothingEnabled = false;
        const bot = window.__mkBot({ auto: false });
        const s = window.__m1.sim();
        const ui = { paused: false, fps: 60, lock: false, auto: false, sub: { who: 'YAZEED', text: 'Sand in my sandals. Already.' }, caps: true, noHud: false, dim: 0 };
        let tDraw = 0, tBlit = 0, n = 0, worst = 0; const all = [];
        for (let k = 0; k < 4000 && s.status === 'play' && s.p.x < until; k++) {
          const i = bot(s); i.viewW = W;
          Sim.step(s, i); s.p.inv = Math.max(s.p.inv, 2);
          const b = performance.now();
          Render.onEvents(s, s.events);
          Render.draw(s, ui);
          const c = performance.now();
          hx.drawImage(lo, 0, 0, W, 216, 0, 0, hi.width, hi.height);
          hx.getImageData(0, 0, 1, 1);
          const d = performance.now();
          tDraw += c - b; tBlit += d - c; n++; all.push(c - b);
          worst = Math.max(worst, d - b);
        }
        all.sort((a, b) => a - b);
        return { n, draw: tDraw / n, p95: all[Math.floor(all.length * 0.95)], blit: tBlit / n, worst, x: Math.round(s.p.x), W };
      }, until);
      console.log(`${label} · ${mis} zone ${zone + 1}: ${r.n} frames to x ${r.x} (picture ${r.W} wide): drawing ${r.draw.toFixed(2)} ms average, ${r.p95.toFixed(2)} ms at the 95th, enlarging ${r.blit.toFixed(2)} ms; slowest ${r.worst.toFixed(1)} ms`);
      await ctx.close();
    }
  }
  await browser.close();
})();
