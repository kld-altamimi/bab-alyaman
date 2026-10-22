// unit3.js - build 3's mechanics one at a time: the jambiya, the coast road, the battery.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
const LEVEL = require(path.join(__dirname, '../src/level.js'));
LEVEL.ground = require(path.join(__dirname, '../gen/ground.json'));
const T = Sim.T, D = Sim.D, B = Sim.B;
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
const inp = o => Object.assign({}, none, o);
function stepN(s, n, i, each) { const evs = []; for (let k = 0; k < n; k++) { Sim.step(s, typeof i === 'function' ? i(k, s) : i); for (const e of s.events) evs.push(Object.assign({ tick: s.tick }, e)); if (each) each(s, k); } return evs; }
const has = (evs, t, f) => evs.filter(e => e.t === t && (!f || f(e)));

// ------------------------------------------------------------------ the jambiya
function beach(spawns) {
  const L = Object.assign({}, LEVEL, { props: [], gates: [], groups: { X: { zone: 0, trig: 0, noSurrender: true } }, spawns: spawns });
  return Sim.create(L, { viewW: 468, seed: 5 });
}
{
  const s = beach([{ g: 'X', k: 'rifle', x: 200, post: 1 }]);
  s.p.x = 200 - 16; s.enemies[0].cd = 9999;
  const sc0 = s.score;
  const evs = stepN(s, 3, inp({ fire: true }));
  ok(has(evs, 'slash').length === 1 && s.bullets.length === 0, 'FIRE with a man 16 px in front draws the knife instead of shooting');
  ok(!s.enemies[0].alive && s.stats.knifed === 1 && s.score - sc0 === Sim.KIND.rifle.score * 2, 'one cut puts a rifleman down, for double his score (' + (s.score - sc0) + ')');
}
{
  const s = beach([{ g: 'X', k: 'rifle', x: 240, post: 1 }]);
  s.p.x = 200; s.enemies[0].cd = 9999;
  const evs = stepN(s, 3, inp({ fire: true }));
  ok(has(evs, 'slash').length === 0 && has(evs, 'shot').length === 1, 'at 40 px he shoots instead');
}
{
  const s = beach([{ g: 'X', k: 'rifle', x: 185, post: 1 }]);
  s.p.x = 200; s.p.face = 1; s.enemies[0].cd = 9999;
  const evs = stepN(s, 3, inp({ fire: true }));
  ok(has(evs, 'slash').length === 0, 'a man 15 px behind him is not cut');
}
{
  const s = beach([{ g: 'X', k: 'door', x: 200, post: 1 }]);
  s.p.x = 200 - 18; const e = s.enemies[0]; e.cd = 9999; e.bashCd = 9999; e.face = -1;
  let cuts = 0, broke = -1;
  for (let k = 0; k < 140 && broke < 0; k++) {
    Sim.step(s, inp({ fire: true }));
    e.cd = 9999; e.bashCd = 9999; s.p.inv = 5;
    let brokeNow = false;
    for (const ev of s.events) { if (ev.t === 'slash') cuts++; if (ev.t === 'door_break') brokeNow = true; }
    if (brokeNow) broke = cuts;
  }
  ok(broke === 4, 'a door facing him comes apart on the fourth cut (' + broke + ')');
}
{
  const s = beach([{ g: 'X', k: 'rifle', x: 200, post: 1 }, { g: 'X', k: 'rifle', x: 205, post: 1 }]);
  s.p.x = 200 - 16; s.enemies.forEach(e => { e.cd = 9999; });
  const evs = stepN(s, 40, inp({ fire: true }), s => { s.p.inv = 5; });
  const sl = has(evs, 'slash');
  ok(sl.length === 2 && sl[1].tick - sl[0].tick >= T.KNIFE_CD, 'two men at arm\'s length: two cuts, ' + (sl.length === 2 ? sl[1].tick - sl[0].tick : '?') + ' ticks apart');
}
{
  const s = beach([{ g: 'X', k: 'rifle', x: 200, post: 1 }]);
  s.p.x = 200 - 14; s.enemies[0].cd = 9999;
  const evs = stepN(s, 4, inp({ auto: true }));
  ok(has(evs, 'slash').length === 1, 'auto-fire cuts too, when someone is that close');
}

