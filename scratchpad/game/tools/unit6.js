// unit6.js - The Coffee Port (build 12): the level agrees with the painting, every posted man stands where he can be
// fought, the cook, the steam vents, men out of doors, the Big Roaster's every move, and the careful bot gets through.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
const MOCHA = require(path.join(__dirname, '../src/level_mocha.js'));
const STAGE = require(path.join(__dirname, '../gen/stage_mocha.json'));
const B = require('./bot.js');
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
const inp = o => Object.assign({}, none, o);
const T = Sim.T, R = Sim.R, THUMBS = [0.18, 0.25];

// ---- the level and the painting
{
  const bad = [];
  for (const pl of MOCHA.plats) {
    const p2 = STAGE.plats[pl.id];
    if (!p2 || JSON.stringify(p2) !== JSON.stringify(pl.pts)) bad.push(pl.id);
  }
  for (const id in STAGE.plats) if (!MOCHA.plats.some(p => p.id === id)) bad.push(id + ' (painted, not in the level)');
  ok(!bad.length, 'every platform in the level is where the painting has it, and every painted one is in the level' + (bad.length ? ': ' + bad.join(', ') : ''));
  ok(JSON.stringify(MOCHA.ground) === JSON.stringify(STAGE.ground) && STAGE.world.WORLD === MOCHA.width, 'the floor and the length agree with the painting');
  const doors = STAGE.world.doors, off = [];
  for (const sp of MOCHA.spawns) if (sp.door && !doors.some(d => Math.abs(d - sp.x) <= 2)) off.push(sp.g + '@' + sp.x);
  ok(!off.length && doors.length === 4, 'every man who comes out of a door comes out of a painted one (' + doors.join(', ') + ')' + (off.length ? ': not ' + off.join(', ') : ''));
}

// ---- every posted man stands inside the middle of his gate's screen at every width (or he would be guarded for ever)
{
  const gateOf = g => MOCHA.gates.find(gt => gt.groups.indexOf(g) >= 0);
  const out = [];
  for (const vw of [384, 416, 449, 468]) {
    for (const sp of MOCHA.spawns) {
      if (!sp.post) continue;
      const gt = gateOf(sp.g), cam = gt.x - vw * T.HOLD;
      const lo = cam + vw * THUMBS[0] - 10, hi = cam + vw * (1 - THUMBS[1]) + 10;
      if (sp.x < lo || sp.x > hi) out.push(vw + ':' + sp.g + '@' + sp.x);
    }
  }
  ok(!out.length, 'every posted man can be fought from where his gate holds the screen, 384 to 468 wide' + (out.length ? ': ' + out.join(', ') : ''));
  const det = MOCHA.props.filter(o => o.k === 'detainee');
  ok(det.length === 2, 'two people held: on the gallery and on the catwalk');
}

// a quiet stretch of the level with one thing in it
function bare(extra) {
  return Object.assign({}, MOCHA, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [] }, extra || {});
}

// ---- the cook: three beans in a fan at a distance, the ladle up close, four shots to put him down
{
  const L = bare({ spawns: [{ g: 'X', k: 'cook', x: 300, post: 1 }] });
  const s = Sim.create(L, { viewW: 468, seed: 1, lanes: THUMBS });
  s.p.x = 160; s.p.y = 184;
  const e = s.enemies[0];
  e.cd = 0;
  let beans = 0, tell = false;
  for (let k = 0; k < 60; k++) {
    Sim.step(s, inp({ viewW: 468 }));
    for (const ev of s.events) { if (ev.t === 'tell' && ev.k === 'scoop') tell = true; if (ev.t === 'fling') beans = s.bullets.filter(b => b.bean && !b.own).length; }
  }
  ok(tell && beans === 3, 'a cook 140 px off warns (the ladle drawn back) and flings three hot beans');
  // where they come down: around where Yazeed stood
  const xs = [];
  const s2 = Sim.create(L, { viewW: 468, seed: 1, lanes: THUMBS });
  s2.p.x = 160; s2.p.inv = 9999;
  s2.enemies[0].cd = 0;
  for (let k = 0; k < 200; k++) { Sim.step(s2, inp({ viewW: 468 })); for (const ev of s2.events) if (ev.t === 'hit' && ev.kind === 'bean') xs.push(Math.round(ev.x)); }
  ok(xs.length === 3 && Math.min(...xs) < 175 && Math.max(...xs) > 120, 'they land short, on him and long (' + xs.join(', ') + ')');
  // up close: the ladle
  const s3 = Sim.create(L, { viewW: 468, seed: 1, lanes: THUMBS });
  s3.enemies[0].x = 200; s3.p.x = 182; s3.enemies[0].swingCd = 0;
  let swung = false, hurt = false;
  for (let k = 0; k < 90 && !hurt; k++) { Sim.step(s3, inp({ viewW: 468 })); for (const ev of s3.events) { if (ev.t === 'tell' && ev.k === 'swing') swung = true; if (ev.t === 'plate_lost') hurt = true; } }
  ok(swung && hurt && s3.stats.hurtBy.ladle === 1, 'up close he raises the ladle, and it lands');
  ok(Sim.KIND.cook.hp === 4, 'he takes four shots');
}

