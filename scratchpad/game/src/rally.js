// rally.js - the Spokesman's rally on the top of the terraces (zone 3), as the storyboard Khaled passed on 29 Oct ("The
// story board looks great"). He is at his podium on the stage's deck, giving his statement (D) to the five of his audience
// in the chairs in front of it, who clap; the relay station's fight goes on around them. He and his audience are scenery,
// as his screens are: in nothing the game hits (no box, no list that a shot, a blast or a man looks in), so shots pass
// them and nothing can touch them. Once the station is cleared (its fight over, and nothing of theirs left in the picture,
// burning, flying or on its way) and Yazeed comes up to the chairs, Yazeed says "Nice beret." and the Spokesman stops
// mid-word (rally_heard); a moment later he jumps: the podium was hiding the rest, no trousers (rally_jump; his audience
// applauds anyway). He lands on the deck and runs for the pass, off the stage's far end and out of the picture
// (rally_gone), and the station's gate opens (the level's gate with `until: 'rally'`).
// The level says where: L.stage = { gate, x0, x1, deck, podium, seats: [[x, y]], lines: [his statement's line ids] }
// (render_ibb.js draws it all and has him heard: the nearest of his screens, or him, carries his voice).
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var DT = Sim.DT, I = Sim._, ev = I.ev;
  var R = Sim.RALLY = {
    BEHIND: 3,          // he stands this close behind his podium (to its right: he faces left, his audience and Yazeed):
                        // it hides everything below his belt
    REACH: 70,          // Yazeed has come up to the chairs: this near the stage's left end
    HEARD: 80,          // from "Nice beret." to the jump
    JUMP: 44,           // the jump, up from behind the podium and back down onto the deck
    HIGH: 28,           // how high
    RUN: 110,           // his dash for the pass, px a second
    FALL: 600           // off the stage's far end: gravity, px a second a second
  };

  function create(s) {
    var Lg = s.L.stage;
    s.rally = Lg && Lg.gate ? { st: 'speech', t: 0, x: Lg.podium + R.BEHIND, y: Lg.deck, vy: 0, face: -1, runD: 0, clearT: 0 } : null;
    if (s.rally && gateOf(s) && gateOf(s).done) s.rally.st = 'gone';         // (a game started past it)
  }
  function done(s) { return !s.rally || s.rally.st === 'gone'; }
  function gateOf(s) {
    for (var i = 0; i < s.gates.length; i++) if (s.gates[i].id === s.L.stage.gate) return s.gates[i];
    return null;
  }
  // the station is cleared: its fight is over, nobody of theirs is awake with his feet in the picture, and nothing is
  // burning, flying or on its way
  function cleared(s) {
    var gt = gateOf(s), i;
    if (!gt) return false;
    for (i = 0; i < gt.groups.length; i++) if (!s.groups[gt.groups[i]].done) return false;
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i], G = s.groups[e.g];
      if (e.alive && e.hostile && (!G || G.awake) && Sim.onScreen(s, e.x, -2)) return false;
    }
    for (i = 0; i < s.bombs.length; i++) if (!s.bombs[i].gone) return false;
    for (i = 0; i < s.bullets.length; i++) if (!s.bullets[i].gone && !s.bullets[i].own) return false;
    return true;
  }

  function step(s) {
    var r = s.rally, Lg = s.L.stage, p = s.p;
    if (!r || r.st === 'gone') return;
    r.t++;
    if (r.st === 'speech') {
      if (!p.dead && p.x >= Lg.x0 - R.REACH && Sim.onScreen(s, r.x, -12) && cleared(s)) { r.st = 'heard'; r.t = 0; ev(s, { t: 'rally_heard', x: r.x, y: r.y }); }
    } else if (r.st === 'heard') {
      if (r.t >= R.HEARD) { r.st = 'jump'; r.t = 0; ev(s, { t: 'rally_jump', x: r.x, y: r.y }); }
    } else if (r.st === 'jump') {
      var u = r.t / R.JUMP;
      r.y = Lg.deck - 4 * R.HIGH * u * (1 - u);
      if (r.t >= R.JUMP) { r.y = Lg.deck; r.st = 'run'; r.t = 0; r.face = 1; ev(s, { t: 'rally_land', x: r.x, y: r.y }); }
    } else if (r.st === 'run') {
      r.x += R.RUN * DT; r.runD += R.RUN * DT;
      if (r.x > Lg.x1) {                                   // (off the deck's far end, down to the ground behind the stage)
        var g = Sim.surfaceY(s.L, -1, r.x);
        r.vy += R.FALL * DT; r.y = Math.min(g, r.y + r.vy * DT);
      }
      if (r.x > Math.max(s.cam + s.viewW, Lg.x1 + 8) + 16) { r.st = 'gone'; r.t = 0; ev(s, { t: 'rally_gone' }); }
    }
  }

  Sim.ext.rally = { create: create, step: step, done: done, cleared: cleared };
})();
if (typeof module !== 'undefined') module.exports = Sim;
