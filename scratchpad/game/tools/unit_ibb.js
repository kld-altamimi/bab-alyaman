// unit_ibb.js - Ibb (level_ibb.js), built zone by zone, checked without a screen: its own sense (every line its screens
// play recorded, every screen standing inside the level, every posted man staged at his fight, the fights in order, the
// way out past the last one), its platforms where the painting has them (gen/stage_ibb.json), every checkpoint starting a
// game, a bot fighting its way through the zones painted so far at both fire settings, and the same seed giving the same
// game. (Its screens are scenery, drawn and voiced by render_ibb.js: nothing in the simulation touches them.)
'use strict';
const path = require('path');
const fs = require('fs');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
require(path.join(__dirname, '../src/fly.js'));
const IBB = require(path.join(__dirname, '../src/level_ibb.js'));
const AUDIO = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/audio.json'), 'utf8'));
const STAGE = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/stage_ibb.json'), 'utf8'));
let fails = 0;
function ok(c, msg) { if (!c) { fails++; console.log('FAIL ' + msg); } }

// ------------------------------------------------------------------ the range
(function level() {
  const L = IBB, lines = AUDIO.speech && AUDIO.speech.ibb ? AUDIO.speech.ibb.lines : {};
  ok(Object.keys(lines).length >= 30, 'the Spokesman\'s lines are in gen/audio.json (' + Object.keys(lines).length + ')');
  ok(L.speech === true && !L.speakers, 'the level asks for his lines, and has no speakers');
  for (const q of L.screens) {
    ok(q.size === 'board' || q.size === 'tv', q.size + ' at ' + q.x + ': a billboard or a set');
    ok(q.x > 60 && q.x < L.endRight - 30, q.size + ' at ' + q.x + ' inside the level');
    ok(q.lines.length > 0, q.size + ' at ' + q.x + ' has lines');
    for (const id of q.lines) ok(!!lines[id], q.size + ' at ' + q.x + ': line ' + id + ' recorded');
    const gy = q.gy != null ? q.gy : Sim.groundY(L, q.x);
    ok(gy >= STAGE.world.VERGE && gy <= 184, q.size + ' at ' + q.x + ' stands on the verge or the road (' + gy + ')');
  }
  // a posted man must stand in the middle of his gate's held screen, outside the lanes the others walk in by, at every
  // width a phone gives (the screen stops at the gate's line halfway across, or at the level's end if that comes first)
  const HOLD = 0.5, LANE_L = 0.18, LANE_R = 0.25;
  for (const sp of L.spawns) {
    if (!sp.post) continue;
    const gate = L.gates.find(g => g.groups.includes(sp.g));
    let inside = !!gate;
    for (const vw of [384, 420, 468]) {
      if (!gate) break;
      const cam = Math.min(gate.x - vw * HOLD, L.endRight - vw);
      if (sp.x < cam + vw * LANE_L || sp.x > cam + vw * (1 - LANE_R)) inside = false;
    }
    ok(inside, 'posted ' + sp.g + ' ' + sp.k + ' at ' + sp.x + ' staged in the middle of his fight\'s screen');
    if (sp.plat) { const pl = L.plats.find(p => p.id === sp.plat); ok(pl && Sim.platY(pl, sp.x) !== null, 'posted ' + sp.g + ' at ' + sp.x + ' on ' + sp.plat); }
  }
  for (const k in L.groups) ok(L.gates.some(g => g.groups.includes(k)), 'group ' + k + ' has a fight');
  for (let i = 1; i < L.gates.length; i++) ok(L.gates[i].x > L.gates[i - 1].x, 'fights in order ' + L.gates[i].id);
  ok(L.exitX > L.gates[L.gates.length - 1].x, 'the way out is past the last fight');
  ok(L.props.filter(q => q.k === 'detainee').length <= 1, 'one to free at most (the teacher comes with zone 2)');
  ok(L.art === 'ibb' && L.endRight <= STAGE.world.END, 'the level ends where the painted road ends (' + STAGE.world.END + ')');
  for (const pl of L.plats) {
    const pp = STAGE.plats[pl.id];
    ok(!!pp && JSON.stringify(pp) === JSON.stringify(pl.pts), 'platform ' + pl.id + ' where the painting has it');
  }
  for (const id in STAGE.plats) ok(L.plats.some(pl => pl.id === id), 'painted top ' + id + ' is a platform');
  for (let z = 0; z < L.zones.length; z++) {
    const s = Sim.create(L, { viewW: 468, zone: z });
    ok(s.status === 'play' && Math.abs(s.p.x - L.zones[z].spawn) < 1, 'zone ' + z + ' (' + L.zones[z].name + ') starts a game');
  }
})();

// ------------------------------------------------------------------ the whole range, by a bot
// (bot.js's player, which fights as it goes: turns to whoever is there, captures whoever gives up, frees whoever is
// tied up; what must always hold is checked on every tick)
const B = require(path.join(__dirname, 'bot.js'));
function walk(seed, auto) { return B.run(B.smartBot({ auto: auto }), { level: IBB, seed: seed, seconds: 360, continues: 9, name: 'ibb ' + seed }); }
(function bot() {
  for (const [seed, auto] of [[7, false], [11, true], [23, false]]) {
    const r = walk(seed, auto), s = r.s;
    ok(s.status === 'clear', 'bot (seed ' + seed + (auto ? ', auto fire' : '') + ') gets to the end of the range (' + s.status + ' after ' + s.time.toFixed(0) + ' s, at x ' + Math.round(s.p.x) + ')');
    ok(!r.evCount.failsafe, 'no fight left to the failsafe (seed ' + seed + ')');
    console.log('bot ' + seed + (auto ? ' auto' : '') + ': ' + s.time.toFixed(1) + ' s, deaths ' + s.stats.deaths + ', continues ' + s.stats.continues +
                '; kills ' + s.stats.kills + ', captures ' + s.stats.captures + ', freed ' + s.stats.freed + '/' + s.stats.detainees);
  }
  const a = walk(7, false), b = walk(7, false);
  ok(B.snap(a.s) === B.snap(b.s), 'the same seed gives the same game');
})();

console.log(fails ? fails + ' FAILED' : 'all Ibb checks pass');
process.exit(fails ? 1 : 0);
