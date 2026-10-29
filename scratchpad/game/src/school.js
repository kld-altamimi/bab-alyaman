// school.js - Ibb's school (zone 2, Jibla), as the storyboard Khaled passed on 29 Oct ("All good"; the children redrawn
// in the cast's style): three classrooms, padlocked. Once the yard is clear (the school's fight over, and nothing of theirs
// left burning, flying or on its way), Yazeed walks up to a door and it opens, and the class runs out for home: to the
// left, off the screen. While any child is out his gun points at the ground and nothing can be fired, thrown or cut
// (s.calm); from the moment the yard is clear until every class is out and away, nobody new comes in (s.hush); and the
// children are in nothing the game hits: no box, no list that a shot, a blast or a man looks in. Nothing can touch them.
// The first child out stops by Yazeed and waves, and he says "Go home. Tell your mother." With every class out and away,
// the teacher (freed at his flagpole, he waits there for them) goes after his pupils, and the school's gate opens (the
// level's gate with `until: 'school'`).
// The level says where: L.school = { gate, doors: [{ x, n }], teacher: x of the detainee at the flagpole, y: the yard }.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var DT = Sim.DT, I = Sim._, ev = I.ev;
  var S = Sim.SCHOOL = {
    REACH: 16,          // how near a shut door he has to come for it to open
    FIRST: 10,          // the first child is out this long after the door opens; then one every OUT ticks
    OUT: 12,
    RUN: 84,            // how fast they run for home, px a second (each a little faster or slower)
    STOP: 18,           // the first child stops this far past Yazeed, on his way home, and turns to wave
    WAVE: 140,          // how long he stays, while Yazeed has his say
    NAMES: ['boy1', 'girl1', 'boy2', 'girl2']
  };

  function create(s) {
    var Sc = s.L.school;
    s.kids = [];
    s.calm = 0; s.hush = false;
    s.school = Sc ? { doors: Sc.doors.map(function (d) { return { x: d.x, n: d.n, open: false, out: 0, t: 0 }; }), clear: false, stopped: false, done: false, kidN: 0 } : null;
    if (s.school && gateOf(s) && gateOf(s).done) s.school.done = true;       // (a game started past it)
  }
  function done(s) { return !s.school || s.school.done; }
  function gateOf(s) {
    for (var i = 0; i < s.gates.length; i++) if (s.gates[i].id === s.L.school.gate) return s.gates[i];
    return null;
  }
  // the yard is clear: the school's fight is over, nobody of theirs is awake on the screen (one further up the street,
  // off it, stays where he is while the school is let out: sim.js holds him), and nothing is burning, flying or on its way
  function yardClear(s) {
    var gt = gateOf(s), i;
    if (!gt) return false;
    for (i = 0; i < gt.groups.length; i++) if (!s.groups[gt.groups[i]].done) return false;
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i], G = s.groups[e.g];
      if (e.alive && e.hostile && (!G || G.awake) && Sim.onScreen(s, e.x, 20)) return false;
    }
    for (i = 0; i < s.bombs.length; i++) if (!s.bombs[i].gone) return false;
    for (i = 0; i < s.bullets.length; i++) if (!s.bullets[i].gone && !s.bullets[i].own) return false;
    return true;
  }
  // the doors he can open now (the yard clear, the door still shut)
  function waiting(s) {
    var sc = s.school;
    if (!sc || sc.done || !sc.clear) return [];
    return sc.doors.filter(function (d) { return !d.open; });
  }

  function addKid(s, d) {
    var sc = s.school, n = sc.kidN++;
    var k = { id: s.nextId++, x: d.x + (n % 2 ? 3 : -3), y: s.L.school.y, name: S.NAMES[(n + Math.floor(n / 4)) % 4],
              vx: -S.RUN * (0.88 + 0.24 * s.rand()), walkD: n * 3, st: 'run', t: 0, face: -1, gone: false };
    if (!sc.stopped) { sc.stopped = true; k.stopper = true; }
    s.kids.push(k);
    ev(s, { t: 'kid_out', x: k.x, y: k.y });
  }
  function stepKid(s, k) {
    var p = s.p;
    k.t++;
    if (k.st === 'run') {
      // (the first one out stops a little way past Yazeed, on his way home, turns and waves)
      if (k.stopper && !k.waved && k.x <= p.x - S.STOP) { k.st = 'wave'; k.t = 0; k.waved = true; k.face = 1; ev(s, { t: 'kid_stop', x: k.x, y: k.y }); }
      else { k.x += k.vx * DT; k.walkD += Math.abs(k.vx) * DT; k.face = -1; }
    } else if (k.st === 'wave' && k.t > S.WAVE) { k.st = 'run'; k.t = 0; }
    if (k.x < s.cam - 24) k.gone = true;          // home
  }
  // the teacher: freed, he waits at his flagpole until the last of his pupils is away, then goes after them
  function teacher(s, sc) {
    for (var i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.k !== 'detainee' || o.gone || Math.abs(o.px - s.L.school.teacher) > 2) continue;
      if (o.st === 'freed' && !sc.done && o.t > 70) o.t = 70;
    }
  }

  function step(s) {
    var sc = s.school, p = s.p, i;
    if (!sc) return;
    if (sc.done) { s.calm = 0; s.hush = false; return; }
    // (looked at every moment: a man woken further up the street and come into view shuts the doors again until he is dealt with)
    var was = sc.clear, opened = false;
    sc.clear = yardClear(s);
    if (sc.clear && !was) ev(s, { t: 'yard_clear' });
    for (i = 0; i < sc.doors.length; i++) if (sc.doors[i].open) opened = true;
    s.hush = sc.clear || opened;
    // a door opens when he comes up to it
    if (sc.clear && !p.dead && !p.air && Math.abs(p.y - s.L.school.y) < 8) {          // (in the yard, not up on the walkway)
      for (i = 0; i < sc.doors.length; i++) {
        var d = sc.doors[i];
        if (!d.open && Math.abs(p.x - d.x) < S.REACH) { d.open = true; d.t = 0; ev(s, { t: 'class_open', x: d.x, i: i }); }
      }
    }
    // the classes come out, one child at a time
    for (i = 0; i < sc.doors.length; i++) {
      var dd = sc.doors[i];
      if (!dd.open) continue;
      dd.t++;
      if (dd.out < dd.n && dd.t >= S.FIRST + dd.out * S.OUT) { addKid(s, dd); dd.out++; }
    }
    for (i = 0; i < s.kids.length; i++) stepKid(s, s.kids[i]);
    s.kids = s.kids.filter(function (k) { return !k.gone; });
    var out = s.kids.length > 0, all = true;
    for (i = 0; i < sc.doors.length; i++) {
      var q = sc.doors[i];
      if (q.open && q.out < q.n) out = true;
      if (!q.open || q.out < q.n) all = false;
    }
    s.calm = out ? 1 : 0;
    teacher(s, sc);
    if (all && !out) { sc.done = true; s.calm = 0; s.hush = false; ev(s, { t: 'school_done' }); }
  }

  Sim.ext.school = { create: create, step: step, done: done, waiting: waiting, yardClear: yardClear };
})();
if (typeof module !== 'undefined') module.exports = Sim;
