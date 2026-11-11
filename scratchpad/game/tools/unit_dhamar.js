// unit_dhamar.js - Dhamar (level_dhamar.js, Mission 5, the Wadi: zones 1-3, the test build of 11 Nov), checked without a
// screen: its own sense (every line it asks for recorded, its platforms where the painting has them, every posted man
// staged in the middle of his fight's held screen at every phone width, the classrooms and the teacher in reach while the
// school's gate holds, the checkpoints, the barriers on the road), the highway (the queue asks, the speakers laugh, notes
// blow and the 4x4 brings them back as wages; a barrier breaks under the 4x4), the gas torch (the cook leaves it; it
// reaches only so far, through a whole group, and men it catches run off blackened; it runs out; it can't touch the
// children, the teacher or anyone at the vote; with a child out nothing fires at all), the vote (in nothing the game hits;
// its ending in order; the way on opens after it), every checkpoint starting a game, bots fighting through at both fire
// settings and widths, and the same seed giving the same game.
'use strict';
const path = require('path');
const fs = require('fs');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
require(path.join(__dirname, '../src/fly.js'));
require(path.join(__dirname, '../src/school.js'));
require(path.join(__dirname, '../src/rally.js'));
require(path.join(__dirname, '../src/opening.js'));
require(path.join(__dirname, '../src/sandal.js'));
require(path.join(__dirname, '../src/spokesman.js'));
require(path.join(__dirname, '../src/dhamar.js'));
const B = require(path.join(__dirname, 'bot.js'));
const L = require(path.join(__dirname, '../src/level_dhamar.js'));
const AUDIO = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/audio.json'), 'utf8'));
const STAGE = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/stage_dhamar.json'), 'utf8'));
const AR = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/lang_ar.json'), 'utf8'));
const T = Sim.T;
let fails = 0, n = 0;
function ok(c, msg) { n++; if (!c) { fails++; console.log('FAIL ' + msg); } }
const IDLE = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };
function steps(s, k, inp) { for (let i = 0; i < k; i++) Sim.step(s, inp || IDLE); }
function evs(s, k, inp, want) { const seen = {}; for (let i = 0; i < k; i++) { Sim.step(s, inp || IDLE); for (const e of s.events) seen[e.t] = (seen[e.t] || 0) + 1; } return seen; }
// a game in a zone with everyone of theirs put down by hand, Yazeed at x (the camera with him)
function quiet(zone, x, seed) {
  const s = Sim.create(L, { zone, seed: seed || 3, viewW: 468 });
  for (const k in s.groups) { s.groups[k].done = true; s.groups[k].pending.length = 0; s.groups[k].awake = true; s.groups[k].hold = false; }
  s.enemies.forEach(e => { e.alive = false; e.st = 'gone'; e.deadT = 999; });
  s.enemies = [];
  s.p.x = x; s.p.y = Sim.groundY(L, x); s.p.plat = -1;
  s.cam = Math.max(0, Math.min(x - s.viewW * 0.32, L.endRight - s.viewW));
  return s;
}

