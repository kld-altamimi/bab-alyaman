// frames_zabid.js - The Souq, frame by frame: the careful bot plays it through and frames are kept at the moments worth
// looking at (checkpoints, sacks bursting, sneezes, barricades going, shopkeepers freed, every move of the Spice Cannon).
// usage: node frames_zabid.js [width] [seed]   (pictures go to shots/zabid/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/zabid/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
fs.mkdirSync(out, { recursive: true });
const VW = +(process.argv[2] || 468), SEED = +(process.argv[3] || 7);
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 500 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message + '\n' + e.stack));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.addScriptTag({ content: BOT });
  const res = await page.evaluate(({ VW, SEED }) => {
    window.__m1.frozen = true;
    const W = VW, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {}, log = [];
    const L = LEVEL_ZABID;
    let s = Sim.create(L, { viewW: W, seed: SEED, lanes: [0.18, 0.25] });
    Render.reset();
    const bot = window.__mkBot({});
    const want = {}, count = k => (want[k] = (want[k] || 0) + 1);
    let lastShot = -999;
    for (let k = 0; k < 60 * 400; k++) {
      const inp = Object.assign({ viewW: W, lanes: [0.18, 0.25] }, bot(s));
      Sim.step(s, inp);
      Render.onEvents(s, s.events);
      Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: null, caps: true, noHud: false, dim: 0 });
      let take = null;
      for (const e of s.events) {
        if (/^(checkpoint|boss_|clear|freed|surrender|capture|emerge|spice_burst|sneeze|bar_break|cannon_shot|cone|cough|shove|pant|life_lost)/.test(e.t)) log.push(Math.round(s.time * 10) / 10 + ':' + e.t + (e.k ? '/' + e.k : '') + (e.n ? '/' + e.n : '') + (e.who ? '/' + e.who : '') + ' x' + Math.round(s.p.x));
        if (e.t === 'checkpoint' || e.t === 'boss_intro' || e.t === 'boss_phase' || e.t === 'clear') take = e.t + (e.n || '');
        if (e.t === 'emerge' && count('emerge') <= 2) take = 'emerge';
        if (e.t === 'freed' && count('freed') <= 4) take = 'freed';
        if (e.t === 'bar_break' && count('barbreak') <= 3) take = 'barbreak';
        if (e.t === 'tell' && /^(cone|shell_hi|shell_lo|cough|shove)$/.test(e.k) && count(e.k) <= 2) take = 'tell_' + e.k;
      }
      if (!take && s.clouds.length && s.clouds[0].t === 30 && count('cloud') <= 6) take = 'cloud';
      if (!take && s.enemies.some(e => e.st === 'sneeze' && e.stT === 20) && count('sneezing') <= 4) take = 'sneezing';
      if (!take && s.p.sneezeT === Sim.T.P_SNEEZE - 2 && count('psneeze') <= 2) take = 'yazeed_sneeze';
      if (!take && s.bars.some(o => !o.gone && Math.abs(o.x0 - s.p.x) < 60) && count('barnear') % 120 === 1 && count('barshots') <= 4) take = 'barricade';
      if (!take && s.boss && s.boss.st === 'shove' && count('shoving') <= 1) take = 'shoving';
      if (!take && s.boss && s.boss.st === 'pant' && s.boss.stT === 20 && count('panting') <= 2) take = 'panting';
      if (!take && s.boss && s.boss.st === 'cone' && s.boss.stT === 30 && count('coning') <= 2) take = 'chillies';
      if (!take && s.boss && s.boss.st === 'dead' && count('dead') === 40) take = 'deadcannon';
      if (!take && s.L.pits && s.L.pits.some(q => s.p.x > q[0] && s.p.x < q[1]) && count('pitshots') <= 1) take = 'gap';
      if (!take && k - lastShot > 60 * 7) take = 'every';
      if (take) { shots[('0000' + Math.round(s.time * 10)).slice(-5) + '_' + take] = cv.toDataURL('image/png'); lastShot = k; }
      if (s.status === 'clear' && s.clearT > 150) break;
      if (s.status === 'over') { s = Sim.continueZone(s, W); }
    }
    return { shots, log, status: s.status, time: s.time, score: s.score, plates: s.stats.plates, freed: s.stats.freed };
  }, { VW, SEED });
  for (const f of fs.readdirSync(out)) fs.unlinkSync(out + f);
  for (const n in res.shots) fs.writeFileSync(out + n + '.png', Buffer.from(res.shots[n].split(',')[1], 'base64'));
  console.log(res.log.join('\n'));
  console.log('status', res.status, 'time', res.time.toFixed(1), 'score', res.score, 'plates', res.plates, 'freed', res.freed, 'frames', Object.keys(res.shots).length);
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await browser.close();
})();
