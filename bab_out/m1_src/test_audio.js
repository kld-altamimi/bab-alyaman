// test_audio.js - let the bot play a whole run in the browser while recording what would come out of the loudspeaker, then save it for measuring.
const { chromium } = require('playwright');
const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
const auto = process.argv.includes('auto');
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.evaluate(() => window.__m1.wake());
  if (auto) { await page.tap('#bOpts'); await page.tap('#segAuto'); await page.tap('#bBack'); }
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  // record from the last node before the loudspeaker
  await page.evaluate(() => {
    const t = Sound.tap();
    window.__recs = {};
    for (const k of ['node', 'music', 'sfx', 'voice']) {
      const dest = t.ctx.createMediaStreamDestination();
      t[k].connect(dest);
      const rec = new MediaRecorder(dest.stream, { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 256000 });
      const chunks = [];
      rec.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
      rec.start(500);
      window.__recs[k] = { rec, chunks };
    }
  });
  await page.evaluate(BOT);
  await page.evaluate(a => { const bot = window.__mkBot({ auto: a }); Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; }, auto);
  const t0 = Date.now();
  while (Date.now() - t0 < 120000) {
    const st = await page.evaluate(() => window.__m1.state());
    if (st === 'over') await page.tap('#bContinue');
    if (st === 'results') break;
    await sleep(200);
  }
  await sleep(1500);
  let out = '';
  for (const k of ['node', 'music', 'sfx', 'voice']) {
    const b64 = await page.evaluate(k => new Promise(res => {
      const r = window.__recs[k];
      r.rec.onstop = () => { const blob = new Blob(r.chunks, { type: 'audio/webm' }); const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(blob); };
      r.rec.stop();
    }), k);
    out = '/home/claude/bab_out/m1_src/shots/run_' + (auto ? 'auto' : 'hold') + (k === 'node' ? '' : '_' + k) + '.webm';
    fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  }
  out = '/home/claude/bab_out/m1_src/shots/run_' + (auto ? 'auto' : 'hold') + '.webm';
  const info = await page.evaluate(() => ({ counts: Sound.counts(), time: window.__m1.sim().time, info: Sound.info() }));
  console.log('recorded ' + (fs.statSync(out).size / 1024).toFixed(0) + ' KB to ' + out + '; game clock ' + info.time.toFixed(1) + ' s; sound ' + JSON.stringify(info.info));
  console.log('sounds asked for: ' + Object.keys(info.counts).sort((a, b) => info.counts[b] - info.counts[a]).map(k => k + ' ' + info.counts[k]).join(', '));
  if (errors.length) console.log('ERRORS', errors);
  await browser.close();
})();
