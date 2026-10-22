// test_music_load.js - a mission's music is fetched when that mission is chosen, not at the start (0.8.46): the title
// screen fetches only the effects, the voices, the menus' music and the jingles; the map card of a mission, looked at for
// a moment, fetches its stage theme and its boss's; the mission plays its music; another mission's music lets the first
// go; the boss's music is there when the boss is; and nothing on the page goes wrong.
const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [], got = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  page.on('response', async r => { const u = r.url(); if (/\/audio\/[^/]+\.mp3$/.test(u)) { let n = 0; try { n = (await r.body()).length; } catch (e) {} got.push({ f: u.split('/').pop().replace('.mp3', ''), n }); } });
  const files = () => got.map(g => g.f);
  const kb = list => Math.round(got.filter(g => list.indexOf(g.f) >= 0).reduce((a, g) => a + g.n, 0) / 1024);
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.waitForFunction(() => Sound.isReady(), null, { timeout: 20000 });
  await sleep(800);
  const boot = files().slice().sort();
  note(JSON.stringify(boot) === JSON.stringify(['jingle_complete', 'jingle_start', 'music_map', 'music_title', 'sfx', 'voices']),
    'at the title only the effects, the voices, the menus\' music and the jingles are fetched (' + boot.join(', ') + ': ' + kb(boot) + ' KB)');
  // the map, opening on the Strait: its music is fetched once its card has been up a moment
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.waitForFunction(() => window.__m1.menu().sel === 'm1');
  await sleep(1500);
  note(files().indexOf('music_strait') >= 0 && files().indexOf('music_battery') >= 0 && files().indexOf('music_mocha') < 0 && files().indexOf('music_souq') < 0,
    'the Strait\'s card fetches the Strait\'s music and the battery\'s, and nothing else (' + files().slice(boot.length).join(', ') + ')');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForFunction(() => Sound.playing() === 'strait', null, { timeout: 8000 }).catch(() => {});
  note((await page.evaluate(() => Sound.playing())) === 'strait', 'Start mission: the Strait\'s theme plays');
  const d1 = await page.evaluate(() => Sound.info().decoded);
  note(d1 === '8/12', 'eight of the twelve files are in hand, not all twelve (' + d1 + ')');
  // the Souq from its last checkpoint: its music comes, the Strait's goes, and the Tailor's is there for the Tailor
  await page.evaluate(BOT);
  await page.evaluate(() => window.__m1.begin('zabid', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForFunction(() => Sound.playing() === 'souq', null, { timeout: 8000 }).catch(() => {});
  note((await page.evaluate(() => Sound.playing())) === 'souq', 'the Souq: its own theme plays (fetched there and then: ' + files().filter(f => /souq|tailor/.test(f)).join(', ') + ')');
  // (the boss's theme is decoded after the stage's, which the mission waits for: give it a few seconds, long before he comes)
  await page.waitForFunction(() => Sound.hasTrack('tailor'), null, { timeout: 8000 }).catch(() => {});
  const d2 = await page.evaluate(() => [Sound.info().decoded, Sound.hasTrack('strait'), Sound.hasTrack('battery'), Sound.hasTrack('tailor')]);
  note(d2[0] === '8/12' && !d2[1] && !d2[2] && d2[3], 'the Strait\'s music is let go and the Tailor\'s is ready within seconds (' + JSON.stringify(d2) + ')');
  await page.evaluate(() => { const bot = window.__mkBot({}); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; });
  let boss = null;
  for (let k = 0; k < 120 && !boss; k++) { await sleep(250); boss = await page.evaluate(() => { const s = window.__m1.sim(); return s.boss && s.boss.st !== 'intro' ? Sound.playing() : null; }); }
  note(boss === 'tailor', 'the Tailor comes on to his own music (' + boss + ')');
  // back on the map, Mocha's card: its music comes, the Souq's goes
  await page.evaluate(() => window.__m1.toMap('mocha'));
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(1500);
  const d3 = await page.evaluate(() => [Sound.info().decoded, Sound.hasTrack('mocha'), Sound.hasTrack('roaster'), Sound.hasTrack('souq'), Sound.hasTrack('tailor')]);
  note(d3[1] && d3[2] && !d3[3] && !d3[4] && d3[0] === '8/12', 'Mocha\'s card, looked at: the Coffee Port\'s music comes and the Souq\'s goes (' + JSON.stringify(d3) + ')');
  const total = kb(files());
  console.log('     fetched in all: ' + files().join(', ') + ' (' + total + ' KB)');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