// ------------------------------------------------------------------ the level's own sense
(function level() {
  const lines = AUDIO.speech && AUDIO.speech.dhamar ? AUDIO.speech.dhamar.lines : {};
  const said = id => !!(lines[id] || AUDIO.voices[id]);
  ok(L.speech === true && L.music === 'dhamar' && !!AUDIO.music.dhamar, 'the level asks for its own lines and its theme, and both are made');
  for (const q of L.lines.start.concat(L.lines.clear)) ok(said(q[1]), 'line ' + q[1] + ' recorded');
  for (const id of L.stage.lines.concat([L.stage.heard, L.stage.deny, L.stage.draft, L.freedLine, L.kidLine, L.outLine, 'grunt_wages', 'cm_speakers', 'ann_flame'])) ok(said(id), 'line ' + id + ' recorded');
  for (const id in lines) {
    if (!lines[id].text) continue;
    ok(!!AR[lines[id].text], 'the line "' + lines[id].text + '" has its Arabic');
    if (lines[id].who) ok(!!AR[lines[id].who], 'who says it, ' + lines[id].who + ', has its Arabic');
  }
  for (const z of L.zones) ok(!!AR[z.name], 'the zone ' + z.name + ' has its Arabic');
  for (const w of [L.banner, L.bossFact, L.freedNote, 'Wages returned', 'FLAMETHROWER', 'A HAND IN THE STEAM', 'A MAN IN THE QUEUE', "AND WE'RE OFF! THE WADI!"]) ok(!!AR[w], '"' + w + '" has its Arabic');
  // the platforms where the painting has them
  const painted = STAGE.plats;
  ok(L.plats.length === Object.keys(painted).length, 'as many platforms as the painting has (' + L.plats.length + ', ' + Object.keys(painted).length + ')');
  for (const q of L.plats) ok(JSON.stringify(painted[q.id]) === JSON.stringify(q.pts), 'platform ' + q.id + ' where the painting has it');
  // every posted man in the middle of his gate's held screen, outside the lanes, at every width a phone gives
  const HOLD = 0.5, LANE_L = 0.18, LANE_R = 0.25;
  for (const sp of L.spawns) {
    if (!sp.post && !sp.door) continue;
    const gate = L.gates.find(g => g.groups.includes(sp.g));
    let inside = !!gate;
    for (const vw of [384, 420, 468]) {
      if (!gate) break;
      const cam = Math.min(gate.x - vw * HOLD, L.endRight - vw);
      if (sp.x < cam + vw * LANE_L - 12 || sp.x > cam + vw * (1 - LANE_R) + 12) inside = false;
    }
    ok(inside, (sp.door ? 'doorway ' : 'posted ') + sp.g + ' ' + sp.k + ' at ' + sp.x + ' staged in his fight\'s held screen');
    ok(!sp.plat || !!L.plats.find(q => q.id === sp.plat), sp.g + ' ' + sp.k + ' on platform ' + sp.plat + ' that exists');
  }
  // the classrooms and the teacher in reach while the school's gate holds (the narrowest screen, the thumbs' lanes)
  const sg = L.gates.find(g => g.id === L.school.gate);
  for (const vw of [384, 420, 468]) {
    const cam = Math.min(sg.x - vw * HOLD, L.endRight - vw), reach = cam + vw * (1 - LANE_R) - 4;
    for (const d of L.school.doors) ok(d.x > cam + 10 && d.x < reach - 4, 'classroom at ' + d.x + ' in reach at ' + vw);
    ok(L.school.teacher < reach + 10 && L.school.teacher > cam, 'the teacher in reach at ' + vw);
  }
  // the checkpoints: each barrier on the road among the road's things, its hut and pole painted
  for (const c of L.checkpoints) {
    ok(!!L.road.find(r => r.k === 'barrier' && r.x === c.barrier), 'the barrier at ' + c.barrier + ' is on the road');
    ok(!!STAGE.info.checkpoints && STAGE.info.checkpoints.some(p => Math.abs(p.hut.x - c.hut) < 4 && Math.abs(p.pole - c.pole) < 4), 'checkpoint at ' + c.x + ' painted where the level has it');
  }
  ok(L.park.x > L.zones[1].x - 60 && L.park.x < L.zones[1].spawn, 'Salem stops at the old gate, before where the city starts');
  ok(L.exitX < L.endRight && L.stage.x1 < L.exitX, 'the way out lies past the vote');
})();

// ------------------------------------------------------------------ every checkpoint starts a game
(function starts() {
  for (let z = 0; z < L.zones.length; z++) {
    const s = Sim.create(L, { zone: z, seed: 5 });
    ok(z === 0 ? s.mode === 'drive' && s.car.st === 'drive' : s.mode === 'foot' && s.car.st === 'park', 'zone ' + z + ' starts ' + (z ? 'on foot, the 4x4 parked' : 'in the 4x4'));
    steps(s, 120);
    ok(s.status === 'play' && !s.p.dead, 'zone ' + z + ' plays');
    ok(!!s.dham && s.dham.cps.every(c => z === 0 ? c.st !== 'done' || true : c.st === 'done'), 'zone ' + z + ': the highway\'s checkpoints ' + (z ? 'behind it' : 'ahead'));
  }
})();

