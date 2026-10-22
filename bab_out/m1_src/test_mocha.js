// test_mocha.js - The Coffee Port in a real browser on a phone on its side: from the map (with the Strait cleared) into
// the mission, its music and its boss's, the careful bot playing it through, the results, the reveal of the fork
// beyond it, Play again, and continuing after the last life.
const { chromium } = require('playwright');
const fs = require('fs');
const shots = '/home/claude/bab_out/m1_src/shots/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  // the Strait cleared and stamped: the road to the Coffee Port is open
  await ctx.addInitScript(() => {
    try {
      if (!sessionStorage.getItem('seeded')) {
        localStorage.setItem('strait-m1', JSON.stringify({ prog: { m1: { reached: 4, cleared: true, best: { total: 40000, time: 200 }, runs: 1, stamped: true } } }));
        sessionStorage.setItem('seeded', '1');
      }
    } catch (e) {}
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  const homeLine = await page.evaluate(() => Menu.statuses(window.__m1.prog()).mocha);
  note(homeLine === 'open', 'with the Strait cleared, the Coffee Port is open (' + homeLine + ')');
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(600);
  const card = await page.evaluate(() => [window.__m1.menu().sel, document.getElementById('mName').textContent, document.getElementById('mTag').textContent, document.getElementById('bPlay').textContent,
                                          [...document.querySelectorAll('#mCps li')].map(li => li.textContent).join('|'), document.getElementById('mBest').textContent]);
  note(card[0] === 'mocha' && card[1] === 'The Coffee Port' && card[2] === 'Mocha' && card[3] === 'Start mission', 'the map opens on the Coffee Port, ready: ' + JSON.stringify(card.slice(0, 4)));
  note(card[4] === 'The quay|The warehouses|The roasting house|The old lighthouse', 'its card lists its four checkpoints (' + card[4] + ')');
  note(/Not played yet/.test(card[5]), 'and says it has not been played (' + card[5] + ')');
  await page.screenshot({ path: shots + 'mocha_card.png' });
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const lv = await page.evaluate(() => [window.__m1.cur(), window.__m1.sim().L.id, window.__m1.sim().L.name]);
  note(lv[0] === 'mocha' && lv[1] === 'mocha', 'Start mission plays the Coffee Port (' + lv.join(', ') + ')');
  await sleep(5200);
  const mus = await page.evaluate(() => Sound.playing());
  note(mus === 'mocha', 'its own stage theme plays (' + mus + ')');
  const lines = await page.evaluate(() => ['ann_mocha', 'yazeed_coffee', 'cook_hungry', 'yazeed_roaster', 'qm_behold', 'qm_chimney', 'qm_dark', 'qm_surrender', 'yazeed_cup'].filter(k => !Sound.lineOf(k)));
  note(!lines.length, 'every line it speaks is in the voices file' + (lines.length ? ': missing ' + lines.join(', ') : ''));
  const sfxMissing = await page.evaluate(() => ['door_creak', 'hiss', 'steam', 'bean_spray', 'pop', 'pour', 'rev'].filter(k => !AUDIO.sfx[k]));
  note(!sfxMissing.length, 'every new effect is in the effects file' + (sfxMissing.length ? ': missing ' + sfxMissing.join(', ') : ''));
  await page.screenshot({ path: shots + 'mocha_start.png' });
  // the bot plays it through
  await page.evaluate(BOT);
  await page.evaluate(() => { const bot = window.__mkBot({}); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; });
  const seen = {};
  for (let k = 0; k < 400; k++) {
    await sleep(500);
    const st = await page.evaluate(() => { const s = window.__m1.sim(); return { state: window.__m1.state(), zone: s ? s.zone : -1, boss: s && s.boss ? s.boss.st : null, music: Sound.playing(), time: s ? s.time : 0 }; });
    if (st.state === 'over') { await page.tap('#bContinue'); continue; }
    if (st.zone >= 0 && !seen['zone' + st.zone]) { seen['zone' + st.zone] = st.time; await page.screenshot({ path: shots + 'mocha_zone' + st.zone + '.png' }); }
    if (st.boss === 'idle' && !seen.boss) { seen.boss = st.music; await page.screenshot({ path: shots + 'mocha_boss.png' }); }
    if (st.state === 'results') break;
  }
  note(seen.boss === 'roaster', 'the Big Roaster brings its own music (' + seen.boss + ')');
  const res = await page.evaluate(() => [window.__m1.state(), [...document.querySelectorAll('#rFacts li')].map(li => li.textContent).join('|'), document.getElementById('rMedals').textContent, JSON.stringify(window.__m1.prog().mocha)]);
  note(res[0] === 'results', 'the bot finished it in the page (' + res[0] + ')');
  note(/Roaster put out in/.test(res[1]), 'the results say how long the Roaster took (' + res[1] + ')');
  note(/Liberator: (yes|no, somebody is still tied up among the sacks)/.test(res[2]), 'and speak of its hostages (' + res[2] + ')');
  const pm = JSON.parse(res[3]);
  note(pm.cleared && pm.best && pm.reached === 3 && pm.runs === 1 && !pm.stamped, 'the clear is kept for the Coffee Port: ' + res[3]);
  await page.screenshot({ path: shots + 'mocha_results.png' });
  // the map: CLEAR stamped on Mocha, both roads beyond it opened (still being built)
  await page.tap('#bToMap');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.waitForFunction(() => window.__m1.menu().rv > 40);
  await page.screenshot({ path: shots + 'mocha_stamp.png' });
  await page.waitForFunction(() => window.__m1.menu().rv < 0, null, { timeout: 9000 });
  await sleep(400);
  const after = await page.evaluate(() => { const st = Menu.statuses(window.__m1.prog()); return [window.__m1.prog().mocha.stamped, st.mocha, st.zabid, st.taiz, window.__m1.menu().sel]; });
  note(after[0] && after[1] === 'cleared' && after[2] === 'open' && after[3] === 'soon', 'back on the map: CLEAR stamped on Mocha, the coast road open to the Souq, the mountain road open but its mission coming soon (' + JSON.stringify(after) + ')');
  await page.screenshot({ path: shots + 'mocha_map_after.png' });
  // Play again from its card
  await page.evaluate(() => window.__m1.toMap('mocha'));
  await sleep(500);
  note((await page.evaluate(() => document.getElementById('bPlay').textContent)) === 'Play again', 'the Coffee Port now offers Play again');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  note((await page.evaluate(() => window.__m1.sim().L.id)) === 'mocha', 'Play again plays the Coffee Port');
  // pause, quit to the map: the march; the Strait still plays the Strait
  await page.keyboard.press('p');
  await page.waitForFunction(() => window.__m1.state() === 'pause');
  await page.tap('#bQuit');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(1200);
  note((await page.evaluate(() => Sound.playing())) === 'map', 'quitting it brings back the map\'s march');
  await page.evaluate(() => window.__m1.toMap('m1'));
  await sleep(400);
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(5200);
  note((await page.evaluate(() => [window.__m1.sim().L.id, Sound.playing()].join(','))) === 'm1,strait', 'and the Strait still plays the Strait, with its own theme');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
})();
