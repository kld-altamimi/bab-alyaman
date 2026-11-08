// sandal.js - Ibb: Yazeed one sandal short through Jibla (the mock page of 6 Nov; Khaled: "build it as proposed").
// Statement B ends «One enemy sandal has been captured.»: as he comes into Jibla a lit stick comes down at his feet,
// fizzes a moment and pops, and the sandal comes off his front foot and lands behind him; he goes through Jibla with that
// foot bare while its screens tell statement B, and has both again on the terraces. It is a scene, not an attack: the
// stick is in nothing the game hits and its pop hurts nobody; nothing in how he moves or in what can hit him changes, and
// nobody is made untouchable. Once per run: a continue in Jibla starts him there one sandal short (no stick again).
// The level says where: L.sandal = { at: x where he is when it comes down, back: x from which he has it again }.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var SD = Sim.SANDAL = {
    AHEAD: 10,          // it comes down this far in front of where his feet will be by then (walking on, at them)
    FROM: [70, 150],    // from this far ahead and this far up (out of the top of the picture)
    FLY: 24,            // its way down, in frames
    FUSE: 12,           // fizzing on the ground before it pops
    UP: -250, BACK: 80, G: 900    // the sandal off his foot: up, back the way he came, and down again
  };

  // which of the level's zones a point is in
  function zoneOf(L, x) { var z = 0; for (var i = 0; i < L.zones.length; i++) if (L.zones[i].x <= x) z = i; return z; }

  function create(s, opts) {
    var S = s.L.sandal;
    s.sandal = null;
    if (!S) return;
    var z = (opts && opts.zone) | 0;
    s.sandal = { st: opts && opts.stats && z === zoneOf(s.L, S.at) ? 'short' : 'on', t: 0, lie: false };
  }
  // one sandal short: the stick has gone off and he is not on the terraces yet (render_ibb.js draws the bare foot)
  function short(s) { var sd = s.sandal; return !!sd && sd.st === 'short'; }

  function step(s) {
    var sd = s.sandal, S = s.L.sandal, p = s.p;
    if (!sd || sd.st === 'back') return;
    sd.t++;
    switch (sd.st) {
      case 'on':
        if (p.x >= S.at && p.x < S.back && !p.dead && !p.air && !p.hidden) {
          var tx = p.x + p.face * SD.AHEAD + p.vx * SD.FLY * DT;
          sd.st = 'stick'; sd.t = 0; sd.tx = tx; sd.ty = groundY(s.L, tx);
          sd.sx = tx + p.face * SD.FROM[0]; sd.sy = sd.ty - SD.FROM[1];
          ev(s, { t: 'sandal_throw', x: sd.sx, y: sd.sy });
        }
        break;
      case 'stick':
        if (sd.t >= SD.FLY) { sd.st = 'fuse'; sd.t = 0; ev(s, { t: 'sandal_land', x: sd.tx, y: sd.ty }); }
        break;
      case 'fuse':
        if (sd.t >= SD.FUSE) {
          // the pop: the sandal off his front foot, wherever he has got to, up and back the way he came
          sd.st = 'short'; sd.t = 0; sd.lie = false;
          sd.fx = p.x + p.face * 5; sd.fy = p.y - 2; sd.fvx = -p.face * SD.BACK; sd.fvy = SD.UP; sd.fair = true;
          ev(s, { t: 'sandal_pop', x: sd.tx, y: sd.ty, fx: sd.fx, fy: sd.fy });
        }
        break;
      case 'short':
        if (sd.fair) {
          sd.fvy += SD.G * DT; sd.fx += sd.fvx * DT; sd.fy += sd.fvy * DT;
          var gx = Math.max(0, Math.min(s.L.width - 1, sd.fx)), gy = groundY(s.L, gx);
          if (sd.fvy > 0 && sd.fy >= gy) { sd.fy = gy; sd.fair = false; sd.lie = true; ev(s, { t: 'sandal_down', x: sd.fx, y: sd.fy }); }
        }
        break;
    }
    if (sd.st !== 'on' && p.x >= S.back) { sd.st = 'back'; sd.t = 0; }
  }

  Sim.ext.sandal = { create: create, step: step, short: short };
})();
if (typeof module !== 'undefined') module.exports = Sim;
