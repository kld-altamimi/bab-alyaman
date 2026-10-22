// test_menu_music.js - the menus' music in a real browser: which loop is sounding on each screen, that it is actually
// coming out of the music bus, and that it hands over to the game's music and back.
const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fails = 0;
function note(ok, msg) { console.log((ok ? 'ok   ' : 'FAIL ') + msg); if (!ok) fails++; }
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  async function open() {
    const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    await page.waitForFunction(() => Sound.isReady(), null, { timeout: 20000 }).catch(() => {});
    return { ctx, page, errors };
  }
  // how loud the music bus is over the next half second (RMS of what passes through it)
  const level = page => page.evaluate(() => new Promise(res => {
    const t = Sound.tap();
    if (!t.ctx) { res(0); return; }
    if (!window.__an) { window.__an = t.ctx.createAnalyser(); window.__an.fftSize = 2048; t.music.connect(window.__an); }
    const a = window.__an, buf = new Float32Array(a.fftSize);
    let sum = 0, n = 0;
    const iv = setInterval(() => { a.getFloatTimeDomainData(buf); for (const v of buf) { sum += v * v; n++; } }, 40);
    setTimeout(() => { clearInterval(iv); res(Math.sqrt(sum / Math.max(1, n))); }, 520);
  }));
  const playing = page => page.evaluate(() => Sound.playing());
  const state = page => page.evaluate(() => window.__m1.state());
  let lv;

  // 1. the usual way in: Start on the home screen
  let { ctx, page, errors } = await open();
  note((await playing(page)) === null && (await page.evaluate(() => Sound.track())) === 'title' && (await page.evaluate(() => document.querySelector('#pHome .acts').hidden)), 'before the first tap nothing plays and Start is not shown (the home theme is waiting for a tap)');
  await page.tap('#pad');
  await page.waitForFunction(() => window.__m1.woke());
  await sleep(1200);
  lv = await level(page);
  note((await playing(page)) === 'title' && lv > 0.02 && (await state(page)) === 'home' && !(await page.evaluate(() => document.querySelector('#pHome .acts').hidden)), `the first tap: the home theme plays, still on the home screen, Start shown (music bus at ${lv.toFixed(3)} RMS)`);
  await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(1200);
  lv = await level(page);
  note((await playing(page)) === 'map' && lv > 0.02, `Start: the map's march plays (music bus at ${lv.toFixed(3)} RMS)`);
  await page.tap('#bBriefs');
  await page.waitForFunction(() => window.__m1.state() === 'brief');
  await sleep(300);
  note((await playing(page)) === 'map', 'Briefings: the march carries on');
  await page.tap('#bBriefBack');
  await page.tap('#bOpts2');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(300);
  note((await playing(page)) === 'map', 'Options from the map: the march carries on');
  await page.tap('#bBack');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.tap('#bHome');
  await page.waitForFunction(() => window.__m1.state() === 'home');
  await sleep(1400);
  lv = await level(page);
  note((await playing(page)) === 'title' && lv > 0.02, `Home: the theme plays (music bus at ${lv.toFixed(3)} RMS)`);
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(300);
  note((await playing(page)) === 'title', 'Options from the home screen: the theme carries on');
  await page.tap('#bBack');
  await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(1200);
  note((await playing(page)) === 'map', 'Start again: back to the march');
  // 2. into a mission and out of it
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(5000);
  note((await playing(page)) === 'strait', `in the mission: the stage theme (${await playing(page)})`);
  await page.keyboard.press('p');
  await page.waitForFunction(() => window.__m1.state() === 'pause', null, { timeout: 5000 }).catch(() => {});
  if ((await state(page)) === 'pause') {
    await page.tap('#bQuit');
    await page.waitForFunction(() => window.__m1.state() === 'map');
    await sleep(1400);
    lv = await level(page);
    note((await playing(page)) === 'map' && lv > 0.02, `Mission map from the pause: the march again (music bus at ${lv.toFixed(3)} RMS)`);
  } else note(false, 'could not pause the mission to leave it (state ' + (await state(page)) + ')');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await ctx.close();

  // 3. a key wakes it too, and the theme carries on into the options
  ({ ctx, page, errors } = await open());
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__m1.woke());
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(1200);
  lv = await level(page);
  note((await playing(page)) === 'title' && lv > 0.02, `a key wakes it, then Options: the theme plays on (music bus at ${lv.toFixed(3)} RMS)`);
  await page.tap('#bBack');
  await page.waitForFunction(() => window.__m1.state() === 'home');
  await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(1500);
  note((await playing(page)) === 'map', 'then Start: it hands over to the march');
  // sound off silences it, on brings it back
  await page.tap('#bOpts2');
  await page.tap('#bSound3');
  await sleep(300);
  const off = await page.evaluate(() => Sound.isMuted());
  await page.tap('#bSound3');
  await page.tap('#bBack');
  note(off && !(await page.evaluate(() => Sound.isMuted())) && (await playing(page)) === 'map', 'Sound off and on again in the options: the march is still there');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await ctx.close();
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
})();
