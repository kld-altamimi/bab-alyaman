// dhamar.js - what Dhamar (Mission 5, the Wadi) adds on the highway across Qa' Jahran (zone 1, on wheels; drive.js does the
// driving). Khaled, 11 Nov: zones 1-3 built straight through as one test build, from the stage plan.
// The Committee's checkpoints (L.checkpoints): as one comes into the picture a man in its queue asks the question (cp_ask:
// "And the wages?"), and the speakers on its pole laugh back, long (cp_laugh: the Committee's voice before he is seen); a
// note or two blows out of the stamp window and across the road. Yazeed never stops for them: a note the 4x4 goes through,
// in the air or lying on the road, counts as wages returned (s.stats.wages, the results screen's counter) and some score.
// Each checkpoint's barrier (the road item 'barrier', drive.js puts it on the road with the rest) is a striped pole across
// the near lane: the 4x4 goes through it (it breaks, a jolt and some score; a hop clears it), or a grenade breaks it.
// The barrier lifts for the Zanabeel's goats and not for you: render_dhamar.js draws it up while they cross, well before
// the 4x4 is there. The queue, the goats, the convoy's lorries going the other way: scenery (render_dhamar.js), in nothing
// the game hits.
// Every other mission: nothing (s.dham is null; no random number is drawn).
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var DT = Sim.DT, I = Sim._, ev = I.ev;
  var DH = Sim.DHAMAR = {
    SEE: 520,           // a checkpoint's speakers' pole is this far ahead of the 4x4: the queue asks
    LAUGH: 50,          // ...and this long after, the speakers laugh back
    NOTE_EVERY: 16,     // the notes blow out of the window one after another while he laughs
    NOTE_VX: -44,       // the wind takes them back down the road toward the 4x4, px a second
    NOTE_VY: -30,       // ...up out of the window first (no higher than the 4x4's roof)
    NOTE_G: 52,         // ...then they settle, slowly
    NOTE_DRAG: 0.985,
    NOTE_PTS: 50,       // one note back
    NOTE_LIE: 900,      // a note on the road stays there this long (a game started past it never sees it)
    BAR_PTS: 100,       // a barrier through
    BAR_H: 22           // the pole's height over the road: a 4x4 coming down onto it, or hopping lower than this, breaks it
  };

  function create(s) {
    var L = s.L;
    s.dham = null;
    if (!L.checkpoints) return;
    if (s.stats.wages == null) s.stats.wages = 0;
    s.dham = { cps: L.checkpoints.map(function (c) { return { x: c.x, hut: c.hut, pole: c.pole, barrier: c.barrier, n: c.notes || 2, st: 'wait', t: 0, out: 0 }; }), notes: [] };
    // (a game started past the road: its checkpoints are behind it)
    if (s.mode !== 'drive') for (var i = 0; i < s.dham.cps.length; i++) s.dham.cps[i].st = 'done';
  }

  function addNote(s, cp) {
    var d = s.dham;
    d.notes.push({ id: s.nextId++, x: cp.hut + 2, y: 150 - 4 * s.rand(), vx: DH.NOTE_VX * (0.7 + 0.6 * s.rand()), vy: DH.NOTE_VY * (0.6 + 0.6 * s.rand()), t: 0, st: 'fly', ph: s.rand() * 6.28 });
  }

  function step(s) {
    var d = s.dham, c = s.car, L = s.L, i;
    if (!d) return;
    var driving = s.mode === 'drive' && c && (c.st === 'drive' || c.st === 'stop') && !s.p.dead;
    // (the mission starts in the 4x4: the word on how to drive it, as the coast road gives it when Yazeed gets in)
    if (driving && s.tick === 150 && !s.hinted.drive) { s.hinted.drive = 1; ev(s, { t: 'hint', k: 'drive' }); }
    for (i = 0; i < d.cps.length; i++) {
      var cp = d.cps[i];
      cp.t++;
      if (cp.st === 'wait') {
        if (driving && cp.pole - c.x < DH.SEE) { cp.st = 'ask'; cp.t = 0; ev(s, { t: 'cp_ask', x: cp.hut - 30, y: 150, n: i }); }
      } else if (cp.st === 'ask') {
        if (cp.t >= DH.LAUGH) { cp.st = 'laugh'; cp.t = 0; ev(s, { t: 'cp_laugh', x: cp.pole, y: 120, n: i }); }
      } else if (cp.st === 'laugh') {
        if (cp.out < cp.n && cp.t >= 20 + cp.out * DH.NOTE_EVERY) { addNote(s, cp); cp.out++; }
        if (cp.out >= cp.n && cp.t > 400) { cp.st = 'done'; cp.t = 0; }
      }
    }
    // the notes: up out of the window on the wind, then down onto the road, fluttering
    for (i = 0; i < d.notes.length; i++) {
      var n = d.notes[i];
      n.t++;
      if (n.st === 'fly') {
        n.vx *= DH.NOTE_DRAG; n.vy += DH.NOTE_G * DT;
        if (n.vy > 26) n.vy = 26;
        n.x += (n.vx + Math.sin(n.t / 9 + n.ph) * 14) * DT; n.y += n.vy * DT;
        var gy = Sim.groundY(L, n.x) - 1;
        if (n.y >= gy) { n.y = gy; n.st = 'lie'; n.t = 0; }
      } else if (n.st === 'lie' && n.t > DH.NOTE_LIE) n.st = 'gone';
      // the 4x4 through it: wages returned
      if (n.st !== 'gone' && driving) {
        var b = Sim.ext.drive.carBox(c);
        if (n.x > b.x0 - 3 && n.x < b.x1 + 3 && n.y > b.y0 - 6 && n.y < b.y1 + 2) {
          n.st = 'gone';
          s.stats.wages++; s.score += DH.NOTE_PTS;
          ev(s, { t: 'note_back', x: n.x, y: n.y, pts: DH.NOTE_PTS, n: s.stats.wages });
        }
      }
      if (n.x < s.cam - 30) n.st = 'gone';
    }
    // the barriers (put on the road by drive.js, with the mines and the drums): the 4x4 through one breaks it
    if (s.mode === 'drive' && c && c.st !== 'wreck' && !s.p.dead) {
      var cb = Sim.ext.drive.carBox(c);
      for (i = 0; i < s.props.length; i++) {
        var o = s.props[i];
        if (o.k !== 'barrier' || o.gone || o.st === 'broken') continue;
        if (o.x > cb.x0 && o.x < cb.x1 + 2 && c.y > o.y - DH.BAR_H) breakBar(s, o, 'ram', 1);
      }
    }
  }
  function breakBar(s, o, how, dir) {
    o.st = 'broken'; o.t = 0; o.dir = dir;
    s.score += DH.BAR_PTS;
    if (how === 'ram') s.stopT = Math.max(s.stopT, 2);
    ev(s, { t: 'bar_smash', x: o.x, y: o.y, how: how, pts: DH.BAR_PTS });
  }
  // one of his grenades going off near a barrier breaks it too
  function blast(s, x, y, r, kind, own) {
    if (!s.dham || !own) return;
    for (var i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.k !== 'barrier' || o.gone || o.st === 'broken') continue;
      if (Math.abs(o.x - x) < r + 10 && y > o.y - DH.BAR_H - r) breakBar(s, o, 'blast', x < o.x ? 1 : -1);
    }
  }
  function sweep(s) {
    if (s.dham) s.dham.notes = s.dham.notes.filter(function (n) { return n.st !== 'gone'; });
  }

  Sim.ext.dhamar = { create: create, step: step, blast: blast, sweep: sweep };
})();
if (typeof module !== 'undefined') module.exports = Sim;
