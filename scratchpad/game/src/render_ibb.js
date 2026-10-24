// render_ibb.js - how Ibb's speakers and screens look, and what the men under a speaker do (Render.bosses.ibb). The
// pictures are a sheet of their own (art/out/ibb.png, tools/ibb_sprites.py). It also chooses the Spokesman's next line:
// the nearest speaker or screen on screen that is playing, and it says its lines in turn (talk(), asked by main.js).
//   a speaker: its pole, its crossbar and two horns; while it plays, the sound going out of the horns on the beat of the
//     chant; hit, a white flash; dead, the horns hanging, burnt; taken over, quiet (the announcer is the subtitle)
//   a man under a speaker that plays: standing, he chants (a fist up, a fist down, all of them in step); whatever he
//     does, a speech bubble over his head, beating with the chant
//   a man flinching (a screen beside him has just gone): his arm up over his eyes
//   a screen: the billboard on its legs, or a shop's set on a crate; his face, the mouth going with the line when it is
//     the one talking (the shapes come with each line, gen/audio.json), on its own when it is not; shot, static and
//     a crack
(function () {
  'use strict';
  var FS = null, IMI = null, cx = null;
  var BEAT = 24;                        // the chant: a fist up for 24 ticks, down for 24, everyone together
  var cur = null, lastEnd = -999, lastSrc = 0;      // the line being said: by which source, which line, from when
  var noise = [];                       // static, made once: four little frames of it

  function sheet() {
    if (!FS) FS = (typeof ATLAS !== 'undefined' && ATLAS.ibb) || null;
    if (!IMI) IMI = Render.image('ibb');
    return !!(FS && IMI);
  }
  function ispr(name, x, y, flip, alpha) {
    var f = FS.frames[name];
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    if (alpha != null && alpha < 1) cx.globalAlpha = alpha;
    if (flip) { cx.save(); cx.translate(x + 1, y); cx.scale(-1, 1); cx.drawImage(IMI, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]); cx.restore(); }
    else cx.drawImage(IMI, f[0], f[1], f[2], f[3], x - f[4], y - f[5], f[2], f[3]);
    if (alpha != null && alpha < 1) cx.globalAlpha = 1;
  }
  function isprRot(name, x, y, ang, flip) {
    var f = FS.frames[name];
    if (!f) return;
    cx.save(); cx.translate(Math.round(x), Math.round(y)); if (flip) cx.scale(-1, 1); cx.rotate(ang);
    cx.drawImage(IMI, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
    cx.restore();
  }
  function hash(a, b) { var t = (a * 374761393 + b * 668265263) | 0; t = Math.imul(t ^ (t >>> 13), 1274126177); return ((t ^ (t >>> 16)) >>> 0) / 4294967296; }
  function staticFrame(k) {
    if (!noise.length) {
      for (var n = 0; n < 4; n++) {
        var c = document.createElement('canvas'); c.width = 48; c.height = 32;
        var g = c.getContext('2d'), im = g.createImageData(48, 32);
        for (var i = 0; i < 48 * 32; i++) {
          var v = Math.floor(40 + hash(i, n * 977 + 13) * 200), row = Math.floor(i / 48);
          if ((row + n) % 7 === 0) v = Math.min(255, v + 50);                       // (a brighter band rolling down it)
          im.data[i * 4] = v; im.data[i * 4 + 1] = v; im.data[i * 4 + 2] = Math.min(255, v + 12); im.data[i * 4 + 3] = 255;
        }
        g.putImageData(im, 0, 0);
        noise.push(c);
      }
    }
    return noise[k & 3];
  }

  // ---------------------------------------------------------------- the speakers
  function drawSpeaker(s, o, K) {
    var x = Math.round(o.x), y = Math.round(o.y), top = y - Sim.ext.ibb.I.POLE_H, tick = s.tick, wh = o.hurtT < 2 ? '!' : '';
    ispr('spk_pole' + wh, x, y);
    ispr('spk_bar' + wh, x, top);
    if (o.st === 'dead') {
      // the horns hanging off the crossbar, burnt
      isprRot('spk_horn_burnt', x + 8, top - 1, 0.9 + Math.min(0.5, o.t * 0.04), false);
      isprRot('spk_horn_burnt', x - 9, top - 1, 0.35, true);
      if (o.t < 200 && tick % 7 === 0) K.part('ember', x + 10 + (Math.random() - 0.5) * 6, top + 6, { life: 10 + Math.random() * 10, vx: (Math.random() - 0.5) * 60, vy: -40 - Math.random() * 40, g: 400 });
      if (o.t < 160 && tick % 9 === 0) K.part('wisp', x + 6, top - 4, { life: 22, vy: -30, vx: (Math.random() - 0.5) * 10 });
      return;
    }
    ispr('spk_horn' + wh, x + 8, top - 1);
    ispr('spk_horn' + wh, x - 9, top - 1, true);
    if (o.st === 'live') {
      var b = Math.floor(tick / (BEAT / 1.5)) % 3;                // (the sound going out: three rings, twice to each fist)
      ispr('spk_wave' + b, x + 8 + 12, top - 1);
      ispr('spk_wave' + b, x - 9 - 12, top - 1, true);
      // the first one says what to do about it (with the hint), for as long as Yazeed is not right up against it
      if (o.hint && Math.abs(s.p.x - o.x) > 14 && (tick >> 4) % 2) K.text('s_lav', T('WALK IN'), x, top - 24, 'c');
    } else if (o.st === 'hijack' && o.t < 170) {
      // (taken over: the announcer coming out of it, in gold)
      var g = Math.floor(o.t / 8) % 3;
      ispr('spk_wave' + g, x + 8 + 12, top - 1, false, 0.55);
      ispr('spk_wave' + g, x - 9 - 12, top - 1, true, 0.55);
    }
  }

  // ---------------------------------------------------------------- the screens
  // the mouth of a screen: with the line, frame by frame, if it is the one talking; on its own (soundless) if not
  function mouthOf(s, o, K) {
    var sub = K.sub();
    if (cur && cur.src === o.id && sub && sub.id === cur.id) {
      var v = Sound.lineOf(cur.id), i = Math.floor((s.tick - cur.t0) * 15 / 60);
      return v && v.m && i < v.m.length ? +v.m.charAt(i) : 0;
    }
    var h = hash(Math.floor(s.tick / 5), o.id * 31);
    return h < 0.35 ? 0 : (h < 0.65 ? 1 : 2);
  }
  function blinkOf(s, o) { return (s.tick + o.id * 53) % 200 < 6; }
  function drawBoard(s, o, K) {
    var x0 = Math.round(o.x) - 72, y1 = Math.round(o.y) - Sim.ext.ibb.I.BOARD_LIFT, y0 = y1 - 96, gy = Math.round(o.y);
    // its two legs
    cx.fillStyle = '#120e0a'; cx.fillRect(x0 + 22, y1 + 3, 6, gy - y1 - 3); cx.fillRect(x0 + 116, y1 + 3, 6, gy - y1 - 3);
    cx.fillStyle = '#3a3e44'; cx.fillRect(x0 + 23, y1 + 3, 4, gy - y1 - 3); cx.fillRect(x0 + 117, y1 + 3, 4, gy - y1 - 3);
    cx.fillStyle = '#5a6068'; cx.fillRect(x0 + 23, y1 + 3, 1, gy - y1 - 3); cx.fillRect(x0 + 117, y1 + 3, 1, gy - y1 - 3);
    if (o.st === 'on') {
      ispr('board', x0, y0);
      var m = mouthOf(s, o, K);
      if (m) ispr('board_m' + m, x0, y0);
      if (blinkOf(s, o)) ispr('board_bl', x0, y0);
      if (o.hurtT < 2) { cx.globalAlpha = 0.35; cx.fillStyle = '#ffffff'; cx.fillRect(x0, y0, 144, 96); cx.globalAlpha = 1; }
    } else {
      cx.imageSmoothingEnabled = false;
      cx.drawImage(staticFrame(s.tick >> 1), x0, y0, 144, 96);
      cx.globalAlpha = 0.25; cx.fillStyle = '#000000'; cx.fillRect(x0, y0, 144, 96); cx.globalAlpha = 1;
      ispr('board_crack', x0, y0);
    }
    ispr('board_frame', x0, y0);
  }
  function drawTV(s, o, K) {
    var x = Math.round(o.x), gy = Math.round(o.y), I = Sim.ext.ibb.I, base = gy - I.CRATE_H;
    ispr('crate', x, gy);
    var sx = x - 20, sy = base - 26;                           // the screen's top left, inside the set
    if (o.st === 'on') {
      var m = mouthOf(s, o, K);
      ispr(m === 0 && blinkOf(s, o) ? 'tvb' : 'tv' + m, sx, sy);
      if (o.hurtT < 2) { cx.globalAlpha = 0.45; cx.fillStyle = '#ffffff'; cx.fillRect(sx, sy, 32, 21); cx.globalAlpha = 1; }
    } else {
      cx.imageSmoothingEnabled = false;
      cx.drawImage(staticFrame(s.tick >> 1), 0, 0, 32, 21, sx, sy, 32, 21);
      ispr('tv_crack', sx, sy);
    }
    ispr('tv_box', x, base);
  }

  function scene(s, paused, K) {
    if (!s.ibb || !sheet()) return;
    cx = K.ctx();
    var cam = s.cam, W = K.W(), i, o;
    for (i = 0; i < s.ibb.scr.length; i++) {
      o = s.ibb.scr[i];
      if (o.x1 < cam - 10 || o.x0 > cam + W + 10) continue;
      if (o.big) drawBoard(s, o, K); else drawTV(s, o, K);
    }
    for (i = 0; i < s.ibb.spk.length; i++) {
      o = s.ibb.spk[i];
      if (o.x < cam - 40 || o.x > cam + W + 40) continue;
      drawSpeaker(s, o, K);
    }
  }

  // ---------------------------------------------------------------- the men
  function look(e) { return e.k === 'bomber' ? 'bomber' : 'rifle_' + e.look; }
  function pose(s, e, K, name, rx, down, flip) {
    if (!sheet() || !e.alive || !e.hostile || name.charAt(name.length - 1) === '!') return false;
    if (e.k !== 'rifle' && e.k !== 'bomber') return false;
    cx = K.ctx();
    if (e.st === 'flinch') { ispr(look(e) + '_flinch', e.x + rx, e.y, flip); return true; }
    if ((e.st === 'wait' || e.st === 'walk') && !e.moving && !Sim.guarded(s, e) && Sim.ext.ibb.chanting(s, e)) {
      ispr(look(e) + '_chant' + (Math.floor(s.tick / BEAT) % 2), e.x + rx, e.y + down, flip);
      return true;
    }
    return false;
  }
  function mark(s, e, K) {
    if (!sheet() || !Sim.ext.ibb.chanting(s, e) || e.st === 'shock' || e.st === 'surr' || e.st === 'flinch') return;
    cx = K.ctx();
    var k = Math.floor(s.tick / BEAT) % 2;
    ispr('bubble' + k, e.x - 3, e.y - e.h - 3 - k);
  }

  // ---------------------------------------------------------------- what they hear
  function talk(s, K) {
    if (!s.ibb || !s.ibb.src.length) return null;
    var p = s.p, best = null, bd = 1e9, i;
    for (i = 0; i < s.ibb.src.length; i++) {
      var o = s.ibb.src[i];
      if (!o.on || !o.lines.length || !Sim.onScreen(s, o.x, -8)) continue;
      var d = Math.abs(o.x - p.x);
      if (d < bd) { bd = d; best = o; }
    }
    if (!best) return null;
    // (he pauses for breath between his phrases; a screen going round to the start of its lines again waits a little)
    var wait = best.id === lastSrc && best.li === 0 ? 110 : 0;
    if (s.tick - lastEnd < wait) return null;
    var id = best.lines[best.li], v = Sound.lineOf(id);
    best.li = (best.li + 1) % best.lines.length;
    var dur = v ? Math.round(v.at[1] * 60) : 120;
    cur = { src: best.id, id: id, t0: s.tick };
    lastEnd = s.tick + dur; lastSrc = best.id;
    return v ? { id: id, o: { pri: 0.5, src: best.id } } : null;
  }

  // ---------------------------------------------------------------- moments
  function misc(e, s, K) {
    var i;
    switch (e.t) {
      case 'spk_hit':
        for (i = 0; i < 3; i++) K.part('ember', e.x + (Math.random() - 0.5) * 6, e.y, { life: 8 + Math.random() * 8, vx: (Math.random() - 0.5) * 120, vy: -50 - Math.random() * 60, g: 500 });
        return true;
      case 'spk_dead':
        for (i = 0; i < 12; i++) K.part('ember', e.x + (Math.random() - 0.5) * 30, e.y, { life: 14 + Math.random() * 14, vx: (Math.random() - 0.5) * 200, vy: -80 - Math.random() * 120, g: 520 });
        K.part('smoke', e.x, e.y - 4, { life: 40, vx: 6, vy: -30 });
        K.shake(2);
        if (cur && cur.src === e.src) cur = null;
        return true;
      case 'spk_hijack':
        if (cur && cur.src === e.src) cur = null;
        return true;
      case 'scr_hit':
        K.part('ember', e.x + (Math.random() - 0.5) * (e.big ? 100 : 20), e.y + (Math.random() - 0.5) * (e.big ? 60 : 12), { life: 8, vx: (Math.random() - 0.5) * 80, vy: -40, g: 400 });
        return true;
      case 'scr_dead':
        // glass, and a flash of white from the tube
        for (i = 0; i < (e.big ? 26 : 10); i++) K.part('clod', e.x + (Math.random() - 0.5) * (e.big ? 130 : 26), e.y + (Math.random() - 0.5) * (e.big ? 80 : 16),
          { life: 18 + Math.random() * 16, vx: (Math.random() - 0.5) * 160, vy: -60 - Math.random() * 90, g: 600, col: ['#e8f4ff', '#a8c8e0', '#5a7890'][i % 3] });
        K.part('smoke', e.x, e.y, { life: 36, vx: 4, vy: -24 });
        K.flash(e.big ? 5 : 3); K.shake(e.big ? 3 : 1);
        if (cur && cur.src === e.src) cur = null;
        return true;
    }
    return false;
  }
  function reset() { cur = null; lastEnd = -999; lastSrc = 0; }

  Render.bosses.ibb = { scene: scene, pose: pose, mark: mark, talk: talk, misc: misc, reset: reset };
})();