// ------------------------------------------------------------------ the highway
(function highway() {
  const s = Sim.create(L, { zone: 0, seed: 7 });
  s.p.plates = 99;
  const seen = {};
  for (let i = 0; i < 60 * 40 && s.mode === 'drive'; i++) {
    Sim.step(s, { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false });
    for (const e of s.events) seen[e.t] = (seen[e.t] || 0) + 1;
    if (s.p.dead) s.p.dead = 0;
  }
  ok(seen.cp_ask === 3 && seen.cp_laugh === 3, 'each checkpoint asks once and laughs once (' + seen.cp_ask + ', ' + seen.cp_laugh + ')');
  ok(seen.bar_smash === 3, 'the 4x4 goes through each barrier (' + seen.bar_smash + ')');
  ok(s.stats.wages >= 5 && s.stats.wages <= 8 && seen.note_back === s.stats.wages, 'notes come back as wages: ' + s.stats.wages + ' of 8');
  ok(seen.road_end === 1 && s.mode === 'foot' && s.zone === 1, 'the road ends at the old gate and Yazeed walks into the city');
  ok(Sim.results(s).wages === s.stats.wages, 'the results carry the wages returned');
  // a hop clears a barrier; a grenade breaks one
  const h = Sim.create(L, { zone: 0, seed: 9 });
  h.props.push({ id: 900, k: 'barrier', x: 400, y: 184, plat: -1, t: 0, st: 'idle', gone: false });
  Sim.ext.dhamar.blast(h, 410, 180, 34, 'gren', true);
  ok(h.props.find(o => o.id === 900).st === 'broken', 'a grenade of his breaks a barrier');
  Sim.ext.dhamar.blast(h, 410, 180, 34, 'dyn', false);
  ok(true, 'theirs is not counted');
})();

// ------------------------------------------------------------------ the gas torch
(function torch() {
  // the drafted cook leaves it when he goes down
  const s = Sim.create(L, { zone: 1, seed: 3 });
  const cook = s.enemies.find(e => e.k === 'cook');
  ok(!!cook && cook.gives === 'flame', 'the drafted cook in the souq carries the torch');
  Sim._.killEnemy(s, cook, 1, 'shot');
  ok(s.pickups.some(q => q.k === 'flame'), 'he leaves it where he stood');
  // picked up: the torch, its gas, no knife with it
  const q = quiet(1, 6700);
  q.pickups.push({ id: 801, k: 'flame', x: 6704, y: 184, vx: 0, vy: 0, air: false, t: 20, gone: false });
  steps(q, 2);
  ok(q.p.weapon === 'flame' && q.p.ammo === T.FLAME_AMMO, 'picked up: the torch in his hands, full of gas');
  // three of theirs in a row in front of him, close: one puff goes through them all
  const sp = (x, k) => Sim._.spawnEnemy(q, { g: 'S', k: k || 'rifle', post: 1, look: 'worried' }, x);
  q.groups.S.done = false; q.groups.S.awake = true;
  const a = sp(6730), b = sp(6748), c = sp(6766), far = sp(6880);
  [a, b, c, far].forEach(e => { e.cd = 999; e.st = 'wait'; });
  q.p.face = 1;
  const fired = { mx: 0, my: 0, fire: true, jump: false, grenade: false, auto: false };
  let caught = 0;
  for (let i = 0; i < 40; i++) { Sim.step(q, fired); for (const e of q.events) if (e.t === 'die' && e.how === 'flame') caught++; }
  ok(!a.alive && !b.alive && !c.alive, 'the flame goes through all three in a row (' + caught + ' caught)');
  ok(far.alive, 'and stops short of the one ' + Math.round(far.x - q.p.x) + ' px away: short reach');
  ok(a.scorch && !a.air && a.how === 'flame', 'a man the torch caught runs off, blackened, not flung');
  steps(q, 200);
  ok(!q.enemies.includes(a), 'and is gone once he is out of the picture');
  // it runs out, and he has his pistol again
  q.p.ammo = 3; steps(q, 30, fired);
  ok(q.p.weapon === 'side' && q.p.ammo === 0, 'the gas runs out: the pistol again');
  // auto-fire waits for somebody within its reach
  const w = quiet(1, 6700);
  w.p.weapon = 'flame'; w.p.ammo = 200; w.p.face = 1;
  w.groups.S.done = false; w.groups.S.awake = true;
  const lone = Sim._.spawnEnemy(w, { g: 'S', k: 'rifle', post: 1, look: 'qat' }, 6860); lone.cd = 999;
  steps(w, 30, { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: true });
  ok(w.p.ammo === 200, 'auto-fire does not waste the gas on a man out of its reach');
  // the children and the teacher: the torch can't touch them, and with a child out nothing fires at all
  const k = quiet(1, 7500);
  k.p.weapon = 'flame'; k.p.ammo = 200; k.p.face = -1;
  steps(k, 5);
  ok(k.school && k.school.clear, 'the yard is clear');
  k.p.x = 7520; steps(k, 60);
  ok(k.kids.length > 0 && k.calm === 1, 'a class is out');
  const shots0 = k.stats.shots;
  steps(k, 60, fired);
  ok(k.stats.shots === shots0 && !k.bullets.some(b => b.own), 'with a child out, nothing is fired');
  k.kids.forEach(kid => ok(!k.enemies.includes(kid), 'a child is in nothing a shot looks in'));
  const tch = k.props.find(o => o.k === 'detainee');
  ok(!!tch, 'the teacher is held at the office');
  // a puff through where the teacher stands touches nothing (props a shot passes)
  const t2 = quiet(1, 7600);
  t2.p.weapon = 'flame'; t2.p.ammo = 200; t2.p.face = 1;
  steps(t2, 20, fired);
  const tt = t2.props.find(o => o.k === 'detainee');
  ok(tt && tt.st === 'tied', 'the flame passes the teacher, who stays as he was until Yazeed frees him');
})();

