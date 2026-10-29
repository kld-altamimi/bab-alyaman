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
require(path.join(__dirname, '../src/school.js'));
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
  ok(L.props.filter(q => q.k === 'detainee').length <= 1, 'one to free at most: the teacher');
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

// ------------------------------------------------------------------ the school's children (school.js)
// Khaled, 29 Oct: the storyboard "All good", the children redrawn. What must always hold: the classrooms stay shut until
// the yard is clear; while any child is out nothing is fired, thrown or cut, and nobody wakes or comes in; nothing touches
// a child (they leave only by running off the screen, home); the first one out stops and waves, once; a freed teacher
// waits for the last of them, then goes after them; the school's gate opens only when every class is out and away.
(function school() {
  const L = IBB, Sc = L.school, B = require(path.join(__dirname, 'bot.js')), X = Sim.ext.school;
  ok(!!Sc && Sc.doors.length === 3 && Sc.doors.reduce((a, d) => a + d.n, 0) === 14, 'three classrooms, fourteen children');
  ok(JSON.stringify(Sc.doors.map(d => d.x)) === JSON.stringify(STAGE.info.z2.school.doors), 'the classroom doors where the painting has them');
  ok(L.gates.some(g => g.id === Sc.gate && g.until === 'school'), 'the school\'s gate waits for its classes');
  for (const [seed, auto] of [[3, false], [8, true], [21, false]]) {
    let s = Sim.create(L, { viewW: 468, seed: seed, zone: 1 });
    const bot = B.smartBot({ auto: auto }), tag = 'seed ' + seed + (auto ? ', auto fire' : '');
    let early = 0, opened = 0, out = 0, stops = 0, calmActs = 0, hushIn = 0, lost = 0, ranEarly = false, doneAt = -1, goAt = -1, maxKids = 0, calmTicks = 0, seq = 0;
    const last = {};
    for (let t = 0; t < 60 * 300 && s.status === 'play'; t++) {
      const inp = bot(s); inp.viewW = 468;
      const calm0 = s.calm, hush0 = s.hush, n0 = s.enemies.length;
      if (calm0) { inp.fire = true; inp.auto = true; inp.grenade = t % 2 === 0; }          // (try everything while they are out)
      Sim.step(s, inp);
      s.p.inv = Math.max(s.p.inv, 2);
      if (calm0) calmTicks++;
      for (const e of s.events) {
        seq++;                                          // (events in the order they happened, within a moment too)
        if (e.t === 'class_open') { opened++; if (!s.school.clear) early++; }
        if (e.t === 'kid_out') out++;
        if (e.t === 'kid_stop') stops++;
        if (calm0 && (e.t === 'shot' || e.t === 'throw' || e.t === 'slash')) calmActs++;
        if (hush0 && (e.t === 'emerge' || e.t === 'behind')) hushIn++;
        if (e.t === 'school_done') doneAt = seq;
        if (e.t === 'go' && e.gate === Sc.gate) goAt = seq;
      }
      if (hush0 && s.enemies.length > n0) hushIn++;
      // every child that has gone has gone home: off the left of the screen
      const now = new Set(s.kids.map(k => k.id));
      for (const id in last) if (!now.has(+id) && last[id] >= s.cam - 20) lost++;
      for (const k in last) delete last[k];
      for (const k of s.kids) last[k.id] = k.x;
      maxKids = Math.max(maxKids, s.kids.length);
      const tch = s.props.find(o => o.k === 'detainee' && Math.abs(o.px - Sc.teacher) < 2);
      if (tch && tch.st === 'run' && !s.school.done) ranEarly = true;
    }
    ok(s.status === 'clear', tag + ': the bot opens the classrooms and gets out of Jibla (' + s.status + ')');
    ok(early === 0 && opened === 3 && out === 14 && s.school.done, tag + ': every classroom opened once the yard was clear (' + opened + '), all ' + out + ' children out');
    ok(stops === 1, tag + ': one child stops by Yazeed to wave (' + stops + ')');
    ok(calmTicks > 0 && calmActs === 0, tag + ': while children were out (' + calmTicks + ' ticks) nothing was fired, thrown or cut, though the bot tried every tick (' + calmActs + ')');
    ok(hushIn === 0, tag + ': nobody woke or came in while the school was being let out (' + hushIn + ')');
    ok(lost === 0, tag + ': every child went home, off the screen; none went any other way (' + lost + ')');
    ok(!ranEarly, tag + ': the teacher went after his pupils only once the last of them was away');
    ok(doneAt >= 0 && goAt > doneAt, tag + ': the school\'s gate opened after the last class was away (event ' + goAt + ', after ' + doneAt + ')');
  }
  // nothing touches them: two games let out the same way by hand; in one of them a grenade and a stick of dynamite go off on
  // every child in the yard and a shot of each side is sent through them. The children do exactly the same in both.
  {
    const mk = () => {
      const s = Sim.create(L, { viewW: 468, seed: 5, zone: 1 });
      for (const g in s.groups) if (['F', 'F2', 'E', 'E2'].indexOf(g) >= 0) { s.groups[g].done = true; s.groups[g].pending.length = 0; }
      s.enemies.length = 0; s.p.x = 1740; s.cam = 1880 - 468 * 0.5;
      for (let t = 0; t < 50; t++) Sim.step(s, { viewW: 468 });
      s.p.inv = 999;
      return s;
    };
    const a = mk(), b = mk();
    ok(a.kids.length >= 2 && a.calm === 1, 'a class let out by hand: ' + a.kids.length + ' children in the yard');
    const ids = a.kids.map(k => k.id);
    for (const k of b.kids) {
      Sim._.explode(b, k.x, k.y - 10, 40, 'gren', true);
      Sim._.explode(b, k.x, k.y - 10, 40, 'dyn', false);
      b.bullets.push({ x: k.x + 30, y: k.y - 12, vx: -172, vy: 0, life: 60, own: false, src: 'test' });
      b.bullets.push({ x: k.x - 30, y: k.y - 12, vx: 450, vy: 0, life: 60, own: true });
    }
    let same = true, moved = 0;
    for (let t = 0; t < 60; t++) {
      Sim.step(a, { viewW: 468 }); Sim.step(b, { viewW: 468 });
      for (const id of ids) {
        const ka = a.kids.find(k => k.id === id), kb = b.kids.find(k => k.id === id);
        if (!ka !== !kb || (ka && (ka.x !== kb.x || ka.st !== kb.st || ka.face !== kb.face))) same = false;
      }
    }
    for (const id of ids) { const k = a.kids.find(q => q.id === id); if (!k || k.st === 'run') moved++; }
    ok(same && moved > 0 && b.kids.every(k => !('hp' in k)) && b.enemies.every(e => b.kids.indexOf(e) < 0) && b.status === 'play',
       'a grenade, dynamite and shots on the children: they do exactly as they would have (nothing in the game has them to hit)');
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
