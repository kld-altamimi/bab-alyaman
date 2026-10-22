// render_roaster.js - how the Big Roaster looks: its parts stacked (tracks, body, drum, hopper, chimney, the
// quartermaster in his cab), what it shows before each move, its smoke and steam, the pour of burning beans rolling
// along the ground, and what is left of it. It plugs into render.js (Render.bosses.roaster).
(function () {
  'use strict';
  var R = Sim.R, seen = {};
  // the first two times each move comes, a word on the screen says what to do about it
  var SAY = { spraytell_hi: 'GET DOWN!', spraytell_lo: 'JUMP IT!', pourtell: 'JUMP IT!', lungetell: 'GET BEHIND THE LINE!', steamtell: 'BACK OFF!' };

  function draw(s, b, paused, K) {
    var tick = K.tick(), x = Math.round(b.x + (b.rock || 0)), y = Math.round(b.y), i, w;
    if (b.st === 'dead') {
      K.spr('rst_wreck', x, y);
      if (!paused && tick % 4 === 0) K.part('smoke', x + (Math.random() - 0.5) * 80, y - 46 - Math.random() * 24, { life: 40, vx: 6, vy: -40 });
      return;
    }
    // the pour of burning beans, rolling along the yard
    for (i = 0; i < s.waves.length; i++) {
      w = s.waves[i];
      K.spr('fx_pour' + ((tick >> 2) % 2), w.x, w.y);
      if (!paused && tick % 3 === 0) K.part('ember', w.x + (Math.random() - 0.5) * 10, w.y - 8, { life: 12, vx: 30, vy: -60, g: 300 });
    }
    // where the lunge will stop: a line on the ground, and keep behind it
    if (b.st === 'lungetell' || (b.st === 'lunge' && b.lungeTo)) {
      var lx = Math.round(b.lungeTo - R.HW), gy = Math.round(Sim.groundY(s.L, Math.max(0, lx)));
      K.dotted(lx, gy - 46, lx, gy, 3, '#ff4030');
      if ((tick >> 2) % 2) K.spr('hud_alert', lx - 4, gy - 50);
    }
    // a hit shows as a white flash laid over it (half strength: with the heavy MG on it, it is hit every few frames)
    var white = b.hurtT < 2 || (b.st === 'dying' && (tick >> 1) % 3 === 0), wh = '', cx = K.ctx();
    var tk = ((Math.floor(Math.abs(b.tread) / 3) % 3) + 3) % 3;
    if (b.st === 'lungetell') tk = (tick >> 1) % 3;                         // the tracks spinning on the spot
    var fast = b.st === 'spraytell' || b.st === 'spray' || b.st === 'dying';
    var spin = fast ? (tick >> 1) % 3 : (tick >> 3) % 3;
    var kick = b.st === 'spray' && b.stT % R.SPRAY_GAP < 3 ? 1 : 0;
    var hop = b.st === 'lob' && b.stT % 10 < 4 ? 2 : (b.st === 'lobtell' && (tick >> 1) % 2 ? 1 : 0);
    function body(sfx) {
      K.spr('rst_track' + tk + sfx, x, y);
      K.spr('rst_body' + b.phase + sfx, x, y);
      K.spr((b.phase === 3 ? 'rst_drumc' : 'rst_drum') + spin + sfx, x + kick, y);
      if (b.phase < 3) K.spr('rst_hopper' + sfx, x, y - hop);
      K.spr((b.phase === 1 ? 'rst_chimney' : 'rst_stub') + sfx, x, y);
    }
    body('');
    if (white) { cx.globalAlpha = 0.55; body('!'); cx.globalAlpha = 1; }
    // the quartermaster: shouting and hauling on his lever while it does something, ducked down in the lunge
    var shout = b.st === 'spray' || b.st === 'lob' || b.st === 'pour' || b.st === 'steam' || b.st === 'intro';
    if (b.st !== 'lunge' && b.st !== 'dying') K.spr('rst_qm' + (shout && (tick >> 3) % 2 ? 1 : 0), x + 38, y - 82 + (b.st === 'stun' ? 3 : 0));
    // what it shows before it moves: the spout glowing (high or low), steam at the grille, the hopper rattling
    if (b.st === 'spraytell' && (tick >> 2) % 2) {
      K.spr('fx_spark2', x + R.SPOUT[0] - 4, y - (b.hi ? R.HIGH : R.LOW));
      K.spr('hud_alert', x + R.SPOUT[0] - 8, y - (b.hi ? R.HIGH : R.LOW) - 12);
    }
    if (b.st === 'steam') K.spr('sjet' + ((tick >> 2) % 2), x - R.HW - 2, y - 12);
    if (paused) return;
    if ((b.st === 'steamtell' || b.st === 'pourtell') && tick % 3 === 0) K.part('wisp', x + R.GRILLE[0] - 4, y + R.GRILLE[1] - 2, { life: 14, vx: -40, vy: -20 });
    if (b.st === 'lobtell' && tick % 4 === 0) K.part('wisp', x - 6, y - R.TOP - 2, { life: 16, vx: (Math.random() - 0.5) * 20, vy: -40 });
    // smoke from the chimney (or what is left of it), darker the more it is hurt
    var cy = b.phase === 1 ? y - 101 : y - 69;
    if (tick % (b.st === 'lungetell' || b.st === 'lunge' ? 2 : 6) === 0) K.part('smoke', x + 38 + (Math.random() - 0.5) * 4, cy, { life: 34, vx: 12 + (b.vx || 0) * -0.2, vy: -46 });
    if (b.phase >= 2 && tick % 9 === 0) K.part('wisp', x + (Math.random() - 0.5) * 80, y - 30 - Math.random() * 30, { life: 20, vy: -40, vx: (Math.random() - 0.5) * 20 });
    if (b.phase === 3 && tick % 5 === 0) K.part('ember', x - 10 + (Math.random() - 0.5) * 50, y - 50, { life: 14, vx: (Math.random() - 0.5) * 60, vy: -60, g: 300 });
    if (Math.abs(b.vx || 0) > 50 && tick % 3 === 0) K.part('puff', x + (b.vx < 0 ? R.HW - 6 : -R.HW + 6), y - 3, { life: 9, flip: b.vx > 0 });
  }

  function events(e, s, K) {
    switch (e.t) {
      case 'boss_intro': K.shake(4); break;
      case 'boss_phase':
        K.embers(e.x, e.y, 18, 320);
        K.pop(e.x, e.y - 20, e.n === 2 ? 'THERE GOES THE CHIMNEY' : 'THE DRUM HAS CRACKED', 's_lav');
        if (e.n === 2) K.part('piece', e.x, e.y, { life: 90, vx: 70, vy: -260, g: 600, spin: 0.3, name: 'rst_chimney', oy: 0 });
        else K.part('piece', e.x, e.y - 10, { life: 90, vx: -60, vy: -280, g: 600, spin: -0.25, name: 'rst_hopper', oy: 0 });
        K.shake(12); K.flash(2);
        break;
      case 'boss_dying': K.shake(12); K.flash(3); break;
      case 'boss_dead':
        K.pop(e.x, e.y - 30, String(e.pts), 'm_org');
        K.embers(e.x, e.y, 30, 440);
        // the drum goes: a cloud of roast coffee
        for (var k = 0; k < 14; k++) K.part('smoke', e.x + (Math.random() - 0.5) * 70, e.y + (Math.random() - 0.5) * 30, { life: 40 + Math.random() * 30, vx: (Math.random() - 0.5) * 80, vy: -30 - Math.random() * 50 });
        K.part('piece', e.x + 40, e.y - 30, { life: 110, vx: 80, vy: -300, g: 560, spin: 0.35, name: 'rst_stub', oy: 0 });
        K.shake(26); K.flash(5);
        break;
    }
  }

  // the roaster's own moments that are not boss_* events
  function misc(e, s, K) {
    switch (e.t) {
      case 'rspray': K.part('muzzle', e.x, e.y, { life: 3, flip: true, name: 'fx_muzzle_s', ang: 0 }); K.part('wisp', e.x - 2, e.y, { life: 10, vx: -30, vy: -10 }); return true;
      case 'rlob': K.part('puff', e.x, e.y, { life: 8 }); return true;
      case 'steam_jet': K.shake(3); return true;
      case 'pour': K.embers(e.x, e.y - 10, 8, 160); return true;
      case 'lunge': K.shake(6); return true;
      case 'brake': K.part('puff', e.x - 4, e.y - 3, { life: 10 }); K.part('puff', e.x + 8, e.y - 3, { life: 10, flip: true }); K.shake(4); return true;
    }
    return false;
  }

  function hud(s, b, K, paused) {
    if (b.st === 'intro' && b.stT === 1) seen = {};
    var key = b.st === 'spraytell' ? 'spraytell_' + (b.hi ? 'hi' : 'lo') : b.st;
    if (!SAY[key]) return;
    if (b.stT === 1 && !paused) seen[key] = (seen[key] || 0) + 1;
    if ((seen[key] || 0) <= 2 && (K.tick() >> 2) % 2) K.text('b_org', T(SAY[key]), Math.floor(K.W() / 2), 70, 'c');
  }

  Render.bosses.roaster = { draw: draw, events: events, misc: misc, hud: hud, under: true };
})();
