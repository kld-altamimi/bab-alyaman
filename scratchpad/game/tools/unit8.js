// unit8.js - The Souq (build 28; the Tailor, build 30): the level agrees with the painting, every posted man stands
// where he can be fought, the spice sacks and their clouds (a Dhanab who sneezes cannot fight, nor can Yazeed), the
// barricades (they stop him, they wear down, grenades and drums do it faster, the men behind come through when they go,
// auto-fire works at them), the rooftops (walls, drops, the gaps), the shopkeepers, the Tailor's every move, and the
// careful bot gets through.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
require(path.join(__dirname, '../src/tailor.js'));
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
    if (pl.dyn) continue;                       // (a platform that moves is not painted)
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

// ---- every posted man stands inside the middle of his gate's screen at every width (or he would never start a fight)
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
  return Object.assign({}, ZABID, { props: [], gates: [], groups: { X: { zone: 0, trig: 0 } }, spawns: [], tailor: null }, extra || {});
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

// ---- the Tailor
const TL = Sim.TL, X = Sim.ext.tailor;
const CM = ZABID.world.CM;
// walk in to the shop and wait for the fight proper (his hello over and the first shuffle done)
function arena(seed, until) {
  const s = Sim.create(ZABID, { viewW: 468, seed: seed || 3, zone: 3, lanes: THUMBS });
  s.p.inv = 0;
  until = until || (s => s.boss && s.boss.st === 'hunt');
  for (let k = 0; k < 60 * 20 && !until(s); k++) Sim.step(s, inp({ viewW: 468, mx: s.p.x < CM + 280 ? 1 : 0 }));
  return s;
}
function stepFor(s, n, act, until) {
  const got = { ev: {}, plates: 0 };
  for (let k = 0; k < n; k++) {
    Sim.step(s, inp(Object.assign({ viewW: 468 }, act ? act(s, k) : {})));
    for (const ev of s.events) { const key = ev.t + (ev.k ? ':' + ev.k : ''); got.ev[key] = (got.ev[key] || 0) + 1; if (ev.t === 'plate_lost') got.plates++; }
    if (until && until(s, got)) break;
  }
  return got;
}
// a round of Yazeed's at chest height, from just short of a figure, flying right
function shoot(s, x) { s.bullets.push({ x: x - 12, y: X.floorY(s) - TL.STAND_H - 20, vx: 400, vy: 0, life: 60, own: true, age: 5, hide: 0 }); }
const live = s => s.tailor.figs.filter(f => f.st !== 'off');
{
  // before the fight they are only furniture: a shot stops in a figure, nothing gives, nobody is hurt
  const s = Sim.create(ZABID, { viewW: 468, seed: 3, zone: 3, lanes: THUMBS });
  s.p.x = CM + 200; s.cam = s.p.x - 140;
  shoot(s, ZABID.tailor.slots[0]);
  const g = stepFor(s, 20);
  ok(!s.boss && g.ev.hit === 1 && !g.ev.shred && live(s).length === TL.FIGS[1] && live(s).every(f => f.st === 'dressed' || f.st === 'him'),
    'before the fight the figures are only furniture: a shot stops in one and nothing gives (' + JSON.stringify(g.ev) + ')');
  ok(s.props.filter(o => o.k === 'spice' && o.tailor).length === 3, 'three sacks of spice stand along the front of his shop');
}
{
  // the fight: he says hello from his stand (the only one that moves), then they are shuffled
  const s = Sim.create(ZABID, { viewW: 468, seed: 3, zone: 3, lanes: THUMBS });
  let intro = null, show = 0, startSlot = -1, swaps = 0, moved = 0, hunt = false;
  for (let k = 0; k < 60 * 20 && !hunt; k++) {
    const was = s.tailor.figs.map(f => f.x);
    Sim.step(s, inp({ viewW: 468, mx: s.p.x < CM + 280 ? 1 : 0 }));
    for (const ev of s.events) { if (ev.t === 'boss_intro') intro = s.boss; if (ev.t === 'swap') swaps++; }
    if (s.boss && s.boss.st === 'show') { show++; if (startSlot < 0) startSlot = X.real(s).slot; if (s.tailor.figs.some((f, i) => f.x !== was[i])) moved++; }
    if (s.boss && s.boss.st === 'hunt') hunt = true;
  }
  const b = s.boss;
  ok(intro && b.kind === 'tailor' && b.label === 'THE TAILOR' && b.full === TL.HP, 'in the covered market the Tailor shows himself among his dummies and the fight starts');
  ok(startSlot === ZABID.tailor.start && show >= TL.SHOW - 1 && moved === 0, 'he starts on the stand the level says, and nothing moves while he says hello');
  ok(hunt && swaps === TL.SWAPS[1], 'then the stands are swapped about, ' + TL.SWAPS[1] + ' times, two at a time (' + swaps + ')');
  const slots = live(s).map(f => f.slot).sort();
  ok(JSON.stringify(slots) === JSON.stringify([0, 1, 2, 3]) && live(s).every(f => f.x === ZABID.tailor.slots[f.slot]), 'and after it every stand is back in a place, one to a place');
  ok(s.tailor.figs.filter(f => f.real).length === 1 && s.tailor.figs[4].st === 'off', 'one of them is him; the fifth stand waits for later');
}
{
  // he moves in every other swap, so he is never just left standing while the others go round him
  let all = true;
  for (let seed = 1; seed <= 12; seed++) {
    const s = arena(seed, s => s.boss && s.boss.st === 'shuffle');
    const sw = s.tailor.shuffle.swaps;
    let me = X.real(s).slot;
    for (let k = 0; k < sw.length; k++) {
      if (k % 2 === 0 && sw[k][0] !== me) all = false;
      if (sw[k][0] === me) me = sw[k][1]; else if (sw[k][1] === me) me = sw[k][0];
    }
  }
  ok(all, 'every other swap moves him (twelve fights)');
}
{
  // a dummy shot by mistake: its clothes come off and its pins come back at you; shot again it goes over; at the next
  // shuffle it is stood up and dressed again
  const s = arena(4);
  const b = s.boss;
  b.cd = 1e9;
  const me = X.real(s), dum = live(s).filter(f => !f.real).sort((f1, f2) => Math.abs(f1.x - me.x) - Math.abs(f2.x - me.x)).pop();
  s.p.x = dum.x - 70; s.p.y = Sim.groundY(ZABID, s.p.x);
  shoot(s, dum.x);
  const g = stepFor(s, 4);
  const pins = s.bullets.filter(q => !q.gone && q.src === 'dummy pins');
  ok(dum.st === 'bare' && g.ev.shred === 1 && b.hp === TL.HP && pins.length === TL.BACKFIRE_PINS && pins.every(q => q.vx < 0),
    'a dummy shot by mistake: its clothes come off and ' + pins.length + ' pins spring back at whoever shot it');
  s.p.inv = 0;
  const hit = stepFor(s, 90, null, s => !s.bullets.some(q => !q.gone && q.src === 'dummy pins'));
  ok(hit.plates >= 1 && s.stats.hurtBy['dummy pins'] >= 1, '   standing there, they hurt');
  shoot(s, dum.x);
  const g2 = stepFor(s, 4);
  ok(dum.st === 'down' && g2.ev.topple === 1 && !s.bullets.some(q => !q.gone && q.src === 'dummy pins' && q.age < 4), '   shot again, it goes over (no more pins)');
  shoot(s, me.x);
  stepFor(s, 4);
  ok(b.st === 'caught', '   and then a round into him catches him out');
  const g3 = stepFor(s, TL.CAUGHT + 4);
  ok(g3.ev.redress === 1 && dum.st === 'dressed', '   at the next shuffle the dummy is stood up and dressed again');
}
{
  // a shot does not go through a dummy: with one between Yazeed and him, it is the dummy that takes it
  const s = arena(5);
  const b = s.boss, me = X.real(s);
  b.cd = 1e9;
  const before = live(s).filter(f => !f.real && f.x < me.x).sort((f1, f2) => f2.x - f1.x)[0];
  if (before) {
    shoot(s, before.x);
    stepFor(s, 10);
    ok(before.st === 'bare' && b.hp === TL.HP && b.st === 'hunt', 'a shot does not go through a dummy: the one in front of him takes it, and he is untouched');
  } else ok(true, 'a shot does not go through a dummy (he is in front this time; not checked)');
}
{
  // a round into him: caught out, every round counts until the shuffle starts again (or he has taken CATCH_HITS)
  const s = arena(6);
  const b = s.boss, me = X.real(s);
  b.cd = 1e9;
  const hp0 = b.hp;
  shoot(s, me.x);
  const g = stepFor(s, 3);
  ok(b.st === 'caught' && g.ev.caught === 1 && b.hp === hp0 - 1 && X.shown(b), 'a round into him: he is caught out (flapping, out of his pose) and it counts');
  let n = 1;
  for (let k = 0; k < 20 && b.st === 'caught'; k++) { shoot(s, me.x); stepFor(s, 2); n++; }
  ok(hp0 - b.hp === TL.CATCH_HITS && b.st === 'shuffle', 'while he is caught every round counts, up to ' + TL.CATCH_HITS + '; then the shuffle starts again (' + (hp0 - b.hp) + ' taken)');
  const s2 = arena(6);
  s2.boss.cd = 1e9;
  shoot(s2, X.real(s2).x);
  stepFor(s2, 3);
  const g2 = stepFor(s2, TL.CAUGHT + 2);
  ok(g2.ev.shuffle === 1 && s2.boss.hp === TL.HP - 1, '   left alone, he gets back on his stand and they are shuffled again');
}
{
  // his throws: the shears at chest height (get down and they go over); a spray of pins; the tape along the floor (jump
  // it, or be hauled in)
  const throwAt = (seed, kind, act) => {
    const s = arena(seed);
    const b = s.boss, me = X.real(s);
    b.phase = kind === 'scissors' ? 1 : (kind === 'pins' ? 2 : 3); b.next = kind === 'scissors' ? 0 : (kind === 'pins' ? 1 : 2); b.cd = 1; b.sneezeImm = 1e9;
    s.p.x = me.x - 100; s.p.y = Sim.groundY(ZABID, s.p.x); s.p.inv = 0; s.p.face = 1;
    const got = stepFor(s, 160, act, (s, got) => got.ev['tell:tl_' + kind] && b.st === 'hunt' && !s.bullets.some(q => !q.gone && !q.own) && !s.tailor.tape);
    return { s, got };
  };
  const a = throwAt(7, 'scissors', () => ({}));
  ok(a.got.ev['tell:tl_scissors'] && a.got.ev.snip && a.s.stats.hurtBy['tailor scissors'] >= 1, 'he raises his shears (that gives him away) and throws them: standing, Yazeed is hit');
  const a2 = throwAt(7, 'scissors', () => ({ my: 1 }));
  ok(a2.got.ev.snip && !a2.s.stats.hurtBy['tailor scissors'], '   down on his knees, they go over him');
  const p = throwAt(8, 'pins', () => ({}));
  ok(p.got.ev['tell:tl_pins'] && p.got.ev.pins && p.s.stats.hurtBy['tailor pins'] >= 1, 'later a spray of pins, ' + TL.PINS + ' at a time');
  const t = throwAt(9, 'tape', () => ({}));
  ok(t.got.ev['tell:tl_tape'] && t.got.ev.tape && t.got.ev.yank && t.s.stats.hurtBy['tailor tape'] >= 1, 'last of all his tape, run out along the floor: it catches Yazeed and hauls him in');
  const t2 = throwAt(9, 'tape', s => { const tp = s.tailor.tape; return { jump: !!tp && tp.st === 'out' && Math.abs(tp.x0 + tp.dir * tp.len - s.p.x) < 40 }; });
  ok(t2.got.ev.tape && !t2.got.ev.yank && !t2.s.stats.hurtBy['tailor tape'], '   jumped, it goes under him');
}
{
  // dummies don't sneeze: a cloud on a dummy does nothing; a cloud on him and he sneezes, out of his pose
  const s = arena(10);
  const b = s.boss, me = X.real(s), fy = X.floorY(s) - TL.STAND_H;
  b.cd = 1e9;
  const dum = live(s).filter(f => !f.real).sort((f1, f2) => Math.abs(f2.x - me.x) - Math.abs(f1.x - me.x))[0];
  I.addCloud(s, dum.x, fy - 22, 14, 'red', 150, 0);
  const g = stepFor(s, 40);
  ok(!g.ev.sneeze && b.st === 'hunt', 'a cloud of chilli on a dummy: nothing (' + Math.abs(dum.x - me.x) + ' from him)');
  s.clouds.length = 0;
  I.addCloud(s, me.x, fy - 22, 14, 'red', 150, 0);
  const g2 = stepFor(s, 40);
  ok(g2.ev.sneeze && b.st === 'sneeze' && X.shown(b), 'a cloud on him: he sneezes, and it gives him away');
}
{
  // two thirds: a pickup out of the shop and a fifth dummy wheeled in; one third: the sheets over them for the shuffles
  const s = arena(11);
  const b = s.boss;
  b.cd = 1e9;
  X.hurt(s, TL.HP - Math.floor(TL.HP * 2 / 3) - 1);
  shoot(s, X.real(s).x);
  const g = stepFor(s, TL.CAUGHT + 10);
  ok(g.ev['boss_phase:tailor'] && b.phase === 2 && s.pickups.some(q => q.k === 'gren') && g.ev.roll_in === 1, 'at two thirds he is left dazed, grenades come out of the shop and a fifth dummy is wheeled in');
  const g2 = stepFor(s, 60 * 6, null, s => b.st === 'hunt');
  ok(live(s).length === 5 && JSON.stringify(live(s).map(f => f.slot).sort()) === '[0,1,2,3,4]' && g2.ev.swap === TL.SWAPS[2], '   then five are shuffled, ' + TL.SWAPS[2] + ' swaps');
  b.cd = 1e9;
  X.hurt(s, b.hp - Math.floor(TL.HP / 3) + 1);
  shoot(s, X.real(s).x);
  const g3 = stepFor(s, TL.CAUGHT + TL.STUN + TL.COVER_T + 30, null, s => s.tailor.cover >= TL.COVER_T);
  ok(b.phase === 3 && s.pickups.some(q => q.k === 'hmg') && g3.ev.cover === 1 && s.tailor.cover === TL.COVER_T, 'at one third a heavy gun comes out and the sheets go over them for the shuffle');
  shoot(s, live(s)[0].x);
  const g4 = stepFor(s, 6);
  ok(g4.ev.hit === 1 && !g4.ev.shred && !g4.ev.caught, '   under a sheet a shot only stops: nothing gives, whoever it is');
  const g5 = stepFor(s, 60 * 8, null, s => b.st === 'hunt');
  ok(g5.ev.uncover === 1 && s.tailor.cover === 0 && b.st === 'hunt', '   and when the shuffle is done the sheets come off');
}
{
  // never found, he has them shuffled again anyway
  const s = arena(12);
  const b = s.boss;
  b.sneezeImm = 1e9;
  const g = stepFor(s, TL.HUNT_MAX + 400, s => { s.p.inv = 60; return {}; }, (s, got) => got.ev.shuffle);       // (Yazeed not to be hit meanwhile)
  ok(g.ev.shuffle === 1, 'left too long without being found, he has them shuffled again');
}
{
  // a grenade: on him it counts five and catches him out; on a dummy it only knocks it over (no pins)
  const s = arena(13);
  const b = s.boss, me = X.real(s), fy = X.floorY(s);
  b.cd = 1e9;
  const dum = live(s).filter(f => !f.real).sort((f1, f2) => Math.abs(f2.x - me.x) - Math.abs(f1.x - me.x))[0];
  X.blast(s, dum.x, fy - 20, 14, 'gren', true);
  ok(dum.st === 'down' && !s.bullets.some(q => !q.gone && q.src === 'dummy pins') && b.hp === TL.HP, 'a grenade on a dummy knocks it over (no pins come back)');
  X.blast(s, me.x, fy - 20, 14, 'gren', true);
  ok(b.hp === TL.HP - TL.GREN_DMG && b.st === 'caught', 'a grenade on him counts ' + TL.GREN_DMG + ' and catches him out');
}
{
  // the end: his own tape winds round him, the dummies go over (chillies inside), he hops down and gives up
  const s = arena(14);
  const b = s.boss;
  b.cd = 1e9;
  const n = live(s).filter(f => !f.real).length;
  X.hurt(s, b.hp);
  let dead = false, chillies = 0, surr = 0, caps = 0, clear = false, topples = 0;
  for (let k = 0; k < 60 * 25 && !clear; k++) {
    const w = s.enemies.find(e => e.wrapped && e.st === 'surr' && !e.captured);
    const want = w ? (Math.abs(w.x - s.p.x) < 4 ? 0 : (w.x > s.p.x ? 1 : -1)) : (dead && !s.enemies.some(e => e.wrapped && !e.captured) ? 1 : 0);
    Sim.step(s, inp({ viewW: 468, mx: want }));
    for (const ev of s.events) {
      if (ev.t === 'boss_dead') { dead = true; chillies = s.pickups.filter(q => q.k === 'chilli').length; }
      if (ev.t === 'topple' && dead) topples++;
      if (ev.t === 'surrender' && ev.k === 'tailor') surr++;
      if (ev.t === 'capture') caps++;
      if (ev.t === 'clear') clear = true;
    }
  }
  ok(dead && topples === n && chillies === n * TL.CHILLIES && X.real(s).st === 'empty', 'his tape winds round him and every dummy goes over, ' + chillies + ' chillies out of them');
  ok(surr === 1 && caps === 1, 'wound up in his tape he hops down, gives up, and is walked off');
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
