// unit8.js - The Souq (build 28; the Great Scale, build 29): the level agrees with the painting, every posted man stands
// where he can be fought, the spice sacks and their clouds (a Dhanab who sneezes cannot fight, nor can Yazeed), the
// barricades (they stop him, they wear down, grenades and drums do it faster, the men behind come through when they go,
// auto-fire works at them), the rooftops (walls, drops, the gaps), the shopkeepers, the Great Scale's every move, and
// the careful bot gets through.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
require(path.join(__dirname, '../src/scale.js'));
const ZABID = require(path.join(__dirname, '../src/level_zabid.js'));
const STAGE = require(path.join(__dirname, '../gen/stage_zabid.json'));
ZABID.ground = STAGE.ground;
const B = require('./bot.js');
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
const inp = o => Object.assign({}, none, o);
const T = Sim.T, I = Sim._, THUMBS = [0.18, 0.25];

// ---- the level and the painting
{
  const bad = [];
  for (const pl of ZABID.plats) {
    if (pl.dyn) continue;                       // (the Great Scale's spice pan is not painted: it rides up and down with the beam)
    const p2 = STAGE.plats[pl.id];
    if (!p2 || JSON.stringify(p2) !== JSON.stringify(pl.pts)) bad.push(pl.id);
  }
  for (const id in STAGE.plats) if (!ZABID.plats.some(p => p.id === id)) bad.push(id + ' (painted, not in the level)');
  ok(!bad.length, 'every platform in the level is where the painting has it, and every painted one is in the level' + (bad.length ? ': ' + bad.join(', ') : ''));
  ok(STAGE.world.WORLD === ZABID.width && JSON.stringify(STAGE.world.pits) === JSON.stringify(ZABID.pits), 'the length and the gaps between the roofs agree with the painting');
  const doors = STAGE.world.doors, off = [];
  for (const sp of ZABID.spawns) if (sp.door && !doors.some(d => Math.abs(d - sp.x) <= 2)) off.push(sp.g + '@' + sp.x);
  ok(!off.length, 'every man who comes out of a door comes out of a painted one' + (off.length ? ': not ' + off.join(', ') : ''));
  const bars = ZABID.props.filter(o => o.bar), wrong = [];
  for (const o of bars) {
    const w = STAGE.world.bars[o.bar], back = ZABID.plats.find(p => p.id === o.bar + 'back');
    if (!w || w.x0 !== o.x0 || w.x1 !== o.x1 || !back || back.pts[1][0] !== o.x1 || back.pts[0][0] < o.x0 + T.BAR_W - 12) wrong.push(o.bar);
  }
  ok(bars.length === 3 && !wrong.length, 'three barricades, each where the painting leaves room for it, with the crates behind it to stand on' + (wrong.length ? ': ' + wrong.join(', ') : ''));
  // the ground is flat at 184 off the rooftops, and the rooftops are what the painting has (gaps a long way down)
  const gy = x => Sim.groundY(ZABID, x);
  ok(gy(500) === 184 && gy(2000) === 184 && gy(4200) === 184 && gy(2700) < 160 && gy(2780) > 185 && gy(3000) > 185 && gy(3310) > 185,
    'the street at 184, the roofs up at ' + gy(2700) + ', the gaps between them down at ' + gy(2780).toFixed(0));
  // walls is on for the Souq only
  ok(ZABID.walls === true && !B.LEVEL.walls && !B.MOCHA.walls, 'steps and walls are the Souq\'s alone');
}

// ---- every posted man stands inside the middle of his gate's screen at every width (or he would be guarded for ever)
{
  const gateOf = g => ZABID.gates.find(gt => gt.groups.indexOf(g) >= 0);
  const out = [];
  for (const vw of [384, 416, 449, 468]) {
    for (const sp of ZABID.spawns) {
      if (!sp.post) continue;
      const gt = gateOf(sp.g), cam = gt.x - vw * T.HOLD;
      const lo = cam + vw * THUMBS[0] - 10, hi = cam + vw * (1 - THUMBS[1]) + 10;
      if (sp.x < lo || sp.x > hi) out.push(vw + ':' + sp.g + '@' + sp.x);
    }
  }
  ok(!out.length, 'every posted man can be fought from where his gate holds the screen, 384 to 468 wide' + (out.length ? ': ' + out.join(', ') : ''));
  const det = ZABID.props.filter(o => o.k === 'detainee');
  const shops = det.filter(o => o.look && /^shop_/.test(o.look));
  ok(det.length === 4 && shops.length === 3 && new Set(shops.map(o => o.look)).size === 3, 'four people held: three shopkeepers behind their counters, each his own man, and one more up on the roofs');
  const s = Sim.create(ZABID, { viewW: 468, seed: 1, lanes: THUMBS });
  ok(s.stats.detainees === 4, 'all four count for the Liberator');
}

