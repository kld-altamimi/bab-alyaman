// frames_tailor_moves.js - the Tailor's moves one at a time, staged: Yazeed stands still at the left of the shop and the
// Tailor is set to throw each thing in turn (his shears, his pins, his tape), then put in a cloud of chilli to sneeze, and
// frames are kept as each one goes (with the scene enlarged round the shop in a second copy).
// usage: node frames_tailor_moves.js [width] [lang]   (pictures go to shots/tailor_moves/)
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/tailor_moves' + (process.argv[3] === 'ar' ? '_ar' : '') + '/';
fs.mkdirSync(out, { recursive: true });
const VW = +(process.argv[2] || 468), LANG = process.argv[3] || 'en';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 500 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message + '\n' + e.stack));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  if (LANG === 'ar') await page.evaluate(() => Lang.set('ar'));
  const res = await page.evaluate(({ VW }) => {
    window.__m1.frozen = true;
    const W = VW, cv = document.getElementById('lo');
    Render.resize(W);
    const shots = {}, log = [];
    const s = Sim.create(LEVEL_ZABID, { viewW: W, seed: 3, zone: 3, lanes: [0.18, 0.25] });
    Render.reset();
    const CM = LEVEL_ZABID.world.CM, X = Sim.ext.tailor, I = Sim._;
    let k = 0;
    const idle = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false, viewW: W, lanes: [0.18, 0.25] };
    function tick(inp) {
      Sim.step(s, Object.assign({}, idle, inp || {}));
      Render.onEvents(s, s.events);
      Render.draw(s, { paused: false, fps: 60, lock: false, auto: false, sub: null, caps: true, noHud: false, dim: 0 });
      for (const e of s.events) if (!/^(step|shot|land)$/.test(e.t)) log.push(Math.round(s.time * 10) / 10 + ':' + e.t + (e.k ? '/' + e.k : '') + (e.src ? '/' + e.src : ''));
      k++;
    }
    function snap(name) { shots[('0000' + k).slice(-5) + '_' + name] = cv.toDataURL('image/png'); }
    // walk in to the shop, and wait for the hunt
    for (let i = 0; i < 900 && !(s.boss && s.boss.st === 'hunt'); i++) tick({ mx: s.p.x < CM + 280 ? 1 : 0 });
    const b = s.boss;
    s.p.inv = 0;
    // each of his throws, in turn: (phase, which kind) and what to keep
    const plan = [['scissors', 1, 0], ['pins', 2, 1], ['tape', 3, 2]];
    for (const [what, ph, nx] of plan) {
      b.phase = ph; b.next = nx; b.cd = 1; b.huntT = 0;
      for (let i = 0; i < 160; i++) {
        tick();
        s.p.inv = 0; s.p.dead = 0; s.p.plates = 3; if (s.p.lives < 3) s.p.lives = 3;
        if (b.st === 'tell' && (b.stT === 4 || b.stT === 20)) snap(what + '_tell' + b.stT);
        if (b.st === 'throw' && (b.stT === 4 || b.stT === 12)) snap(what + '_throw' + b.stT);
        if (b.st === 'hunt' && (b.stT === 8 || b.stT === 20 || b.stT === 34)) snap(what + '_after' + b.stT);
        if (s.tailor.tape && s.tailor.tape.st === 'hold' && s.tailor.tape.t === 2) snap('tape_hold');
        if (b.st === 'hunt' && b.stT > 40 && !s.tailor.tape && !s.bullets.some(q => !q.gone && !q.own)) break;
      }
    }
    // a cloud of chilli on him: he sneezes, and nobody else does
    const me = X.real(s);
    I.addCloud(s, me.x, X.floorY(s) - 30, 18, 'red', 150, 0);
    for (let i = 0; i < 120; i++) {
      tick();
      if (b.st === 'sneeze' && (b.stT === 4 || b.stT === 12 || b.stT === 40)) snap('sneeze' + b.stT);
    }
    // caught, then a dummy shot (its clothes go), then knocked over
    b.st = 'hunt'; b.stT = 0; b.cd = 999;
    const fy = X.floorY(s) - Sim.TL.STAND_H - 20;
    s.bullets.push({ x: me.x - 12, y: fy, vx: 400, vy: 0, life: 60, own: true, age: 5, hide: 0 });
    for (let i = 0; i < 30; i++) { tick(); if (b.st === 'caught' && (b.stT === 3 || b.stT === 10)) snap('caught' + b.stT); }
    b.st = 'hunt'; b.stT = 0; b.cd = 999;
    const dum = s.tailor.figs.find(f => f.st === 'dressed');
    s.bullets.push({ x: dum.x - 12, y: fy, vx: 400, vy: 0, life: 60, own: true, age: 5, hide: 0 });
    for (let i = 0; i < 40; i++) { tick(); s.p.inv = 0; if (i === 2 || i === 6 || i === 14) snap('shred' + i); }
    s.bullets.push({ x: dum.x - 12, y: fy, vx: 400, vy: 0, life: 60, own: true, age: 5, hide: 0 });
    for (let i = 0; i < 20; i++) { tick(); if (i === 3) snap('topple'); }
    return { shots, log };
  }, { VW });
  for (const f of fs.readdirSync(out)) fs.unlinkSync(out + f);
  for (const n in res.shots) fs.writeFileSync(out + n + '.png', Buffer.from(res.shots[n].split(',')[1], 'base64'));
  console.log(res.log.filter(l => !/eshot|hit/.test(l)).join(' '));
  console.log('frames', Object.keys(res.shots).length);
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await browser.close();
})();
