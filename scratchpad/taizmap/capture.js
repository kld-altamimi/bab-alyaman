// capture.js - the whole Taiz stage in one picture, drawn by the game's own renderer: the picture made as big as the
// level (7950 x 1300 world pixels, 1:1), the camera at 0,0, no HUD, nobody in it, the Apache out of the way. Once at night
// (as the level is played) and once with the night lifted (s.dark = 0), for reading the layout.
// Usage: node capture.js <base url> <out dir>
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3];
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)|\.mp3$/, (r) => r.abort());
  await page.goto(BASE + '?internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli && window.__m1.sim().heli.st === 'fly', null, { timeout: 30000 });
  await page.waitForTimeout(500);
  for (const [name, dark] of [['night', 1], ['day', 0]]) {
    const r = await page.evaluate(([dark]) => {
      window.__m1.frozen = true;
      const s = window.__m1.sim();
      const W = s.L.width, H = s.L.height;
      s.enemies.length = 0; if (s.bullets) s.bullets.length = 0; if (s.ebullets) s.ebullets.length = 0;
      if (s.drones) s.drones.length = 0; if (s.missiles) s.missiles.length = 0; if (s.rockets) s.rockets.length = 0;
      s.heli.x = -4000; s.heli.y = -4000; s.p.x = -4000; s.p.y = -4000;
      s.dark = dark;
      s.viewW = W; s.viewH = H; s.cam = 0; s.camY = 0;
      Render.reset();
      Render.resize(W / (H / 216), H / 216);
      Render.draw(s, { paused: true, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: true, dim: 0 });
      const lo = document.getElementById('lo');
      return { w: lo.width, h: lo.height, url: lo.toDataURL('image/png') };
    }, [dark]);
    fs.writeFileSync(OUT + '/map_' + name + '.png', Buffer.from(r.url.split(',')[1], 'base64'));
    console.log(name, r.w + 'x' + r.h);
  }
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
