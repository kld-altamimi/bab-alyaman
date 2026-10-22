// frames_mocha.js - The Coffee Port, frame by frame: the careful bot plays it through and frames are kept at the moments
// worth looking at (checkpoints, men out of doors, cooks, vents, every move of the Big Roaster, the end).
// usage: node frames_mocha.js [width] [seed]   (pictures go to shots/mocha/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/mocha/';
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
    const L = LEVEL_MOCHA;
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
        if (/^(checkpoint|boss_|clear|freed|surrender|capture|emerge|vent_blast|rspray|rlob|steam_jet|pour|lunge|brake|life_lost)/.test(e.t)) log.push(Math.round(s.time * 10) / 10 + ':' + e.t + (e.k ? '/' + e.k : '') + (e.n ? '/' + e.n : '') + ' x' + Math.round(s.p.x));
        if (e.t === 'checkpoint' || e.t === 'boss_intro' || e.t === 'boss_phase' || e.t === 'clear') take = e.t + (e.n || '');
        if (e.t === 'emerge' && count('emerge') <= 3) take = 'emerge';
        if (e.t === 'tell' && /^(spray_hi|spray_lo|lob|steam|pour|lunge|scoop|swing)$/.test(e.k) && count(e.k) <= 2) take = 'tell_' + e.k;
      }
      if (!take && s.boss && s.boss.st === 'lunge' && count('lunging') <= 1) take = 'lunging';
      if (!take && s.boss && s.boss.st === 'spray' && s.boss.stT === 10 && count('spraying') <= 3) take = 'spraying';
      if (!take && s.boss && s.boss.st === 'steam' && s.boss.stT === 12 && count('steaming') <= 1) take = 'steaming';
      if (!take && s.boss && s.boss.st === 'dead' && count('dead') === 30) take = 'deadcoffee';
      if (!take && s.props.some(o => o.k === 'vent' && o.st === 'blast' && Math.abs(o.x - s.p.x) < 120) && count('ventnear') % 90 === 1 && count('ventshots') <= 3) take = 'vent';
      if (!take && k - lastShot > 60 * 9) take = 'every';
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