// a quiet stretch of the level with one thing in it
function bare(extra) {
  return Object.assign({}, ZABID, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [], scale: null }, extra || {});
}
function events(s, t) { return s.events.filter(e => e.t === t); }

// ---- a sack of spice: shot open, a cloud; a Dhanab in it sneezes and does nothing else for a while
{
  const L = bare({ props: [{ k: 'spice', x: 300, col: 'red', zone: 0 }], spawns: [{ g: 'X', k: 'rifle', x: 312, post: 1, look: 'angry' }] });
  const s = Sim.create(L, { viewW: 468, seed: 1, lanes: THUMBS });
  s.p.x = 150; s.p.inv = 1e9;
  let burst = false, sneeze = false, shotsWhile = 0, sneezeT = 0;
  const e = s.enemies[0];
  for (let k = 0; k < 400; k++) {
    Sim.step(s, inp({ viewW: 468, my: k < 30 ? 1 : 0, fire: k === 0 }));            // (one round, crouched)
    for (const ev of s.events) {
      if (ev.t === 'spice_burst') burst = true;
      if (ev.t === 'sneeze' && ev.who === 'man') sneeze = true;
      if (ev.t === 'eshot' && e.st === 'sneeze') shotsWhile++;
    }
    if (e.st === 'sneeze') sneezeT++;
  }
  ok(burst && sneeze, 'one round, crouched, goes into the sack beside him and bursts it; the cloud reaches him and he doubles up sneezing');
  ok(shotsWhile === 0 && sneezeT >= T.SNEEZE_T - 2 && e.alive, 'he does not fire while he sneezes (' + sneezeT + ' ticks of it)');
  // and with his fit over, the cloud thinning, he is a soldier again
  ok(e.st !== 'sneeze' && s.clouds.length === 0, 'the fit passes and the cloud is gone (' + e.st + ')');
}
{
  // a bomber with a lit stick drops it at his feet
  const L = bare({ spawns: [{ g: 'X', k: 'bomber', x: 330, post: 1 }] });
  const s = Sim.create(L, { viewW: 468, seed: 2, lanes: THUMBS });
  s.p.x = 150; s.p.inv = 1e9;
  const e = s.enemies[0];
  let lit = false;
  for (let k = 0; k < 600 && !lit; k++) { Sim.step(s, inp({ viewW: 468 })); if (e.lit) lit = true; }
  I.addCloud(s, e.x, e.y - 20, T.CLOUD_R, 'red', T.CLOUD_LIFE, 0);
  let fumble = false, boomNear = false;
  for (let k = 0; k < 120; k++) {
    Sim.step(s, inp({ viewW: 468 }));
    for (const ev of s.events) { if (ev.t === 'fumble') fumble = true; if (ev.t === 'explode' && Math.abs(ev.x - e.x) < 40) boomNear = true; }
  }
  ok(lit && fumble && boomNear, 'a bomber caught in it with a stick lit drops it at his own feet');
}
{
  // Yazeed in a cloud: he sneezes, slows, and cannot shoot or throw until it is over
  const L = bare({});
  const s = Sim.create(L, { viewW: 468, seed: 3, lanes: THUMBS });
  s.p.x = 200;
  Sim.step(s, inp({ viewW: 468 }));
  I.addCloud(s, 200, s.p.y - 17, T.CLOUD_R, 'red', T.CLOUD_LIFE, 0);
  let shots = 0, gren = 0, sneezed = false, hint = false, firstShot = -1;
  for (let k = 0; k < T.CLOUD_GROW + T.P_SNEEZE + 10; k++) {
    Sim.step(s, inp({ viewW: 468, fire: true, grenade: k % 40 === 0 }));
    for (const ev of s.events) {
      if (ev.t === 'sneeze' && ev.who === 'p') sneezed = true;
      if (ev.t === 'hint' && ev.k === 'sneeze') hint = true;
      if (ev.t === 'shot' && sneezed && s.p.sneezeT > 0) shots++;
      if (ev.t === 'throw' && sneezed && s.p.sneezeT > 0) gren++;
      if (ev.t === 'shot' && sneezed && s.p.sneezeT <= 0 && firstShot < 0) firstShot = k;
    }
  }
  ok(sneezed && hint && shots === 0 && gren === 0, 'Yazeed walks into chilli: he sneezes, a word says so, and while it lasts he cannot shoot or throw');
  ok(firstShot >= 0, '   and when it is over the gun works again');
  ok(s.p.sneezeImm >= 0 && T.P_SNEEZE_IMM > T.P_SNEEZE, '   (and he gets a moment clear of it before the next fit)');
}

