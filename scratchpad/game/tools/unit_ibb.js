// unit_ibb.js - Ibb's speakers and screens (ibb.js) and its test range (level_ibb.js), checked without a screen:
// the range's own sense (every speaker with its group, every line it plays recorded, every posted man staged at his
// fight), the three states of a speaker as the men show them (live: they never give up; taken over: they all give up,
// and nobody else of theirs comes; shot: they fight on, and the last may give up), a screen going (static, the men near
// it flinch, and come out of it), what a shot and a blast do to them, a bot walking the whole range, and the same seed
// giving the same game.
'use strict';
const path = require('path');
const fs = require('fs');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
require(path.join(__dirname, '../src/fly.js'));
require(path.join(__dirname, '../src/ibb.js'));
const IBB = require(path.join(__dirname, '../src/level_ibb.js'));
const AUDIO = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/audio.json'), 'utf8'));
const X = Sim.ext.ibb, I = X.I;
let fails = 0;
function ok(c, msg) { if (!c) { fails++; console.log('FAIL ' + msg); } }
function stepN(s, n, inp) { for (let i = 0; i < n; i++) { Sim.step(s, Object.assign({ mx: 0, my: 0, viewW: 468 }, inp || {})); s.p.inv = Math.max(s.p.inv, 2); } }
function evs(s, n, inp, t) { let k = 0; for (let i = 0; i < n; i++) { Sim.step(s, Object.assign({ mx: 0, my: 0, viewW: 468 }, inp || {})); s.p.inv = Math.max(s.p.inv, 2); k += s.events.filter(e => e.t === t).length; } return k; }
function fresh(L, o) { return Sim.create(L || IBB, Object.assign({ viewW: 468 }, o || {})); }
function men(s, g) { return s.enemies.filter(e => e.g === g && e.alive); }
function wake(s, g) { const G = s.groups[g]; G.awake = true; G.awakeT = 0; }
function variant(edit) { const L = JSON.parse(JSON.stringify(IBB)); edit(L); return L; }

// ------------------------------------------------------------------ the range
(function level() {
  const L = IBB, lines = AUDIO.speech && AUDIO.speech.ibb ? AUDIO.speech.ibb.lines : {};
  ok(Object.keys(lines).length > 30, 'the Spokesman\'s lines are in gen/audio.json (' + Object.keys(lines).length + ')');
  for (const q of L.speakers) {
    ok(!!L.groups[q.g], 'speaker at ' + q.x + ': its group ' + q.g + ' exists');
    ok(L.spawns.some(sp => sp.g === q.g), 'speaker at ' + q.x + ': its group has men');
    for (const id of q.lines) ok(!!lines[id], 'speaker at ' + q.x + ': line ' + id + ' recorded');
    const gate = L.gates.find(g => g.groups.includes(q.g));
    ok(gate && q.x >= gate.x - 133 && q.x <= gate.x + 106, 'speaker at ' + q.x + ' inside its fight\'s held screen');
  }
  for (const q of L.screens) for (const id of q.lines) ok(!!lines[id], q.size + ' at ' + q.x + ': line ' + id + ' recorded');
  for (const sp of L.spawns) {
    if (!sp.post) continue;
    const gate = L.gates.find(g => g.groups.includes(sp.g));
    ok(gate && sp.x >= gate.x - 133 && sp.x <= gate.x + 106, 'posted ' + sp.g + ' ' + sp.k + ' at ' + sp.x + ' staged at his fight');
    if (sp.plat) { const pl = L.plats.find(p => p.id === sp.plat); ok(pl && Sim.platY(pl, sp.x) !== null, 'posted ' + sp.g + ' at ' + sp.x + ' on ' + sp.plat); }
  }
  for (let i = 1; i < L.gates.length; i++) ok(L.gates[i].x > L.gates[i - 1].x, 'gates in order ' + L.gates[i].id);
  ok(L.exitX > L.gates[L.gates.length - 1].x, 'the way out is past the last fight');
  // each checkpoint makes a game with the speakers and screens of its own zone and after
  for (let z = 0; z < L.zones.length; z++) {
    const s = fresh(L, { zone: z });
    ok(s.ibb && s.ibb.spk.length === L.speakers.filter(q => q.zone >= z).length && s.ibb.scr.length === L.screens.filter(q => q.zone >= z).length, 'zone ' + z + ': its speakers and screens');
  }
  // and a level with neither has nothing of Ibb's
  const plain = Sim.create(variant(L => { delete L.speakers; delete L.screens; }), { viewW: 468 });
  ok(plain.ibb === null, 'a level without speakers or screens: no s.ibb');
})();