// ------------------------------------------------------------------ the coast road
function road(items, opts) {
  const L = Object.assign({}, LEVEL, { road: items || [] });
  const s = Sim.create(L, Object.assign({ viewW: 468, seed: 9, zone: 3 }, opts || {}));
  s.p.inv = 0;
  return s;
}
{
  const s = road([]);
  ok(s.mode === 'drive' && s.p.weapon === 'hmg', 'the coast road starts in the back of the pickup, on the heavy gun');
  stepN(s, 150, inp({}));
  const cruise = s.car.vx;
  stepN(s, 120, inp({ mx: 1 }));
  const fast = s.car.vx;
  stepN(s, 150, inp({ mx: -1 }));
  const slow = s.car.vx;
  ok(Math.abs(cruise - D.V_CRUISE) < 1 && Math.abs(fast - D.V_FAST) < 1 && Math.abs(slow - D.V_SLOW) < 1, 'the stick is the pedal: ' + slow.toFixed(0) + ' / ' + cruise.toFixed(0) + ' / ' + fast.toFixed(0) + ' px a second');
  const y0 = s.car.y; let top = y0, air = 0, landed = null;
  const evs = stepN(s, 90, (k) => inp({ jump: k < 30 }), (st) => { top = Math.min(top, st.car.y); if (st.car.air) air++; });
  landed = has(evs, 'car_land');
  ok(y0 - top > 45 && y0 - top < 60 && landed.length === 1, 'a held hop rises ' + (y0 - top).toFixed(0) + ' px and lasts ' + (air / 60).toFixed(2) + ' s');
}
{
  const s = road([]);
  stepN(s, 30, inp({}));
  const c = s.car, pl = s.p.plates;
  s.bullets.push({ x: c.x + 70, y: c.y - 20, vx: -T.E_BULLET_V, vy: 0, life: 200, own: false, src: 'test' });
  let evs = stepN(s, 40, inp({}));
  ok(s.p.plates === pl && has(evs, 'hit', e => e.kind === 'metal').length === 1, 'a rifle round rings off the car and costs nothing');
  s.bullets.push({ x: s.car.x + 70, y: s.car.y - 20, vx: -D.HEAVY_V, vy: 0, life: 200, own: false, heavy: true, src: 'test heavy' });
  evs = stepN(s, 40, inp({}));
  ok(s.p.plates === pl - 1, 'a round from their heavy gun costs a plate');
}
{
  const s = road([{ x: 1452 + 380, k: 'men', n: 1 }]);
  s.p.inv = 9999;
  const evs = stepN(s, 300, inp({ mx: 1 }));
  const d = has(evs, 'die', e => e.how === 'ram');
  ok(d.length === 1 && s.stats.ranOver === 1, 'a man on the tarmac is run over (he panics first: ' + has(evs, 'panic').length + ' panic)');
}
{
  const s = road([{ x: 1452 + 420, k: 'truck', mode: 'block', nogun: true }]);
  s.p.inv = 9999;
  const sc0 = s.score;
  let v0 = 0;
  const evs = stepN(s, 300, inp({}), (st) => { if (!v0 && st.trucks.length && st.trucks[0].st === 'ok') v0 = st.car.vx; });
  const f = has(evs, 'flip');
  ok(f.length === 1 && s.stats.flips === 1 && s.score - sc0 >= D.FLIP_PTS, 'driving into their pickup flips it (+' + (s.score - sc0) + ')');
  ok(has(evs, 'truck_dead', e => e.how === 'flip').length === 1, 'and it goes up where it comes down');
}
{
  // land on one: how wide is the window?
  const good = [];
  for (let dist = 90; dist <= 260; dist += 10) {
    const s = road([{ x: 1452 + 600, k: 'truck', mode: 'block', nogun: true }]);
    s.p.inv = 9999;
    let hopped = false;
    const evs = stepN(s, 400, (k, st) => {
      const t = st.trucks[0];
      const go = !hopped && t && t.x - st.car.x <= dist;
      if (go) hopped = true;
      return inp({ jump: go || (hopped && st.car.air && st.car.vy < 0) });
    });
    if (has(evs, 'truck_dead', e => e.how === 'crush').length) good.push(dist);
  }
  ok(good.length >= 3, 'coming down on its roof crushes it: a held hop started ' + (good.length ? good[0] + ' to ' + good[good.length - 1] : 'never') + ' px short of it lands on it');
}
{
  const s = road([{ x: 1452 + 520, k: 'men', n: 7, gap: 16 }]);
  s.p.inv = 9999;
  const sc0 = s.score;
  const evs = stepN(s, 500, inp({ mx: 1 }));
  ok(has(evs, 'strike').length === 1, 'six men run over in quick succession is a strike (' + s.stats.ranOver + ' run over, +' + (s.score - sc0) + ')');
}
{
  const s = road([{ x: 1452 + 400, k: 'rmine' }]);
  const pl = s.p.plates;
  const evs = stepN(s, 300, inp({}));
  ok(has(evs, 'explode', e => e.kind === 'mine').length === 1 && s.p.plates === pl - 1, 'a road mine under a wheel costs a plate');
  const s2 = road([{ x: 1452 + 400, k: 'rmine' }]);
  let hopped = false;
  const evs2 = stepN(s2, 300, (k, st) => {
    const m = st.props.find(o => o.k === 'rmine');
    const go = !hopped && m && m.x - (st.car.x + D.WHEEL) < 30;
    if (go) hopped = true;
    return inp({ jump: go || (hopped && st.car.air && st.car.vy < 0) });
  });
  ok(has(evs2, 'explode', e => e.kind === 'mine').length === 0 && s2.p.plates === pl, 'hopped over, it stays where it is');
}
{
  const s = road([{ x: 1452 + 520, k: 'truck', mode: 'block', nogun: true }]);
  s.p.inv = 9999;
  const evs = stepN(s, 200, (k) => inp({ grenade: k === 60 }));
  const thr = has(evs, 'throw'), bx = has(evs, 'explode', e => e.kind === 'gren');
  ok(thr.length === 1 && bx.length === 1 && bx[0].tick - thr[0].tick < 40, 'a grenade from the car goes flat and bursts where it lands, ' + (bx.length ? ((bx[0].tick - thr[0].tick) / 60).toFixed(2) : '?') + ' s after the throw');
}
{
  const s = road([]);
  s.car.x = LEVEL.park.x - 600; s.cam = s.car.x - 468 * D.CAM;
  let wpn = null;
  const evs = stepN(s, 600, inp({ mx: 1 }), (st) => { if (wpn === null && st.events.some(e => e.t === 'dismount')) wpn = st.p.weapon; });
  const end = has(evs, 'road_end'), off = has(evs, 'dismount');
  ok(end.length === 1 && off.length === 1 && s.mode === 'foot' && Math.abs(s.car.x - LEVEL.park.x) < 3, 'at the barrier Salem stops (' + (s.car.x - LEVEL.park.x).toFixed(1) + ' px from the mark) and Yazeed gets down');
  ok(wpn === 'side', 'and he has his own gun back');
}
{
  // the pickup comes for him at the end of the beach
  const s = Sim.create(LEVEL, { viewW: 468, seed: 2, zone: 2 });
  ['C', 'C2', 'C3'].forEach(g => { s.groups[g].done = true; });
  s.enemies.length = 0; s.p.x = 1300; s.cam = 1080;
  const evs = stepN(s, 600, (k, st) => inp({ mx: st.car.st === 'wait' || k > 40 ? 1 : 0 }));
  ok(has(evs, 'horn', e => e.k === 'shass').length === 1 && has(evs, 'car_wait').length === 1, 'with the beach clear Salem drives up, hooting, and waits');
  ok(has(evs, 'mount').length === 1 && s.mode === 'drive', 'walking up to the pickup puts Yazeed in the back');
}