// ---- barricades
function barLevel(extra) {
  return bare(Object.assign({ props: [{ k: 'cover', bar: 'b1', x: 1219, x0: 1196, x1: 1290, top: 154, hp: 30, art: 'barr', zone: 0 }] }, extra || {}));
}
function at(L, x, seed) {
  const s = Sim.create(L, { viewW: 468, seed: seed || 4, lanes: THUMBS });
  s.p.x = x; s.cam = Math.max(0, x - 140);
  return s;
}
{
  const s = at(barLevel(), 1100);
  for (let k = 0; k < 200; k++) Sim.step(s, inp({ viewW: 468, mx: 1 }));
  ok(s.p.x <= 1196 - 8 + 0.01, 'walking into a barricade, he stops in front of it (' + s.p.x.toFixed(1) + ')');
  for (let k = 0; k < 60; k++) Sim.step(s, inp({ viewW: 468, mx: 1, jump: k % 20 < 10 }));
  ok(s.p.x <= 1196 - 8 + 0.01, '   nor can he jump it');
  const o = s.bars[0];
  let hits = 0, broke = null;
  for (let k = 0; k < 60 * 20 && !o.gone; k++) {
    Sim.step(s, inp({ viewW: 468, fire: true }));
    hits += events(s, 'bar_hit').length;
    for (const ev of events(s, 'bar_break')) broke = ev;
  }
  ok(o.gone && hits === 30 && broke && broke.pts === 300, 'thirty rounds into it and it comes down (' + hits + ' hits, ' + (broke && broke.pts) + ' points)');
  for (let k = 0; k < 120; k++) Sim.step(s, inp({ viewW: 468, mx: 1 }));
  ok(s.p.x > 1260, '   and then he walks on through (' + s.p.x.toFixed(0) + ')');
}
{
  // a grenade knocks a lump out of it; a drum beside it brings it down at once
  const s = at(barLevel(), 1130);
  let thrown = 0;
  for (let k = 0; k < 200 && thrown < 1; k++) { Sim.step(s, inp({ viewW: 468, grenade: k === 0 })); thrown += events(s, 'throw').length; }
  for (let k = 0; k < 120; k++) Sim.step(s, inp({ viewW: 468 }));
  ok(s.bars[0].hp === 30 - T.BAR_GREN, 'a grenade at it takes ' + T.BAR_GREN + ' (hp ' + s.bars[0].hp + ')');
  const L2 = barLevel();
  L2.props = L2.props.concat([{ k: 'drum', x: 1170, paint: 'oxide', zone: 0 }]);
  const s2 = at(L2, 1060);
  for (let k = 0; k < 200 && !s2.bars[0].gone; k++) Sim.step(s2, inp({ viewW: 468, fire: true }));
  ok(s2.bars[0].gone, 'a drum beside it, shot, takes the whole barricade with it');
}
{
  // a man behind it comes up over it to fire: a man crouched in front is under his shots, a man standing is not
  const L = barLevel({ spawns: [{ g: 'X', k: 'rifle', x: 1254, plat: 'b1back', post: 1, covered: 1, look: 'angry' }] });
  const run = crouch => {
    const s = at(L, 1150);
    let fired = 0, hurt = 0;
    for (let k = 0; k < 600; k++) {
      Sim.step(s, inp({ viewW: 468, my: crouch ? 1 : 0 }));
      for (const ev of s.events) { if (ev.t === 'eshot') fired++; if (ev.t === 'plate_lost') hurt++; }
    }
    return { s, fired, hurt };
  };
  const down = run(true), up = run(false);
  ok(down.s.enemies[0].covered && down.fired > 0 && down.hurt === 0 && up.hurt > 0, 'a man behind it comes up over it to fire: crouched in front of it, his shots go over (' + down.fired + ' shots); standing, they do not');
  // and when it goes he has nothing to hide behind
  I.hitBar(down.s, down.s.bars[0], 99, 1, 'test');
  ok(!down.s.enemies[0].covered, '   once it is down he is out in the open');
  // nor do shots stop at the back of it (the pile is at its front: a man behind it may be shot over it from afar)
  const s3 = at(L, 1150);
  const e = s3.enemies[0];
  let wood = 0, body = 0;
  for (let k = 0; k < 300 && e.alive; k++) {
    Sim.step(s3, inp({ viewW: 468, fire: true }));
    for (const ev of s3.events) { if (ev.t === 'hit' && ev.kind === 'wood') wood++; if (ev.t === 'hit' && ev.kind === 'body') body++; }
  }
  ok(wood > 0, '   his shots from close in front go into the pile (' + wood + '), and a few over it into whoever comes up (' + body + ')');
}
{
  // left to itself the gun works at a barricade close in front (auto-fire), and not at one a long way off
  const s = at(barLevel(), 1100);
  let shots = 0;
  for (let k = 0; k < 120; k++) { Sim.step(s, inp({ viewW: 468, auto: true })); shots += events(s, 'shot').length; }
  const s2 = at(barLevel(), 900);
  let shots2 = 0;
  for (let k = 0; k < 120; k++) { Sim.step(s2, inp({ viewW: 468, auto: true })); shots2 += events(s2, 'shot').length; }
  ok(shots > 5 && shots2 === 0, 'with auto-fire on, standing close to a barricade the gun works at it (' + shots + ' shots), and not from far off (' + shots2 + ')');
}
{
  // pressed against one for a while, not shooting: a word on what to do
  const s = at(barLevel(), 1150);
  let hint = -1;
  for (let k = 0; k < 400 && hint < 0; k++) { Sim.step(s, inp({ viewW: 468, mx: 1 })); if (events(s, 'hint').some(e => e.k === 'bar')) hint = k; }
  ok(hint > T.BAR_PRESS && hint < T.BAR_PRESS + 120, 'stuck against it, after a while a word on grenades and drums (' + hint + ' ticks)');
}
{
  // in the level: the gate in the town gate waits for its barricade, and the men waiting behind it come through when it goes
  const s = Sim.create(ZABID, { viewW: 468, seed: 5, lanes: THUMBS });
  for (const id of ['A', 'A2', 'B', 'W']) { s.groups[id].done = true; s.groups[id].pending.length = 0; s.groups[id].awake = true; }
  for (const e of s.enemies) if (['A', 'A2', 'B', 'W'].indexOf(e.g) >= 0) { e.alive = false; e.hostile = false; e.st = 'gone'; }
  s.p.x = 1100; s.cam = 900; s.p.inv = 1e9;
  for (let k = 0; k < 600; k++) Sim.step(s, inp({ viewW: 468, mx: 1 }));
  const t1 = s.gates.find(g => g.id === 't1');
  ok(!t1.done && !s.groups.W2.awake && s.failsafe === 0 && s.p.x <= 1188.01, 'with every man in the gateway down but the barricade up, the way stays shut (and the failsafe leaves it alone)');
  I.hitBar(s, s.bars.find(o => o.bar === 'b1'), 99, 1, 'test');
  let came = 0;
  for (let k = 0; k < 200; k++) { Sim.step(s, inp({ viewW: 468 })); came = s.enemies.filter(e => e.g === 'W2' && e.alive).length; if (came) break; }
  ok(s.groups.W2.awake && came > 0, 'it comes down, and the men waiting behind it come through (' + came + ')');
}