// ---- the steam vents
{
  const L = bare({ props: [{ k: 'vent', x: 240, every: 150, phase: 0, zone: 0 }] });
  const s = Sim.create(L, { viewW: 468, seed: 2, lanes: THUMBS });
  const v = s.props[0];
  const seq = [];
  for (let k = 0; k < 160; k++) { Sim.step(s, inp({ viewW: 468 })); if (!seq.length || seq[seq.length - 1][0] !== v.st) seq.push([v.st, s.tick]); }
  ok(seq.map(q => q[0]).join(',') === 'hiss,blast,idle,hiss' && seq[1][1] === T.VENT_HISS && seq[2][1] - seq[1][1] === T.VENT_BLAST && seq[3][1] === 150,
     'a vent hisses for ' + T.VENT_HISS + ' ticks, blows for ' + T.VENT_BLAST + ', rests, and hisses again ' + 150 + ' ticks on (' + JSON.stringify(seq) + ')');
  // standing on it while it blows costs a plate; a step to the side does not
  const hit = dx => {
    const s2 = Sim.create(L, { viewW: 468, seed: 2, lanes: THUMBS });
    s2.p.x = 240 + dx;
    for (let k = 0; k < 90; k++) Sim.step(s2, inp({ viewW: 468 }));
    return s2.stats.plates;
  };
  ok(hit(0) === 1 && hit(6) === 1 && hit(14) === 0 && hit(-14) === 0, 'it scalds whoever stands on the grating (' + hit(0) + '), not a step to the side (' + hit(14) + ')');
  // nor whoever is up on the catwalk over it
  const s3 = Sim.create(bare({ props: [{ k: 'vent', x: 2794, every: 150, phase: 0, zone: 0 }] }), { viewW: 468, seed: 2, lanes: THUMBS });
  s3.cam = 2600; s3.p.x = 2794; s3.p.plat = Sim._.platIndex(s3.L, 'catwalk'); s3.p.y = 118;
  for (let k = 0; k < 90; k++) Sim.step(s3, inp({ viewW: 468 }));
  ok(s3.stats.plates === 0 && s3.p.y === 118, 'up on the catwalk over it, he is above the steam');
}

