// frames_scale.js - the Great Scale, frame by frame: from the covered market's checkpoint the careful bot fights it
// (holding its fire for a stretch so the porters get a sack or two in) and frames are kept at the moments worth looking
// at: the scale before the fight, the intro, sacks bursting, the beam tipping, every one of his moves, the slam and the
// bonk, the porters, the weights, the swinging pan, the break, the surrender.
// usage: node frames_scale.js [width] [seed] [lang]   (pictures go to shots/scale/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/scale' + (process.argv[4] === 'ar' ? '_ar' : '') + '/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
fs.mkdirSync(out, { recursive: true });
const VW = +(process.argv[2] || 468), SEED = +(process.argv[3] || 7), LANG = process.argv[4] || 'en';
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
  const res = await page.evaluate(({ VW, SEED }) => {
    window.__m1.frozen = true;
    const W = VW, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {}, log = [];
    let s = Sim.create(LEVEL_ZABID, { viewW: W, seed: SEED, zone: 3, lanes: [0.18, 0.25] });
    Render.reset();
    const bot = window.__mkBot({});
    const want = {}, count = k => (want[k] = (want[k] || 0) + 1);
    let fightT = -1, after = {};
    for (let k = 0; k < 60 * 240; k++) {
      const inp = Object.assign({ viewW: W, lanes: [0.18, 0.25] }, bot(s));
      if (fightT >= 0 && s.time - fightT > 7 && s.time - fightT < 15) { inp.fire = false; inp.grenade = false; }      // (let the porters work)
      Sim.step(s, inp);
      Render.onEvents(s, s.events);
      Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: null, caps: true, noHud: false, dim: 0 });
      const b = s.boss, sc = s.scale;
      let take = null;
      for (const e of s.events) {
        if (/^(boss_|slam|bonk|dazed|hop_in|plonk|porter|sack_in|lob|surrender|capture|clear|life_lost|buck)/.test(e.t) || (e.t === 'tell')) log.push(Math.round(s.time * 10) / 10 + ':' + e.t + (e.k ? '/' + e.k : '') + (e.n ? '/' + e.n : '') + ' hp' + (b ? b.hp : '-'));
        if (e.t === 'boss_start') fightT = s.time;
        if (/^(boss_intro|boss_phase|boss_dying|boss_dead|slam|bonk|boss_down|sack_in|surrender|capture|clear)$/.test(e.t) && count(e.t) <= 2) after[e.t + count(e.t)] = k + (e.t === 'slam' ? 4 : (e.t === 'boss_dead' ? 2 : 3));
      }
      for (const key in after) if (after[key] === k) take = key;
      if (!take && !b && s.p.x > LEVEL_ZABID.world.CM + 150 && count('before') === 1) take = 'before';
      if (!take && b && b.st === 'rise' && b.stT === 16 && count('rise') <= 2) take = 'rise';
      if (!take && b && b.st === 'shoot' && b.stT === 3 && count('shootlvl') <= 2) take = 'levelshot';
      if (!take && b && b.st === 'aim' && b.stT === 30 && count('aim') <= 2) take = 'aim';
      if (!take && b && b.st === 'fire' && b.stT === 2 && count('fire') <= 2) take = 'fire';
      if (!take && b && b.st === 'lobtell' && b.stT === 24 && count('heft') <= 2) take = 'heft';
      if (!take && s.bombs.some(q => q.boom === 'weight' && !q.gone && q.t === 30) && count('weights') <= 2) take = 'weights';
      if (!take && sc && sc.man.st === 'dazed' && sc.man.t === 50 && count('dazed') <= 2) take = 'dazed';
      if (!take && sc && sc.man.st === 'hop' && sc.man.t === 22 && count('hop') <= 2) take = 'hop';
      if (!take && sc && sc.man.st === 'fly' && sc.man.t === 6 && count('fly') <= 2) take = 'fly';
      if (!take && s.enemies.some(e => e.porter && e.alive && e.carry && e.st === 'walk' && Sim.onScreen(s, e.x, -20)) && count('porterw') % 90 === 1 && count('porterws') <= 3) take = 'porter';
      if (!take && s.enemies.some(e => e.porter && e.st === 'heave' && e.stT === 14) && count('heave') <= 2) take = 'heave';
      if (!take && sc && sc.snap && b && b.st !== 'dead' && count('swingT') % 50 === 1 && count('swing') <= 5) take = 'swing';
      if (!take && b && b.st === 'sneeze' && b.stT === 20 && count('bsneeze') <= 1) take = 'sneeze';
      if (!take && b && b.st === 'dead' && (b.stT === 20 || b.stT === 45 || b.stT === 120)) take = 'dead' + b.stT;
      if (take) shots[('0000' + Math.round(s.time * 10)).slice(-5) + '_' + take] = cv.toDataURL('image/png');
      if (s.status === 'clear' && s.clearT > 100) break;
      if (s.status === 'over') { s = Sim.continueZone(s, W); }
    }
    return { shots, log, status: s.status, time: s.time, bossT: s.stats.bossT, hurt: s.stats.hurtBy };
  }, { VW, SEED });
  for (const f of fs.readdirSync(out)) fs.unlinkSync(out + f);
  for (const n in res.shots) fs.writeFileSync(out + n + '.png', Buffer.from(res.shots[n].split(',')[1], 'base64'));
  console.log(res.log.join('\n'));
  console.log('status', res.status, 'time', res.time.toFixed(1), 'boss', res.bossT.toFixed(1), 'hurt', JSON.stringify(res.hurt), 'frames', Object.keys(res.shots).length);
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await browser.close();
})();
