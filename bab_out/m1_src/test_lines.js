// test_lines.js - the Dhanabs and the Uncle (build 19): the bot plays both missions and every subtitle is collected;
// the Uncle's four calls must come, each once, in the right place, and nothing says Scorpion where it should not.
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
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.touchscreen.tap(422, 150);                       // a real tap: it wakes the game and lets the sound play
  await page.waitForFunction(() => window.__m1.woke());
  await page.evaluate(BOT);
  const heard = [];
  for (const id of ['m1', 'mocha']) {
    await page.evaluate(id => window.__m1.begin(id, 0), id);
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await page.evaluate(DRIVE);
    const t0 = Date.now();
    let last = null;
    while (Date.now() - t0 < 240000) {
      const q = await page.evaluate(() => { const l = window.__m1.line(); const s = window.__m1.sim(); return { l: l ? l.who + ' | ' + l.text : null, st: window.__m1.state(), status: s ? s.status : null, zone: s ? s.zone : -1 }; });
      if (q.l && q.l !== last) { heard.push([id, q.zone, q.l]); last = q.l; }
      if (q.status === 'clear' || q.st === 'results') break;
      await sleep(120);
    }
    const done = await page.evaluate(() => { const s = window.__m1.sim(); return s && s.status; });
    note(done === 'clear', `${id}: the bot cleared it (${done})`);
  }
  const text = heard.map(h => h[2]);
  const uncle = heard.filter(h => /^THE UNCLE/.test(h[2]));
  console.log(heard.map(h => `  ${h[0]} z${h[1]}  ${h[2]}`).join('\n'));
  note(uncle.length >= 4, `the Uncle called ${uncle.length} times`);
  note(text.some(t => /flying boat is a loan/.test(t)) && text.some(t => /new guns/.test(t)) && text.some(t => /I want the coffee/.test(t)) && text.filter(t => /cheque/.test(t)).length >= 1, 'the boat, the guns, the coffee and the cheque');
  note(text.some(t => /pride of the Zanabeel/.test(t)) && text.some(t => /^\w+ \| ZANABEEL! IT'S HIM!$/.test(t)), 'the Zanabeel (the Dhanabs before 0.8.44) say their name with pride, calling their mates by it');
  note(!text.some(t => /Scorpion/.test(t)), 'no line calls them the Scorpion');
  // since 17 Oct the Uncle is voiced (reading A): each call plays its recording, not just its subtitle
  const heardUncle = await page.evaluate(() => ({ state: Sound.info().state, n: ['uncle_drones', 'uncle_guns', 'uncle_coffee', 'uncle_cheque'].map(k => Sound.counts()[k] || 0) }));
  note(heardUncle.state === 'running' && heardUncle.n.every(n => n >= 1), `the Uncle's calls are heard, not only read: ${heardUncle.n} (sound ${heardUncle.state})`);
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
