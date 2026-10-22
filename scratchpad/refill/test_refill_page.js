// test_refill_page.js - the refill in the real page: start a mission, take lives and plates away, walk Yazeed over the
// next checkpoint, and check both come back (extra lives kept); for the Strait and the Coffee Port; plus one picture of
// the HUD just after a refill and no page errors. Usage: node test_refill_page.js <base url>
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8781/index.html';
const SHOT = __dirname + '/shot_refill_hud.png';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(BASE + '?internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  const want = process.env.WANT_BUILD || '0.10.65';
  note((await page.evaluate(() => typeof BUILD !== 'undefined' ? BUILD : '')) === want, 'build string ' + want);
  await page.touchscreen.tap(422, 150);
  for (const [mission, lives, plates, wantLives] of [['m1', 1, 1, 3], ['mocha', 2, 1, 3], ['m1', 5, 2, 5]]) {
    await page.evaluate((m) => window.__m1.begin(m, 0), mission);
    await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim() && window.__m1.sim().p, null, { timeout: 20000 });
    await page.waitForTimeout(400);
    const r = await page.evaluate(async ([lives, plates]) => {
      const s = window.__m1.sim();
      s.p.lives = lives; s.p.plates = plates;
      const z1 = s.L.zones[1].x;
      for (const g of s.gates) g.done = true;                      // (open the fights in the way, as if they were won)
      s.cam = Math.max(0, z1 - s.viewW * 0.5);
      s.p.x = z1 + 2;
      await new Promise((res) => setTimeout(res, 250));
      const t = window.__m1.sim();
      return { zone: t.zone, lives: t.p.lives, plates: t.p.plates, dead: t.p.dead };
    }, [lives, plates]);
    note(r.zone === 1 && r.lives === wantLives && r.plates === 3 && !r.dead,
      mission + ': ' + lives + ' lives and ' + plates + ' plates before the checkpoint, after: ' + JSON.stringify(r));
    if (mission === 'mocha') await page.screenshot({ path: SHOT, clip: { x: 0, y: 0, width: 844, height: 120 } });
  }
  note(errors.length === 0, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
  process.exit(fails ? 1 : 0);
})();
