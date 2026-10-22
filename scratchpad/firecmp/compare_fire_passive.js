// compare_fire.js - do the enemies on foot fire any differently in the live build after Taiz (B: 0.13.70) than before it
// (A: 0.12.67)? The same seeded smart bot plays the Strait and the Coffee Port in each page; every enemy shot is counted
// by kind, and the whole event stream is hashed in 10-second windows to find the first moment the two games differ.
const { chromium } = require('playwright');
const fs = require('fs');
const BOT = fs.readFileSync('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/bot.js', 'utf8');
const SMART = BOT.slice(BOT.indexOf('function smartBot(opts) {'), BOT.indexOf('function run(bot, opts) {'));
const MUL = BOT.slice(BOT.indexOf('function mulberry(a) {'), BOT.indexOf('// ------------------------------------------------------------------ what must always be true'));
async function play(url) {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const page = await (await browser.newContext({ viewport: { width: 844, height: 390 } })).newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(url);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  const out = await page.evaluate(([smart, mul]) => {
    window.__m1.frozen = true;
    const T = Sim.T, res = {};
    const mulberry = eval('(' + mul.replace(/^function mulberry/, 'function') + ')');
    const smartBot = eval('(' + smart.replace(/^function smartBot/, 'function') + ')');
    const kinds = { smart: () => smartBot({}), idle: () => () => ({ mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false }), walker: () => { let t = 0; return () => ({ mx: (t++ % 240) < 200 ? 1 : 0, my: 0, fire: false, jump: (t % 90) === 0, grenade: false, auto: false }); } };
    for (const [name, L] of [['m1', LEVEL], ['mocha', LEVEL_MOCHA]]) for (const [kind, zone] of [['idle', 0], ['idle', 1], ['idle', 2], ['walker', 0], ['walker', 2]]) { const seed = 5;
      let s = Sim.create(L, { viewW: 468, seed: seed, zone: zone }), cont = 0;
      const bot = kinds[kind](), shots = {}, win = [];
      let acc = '', t = 0;
      for (; t < 60 * 90; t++) {
        const inp = bot(s);
        Sim.step(s, inp);
        for (const e of s.events) {
          if (e.t === 'eshot') shots[e.k] = (shots[e.k] || 0) + 1;
          acc += e.t + (e.k || '') + Math.round(e.x || 0) + ',';
        }
        if (t % 600 === 599) { let h = 0; for (let i = 0; i < acc.length; i++) h = (h * 31 + acc.charCodeAt(i)) | 0; win.push(h); acc = ''; }
        if (s.status === 'over') { if (cont >= 3) break; cont++; s = Sim.continueZone(s); }
        if (s.status === 'clear' && s.clearT > 60) break;
      }
      const total = Object.values(shots).reduce((a, b) => a + b, 0);
      res[name + '/' + kind + '@z' + zone] = { ticks: t, status: s.status, continues: cont, total, perMin: +(total / (t / 3600)).toFixed(1), shots, win };
    }
    return res;
  }, [SMART, MUL]);
  await browser.close();
  return { out, errors };
}
(async () => {
  const a = await play('http://127.0.0.1:8795/index.html?internal=1'), b = await play('http://127.0.0.1:8796/index.html?internal=1');
  for (const k of Object.keys(a.out)) {
    const A = a.out[k], B = b.out[k];
    let first = -1; for (let i = 0; i < Math.max(A.win.length, B.win.length); i++) if (A.win[i] !== B.win[i]) { first = i; break; }
    console.log(k.padEnd(16), 'before:', A.total, 'shots in', (A.ticks / 60).toFixed(0) + 's', '(' + A.perMin + '/min,', A.status + ', continues ' + A.continues + ')',
      '| after:', B.total, 'in', (B.ticks / 60).toFixed(0) + 's', '(' + B.perMin + '/min,', B.status + ', continues ' + B.continues + ')',
      '|', first < 0 ? 'the same game, event for event' : 'first differs in the ' + (first * 10) + '-' + (first * 10 + 10) + ' s window');
    if (first >= 0) console.log('          before', JSON.stringify(A.shots), '\n          after ', JSON.stringify(B.shots));
  }
  console.log('page errors:', a.errors.length + b.errors.length ? a.errors.concat(b.errors).join(' | ') : 'none');
})();
