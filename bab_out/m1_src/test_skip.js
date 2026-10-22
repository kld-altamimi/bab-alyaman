// test_skip.js - skipping in a real browser (build 13), on a phone on its side and upright, from a fresh save: the
// card's "From" list of checkpoints, a run from the battery (a practice run: the clear counts, no best, no medals), Play again from
// the same checkpoint, the Coffee Port played before its road is open ("Skip ahead", from the old lighthouse),
// the pause menu's skip from checkpoint to checkpoint (score, clock and lives kept), Start over, and the keys.
const { chromium } = require('playwright');
const fs = require('fs');
const shots = '/home/claude/bab_out/m1_src/shots/skip/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const DRIVE = '(function () { var bot = window.__mkBot({}); Input.sample = function () { var s = window.__m1.sim(); var i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; })()';
fs.mkdirSync(shots, { recursive: true });
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
const st = page => page.evaluate(() => { const s = window.__m1.sim(); return { state: window.__m1.state(), cur: window.__m1.cur(), id: s ? s.L.id : null, zone: s ? s.zone : -1, mode: s ? s.mode : null, time: s ? s.time : 0, score: s ? s.score : 0, lives: s ? s.p.lives : 0, run: window.__m1.run(), music: Sound.playing(), boss: s && s.boss ? s.boss.st : null }; });
// (since 0.6.38 the From list is for developers only: these runs have Developer switched on, as Khaled's own do)
async function newPage(browser, vp, plain) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  if (!plain) await ctx.addInitScript(() => { try { if (!sessionStorage.getItem('devset')) { const o = JSON.parse(localStorage.getItem('strait-m1') || '{}'); o.dev = true; localStorage.setItem('strait-m1', JSON.stringify(o)); sessionStorage.setItem('devset', '1'); } } catch (e) {} });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', e => page.errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource/.test(msg.text())) page.errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(700);
  return { ctx, page };
}
async function pauseNow(page) { await page.keyboard.press('p'); await page.waitForFunction(() => window.__m1.state() === 'pause'); await sleep(150); }
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  // ---------------------------------------------------------------- a player's card has no From list (developers only)
  {
    const pl = await newPage(browser, { width: 844, height: 390 }, true);
    note(await pl.page.evaluate(() => document.getElementById('mFromRow').hidden), 'with Developer off, the card has no From list: a mission starts at its start');
    await pl.ctx.close();
  }
  // ---------------------------------------------------------------- a fresh save, on its side
  let { ctx, page } = await newPage(browser, { width: 844, height: 390 });
  const c1 = await page.evaluate(() => ({ sel: window.__m1.menu().sel, row: !document.getElementById('mFromRow').hidden, opts: [...document.querySelectorAll('#mFrom option')].map(o => o.textContent), v: document.getElementById('mFrom').value, btn: document.getElementById('bPlay').textContent }));
  note(c1.sel === 'm1' && c1.row && c1.opts.join('|') === 'Landfall|The fishing camp|Container beach|The coast road|The battery' && c1.v === '0' && c1.btn === 'Start mission',
    'the Strait\'s card starts it from Landfall, with its five checkpoints to choose from (' + c1.opts.join(', ') + ')');
  const box = await page.evaluate(() => { const a = document.getElementById('mFrom').getBoundingClientRect(), b = document.getElementById('bPlay').getBoundingClientRect(), p = document.getElementById('pMap').getBoundingClientRect(); return { sel: [a.top, a.bottom, a.height], btn: [b.top, b.bottom], panel: [p.top, p.bottom], ih: innerHeight }; });
  note(box.sel[0] >= box.panel[0] && box.btn[1] <= box.panel[1] && box.btn[1] <= box.ih && box.sel[2] >= 40, 'on its side, the list and Start mission both sit inside the card, on screen (' + JSON.stringify(box) + ')');
  await page.screenshot({ path: shots + 'card_land.png' });
  // keys: arrows in the list choose in the list, not along the map
  await page.focus('#mFrom');
  await page.keyboard.press('ArrowDown');
  await sleep(200);
  const k1 = await page.evaluate(() => [window.__m1.menu().sel, document.getElementById('mFrom').value]);
  note(k1[0] === 'm1', 'with the list in focus, the arrow keys leave the map alone (still on ' + k1[0] + ', list at ' + k1[1] + ')');
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  // start at the battery
  await page.selectOption('#mFrom', '4');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(400);
  let s = await st(page);
  note(s.id === 'm1' && s.zone === 4 && s.run.from === 4 && !s.run.skipped && s.time < 2 && s.mode === 'foot', 'Start mission from the battery starts there, on foot (' + JSON.stringify([s.id, s.zone, s.run, s.mode]) + ')');
  await page.screenshot({ path: shots + 'battery_start.png' });
  await pauseNow(page);
  note(await page.evaluate(() => document.getElementById('bSkip').hidden), 'at the last checkpoint the pause menu has nothing to skip to');
  await page.tap('#bResume');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  // the bot finishes it
  await page.evaluate(BOT); await page.evaluate(DRIVE);
  let seenBoss = null;
  for (let k = 0; k < 240; k++) {
    await sleep(500);
    s = await st(page);
    if (s.state === 'over') { await page.tap('#bContinue'); continue; }
    if (s.boss === 'idle' || (s.boss && !seenBoss)) seenBoss = seenBoss || s.music;
    if (s.state === 'results') break;
  }
  const r1 = await page.evaluate(() => [window.__m1.state(), document.getElementById('rBest').textContent, document.getElementById('rMedals').textContent, JSON.stringify(window.__m1.prog().m1)]);
  note(r1[0] === 'results', 'the bot beat the boat from there (' + r1[0] + ', boss music ' + seenBoss + ')');
  note(/^Started at the battery, so this run is not kept as a best\./.test(r1[1]) && /^Medals are won on a run from the start with nothing skipped\./.test(r1[2]), 'the results say it was a practice run: "' + r1[1] + '" / "' + r1[2] + '"');
  const pm1 = JSON.parse(r1[3]);
  note(pm1.cleared && !pm1.best && !pm1.ace && !pm1.lib && !pm1.stamped, 'the Strait counts as cleared, with no best and no medals kept: ' + r1[3]);
  await page.screenshot({ path: shots + 'battery_results.png' });
  // Play again starts at the battery again
  await page.tap('#bAgain');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(300);
  s = await st(page);
  note(s.zone === 4 && s.run.from === 4 && s.time < 2, 'Play again starts at the battery again (zone ' + s.zone + ')');
  await pauseNow(page);
  await page.tap('#bQuit');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.waitForFunction(() => window.__m1.menu().rv > 30, null, { timeout: 9000 });
  await page.waitForFunction(() => window.__m1.menu().rv < 0, null, { timeout: 12000 });
  await sleep(400);
  const a1 = await page.evaluate(() => { const q = Menu.statuses(window.__m1.prog()); return [q.m1, q.mocha, window.__m1.prog().m1.stamped]; });
  note(a1[0] === 'cleared' && a1[1] === 'open' && a1[2], 'back on the map the Strait is stamped CLEAR and the Coffee Port opens (' + a1.join(', ') + ')');
  // the card remembers the start chosen for each mission
  await page.evaluate(() => window.__m1.toMap('m1'));
  await sleep(400);
  note((await page.evaluate(() => document.getElementById('mFrom').value)) === '4', 'the Strait\'s card still says the battery');
  // ---------------------------------------------------------------- the pause menu's skip, through the whole Strait
  await page.selectOption('#mFrom', '0');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(1500);
  const labels = [], walk = [];
  for (let z = 0; z < 4; z++) {
    const before = await st(page);
    await pauseNow(page);
    const sk = await page.evaluate(() => [document.getElementById('bSkip').hidden, document.getElementById('bSkip').textContent]);
    labels.push(sk[1]);
    if (z === 0) await page.screenshot({ path: shots + 'pause_skip.png' });
    await page.tap('#bSkip');
    await page.waitForFunction(() => window.__m1.state() === 'play');
    await sleep(900);
    const now = await st(page);
    walk.push([now.zone, now.mode, now.score >= before.score, now.time >= before.time, now.lives === before.lives, now.run.skipped]);
    if (z === 2) await page.screenshot({ path: shots + 'skip_road.png' });
  }
  note(JSON.stringify(labels) === JSON.stringify(['Skip to the fishing camp', 'Skip to Container beach', 'Skip to the coast road', 'Skip to the battery']), 'the pause menu names the next checkpoint each time (' + labels.join(', ') + ')');
  note(walk.map(w => w[0]).join() === '1,2,3,4' && walk[2][1] === 'drive' && walk[3][1] === 'foot' && walk.every(w => w[2] && w[3] && w[4] && w[5]), 'each skip goes one checkpoint on (into the pickup at the coast road), keeping the score, the clock and the lives: ' + JSON.stringify(walk));
  await pauseNow(page);
  const rep = await page.evaluate(() => [document.getElementById('bSkip').hidden, document.getElementById('report').textContent.split('\n')[1]]);
  note(rep[0] && /^Mission: The Strait, checkpoints skipped, now at the battery$/.test(rep[1]), 'at the battery there is nothing left to skip, and the phone report says how the run went: "' + rep[1] + '"');
  await page.tap('#bRestart');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  await sleep(300);
  s = await st(page);
  note(s.zone === 0 && s.run.from === 0 && !s.run.skipped && s.time < 2, 'Start over goes back to where the run began, Landfall, and the run is a whole one again');
  note(page.errors.length === 0, 'no errors on the page' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await ctx.close();
  // ---------------------------------------------------------------- a fresh save again: skip ahead to the Coffee Port
  ({ ctx, page } = await newPage(browser, { width: 844, height: 390 }));
  await page.evaluate(() => window.__m1.toMap('mocha'));
  await sleep(500);
  const c2 = await page.evaluate(() => ({ eye: document.getElementById('mEye').textContent, btn: document.getElementById('bPlay').textContent, dis: document.getElementById('bPlay').disabled, ahead: document.getElementById('mAhead').textContent, opts: [...document.querySelectorAll('#mFrom option')].map(o => o.textContent), row: !document.getElementById('mFromRow').hidden }));
  note(/Locked/.test(c2.eye) && c2.btn === 'Skip ahead' && !c2.dis && /Clear the Strait to open the road here, or skip ahead and play it now\./.test(c2.ahead) && c2.row && c2.opts.length === 4,
    'the Coffee Port, locked, offers Skip ahead, from any of its four checkpoints (' + c2.btn + '; ' + c2.ahead + ')');
  await page.screenshot({ path: shots + 'card_locked.png' });
  // a second tap on the map still only reads a locked mission
  // (Ibb: Taiz has been built since 0.9.50, its flying test range)
  const ibb = await page.evaluate(() => { window.__m1.toMap('ibb'); return [document.getElementById('bPlay').textContent, document.getElementById('bPlay').disabled, document.getElementById('mFromRow').hidden]; });
  note(ibb[0] === 'Coming soon' || ibb[0] === 'Locked', 'a mission not built yet offers nothing to skip to (' + ibb.join(', ') + ')');
  note(ibb[1] && ibb[2], 'its button is off and it has no Start at list');
  // (the Souq is built: before its road is open it offers Skip ahead, as the Coffee Port does)
  const zabid = await page.evaluate(() => { window.__m1.toMap('zabid'); return [document.getElementById('bPlay').textContent, document.getElementById('bPlay').disabled, document.getElementById('mFromRow').hidden, document.querySelectorAll('#mFrom option').length]; });
  note(zabid[0] === 'Skip ahead' && !zabid[1] && !zabid[2] && zabid[3] === 4, 'the Souq, built but its road not open yet, offers Skip ahead from its four checkpoints (' + zabid.join(', ') + ')');
  await page.evaluate(() => window.__m1.toMap('mocha'));
  await sleep(400);
  await page.selectOption('#mFrom', '3');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(300);
  s = await st(page);
  note(s.id === 'mocha' && s.cur === 'mocha' && s.zone === 3 && s.run.from === 3, 'Skip ahead starts the Coffee Port at the old lighthouse (' + JSON.stringify([s.id, s.zone]) + ')');
  await page.evaluate(BOT); await page.evaluate(DRIVE);
  let roast = null;
  for (let k = 0; k < 60 && !roast; k++) { await sleep(500); s = await st(page); if (s.boss && s.boss !== 'intro') roast = s.music; }
  note(roast === 'roaster', 'the Big Roaster comes, with its music (' + roast + ')');
  await page.screenshot({ path: shots + 'roaster_skip.png' });
  await pauseNow(page);
  await page.tap('#bQuit');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(500);
  const a2 = await page.evaluate(() => { const q = Menu.statuses(window.__m1.prog()); return [q.mocha, window.__m1.prog().mocha.runs, window.__m1.prog().mocha.reached]; });
  note(a2[0] === 'locked' && a2[1] === 1 && a2[2] === 3, 'quitting it leaves the Coffee Port locked as before, with the go counted (' + a2.join(', ') + ')');
  note(page.errors.length === 0, 'no errors on the page' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await ctx.close();
  // ---------------------------------------------------------------- upright
  ({ ctx, page } = await newPage(browser, { width: 390, height: 844 }));
  const box2 = await page.evaluate(() => { const on = r => r.left >= -0.5 && r.top >= -0.5 && r.right <= innerWidth + 0.5 && r.bottom <= innerHeight + 0.5;
    const a = document.getElementById('mFrom').getBoundingClientRect(), b = document.getElementById('bPlay').getBoundingClientRect();
    return { rot: window.__m1.geo().rot, sel: on(a), btn: on(b), long: Math.max(a.width, a.height) }; });
  note(box2.rot && box2.sel && box2.btn && box2.long > 150, 'held upright, the game is turned on its side, and the list and Start mission are on screen (' + JSON.stringify(box2) + ')');
  await page.screenshot({ path: shots + 'card_port.png' });
  note(page.errors.length === 0, 'no errors on the page' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await ctx.close();
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
})();
