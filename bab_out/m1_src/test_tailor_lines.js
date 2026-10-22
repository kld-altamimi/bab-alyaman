// test_tailor_lines.js - the Tailor in a real page (0.5.30): from the covered market's checkpoint the bot fights him with
// the sound on (guessing at first, so a dummy gets shot); every subtitle is collected, and the Tailor's lines, Yazeed's,
// the Uncle's call and the shop's noises must come (heard, not only read), with his own music and no page errors.
const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const DRIVE = '(function () { var bot = window.__mkBot({ guess: true }); Input.sample = function () { var s = window.__m1.sim(); var i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; })()';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.touchscreen.tap(422, 150);
  await page.waitForFunction(() => window.__m1.woke());
  await page.evaluate(BOT);
  await page.evaluate(() => window.__m1.begin('zabid', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.evaluate(DRIVE);
  const heard = [];
  const t0 = Date.now();
  let last = null, music = null;
  while (Date.now() - t0 < 240000) {
    const q = await page.evaluate(() => { const l = window.__m1.line(); const s = window.__m1.sim(); return { l: l ? l.who + ' | ' + l.text : null, st: window.__m1.state(), status: s ? s.status : null, boss: s && s.boss ? s.boss.st : null, mus: Sound.playing() }; });
    if (q.l && q.l !== last) { heard.push(q.l); last = q.l; }
    if (q.boss === 'hunt' && !music) music = q.mus;
    if (q.st === 'over') { await page.tap('#bContinue'); continue; }
    if (q.status === 'clear' || q.st === 'results') break;
    await sleep(100);
  }
  console.log(heard.map(h => '  ' + h).join('\n'));
  const done = await page.evaluate(() => { const s = window.__m1.sim(); return s && s.status; });
  note(done === 'clear', 'the bot beat the Tailor in the page (' + done + ')');
  note(music === 'tailor', 'with his own music (' + music + ')');
  const want = [[/^TAILOR \| Welcome! Everything here is made to measure\. Including you\.$/, 'the Tailor says hello'], [/^YAZEED \| They're all wearing the same coat\.$/, 'Yazeed sees the trouble'],
                [/^THE UNCLE \| The spice is mine\. Hide it where nobody looks\.$/, 'the Uncle calls'], [/^TAILOR \| I'm a dummy! Dummies don't talk!$/, 'found out, he tries being a dummy'],
                [/^TAILOR \| Not the silk!$/, 'a dummy shot: not the silk'], [/^TAILOR \| More dummies! I have plenty\.$/, 'the spare dummy comes in'],
                [/^TAILOR \| Cover them! Cover everything!$/, 'the sheets go over'], [/^TAILOR \| All right! The coat is on the house\.$/, 'he gives up']];
  for (const [re, what] of want) note(heard.some(h => re.test(h)), what);
  note(!heard.some(h => /WEIGHMASTER|PORTER|scale/i.test(h)), 'nothing from the Great Scale');
  const counts = await page.evaluate(() => { const c = Sound.counts(); return ['tl_welcome', 'yazeed_coat', 'uncle_spice', 'tl_dummy', 'tl_silk', 'tl_more', 'tl_cover', 'tl_surrender', 'tl_ow', 'tl_whoa',
    'snip', 'rip', 'pins', 'clatter', 'whoosh'].map(k => k + ':' + (c[k] || 0)); });
  note(counts.every(c => +c.split(':')[1] >= 1), 'and they are heard, not only read: ' + counts.join(' '));
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