// ------------------------------------------------------------------ the battery
function battery(seed) {
  const s = Sim.create(LEVEL, { viewW: 468, seed: seed || 4, zone: 4 });
  s.p.inv = 0;
  return s;
}
function toFight(s) {
  return stepN(s, 600, (k, st) => inp({ mx: st.boss ? 0 : 1 }), (st) => { st.p.inv = Math.max(st.p.inv, 2); });
}
{
  const s = battery();
  const evs = toFight(s);
  ok(has(evs, 'boss_intro').length === 1 && s.boss && s.cmdr && !s.cmdr.hostile, 'past the dish the boat comes up out of the sea, and the Commander takes his tower');
  const g = s.gates.find(g => g.id === 'gB');
  ok(g && !g.done && s.cam <= g.x - 468 * T.HOLD + 1, 'the screen stops at the fight');
  const hp0 = s.boss.hp;
  stepN(s, 200, inp({ my: -1, fire: true }), (st) => { st.p.inv = 5; });
  ok(s.boss.hp < hp0, 'shots up at it hurt it (' + (hp0 - s.boss.hp) + ' hits in 3.3 s)');
}
{
  const s = battery(6);
  toFight(s);
  stepN(s, 140, inp({}), st => { st.p.inv = 5; });
  const hb = Sim.ext.boss;
  hb.hurt(s, Math.ceil(B.HP / 3) + 1);
  let evs = stepN(s, 4, inp({}), st => { st.p.inv = 5; });
  ok(s.boss.phase === 2 && has(evs, 'boss_phase').length === 1 && s.pickups.some(q => q.k === 'gren'), 'a third of the way down, a rotor goes and grenades fall off it');
  stepN(s, 80, inp({}), st => { st.p.inv = 5; });
  hb.hurt(s, Math.ceil(B.HP / 3) + 1);
  evs = stepN(s, 4, inp({}), st => { st.p.inv = 5; });
  ok(s.boss.phase === 3 && s.pickups.some(q => q.k === 'hmg'), 'two thirds down, another, and a heavy MG');
  stepN(s, 80, inp({}), st => { st.p.inv = 5; });
  const sc0 = s.score;
  hb.hurt(s, s.boss.hp);
  evs = stepN(s, 400, inp({}), st => { st.p.inv = 5; });
  ok(s.boss.st === 'dead' && s.site.launcher === 'wreck' && s.score - sc0 >= B.PTS, 'at nothing it comes down on its own launcher (+' + (s.score - sc0) + ')');
  ok(s.gates.find(g => g.id === 'gB').done, 'and the screen opens');
  ok(has(evs, 'surrender').length === 1 && s.cmdr.st === 'surr', 'the Commander is thrown off his tower and puts his hands up');
  const sc1 = s.score;
  evs = stepN(s, 600, (k, st) => inp({ mx: st.cmdr.captured ? 0 : (st.cmdr.x > st.p.x ? 1 : -1) }), st => { st.p.inv = 5; });
  ok(s.cmdr.captured && s.score - sc1 >= B.CMDR_PTS, 'walking into him takes him in (+' + (s.score - sc1) + ')');
}
{
  // the low pass: standing in its way costs a plate, crouching under it does not
  const res = {};
  for (const crouch of [false, true]) {
    const s = battery(8);
    toFight(s);
    stepN(s, 140, inp({}), st => { st.p.inv = 5; });
    const b = s.boss;
    b.phase = 3; b.hp = Math.floor(B.HP / 3) - 1; b.next = 0; b.cd = 1; b.st = 'idle';
    s.p.inv = 0; s.bombs.length = 0; s.bullets.length = 0;
    const pl = s.p.plates;
    let passed = false;
    stepN(s, 200, inp({ my: crouch ? 1 : 0 }), st => { if (st.boss.st === 'swoop' && Math.abs(st.boss.x - st.p.x) < 10) passed = true; if (st.boss.st !== 'swoop' && st.boss.st !== 'swooptell') st.p.inv = 5; });
    res[crouch ? 'down' : 'up'] = { passed: passed, lost: pl - s.p.plates };
  }
  ok(res.up.passed && res.up.lost === 1, 'standing in its low pass costs a plate');
  ok(res.down.passed && res.down.lost === 0, 'crouching, it goes over him');
}
{
  // its bombs burst where they land
  const s = battery(10);
  toFight(s);
  stepN(s, 140, inp({}), st => { st.p.inv = 5; });
  const b = s.boss;
  b.next = 0; b.cd = 1; b.st = 'idle';
  s.bombs.length = 0;                     // (its first run, before this one, may still have one in the air)
  const evs = stepN(s, 240, inp({}), st => { st.p.inv = 5; });
  const drops = has(evs, 'bomb_drop'), booms = has(evs, 'explode', e => e.kind === 'bbomb');
  ok(drops.length >= 3 && booms.length === drops.length, 'a bombing run drops ' + drops.length + ' bombs and each bursts where it lands');
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL BUILD 3 MECHANICS OK');
process.exit(fails ? 1 : 0);