// ---- out of a doorway: nothing touches him until he is out
{
  const L = bare({ groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', door: 1, x: 300, delay: 0, look: 'youth' }] });
  const s = Sim.create(L, { viewW: 468, seed: 4, lanes: THUMBS });
  s.p.x = 200;
  let em = 0;
  Sim.step(s, inp({ viewW: 468 }));
  for (const ev of s.events) if (ev.t === 'emerge') em++;
  const e = s.enemies[0];
  ok(em === 1 && e && e.x === 300 && e.emerge > 0 && Sim.guarded(s, e), 'a man comes out of the door at 300, guarded while he does');
  let glance = 0, body = 0;
  for (let k = 0; k < T.EMERGE + 30; k++) {
    Sim.step(s, inp({ viewW: 468, fire: true }));
    for (const ev of s.events) { if (ev.t === 'hit' && ev.kind === 'guard') glance++; if (ev.t === 'hit' && ev.kind === 'body') body++; }
  }
  ok(glance > 0 && body > 0 && !e.alive, 'shots glance off him in the doorway (' + glance + '), and once he is out they put him down');
}

// ---- the Big Roaster
function arena(seed) {
  const s = Sim.create(MOCHA, { viewW: 468, seed: seed || 3, zone: 3, lanes: THUMBS });
  s.p.inv = 0;
  // walk up to the yard and wait for it
  for (let k = 0; k < 60 * 12 && !(s.boss && s.boss.st === 'idle'); k++) Sim.step(s, inp({ viewW: 468, mx: s.p.x < 3830 ? 1 : 0 }));
  return s;
}
{
  const s = arena();
  const b = s.boss;
  ok(b && b.kind === 'roaster' && b.st === 'idle' && b.hp === R.HP, 'in the yard the Big Roaster rolls in and squares up (' + (b ? b.st : 'none') + ')');
  ok(s.camMax === MOCHA.gates.find(g => g.id === 'gB').x - 468 * T.HOLD, 'the screen holds at the yard (' + s.camMax + ')');
  // shots from the left hit it
  const hp0 = b.hp;
  for (let k = 0; k < 40; k++) { b.cd = 999; Sim.step(s, inp({ viewW: 468, fire: true })); }
  ok(b.hp < hp0, 'shots hit it (' + hp0 + ' to ' + b.hp + ')');
  // nobody walks through it
  for (let k = 0; k < 120; k++) { b.cd = 999; Sim.step(s, inp({ viewW: 468, mx: 1 })); }
  ok(s.p.x <= Sim.ext.roaster.front(b) - 6, 'walking at it, he stops in front of it (' + s.p.x.toFixed(0) + ', its front at ' + Sim.ext.roaster.front(b).toFixed(0) + ')');
}
function spray(hi, pose) {
  const s = arena(5);
  const b = s.boss;
  b.phase = hi ? 1 : 2; b.next = 0; b.cd = 1;                // (once hurt, its first spray is a low one)
  s.p.x = Sim.ext.roaster.front(b) - 140;
  let plates = 0, k = 0, fired = 0, hold = 0;
  for (; k < 240; k++) {
    const i = { viewW: 468 };
    if (pose === 'down') i.my = 1;
    if (pose === 'jump' && s.bullets.some(q => q.hot && q.x - s.p.x < 40 && q.x - s.p.x > 0) && !s.p.air) hold = 14;
    if (hold > 0) { i.jump = true; hold--; }
    b.cd = Math.max(b.cd, b.st === 'idle' && fired ? 2 : b.cd);
    Sim.step(s, inp(i));
    for (const ev of s.events) { if (ev.t === 'plate_lost') plates++; if (ev.t === 'rspray') fired++; }
  }
  return { plates, fired, hi: b.hi };
}
{
  const a = spray(true, 'stand'), c = spray(true, 'down');
  ok(a.fired && a.hi && a.plates >= 1, 'a high spray of beans hits a man standing (' + a.plates + ' plate)');
  ok(c.fired && c.plates === 0, '   and passes over a man who gets down');
  const d = spray(false, 'stand'), e = spray(false, 'jump');
  ok(d.fired && !d.hi && d.plates >= 1, 'a low spray (once it is hurt) hits a man standing');
  ok(e.fired && e.plates === 0, '   and passes under a man who jumps it');
}
{
  // steam: at anyone close in front of it, and not further off
  const near = arena(6), b = near.boss;
  b.cd = 999;
  near.p.x = Sim.ext.roaster.front(b) - 40;
  let plates = 0, jet = false;
  for (let k = 0; k < 140; k++) { b.cd = 999; Sim.step(near, inp({ viewW: 468 })); for (const ev of near.events) { if (ev.t === 'steam_jet') jet = true; if (ev.t === 'plate_lost') plates++; } }
  ok(jet && plates >= 1, 'standing close in front of it gets a jet of steam from its grille');
  const far = arena(6), b2 = far.boss;
  far.p.x = Sim.ext.roaster.front(b2) - 120;
  let jet2 = false;
  for (let k = 0; k < 140; k++) { b2.cd = 999; Sim.step(far, inp({ viewW: 468 })); for (const ev of far.events) if (ev.t === 'steam_jet') jet2 = true; }
  ok(!jet2 && far.stats.plates === 0, '   a third of a screen off, none');
}
{
  // the lunge: it shows the line it will stop at, and does not cross it
  const s = arena(7), b = s.boss;
  b.phase = 3; b.next = 0; b.cd = 1;
  s.p.x = s.cam + 30;
  let line = null, maxLeft = 1e9;
  for (let k = 0; k < 400; k++) {
    Sim.step(s, inp({ viewW: 468 }));
    for (const ev of s.events) if (ev.t === 'tell' && ev.k === 'lunge') line = ev.x;
    if (b.st === 'lunge' || b.st === 'brake') maxLeft = Math.min(maxLeft, Sim.ext.roaster.front(b));
    if (b.st === 'idle' && line !== null) break;
  }
  ok(line !== null && maxLeft >= line - 0.5 && s.stats.plates === 0, 'the lunge stops at the line it showed (' + (line && line.toFixed(0)) + ', front at ' + maxLeft.toFixed(0) + '), and a man behind it is safe');
}
{
  // the pour: burning beans along the ground, jumped
  const run = jump => {
    const s = arena(8), b = s.boss;
    b.phase = 2; b.next = 1; b.cd = 1;
    s.p.x = Sim.ext.roaster.front(b) - 130;
    let poured = false, hold = 0;
    for (let k = 0; k < 260; k++) {
      const i = { viewW: 468 };
      if (jump && s.waves.some(w => w.x - s.p.x < 30 && w.x - s.p.x > 0) && !s.p.air) hold = 14;
      if (hold > 0) { i.jump = true; hold--; }
      Sim.step(s, inp(i));
      for (const ev of s.events) if (ev.t === 'pour') poured = true;
      b.cd = Math.max(b.cd, 2);
    }
    return { poured, plates: s.stats.plates };
  };
  const st = run(false), jp = run(true);
  ok(st.poured && st.plates >= 1 && jp.poured && jp.plates === 0, 'once the chimney has gone it pours burning beans along the ground: they burn a man who stands, not one who jumps them');
}
{
  // phases, what falls off it, and the end
  const s = arena(9), b = s.boss;
  const got = [];
  Sim.ext.roaster.hurt(s, R.HP / 3 + 1);
  for (let k = 0; k < 30; k++) { Sim.step(s, inp({ viewW: 468 })); for (const ev of s.events) if (ev.t === 'boss_phase') got.push(ev.n); }
  const p1 = s.pickups.map(q => q.k).join(',');
  Sim.ext.roaster.hurt(s, R.HP / 3 + 1);
  for (let k = 0; k < 120; k++) { Sim.step(s, inp({ viewW: 468 })); for (const ev of s.events) if (ev.t === 'boss_phase') got.push(ev.n); }
  ok(got.join(',') === '2,3' && /gren/.test(p1) && s.pickups.some(q => q.k === 'hmg'), 'at two thirds the chimney goes and grenades fall off it, at one third the drum cracks and a heavy MG falls (' + got.join(',') + ')');
  let dead = false, qm = null, beans = 0, surr = false, cap = false, clear = false;
  Sim.ext.roaster.hurt(s, R.HP);
  for (let k = 0; k < 60 * 20 && !clear; k++) {
    const e = s.qm;
    const want = e && e.st === 'surr' && !e.captured ? (e.x > s.p.x ? 1 : -1) : (dead && (!e || e.captured) ? 1 : 0);
    Sim.step(s, inp({ viewW: 468, mx: want }));
    for (const ev of s.events) {
      if (ev.t === 'boss_dead') { dead = true; beans = s.pickups.filter(q => q.k === 'bean').length; }
      if (ev.t === 'surrender' && ev.k === 'quartermaster') surr = true;
      if (ev.t === 'capture') cap = true;
      if (ev.t === 'clear') clear = true;
    }
  }
  ok(dead && beans === R.BEANS, 'it bursts and rains roast coffee: ' + beans + ' beans to pick up');
  ok(surr && cap, 'the quartermaster climbs out, gives himself up and is walked off');
  ok(clear, 'and with that the mission is clear');
}

// ---- the careful bot gets through, both people freed, at the narrowest and widest pictures
{
  const res = [];
  for (const vw of [384, 468]) for (const seed of [1, 2, 3]) {
    const o = B.run(B.smartBot({}), { level: MOCHA, seed, viewW: vw, continues: 3, seconds: 600, lanes: THUMBS });
    res.push([vw, seed, o.s.status, o.r.freed, Math.round(o.r.time)]);
  }
  ok(res.every(r => r[2] === 'clear' && r[3] === 2), 'the careful bot clears it every time, freeing both: ' + JSON.stringify(res));
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL COFFEE PORT CHECKS OK');
process.exit(fails ? 1 : 0);
