// test_scale_lines.js - the Great Scale in a real page (0.5.29): from the covered market's checkpoint the careful bot
// fights it with the sound on; every subtitle is collected, and the scale's lines, the Uncle's call and its new noises
// must come (heard, not only read), with no page errors.
const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const DRIVE = '(function () { var bot = window.__mkBot({}); Input.sample = function () { var s = window.__m1.sim(); var i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; })()';
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
  while (Date.now() - t0 < 200000) {
    const q = await page.evaluate(() => { const l = window.__m1.line(); const s = window.__m1.sim(); return { l: l ? l.who + ' | ' + l.text : null, st: window.__m1.state(), status: s ? s.status : null, boss: s && s.boss ? s.boss.st : null, mus: Sound.playing() }; });
    if (q.l && q.l !== last) { heard.push(q.l); last = q.l; }
    if (q.boss === 'idle' && !music) music = q.mus;
    if (q.status === 'clear' || q.st === 'results') break;
    await sleep(100);
  }
  console.log(heard.map(h => '  ' + h).join('\n'));
  const done = await page.evaluate(() => { const s = window.__m1.sim(); return s && s.status; });
  note(done === 'clear', 'the bot beat the Great Scale in the page (' + done + ')');
  note(music === 'scale', 'with its own music (' + music + ')');
  const want = [[/^YAZEED \| Is that\.\.\. a set of scales\?$/, 'Yazeed sees the scale'], [/^WEIGHMASTER \| Everything in this souq gets weighed/, 'the Weighmaster introduces himself'],
                [/^THE UNCLE \| The spice is mine\. Every gram of it\. Weigh it again\.$/, 'the Uncle calls'], [/^WEIGHMASTER \| Porters!/, 'he shouts for his porters'],
                [/^WEIGHMASTER \| Have a weight!/, 'his weights come out'], [/^WEIGHMASTER \| My chain!/, 'his chain snaps'], [/^WEIGHMASTER \| Fine\. FINE\./, 'he gives up']];
  for (const [re, what] of want) note(heard.some(h => re.test(h)), what);
  note(!heard.some(h => /PUSHER|cannon/i.test(h)), 'nothing from the Spice Cannon');
  const counts = await page.evaluate(() => { const c = Sound.counts(); return ['yazeed_scale', 'wm_behold', 'uncle_spice', 'wm_whoa', 'wm_ow', 'wm_surrender'].map(k => k + ':' + (c[k] || 0)); });
  note(counts.every(c => +c.split(':')[1] >= 1), 'and they are heard, not only read: ' + counts.join(' '));
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
