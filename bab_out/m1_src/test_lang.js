// test_lang.js - Arabic (0.3.21): a browser set to Arabic gets the game in Arabic from the first screen; the panels read
// right to left and still fit on a phone on its side; the picture's words (HUD, banners, subtitles, the map) are drawn
// in Arabic; the switch in the options goes back to English and is remembered; photographs of every screen for a look.
const { chromium } = require('playwright');
const fs = require('fs');
const shots = '/home/claude/bab_out/m1_src/shots/lang/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const DRIVE = '(function () { var bot = window.__mkBot({}); Input.sample = function () { var s = window.__m1.sim(); var i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; })()';
fs.mkdirSync(shots, { recursive: true });
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
const AR = /[؀-ۿ]/;
// every bit of text in the panels that is still English (no Arabic in it, Latin letters in it) while the game is Arabic;
// the language switch (data-fixed) and the phone report's own text are English on purpose
const englishLeft = page => page.evaluate(() => {
  const left = [], w = document.createTreeWalker(document.getElementById('ui'), NodeFilter.SHOW_TEXT, null);
  let n;
  while ((n = w.nextNode())) {
    const t = n.nodeValue, p = n.parentNode;
    if (!/[A-Za-z]/.test(t) || /[\u0600-\u06FF]/.test(t)) continue;
    if (p.closest('[data-fixed], .rep pre, .rep textarea, .rep code, script, style')) continue;
    if (p.closest('#mEye, #rPar')) continue;      // placeholders, written over (in Arabic) before their panel shows
    if (/^\s*(V?[0-9.:]+|FPS|Enter|Escape|[A-Z])\s*$/.test(t)) continue;
    left.push((p.id ? '#' + p.id : p.tagName.toLowerCase() + (p.className ? '.' + p.className : '')) + ': ' + t.trim().slice(0, 60));
  }
  return left;
});
const logos = page => page.evaluate(async () => {
  const seen = {}, o = Render.spr;
  Render.spr = function (n) { if (/^menu_logo/.test(n)) seen[n] = 1; return o.apply(this, arguments); };
  await new Promise(r => setTimeout(r, 400));
  Render.spr = o;
  return Object.keys(seen).join();
});
const fits = (page, id) => page.evaluate(id => { const p = document.getElementById(id), r = p.getBoundingClientRect(); return { sh: p.scrollHeight, ch: p.clientHeight, sw: p.scrollWidth, cw: p.clientWidth, bottom: r.bottom, ih: innerHeight, dir: p.closest('#ui').dir }; }, id);
async function open(browser, locale, vp) {
  const ctx = await browser.newContext({ viewport: vp || { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: locale });
  const page = await ctx.newPage();
  page.errors = [];
  page.on('pageerror', e => page.errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) page.errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  return { ctx, page };
}
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  // ---------------------------------------------------------------- an Arabic phone
  let { ctx, page } = await open(browser, 'ar-YE');
  note((await page.evaluate(() => window.__m1.lang())) === 'ar', 'a browser in Arabic gets the game in Arabic');
  await page.touchscreen.tap(422, 150);
  await page.waitForFunction(() => window.__m1.woke());
  await sleep(600);
  let t = await page.evaluate(() => ({ start: document.getElementById('bStart').textContent, opts: document.getElementById('bOpts').textContent, dir: document.getElementById('ui').dir, lang: document.documentElement.lang }));
  note(AR.test(t.start) && AR.test(t.opts) && t.dir === 'rtl' && t.lang === 'ar', 'home: the buttons are in Arabic, the panels read right to left (' + JSON.stringify(t) + ')');
  await page.screenshot({ path: shots + 'ar_home.png' });
  let lg = await logos(page);
  note(lg === 'menu_logo_ar', 'the Arabic home screen shows the Arabic logo (' + lg + ')');
  let left = await englishLeft(page);
  note(left.length === 0, 'no English left anywhere in the panels' + (left.length ? ': ' + left.join(' | ') : ''));
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(400);
  let f = await fits(page, 'pOpts');
  t = await page.evaluate(() => ({ h: document.getElementById('hOpts').textContent, hold: document.getElementById('segHold').textContent, note: document.querySelector('#pOpts .scheme-note').textContent, how: document.getElementById('howTo').textContent.slice(0, 20), sound: document.getElementById('bSound3').textContent, en: document.getElementById('langEn').textContent, ar: document.getElementById('langAr').getAttribute('aria-checked') }));
  note(AR.test(t.h) && AR.test(t.hold) && AR.test(t.note) && AR.test(t.how) && AR.test(t.sound) && t.en === 'English' && t.ar === 'true', 'options: every label in Arabic, the switch on العربية (' + JSON.stringify(t) + ')');
  note(f.sh <= f.ch + 1 && f.sw <= f.cw + 1 && f.bottom <= f.ih, 'the Arabic options fit on a phone on its side (' + JSON.stringify(f) + ')');
  await page.screenshot({ path: shots + 'ar_options.png' });
  await page.tap('#bBack');
  await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(900);
  f = await fits(page, 'pMap');
  t = await page.evaluate(() => ({ eye: document.getElementById('mEye').textContent, name: document.getElementById('mName').textContent, brief: document.getElementById('mBrief').textContent.slice(0, 30), ahead: document.getElementById('mAhead').textContent, play: document.getElementById('bPlay').textContent, from: [...document.querySelectorAll('#mFrom option')].map(o => o.textContent).join('|'), fromHidden: document.getElementById('mFromRow').hidden, cps: [...document.querySelectorAll('#mCps li')].map(o => o.textContent).join('|') }));
  note(AR.test(t.eye) && AR.test(t.name) && AR.test(t.brief) && AR.test(t.ahead) && AR.test(t.play) && (t.fromHidden || (AR.test(t.from) && !/[A-Za-z]/.test(t.from))) && AR.test(t.cps), 'the mission card: name, briefing, what is ahead, Start, the checkpoints (the start picker is for developers only since 0.6.38) (' + JSON.stringify(t) + ')');
  note(f.bottom <= f.ih + 1, 'the Arabic card sits on screen (' + JSON.stringify(f) + ')');
  await page.screenshot({ path: shots + 'ar_map.png' });
  await page.tap('#bBriefs');
  await page.waitForFunction(() => window.__m1.state() === 'brief');
  await sleep(400);
  t = await page.evaluate(() => [...document.querySelectorAll('#bList .bname')].map(x => x.textContent).join('|'));
  note(AR.test(t) && !/[A-Za-z]/.test(t), 'the briefings list every mission by its Arabic name (' + t + ')');
  await page.screenshot({ path: shots + 'ar_briefs.png' });
  await page.tap('#bBriefBack');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  // into the mission: the HUD, a subtitle, the pause menu
  await page.evaluate(BOT);
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(300);
  await page.screenshot({ path: shots + 'ar_start.png' });
  await page.evaluate(DRIVE);
  const t0 = Date.now();
  let gotLine = null;
  while (Date.now() - t0 < 20000) {
    const l = await page.evaluate(() => { const l = window.__m1.line(); return l ? l.who + ' | ' + l.text : null; });
    if (l && AR.test(l)) { gotLine = l; await page.screenshot({ path: shots + 'ar_play.png' }); break; }
    await sleep(100);
  }
  note(!!gotLine && !/[A-Za-z]/.test(gotLine), 'in play a line is spoken in Arabic, the speaker named in Arabic (' + gotLine + ')');
  await page.keyboard.press('p');
  await page.waitForFunction(() => window.__m1.state() === 'pause');
  await sleep(300);
  f = await fits(page, 'pPause');
  t = await page.evaluate(() => ({ h: document.getElementById('hPause').textContent, skip: document.getElementById('bSkip').textContent, quit: document.getElementById('bQuit').textContent }));
  note(AR.test(t.h) && AR.test(t.skip) && AR.test(t.quit) && f.sh <= f.ch + 1, 'the pause menu in Arabic, and it fits (' + JSON.stringify([t, f.sh, f.ch]) + ')');
  await page.screenshot({ path: shots + 'ar_pause.png' });
  // out of lives: the game-over panel in Arabic, then Continue
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  await page.evaluate(() => { window.__m1.sim().status = 'over'; });
  await page.waitForFunction(() => window.__m1.state() === 'over');
  await sleep(500);
  t = await page.evaluate(() => document.getElementById('pOver').textContent.replace(/\s+/g, ' ').trim());
  left = await englishLeft(page);
  f = await fits(page, 'pOver');
  note(AR.test(t) && !/[A-Za-z]/.test(t) && f.sh <= f.ch + 1, 'game over in Arabic, every word, and it fits (' + t + ')');
  await page.screenshot({ path: shots + 'ar_over.png' });
  await page.tap('#bContinue');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  // the switch back to English, kept across a reload
  await page.evaluate(() => window.__m1.setLang('en'));
  await sleep(200);
  await page.keyboard.press('p');
  await page.waitForFunction(() => window.__m1.state() === 'pause');
  t = await page.evaluate(() => ({ h: document.getElementById('hPause').textContent, lang: window.__m1.lang(), dir: document.getElementById('ui').dir }));
  note(t.h === 'Paused' && t.lang === 'en' && t.dir === 'ltr', 'switched to English: the pause menu says Paused, left to right');
  await page.reload();
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  note((await page.evaluate(() => window.__m1.lang())) === 'en', 'after a reload the Arabic browser still gets English: the choice is kept');
  note(page.errors.length === 0, 'no errors on the page' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await ctx.close();
  // ---------------------------------------------------------------- the end of a mission: the boss, the results, the map after
  ({ ctx, page } = await open(browser, 'ar-YE'));
  await page.evaluate(() => window.__m1.wake());
  await page.evaluate(BOT);
  await page.evaluate(() => window.__m1.begin('m1', 4));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.evaluate(DRIVE);
  const t1 = Date.now();
  let bossShot = false, bossLabel = null, lowLives = false;
  while (Date.now() - t1 < 300000) {
    const q = await page.evaluate(() => { const s = window.__m1.sim(); return { state: window.__m1.state(), boss: s.boss ? s.boss.st : null, label: s.boss ? s.boss.label : null }; });
    if (!bossShot && (q.boss === 'idle' || q.boss === 'bomb')) { bossShot = true; bossLabel = q.label; await sleep(400); await page.screenshot({ path: shots + 'ar_boss.png' }); }
    if (q.state === 'over') { await page.tap('#bContinue'); lowLives = true; }
    if (q.state === 'results') break;
    await sleep(150);
  }
  note((await page.evaluate(() => window.__m1.state())) === 'results', 'the bot cleared the missile battery in Arabic' + (lowLives ? ' (needed a continue)' : ''));
  note(bossShot && AR.test(await page.evaluate(l => T(l), bossLabel)), 'the boss was named in Arabic on the HUD (' + bossLabel + ' → ' + (await page.evaluate(l => T(l), bossLabel)) + ')');
  await sleep(600);
  f = await fits(page, 'pDone');
  // (the results as 0.7.42 has them: the time, the total and its breakdown, the two badges, Advance; the facts in the
  // developer's run details)
  t = await page.evaluate(() => ({ h: document.getElementById('hDone').textContent, total: document.querySelector('#pDone .total').textContent.replace(/\s+/g, ' ').trim(), badges: [...document.querySelectorAll('#rBadges .badge')].map(b => b.textContent.replace(/\s+/g, ' ').trim()).join(' / '), facts: document.querySelector('#pDone .facts').textContent.replace(/\s+/g, ' ').trim().slice(0, 80), map: document.getElementById('bToMap').textContent }));
  note(AR.test(t.h) && AR.test(t.total) && AR.test(t.badges) && AR.test(t.facts) && AR.test(t.map) && !/[A-Za-z]/.test(t.total + t.badges + t.map), 'the results in Arabic: heading, total, badges, facts, button (' + JSON.stringify(t) + ')');
  note(f.sh <= f.ch + 1 && f.sw <= f.cw + 1 && f.bottom <= f.ih + 1, 'the results fit on a phone on its side (' + JSON.stringify(f) + ')');
  await page.screenshot({ path: shots + 'ar_results.png' });
  await page.tap('#bToMap');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.waitForFunction(() => window.__m1.menu().rv > 40, null, { timeout: 8000 });
  await page.screenshot({ path: shots + 'ar_map_stamp.png' });
  await page.waitForFunction(() => window.__m1.menu().rv < 0, null, { timeout: 8000 });
  await sleep(500);
  t = await page.evaluate(() => ({ name: document.getElementById('mName').textContent, eye: document.getElementById('mEye').textContent, play: document.getElementById('bPlay').textContent, best: (document.querySelector('#pMap .best') || {}).textContent }));
  note(AR.test(t.name) && AR.test(t.eye) && AR.test(t.play) && !/[A-Za-z]/.test(t.name + t.eye + t.play), 'back on the map, the Coffee Port offered in Arabic (' + JSON.stringify(t) + ')');
  await page.screenshot({ path: shots + 'ar_map_after.png' });
  note(page.errors.length === 0, 'no errors through the fight' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await ctx.close();
  // ---------------------------------------------------------------- an English phone, switching in the options
  ({ ctx, page } = await open(browser, 'en-GB'));
  note((await page.evaluate(() => window.__m1.lang())) === 'en', 'an English browser gets English');
  lg = await logos(page);
  note(lg === 'menu_logo', 'and the English logo (' + lg + ')');
  await page.evaluate(() => window.__m1.wake());
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await page.tap('#langAr');
  await sleep(300);
  t = await page.evaluate(() => ({ h: document.getElementById('hOpts').textContent, lang: window.__m1.lang() }));
  note(AR.test(t.h) && t.lang === 'ar', 'the switch in the options turns the page Arabic at once (' + t.h + ')');
  await page.tap('#bBack');
  await page.waitForFunction(() => window.__m1.state() === 'home');
  await sleep(300);
  await page.screenshot({ path: shots + 'ar_home_switched.png' });
  // a small phone: the Arabic options and card still fit
  await ctx.close();
  ({ ctx, page } = await open(browser, 'ar', { width: 568, height: 320 }));
  await page.evaluate(() => window.__m1.wake());
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(300);
  f = await fits(page, 'pOpts');
  note(f.sw <= f.cw + 1 && f.bottom <= f.ih + 1, 'on a small phone the Arabic options stay on screen, nothing sideways (' + JSON.stringify(f) + ')');
  await page.screenshot({ path: shots + 'ar_options_small.png' });
  await page.tap('#bBack');
  await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(600);
  f = await fits(page, 'pMap');
  note(f.sw <= f.cw + 1 && f.bottom <= f.ih + 1, 'and so does the card (' + JSON.stringify(f) + ')');
  await page.screenshot({ path: shots + 'ar_map_small.png' });
  // the HUD on the small phone, with auto-fire on so the AUTO mark shows: photographed for a look (Arabic, then English)
  for (const code of ['ar', 'en']) {
    await page.evaluate(c => window.__m1.setLang(c), code);
    await page.evaluate(() => document.getElementById('bOpts2').click());     // (the nav row is folded away on a short screen)
    await page.waitForFunction(() => window.__m1.state() === 'opts');
    await page.tap('#segAuto');
    await page.tap('#bBack');
    await page.waitForFunction(() => window.__m1.state() === 'map');
    await page.tap('#bPlay');
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await sleep(1800);
    await page.screenshot({ path: shots + code + '_play_small.png' });
    await page.keyboard.press('p');
    await page.waitForFunction(() => window.__m1.state() === 'pause');
    await page.tap('#bQuit');
    await page.waitForFunction(() => window.__m1.state() === 'map');
  }
  note(page.errors.length === 0, 'no errors on the small page' + (page.errors.length ? ': ' + page.errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
