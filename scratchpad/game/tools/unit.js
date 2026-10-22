// unit.js - the mechanics one at a time, with the numbers that matter for feel printed out.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
const LEVEL = require(path.join(__dirname, '../src/level.js'));
LEVEL.ground = require(path.join(__dirname, '../gen/ground.json'));
const T = Sim.T;
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
const inp = o => Object.assign({}, none, o);
// an empty beach: the level with nobody in it
function empty(extra) {
  const L = Object.assign({}, LEVEL, { spawns: [], props: [], gates: [], groups: {} }, extra || {});
  return Sim.create(L, { viewW: 468, seed: 3 });
}
function stepN(s, n, i) { for (let k = 0; k < n; k++) Sim.step(s, typeof i === 'function' ? i(k) : i); }

// ---- movement
{
  const s = empty(); const x0 = s.p.x;
  stepN(s, 60, inp({ mx: 1 }));
  ok(Math.abs((s.p.x - x0) - T.RUN) < 1.5, 'runs ' + (s.p.x - x0).toFixed(0) + ' px in a second (a 468 px screen in ' + (468 / T.RUN).toFixed(1) + ' s)');
  const s2 = empty(); const y0 = s2.p.y; let top = y0, air = 0;
  for (let k = 0; k < 120; k++) { Sim.step(s2, inp({ jump: true })); top = Math.min(top, s2.p.y); if (s2.p.air) air++; }
  ok(y0 - top > 58 && y0 - top < 66, 'full jump rises ' + (y0 - top).toFixed(1) + ' px and lasts ' + (air / 60).toFixed(2) + ' s');
  const s3 = empty(); let top3 = s3.p.y, air3 = 0; const y3 = s3.p.y;
  for (let k = 0; k < 120; k++) { Sim.step(s3, inp({ jump: k < 4 })); top3 = Math.min(top3, s3.p.y); if (s3.p.air) air3++; }
  ok(y3 - top3 > 12 && y3 - top3 < 34, 'a tap hops ' + (y3 - top3).toFixed(1) + ' px in ' + (air3 / 60).toFixed(2) + ' s');
  const s4 = empty(); const c0 = s4.p.x;
  stepN(s4, 60, inp({ mx: 1, my: 1 }));
  ok(s4.p.crouch && Math.abs((s4.p.x - c0) - T.CROUCH_RUN) < 1.5, 'crouch-walks ' + (s4.p.x - c0).toFixed(0) + ' px in a second');
  // jump buffer and coyote time
  const s5 = empty(); s5.p.x = 820; s5.p.plat = 0; s5.p.y = Sim.surfaceY(s5.L, 0, 820); s5.cam = 600;
  let leftAt = -1, jumped = false;
  for (let k = 0; k < 60; k++) {
    const wasAir = s5.p.air;
    Sim.step(s5, inp({ mx: 1, jump: leftAt >= 0 && k === leftAt + 4 }));
    if (!wasAir && s5.p.air && leftAt < 0) leftAt = k;
    for (const e of s5.events) if (e.t === 'jump') jumped = true;
  }
  ok(leftAt > 0 && jumped, 'a jump pressed 4 frames after running off a ledge still jumps (coyote time ' + T.COYOTE + ' frames)');
}
// ---- platforms
{
  const s = empty(); s.cam = 600; s.p.x = 760; s.p.y = Sim.groundY(s.L, 760);
  let landed = null;
  for (let k = 0; k < 90 && landed === null; k++) { Sim.step(s, inp({ jump: k < 20 })); if (!s.p.air && k > 5) landed = s.p.plat; }
  ok(landed === 0, 'jumping under the wreck lands on its deck (surface ' + landed + ', y ' + s.p.y.toFixed(0) + ')');
  stepN(s, 3, inp({ my: 1 }));
  stepN(s, 2, inp({ my: 1, jump: true }));
  let back = false;
  for (let k = 0; k < 60; k++) { Sim.step(s, inp({ my: 1 })); if (!s.p.air && s.p.plat === -1) back = true; }
  ok(back, 'down + jump drops through the deck to the sand');
  // deck to the roof
  const r = empty(); r.cam = 600; r.p.x = 772; r.p.plat = 0; r.p.y = Sim.surfaceY(r.L, 0, 772);
  let onRoof = false;
  for (let k = 0; k < 80; k++) { Sim.step(r, inp({ mx: -1, jump: k < 24 })); if (!r.p.air && r.p.plat === 1) onRoof = true; }
  ok(onRoof, 'a running jump from the middle of the deck reaches the deckhouse roof');
  const r2 = empty(); r2.cam = 600; r2.p.x = 706; r2.p.y = Sim.groundY(r2.L, 706);
  let onRoof2 = false;
  for (let k = 0; k < 80; k++) { Sim.step(r2, inp({ jump: k < 26 })); if (!r2.p.air && r2.p.plat === 1) onRoof2 = true; }
  ok(onRoof2, 'so does a full jump straight up from the sand in front of it');
  // sand to the container top, container to the box above
  const c = empty(); c.cam = 936; c.p.x = 1100; c.p.y = Sim.groundY(c.L, 1100);
  let onBlue = false, onGreen = false;
  for (let k = 0; k < 80; k++) { Sim.step(c, inp({ jump: k < 24 })); if (!c.p.air && c.p.plat === 4) onBlue = true; }
  for (let k = 0; k < 90; k++) { Sim.step(c, inp({ mx: 1, jump: k > 2 && k < 26 })); if (!c.p.air && c.p.plat === 5) onGreen = true; }
  ok(onBlue && onGreen, 'sand to the blue box, and the blue box to the green one, are each one jump');
}
// ---- weapons
{
  const s = empty(); let shots = 0;
  for (let k = 0; k < 120; k++) { Sim.step(s, inp({ fire: true })); for (const e of s.events) if (e.t === 'shot') shots++; }
  ok(shots >= 12 && shots <= 14, 'sidearm, held: ' + (shots / 2).toFixed(1) + ' shots a second');
  const t = empty(); let taps = 0;
  for (let k = 0; k < 120; k++) { Sim.step(t, inp({ fire: k % 5 < 2 })); for (const e of t.events) if (e.t === 'shot') taps++; }
  ok(taps > shots, 'sidearm, tapped every 5 frames: ' + (taps / 2).toFixed(1) + ' shots a second');
  const h = empty(); h.p.weapon = 'hmg'; h.p.ammo = 30; let hs = 0, empty_ = false;
  for (let k = 0; k < 180; k++) { Sim.step(h, inp({ fire: true })); for (const e of h.events) { if (e.t === 'shot' && e.w === 'hmg') hs++; if (e.t === 'weapon_empty') empty_ = true; } }
  ok(hs === 30 && empty_ && h.p.weapon === 'side', 'heavy MG fires ' + (60 / T.HMG_CD).toFixed(0) + ' a second, runs dry after its rounds and falls back to the sidearm');
  // grenade
  const g = empty(); const gx = g.p.x; let boom = null;
  for (let k = 0; k < 200 && !boom; k++) { Sim.step(g, inp({ grenade: k === 0 })); for (const e of g.events) if (e.t === 'explode') boom = { x: e.x, t: k }; }
  ok(boom && boom.x - gx > 80 && boom.x - gx < 130, 'a grenade thrown standing still goes off ' + (boom.x - gx).toFixed(0) + ' px ahead after ' + (boom.t / 60).toFixed(2) + ' s, one bounce on the way');
  ok(g.p.grenades === T.GREN_MAX - 1, 'ten grenades, one gone');
}
// ---- aim assist
{
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 300, post: 1 }] });
  const test = (ex, ey) => {
    const s = Sim.create(L, { viewW: 468, seed: 1 });
    s.enemies[0].x = ex; s.enemies[0].y = ey; s.enemies[0].cd = 9999;
    Sim.step(s, inp({ fire: true }));
    const b = s.bullets[0];
    return Math.atan2(-b.vy, b.vx) * 180 / Math.PI;
  };
  const gy = Sim.groundY(LEVEL, 118);
  const a1 = test(118 + 140, gy - 28), a2 = test(118 + 100, gy - 80);
  ok(a1 > 5 && a1 < 20, 'a man 140 px ahead and 28 px up: the shot bends ' + a1.toFixed(1) + ' degrees to him');
  ok(Math.abs(a2) < 0.01, 'a man 100 px ahead and 80 px up is outside 20 degrees: the shot goes straight (' + a2.toFixed(1) + ')');
}
// ---- aiming at 45 degrees
{
  const s = empty(); let b = null;
  Sim.step(s, inp({ mx: 1, my: -1, fire: true })); b = s.bullets[0];
  const a1 = Math.atan2(-b.vy, b.vx) * 180 / Math.PI;
  ok(s.p.aim === 'diag' && Math.abs(a1 - 45) < 0.01, 'stick up and along: the shot leaves at ' + a1.toFixed(0) + ' degrees, on the run');
  const u = empty(); Sim.step(u, inp({ my: -1, fire: true }));
  ok(u.p.aim === 'up' && Math.abs(u.bullets[0].vx) < 0.01 && u.bullets[0].vy < 0, 'stick straight up: straight up, standing');
  const d = empty(); stepN(d, 10, inp({ jump: true })); d.bullets.length = 0; d.p.fireCd = 0;
  Sim.step(d, inp({ mx: 1, my: 1, fire: true, jump: true })); b = d.bullets[d.bullets.length - 1];
  const a2 = Math.atan2(-b.vy, b.vx) * 180 / Math.PI;
  ok(d.p.aim === 'ddiag' && Math.abs(a2 + 45) < 0.01, 'in the air, down and along: ' + a2.toFixed(0) + ' degrees');
  const l = empty(); Sim.step(l, inp({ mx: -1, my: -1, fire: true })); b = l.bullets[0];
  ok(b.vx < 0 && b.vy < 0 && Math.abs(b.vx + b.vy * -1 * -1 - 2 * b.vx) < 1e-6 || Math.abs(Math.abs(b.vx) - Math.abs(b.vy)) < 1e-6, 'and the same to the left');
  // a man up on a box, 45 degrees off: level shots pass under him, the diagonal reaches him
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 300, post: 1 }] });
  const mk = () => { const t = Sim.create(L, { viewW: 468, seed: 1 }); const e = t.enemies[0]; e.x = t.p.x + 96; e.y = t.p.y - 84; e.cd = 9999; e.plat = -2; e.air = false; return t; };
  let t = mk(), hits = 0;
  for (let k = 0; k < 50; k++) { Sim.step(t, inp({ fire: true })); t.enemies[0] && (t.enemies[0].cd = 9999); for (const e of t.events) if (e.t === 'hit' && e.kind === 'body') hits++; }
  ok(hits === 0, 'a man 96 px along and 84 px up cannot be reached with level fire');
  t = mk(); hits = 0; const x0 = t.p.x;
  t.p.x = t.cam + 9;                                           // (against the left edge of the screen, so pushing along does not carry him away)
  t.enemies[0].x = t.p.x + 96;
  for (let k = 0; k < 50; k++) { Sim.step(t, inp({ mx: -1, my: -1, fire: false })); }
  for (let k = 0; k < 50 && !hits; k++) { Sim.step(t, inp({ mx: 1, my: -1, fire: true })); for (const e of t.events) if (e.t === 'hit' && e.kind === 'body') hits++; }
  ok(hits > 0, 'the 45 degree shot gets him');
}
// ---- the man with the door
{
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'door', x: 240, post: 1 }] });
  const mk = (px) => { const s = Sim.create(L, { viewW: 468, seed: 1 }); s.enemies[0].cd = 9999; s.enemies[0].st = 'wait'; if (px) s.p.x = px; return s; };
  const hold = s => { const e = s.enemies[0]; if (e && e.alive && e.door > 0) { e.cd = 9999; e.bashCd = 9999; } };
  let s = mk();
  let clang = 0, body = 0, broke = -1, died = -1, shots = 0;
  for (let k = 0; k < 400 && died < 0; k++) {
    Sim.step(s, inp({ fire: true })); hold(s);
    for (const e of s.events) { if (e.t === 'shot') shots++; if (e.t === 'hit') { if (e.kind === 'door') clang++; if (e.kind === 'body') body++; } if (e.t === 'door_break') broke = k; if (e.t === 'die') died = k; }
  }
  ok(clang === T.DOOR_HITS && broke > 0, 'shots from the front ring off the door, and after ' + clang + ' of them it comes apart (' + (broke / 60).toFixed(1) + ' s of holding the sidearm on it)');
  ok(died > broke && body === Sim.KIND.door.hp, 'the man behind it then takes ' + body + ' hits (down ' + ((died - broke) / 60).toFixed(2) + ' s after his door)');
  s = mk(); s.p.weapon = 'hmg'; s.p.ammo = 200; broke = -1;
  for (let k = 0; k < 200 && broke < 0; k++) { Sim.step(s, inp({ fire: true })); hold(s); for (const e of s.events) if (e.t === 'door_break') broke = k; }
  ok(broke > 0 && broke < 80, 'the heavy MG chews through the door in ' + (broke / 60).toFixed(1) + ' s');
  // grenades: from the front the door takes it, from behind he does
  s = mk(); broke = -1; let alive = true;
  for (let k = 0; k < 110; k++) { Sim.step(s, inp({ grenade: k === 0 })); hold(s); for (const e of s.events) if (e.t === 'door_break') broke = k; }
  ok(broke > 0 && s.enemies[0].alive && s.enemies[0].door === 0, 'a grenade thrown at him from 120 px takes the door and leaves the man');
  s = mk(); const e1 = s.enemies[0];
  s.bombs.push({ id: 999, kind: 'gren', own: true, x: e1.x + 16, y: e1.y - 2, vx: 0, vy: 0, air: false, fuse: 2, bounced: 1, t: 0 });
  stepN(s, 6, none);
  ok(!e1.alive, 'one that lands behind him deals with him outright');
  s = mk(); const e2 = s.enemies[0];
  s.props.push({ id: 998, k: 'drum', x: e2.x - 24, y: e2.y, plat: -1, t: 0, st: 'idle', gone: false, hp: 0, paint: 'oxide', fuse: 2 });
  stepN(s, 6, none);
  ok(!e2.alive, 'a drum going up in front of him is too much for any door');
  // behind him
  s = mk(300); s.p.face = -1; body = 0;
  for (let k = 0; k < 60; k++) { Sim.step(s, inp({ fire: true })); const e = s.enemies[0]; if (e && e.alive) { e.cd = 9999; e.bashCd = 9999; e.turnT = 0; } if (k === 0) s.p.face = -1; for (const ev of s.events) if (ev.t === 'hit' && ev.kind === 'body') body++; }
  ok(!s.enemies[0] || !s.enemies[0].alive, 'shots in the back get through: ' + body + ' and he is down');
  s = mk(300); s.p.face = -1; let turned = -1;
  for (let k = 0; k < 60 && turned < 0; k++) { Sim.step(s, none); if (s.enemies[0].face === 1) turned = k; }
  ok(turned > 0 && turned <= T.DOOR_TURN + 2, 'but he turns to face you in ' + (turned / 60).toFixed(2) + ' s');
  // leaning out to fire, the door is lowered: stand and you can hit him, crouch and you hit the door
  s = mk(); s.enemies[0].cd = 0; let leanAt = -1; body = 0; clang = 0;
  for (let k = 0; k < 200 && leanAt < 0; k++) { Sim.step(s, none); if (s.enemies[0].st === 'lean') leanAt = k; }
  for (let k = 0; k < 44; k++) { Sim.step(s, inp({ fire: true })); for (const e of s.events) if (e.t === 'hit') { if (e.kind === 'body') body++; if (e.kind === 'door') clang++; } }
  ok(leanAt >= 0 && body >= 2, 'when he drops the door to fire over it, standing shots reach him (' + body + ' in the time it is down)');
  s = mk(); s.enemies[0].cd = 0; leanAt = -1; body = 0; clang = 0;
  for (let k = 0; k < 200 && leanAt < 0; k++) { Sim.step(s, inp({ my: 1 })); if (s.enemies[0].st === 'lean') leanAt = k; }
  for (let k = 0; k < 60; k++) { Sim.step(s, inp({ my: 1, fire: true })); for (const e of s.events) { if (e.t === 'hit') { if (e.kind === 'body') body++; if (e.kind === 'door') clang++; } } }
  ok(body === 0 && clang >= 2 && s.p.plates === T.PLATES, 'crouching keeps you under his three shots, but your own then only find the door (' + clang + ' on it)');
  // the shove
  s = mk(222); s.enemies[0].bashCd = 0; s.enemies[0].cd = 9999; let tell = -1, hit = -1, x0 = 0;
  for (let k = 0; k < 90; k++) { Sim.step(s, none); const e = s.enemies[0]; e.cd = 9999; for (const ev of s.events) { if (ev.t === 'tell' && ev.k === 'bash' && tell < 0) { tell = k; x0 = s.p.x; } if (ev.t === 'bash' && ev.hit && hit < 0) hit = k; } if (hit >= 0) e.bashCd = 9999; }
  ok(tell >= 0 && hit > tell && s.p.plates === T.PLATES - 1 && s.p.x < x0 - 24, 'stand within reach and he swings the door: ' + ((hit - tell) / 60).toFixed(2) + ' s of warning, a plate gone, and Yazeed shoved back ' + (x0 - s.p.x).toFixed(0) + ' px');
  s = mk(222); s.enemies[0].bashCd = 0; tell = -1; let missed = false;
  for (let k = 0; k < 90; k++) { Sim.step(s, inp({ mx: tell >= 0 ? -1 : 0 })); const e = s.enemies[0]; e.cd = 9999; for (const ev of s.events) { if (ev.t === 'tell' && ev.k === 'bash') tell = k; if (ev.t === 'bash' && !ev.hit) missed = true; } }
  ok(missed && s.p.plates === T.PLATES, 'step back when he winds up and it meets only air');
  s = mk(222); s.enemies[0].bashCd = 0; tell = -1; missed = false;
  for (let k = 0; k < 90; k++) { Sim.step(s, inp({ jump: tell >= 0 && k < tell + 20 })); const e = s.enemies[0]; e.cd = 9999; for (const ev of s.events) { if (ev.t === 'tell' && ev.k === 'bash') tell = k; if (ev.t === 'bash' && !ev.hit) missed = true; } }
  ok(missed && s.p.plates === T.PLATES, 'or jump');
  // jumping over and shooting down at 45 degrees gets over the door
  s = mk(196); body = 0;
  for (let k = 0; k < 60; k++) { Sim.step(s, inp({ mx: 1, my: s.p.air ? 1 : 0, jump: k < 30, fire: true })); hold(s); for (const ev of s.events) if (ev.t === 'hit' && ev.kind === 'body') body++; }
  ok(body >= 1, 'a jump toward him firing down at 45 degrees puts ' + body + ' over the top of the door');
  s = mk();
  const aim = Sim.assist(s, Sim.muzzle(s.p), true);
  ok(aim !== null, 'the gun now bears on a raised door, so auto-fire wears it down too');
}
// ---- the last man, capture, the detainee
{
  const L = Object.assign({}, LEVEL, { props: [{ k: 'detainee', x: 200, zone: 0 }], gates: [], groups: { X: { zone: 0, trig: 0, lastManSurrenders: true } },
    spawns: [{ g: 'X', k: 'rifle', x: 300, post: 1 }, { g: 'X', k: 'rifle', x: 380, post: 1 }] });
  const s = Sim.create(L, { viewW: 468, seed: 1 }); const seen = {};
  s.enemies.forEach(e => e.cd = 9999);
  for (let k = 0; k < 600; k++) {
    Sim.step(s, inp({ mx: 1, fire: s.enemies.some(e => e.alive && e.hostile) }));
    s.enemies.forEach(e => e.cd = 9999);
    for (const e of s.events) seen[e.t] = (seen[e.t] || 0) + 1;
  }
  ok(seen.die === 1 && seen.surrender === 1 && seen.capture === 1, 'two men: one shot, the other gives up and is taken by walking into him');
  ok(seen.freed === 1 && s.stats.freed === 1 && s.p.grenades === T.GREN_MAX + 5, 'the detainee is freed on contact and hands over five grenades');
  ok(s.radio === 2, 'a capture and a rescue fill two radio bars');
  const before = s.score;
  ok(before === 100 + 200 + 500 + 100, 'score: 100 for the kill, 200 for the capture, 500 for the rescue, 100 for the grenades');
  // a surrendered man cannot be hurt

}
// ---- armour, lives, continue
{
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 240, post: 1 }] });
  let s = Sim.create(L, { viewW: 468, seed: 1 }); const seen = {}; let firstHit = -1;
  for (let k = 0; k < 60 * 80 && s.status === 'play'; k++) { Sim.step(s, none); for (const e of s.events) { seen[e.t] = (seen[e.t] || 0) + 1; if (e.t === 'plate_lost' && firstHit < 0) firstHit = k; } }
  ok(s.status === 'over' && seen.plate_lost === 6 && seen.life_lost === 3 && seen.respawn === 2 && seen.low_armour === 3, 'standing in front of a rifleman: 3 plates a life, 3 lives, then game over (first hit after ' + (firstHit / 60).toFixed(1) + ' s)');
  const c = Sim.continueZone(s);
  ok(c.status === 'play' && c.p.lives === T.LIVES && c.p.plates === T.PLATES && c.stats.continues === 1 && c.enemies.length === 1, 'continue: same zone again, three lives, the men back at their posts');
  // crouching under level fire
  s = Sim.create(L, { viewW: 468, seed: 1 }); let hit = 0;
  for (let k = 0; k < 60 * 20; k++) { Sim.step(s, inp({ my: 1 })); for (const e of s.events) if (e.t === 'plate_lost') hit++; }
  ok(hit === 0, 'crouching, his bursts pass overhead for 20 s');
}
// ---- things that go off
{
  const L = Object.assign({}, LEVEL, { props: [{ k: 'mine', x: 230, zone: 0 }, { k: 'drum', x: 268, paint: 'oxide', zone: 0 }], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 250, post: 1 }] });
  const s = Sim.create(L, { viewW: 468, seed: 1 }); s.enemies[0].cd = 9999; s.enemies[0].hp = 4;
  const seen = [];
  s.bullets.push({ x: 200, y: Sim.groundY(L, 200) - 12, vx: 450, vy: 0, life: 40, own: true });
  for (let k = 0; k < 60; k++) { Sim.step(s, none); for (const e of s.events) if (e.t === 'explode') seen.push(e.kind); }
  ok(seen.join() === 'mine,drum' && (!s.enemies[0] || !s.enemies[0].alive), 'shooting the mine sets off the drum beside it, and the man between them is gone');
  const m = Sim.create(Object.assign({}, L, { spawns: [], groups: {} }), { viewW: 468, seed: 1 });
  let lost = 0;
  for (let k = 0; k < 120; k++) { Sim.step(m, inp({ mx: 1 })); for (const e of m.events) if (e.t === 'plate_lost') lost++; }
  ok(lost === 1, 'walking onto the mine costs a plate');
}
// ---- bomber
{
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'bomber', x: 290, post: 1 }] });
  let s = Sim.create(L, { viewW: 468, seed: 1 }); let lob = -1, boom = -1, bx = 0;
  for (let k = 0; k < 400 && boom < 0; k++) { Sim.step(s, none); for (const e of s.events) { if (e.t === 'lob' && lob < 0) lob = k; if (e.t === 'explode') { boom = k; bx = e.x; } } }
  ok(lob > 0 && boom > lob && Math.abs(bx - s.p.x) < 12 && s.p.plates === T.PLATES - 1, 'the bomber winds up, lobs, and ' + ((boom - lob) / 60).toFixed(2) + ' s later it goes off at your feet if you stand still');
  s = Sim.create(L, { viewW: 468, seed: 1 }); let lost = 0, walked = false;
  let dir = -1;
  for (let k = 0; k < 600; k++) {
    let l = false;
    for (const b of s.bombs) if (!b.own && !b.gone) l = true;
    if (!l) dir = s.p.x < 90 ? 1 : -1;
    Sim.step(s, inp({ mx: l ? dir : 0 }));
    for (const e of s.events) if (e.t === 'plate_lost') lost++;
  }
  ok(lost === 0, 'stepping away when it is in the air: no plates lost in 10 s');
  s = Sim.create(L, { viewW: 468, seed: 1 }); const seen = {};
  for (let k = 0; k < 400; k++) { const lit = s.enemies[0] && s.enemies[0].lit; Sim.step(s, inp({ fire: !!lit })); for (const e of s.events) seen[e.t + (e.kind ? ':' + e.kind : '')] = 1; }
  ok(seen.die && seen['explode:dyn'], 'shot while winding up, he drops it and it goes off where he stood');
}
// ---- the fight is staged away from the thumbs: the screen stops at a gate, Yazeed walks on across it, and nobody fights from the edge lanes
{
  for (const [vw, lanes, label] of [[384, [T.LANE_L, T.LANE_R], 'thumbs over the picture'], [468, [T.LANE_L, T.LANE_R], 'thumbs over the picture'], [468, [0.07, 0.09], 'nothing over the picture']]) {
    const L = Object.assign({}, LEVEL, { props: [], gates: [{ id: 'g', x: 400, groups: ['X'] }], groups: { X: { zone: 0, trig: 150 } },
      spawns: [{ g: 'X', k: 'rifle', enter: 1, delay: 0 }, { g: 'X', k: 'rifle', enter: -1, delay: 30 }, { g: 'X', k: 'bomber', enter: 1, delay: 60 }, { g: 'X', k: 'door', enter: 1, delay: 90 }] });
    const s = Sim.create(L, { viewW: vw, seed: 5, lanes: lanes });
    let maxFrac = 0, tells = [], gone = false, stoppedAt = -1;
    for (let k = 0; k < 60 * 14; k++) {
      const x0 = s.p.x;
      Sim.step(s, inp({ mx: 1, my: 1 }));            // crouch-walk right the whole time, never firing
      s.p.plates = 3; s.p.inv = 5;                    // (he is not here to be hurt)
      maxFrac = Math.max(maxFrac, (s.p.x - s.cam) / vw);
      if (stoppedAt < 0 && Math.abs(s.cam - (400 - vw * T.HOLD)) < 0.5) stoppedAt = (s.p.x - s.cam) / vw;
      for (const e of s.events) if (e.t === 'tell' && e.k !== 'bash') tells.push((e.x - s.cam) / vw);
    }
    const lo = Math.min.apply(null, tells), hi = Math.max.apply(null, tells), edge = 1 - lanes[1] - 4 / vw;
    ok(Math.abs(s.cam - (400 - vw * T.HOLD)) < 0.5 && stoppedAt > 0 && stoppedAt < 0.5 && Math.abs(maxFrac - edge) < 0.005,
      'gate shut, ' + vw + ' wide, ' + label + ': the screen stops with Yazeed ' + (stoppedAt * 100).toFixed(0) + '% of the way across, and he can walk on to ' + (maxFrac * 100).toFixed(0) + '%');
    ok(tells.length >= 5 && lo >= lanes[0] - 0.01 && hi <= 1 - lanes[1] + 0.01, '   ' + tells.length + ' attacks begun, all from between ' + (lo * 100).toFixed(0) + '% and ' + (hi * 100).toFixed(0) + '% of the way across');
    for (const e of s.enemies) if (e.alive && e.hostile) { e.hp = 0; e.door = 0; }
    for (const e of s.enemies.slice()) if (e.alive && e.hostile) { s.bullets.push({ x: e.x - 3, y: e.y - 30, vx: 100, vy: 0, life: 5, own: true, age: 5 }); }
    for (let k = 0; k < 400; k++) { Sim.step(s, inp({ mx: 1 })); for (const e of s.events) if (e.t === 'go') gone = true; }
    ok(gone && s.p.x > 600, '   with them dealt with the gate opens and he runs on (x ' + s.p.x.toFixed(0) + ')');
  }
  // while a gate is shut, nothing further on can be woken by walking: every later trigger and checkpoint is out of his reach
  let bad = [];
  for (const vw of [384, 468]) for (const lr of [T.LANE_R, 0.09]) {
    LEVEL.gates.forEach((g, i) => {
      const reach = g.x + vw * (T.HOLD - lr);
      for (const k in LEVEL.groups) { const gr = LEVEL.groups[k]; if (gr.trig != null && gr.trig > g.x && g.groups.indexOf(k) < 0 && gr.trig <= reach) bad.push(g.id + ' reaches trigger ' + k); }
      LEVEL.zones.forEach(z => { if (z.x > g.x && z.x <= reach) bad.push(g.id + ' reaches zone ' + z.name); });
      if (LEVEL.exitX <= reach) bad.push(g.id + ' reaches the exit');
    });
  }
  ok(bad.length === 0, 'with a gate shut, the furthest he can walk wakes nothing beyond it' + (bad.length ? ': ' + bad.join(', ') : ''));
}
// ---- a man behind sandbags
{
  const mk = () => {
    const L = Object.assign({}, LEVEL, { props: [{ k: 'cover', x: 916, x0: 886, x1: 946, top: 150, zone: 0 }], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [{ g: 'X', k: 'rifle', x: 914, post: 1, covered: 1 }],
      zones: [{ x: 0, name: 'z', spawn: 800 }] });
    const s = Sim.create(L, { viewW: 468, seed: 2 });
    s.cam = 640;
    return s;
  };
  let s = mk(), bags = 0, body = 0, upTicks = 0;
  s.enemies[0].cd = 99999;                                    // he stays down
  for (let k = 0; k < 240; k++) { Sim.step(s, inp({ fire: true })); for (const e of s.events) if (e.t === 'hit') { if (e.kind === 'bags') bags++; if (e.kind === 'body') body++; } }
  ok(bags > 20 && body === 0 && s.enemies[0].alive, 'head down behind the bags: ' + bags + ' standing shots stop in the sandbags and none reach him');
  ok(Sim.assist(s, Sim.muzzle(s.p), true) === null, 'and the gun does not aim at him while he is down, so auto-fire holds its fire');
  s = mk(); let fired = 0, died = -1, upAt = -1;
  for (let k = 0; k < 600 && died < 0; k++) {
    const e0 = s.enemies[0], up = e0 && e0.alive && !Sim.ducked(e0);
    if (up && upAt < 0) upAt = k;
    Sim.step(s, inp({ fire: up, my: up ? 0 : 1 }));           // crouch under his fire, stand and shoot when he comes up
    for (const e of s.events) { if (e.t === 'shot') fired++; if (e.t === 'die') died = k; }
  }
  ok(died > 0 && fired <= 4, 'when he comes up to aim he can be shot: down after ' + fired + ' shot' + (fired === 1 ? '' : 's') + ', ' + ((died - upAt) / 60).toFixed(2) + ' s after he showed himself');
  s = mk(); s.enemies[0].cd = 99999; s.p.x = 812; let dead = false;
  for (let k = 0; k < 200; k++) { Sim.step(s, inp({ grenade: k === 2 })); for (const e of s.events) if (e.t === 'die') dead = true; }
  ok(dead, 'a grenade from 100 px away gets him while he is down');
}
// ---- a drum burns before it goes
{
  const L = Object.assign({}, LEVEL, { props: [{ k: 'drum', x: 300, paint: 'oxide', zone: 0 }], gates: [], groups: {}, spawns: [] });
  let s = Sim.create(L, { viewW: 468, seed: 1 }); let lit = -1, boom = -1, lost = 0;
  s.p.x = 270; s.p.y = Sim.groundY(L, 270);
  for (let k = 0; k < 200; k++) {
    Sim.step(s, inp({ fire: lit < 0, mx: lit >= 0 ? -1 : 0 }));
    for (const e of s.events) { if (e.t === 'drum_lit') lit = k; if (e.t === 'explode') boom = k; if (e.t === 'plate_lost') lost++; }
  }
  ok(lit > 0 && Math.abs(boom - lit - T.DRUM_FUSE) <= 1 && lost === 0, 'a drum shot from 30 px away burns for ' + ((boom - lit) / 60).toFixed(2) + ' s before it goes: time to step clear without losing a plate');
  s = Sim.create(L, { viewW: 468, seed: 1 }); s.p.x = 270; s.p.y = Sim.groundY(L, 270); lost = 0;
  for (let k = 0; k < 200; k++) { Sim.step(s, inp({ fire: k < 30 })); for (const e of s.events) if (e.t === 'plate_lost') lost++; }
  ok(lost === 1, 'standing beside it anyway costs a plate');
}
console.log(fails ? '\n' + fails + ' FAILED' : '\nALL MECHANICS OK');
process.exit(fails ? 1 : 0);
