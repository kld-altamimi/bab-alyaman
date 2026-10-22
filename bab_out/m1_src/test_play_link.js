// test_play_link.js - the live game's ?play link (0.10.51, the other chat's), carried into the preview: someone new gets
// the first mission's picture with TAP TO PLAY and the thumbs on show, one tap starts Mission 1; someone who has played
// goes to the map; the Share buttons are there; the turn-your-phone note shows only upright; no errors on the page.
// Usage: node test_play_link.js [base url, without the query]
const { chromium } = require('playwright');
const BASE = process.argv[2] || 'http://127.0.0.1:8766/index.html';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const errors = [];
  const fresh = async (vp) => {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
    const page = await ctx.newPage();
    page.on('pageerror', e => errors.push(e.message));
    return { ctx, page };
  };
  // someone new, phone on its side
  let { ctx, page } = await fresh({ width: 844, height: 390 });
  await page.goto(BASE + '?play&internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  const q = await page.evaluate(() => ({ quick: document.getElementById('app').classList.contains('is-quick'), share: !!document.getElementById('bShare') && !!document.getElementById('bShare2'), turnHidden: document.getElementById('turn').hidden }));
  note(q.quick, 'someone new: the ?play picture (is-quick)');
  note(q.share, 'the Share buttons are on the page');
  note(q.turnHidden, 'on its side: no note to turn the phone');
  await page.touchscreen.tap(422, 200);
  const st = await page.waitForFunction(() => window.__m1.state() === 'play' ? window.__m1.cur() : null, null, { timeout: 15000 }).then(h => h.jsonValue()).catch(() => null);
  note(st === 'm1', 'one tap starts Mission 1 (' + st + ')');
  await ctx.close();
  // someone new, phone upright: the note to turn it
  ({ ctx, page } = await fresh({ width: 390, height: 844 }));
  await page.goto(BASE + '?play&internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.waitForTimeout(300);
  note(await page.evaluate(() => !document.getElementById('turn').hidden), 'upright: the note to turn the phone shows');
  await ctx.close();
  // someone who has played: the map
  ({ ctx, page } = await fresh({ width: 844, height: 390 }));
  await page.goto(BASE + '?internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('m1', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForTimeout(500);
  await page.goto(BASE + '?play&internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state && ['map', 'home'].indexOf(window.__m1.state()) >= 0, null, { timeout: 20000 });
  await page.waitForTimeout(300);
  note((await page.evaluate(() => window.__m1.state())) === 'map', 'someone who has played: straight to the map (' + await page.evaluate(() => window.__m1.state()) + ')');
  await ctx.close();
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
