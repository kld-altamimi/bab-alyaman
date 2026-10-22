// frames.js - draw chosen moments of the game exactly, frame by frame, with the real renderer, and save them for looking at.
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/frames/';
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 500 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message + '\n' + e.stack));
  page.on('console', m => { if (m.type() === 'error' && !/font|ERR_/.test(m.text())) errors.push(m.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'title');
  const res = await page.evaluate(() => {
    window.__m1.frozen = true;
    const W = 468, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {};
    const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
    const I = o => Object.assign({ viewW: W }, none, o);
    // run a scene: make(s) sets it up, input(s, k) drives it, and frames lists the ticks to photograph
    function scene(name, opt) {
      const L = opt.level ? Object.assign({}, LEVEL, opt.level) : LEVEL;
      let s = Sim.create(L, { viewW: W, seed: opt.seed || 7, zone: opt.zone || 0 });
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
    // 1. Yazeed's moves on an empty beach
    scene('run', { level: empty, input: () => ({ mx: 1 }), frames: [20, 23, 26, 29, 32, 35, 38, 41] });
    scene('jump', { level: empty, input: (s, k) => ({ jump: k > 4 && k < 30, mx: 1, fire: true }), frames: [4, 8, 14, 22, 30, 38, 46, 50] });
    scene('jumpup', { level: empty, input: (s, k) => ({ jump: k > 4 && k < 30, my: -1, fire: true }), frames: [3, 10, 18, 26, 34, 44] });
    scene('jumpdown', { level: empty, input: (s, k) => ({ jump: k > 4 && k < 30, my: k > 12 ? 1 : 0, fire: true }), frames: [14, 22, 30, 38] });
    scene('crouch', { level: empty, input: (s, k) => ({ my: 1, fire: k > 6, mx: k > 30 ? 1 : 0 }), frames: [5, 10, 14, 34, 40, 46] });
    scene('throw', { level: empty, input: (s, k) => ({ grenade: k === 5 }), frames: [4, 7, 10, 14, 24, 40, 55, 62, 70] });
    scene('hmg', { level: empty, make: s => { s.p.weapon = 'hmg'; s.p.ammo = 200; }, input: (s, k) => ({ fire: true, mx: k > 20 ? 1 : 0, my: k > 40 ? -1 : 0 }), frames: [6, 9, 24, 28, 44, 48] });
    // 2. being hit, and going down
    const one = { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 250, post: 1, look: 'angry' }] };
    scene('rifle', { level: one, make: s => { s.enemies[0].cd = 4; }, frames: [3, 12, 24, 31, 34, 40, 47, 60] });
    scene('death', { level: one, make: s => { s.enemies[0].cd = 4; s.p.plates = 1; }, frames: [34, 44, 54, 70, 90, 104, 112, 130] });
    // 3. the three kinds of trouble
    scene('bomber', { level: { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'bomber', x: 300, post: 1 }] }, make: s => { s.enemies[0].cd = 4; }, frames: [3, 20, 40, 46, 60, 80, 100, 112, 118] });
    scene('door', { level: { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'door', enter: 1 }] }, input: (s, k) => ({ fire: k > 150 && k < 215 }), each: s => { s.p.inv = 5; }, frames: [140, 170, 185, 200, 215, 230, 245, 262] });
    scene('doorhit', { level: { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'door', x: 240, post: 1 }] }, make: s => { s.enemies[0].cd = 20; }, input: (s, k) => ({ fire: k > 40 }), each: s => { s.p.inv = 5; }, frames: [30, 52, 56, 60, 64, 70, 80, 95] });
    // 4. the sandbag man, down and up, and the things that go off
    scene('bags', { zone: 1, make: s => { s.p.x = 800; s.p.y = Sim.groundY(s.L, 800); s.cam = 590; s.groups.W.awake = true; for (const e of s.enemies) { if (e.covered) e.cd = 30; else if (e.g === 'W') e.cd = 9999; } s.groups.W.pending = []; },
                   input: (s, k) => ({ my: 1 }), frames: [10, 31, 34, 40, 56, 64, 72, 90] });
    scene('mine', { make: s => { s.p.x = 380; s.p.y = Sim.groundY(s.L, 380); s.cam = 250; s.groups.A.pending = []; }, input: (s, k) => ({ mx: k > 20 ? 1 : 0 }), each: s => { if (s.p.plates < 2) s.p.plates = 2; }, frames: [10, 40, 54, 58, 62, 68, 80, 100] });
    scene('drum', { zone: 2, make: s => { s.p.x = 930; s.p.y = Sim.groundY(s.L, 930); s.cam = 800; }, input: (s, k) => ({ fire: k > 5 && k < 40, mx: k > 44 ? -1 : 0 }), frames: [4, 30, 44, 60, 80, 88, 92, 98] });
    // 5. the elder
    scene('elder', { zone: 1, make: s => { s.p.x = 722; s.p.plat = 1; s.p.y = 122; s.cam = 560; s.groups.W.pending = []; for (const e of s.enemies) e.cd = 9999; }, input: (s, k) => ({ mx: k > 10 && k < 24 ? -1 : 0 }), each: s => { s.p.inv = 5; }, frames: [8, 26, 34, 50, 80, 110, 130, 160] });
    // 6. the end of the slice
    const sEnd = scene('end', { zone: 2, make: s => { for (const k in s.groups) { s.groups[k].done = true; s.groups[k].pending = []; } for (const e of s.enemies) { e.alive = false; e.st = 'gone'; e.deadT = 999; } for (const g of s.gates) g.done = true; s.p.x = 1400; s.p.y = Sim.groundY(s.L, 1400); s.cam = 1150; },
                    input: () => ({ mx: 1 }), frames: [20, 60, 120, 200] });
    // 6b. a wave arriving while he holds at a gate with the trigger down
    scene('wave', { make: s => { s.p.x = 380; s.p.y = Sim.groundY(s.L, 380); s.cam = 146; s.groups.A.awake = true; s.groups.A.awakeT = 0; }, input: (s, k) => ({ fire: true }), each: s => { s.p.inv = 3; },
                    frames: [20, 40, 55, 70, 85, 100, 130, 160] });
    // 7. hit boxes
    Render.opts.boxes = true;
    scene('boxes', { zone: 1, make: s => { s.p.x = 700; s.p.y = Sim.groundY(s.L, 700); s.cam = 590; }, frames: [40] });
    Render.opts.boxes = false;
    window.__m1.frozen = false;
    Render.resize(window.__m1.width());
    return shots;
  });
  let n = 0;
  for (const k in res) { fs.writeFileSync(out + k + '.png', Buffer.from(res[k].split(',')[1], 'base64')); n++; }
  console.log(n + ' frames saved' + (errors.length ? '; ERRORS:\n' + errors.join('\n') : '; no errors'));
  await browser.close();
})();