// ------------------------------------------------------------------ live: they chant, and never give up
(function live() {
  // (a copy where the first speaker's group would always give up its last man, to show the speaker stops it)
  const L = variant(L => { L.groups.A.lastManSurrenders = true; L.spawns = L.spawns.filter(sp => !(sp.g === 'A' && sp.enter)); });
  const s = fresh(L), o = s.ibb.spk[0];
  ok(o.st === 'live' && s.groups.A.noSurr, 'the first speaker plays, and its group does not give up');
  stepN(s, 2);
  const A = men(s, 'A');
  ok(A.length === 3 && A.every(e => X.chanting(s, e) === o && e.deco === 'ibb'), 'its three men chant for it');
  ok(men(s, 'C').every(e => !X.chanting(s, e)), 'men with no speaker do not chant');
  // put all but one down: the last stands his ground
  A.slice(0, 2).forEach(e => Sim._.killEnemy(s, e, 1, 'shot'));
  stepN(s, 30);
  ok(A[2].alive && A[2].hostile && A[2].st !== 'shock' && A[2].st !== 'surr', 'the last man under a playing speaker does not give up (' + A[2].st + ')');
  // shoot the speaker: silence, and now he does
  X.hurtSpeaker(s, o, I.SPK_HP, 'shot');
  ok(o.st === 'dead' && !s.groups.A.noSurr && !X.chanting(s, A[2]), 'shot: the speaker is dead, and he no longer chants');
  stepN(s, 20);
  ok(A[2].st === 'shock' || A[2].st === 'surr', 'with the speaker gone, the last man gives up (' + A[2].st + ')');
})();

// ------------------------------------------------------------------ taken over: they all give up
(function hijack() {
  const s = fresh(), o = s.ibb.spk[0];
  wake(s, 'A');
  stepN(s, 2);
  const before = men(s, 'A').length;
  s.cam = o.x - 250; s.p.x = o.x - 30;
  let n = evs(s, 60, { mx: 1 }, 'spk_hijack');
  ok(o.st === 'hijack' && n === 1, 'walking into the pole takes it over, once (' + o.st + ', ' + n + ' events)');
  ok(s.groups.A.pending.length === 0 && s.groups.A.hijacked, 'nobody else of its group comes');
  stepN(s, 30);
  const A = men(s, 'A');
  ok(A.length >= 1 && A.every(e => e.st === 'surr' && !e.hostile && e.why === 'speaker'), 'every man of its group has given up (' + A.map(e => e.st).join(' ') + ')');
  ok(men(s, 'B').every(e => e.hostile), 'the next speaker\'s men are not affected');
  stepN(s, 60);
  ok(s.groups.A.done, 'its fight is over');
  // a speaker that was taken over can still be shot, and nothing comes of it
  X.hurtSpeaker(s, o, I.SPK_HP, 'shot');
  ok(o.st === 'dead', 'a speaker taken over can still be shot');
  // a speaker already dead cannot be taken over
  const s2 = fresh(), o2 = s2.ibb.spk[0];
  X.hurtSpeaker(s2, o2, I.SPK_HP, 'shot');
  s2.cam = o2.x - 250; s2.p.x = o2.x - 20;
  stepN(s2, 40, { mx: 1 });
  ok(o2.st === 'dead' && men(s2, 'A').every(e => e.hostile), 'walking into a dead speaker does nothing');
  // nor while dead himself, or not on his feet
  const s3 = fresh(), o3 = s3.ibb.spk[0];
  s3.cam = o3.x - 250; s3.p.x = o3.x - 5; s3.p.dead = 30;
  stepN(s3, 2);
  ok(o3.st === 'live', 'no taking over while dead');
})();

