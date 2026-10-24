// unit_ibb.js - Ibb's test range (level_ibb.js), checked without a screen: its own sense (every line its screens play
// recorded, every screen on the ground inside the level, every posted man staged at his fight, the fights in order, the
// way out past the last one), every checkpoint starting a game, a bot fighting its way through the whole range at both
// fire settings, and the same seed giving the same game. (Its screens are scenery, drawn and voiced by render_ibb.js:
// nothing in the simulation touches them, and nothing breaks them.)
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
    ok(Math.abs(Sim.groundY(L, q.x) - 184) < 0.01, q.size + ' at ' + q.x + ' stands on the quay\'s floor');
  }
  for (const sp of L.spawns) {
    if (!sp.post) continue;
    const gate = L.gates.find(g => g.groups.includes(sp.g));
    ok(gate && sp.x >= gate.x - 133 && sp.x <= gate.x + 106, 'posted ' + sp.g + ' ' + sp.k + ' at ' + sp.x + ' staged at his fight');
    if (sp.plat) { const pl = L.plats.find(p => p.id === sp.plat); ok(pl && Sim.platY(pl, sp.x) !== null, 'posted ' + sp.g + ' at ' + sp.x + ' on ' + sp.plat); }
  }
  for (const k in L.groups) ok(L.gates.some(g => g.groups.includes(k)), 'group ' + k + ' has a fight');
  for (let i = 1; i < L.gates.length; i++) ok(L.gates[i].x > L.gates[i - 1].x, 'fights in order ' + L.gates[i].id);
  ok(L.exitX > L.gates[L.gates.length - 1].x, 'the way out is past the last fight');
  ok(L.props.filter(q => q.k === 'detainee').length === 1, 'somebody to free');
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
