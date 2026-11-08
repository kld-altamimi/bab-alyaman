// snap_sandal.js - pictures of Yazeed losing a sandal as he comes into Jibla (sandal.js, 9 Nov), in the game as it runs:
// the lit stick coming down, fizzing at his feet, the pop with the sandal in the air, the sandal lying behind him and his
// bare front foot, running on through Jibla; and the terraces, both sandals again. Each with a close-up of his feet.
// Usage: node snap_sandal.js <url> <out dir> [en|ar]
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2], OUT = process.argv[3], LANG = process.argv[4] || 'en';
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, locale: LANG === 'ar' ? 'ar' : 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.mouse.click(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  const info = () => page.evaluate(() => {
    const s = window.__m1.sim(), sd = s.sandal || {};
    return { x: Math.round(s.p.x), cam: Math.round(s.cam), st: sd.st, t: sd.t, fair: !!sd.fair, lie: !!sd.lie, fx: sd.fx != null ? Math.round(sd.fx) : null, line: (window.__m1.line() || {}).id || null };
  });
  // where Yazeed's feet are on the page, for a close-up
  const feet = () => page.evaluate(() => {
    const s = window.__m1.sim(), r = document.querySelector('canvas').getBoundingClientRect();
    const k = r.width / Render.width();
    return { x: r.left + (s.p.x - s.cam) * k, y: r.top + (s.p.y - (s.camY || 0)) * k, k: k };
  });
  const snap = async (name, close) => {
    await page.screenshot({ path: OUT + '/' + name + '.png' });
    if (close) {
      const f = await feet();
      const w = 60 * f.k, h = 26 * f.k;
      await page.screenshot({ path: OUT + '/' + name + '_feet.png', clip: { x: Math.max(0, f.x - w / 2), y: Math.max(0, f.y - h + 4 * f.k), width: w, height: h } });
    }
    console.log('picture', name, JSON.stringify(await info()));
  };
  const until = (fn, ms) => page.waitForFunction(fn, null, { timeout: ms || 15000, polling: 16 }).catch(() => console.log('(timed out)'));

  await page.evaluate(() => window.__m1.begin('ibb', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(400);
  await snap('sandal_0_before', true);
  await page.keyboard.down('ArrowRight');
  await until(() => { const sd = window.__m1.sim().sandal; return sd && sd.st === 'stick' && sd.t >= 14; });
  await page.keyboard.up('ArrowRight');
  await snap('sandal_1_stick');
  await until(() => { const sd = window.__m1.sim().sandal; return sd && sd.st === 'fuse' && sd.t >= 6; });
  await snap('sandal_2_fuse');
  await until(() => { const sd = window.__m1.sim().sandal; return sd && sd.st === 'short' && sd.fair && sd.t >= 6; });
  await snap('sandal_3_pop');
  await until(() => { const sd = window.__m1.sim().sandal; return sd && sd.lie; });
  await page.waitForTimeout(300);
  await snap('sandal_4_short', true);
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(500);
  await snap('sandal_5_run', true);
  await page.keyboard.up('ArrowRight');
  await page.waitForTimeout(1500);
  await snap('sandal_5b_screen');
  // the terraces: both sandals
  await page.evaluate(() => window.__m1.begin('ibb', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(700);
  await snap('sandal_6_terraces', true);
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
