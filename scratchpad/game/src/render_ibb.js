// render_ibb.js - Ibb's screens (Render.bosses.ibb): the Spokesman on the billboard and on the shops' sets, talking.
// The level lists them (L.screens: { x, size: 'board' | 'tv', zone, lines, gy }: gy, where its feet are, when it stands
// on the verge behind the road rather than on the floor where the fight is); they are the scenery's, not the fight's:
// shots pass them and nothing breaks them (Khaled, 24 Oct: people want to hear him). The pictures are a sheet of their
// own (art/out/ibb.png, tools/ibb_sprites.py).
//   the billboard on its two legs; a shop's set on a crate. His face, the mouth going with the line when that screen is
//   the one talking (the shapes come with each line, gen/audio.json), on its own (soundless) when it is not; a blink.
//   talk() chooses his next line for main.js: the nearest screen in the picture says its lines in turn, so walking past
//   them puts a statement together.
// The school (zone 2, Jibla; school.js): its classroom doors are painted shut, a bar across each and a padlock on the bar;
// the lock catches the light now and then. Once the yard is clear, OPEN blinks over each door still shut; a door he has
// opened is a dark doorway with its leaf swung back. The children run for home, the first one out stopped by Yazeed to
// wave; while any child is out, Yazeed is drawn with his gun pointed at the ground (yazeed(), asked by render.js).
(function () {
  'use strict';
  var FS = null, IMI = null, cx = null;
  var BOARD_LIFT = 16, CRATE_H = 14;     // the billboard's picture this far off the ground; a set stands on a crate this high
  var cur = null, lastEnd = -999, lastSrc = -1;     // the line being said: by which screen, which line, from when
  var st = { L: null, at: [], s: null }; // each screen's place and the next of its lines, for the level being played

  function sheet() {
    if (!FS) FS = (typeof ATLAS !== 'undefined' && ATLAS.ibb) || null;
    if (!IMI) IMI = Render.image('ibb');
    return !!(FS && IMI);
  }
  function ispr(name, x, y, flip) {
    var f = FS.frames[name];
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    if (flip) {                                      // (turned about its anchor, as render.js's spr() does)
      cx.save(); cx.translate(x + 1, y); cx.scale(-1, 1);
      cx.drawImage(IMI, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
      cx.restore();
    } else cx.drawImage(IMI, f[0], f[1], f[2], f[3], x - f[4], y - f[5], f[2], f[3]);
  }
  function hash(a, b) { var t = (a * 374761393 + b * 668265263) | 0; t = Math.imul(t ^ (t >>> 13), 1274126177); return ((t ^ (t >>> 16)) >>> 0) / 4294967296; }
  // where each screen stands (and which of its lines comes next), worked out once for the level
  function screens(s) {
    var L = s.L;
    if (st.s !== s) { st.s = s; cur = null; lastEnd = -999; lastSrc = -1; }      // (a new game, or a continue: its clock starts again)
    if (st.L !== L) {
      st.L = L; st.at = [];
      (L.screens || []).forEach(function (q, i) {
        var plat = q.plat ? Sim._.platIndex(L, q.plat) : -1;
        st.at.push({ i: i, x: q.x, y: q.gy != null ? q.gy : Sim.surfaceY(L, plat, q.x), big: q.size === 'board', lines: q.lines || [], li: 0 });
      });
    }
    return st.at;
  }

  // the mouth: with the line, frame by frame, if this screen is the one talking; on its own (soundless) if not
  function mouthOf(s, o, K) {
    var sub = K.sub();
    if (cur && cur.src === o.i && sub && sub.id === cur.id) {
      var v = Sound.lineOf(cur.id), k = Math.floor((s.tick - cur.t0) * 15 / 60);
      return v && v.m && k < v.m.length ? +v.m.charAt(k) : 0;
    }
    var h = hash(Math.floor(s.tick / 5), o.i * 31 + 7);
    return h < 0.35 ? 0 : (h < 0.65 ? 1 : 2);
  }
  function blinkOf(s, o) { return (s.tick + o.i * 53) % 200 < 6; }
  function drawBoard(s, o, K) {
    var x0 = Math.round(o.x) - 72, gy = Math.round(o.y), y1 = gy - BOARD_LIFT, y0 = y1 - 96;
    // its two legs
    cx.fillStyle = '#120e0a'; cx.fillRect(x0 + 22, y1 + 3, 6, gy - y1 - 3); cx.fillRect(x0 + 116, y1 + 3, 6, gy - y1 - 3);
    cx.fillStyle = '#3a3e44'; cx.fillRect(x0 + 23, y1 + 3, 4, gy - y1 - 3); cx.fillRect(x0 + 117, y1 + 3, 4, gy - y1 - 3);
    cx.fillStyle = '#5a6068'; cx.fillRect(x0 + 23, y1 + 3, 1, gy - y1 - 3); cx.fillRect(x0 + 117, y1 + 3, 1, gy - y1 - 3);
    ispr('board', x0, y0);
    var m = mouthOf(s, o, K);
    if (m) ispr('board_m' + m, x0, y0);
    if (blinkOf(s, o)) ispr('board_bl', x0, y0);
    ispr('board_frame', x0, y0);
  }
  function drawTV(s, o, K) {
    var x = Math.round(o.x), gy = Math.round(o.y), base = gy - CRATE_H;
    ispr('crate', x, gy);
    var m = mouthOf(s, o, K);
    ispr(m === 0 && blinkOf(s, o) ? 'tvb' : 'tv' + m, x - 20, base - 26);       // (the screen's top left, inside the set)
    ispr('tv_box', x, base);
  }

  // ---------------------------------------------------------------- the school
  var DOOR_TOP = 140, DOOR_BASE = 170;            // the painted doors: 16 wide about their x, 30 tall (mock/stage_ibb_z2.py)
  function drawDoors(s, K) {
    var sc = s.school, tick = K.tick(), cam = s.cam, W = K.W();
    for (var i = 0; i < sc.doors.length; i++) {
      var d = sc.doors[i], x = Math.round(d.x);
      if (x + 14 < cam || x - 14 > cam + W) continue;
      if (d.open || sc.done) {                        // (a game started past the school finds them all open)
        // the dark of the room behind, and the iron leaf swung back against the wall (seen edge on)
        cx.fillStyle = '#120e0c'; cx.fillRect(x - 8, DOOR_TOP, 16, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#1c4a36'; cx.fillRect(x - 12, DOOR_TOP, 4, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#2e6a4e'; cx.fillRect(x - 12, DOOR_TOP, 1, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#0c0a08'; cx.fillRect(x - 8, DOOR_TOP, 16, 2);              // (the lintel's shadow)
        continue;
      }
      // the padlock on the bar (the painting's bar across the door at 152-153): its shackle round the bar, the brass body under it
      cx.fillStyle = '#1a1612'; cx.fillRect(x - 2, 149, 4, 1); cx.fillRect(x - 3, 150, 1, 4); cx.fillRect(x + 2, 150, 1, 4); cx.fillRect(x - 3, 154, 6, 5);
      cx.fillStyle = '#b4bac2'; cx.fillRect(x - 1, 150, 2, 1); cx.fillRect(x - 2, 151, 1, 3); cx.fillRect(x + 1, 151, 1, 3);
      cx.fillStyle = '#a07a1e'; cx.fillRect(x - 2, 155, 4, 3);
      cx.fillStyle = '#e8c45a'; cx.fillRect(x + 1, 155, 1, 2);
      cx.fillStyle = '#3a2a0c'; cx.fillRect(x - 1, 156, 1, 1);
      // now and then the light catches it (each door in its turn)
      var g = (tick + i * 47) % 150;
      if (g < 10) {
        var r = g < 3 || g > 7 ? 1 : 2;
        cx.fillStyle = '#fff6c8';
        cx.fillRect(x + 1, 155 - r, 1, 2 * r + 1); cx.fillRect(x + 1 - r, 155, 2 * r + 1, 1);
      }
      if (sc.clear && (tick >> 4) % 2) K.text('s_lav', T('OPEN'), x, DOOR_TOP - 9, 'c');
    }
  }
  function drawKids(s) {
    for (var i = 0; i < s.kids.length; i++) {
      var k = s.kids[i], pose = k.st === 'wave' ? 'wave' : (Math.floor(k.walkD / 6) % 2 ? 'run_b' : 'run_a');
      ispr('kid_' + k.name + '_' + pose, k.x, k.y, k.face < 0);
    }
  }
  // Yazeed, while a child is out: his gun pointed at the ground (render.js asks before it draws him; true: drawn here)
  function yazeed(s, p, legs, K) {
    if (!s.calm || !sheet()) return false;
    var gun = p.weapon === 'hmg' ? 'hmg' : 'side';
    if (legs === 'jump' || legs === 'fall') { K.spr('yazeed_' + legs + '_' + gun + '_ddiag', p.x, p.y, p.face < 0); return true; }
    if (legs !== 'stand' && legs !== 'pass' && legs !== 'run') return false;
    cx = K.ctx();
    ispr('ylow_' + legs + '_' + gun, p.x, p.y, p.face < 0);
    return true;
  }

  function scene(s, paused, K) {
    if ((!s.L.screens && !s.school) || !sheet()) return;
    cx = K.ctx();
    var cam = s.cam, W = K.W(), at = s.L.screens ? screens(s) : [];
    if (s.school) drawDoors(s, K);
    for (var i = 0; i < at.length; i++) {
      var o = at[i], hw = o.big ? 80 : 26;
      if (o.x + hw < cam || o.x - hw > cam + W) continue;
      if (o.big) drawBoard(s, o, K); else drawTV(s, o, K);
    }
    if (s.kids && s.kids.length) drawKids(s);
  }

  // ---------------------------------------------------------------- what they hear
  function talk(s, K) {
    if (!s.L.screens) return null;
    var p = s.p, at = screens(s), best = null, bd = 1e9;
    for (var i = 0; i < at.length; i++) {
      var o = at[i];
      if (!o.lines.length || !Sim.onScreen(s, o.x, -8)) continue;
      var d = Math.abs(o.x - p.x);
      if (d < bd) { bd = d; best = o; }
    }
    if (!best) return null;
    // (he pauses for breath between his phrases; a screen going round to the start of its lines again waits a little)
    if (best.i === lastSrc && best.li === 0 && s.tick - lastEnd < 110) return null;
    var id = best.lines[best.li], v = Sound.lineOf(id);
    best.li = (best.li + 1) % best.lines.length;
    cur = { src: best.i, id: id, t0: s.tick };
    lastEnd = s.tick + (v ? Math.round(v.at[1] * 60) : 120); lastSrc = best.i;
    return v ? { id: id, o: { pri: 0.5 } } : null;
  }
  function reset() { cur = null; lastEnd = -999; lastSrc = -1; st.L = null; st.at = []; st.s = null; }

  Render.bosses.ibb = { scene: scene, talk: talk, reset: reset, yazeed: yazeed };
})();
