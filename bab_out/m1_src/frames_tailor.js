// frames_tailor.js - the Tailor, frame by frame: from the covered market's checkpoint the bot fights him (guessing at
// first, so a dummy or two gets shot) and frames are kept at the moments worth looking at: the shop before the fight,
// the hello, the stands passing each other, his tells and throws, his tape on the floor, a dummy's clothes shot off,
// caught out, sneezing, the spare dummy wheeled in, the sheets, the tape winding round him, the dummies going over, and
// him hopping off.
// usage: node frames_tailor.js [width] [seed] [lang] [careful]   (pictures go to shots/tailor/ or shots/tailor_ar/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/tailor' + (process.argv[4] === 'ar' ? '_ar' : '') + '/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
fs.mkdirSync(out, { recursive: true });
const VW = +(process.argv[2] || 468), SEED = +(process.argv[3] || 7), LANG = process.argv[4] || 'en', GUESS = process.argv[5] !== 'careful';
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 500 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message + '\n' + e.stack));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.addScriptTag({ content: BOT });
  if (LANG === 'ar') await page.evaluate(() => Lang.set('ar'));
  const res = await page.evaluate(({ VW, SEED, GUESS }) => {
    window.__m1.frozen = true;
    const W = VW, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {}, log = [];
    let s = Sim.create(LEVEL_ZABID, { viewW: W, seed: SEED, zone: 3, lanes: [0.18, 0.25] });
    Render.reset();
    const bot = window.__mkBot({ guess: GUESS });
    const want = {}, count = k => (want[k] = (want[k] || 0) + 1);
    const after = {};
    for (let k = 0; k < 60 * 300; k++) {
      const inp = Object.assign({ viewW: W, lanes: [0.18, 0.25] }, bot(s));
      Sim.step(s, inp);
      Render.onEvents(s, s.events);
      Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: null, caps: true, noHud: false, dim: 0 });
      const b = s.boss, tl = s.tailor;
      let take = null;
      for (const e of s.events) {
        if (/^(boss_|caught|shred|topple|redress|roll_in|cover|uncover|shuffle|snip|pins|tape$|yank|surrender|capture|clear|life_lost|sneeze)/.test(e.t) || e.t === 'tell') log.push(Math.round(s.time * 10) / 10 + ':' + e.t + (e.k ? '/' + e.k : '') + (e.n ? '/' + e.n : '') + ' hp' + (b ? b.hp : '-'));
        if (/^(boss_intro|boss_phase|boss_dying|boss_dead|caught|shred|topple|roll_in|surrender|capture|clear|yank)$/.test(e.t) && count(e.t) <= 2) after[e.t + count(e.t)] = k + (e.t === 'boss_dead' ? 2 : (e.t === 'roll_in' ? 25 : 3));
      }
      for (const key in after) if (after[key] === k) take = key;
      if (!take && !b && tl && s.p.x > LEVEL_ZABID.world.CM + 150 && count('before') === 1) take = 'before';
      if (!take && b && b.st === 'show' && b.stT === 30) take = 'show';
      if (!take && b && b.st === 'shuffle' && tl.shuffle && tl.cover === 0 && tl.shuffle.t === Math.floor(tl.shuffle.T / 2) && count('swap') <= 3) take = 'swap';
      if (!take && b && b.st === 'hunt' && b.huntT === 24 && count('hunt') <= 2) take = 'hunt';
      if (!take && b && b.st === 'tell' && b.stT === 18 && count('tell_' + b.attack) <= 2) take = 'tell_' + b.attack;
      if (!take && b && b.st === 'throw' && b.stT === 8 && count('throw_' + b.attack) <= 2) take = 'throw_' + b.attack;
      if (!take && tl && tl.tape && tl.tape.st === 'out' && tl.tape.len > 90 && tl.tape.len < 96 && count('tapeout') <= 2) take = 'tapeout';
      if (!take && b && b.st === 'sneeze' && b.stT === 12 && count('bsneeze') <= 2) take = 'sneeze';
      if (!take && b && b.st === 'stun' && b.stT === 30 && count('stun') <= 2) take = 'stun';
      if (!take && tl && tl.coverWant && tl.cover === 13 && count('covering') <= 1) take = 'covering';
      if (!take && b && b.st === 'shuffle' && tl.cover === Sim.TL.COVER_T && tl.shuffle && tl.shuffle.t === Math.floor(tl.shuffle.T / 2) && count('covered') <= 2) take = 'covered';
      if (!take && b && b.st === 'dying' && (b.stT === 20 || b.stT === 70 || b.stT === 104)) take = 'dying' + b.stT;
      if (!take && b && b.st === 'dead' && (b.stT === 6 || b.stT === 40)) take = 'dead' + b.stT;
      if (!take && s.enemies.some(e => e.wrapped && e.st === 'stagger' && e.stT === 18)) take = 'hop';
      if (!take && s.enemies.some(e => e.wrapped && e.captured && e.stT === 100)) take = 'leaving';
      if (take) shots[('0000' + Math.round(s.time * 10)).slice(-5) + '_' + take] = cv.toDataURL('image/png');
      if (s.status === 'clear' && s.clearT > 100) break;
      if (s.status === 'over') { s = Sim.continueZone(s, W); }
    }
    return { shots, log, status: s.status, time: s.time, bossT: s.stats.bossT, hurt: s.stats.hurtBy };
  }, { VW, SEED, GUESS });
  for (const f of fs.readdirSync(out)) fs.unlinkSync(out + f);
  for (const n in res.shots) fs.writeFileSync(out + n + '.png', Buffer.from(res.shots[n].split(',')[1], 'base64'));
  console.log(res.log.join('\n'));
  console.log('status', res.status, 'time', res.time.toFixed(1), 'boss', res.bossT.toFixed(1), 'hurt', JSON.stringify(res.hurt), 'frames', Object.keys(res.shots).length);
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await browser.close();
})();