// ---- the rooftops: walls, ledges, the gaps
{
  const L = bare({});
  // a step up of more than STEP_UP is a wall: walking at the stair down from the roofs' far end from below
  const s = Sim.create(L, { viewW: 468, seed: 6, lanes: THUMBS, zone: 2 });
  s.p.x = 3700; s.p.y = Sim.groundY(L, 3700); s.cam = 3500; s.p.plat = -1; s.p.air = false; s.p.face = -1;
  // (a stair is a run of small steps: it can be walked)
  for (let k = 0; k < 240; k++) Sim.step(s, inp({ viewW: 468, mx: -1 }));
  ok(s.p.y <= 151 && s.p.x < 3640, 'the stair at the end of the roofs is small steps: he walks up it (at ' + s.p.x.toFixed(0) + ', ' + s.p.y.toFixed(0) + ')');
  // into a gap: he drops, and a jump gets him out the far side
  const s2 = Sim.create(L, { viewW: 468, seed: 6, lanes: THUMBS, zone: 2 });
  s2.p.x = 2740; s2.p.y = Sim.groundY(L, 2740); s2.cam = 2600; s2.p.plat = -1;
  let fell = false, hint = false;
  for (let k = 0; k < 90; k++) { Sim.step(s2, inp({ viewW: 468, mx: 1 })); if (s2.p.y > 185) fell = true; if (events(s2, 'hint').some(e => e.k === 'gap')) hint = true; }
  const bottom = s2.p.y;
  ok(fell && hint && s2.p.x > 2762 && s2.p.x < 2798, 'walking off the edge of a roof he drops into the gap (down at ' + bottom.toFixed(0) + '), and a word says to jump them');
  let out = false;
  for (let k = 0; k < 120 && !out; k++) { Sim.step(s2, inp({ viewW: 468, mx: 1, jump: k < 26 })); if (s2.p.x > 2805 && !s2.p.air && s2.p.y < 150) out = true; }
  ok(out, '   one jump, held, and he is out on the next roof');
  ok(s2.p.lives === T.LIVES && s2.stats.plates === 0, '   a gap costs time, not a life');
  // men coming in at the edge never come in down a gap
  const xs = [];
  for (const q of ZABID.pits) for (const x of [q[0] - 5, (q[0] + q[1]) / 2, q[1] + 5]) xs.push([x, I.offPits(ZABID, x, 1), I.offPits(ZABID, x, -1)]);
  ok(xs.every(r => !ZABID.pits.some(q => r[1] > q[0] - 1 && r[1] < q[1] + 1) && !ZABID.pits.some(q => r[2] > q[0] - 1 && r[2] < q[1] + 1)), 'men walking in at the edge are put on a roof, never in a gap');
}

