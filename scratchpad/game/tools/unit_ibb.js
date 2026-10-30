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
require(path.join(__dirname, '../src/rally.js'));
require(path.join(__dirname, '../src/opening.js'));
require(path.join(__dirname, '../src/spokesman.js'));
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
    const gy = q.gy != null ? q.gy : Sim.groundY(L, q.x), g = Sim.groundY(L, q.x);
    ok(gy <= g && gy >= Math.min(STAGE.world.VERGE, g - 24), q.size + ' at ' + q.x + ' stands on the verge, the road or at the back of the path (' + gy + ', ground ' + g + ')');
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
  // the ground as painted: flat through the town, then the terraces' steps, each one a wall Yazeed can hop up
  ok(L.walls === true && L.ground && L.ground.y.length * L.ground.step > L.endRight, 'the ground is the painting\'s, with walls (' + L.ground.y.length + ' samples)');
  let maxStep = 0;
  for (let i = 1; i < L.ground.y.length; i++) maxStep = Math.max(maxStep, L.ground.y[i - 1] - L.ground.y[i]);
  const jumpH = Sim.T.JUMP_V * Sim.T.JUMP_V / (2 * Sim.T.GRAV);
  ok(maxStep > Sim.T.STEP_UP && maxStep < jumpH * 0.4, 'the terraces\' steps are walls, and low enough to hop up (' + maxStep + ' px; a jump is ' + Math.round(jumpH) + ')');
  for (const st of STAGE.info.z3.steps) ok(Sim.groundY(L, st.x) === st.y && Sim.groundY(L, st.x - 4) >= st.y, 'the ground steps up at ' + st.x + ' to ' + st.y + ', where the painting has the wall');
  // the lookout on the pass: its five podiums where the painting has them, all in the one screen at every width
  const A = L.arena, PA = STAGE.info.z4 && STAGE.info.z4.arena;
  ok(!!A && !!PA && A.x0 === PA.x0 && A.x1 === PA.x1 && JSON.stringify(A.podiums) === JSON.stringify(PA.podiums), 'the lookout and its podiums where the painting has them');
  ok(A && A.podiums.length === 5 && A.podiums[4] - A.podiums[0] + 2 * 30 <= 384 && A.podiums.every(x => x > A.x0 + 40 && x < A.x1 - 40),
     'five podiums on the lookout, all in one screen at the narrowest (' + (A ? A.podiums[4] - A.podiums[0] : '?') + ' px apart)');
  ok(L.exitX > A.podiums[4] + 60 && L.exitX <= L.endRight - 30, 'the way out past the last podium (' + L.exitX + ')');
  for (const r of L.remarks || []) ok(!!lines[r.id] && r.x > L.zones[1].x && r.x < L.zones[2].x, 'Yazeed\'s word at ' + r.x + ' (' + r.id + ') recorded, in Jibla');
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
    let early = 0, opened = 0, out = 0, stops = 0, calmActs = 0, hushIn = 0, lost = 0, ranEarly = false, doneAt = -1, goAt = -1, maxKids = 0, calmTicks = 0, seq = 0, hints = 0;
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
        if (hush0 && e.t === 'hint') hints++;                 // (no tip about aiming while his gun is down and the doors are his to open)
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
    ok(hints === 0, tag + ': no tips while the school was being let out (' + hints + ')');
    ok(lost === 0, tag + ': every child went home, off the screen; none went any other way (' + lost + ')');
    ok(!ranEarly, tag + ': the teacher went after his pupils only once the last of them was away');
    ok(doneAt >= 0 && goAt > doneAt, tag + ': the school\'s gate opened after the last class was away (event ' + goAt + ', after ' + doneAt + ')');
  }
  // the yard counts as clear with a man of the next fight awake just off the screen (he stays put), not with one in the picture
  for (const vw of [384, 448, 520]) {
    const s = Sim.create(L, { viewW: vw, seed: 4, zone: 1 });
    for (const g in s.groups) if (['F', 'F2', 'E', 'E2'].indexOf(g) >= 0) { s.groups[g].done = true; s.groups[g].pending.length = 0; }
    s.enemies = s.enemies.filter(e => ['E', 'E2', 'F', 'F2'].indexOf(e.g) < 0);
    s.cam = Math.min(L.gates.find(q => q.id === Sc.gate).x - vw * 0.5, L.endRight - vw); s.p.x = s.cam + 60;
    const g = s.enemies.find(e => e.g === 'G');
    s.groups.G.awake = true;
    g.x = s.cam + vw + 3;
    const off = X.yardClear(s);
    g.x = s.cam + vw - 6;
    const on = X.yardClear(s);
    ok(off && !on, 'screen ' + vw + ': an awake man just off the screen leaves the yard clear (' + off + '), one in the picture does not (' + !on + ')');
  }
  // nothing touches them: two games let out the same way by hand; in one of them a grenade and a stick of dynamite go off on
  // every child in the yard and a shot of each side is sent through them. The children do exactly the same in both.
  {
    const mk = () => {
      const s = Sim.create(L, { viewW: 468, seed: 5, zone: 1 });
      for (const g in s.groups) if (['F', 'F2', 'E', 'E2'].indexOf(g) >= 0) { s.groups[g].done = true; s.groups[g].pending.length = 0; }
      s.enemies.length = 0; s.p.x = Sc.doors[0].x - 14; s.cam = L.gates.find(q => q.id === Sc.gate).x - 468 * 0.5;
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

// ------------------------------------------------------------------ the Spokesman's rally (rally.js)
// Khaled, 29 Oct 21:36: "The story board looks great". What must always hold: he and his audience are in nothing the game
// hits (the audience are not in the simulation at all: render_ibb.js draws them from the level's seats); he stays at his
// podium until the station is cleared and Yazeed comes up to the chairs; then Yazeed's word, the jump, the landing and his
// dash off the stage's far end and out of the picture, each once and in that order; the station's gate opens only once he
// is gone, and the mission can be finished after it.
(function rally() {
  const L = IBB, Lg = L.stage, X = Sim.ext.rally, R = Sim.RALLY, P = STAGE.info.z3.stage, lines = AUDIO.speech.ibb.lines;
  const B = require(path.join(__dirname, 'bot.js'));
  ok(!!X && !!Lg && Lg.gate === 'station' && L.gates.some(g => g.id === Lg.gate && g.until === 'rally'), 'the station\'s gate waits for the rally');
  ok(Lg.x0 === P.x0 && Lg.x1 === P.x1 && Lg.deck === P.deck && Lg.podium === P.podium, 'the stage and its podium where the painting has them');
  ok(Lg.seats.length === 5 && Lg.seats.every(q => P.seats.some(c => c[0] === q[0] && c[1] === q[1])), 'five in the audience, each in a painted chair');
  ok(Lg.lines.length > 0 && Lg.lines.every(id => !!lines[id]), 'his statement recorded (' + Lg.lines.length + ' lines)');
  ok(['yazeed_beret', 'clap_s', 'clap_l'].every(id => !!lines[id]), 'Yazeed\'s word and the claps recorded');
  for (const [seed, auto] of [[2, false], [9, true], [17, false]]) {
    const s = Sim.create(L, { viewW: 468, seed: seed, zone: 2 });
    const bot = B.smartBot({ auto: auto }), tag = 'seed ' + seed + (auto ? ', auto fire' : '');
    const order = [], at = {}, x0 = s.rally.x, y0 = s.rally.y;
    let moved = 0, early = 0, seq = 0, nearAtHeard = null;
    for (let t = 0; t < 60 * 240 && s.status === 'play'; t++) {
      const inp = bot(s); inp.viewW = 468;
      Sim.step(s, inp);
      s.p.inv = Math.max(s.p.inv, 2);
      if ((s.rally.st === 'speech' || s.rally.st === 'heard') && (s.rally.x !== x0 || s.rally.y !== y0)) moved++;
      for (const e of s.events) {
        seq++;
        if (/^rally_/.test(e.t)) { order.push(e.t); at[e.t] = seq; }
        if (e.t === 'rally_heard') { nearAtHeard = s.p.x; if (!X.cleared(s)) early++; }
        if (e.t === 'go' && e.gate === Lg.gate) at.go = seq;
        if (e.t === 'clear') at.clear = seq;
      }
    }
    ok(s.status === 'clear', tag + ': the bot clears the station, sees him off and finishes (' + s.status + ')');
    ok(order.join(',') === 'rally_heard,rally_jump,rally_land,rally_gone', tag + ': Yazeed\'s word, the jump, the landing, his dash, once each and in order (' + order.join(',') + ')');
    ok(early === 0 && nearAtHeard !== null && nearAtHeard >= Lg.x0 - R.REACH, tag + ': Yazeed\'s word only with the station cleared and Yazeed at the chairs (x ' + Math.round(nearAtHeard) + ')');
    ok(moved === 0, tag + ': he stayed at his podium until the jump (' + moved + ')');
    ok(at.go > at.rally_gone && at.clear > at.go, tag + ': the station\'s gate opened once he was gone, and the mission ended after it');
  }
  // nothing touches him: two games at the station by hand, the same, its fight put down; in one of them grenades, dynamite
  // and a shot of each side go off on him, on his podium and on every seat. He does exactly the same in both.
  {
    const mk = () => {
      const s = Sim.create(L, { viewW: 468, seed: 6, zone: 2 });
      for (const g of ['I', 'I2', 'J', 'J2', 'K', 'K2', 'L', 'L2']) { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
      for (const g of s.gates) if (g.id !== 'station') g.done = true;
      s.enemies.length = 0; s.p.x = Lg.x0 - R.REACH - 30; s.p.y = Sim.groundY(L, s.p.x);
      s.cam = Math.min(L.gates.find(q => q.id === Lg.gate).x - 468 * 0.5, L.endRight - 468);
      s.p.inv = 999;
      return s;
    };
    const a = mk(), b = mk();
    const spots = [[Lg.podium + R.BEHIND, Lg.deck - 20], [Lg.podium, Lg.deck - 10]].concat(Lg.seats.map(q => [q[0] + 6, q[1] - 10]));
    for (const [x, y] of spots) {
      Sim._.explode(b, x, y, 40, 'gren', true);
      Sim._.explode(b, x, y, 40, 'dyn', false);
      b.bullets.push({ x: x + 30, y: y, vx: -172, vy: 0, life: 60, own: false, src: 'test' });
      b.bullets.push({ x: x - 30, y: y, vx: 450, vy: 0, life: 60, own: true });
    }
    let same = true, sawSpeech = 0;
    for (let t = 0; t < 400; t++) {
      // (the shots fly for a while, Yazeed standing back; then what is left of them is cleared away in both games, as
      // the station has to be clear before anything happens, and Yazeed walks up to the chairs)
      if (t === 40) { a.bullets.length = 0; b.bullets.length = 0; }
      const inp = { viewW: 468, mx: t > 40 ? 1 : 0 };
      Sim.step(a, inp); Sim.step(b, inp);
      a.p.inv = b.p.inv = 999;
      const ra = a.rally, rb = b.rally;
      if (ra.st === 'speech') sawSpeech++;
      if (ra.st !== rb.st || ra.x !== rb.x || ra.y !== rb.y || ra.t !== rb.t) same = false;
    }
    ok(sawSpeech > 0 && same && a.rally.st === 'gone' && !('hp' in b.rally), 'grenades, dynamite and shots on him, his podium and his audience: he does exactly as he would have, and is gone (' + a.rally.st + ')');
  }
})();

// ------------------------------------------------------------------ the opening (opening.js)
// Khaled, 30 Oct 00:39, "Go ahead and finish the whole level": the mission begins with Salem dropping Yazeed off under the
// billboard. What must always hold: only at the start of a mission (not from a later checkpoint, not on a continue); the
// 4x4's arrival, its stop, Yazeed's jump down, Salem's word, the 4x4 backing off and the stick given back, once each and in
// that order, in a few seconds; until then the stick, the trigger and the grenade do nothing and nothing touches Yazeed;
// then the stick is his.
(function opening() {
  const L = IBB, O = L.opening, X = Sim.ext.opening, lines = AUDIO.speech.ibb.lines;
  ok(!!X && !!O && O.from < -40 && O.stop > 0 && O.stop < L.gates[0].x - 300, 'the opening: the 4x4 from off the left of the picture to well short of the first fight');
  ok(['salem_noise', 'yazeed_quiet'].every(id => !!lines[id]), 'Salem\'s word and Yazeed\'s recorded');
  for (const [z, extra] of [[1, {}], [3, {}], [0, { stats: { deaths: 1, continues: 1 } }]]) {
    const s = Sim.create(L, Object.assign({ viewW: 468, zone: z }, extra));
    ok(!s.open && !s.script && !s.p.hidden, 'no opening ' + (extra.stats ? 'on a continue' : 'from zone ' + z));
  }
  const s = Sim.create(L, { viewW: 468, seed: 4 });
  ok(!!s.open && !!s.script && !!s.p.hidden, 'a new mission begins with the opening');
  const order = [], at = {}, x0 = s.p.x;
  let fired = 0, hurt = 0, strayed = 0, walked = -1, t;
  for (t = 0; t < 60 * 20 && s.status === 'play'; t++) {
    // (every button held and the stick pushed back the whole time)
    const inp = { viewW: 468, mx: at.op_go != null && t > at.op_go + 5 ? 1 : -1, my: t % 30 < 15 ? 1 : 0, fire: true, jump: t % 6 < 3, grenade: t % 10 < 5, auto: t % 2 === 0 };
    const xb = s.p.x, scripted = !!s.script, st = s.open && s.open.st;
    Sim.step(s, inp);
    if (scripted) {
      if (s.bullets.some(b => b.own) || s.bombs.some(b => b.own)) fired++;
      if (st !== 'hop' && st !== 'stop' && Math.abs(s.p.x - xb) > 0.001) strayed++;
    }
    for (const e of s.events) {
      if (/^op_/.test(e.t)) { order.push(e.t); at[e.t] = t; }
      if (e.t === 'life_lost' || e.t === 'plate_lost' || e.t === 'hurt') hurt++;
    }
    if (at.op_go != null && walked < 0 && s.p.x > xb + 0.5) walked = t;
    if (walked >= 0 && t > walked + 30) break;
  }
  ok(order.join(',') === 'op_arrive,op_stop,op_hop,op_salem,op_back,op_go', 'the 4x4 comes, stops, Yazeed jumps down, Salem says it, he backs off, the stick is Yazeed\'s: once each, in order (' + order.join(',') + ')');
  ok(at.op_go != null && at.op_go < 60 * 8, 'the opening is over in a few seconds (' + (at.op_go / 60).toFixed(1) + ' s)');
  ok(fired === 0 && strayed === 0 && hurt === 0, 'while it plays nothing is fired or thrown (' + fired + '), the stick moves nobody (' + strayed + '), and nothing touches Yazeed (' + hurt + ')');
  ok(Math.abs(s.p.x - x0) > 20 && walked >= 0 && walked - at.op_go <= 6, 'then the stick is his: he walks off (' + Math.round(x0) + ' to ' + Math.round(s.p.x) + ')');
  for (t = 0; t < 60 * 6 && !X.done(s); t++) Sim.step(s, { viewW: 468, mx: 1 });
  ok(!s.script && !s.p.hidden && X.done(s) && s.open.st === 'gone', 'and the 4x4 is away out of the picture (' + (s.open && s.open.st) + ')');
})();

// ------------------------------------------------------------------ Brigadier Breaking on Sumara pass (spokesman.js)
// Khaled, 30 Oct 00:39, "Go ahead and finish the whole level", the storyboard as passed. What must always hold, played by
// the bot at both fire settings and checked on every tick: he is hurt only while he is stunned, and a stun takes a fifth of
// him at most; he is stunned only through the microphone he is speaking into; the reveal comes in its order (caught, the
// screens back on him, the cables, the van's door, the three technicians, the rack smashed, the cloud clearing) and the way
// out opens only after it; the technicians are in nothing the game hits. Since 0.16.94 (Khaled, 30 Oct 13:56): his going
// down takes its time and nothing of theirs touches Yazeed from the last shot on; the screens come back on only a while
// after he is caught and once Yazeed walks on, and Yazeed is held there, not moving and firing nothing, to hear him. And by
// hand: shots and blasts on him while he is not stunned leave him exactly as he would have been.
(function spokesman() {
  const L = IBB, A = L.arena, X = Sim.ext.spokesman, SP = Sim.SP, lines = AUDIO.speech.ibb.lines;
  const B = require(path.join(__dirname, 'bot.js'));
  ok(!!X && !!A && L.gates.some(g => g.id === 'van' && g.until === 'spokesman' && g.x > A.van.x0), 'the last gate, at the van, waits for the reveal');
  ok(L.groups.BOSS && L.groups.BOSS.hold && L.groups.BOSS.zone === 3, 'his fight is held for him, on the pass');
  for (const ph of ['1', '2', '3']) ok(A.lines[ph].length > 0 && A.lines[ph].every(q => !!lines[q[0]] && q[1] > 40), 'what he says at the podiums, phase ' + ph + ', recorded');
  ok(A.lines.E.every(id => !!lines[id]), 'what the screens say once he is caught, recorded');
  ok(['spk_what', 'tech_videos', 'tech_cannot', 'uncle_again', 'uncle_me', 'yazeed_finally', 'feedback'].every(id => !!lines[id]), 'his WHAT?, the technicians, the Uncle, Yazeed and the feedback recorded');
  ok(A.van.door[0] > A.podiums[4] + 40 && A.van.roof < A.van.sill && A.van.sill < A.y, 'the van past the last podium, its door above the floor');
  const WANT = ['boss_intro', 'boss_start', 'boss_dying', 'boss_dead', 'spk_rerender', 'spk_cables', 'van_open', 'spk_smash', 'spk_clearing', 'spk_clear'];
  for (const [seed, auto] of [[3, false], [11, true], [21, false]]) {
    const s = Sim.create(L, { viewW: 468, seed: seed, zone: 3 });
    const bot = B.smartBot({ auto: auto }), tag = 'seed ' + seed + (auto ? ', auto fire' : '');
    const order = [], at = {};
    let seq = 0, offHurt = 0, deep = 0, badCut = 0, cuts = 0, techHit = 0, techs = new Set(), lastHp = SP.HP, chips = 0;
    const tk = {}; let afterHits = 0, held = 0, heldMoved = 0, heldFired = 0, heldX = null, settleX = null;
    for (let t = 0; t < 60 * 300 && s.status === 'play'; t++) {
      const b0 = s.boss && s.boss.kind === 'spokesman' ? s.boss : null, st0 = b0 && b0.st, hp0 = b0 ? b0.hp : SP.HP;
      const inp = bot(s); inp.viewW = 468;
      const rv0 = s.spk && s.spk.rv;
      const holding = rv0 && rv0.st === 'rerender', nOwn = s.bullets.filter(q => q.own).length;
      Sim.step(s, inp);
      if (holding && s.spk.rv.st === 'rerender') {
        held++;
        if (heldX === null) heldX = s.p.x; else if (Math.abs(s.p.x - heldX) > 0.01 && !s.p.air) heldMoved++;
        if (s.bullets.filter(q => q.own).length > nOwn) heldFired++;
      }
      const b = s.boss && s.boss.kind === 'spokesman' ? s.boss : null;
      if (b && b.hp < hp0 && st0 !== 'stun') offHurt++;
      if (b && b.hp < SP.HP - SP.SEG * b.cuts) deep++;
      for (const e of s.events) {
        seq++;
        if (WANT.includes(e.t) && (e.k === 'spokesman' || !/^boss_/.test(e.t))) { if (!(e.t in at)) order.push(e.t); at[e.t] = seq; }
        if (e.t === 'spk_cut') { cuts++; if (st0 !== 'speak') badCut++; }
        if (e.t === 'spk_chip' && st0 !== 'speak') badCut++;
        if (e.t === 'tech_out') techs.add(e.n);
        if ((e.t === 'kill' || e.t === 'hit') && e.id != null && s.enemies.some(q => q.id === e.id && q.tech != null)) techHit++;
        if (e.t === 'go' && e.gate === 'van') at.go = seq;
        if (e.t === 'clear') at.clear = seq;
        if (['boss_dying', 'boss_dead', 'spk_rerender', 'spk_cables'].includes(e.t) && (e.k === 'spokesman' || !/^boss_/.test(e.t)) && !(e.t in tk)) tk[e.t] = { t: t, x: s.p.x };
        if (e.t === 'spk_rerender') settleX = s.spk.rv.x0;
        if ((e.t === 'life_lost' || e.t === 'plate_lost') && 'boss_dying' in tk) afterHits++;
      }
      for (const q of s.enemies) if (q.tech != null && (!q.alive || q.hostile)) techHit++;
    }
    const b = s.boss;
    ok(s.status === 'clear', tag + ': the bot beats him, sees the reveal through and gets off the pass (' + s.status + ', at x ' + Math.round(s.p.x) + ')');
    ok(order.join(',') === WANT.join(','), tag + ': the fight and the reveal in order (' + order.join(',') + ')');
    ok(offHurt === 0, tag + ': hurt only while stunned (' + offHurt + ' ticks otherwise)');
    ok(deep === 0, tag + ': a stun takes a fifth of him at most');
    ok(badCut === 0 && cuts >= 5, tag + ': stunned only through the microphone he was speaking into (' + cuts + ' times; ' + badCut + ' otherwise)');
    ok(techs.size === 3 && techHit === 0, tag + ': the three technicians out (' + techs.size + '), in nothing the game hits (' + techHit + ')');
    ok(at.go > at.spk_clear && at.clear > at.go, tag + ': the way out opened once the cloud cleared, and the mission ended after it');
    ok(b && b.st === 'dead' && s.spk.off && s.spk.clear === 1 && X.done(s), tag + ': caught, every screen dark, the plateau showing');
    const fall = tk.boss_dead && tk.boss_dying ? tk.boss_dead.t - tk.boss_dying.t : -1, gap = tk.spk_rerender && tk.boss_dead ? tk.spk_rerender.t - tk.boss_dead.t : -1;
    ok(fall >= 150, tag + ': he takes his time going down (' + (fall / 60).toFixed(1) + ' s from the last shot)');
    ok(afterHits === 0, tag + ': from the last shot on nothing of theirs touches Yazeed (' + afterHits + ')');
    ok(gap >= SP.SETTLE && settleX !== null && (tk.spk_rerender.x >= settleX + SP.WALK - 0.01 || tk.spk_rerender.x >= A.van.door[0] - 40),
       tag + ': the screens come back on a while after he is caught (' + (gap / 60).toFixed(1) + ' s) and once Yazeed has walked on (' + Math.round(settleX) + ' to ' + Math.round(tk.spk_rerender.x) + ')');
    ok(held >= SP.HOLD - 2 && heldMoved === 0 && heldFired === 0 && tk.spk_cables && tk.spk_cables.t - tk.spk_rerender.t >= SP.HOLD,
       tag + ': held there to hear him for ' + (held / 60).toFixed(1) + ' s, not moving (' + heldMoved + ') and firing nothing (' + heldFired + '), then free to go on');
  }
  // by hand: he goes down with Yazeed standing still on the lookout's near side: the screens stay dark as long as Yazeed
  // stands there, and come back on once he walks on
  {
    const s = Sim.create(L, { viewW: 468, seed: 9, zone: 3 });
    for (const g in s.groups) if (g !== 'BOSS') { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
    for (const g of s.gates) if (g.id !== 'arena' && g.id !== 'van') g.done = true;
    s.enemies.length = 0; s.p.x = L.groups.BOSS.trig + 6; s.p.y = Sim.groundY(L, s.p.x); s.cam = A.x0 - 120; s.p.inv = 9999;
    let t = 0;
    for (; t < 60 * 20 && !(s.boss && s.boss.st === 'speak'); t++) { Sim.step(s, { viewW: 468 }); s.p.inv = 9999; }
    const b = s.boss;
    b.st = 'stun'; b.stT = 0; b.cuts = 5; b.floor = 0; X.hurt(s, 99);
    for (t = 0; t < SP.DIE + SP.SETTLE + 300; t++) { Sim.step(s, { viewW: 468 }); s.p.inv = 9999; }
    const stayed = s.spk.rv && s.spk.rv.st === 'wait', x0 = s.spk.rv && s.spk.rv.x0;
    let at = null, sx = null;
    for (t = 0; t < 900 && s.spk.rv.st === 'wait'; t++) { Sim.step(s, { viewW: 468, mx: 1 }); s.p.inv = 9999; }
    if (s.spk.rv.st === 'rerender') { at = s.p.x; sx = s.p.x - s.cam; }
    ok(stayed && at !== null && at - x0 >= SP.WALK && sx >= SP.CLEAR_X && sx <= SP.CLEAR_X + 6,
       'Yazeed standing still after he goes down: the screens stay dark (' + (stayed ? 'they did' : 'they came on') + '); they come back on once he has walked on (' + (at !== null ? Math.round(at - x0) : '?') + ' px) clear of the close-up (at ' + (sx !== null ? Math.round(sx) : '?') + ' px in the picture)');
  }
  // by hand: two games on the lookout, the same; in one of them every kind of shot and blast goes off on him, his podium
  // and the microphones he is not speaking into, whenever he is not stunned. He does exactly the same in both.
  {
    const mk = () => {
      // (the pass's other fights put down; Yazeed on the lookout's near end, his trigger untouched)
      const s = Sim.create(L, { viewW: 468, seed: 5, zone: 3 });
      for (const g in s.groups) if (g !== 'BOSS') { s.groups[g].done = true; s.groups[g].pending.length = 0; s.groups[g].awake = true; }
      for (const g of s.gates) if (g.id !== 'arena' && g.id !== 'van') g.done = true;
      s.enemies.length = 0; s.p.x = A.x0 + 10; s.p.y = Sim.groundY(L, s.p.x); s.cam = A.x0 - 120;
      s.p.inv = 9999;
      return s;
    };
    const a = mk(), b = mk();
    let same = true, tries = 0, sawSt = new Set();
    for (let t = 0; t < 60 * 40; t++) {
      const inp = { viewW: 468, mx: a.p.x < L.groups.BOSS.trig + 6 ? 1 : 0 };
      const bb = b.boss;
      if (bb && bb.kind === 'spokesman' && bb.st !== 'stun' && bb.st !== 'dying' && bb.st !== 'dead' && t % 3 === 0) {
        sawSt.add(bb.st);
        const fy = A.y, spots = [[bb.x, fy - 26], [bb.x - bb.face * 4, fy - 20], [bb.x, bb.y - 10]];
        for (let i = 0; i < 5; i++) if (i !== bb.pod || bb.st !== 'speak') spots.push([X.micX(b, { pod: i, face: bb.face }), fy - 22], [A.podiums[i], fy - 8]);
        for (const [x, y] of spots) {
          if (bb.st === 'speak' && Math.abs(x - X.micX(b, bb)) <= SP.MIC_HW + 1) continue;      // (not his live microphone: that would cut him off)
          X.shot(b, { x: x, y: y, own: true, vx: 450 }); X.shot(b, { x: x, y: y, own: false, vx: -172 });
          if (!(bb.st === 'speak' && Math.abs(x - X.micX(b, bb)) < 30)) { X.blast(b, x, y, 26, 'gren', true); X.blast(b, x, y, 40, 'dyn', false); }
          tries++;
        }
      }
      Sim.step(a, inp); Sim.step(b, inp);
      a.p.inv = b.p.inv = 9999;
      const pa = a.boss, pb = b.boss;
      if (!!pa !== !!pb || (pa && (pa.st !== pb.st || pa.hp !== pb.hp || pa.x !== pb.x || pa.y !== pb.y || pa.pod !== pb.pod))) same = false;
    }
    ok(tries > 100 && same && a.boss && a.boss.hp === SP.HP && ['speak', 'ready', 'leap'].every(q => sawSt.has(q)),
       'shots and blasts on him, his podiums and the microphones he is not speaking into, while he is not stunned: he does exactly as he would have, unhurt (' + tries + ' tries; ' + [...sawSt].join(', ') + ')');
  }
})();

// ------------------------------------------------------------------ the whole range, by a bot
// (bot.js's player, which fights as it goes: turns to whoever is there, captures whoever gives up, frees whoever is
// tied up; what must always hold is checked on every tick)
const B = require(path.join(__dirname, 'bot.js'));
function walk(seed, auto) { return B.run(B.smartBot({ auto: auto }), { level: IBB, seed: seed, seconds: 480, continues: 9, name: 'ibb ' + seed }); }
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
