// frames3.js - build 3, frame by frame: the knife, the coast road, the battery and its boat.
// usage: node frames3.js [scene,scene...]   (pictures go to shots/frames/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/frames/';
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
fs.mkdirSync(out, { recursive: true });
const only = process.argv[2] && process.argv[2] !== '-' ? process.argv[2].split(',') : null;
const VW = +(process.argv[3] || 468);
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
if (!m) throw new Error('could not find the bot');
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
  const res = await page.evaluate(({ only, VW }) => {
    window.__m1.frozen = true;
    const W = VW, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {}, notes = {};
    const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
    const I = o => Object.assign({ viewW: W }, none, o);
    const range = (a, b, st) => { const r = []; for (let k = a; k <= b; k += st) r.push(k); return r; };
    // opt.when(s, k, events) -> true: take this frame too (up to opt.max of them), named by tick
    function scene(name, opt) {
      if (only && only.indexOf(name) < 0) return null;
      const L = opt.level ? Object.assign({}, LEVEL, opt.level) : LEVEL;
      let s = Sim.create(L, { viewW: W, seed: opt.seed || 7, zone: opt.zone || 0, lanes: opt.lanes });
      Render.reset();
      if (opt.make) opt.make(s);
      const bot = opt.bot ? window.__mkBot(opt.bot === true ? {} : opt.bot) : null;
      const last = opt.until || Math.max.apply(null, opt.frames);
      let extra = 0, log = [];
      for (let k = 0; k <= last; k++) {
        const inp = bot ? Object.assign({ viewW: W }, bot(s)) : I(opt.input ? opt.input(s, k) : {});
        if (opt.over) Object.assign(inp, opt.over(s, k) || {});
        Sim.step(s, inp);
        if (opt.each) opt.each(s, k);
        for (const e of s.events) if (/^(flip|truck_dead|strike|boss_|mount|dismount|road_end|checkpoint|clear|capture|surrender|life_lost)/.test(e.t)) log.push(k + ':' + e.t + (e.how ? '/' + e.how : '') + (e.n ? '/' + e.n : ''));
        Render.onEvents(s, s.events);
        Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: opt.sub || null, caps: true, noHud: !!opt.noHud, dim: 0 });
        let take = opt.frames && opt.frames.indexOf(k) >= 0;
        if (!take && opt.when && extra < (opt.max || 12) && opt.when(s, k, s.events)) { take = true; extra++; }
        if (take) shots[name + '_' + ('0000' + k).slice(-4)] = cv.toDataURL('image/png');
        if (s.status !== 'play' && s.clearT > 200) break;
      }
      notes[name] = { tick: s.tick, x: Math.round(s.p.x), status: s.status, zone: s.zone, mode: s.mode, plates: s.p.plates, lives: s.p.lives, log: log.slice(0, 60) };
      return s;
    }
    const one = { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } } };
    // the jambiya
    scene('knife', { level: Object.assign({}, one, { spawns: [{ g: 'X', k: 'rifle', x: 150, post: 1, look: 'angry' }, { g: 'X', k: 'rifle', x: 190, post: 1, look: 'qat' }] }),
                     make: s => { s.enemies.forEach(e => { e.cd = 9999; }); }, input: (s, k) => ({ mx: k < 14 || (k > 60 && k < 90) ? 1 : 0, fire: k > 16 }), each: s => { s.p.inv = 5; }, frames: [17, 18, 19, 21, 24, 27, 30, 36, 40, 44, 48, 52] });
    scene('knife_door', { level: Object.assign({}, one, { spawns: [{ g: 'X', k: 'door', x: 152, post: 1 }] }), make: s => { s.enemies[0].cd = 9999; s.enemies[0].bashCd = 9999; },
                          input: (s, k) => ({ mx: k < 12 ? 1 : 0, fire: k > 14 }), each: s => { const e = s.enemies[0]; if (e) { e.cd = 9999; e.bashCd = 9999; } s.p.inv = 5; }, frames: [16, 20, 30, 38, 56, 74, 76, 80, 86, 94, 100, 110] });
    // the pickup arrives, and the road as the careful bot drives it
    scene('arrive', { zone: 2, make: s => { s.groups.C.done = s.groups.C2.done = s.groups.C3.done = true; s.enemies.length = 0; s.p.x = 1300; s.cam = 1100; }, input: (s, k) => ({ mx: k > 20 ? 1 : 0 }), frames: [40, 80, 110, 130, 150, 170, 190, 210, 230, 250, 280, 320] });
    scene('road', { zone: 3, bot: true, until: 60 * 64, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: range(60, 60 * 62, 150) });
    scene('road_ev', { zone: 3, bot: true, until: 60 * 64, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 40,
                       when: (s, k, ev) => { const t = s.__t || (s.__t = { at: -99 }); for (const e of ev) if (/^(flip|truck_dead|strike|smash|drone_down|gunner_down)$/.test(e.t) || (e.t === 'explode' && e.kind === 'mine')) t.at = k; return k - t.at === 4 || k - t.at === 14; } });
    scene('hop', { zone: 3, make: s => { s.roadI = 1; }, input: (s, k) => ({ mx: 1, jump: k > 150 && k < 175, fire: k > 100, my: k > 190 ? -1 : 0, grenade: k === 230 }), frames: [120, 152, 158, 164, 170, 176, 182, 188, 194, 200, 234, 250] });
    scene('wreck', { zone: 3, make: s => { s.p.plates = 1; s.p.inv = 0; }, input: (s, k) => ({ mx: 1 }), each: s => { s.p.inv = 0; }, when: (s, k) => s.p.dead > 0 && (s.p.dead % 8 === 2), max: 12, until: 900, frames: [] });
    // build 4: the sand run, from the tarmac giving out to its coming back, and the mines as they come into view
    const Wd = LEVEL.world, marks = [Wd.XR1 - 260, Wd.XR1 + 200, Wd.XR1 + 520, Wd.XS0 + 140, Wd.XS0 + 900, Wd.XS0 + 1700, Wd.XS1 - 300, Wd.XS1 + 200, Wd.XS1 + 560, Wd.XR2 + 60];
    scene('sandrun', { zone: 3, bot: true, until: 60 * 64, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 12,
                       when: (s, k) => { const t = s.__m || (s.__m = { i: 0 }); if (s.mode === 'drive' && t.i < marks.length && s.cam + W * 0.5 >= marks[t.i]) { t.i++; return true; } return false; } });
    const cams = [5380, 5477, 5560, 7000, 9140, 9221, 9300];
    scene('forejoin', { zone: 3, bot: true, until: 60 * 64, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 12,
                        when: (s, k) => { const t = s.__c || (s.__c = { i: 0 }); if (s.mode === 'drive' && t.i < cams.length && s.cam >= cams[t.i]) { t.i++; return true; } return false; } });
    scene('mines', { zone: 3, bot: true, until: 60 * 64, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 24,
                     when: (s, k, ev) => { const t = s.__t || (s.__t = { at: -99 }); for (const e of ev) if (e.t === 'spot' && e.k === 'rmine') t.at = k; return k - t.at === 1 || k - t.at === 24; } });
    // the battery
    scene('battery', { zone: 4, bot: true, until: 60 * 70, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: range(30, 60 * 68, 120) });
    scene('boss_ev', { zone: 4, bot: true, until: 60 * 70, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 40,
                       when: (s, k, ev) => { const t = s.__t || (s.__t = { at: -99 }); for (const e of ev) if (/^(boss_intro|boss_start|boss_phase|boss_dying|boss_dead|swoop|launch|bomb_drop|surrender|capture)$/.test(e.t) || (e.t === 'tell' && /bomb|bgun|swoop/.test(e.k))) { if (k - t.at > 24) t.at = k; } return k - t.at === 6 || k - t.at === 20; } });
    scene('bombs', { zone: 4, bot: true, until: 60 * 70, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, max: 8,
                     when: (s, k) => { const t = s.__b || (s.__b = { at: -99 }); const n = s.bombs.filter(b => b.kind === 'bbomb' && b.air && !b.gone).length; if (n >= 2 && k - t.at > 90) { t.at = k; return true; } return false; } });
    scene('intro', { zone: 4, input: (s, k) => ({ mx: s.p.x < LEVEL.world.XB + 330 ? 1 : 0 }), each: s => { s.p.inv = 5; }, when: (s, k) => s.boss && s.boss.st === 'intro' && s.boss.stT % 12 === 1, max: 12, until: 700, frames: [] });
    // for the art pack: the beach zones as the careful bot plays them, a frame every 100 ticks
    scene('beach', { zone: 0, bot: true, until: 2300, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: range(100, 2300, 100) });
    scene('camp', { zone: 1, bot: true, until: 1500, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: range(60, 1500, 80) });
    scene('containers', { zone: 2, bot: true, until: 1500, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: range(60, 1500, 80) });
    scene('idle_test', { level: Object.assign({}, one, { spawns: [] }), frames: [10, 20, 30, 40, 50, 60, 70, 80] });
    scene('death_test', { level: Object.assign({}, one, { spawns: [{ g: 'X', k: 'rifle', x: 260, post: 1, look: 'angry' }] }), make: s => { s.enemies[0].cd = 9999; },
                          input: (s, k) => ({ fire: k > 2 && k < 8 }), each: s => { s.p.inv = 5; }, frames: [12, 16, 20, 24, 30, 38, 50, 64] });
    scene('boss_end', { zone: 4, bot: true, until: 3620, each: s => { if (s.p.plates < 2) s.p.plates = 3; }, frames: [3370, 3400, 3430, 3452, 3470, 3500, 3540, 3575, 3610] });
    window.__m1.frozen = false;
    Render.resize(window.__m1.width());
    return { shots, notes };
  }, { only, VW });
  let n = 0;
  for (const k in res.shots) { fs.writeFileSync(out + k + '.png', Buffer.from(res.shots[k].split(',')[1], 'base64')); n++; }
  for (const k in res.notes) console.log(k, JSON.stringify(res.notes[k]));
  console.log(n + ' frames saved' + (errors.length ? '; ERRORS:\n' + errors.join('\n') : '; no errors'));
  await browser.close();
})();