// ---- the shopkeepers: freed by walking up, each with his own thanks, each giving something
{
  const L = bare({ props: [{ k: 'detainee', x: 300, look: 'shop_tea', gives: 'gren', zone: 0 }] });
  const s = Sim.create(L, { viewW: 468, seed: 7, lanes: THUMBS });
  s.p.x = 200;
  let freed = null;
  for (let k = 0; k < 200 && !freed; k++) { Sim.step(s, inp({ viewW: 468, mx: 1 })); for (const ev of s.events) if (ev.t === 'freed') freed = ev; }
  ok(freed && freed.look === 'shop_tea' && s.stats.freed === 1 && s.pickups.some(q => q.k === 'gren'), 'the tea seller, freed, says so in his own voice and hands over grenades');
}

// ---- the Great Scale
const SS = Sim.S, ext = Sim.ext.scale;
function arena(seed) {
  const s = Sim.create(ZABID, { viewW: 468, seed: seed || 3, zone: 3, lanes: THUMBS });
  s.p.inv = 0;
  for (let k = 0; k < 60 * 14 && !(s.boss && s.boss.st === 'idle'); k++) Sim.step(s, inp({ viewW: 468, mx: s.p.x < ZABID.world.CM + 260 ? 1 : 0 }));
  return s;
}
// (no porters, no sneezes, unless a check wants them)
function quiet(s) { s.scale.porterT = -1e9; s.boss.sneezeImm = 1e9; }
function stepFor(s, n, act, until) {
  const got = { ev: {}, plates: 0 };
  for (let k = 0; k < n; k++) {
    Sim.step(s, inp(Object.assign({ viewW: 468 }, act ? act(s, k) : {})));
    for (const ev of s.events) { const key = ev.t + (ev.k ? ':' + ev.k : ''); got.ev[key] = (got.ev[key] || 0) + 1; if (ev.t === 'plate_lost') got.plates++; }
    if (until && until(s, got)) break;
  }
  return got;
}
{
  // before the fight it is only furniture: the sacks and the brass stop a shot and nothing gives
  const s = Sim.create(ZABID, { viewW: 468, seed: 3, zone: 3, lanes: THUMBS });
  s.p.x = ZABID.world.CM + 200; s.cam = s.p.x - 140; s.p.face = 1;
  const g = stepFor(s, 60, (s, k) => ({ fire: k % 10 === 0, my: 1 }), s => s.boss);
  ok(!s.boss && s.scale.sacks.length === SS.SACKS && !g.ev.spice_burst, 'before the fight the scale is only furniture: shots stop in it, no sack bursts (' + JSON.stringify(g.ev) + ')');
}
{
  const s = arena();
  const b = s.boss, sc = s.scale;
  ok(b && b.kind === 'scale' && b.st === 'idle' && b.hp === SS.HP && b.label === 'THE SCALE', 'in the covered market the Weighmaster sits up in his pan of the Great Scale and the fight starts (' + (b ? b.st : 'none') + ')');
  ok(s.camMax === ZABID.gates.find(g => g.id === 'gB').x - 468 * T.HOLD, 'the screen holds in the hall (' + s.camMax + ')');
  const g0 = ext.geo(s);
  ok(sc.sacks.length === SS.SACKS && sc.ang === 1 && g0.gy > g0.by + 24, 'six sacks of spice in one pan outweigh him in the other: his end of the beam is up (' + g0.gy.toFixed(0) + ' / ' + g0.by.toFixed(0) + ')');
  // shoot the sacks: each one bursts, and with three gone he comes down
  quiet(s);
  s.p.x = g0.gx - 90; s.p.face = 1;
  const got = stepFor(s, 60 * 6, (s, k) => ({ fire: k % 12 === 0 }), (s, got) => got.ev.boss_down);
  ok(got.ev.boss_down && sc.sacks.length <= SS.SACKS - 3 && sc.ang <= SS.DOWN, 'shots burst the sacks one by one; three gone and the beam tips, and he comes down (' + sc.sacks.length + ' left, the beam at ' + sc.ang.toFixed(2) + ')');
  ok(s.clouds.length > 0 && got.ev.spice_burst === SS.SACKS - sc.sacks.length, '   each sack goes up in a cloud (' + got.ev.spice_burst + ')');
}
{
  // down at the bottom, he comes up out of his pan to shoot across at chest height: down on your knees and it goes over
  const run = crouch => {
    const s = arena(4), b = s.boss, sc = s.scale;
    quiet(s); sc.sacks.length = 2; b.cd = 999;
    stepFor(s, 120, null, () => sc.ang <= -0.99);
    b.st = 'idle'; b.cd = 1; b.downT = 1;
    const g = ext.geo(s);
    s.p.x = g.bx - 120; s.p.face = 1;
    const got = stepFor(s, 120, () => ({ my: crouch ? 1 : 0 }), (s, got) => got.ev.boss_shot && !s.bullets.some(q => !q.gone && !q.own));
    return got;
  };
  const stand = run(false), down = run(true);
  ok(stand.ev['tell:rise'] && stand.ev.boss_shot && stand.plates === 1, 'down on the floor he stands up in his pan and shoots across: standing, it hits');
  ok(down.ev.boss_shot && down.plates === 0, '   crouched, it goes over');
}
{
  // up high, he aims the blunderbuss down at him: three pellets in a fan
  const s = arena(5), b = s.boss;
  quiet(s); b.cd = 1; b.next = 0;
  s.p.x = ext.geo(s).bx - 140;
  let pellets = 0;
  const got = stepFor(s, 200, null, (s, got) => { pellets = Math.max(pellets, s.bullets.filter(q => !q.gone && q.src === 'weighmaster blunderbuss').length); return got.ev.boss_shot && pellets && !s.bullets.some(q => !q.gone && !q.own); });
  ok(got.ev['tell:aim'] && pellets === 3 && got.plates >= 1, 'up high he aims his blunderbuss at him over the rim, and three pellets come at him in a fan; standing still, he is hit');
}
{
  // on to the spice pan from under its near end, as he stands up in his: the slam
  const hp0 = SS.HP;
  const s2 = arena(6), b2 = s2.boss, sc2 = s2.scale;
  quiet(s2); sc2.sacks.length = 1; b2.cd = 999;
  stepFor(s2, 150, null, () => sc2.ang <= -0.99 && Math.abs(sc2.angV) < 0.05);
  b2.st = 'idle'; b2.downT = 1; b2.cd = 4;
  const gg = ext.geo(s2);
  s2.p.x = gg.gx - 6; s2.p.face = 1;
  let hold = 26, st = [], onPan = false, bonkHp = null;
  const got = stepFor(s2, 60 * 6, () => ({ jump: hold-- > 0, fire: true }), (s, got) => {
    if (st[st.length - 1] !== sc2.man.st) st.push(sc2.man.st);
    if (s.p.plat === sc2.gi) onPan = true;
    if (got.ev.bonk && bonkHp === null) bonkHp = b2.hp;
    return got.ev.plonk;
  });
  ok(got.ev.slam && got.ev.bonk && st.join(',').indexOf('sit,fly,dazed,hop,sit') === 0, 'up on to the spice pan while he is up in his: the beam slams over and throws him out, his head hits the vault, he lies seeing stars, and hops back in (' + st.join(',') + ')');
  ok(bonkHp !== null && bonkHp <= hp0 - SS.BONK && b2.hp < bonkHp, '   the vault takes ' + SS.BONK + ' off him, and shots while he is on the floor take more (' + bonkHp + ', then ' + b2.hp + ')');
  ok(got.ev.buck && !onPan, '   and the pan throws Yazeed off it: nobody stands on a pan on chains');
}
{
  // ducked, he holds on to the chains: on to the pan then, and it only throws Yazeed off
  const s = arena(6), b = s.boss, sc = s.scale;
  quiet(s); sc.sacks.length = 1; b.cd = 999;
  stepFor(s, 150, null, () => sc.ang <= -0.99 && Math.abs(sc.angV) < 0.05);
  b.st = 'idle'; b.downT = 1; b.cd = 999;
  const g = ext.geo(s);
  s.p.x = g.gx - 6; s.p.face = 1;
  let hold = 26;
  const got = stepFor(s, 120, () => ({ jump: hold-- > 0 }), (s, got) => got.ev.buck && !s.p.air);
  ok(got.ev.buck && !got.ev.slam && sc.man.st === 'sit', 'on to the pan while he is ducked down holding on: it only throws Yazeed off');
}
{
  // his porters: in from the right with sacks, up into the pan with them, and he goes back up; a porter shot drops his sack
  const s = arena(7), b = s.boss, sc = s.scale;
  sc.sacks.length = 3; b.sneezeImm = 1e9;
  s.p.x = s.cam + 40;
  const got = stepFor(s, 60 * 20, null, () => sc.sacks.length >= SS.SACKS);
  ok(got.ev.porter && (got.ev.sack_in || 0) >= 3 && sc.sacks.length === SS.SACKS, 'left alone, his porters come in with sacks and put them back in the pan (' + (got.ev.porter || 0) + ' porters, ' + (got.ev.sack_in || 0) + ' sacks in)');
  const s2 = arena(7), sc2 = s2.scale;
  sc2.sacks.length = 3; s2.boss.sneezeImm = 1e9;
  stepFor(s2, 60 * 4, null, () => s2.enemies.some(e => e.porter && e.alive && e.carry));
  const e = s2.enemies.find(e => e.porter && e.alive && e.carry);
  I.hurtEnemy(s2, e, 9, 1, 'shot');
  const c0 = s2.clouds.length;
  stepFor(s2, 2);
  ok(e && !e.alive && s2.clouds.length > c0, '   one shot on the way drops his sack in a cloud');
}
{
  // two thirds: grenades fall out of his pan and the iron weights start coming; stand under one and it hurts
  const s = arena(8), b = s.boss;
  quiet(s);
  ext.hurt(s, SS.HP / 3 + 1);
  const ph = stepFor(s, 90);
  ok(ph.ev['boss_phase:scale'] && b.phase === 2 && s.pickups.some(q => q.k === 'gren'), 'at two thirds he shudders and grenades fall out of his pan');
  b.st = 'idle'; b.cd = 1; b.next = 1;
  s.p.x = ext.geo(s).bx - 150; s.p.inv = 0;
  const still = stepFor(s, 200, null, (s, got) => got.ev.lob && !s.bombs.some(q => !q.gone && q.boom === 'weight'));
  ok(still.ev['tell:heft'] && still.ev.lob && (still.ev['explode:weight'] || 0) + (still.ev.explode || 0) >= 2 && still.plates >= 1, 'then he hefts his iron weights and lobs them: standing still under one, he is hit');
  b.st = 'idle'; b.cd = 1; b.next = 1; s.p.inv = 0;
  let mem = null;
  const moved = stepFor(s, 200, (s) => {
    const w = s.bombs.filter(q => !q.gone && q.boom === 'weight' && q.air);
    if (!w.length) return {};
    if (mem === null) {
      // (where each comes down, from its shadow: walk to the widest clear spot)
      const xs = w.map(q => { const tt = (-q.vy + Math.sqrt(q.vy * q.vy + 2 * q.g * Math.max(0, Sim.groundY(s.L, q.x) - q.y))) / q.g; return q.x + q.vx * tt; });
      let best = s.p.x, bd = -1;
      for (let x = s.cam + 20; x < s.cam + 300; x += 4) { const d = Math.min(...xs.map(v => Math.abs(v - x))); if (d > bd) { bd = d; best = x; } }
      mem = best;
    }
    return { mx: Math.abs(s.p.x - mem) > 3 ? (mem > s.p.x ? 1 : -1) : 0 };
  }, (s, got) => got.ev.lob && !s.bombs.some(q => !q.gone && q.boom === 'weight'));
  ok(moved.ev.lob && moved.plates === 0, '   stepping out from under their shadows, he is not');
}
{
  // one third: a chain of his pan snaps, a heavy MG falls out, and the pan swings about under the beam; under it, it hurts
  const s = arena(9), b = s.boss, sc = s.scale;
  quiet(s);
  ext.hurt(s, SS.HP * 2 / 3 + 1);
  const ph = stepFor(s, 120);
  ok(b.phase === 3 && sc.snap && s.pickups.some(q => q.k === 'hmg'), 'at one third a chain of his pan snaps (a heavy MG falls out of it), and the pan swings');
  ok(ext.exposed(s, ext.geo(s)), '   swinging, he has to hold on where he can be seen: he can be hit all the time');
  s.cam = s.camMax; b.st = 'idle'; b.cd = 999;
  const g = ext.geo(s);
  s.p.x = g.rx; s.p.inv = 0;
  const under = stepFor(s, 200, null, (s, got) => got.plates);
  ok(under.plates >= 1 && s.stats.hurtBy['scale swing'] >= 1, '   and a man standing under it is knocked flat');
}
{
  // the end: the beam breaks, both pans come down, every sack goes up, chillies everywhere; he climbs out and gives up
  const s = arena(10), b = s.boss, sc = s.scale;
  quiet(s);
  ext.hurt(s, SS.HP);
  let dead = false, chillies = 0, surr = 0, caps = 0, clear = false;
  for (let k = 0; k < 60 * 25 && !clear; k++) {
    const w = s.enemies.find(e => e.weigh && e.st === 'surr' && !e.captured);
    const want = w ? (Math.abs(w.x - s.p.x) < 4 ? 0 : (w.x > s.p.x ? 1 : -1)) : (dead && !s.enemies.some(e => e.weigh && !e.captured) ? 1 : 0);
    Sim.step(s, inp({ viewW: 468, mx: want }));
    for (const ev of s.events) {
      if (ev.t === 'boss_dead') { dead = true; chillies = s.pickups.filter(q => q.k === 'chilli').length; }
      if (ev.t === 'surrender' && ev.k === 'weighmaster') surr++;
      if (ev.t === 'capture') caps++;
      if (ev.t === 'clear') clear = true;
    }
  }
  ok(dead && sc.broken && sc.sacks.length === 0 && chillies === SS.CHILLIES, 'the beam breaks, every sack goes up, and chillies rain all over the floor: ' + chillies + ' to pick up');
  ok(surr === 1 && caps === 1, 'the Weighmaster climbs out of the wreck of his pan, gives up, and is walked off');
  ok(clear && s.stats.bossT > 0, 'and with that the mission is clear');
}

// ---- the careful bot gets through, everyone freed, at the narrowest and widest pictures, holding the trigger or not
{
  const res = [];
  for (const vw of [384, 468]) for (const seed of [1, 2, 3]) for (const auto of [false, true]) {
    const o = B.run(B.smartBot({ auto }), { level: ZABID, seed, viewW: vw, continues: 3, seconds: 600, lanes: THUMBS });
    res.push([vw, seed, auto ? 'auto' : 'hold', o.s.status, o.r.freed, Math.round(o.r.time), o.s.failsafe]);
  }
  ok(res.every(r => r[3] === 'clear' && r[4] === 4 && r[6] === 0), 'the careful bot clears it every time, freeing all four, no failsafe: ' + JSON.stringify(res));
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL SOUQ CHECKS OK');
process.exit(fails ? 1 : 0);
