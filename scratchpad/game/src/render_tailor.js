// render_tailor.js - how the Tailor's shop looks: the wheeled stands and the figures on them (him, and his dummies in
// exactly his clothes), one passing in front of the other as two are swapped; a dummy with its clothes shot off,
// wobbling, or knocked over; the sheets thrown over them all at the end; the Tailor when he gives himself away (his
// shears up, a pinch of pins, the tape's case, caught out and flapping, sneezing); his tape out along the floor; and him
// wound up in it at the end and hopping off. The stands are part of the shop, so they are drawn whether or not the fight
// has started (scene(), before the men); the tape and what his moves show come with the boss (draw()). It plugs into
// render.js (Render.bosses.tailor).
(function () {
  'use strict';
  var TL = Sim.TL, X = Sim.ext.tailor;
  // the first two times each comes, a word on the screen says what to do about it
  var SAY = { eye: 'KEEP YOUR EYE ON HIM!', duck: 'GET DOWN!', jump: 'JUMP IT!', hit: 'NOW! HIT HIM!', sneeze: "DUMMIES DON'T SNEEZE!" };
  var said = {}, sayKey = null, sayT = 0, was = {}, shreds = 0;
  var CLOTH = ['#74202a', '#b04a44', '#e0dac0', '#3c0c12'];

  // ---- which frame a figure shows. The dummies have the one; he has that one too, until he gives himself away
  function himFrame(s, b, tick) {
    if (!b) return 'tl_pose';
    var t = b.stT;
    switch (b.st) {
      case 'intro': return t > 4 ? ((t >> 3) % 2 ? 'tl_wave1' : 'tl_wave0') : 'tl_pose';
      case 'show': return t < TL.SHOW - 12 ? (((t + 20) >> 3) % 2 ? 'tl_wave1' : 'tl_wave0') : 'tl_pose';
      case 'tell': return b.attack === 'scissors' ? 'tl_raise' : (b.attack === 'pins' ? 'tl_pins' : 'tl_lash');
      case 'throw': return t < 12 ? 'tl_throw' : 'tl_pose';
      case 'sneeze': return (t % 28) >= 8 && (t % 28) < 18 ? 'tl_sneeze' : 'tl_pose';
      case 'caught': return (t >> 2) % 2 ? 'tl_caught1' : 'tl_caught0';
      case 'stun': return 'tl_caught0';
      case 'dying': return t < 46 ? ((t >> 2) % 2 ? 'tl_caught1' : 'tl_caught0') : 'tl_wrapped0';
    }
    return 'tl_pose';
  }
  // (he turns to whoever he is throwing at; standing still, he faces the way they all face, down the hall)
  function turned(b) { return !!b && (b.st === 'tell' || b.st === 'throw' || b.st === 'sneeze' || b.st === 'caught' || b.st === 'stun' || b.st === 'dying'); }
  function stars(K, x, y, tick) {
    for (var k = 0; k < 3; k++) {
      var a = tick * 0.12 + k * 2.1;
      if (((tick >> 2) + k) % 3) K.spr('fx_spark2', x + Math.cos(a) * 9, y + Math.sin(a) * 3);
    }
  }

  // ---- one figure on its stand
  function drawFig(s, b, f, fl, u, K, tick) {
    var p = s.p, x = f.x, top = fl - TL.STAND_H;
    // the one going behind sits a little up the hall, the one coming in front a little nearer
    var dy = f.depth < 0 ? -2 : (f.depth > 0 ? 1 : 0);
    var moving = (f.x0 !== f.x1 && f.x !== f.x1) || f.roll >= 0, bob = moving && (Math.floor(f.x / 5) % 2) ? -1 : 0;
    K.spr('tl_stand', x, fl + dy);
    if (u >= 1 && f.st !== 'off') { K.spr('tl_cover', x, fl + dy); return; }
    var name = null, flip = true, jx = 0;
    if (f.st === 'him') {
      name = himFrame(s, b, tick);
      if (turned(b)) flip = p.x < x;
      if (b && (b.st === 'caught' || (b.st === 'dying' && b.stT < 46))) jx = (tick >> 1) % 2 ? 1 : -1;
      if (b && b.st === 'dying' && b.stT >= 46) flip = Math.floor(Math.sqrt((b.stT - 46) * 1.6)) % 2 === 0;      // (spun round and round as the tape winds on, slower and slower)
    } else if (f.st === 'dressed') name = 'tl_pose';
    if (name) {
      K.spr(name, x + jx, top + dy + bob, flip);
      if (f.hurtT < 2 && K.frame(name + '!')) K.spr(name + '!', x + jx, top + dy + bob, flip, 0.6);
    } else if (f.st === 'bare') {
      // its clothes gone: a dress form on a pole, rocking on its stand from the shot
      var w = f.wob > 0 ? Math.sin(f.wob * 0.9) * 0.16 * (f.wob / 12) : 0;
      K.sprRot('tl_bare', x, top + dy, w, false);
      if (f.hurtT < 2) { var c2 = K.ctx(); c2.globalAlpha = 0.6; K.sprRot('tl_bare!', x, top + dy, w, false); c2.globalAlpha = 1; }
    } else if (f.st === 'down') {
      // knocked off its stand, lying on the floor beside it
      var fall = f.fall || 1;
      K.sprRot('tl_bare', x - fall * 7, fl - 8, fall * Math.PI / 2, false);
    }
    if (f.st === 'him' && b) {
      if (b.st === 'stun') stars(K, x, top - 44, tick);
      if (b.st === 'tell' && (tick >> 2) % 2) K.spr('hud_alert', x, top - 48);
    }
    if (u > 0 && f.st !== 'off') {
      // the sheet coming down over it (or going back up off it)
      var off = Math.round((1 - u) * (1 - u) * 56);
      K.spr('tl_cover', x, fl + dy - off, false, Math.min(1, u * 3));
    }
  }

  // ---- the shop, every frame, before the men: the stands and whoever is on them, the far ones first
  function scene(s, paused, K) {
    var tl = s.tailor;
    if (!tl) return;
    var C = s.L.tailor, W = K.W();
    if (C.slots[C.slots.length - 1] + 60 < s.cam || C.slots[0] - 60 > s.cam + W) return;
    var b = s.boss && s.boss.kind === 'tailor' ? s.boss : null, fl = X.floorY(s), tick = K.tick(), u = tl.cover / TL.COVER_T;
    var figs = tl.figs.slice().sort(function (f1, f2) { return f1.depth - f2.depth; });
    for (var i = 0; i < figs.length; i++) if (figs[i].st !== 'off') drawFig(s, b, figs[i], fl, u, K, tick);
  }

  // ---- with the boss: his tape, out along the floor at ankle height
  function draw(s, b, paused, K) {
    var tp = s.tailor && s.tailor.tape;
    if (!tp) return;
    var cx = K.ctx(), fl = X.floorY(s), ty = fl - TL.TAPE_Y, me = X.real(s), d = tp.dir;
    var x0 = Math.round(tp.x0), x1 = Math.round(tp.x0 + d * tp.len), a = Math.min(x0, x1), w = Math.abs(x1 - x0);
    // (from the case in his hand down to the floor)
    var hx = me.x + d * 10, hy = fl - TL.STAND_H - 16, n = Math.max(1, Math.round(Math.abs(ty - hy)));
    cx.fillStyle = '#ffe264';
    for (var k = 0; k <= n; k++) cx.fillRect(Math.round(hx + (x0 - hx) * k / n), Math.round(hy + (ty - hy) * k / n), 1, 1);
    if (w < 1) return;
    cx.fillStyle = '#2a1c08'; cx.fillRect(a, ty - 2, w + 1, 4);
    cx.fillStyle = '#ffe264'; cx.fillRect(a, ty - 1, w + 1, 1);
    cx.fillStyle = '#d49c1c'; cx.fillRect(a, ty, w + 1, 1);
    cx.fillStyle = '#7a5208';
    for (k = 2; k < w; k += 4) cx.fillRect(x0 + d * k, ty - 1, 1, 1);
    // the brass hook on its end
    cx.fillStyle = '#2a1c08'; cx.fillRect(x1 - (d > 0 ? 0 : 2), ty - 4, 3, 6);
    cx.fillStyle = '#c4922c'; cx.fillRect(x1 - (d > 0 ? -1 : 1), ty - 3, 1, 4);
  }

  function events(e, s, K) {
    switch (e.t) {
      case 'boss_intro': K.shake(2); said = {}; sayKey = null; was = {}; shreds = 0; break;
      case 'boss_phase':
        K.pop(e.x, e.y - 50, T(e.n === 2 ? 'MORE DUMMIES' : 'UNDER WRAPS'), 's_lav');      // (above where FOUND HIM! still hangs)
        K.shake(6); K.flash(1);
        break;
      case 'boss_dying': K.shake(8); K.flash(2); break;
      case 'boss_dead':
        K.pop(e.x, e.y - 30, String(e.pts), 'm_org');
        for (var j = 0; j < 8; j++) K.part('spark', e.x + (Math.random() - 0.5) * 16, e.y - Math.random() * 10, { life: 6, name: 'fx_spark2' });
        K.shake(14); K.flash(4);
        break;
    }
  }

  // the shop's own moments that are not boss_* events
  function misc(e, s, K) {
    var k;
    switch (e.t) {
      case 'shred':
        // a dummy's clothes torn off by a shot: the cloth flies, and (the first times) it says what it was
        for (k = 0; k < 8; k++) K.part('clod', e.x + (Math.random() - 0.5) * 10, e.y - 6 + Math.random() * 16, { life: 26 + Math.random() * 14, vx: (Math.random() - 0.5) * 150, vy: -70 - Math.random() * 110, g: 420, col: CLOTH[k % 4] });
        K.part('puff', e.x, e.y + 4, { life: 9 });
        if (++shreds <= 2) K.pop(e.x, e.y - 22, T('DUMMY!'), 's_org');
        if (shreds === 2) say('sneeze', 120);
        return true;
      case 'topple':
        K.part('puff', e.x - 8, e.y + 16, { life: 9 }); K.part('puff', e.x + 8, e.y + 16, { life: 9, flip: true });
        K.shake(2);
        return true;
      case 'redress':
        K.part('puff', e.x, e.y + 4, { life: 10 });
        for (k = 0; k < 3; k++) K.part('clod', e.x + (Math.random() - 0.5) * 8, e.y - 4, { life: 14, vx: (Math.random() - 0.5) * 60, vy: -40 - Math.random() * 40, g: 300, col: CLOTH[k % 3] });
        return true;
      case 'cover': case 'uncover':
        for (k = 0; k < s.tailor.figs.length; k++) { var f = s.tailor.figs[k]; if (f.st !== 'off' && f.slot < s.tailor.n && e.t === 'uncover') K.part('puff', f.x, X.floorY(s) - 30, { life: 10, flip: k % 2 === 1 }); }
        return true;
      case 'shuffle': say('eye', 110); return true;
      case 'caught':
        K.pop(e.x, e.y - 8, T('FOUND HIM!'), 's_org');
        say('hit', 80);
        return true;
      case 'snip': K.part('spark', e.x, e.y, { life: 5, name: 'fx_spark2' }); return true;
      case 'pins': for (k = 0; k < 3; k++) K.part('spark', e.x + (Math.random() - 0.5) * 6, e.y + (Math.random() - 0.5) * 6, { life: 4, name: 'fx_spark2' }); return true;
      case 'yank': K.shake(5); K.part('puff', e.x, e.y - 2, { life: 9 }); return true;
      case 'tape_wind':
        for (k = 0; k < 4; k++) K.part('clod', e.x + (Math.random() - 0.5) * 18, e.y - 10 + Math.random() * 24, { life: 10, vx: (Math.random() - 0.5) * 120, vy: -30 - Math.random() * 40, g: 200, col: k % 2 ? '#ffe264' : '#d49c1c' });
        return true;
      case 'wrap_hop': K.part('puff', e.x, e.y - 2, { life: 7 }); return true;
      case 'swap': case 'roll_in': case 'tape': return true;
    }
    return false;
  }

  // ---- the word on the screen
  function say(key, n) { said[key] = (said[key] || 0) + 1; if (said[key] <= 2) { sayKey = key; sayT = n; } }
  function hud(s, b, K, paused) {
    if (!s.tailor || b.st === 'intro' || b.st === 'show' || b.st === 'dying' || b.st === 'dead') { if (b.st !== 'show') sayKey = null; return; }
    // (what is going on now, and whether it has just started)
    var now = { duck: b.st === 'tell' && b.attack === 'scissors', jump: b.st === 'tell' && b.attack === 'tape', long: b.st === 'hunt' && b.huntT >= 300 };
    for (var k in now) {
      if (now[k] && !was[k]) {
        if (k === 'long') { if (!said.sneeze) say('sneeze', 120); }
        else say(k, 50);
      }
      was[k] = now[k];
    }
    if (!paused && sayT > 0) sayT--;
    if (!sayKey || sayT <= 0) return;
    if ((K.tick() >> 2) % 2) K.text('b_org', T(SAY[sayKey]), Math.floor(K.W() / 2), 70, 'c');
  }

  // ---- the Tailor himself at the end, wound up in his tape: down off his stand, hopping, giving up, hopping off
  function man(s, e, K) {
    if (!e.wrapped) return false;
    var tick = K.tick(), flip = e.face < 0, name = 'tl_wrapped0', y = e.y, ph = -1;
    if (e.st === 'stagger') { ph = (e.stT % 12) / 12; if (e.stT < 12) y -= Math.round((12 - e.stT) * TL.STAND_H / 12); }
    else if (e.captured && e.stT > 70) ph = (e.walkD / 10) % 1;
    if (ph >= 0) { y -= Math.round(Math.sin(ph * Math.PI) * 5); if (ph < 0.15 || ph > 0.85) name = 'tl_wrapped1'; }
    K.spr(name, e.x, y, flip);
    if (e.st === 'daze') stars(K, e.x, e.y - 44, tick);
    if (e.st === 'surr' && !e.captured && (tick >> 4) % 2) K.text('s_lav', T('WALK IN'), e.x, e.y - 50, 'c');
    return true;
  }

  Render.bosses.tailor = { scene: scene, draw: draw, events: events, misc: misc, hud: hud, man: man };
})();
