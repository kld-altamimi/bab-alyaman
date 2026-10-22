// test_repo_boot.js - the repo folder exactly as it will be pushed (index.html + analytics.js + audio/), served as is:
// the title screen comes up, the sound arrives by its relative path, the Souq starts from the Tailor's checkpoint, and
// nothing on the page goes wrong. Usage: node test_repo_boot.js http://127.0.0.1:8768/index.html?internal=1
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://127.0.0.1:8768/index.html?internal=1';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [], audio = [], missing = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  page.on('response', r => { const u = r.url(); if (u.startsWith('http://127.0.0.1')) { if (/\/audio\/[^/]+\.mp3$/.test(u)) audio.push(u.split('/').pop() + ':' + r.status()); if (r.status() >= 400) missing.push(u + ' ' + r.status()); } });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  note(true, 'the title screen comes up (BUILD ' + (await page.evaluate(() => window.BUILD)) + ')');
  note(await page.evaluate(() => !!(window.HM && window.HM.internal)), 'opened with ?internal=1, analytics.js is loaded and sends nothing');
  await page.waitForFunction(() => Sound.isReady() || Sound.hasFailed(), null, { timeout: 20000 });
  note(await page.evaluate(() => Sound.isReady() && !Sound.hasFailed()), 'the sound arrives from audio/ (' + audio.join(', ') + ')');
  await page.touchscreen.tap(422, 150);
  // the Souq from its last checkpoint when the page has it; otherwise (built --no-souq) the Coffee Port from its last
  const souq = await page.evaluate(() => window.__m1.levels().indexOf('zabid') >= 0);
  const [mis, zone, stage, boss] = souq ? ['zabid', 3, 'souq', 'tailor'] : ['mocha', 2, 'mocha', 'roaster'];
  await page.evaluate(([m, z]) => window.__m1.begin(m, z), [mis, zone]);
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForFunction(st => Sound.playing() === st, stage, { timeout: 8000 }).catch(() => {});
  await page.waitForFunction(b => Sound.hasTrack(b), boss, { timeout: 8000 }).catch(() => {});
  const s = await page.evaluate(b => [window.__m1.sim().L.id, window.__m1.sim().zone, Sound.playing(), Sound.hasTrack(b)], boss);
  note(s[0] === mis && s[1] === zone && s[2] === stage && s[3], mis + ' starts at its last checkpoint with its music, its boss\'s ready (' + JSON.stringify(s) + ')');
  await sleep(1500);
  note(!missing.length, 'every file the page asked for is there' + (missing.length ? ': ' + missing.join(' | ') : ''));
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
