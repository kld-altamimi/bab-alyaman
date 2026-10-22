// test_souq.js - The Souq in a real browser on a phone on its side: from the map (with the Strait and the Coffee Port
// cleared) into the mission, its music and its boss's, its sounds and lines, the careful bot playing it through, the
// results, CLEAR stamped on it and the coast road open beyond it, Play again; then the same in Arabic.
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
const SEED = () => {
  try {
    if (!sessionStorage.getItem('seeded')) {
      localStorage.setItem('strait-m1', JSON.stringify({ prog: {
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
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  const homeLine = await page.evaluate(() => Menu.statuses(window.__m1.prog()).zabid);
  note(homeLine === 'open', 'with the Coffee Port cleared, the Souq is open (' + homeLine + ')');
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(600);
  const card = await page.evaluate(() => [window.__m1.menu().sel, document.getElementById('mName').textContent, document.getElementById('mTag').textContent, document.getElementById('bPlay').textContent,
                                          [...document.querySelectorAll('#mCps li')].map(li => li.textContent).join('|'), document.getElementById('mBest').textContent]);
  note(card[0] === 'zabid' && card[1] === 'The Souq' && card[2] === 'Zabid' && card[3] === 'Start mission', 'the map opens on the Souq, ready: ' + JSON.stringify(card.slice(0, 4)));
  note(card[4] === 'The town gate|The spice stalls|The rooftops|The covered market', 'its card lists its four checkpoints (' + card[4] + ')');
  await page.screenshot({ path: shots + 'souq_card.png' });
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const lv = await page.evaluate(() => [window.__m1.cur(), window.__m1.sim().L.id, window.__m1.sim().L.name]);
  note(lv[0] === 'zabid' && lv[1] === 'zabid', 'Start mission plays the Souq (' + lv.join(', ') + ')');
  await sleep(5200);
  const mus = await page.evaluate(() => Sound.playing());
  note(mus === 'souq', 'its own stage theme plays (' + mus + ')');
  const lines = await page.evaluate(() => ['ann_souq', 'yazeed_souq', 'yazeed_chilli', 'yazeed_scale', 'yazeed_lunch', 'grunt_eyes', 'grunt_wall', 'shop_tea', 'shop_thanks', 'shop_cloth',
    'wm_behold', 'wm_porters', 'wm_weights', 'wm_chain', 'wm_surrender', 'porter_coming', 'uncle_spice', 'yazeed_sneeze', 'grunt_sneeze', 'wm_whoa', 'wm_ow'].filter(k => !Sound.lineOf(k)));
  const gone = await page.evaluate(() => ['yazeed_cannon', 'pusher_push', 'pusher_hup'].filter(k => Sound.lineOf(k)).concat(AUDIO.music.cannon ? ['music cannon'] : []));
  note(!gone.length, 'the Spice Cannon\'s lines and music are gone' + (gone.length ? ': still ' + gone.join(', ') : ''));
  note(!lines.length, 'every line and noise it uses is in the voices file' + (lines.length ? ': missing ' + lines.join(', ') : ''));
  const sfxMissing = await page.evaluate(() => ['sack_burst', 'thunk', 'blunderbuss', 'creak', 'pigeon', 'bonk', 'chain_snap', 'iron_thud'].filter(k => !AUDIO.sfx[k]));
  note(!sfxMissing.length, 'every new effect is in the effects file' + (sfxMissing.length ? ': missing ' + sfxMissing.join(', ') : ''));
  await page.screenshot({ path: shots + 'souq_start.png' });
  // the bot plays it through
  await page.evaluate(BOT);
  await page.evaluate(() => { const bot = window.__mkBot({}); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; });
  const seen = {};
  for (let k = 0; k < 500; k++) {
    await sleep(500);
    const st = await page.evaluate(() => { const s = window.__m1.sim(); return { state: window.__m1.state(), zone: s ? s.zone : -1, boss: s && s.boss ? s.boss.st : null, music: Sound.playing(), time: s ? s.time : 0, clouds: s ? s.clouds.length : 0, bars: s ? s.bars.filter(o => !o.gone).length : 0 }; });
    if (st.state === 'over') { await page.tap('#bContinue'); continue; }
    if (st.zone >= 0 && !seen['zone' + st.zone]) { seen['zone' + st.zone] = st.time; await page.screenshot({ path: shots + 'souq_zone' + st.zone + '.png' }); }
    if (st.clouds && !seen.cloud) { seen.cloud = 1; await page.screenshot({ path: shots + 'souq_cloud.png' }); }
    if (st.boss === 'idle' && !seen.boss) { seen.boss = st.music; await page.screenshot({ path: shots + 'souq_boss.png' }); }
    if (st.state === 'results') break;
  }
  note(seen.boss === 'scale', 'the Great Scale brings its own music (' + seen.boss + ')');
  note(seen.zone1 > 0 && seen.zone2 > 0 && seen.zone3 > 0, 'the bot went through every checkpoint (' + [seen.zone1, seen.zone2, seen.zone3].map(t => t && t.toFixed(0)).join(', ') + ' s)');
  const res = await page.evaluate(() => [window.__m1.state(), [...document.querySelectorAll('#rFacts li')].map(li => li.textContent).join('|'), document.getElementById('rMedals').textContent, JSON.stringify(window.__m1.prog().zabid)]);
  note(res[0] === 'results', 'the bot finished it in the page (' + res[0] + ')');
  note(/Scale broken in/.test(res[1]), 'the results say how long the Scale took (' + res[1] + ')');
  note(/Liberator: (yes|no, a shopkeeper is still tied up behind his counter)/.test(res[2]), 'and speak of the shopkeepers (' + res[2] + ')');
  const pm = JSON.parse(res[3]);
  note(pm.cleared && pm.best && pm.reached === 3 && pm.runs === 1 && !pm.stamped, 'the clear is kept for the Souq: ' + res[3]);
  await page.screenshot({ path: shots + 'souq_results.png' });
  await page.tap('#bToMap');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.waitForFunction(() => window.__m1.menu().rv > 40);
  await page.screenshot({ path: shots + 'souq_stamp.png' });
  await page.waitForFunction(() => window.__m1.menu().rv < 0, null, { timeout: 9000 });
  await sleep(400);
  const after = await page.evaluate(() => { const st = Menu.statuses(window.__m1.prog()); return [window.__m1.prog().zabid.stamped, st.zabid, st.hodeidah]; });
  note(after[0] && after[1] === 'cleared' && after[2] === 'soon', 'back on the map: CLEAR stamped on the Souq, the coast road on to Hodeidah open, its mission coming soon (' + JSON.stringify(after) + ')');
  await page.screenshot({ path: shots + 'souq_map_after.png' });
  await page.evaluate(() => window.__m1.toMap('zabid'));
  await sleep(500);
  note((await page.evaluate(() => document.getElementById('bPlay').textContent)) === 'Play again', 'the Souq now offers Play again');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  note((await page.evaluate(() => window.__m1.sim().L.id)) === 'zabid', 'Play again plays the Souq');
  // from the boss's checkpoint, in Arabic: the boss's words on the screen are Arabic
  await page.evaluate(() => window.__m1.begin('zabid', 3));
  await page.evaluate(() => Lang.set('ar'));
  const ar = await page.evaluate(() => ['THE SOUQ', 'THE SCALE', 'ACHOO!', 'BARRICADE {0}', 'STEP OUT FROM UNDER!', 'NOW! HIT HIM!', 'WEIGHMASTER', 'PORTER', 'SHOPKEEPER', 'The rooftops', 'Scale broken in',
    'SHOOT THE SACKS!', 'JUMP ON THE PAN!', 'KEEP CLEAR OF THE PAN!', 'OUT COME THE WEIGHTS', 'A CHAIN HAS SNAPPED', 'WHAM!', 'BONK!',
    'Crouch and shoot a spice sack: a Dhanab who sneezes cannot fight', 'Jump the gaps between the roofs'].filter(k => !Lang.isArabic(T(k))));
  note(!ar.length, 'the Souq\'s words have Arabic' + (ar.length ? ': not ' + ar.join(', ') : ''));
  await page.evaluate(() => { const bot = window.__mkBot({}); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; });
  for (let k = 0; k < 60; k++) { await sleep(400); const b = await page.evaluate(() => window.__m1.sim().boss && window.__m1.sim().boss.st); if (b === 'rise' || b === 'aim') break; }
  await page.screenshot({ path: shots + 'souq_boss_ar.png' });
  await page.evaluate(() => Lang.set('en'));
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
})();
