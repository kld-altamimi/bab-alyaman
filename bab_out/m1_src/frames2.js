// frames2.js - the things new in build 2, frame by frame: 45 degree aiming, the new explosions, the man with the door, walking on across a stopped screen
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/frames/';
fs.mkdirSync(out, { recursive: true });
const only = process.argv[2] ? process.argv[2].split(',') : null;
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 500 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message + '\n' + e.stack));
  page.on('console', m => { if (m.type() === 'error' && !/font|ERR_/.test(m.text())) errors.push(m.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  const res = await page.evaluate((only) => {
    window.__m1.frozen = true;
    const W = 468, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {};
    const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
    const I = o => Object.assign({ viewW: W }, none, o);
    function scene(name, opt) {
      if (only && only.indexOf(name) < 0) return null;
      const L = opt.level ? Object.assign({}, LEVEL, opt.level) : LEVEL;
      let s = Sim.create(L, { viewW: W, seed: opt.seed || 7, zone: opt.zone || 0, lanes: opt.lanes });
      Render.reset();
      if (opt.make) opt.make(s);
      const last = Math.max.apply(null, opt.frames);
      for (let k = 0; k <= last; k++) {
        Sim.step(s, I(opt.input ? opt.input(s, k) : {}));
        if (opt.each) opt.each(s, k);
        Render.onEvents(s, s.events);
        Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: opt.sub || null, caps: true, noHud: !!opt.noHud, dim: 0 });
        if (opt.frames.indexOf(k) >= 0) shots[name + '_' + ('00' + k).slice(-3)] = cv.toDataURL('image/png');
      }
      return s;
    }
    const empty = { spawns: [], props: [], gates: [], groups: {} };
    const range = (a, b, st) => { const r = []; for (let k = a; k <= b; k += st) r.push(k); return r; };
    // 45 degrees: standing against the screen edge, on the run, in the air up and down, both guns
    scene('diag_side', { level: empty, input: (s, k) => ({ mx: k < 30 ? 1 : (k < 60 ? -1 : 1), my: -1, fire: true }), frames: [6, 12, 20, 26, 40, 52, 70, 76] });
    scene('diag_hmg', { level: empty, make: s => { s.p.weapon = 'hmg'; s.p.ammo = 200; }, input: (s, k) => ({ mx: 1, my: -1, fire: true }), frames: [4, 8, 12, 16, 20, 24, 28, 32] });
    scene('diag_air', { level: empty, make: s => { s.p.weapon = 'hmg'; s.p.ammo = 200; }, input: (s, k) => ({ mx: 1, my: k < 22 ? -1 : 1, jump: k > 2 && k < 30, fire: true }), frames: [6, 12, 18, 24, 30, 36, 42, 48] });
    scene('diag_air_side', { level: empty, input: (s, k) => ({ mx: 1, my: k < 22 ? -1 : 1, jump: k > 2 && k < 30, fire: true }), frames: [6, 12, 18, 24, 30, 36, 42, 48] });
    // explosions: a grenade on the sand, a drum, a stick shot in the air
    scene('boom_gren', { level: empty, input: (s, k) => ({ grenade: k === 2 }), frames: range(44, 86, 3) });
    scene('boom_drum', { level: { spawns: [], gates: [], groups: {}, props: [{ k: 'drum', x: 250, paint: 'oxide', zone: 0 }] }, input: (s, k) => ({ fire: k < 30, mx: k > 30 ? -1 : 0 }), frames: range(74, 124, 3) });
    scene('boom_air', { level: { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'bomber', x: 300, post: 1 }] }, make: s => { s.enemies[0].cd = 2; }, input: (s, k) => ({ fire: k > 44 }), frames: range(46, 96, 3) });
    // the man with the door
    const door1 = { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'door', x: 260, post: 1 }] };
    scene('door_shot', { level: door1, make: s => { s.enemies[0].cd = 9999; s.enemies[0].bashCd = 9999; }, input: () => ({ fire: true }), each: s => { const e = s.enemies[0]; if (e && e.door > 0) e.cd = 9999; s.p.inv = 5; },
                         frames: [30, 70, 110, 136, 140, 144, 150, 158, 166, 176, 190, 200] });
    scene('door_gren', { level: door1, make: s => { s.enemies[0].cd = 9999; s.enemies[0].bashCd = 9999; }, input: (s, k) => ({ grenade: k === 4, fire: k > 80 }), each: s => { const e = s.enemies[0]; if (e && e.door > 0) e.cd = 9999; s.p.inv = 5; },
                         frames: [30, 44, 48, 52, 56, 62, 70, 80, 92, 100, 108, 120] });
    scene('door_bash', { level: door1, make: s => { s.p.x = 240; s.enemies[0].cd = 9999; }, each: s => { const e = s.enemies[0]; e.cd = 9999; }, frames: [2, 8, 14, 19, 21, 24, 28, 34, 40, 50, 60, 70] });
    scene('door_lean', { level: door1, make: s => { s.enemies[0].cd = 6; s.enemies[0].bashCd = 9999; }, input: (s, k) => ({ my: 1 }), frames: [4, 10, 20, 30, 34, 44, 54, 64] });
    scene('door_bare', { level: door1, make: s => { const e = s.enemies[0]; e.door = 0; e.st = 'walk'; e.post = false; e.cd = 30; e.band = 90; }, each: s => { s.p.inv = 5; }, frames: [10, 34, 44, 52, 56, 66, 80, 100] });
    // the stopped screen: he walks on across it
    scene('wall', { input: (s, k) => ({ mx: 1 }), each: s => { s.p.inv = 5; }, frames: [150, 200, 240, 280, 330, 380, 420, 470] });
    scene('wall_clear', { lanes: [0.07, 0.09], input: (s, k) => ({ mx: 1 }), each: s => { s.p.inv = 5; }, frames: [150, 200, 240, 280, 330, 380, 420, 470] });
    window.__m1.frozen = false;
    Render.resize(window.__m1.width());
    return shots;
  }, only);
  let n = 0;
  for (const k in res) { fs.writeFileSync(out + k + '.png', Buffer.from(res[k].split(',')[1], 'base64')); n++; }
  console.log(n + ' frames saved' + (errors.length ? '; ERRORS:\n' + errors.join('\n') : '; no errors'));
  await browser.close();
})();