// ------------------------------------------------------------------ shots and blasts
(function hits() {
  const s = fresh(), o = s.ibb.spk[0], tv = s.ibb.scr[1];
  // his shot at the men round it passes the pole; one up into its horns hits them; theirs pass
  s.cam = o.x - 200;
  const b0 = { x: o.x - 6, y: o.y - 23, vx: 450, vy: 0, life: 3, own: true };
  s.bullets.push(b0);
  stepN(s, 2);
  ok(o.hp === I.SPK_HP, 'his level shot passes the pole (hp ' + o.hp + ')');
  const b = { x: o.x - 10, y: o.y - 40, vx: 0, vy: -450, life: 40, own: true };
  s.bullets.push(b);
  stepN(s, 4);
  ok(b.gone && o.hp === I.SPK_HP - 1, 'a shot up into its horns hits them (hp ' + o.hp + ')');
  const bd0 = { x: o.x - 40, y: o.y - 37, vx: 318, vy: -318, life: 40, own: true };
  s.bullets.push(bd0);
  stepN(s, 6);
  ok(bd0.gone && o.hp === I.SPK_HP - 2, 'so does one up and along from 40 px off (hp ' + o.hp + ')');
  const e1 = { x: o.x + 18, y: o.y - 62, vx: -172, vy: 0, life: 40, own: false };
  s.bullets.push(e1);
  Sim.step(s, { mx: 0, my: 0, viewW: 468 });
  ok(o.hp === I.SPK_HP - 2, 'their shots pass the horns');
  // a level shot from standing hits a set on its crate; a crouched one goes under it
  s.cam = tv.x - 200;
  const b2 = { x: tv.x0 - 4, y: tv.y - 23, vx: 450, vy: 0, life: 40, own: true }, b3 = { x: tv.x0 - 4, y: tv.y - 11, vx: 450, vy: 0, life: 4, own: true };
  s.bullets.push(b2, b3);
  stepN(s, 2);
  ok(b2.gone && tv.hp === I.TV_HP - 1, 'a standing shot hits the set (hp ' + tv.hp + ')');
  ok(tv.hp === I.TV_HP - 1, 'a crouched shot goes under it');
  // the billboard takes a level shot too
  const bd = s.ibb.scr[0];
  s.cam = 0;
  const b4 = { x: bd.x0 - 4, y: bd.y - 23, vx: 450, vy: 0, life: 40, own: true };
  s.bullets.push(b4);
  stepN(s, 2);
  ok(b4.gone && bd.hp === I.BOARD_HP - 1, 'a standing shot hits the billboard (hp ' + bd.hp + ')');
  // a grenade at the foot of a pole and beside a set
  const s2 = fresh(), o2 = s2.ibb.spk[1], tv2 = s2.ibb.scr[1];
  Sim._.explode(s2, o2.x + 8, o2.y - 4, 30, 'gren', true);
  ok(o2.hp === I.SPK_HP - 3, 'a grenade at the foot of the pole hurts it (hp ' + o2.hp + ')');
  Sim._.explode(s2, tv2.x, tv2.y - 4, 30, 'gren', true);
  ok(tv2.st === 'dead', 'a grenade beside a set puts it out');
})();

// ------------------------------------------------------------------ a screen going: the men near it flinch
(function flinch() {
  const s = fresh(), tv = s.ibb.scr[1];
  stepN(s, 2);
  const near = men(s, 'C'), far = men(s, 'A');
  ok(near.length >= 2, 'the stall\'s set has men by it');
  X.hurtScreen(s, tv, I.TV_HP, 'shot');
  ok(tv.st === 'dead' && !tv.on, 'shot until it goes: static');
  ok(near.every(e => e.st === 'flinch'), 'the men by it flinch (' + near.map(e => e.st).join(' ') + ')');
  ok(far.every(e => e.st !== 'flinch'), 'men far from it do not');
  ok(s.groups.C.awake, 'and their group is awake');
  stepN(s, I.FLINCH_T + 14);
  ok(near.every(e => e.st !== 'flinch'), 'they come out of it (' + near.map(e => e.st).join(' ') + ')');
  // a screen already gone takes no more shots
  const b = { x: tv.x0 - 4, y: tv.y - 23, vx: 450, vy: 0, life: 6, own: true };
  s.cam = tv.x - 200;
  s.bullets.push(b);
  stepN(s, 2);
  ok(tv.st === 'dead', 'a dead set stays dead');
})();

// ------------------------------------------------------------------ the whole range, by a bot
// (bot.js's player, which fights as it goes: turns to whoever is there, captures whoever gives up, frees whoever is
// tied up; what must always hold is checked on every tick. Its gun hits the poles as it fires at the men round them.)
const B = require(path.join(__dirname, 'bot.js'));
function walk(seed, auto) {
  const r = B.run(B.smartBot({ auto: auto }), { level: IBB, seed: seed, seconds: 360, continues: 9, name: 'ibb ' + seed });
  return r;
}
(function bot() {
  for (const [seed, auto] of [[7, false], [11, true], [23, false]]) {
    const r = walk(seed, auto), s = r.s;
    ok(s.status === 'clear', 'bot (seed ' + seed + (auto ? ', auto fire' : '') + ') gets to the end of the range (' + s.status + ' after ' + s.time.toFixed(0) + ' s, at x ' + Math.round(s.p.x) + ')');
    console.log('bot ' + seed + (auto ? ' auto' : '') + ': ' + s.time.toFixed(1) + ' s, deaths ' + s.stats.deaths + ', continues ' + s.stats.continues + '; speakers ' + s.ibb.spk.map(o => o.st).join(' ') + '; screens ' + s.ibb.scr.map(o => o.st).join(' ') +
                '; kills ' + s.stats.kills + ', captures ' + s.stats.captures + ', freed ' + s.stats.freed + '/' + s.stats.detainees + (r.evCount.failsafe ? ', failsafe ' + r.evCount.failsafe : ''));
  }
  // the same seed, the same game
  const a = walk(7, false), b = walk(7, false);
  ok(B.snap(a.s) === B.snap(b.s), 'the same seed gives the same game');
})();

console.log(fails ? fails + ' FAILED' : 'all Ibb checks pass');
process.exit(fails ? 1 : 0);
