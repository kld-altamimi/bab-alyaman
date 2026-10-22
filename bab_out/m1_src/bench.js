// bench.js - how long one frame's work takes here: the game step, the drawing, and the enlarging. (Software drawing, so a ceiling, not a forecast.)
const { chromium } = require('playwright');
const fs = require('fs');
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  for (const [label, vp] of [['phone on its side, 3x', [844, 390, 3]], ['phone upright, 3x', [390, 760, 3]], ['desktop, 1x', [1280, 800, 1]]]) {
    const ctx = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: vp[2], hasTouch: true, isMobile: vp[2] > 1 });
    const page = await ctx.newPage();
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    await page.evaluate(BOT);
    const r = await page.evaluate(() => {
      window.__m1.frozen = true;
      const W = window.__m1.width(), lo = document.getElementById('lo'), hi = document.getElementById('hi'), hx = hi.getContext('2d');
      hx.imageSmoothingEnabled = false;
      const bot = window.__mkBot({ auto: false });
      let s = Sim.create(LEVEL, { viewW: W, seed: 3 });
      Render.reset();
      let tStep = 0, tDraw = 0, tBlit = 0, n = 0, worst = 0;
      const ui = { paused: false, fps: 60, lock: false, auto: false, sub: { who: 'YAZEED', text: 'Sand in my sandals. Already.' }, caps: true, noHud: false, dim: 0 };
      for (let k = 0; k < 2400 && s.status !== 'clear'; k++) {
        const i = bot(s); i.viewW = W;
        const a = performance.now();
        Sim.step(s, i);
        const b = performance.now();
        Render.onEvents(s, s.events);
        Render.draw(s, ui);
        const c = performance.now();
        hx.drawImage(lo, 0, 0, W, 216, 0, 0, hi.width, hi.height);
        // force the work to finish, as a real frame would have to
        hx.getImageData(0, 0, 1, 1);
        const d = performance.now();
        tStep += b - a; tDraw += c - b; tBlit += d - c; n++;
        worst = Math.max(worst, d - a);
      }
      window.__m1.frozen = false;
      return { n, step: tStep / n, draw: tDraw / n, blit: tBlit / n, worst, W, hi: hi.width + 'x' + hi.height };
    });
    console.log(`${label}: picture ${r.W} wide, enlarged to ${r.hi}; per frame over ${r.n} frames: game ${r.step.toFixed(3)} ms, drawing ${r.draw.toFixed(2)} ms, enlarging ${r.blit.toFixed(2)} ms; slowest whole frame ${r.worst.toFixed(1)} ms (budget 16.7)`);
    await ctx.close();
  }
  await browser.close();
})();