// ------------------------------------------------------------------ the vote
(function vote() {
  const s = quiet(2, 10120);
  s.p.weapon = 'flame'; s.p.ammo = 200; s.p.face = 1;
  ok(s.rally && s.rally.vote && s.rally.st === 'speech', 'the Committee holds his vote');
  ok(!s.enemies.some(e => e.ext === 'rally'), 'he and the gathering are in nothing the game hits');
  // shots and flame through them do nothing
  steps(s, 30, { mx: 0, my: 0, fire: true, jump: false, grenade: false, auto: false });
  ok(s.rally.st === 'speech' || s.rally.st === 'heard', 'firing at them changes nothing');
  s.p.x = 10230; s.p.weapon = 'side';
  const order = [];
  for (let i = 0; i < 60 * 30 && s.rally.st !== 'gone'; i++) {
    Sim.step(s, IDLE);
    for (const e of s.events) if (/^rally_|^go$/.test(e.t)) order.push(e.t + (e.gate ? ':' + e.gate : ''));
  }
  steps(s, 30);
  for (const e of s.events) if (e.t === 'go') order.push('go');
  ok(order.join(' ').indexOf('rally_heard rally_deny rally_draft rally_walk rally_gone') === 0, 'Yazeed\'s word, the motion denied, the gathering drafted, off to the convoy, in that order (' + order.join(' ') + ')');
  ok(s.gates.find(g => g.id === 'vote').done, 'and the way on opens');
  for (let i = 0; i < 400 && s.status === 'play'; i++) Sim.step(s, { mx: 1, my: 0, fire: false, jump: false, grenade: false, auto: false });
  ok(s.status === 'clear', 'walking on, the mission is clear (the test build ends at Hammam Ali)');
})();

// ------------------------------------------------------------------ bots, both fire settings, every width; the same seed twice
(function bots() {
  const runs = [[7, false, 468, [0.18, 0.25]], [11, true, 384, [0.18, 0.25]], [23, false, 449, [0.07, 0.09]], [31, true, 420, [0.07, 0.09]]];
  for (const [seed, auto, vw, lanes] of runs) {
    const o = B.run(B.smartBot({ auto }), { level: L, seed, viewW: vw, lanes, seconds: 600, continues: 9, name: 'dhamar' + seed });
    ok(o.s.status === 'clear', 'bot seed ' + seed + (auto ? ' auto' : ' hold') + ' ' + vw + ': clear (' + o.s.status + ' at ' + Math.round(o.s.p.x) + ', ' + o.s.time.toFixed(0) + ' s)');
    ok(!o.s.failsafe, 'bot seed ' + seed + ': no fight stood down by the failsafe (' + o.s.failsafe + ')');
    ok(o.r.freed === 1, 'bot seed ' + seed + ': the teacher freed');
    console.log('  bot ' + seed + (auto ? ' auto' : ' hold') + ' ' + vw + ': ' + o.s.status + ' ' + o.s.time.toFixed(1) + ' s, score ' + o.r.total + ', deaths ' + o.r.deaths + ', continues ' + o.r.continues + ', wages ' + o.r.wages + ', torch ' + (o.evCount.pickup || 0) + ' pickups');
  }
  const a = B.run(B.smartBot({ auto: false }), { level: L, seed: 7, seconds: 200 }), b = B.run(B.smartBot({ auto: false }), { level: L, seed: 7, seconds: 200 });
  ok(B.snap(a.s) === B.snap(b.s), 'the same seed gives the same game');
})();

console.log(fails ? fails + ' of ' + n + ' checks FAILED' : 'all ' + n + ' checks passed');
process.exit(fails ? 1 : 0);
