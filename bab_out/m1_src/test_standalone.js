// test_standalone.js - the zipped build, unpacked and served as any web host would: does it start, sound and play?
const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const m = fs.readFileSync(GAME + 'tools/bot.js', 'utf8').match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8767/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 15000 });
  const head = await page.evaluate(() => ({ title: document.title, titleInHead: !!document.head.querySelector('title'), styleInHead: document.head.querySelectorAll('style').length, sw: document.documentElement.scrollWidth, iw: innerWidth, sh: document.documentElement.scrollHeight, ih: innerHeight }));
  console.log('document:', JSON.stringify(head));
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
  await page.evaluate(BOT);
  await page.evaluate(() => { const bot = window.__mkBot({ auto: false }); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; });
  const t0 = Date.now(); let st = '';
  while (Date.now() - t0 < 120000) { st = await page.evaluate(() => window.__m1.state()); if (st === 'over') await page.tap('#bContinue'); if (st === 'results') break; await sleep(250); }
  const r = await page.evaluate(() => ({ state: window.__m1.state(), time: window.__m1.sim().time, snd: Sound.info(), counts: Object.keys(Sound.counts()).length }));
  console.log('played through: state ' + r.state + ', clock ' + r.time.toFixed(1) + ' s, sound ' + r.snd.state + ' with files ' + r.snd.decoded + ', ' + r.counts + ' different sounds played; errors: ' + (errors.length ? errors.join(' | ') : 'none'));
  await browser.close();
})();
