// unit5.js - Yazeed's shots and the edge lanes (builds 10 and 11).
// Build 9 dropped his shots where the right-hand lane begins (a quarter of the way in from the edge with the thumbs over
// the picture): Khaled saw an invisible wall. Build 10 let them fly to the edge and hit anything: then the Scorpion's men
// died the moment they showed. Build 11: the shots fly to the edge, and a man (or a truck, or a drone) still coming in
// through an edge lane is guarded: the shot glances off him and he flashes, until he is in the middle, where the fight
// is. Nobody starts an attack from the lanes.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
const LEVEL = require(path.join(__dirname, '../src/level.js'));
LEVEL.ground = require(path.join(__dirname, '../gen/ground.json'));
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
const inp = o => Object.assign({}, none, o);
const THUMBS = [0.18, 0.25];

// ---- a level shot from as far left as he can stand, with nobody in the way, reaches the right-hand edge
for (const vw of [384, 449, 468]) {
  const L = Object.assign({}, LEVEL, { spawns: [], props: [], gates: [], groups: {} });
  const s = Sim.create(L, { viewW: vw, seed: 3, lanes: THUMBS });
  s.p.x = s.cam + 12;
  Sim.step(s, inp({ fire: true, viewW: vw, lanes: THUMBS }));
  const b = s.bullets.find(q => q.own);
  let far = b ? b.x : -1;
  for (let k = 0; k < 200 && b && !b.gone; k++) { Sim.step(s, inp({ viewW: vw, lanes: THUMBS })); far = Math.max(far, b.x); }
  ok(b && (far - s.cam) / vw >= 1.0, `${vw} wide, thumbs over the picture: with nobody in the way the shot flies to ${Math.round((far - s.cam) / vw * 100)}% of the way across`);
}

// ---- a man still out in the right-hand lane: shots glance off him, he starts nothing; once in the middle he goes down
function laneMan(vw, frac) {
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 300, post: 1 }] });
  const s = Sim.create(L, { viewW: vw, seed: 1, lanes: THUMBS });
  const e = s.enemies[0];
  e.x = s.cam + vw * frac; e.y = s.p.y; e.plat = -2; e.air = false; e.face = -1;
  return { s, e };
}
for (const [vw, frac] of [[449, 0.86], [468, 0.93], [384, 0.80]]) {
  let { s, e } = laneMan(vw, frac);
  let body = 0, glance = 0, tells = 0;
  const hp0 = e.hp;
  for (let k = 0; k < 60; k++) {
    e.cd = 9999; e.x = s.cam + vw * frac;
    Sim.step(s, inp({ fire: true, viewW: vw, lanes: THUMBS }));
    for (const ev of s.events) { if (ev.t === 'hit' && ev.kind === 'body') body++; if (ev.t === 'hit' && ev.kind === 'guard') glance++; }
  }
  ok(e.alive && e.hp === hp0 && body === 0 && glance > 0 && Sim.guarded(s, e), `${vw} wide: a man ${Math.round(frac * 100)}% of the way across is still coming in: ${glance} shots glance off him, none hurt him`);
  ({ s, e } = laneMan(vw, frac));
  for (let k = 0; k < 240; k++) {
    if (k === 0) e.cd = 0;
    e.x = s.cam + vw * frac;
    Sim.step(s, inp({ viewW: vw, lanes: THUMBS }));
    for (const ev of s.events) if (ev.t === 'tell') tells++;
  }
  ok(tells === 0, `   and standing there for four seconds he starts no attack (${tells})`);
  ({ s, e } = laneMan(vw, 0.62));
  let down = false;
  for (let k = 0; k < 60 && !down; k++) { e.cd = 9999; Sim.step(s, inp({ fire: true, viewW: vw, lanes: THUMBS })); down = !e.alive; }
  ok(down && !Sim.guarded(s, e), '   a man 62% of the way across (in the middle) goes down to the same fire');
}

// ---- grenades: a blast does not hurt a man still coming in either
{
  const { s, e } = laneMan(449, 0.9);
  const hp0 = e.hp;
  Sim._.explode(s, e.x, e.y - 10, 30, 'gren', true);
  ok(e.alive && e.hp === hp0, 'a grenade going off on a man still coming in does not hurt him');
  const m = laneMan(449, 0.6);
  Sim._.explode(m.s, m.e.x, m.e.y - 10, 30, 'gren', true);
  ok(!m.e.alive, '   one going off on a man in the middle does');
}

// ---- on the coast road: a truck out in the lane takes no harm; in the middle it does
{
  const s = Sim.create(LEVEL, { viewW: 449, seed: 11, zone: 3, lanes: THUMBS });
  const D = Sim.ext.drive;
  const mk = frac => { const x = s.cam + 449 * frac; return { id: 999, x: x, y: Sim.groundY(LEVEL, x), vx: 0, face: -1, mode: 'park', hp: 8, gun: 0, gst: 'idle', gT: 0, st: 'ok', hurtT: 99 }; };
  s.trucks.length = 0; s.trucks.push(mk(0.88));
  let t = s.trucks[0];
  const g1 = D.shot(s, { x: t.x, y: t.y - 20, vx: 450, vy: 0, own: true });
  ok(g1 && t.hp === 8, 'the coast road: a shot at a truck 88% of the way across glances off (' + t.hp + ' of 8 left)');
  s.trucks.length = 0; s.trucks.push(mk(0.6)); t = s.trucks[0];
  const g2 = D.shot(s, { x: t.x, y: t.y - 20, vx: 450, vy: 0, own: true });
  ok(g2 && t.hp === 7, '   and one at a truck 60% of the way across hurts it (' + t.hp + ' of 8 left)');
}

// ---- the boat: on a low pass out at the edge it still takes his shots (it is not coming in, it is the fight)
{
  const s = Sim.create(LEVEL, { viewW: 449, seed: 5, zone: 4, lanes: THUMBS });
  const x = s.cam + 449 * 0.9, y = 120;
  s.boss = { kind: 'boat', full: 100, x: x, y: y, x0: x, y0: y, vx: 0, hp: 100, phase: 1, st: 'swoop', stT: 0, t: 0, hurtT: 99, cd: 0, next: 0, dir: -1, n: 0, tilt: 0, t0: 0, lowY: y, face: -1 };
  const hit = Sim.ext.boss.shot(s, { x: x, y: y, vx: 450, vy: 0, own: true });
  ok(hit && s.boss.hp === 99, 'the boat on a low pass 90% of the way across takes a shot (' + s.boss.hp + ' of 100 left)');
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL SHOT AND LANE CHECKS OK');
process.exit(fails ? 1 : 0);
