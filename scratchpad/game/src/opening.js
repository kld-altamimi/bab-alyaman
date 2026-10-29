// opening.js - a mission that begins with Salem dropping Yazeed off (Ibb, the brief's opening, built 30 Oct: Khaled,
// 00:39, "Go ahead and finish the whole level"). Salem's 4x4 comes up the road with Yazeed standing in its roof ring and
// stops under the billboard, which is in the middle of a statement; Yazeed jumps down; Salem won't drive in this noise and
// backs off the way he came; Yazeed has his first word and the mission is his. Only at the start of the mission, not on
// a continue or from a later checkpoint. While it plays the stick does nothing and nothing can be fired (s.script, sim.js);
// nobody can reach Yazeed there (the first fight is well up the road), so he is not made untouchable (which would have him
// blink).
// The level says where: L.opening = { from: x the 4x4 comes from (off the left of the picture), stop: x it stops at }.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var OP = Sim.OPENING = {
    V: 170,             // up the road, px a second
    BRAKE: 240,         // and stopping, px a second a second
    WAIT: 20,           // stopped, a moment before Yazeed jumps down
    HOP_VY: -170,       // his jump down off the roof ring
    SALEM: 30,          // landed: this long before Salem says it
    TALK: 104,          // Salem's line
    BACK_V: -150,       // and he backs off
    FREE: 30            // backing off this long, the stick is Yazeed's again
  };
  function D() { return Sim.D || { BED: -22, STAND: 31 }; }      // (drive.js: where Yazeed stands in the 4x4)

  function create(s, opts) {
    var O = s.L.opening;
    s.open = null;
    if (!O || (opts && (opts.zone || opts.stats))) return;
    s.open = { st: 'drive', t: 0, x: O.from, vx: OP.V, wheel: 0 };
    s.script = { mx: 0 };
    s.p.hidden = true;
  }
  function done(s) { return !s.open || s.open.st === 'away' || s.open.st === 'gone'; }

  function step(s) {
    var o = s.open, O = s.L.opening, p = s.p;
    if (!o || o.st === 'gone') return;
    o.t++;
    switch (o.st) {
      case 'drive':
        var left = O.stop - o.x;
        o.vx = left > 0.5 ? Math.max(18, Math.min(OP.V, Math.sqrt(2 * OP.BRAKE * left))) : 0;
        o.x += o.vx * DT; o.wheel += o.vx * DT;
        if (o.t === 1) ev(s, { t: 'op_arrive', x: o.x });
        if (o.vx === 0 || o.x >= O.stop) { o.x = O.stop; o.vx = 0; o.st = 'stop'; o.t = 0; ev(s, { t: 'op_stop', x: o.x }); }
        break;
      case 'stop':
        if (o.t >= OP.WAIT) {
          // down off the roof ring, forward, onto the road in front of the 4x4
          p.hidden = false;
          p.x = o.x + D().BED; p.y = groundY(s.L, o.x) - D().STAND; p.vy = OP.HOP_VY; p.air = true; p.plat = -2; p.face = 1; p.jumpHeld = false;
          s.script.mx = 1;
          o.st = 'hop'; o.t = 0;
          ev(s, { t: 'op_hop', x: p.x, y: p.y });
        }
        break;
      case 'hop':
        if (!p.air) { s.script.mx = 0; o.st = 'down'; o.t = 0; }
        break;
      case 'down':
        if (o.t === OP.SALEM) ev(s, { t: 'op_salem', x: o.x });
        if (o.t >= OP.SALEM + OP.TALK) { o.st = 'back'; o.t = 0; ev(s, { t: 'op_back', x: o.x }); }
        break;
      case 'back':
        o.vx = Math.max(OP.BACK_V, o.vx + OP.BACK_V * DT * 1.6);
        o.x += o.vx * DT; o.wheel += o.vx * DT;
        if (o.t === OP.FREE) { s.script = null; ev(s, { t: 'op_go', x: p.x }); }
        if (o.x < s.cam - 90) { o.st = 'gone'; if (s.script) { s.script = null; ev(s, { t: 'op_go', x: p.x }); } }
        break;
    }
  }

  Sim.ext.opening = { create: create, step: step, done: done };
})();
if (typeof module !== 'undefined') module.exports = Sim;
