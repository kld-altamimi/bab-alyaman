// test_nosouq.js - the release built without the Souq (build.py --no-souq, 21 Oct): the page has no Souq level, code,
// stage pictures or music; with the Strait and the Coffee Port cleared, the Souq's card shows it locked behind the Castle
// (since 0.10.66 the Souq follows Taiz: Khaled, 22 Oct), and coming soon once the Castle is cleared (the Spice Cannon
// teaser, in English and Arabic, nothing to start, no start-from list even for a developer); the Strait and the
// Coffee Port still start with their music; and the Souq's music files are never asked for.
const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
const SEED = () => {
  try {
    if (!sessionStorage.getItem('seeded')) {
      localStorage.setItem('strait-m1', JSON.stringify({ dev: true, prog: {
        m1: { reached: 4, cleared: true, best: { total: 40000, time: 200 }, runs: 1, stamped: true },
        mocha: { reached: 3, cleared: true, best: { total: 38000, time: 240 }, runs: 1, stamped: true } } }));
      sessionStorage.setItem('seeded', '1');
    }
  } catch (e) {}
};
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  await ctx.addInitScript(SEED);
  const page = await ctx.newPage();
  const errors = [], got = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  page.on('request', r => { const u = r.url(); if (/\/audio\/[^/]+\.mp3$/.test(u)) got.push(u.split('/').pop()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  const inside = await page.evaluate(() => ({
    build: window.BUILD, levels: window.__m1.levels(), music: Object.keys(AUDIO.music).sort(),
    souqPics: Object.keys(IMAGES).filter(n => /^z_|^zf_/.test(n)), stages: Object.keys(ATLAS.stages),
    code: ['LEVEL_ZABID'].filter(v => typeof window[v] !== 'undefined').concat(Sim.ext && Sim.ext.tailor ? ['Sim.ext.tailor'] : []).concat(Render.bosses && Render.bosses.tailor ? ['Render.bosses.tailor'] : [])
  }));
  // (since 0.9.50 the test link also has Taiz's flying test range: the Souq is still out)
  note(inside.levels.indexOf('zabid') < 0 && inside.levels.slice(0, 2).join() === 'm1,mocha' && inside.levels.every(id => ['m1', 'mocha', 'taiz'].indexOf(id) >= 0), 'the Strait and the Coffee Port to play, and no Souq (' + inside.levels + '; build ' + inside.build + ')');
  note(!inside.code.length && !inside.souqPics.length && inside.stages.indexOf('zabid') < 0, 'no Souq level, boss code or stage pictures in the page' + (inside.code.length || inside.souqPics.length ? ': ' + inside.code.concat(inside.souqPics).join(', ') : ''));
  note(inside.music.indexOf('souq') < 0 && inside.music.indexOf('tailor') < 0 && inside.music.length === 10, 'no Souq music in the sound list, and the two of Taiz in it (' + inside.music.join(', ') + ')');
  // the map, both earlier missions cleared: the Souq's card as on the live game
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.evaluate(() => window.__m1.toMap('zabid'));
  await sleep(600);
  const card = await page.evaluate(() => ({ st: Menu.statuses(window.__m1.prog()).zabid, name: document.getElementById('mName').textContent, boss: document.getElementById('mBoss').textContent,
    play: document.getElementById('bPlay').textContent, disabled: document.getElementById('bPlay').disabled, from: document.getElementById('mFromRow').hidden, dev: window.__m1.dev() }));
  note(card.st === 'locked' && card.disabled, 'behind the Castle, the Souq is locked, nothing to start (' + card.st + ', "' + card.play + '", disabled ' + card.disabled + ')');
  await page.evaluate(() => { window.__m1.prog().taiz = { reached: 3, cleared: true, best: { total: 50000, time: 400 }, runs: 1, stamped: true }; window.__m1.toMap('zabid'); });
  await sleep(600);
  const card2 = await page.evaluate(() => ({ st: Menu.statuses(window.__m1.prog()).zabid, play: document.getElementById('bPlay').textContent, disabled: document.getElementById('bPlay').disabled }));
  note(card2.st === 'soon' && card2.play === 'Coming soon' && card2.disabled, 'with the Castle cleared, the Souq is coming soon, nothing to start (' + card2.st + ', "' + card2.play + '", disabled ' + card2.disabled + ')');
  note(card.boss === 'The Spice Cannon. It fires chilli. Keep your mouth shut.', 'its card has the live game\'s teaser: ' + card.boss);
  note(card.dev && card.from, 'even a developer gets no start-from list for it (developer ' + card.dev + ', list hidden ' + card.from + ')');
  await page.evaluate(() => window.__m1.setLang('ar'));
  await sleep(200);
  const ar = await page.evaluate(() => document.getElementById('mBoss').textContent);
  note(ar === 'مدفع البهارات. يقذف الفلفل الحار. أبقِ فمك مغلقاً.', 'and in Arabic: ' + ar);
  await page.evaluate(() => window.__m1.setLang('en'));
  // the Coffee Port's card, then play it from its last checkpoint, then the Strait: their music
  await page.evaluate(() => window.__m1.toMap('mocha'));
  await sleep(1400);
  await page.evaluate(() => window.__m1.begin('mocha', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForFunction(() => Sound.playing() === 'mocha', null, { timeout: 8000 }).catch(() => {});
  note((await page.evaluate(() => Sound.playing())) === 'mocha', 'the Coffee Port starts with its theme (' + (await page.evaluate(() => Sound.playing())) + ')');
  await page.evaluate(() => window.__m1.begin('m1', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.waitForFunction(() => Sound.playing() === 'strait', null, { timeout: 8000 }).catch(() => {});
  note((await page.evaluate(() => Sound.playing())) === 'strait', 'the Strait starts with its theme (' + (await page.evaluate(() => Sound.playing())) + ')');
  await sleep(800);
  note(!got.some(f => /souq|tailor/.test(f)), 'the Souq\'s music is never asked for (asked: ' + got.join(', ') + ')');
  const decoded = await page.evaluate(() => Sound.info().decoded);
  note(/\/12$/.test(decoded), 'twelve sound files in all (Taiz has two of its own since 0.9.57), as many as the folder will hold (' + decoded + ')');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
