// render_dhamar.js - Dhamar (Mission 5, the Wadi) on the screen (Render.bosses.dhamar), zones 1-3 as the test build
// (Khaled, 11 Nov 03:25), from the mock page he saw: its own pictures are a sheet of their own (art/out/dhamar.png,
// tools/dhamar_sprites.py); the Zanabeel's men, the 4x4 and the wheels are the atlas's.
// Qa' Jahran (dhamar.js): the convoy's lorries going the other way on the far lane, loaded with the drafted (a cook in his
//   pot helmet, the barber with his chair, a horse that refuses); at each checkpoint the queue of drafted men being counted
//   at the stamp window, hands up; the barrier across the near lane, lifted for the Zanabeel's goats as they trot through
//   and dropped again just before the 4x4 gets there (it goes through it); the notes blowing out across the road.
// Dhamar city (school.js): the recruiting office's three classrooms barred and padlocked, OPEN over them once the yard is
//   clear, the children running home with Yazeed's gun pointed at the ground while any is out (Ibb's, the same frames);
//   the Leader's silent screen on the office wall (a pointing finger; nothing breaks it, nothing is heard); the poster of
//   the Committee's laughing face over the stamp window (no text), stamped with a red mark once the teacher is free; the
//   teacher drafted as his pupils' sergeant (his cap too big, the whistle), tied by the office, then waving his pupils
//   home and going after them.
// Hammam Ali (rally.js, its vote): the steam over the hot pools; the convoy parked; the Committee at his table with its
//   microphones, convening, moving, seconding, carrying alone (his lines in turn when he is the voice nearest Yazeed:
//   talk()); the gathering's hands up through the steam; the hand that asks about the wages, the laugh, a coin out of his
//   jacket ringing on the stone; Yazeed's word; the vote on whether Yazeed is there, denied, the stamp; the gathering
//   drafted in one motion and filing off to the lorries after him. Shots pass all of them: they are in nothing the game
//   hits.
// And men the gas torch caught (sim.js, scorchRun): blackened, the whites of their eyes, their hair smoking, running off.
(function () {
  'use strict';
  var FS = null, IMD = null, cx = null;
  var DOOR_TOP = 140, DOOR_BASE = 170;            // the painted classroom doors: 16 wide about their x (mock/stage_dhamar.py)
  var FAR = 177, QUEUE_Y = 169;                   // the far lane's ground line; where the queue stands (the verge)
  var LORRY_V = 118;                              // the convoy's lorries, coming down the far lane, px a second
  var cur = null, talkEnd = -999, talkLi = 0, st = { s: null, freedAt: -1, coins: [], flying: [] };
  var GATHER_WHO = 'A HAND IN THE STEAM';

  function sheet() {
    if (!FS) FS = (typeof ATLAS !== 'undefined' && ATLAS.dhamar) || null;
    if (!IMD) IMD = Render.image('dhamar');
    return !!(FS && IMD);
  }
  function on(s) { return s.L.art === 'dhamar'; }
  function dspr(name, x, y, flip, alpha) {
    var f = FS.frames[name];
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    if (alpha != null && alpha < 1) cx.globalAlpha = alpha;
    if (flip) {
      cx.save(); cx.translate(x + 1, y); cx.scale(-1, 1);
      cx.drawImage(IMD, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
      cx.restore();
    } else cx.drawImage(IMD, f[0], f[1], f[2], f[3], x - f[4], y - f[5], f[2], f[3]);
    if (alpha != null && alpha < 1) cx.globalAlpha = 1;
  }
  function fresh(s) {
    if (st.s !== s) { st.s = s; cur = null; talkEnd = -999; talkLi = 0; st.freedAt = -1; st.coins = []; st.flying = []; }      // (a new game, or a continue)
  }
  function seen(s, x, pad, K) { return x > s.cam - pad && x < s.cam + K.W() + pad; }

  // ---------------------------------------------------------------- Qa' Jahran
  // the convoy: lorry k set off from L.convoy.from + k * every and comes down the far lane at LORRY_V; its load by k
  function drawConvoy(s, K) {
    var C = s.L.convoy, n = Math.floor((C.to - C.from) / C.every) + 1, rig = 21;
    for (var k = 0; k < n; k++) {
      var x = C.from + k * C.every + 300 - LORRY_V * s.time;
      if (!seen(s, x, 90, K)) continue;
      var bob = (Math.floor(s.time * 7 + k) % 4 === 0) ? 1 : 0, y = FAR - bob, bed = y - 15;
      // the load first, the slats in front of it (facing left: the lorry is flipped, its cab at the left)
      // (the drafted: men of the plateau in their own clothes, a cook in his pot helmet, the barber with his chair, the horse)
      var kind = k % 3;
      if (kind === 0) { K.spr('cook_up_stand', x + 10, bed + 2, true); dspr('horse', x + 34, bed - 11, true); dspr('g0_hands', x - 6, bed + 2, true); }
      else if (kind === 1) { dspr('g1_stand', x + 4, bed + 2, true); dspr('chair', x + 22, bed - 16); dspr('g3_hands', x + 40, bed + 2, true); }
      else { dspr('g4_stand', x - 2, bed + 2, true); K.spr('cook_up_stand', x + 20, bed + 2, true); dspr('g6_hands', x + 42, bed + 2, true); }
      dspr('lorry', x, y, true);
      var wn = 'wheel' + (3 - (((Math.floor(-LORRY_V * s.time / 2.4) % 4) + 4) % 4));
      K.spr(wn, x + 42, y - 10); K.spr(wn, x + 20, y - 10); K.spr(wn, x - 48, y - 10);
    }
  }
  // a checkpoint's queue: men of the plateau in their own clothes (not the Zanabeel's), waiting to be counted at the stamp
  // window, the one at the front with his hands up; and the goats it lets through
  function drawCheckpoint(s, cp, i, K) {
    if (!seen(s, cp.hut, 140, K)) return;
    var tk = K.tick();
    for (var q = 3; q >= 0; q--) {
      var qx = cp.hut - 22 - q * 14, g = (q + i * 2) % 7;
      // (the one at the window steps up and back as he is counted; the one asking leans in)
      var dx = q === 0 && (tk >> 5) % 2 ? 2 : 0;
      var pose = q === 0 ? 'hands' : (q === 1 && (cp.st === 'ask' || cp.st === 'laugh') && g === 2 ? 'ask' : 'stand');
      if (!FS.frames['g' + g + '_' + pose]) pose = 'stand';
      dspr('g' + g + '_' + pose, qx + dx, QUEUE_Y, false);
    }
    // the goats: through under the lifted barrier while the 4x4 is still a way off
    var c = s.car, d = c ? cp.barrier - c.x : 999;
    if (d > 150 && d < 420) {
      var u = (420 - d) / 270;
      for (var g = 0; g < 3; g++) dspr(((tk >> 3) + g) % 2 ? 'goat1' : 'goat2', cp.barrier - 30 + u * 70 + g * 10, FAR - (g % 2), false);
    } else if (d <= 150) {
      for (var g2 = 0; g2 < 3; g2++) dspr('goat1', cp.barrier + 44 + g2 * 11, FAR - 6 - (g2 % 2), false);      // (grazing on the verge beyond)
    }
  }
  // the barrier: a striped pole on its post at the near end, its arm out along the lane (the 4x4 meets the post first);
  // it pivots up at the post
  function pole(x0, y0, ang, len, broken) {
    var ca = Math.cos(ang), sa = Math.sin(ang);
    for (var k = 0; k < len; k++) {
      var px = Math.round(x0 + ca * k), py = Math.round(y0 - sa * k);
      cx.fillStyle = (Math.floor(k / 5) % 2) ? '#f2eee4' : '#c4281c';
      cx.fillRect(px, py, 1, 2);
    }
    if (broken) { cx.fillStyle = '#4a3a2a'; cx.fillRect(Math.round(x0 + ca * len) - 1, Math.round(y0 - sa * len) - 1, 2, 3); }
  }
  function drawBarrier(s, o, K) {
    if (!seen(s, o.x, 60, K)) return;
    var c = s.car, d = c ? o.x - c.x : 0, y = o.y, px = o.x - 6;
    cx.fillStyle = '#1e1c20'; cx.fillRect(px - 2, y - 24, 5, 24);
    cx.fillStyle = '#5a5862'; cx.fillRect(px - 1, y - 23, 3, 23);
    cx.fillStyle = '#c4281c'; cx.fillRect(px - 1, y - 23, 3, 2);
    if (o.st === 'broken') {
      pole(px + 1, y - 17, -0.2, 9, true);                                    // the stub left on the post
      return;
    }
    // lifted for the goats, while the 4x4 is a way off; dropping as it comes; down
    var ang = d > 170 ? 1.25 : (d > 140 ? 1.25 * (d - 140) / 30 : 0);
    pole(px + 1, y - 17, ang, 44, false);
  }
  // the arm the 4x4 broke off, turning over in the air and coming down behind it
  function drawFlying(s, paused) {
    for (var i = st.flying.length - 1; i >= 0; i--) {
      var f = st.flying[i];
      if (!paused) { f.t++; f.vy += 640 / 60; f.x += f.vx / 60; f.y += f.vy / 60; f.ang += f.spin; }
      if (f.t > 70 || f.y > 230) { st.flying.splice(i, 1); continue; }
      pole(f.x - Math.cos(f.ang) * 17, f.y + Math.sin(f.ang) * 17, f.ang, 35, false);
    }
  }
  // a note, in the air (turning over as it flutters) or lying on the road; the game's own paper, no figures, no script
  function drawNote(n, tk) {
    var x = Math.round(n.x), y = Math.round(n.y);
    if (n.st === 'lie') {
      cx.fillStyle = '#2e4a34'; cx.fillRect(x - 3, y - 1, 7, 2);
      cx.fillStyle = '#9cc49a'; cx.fillRect(x - 2, y - 1, 5, 1);
      return;
    }
    var ph = Math.sin(n.t / 5 + n.ph), h = Math.abs(ph) < 0.35 ? 1 : 4;
    cx.fillStyle = '#2e4a34'; cx.fillRect(x - 3, y - h, 7, h + (h > 1 ? 1 : 0));
    if (h > 1) { cx.fillStyle = '#b8dcb0'; cx.fillRect(x - 2, y - h + 1, 5, h - 1); cx.fillStyle = '#5e8a62'; cx.fillRect(x, y - h + 1, 1, h - 1); }
    else { cx.fillStyle = '#d8f0d0'; cx.fillRect(x - 2, y - 1, 5, 1); }
  }

  // ---------------------------------------------------------------- Dhamar city: the recruiting office
  function drawDoors(s, K, hints) {
    var sc = s.school, tick = K.tick();
    for (var i = 0; i < sc.doors.length; i++) {
      var d = sc.doors[i], x = Math.round(d.x);
      if (!seen(s, x, 16, K)) continue;
      if (hints) {
        if (!d.open && !sc.done && sc.clear && (tick >> 4) % 2) K.text('s_lav', T('OPEN'), x, DOOR_TOP - 9, 'c');
        continue;
      }
      if (d.open || sc.done) {
        cx.fillStyle = '#120e0c'; cx.fillRect(x - 8, DOOR_TOP, 16, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#1c4a36'; cx.fillRect(x - 12, DOOR_TOP, 4, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#2e6a4e'; cx.fillRect(x - 12, DOOR_TOP, 1, DOOR_BASE - DOOR_TOP);
        cx.fillStyle = '#0c0a08'; cx.fillRect(x - 8, DOOR_TOP, 16, 2);
        continue;
      }
      // the bar across the door, and the padlock on it
      cx.fillStyle = '#1a1612'; cx.fillRect(x - 10, 151, 20, 4);
      cx.fillStyle = '#6a6e74'; cx.fillRect(x - 9, 152, 18, 2);
      cx.fillStyle = '#9ca2a8'; cx.fillRect(x - 9, 152, 18, 1);
      cx.fillStyle = '#1a1612'; cx.fillRect(x - 2, 149, 4, 1); cx.fillRect(x - 3, 150, 1, 4); cx.fillRect(x + 2, 150, 1, 4); cx.fillRect(x - 3, 154, 6, 5);
      cx.fillStyle = '#b4bac2'; cx.fillRect(x - 1, 150, 2, 1); cx.fillRect(x - 2, 151, 1, 3); cx.fillRect(x + 1, 151, 1, 3);
      cx.fillStyle = '#a07a1e'; cx.fillRect(x - 2, 155, 4, 3);
      cx.fillStyle = '#e8c45a'; cx.fillRect(x + 1, 155, 1, 2);
      var g = (tick + i * 47) % 150;
      if (g < 10) {
        var r = g < 3 || g > 7 ? 1 : 2;
        cx.fillStyle = '#fff6c8';
        cx.fillRect(x + 1, 155 - r, 1, 2 * r + 1); cx.fillRect(x + 1 - r, 155, 2 * r + 1, 1);
      }
    }
  }
  function drawOffice(s, K) {
    var O = s.L.office;
    if (!O || !seen(s, O.screen[0], 80, K)) return;
    dspr('leader', O.screen[0], O.screen[1]);
    // (a faint roll of the picture now and then: it is on, and says nothing)
    var tk = K.tick();
    if (tk % 240 < 20) { cx.fillStyle = 'rgba(200,220,210,0.10)'; cx.fillRect(O.screen[0] + 3, O.screen[1] + 3 + ((tk % 240) * 2) % 30, 48, 2); }
    dspr('poster', O.poster[0], O.poster[1]);
    // freed, the teacher stamps it: a red mark across the face (no word on it)
    if (st.freedAt >= 0 && s.tick - st.freedAt > 100) {
      var px = O.poster[0] + 4, py = O.poster[1] + 7;
      cx.fillStyle = 'rgba(196,30,22,0.88)';
      cx.fillRect(px, py, 18, 2); cx.fillRect(px, py + 8, 18, 2); cx.fillRect(px, py, 2, 10); cx.fillRect(px + 16, py, 2, 10);
      for (var k = 0; k < 12; k++) cx.fillRect(px + 3 + k, py + 7 - Math.floor(k / 2), 1, 1);
    }
  }
  function teacherFreed(s) {
    var Sc = s.L.school;
    if (!Sc || st.freedAt >= 0) return;
    for (var i = 0; i < s.props.length; i++) { var o = s.props[i]; if (o.k === 'detainee' && Math.abs(o.px - Sc.teacher) <= 2 && o.st !== 'tied') { st.freedAt = s.tick; return; } }
    if (s.stats.rescued && s.stats.rescued.indexOf(Sc.teacher) >= 0) st.freedAt = s.tick - 200;       // (freed before a continue)
  }
  function drawKids(s) {
    for (var i = 0; i < s.kids.length; i++) {
      var k = s.kids[i], pose = k.st === 'wave' ? 'wave' : (Math.floor(k.walkD / 6) % 2 ? 'run_b' : 'run_a');
      dspr('kid_' + k.name + '_' + pose, k.x, k.y, k.face < 0);
    }
  }

  // ---------------------------------------------------------------- Hammam Ali: the vote
  var HIS = { cm_minutes: 1, cm_favour: 1, cm_voted: 1, cm_laugh: 1, cm_noted: 1, cm_denied: 1, cm_drafted: 1 };
  function mouthOf(s, K) {
    var sub = K.sub();
    if (cur && sub && sub.id === cur.id) {
      var v = Sound.lineOf(cur.id), k = Math.floor((s.tick - cur.t0) * 15 / 60);
      return v && v.m && k < v.m.length ? +v.m.charAt(k) : 0;
    }
    return 0;
  }
  // his mouth going with whatever he is saying now (his lines at the end of the vote are main.js's, not talk()'s)
  function mouthOn(s, K, tk) {
    var sub = K.sub();
    if (sub && HIS[sub.id]) { var v = Sound.lineOf(sub.id), k = Math.floor((s.tick - (sub.t0 || s.tick)) * 15 / 60); if (v && v.m) return k < v.m.length && +v.m.charAt(k) ? 'cm_speak' : 'cm_stand'; }
    return (tk >> 2) % 2 ? 'cm_speak' : 'cm_stand';
  }
  // the line being heard now, if it is one of the vote's (talk() started it), else null
  function saying(s, K) { var sub = K.sub(); return cur && sub && sub.id === cur.id ? cur.id : null; }
  function drawVote(s, K) {
    var Lg = s.L.stage, r = s.rally, tk = K.tick();
    if (!r || !seen(s, (Lg.x0 + Lg.x1) / 2, 320, K)) return;
    // the convoy parked behind the gathering
    (s.L.parked || []).forEach(function (x, k) {
      dspr('lorry', x, Lg.deck - 2 - k, false);
      var wn = 'wheel0';
      K.spr(wn, x - 42, Lg.deck - 12 - k); K.spr(wn, x - 20, Lg.deck - 12 - k); K.spr(wn, x + 48, Lg.deck - 12 - k);
    });
    var line = r.st === 'speech' ? saying(s, K) : null;
    // the coins out of his jacket, on the stone, each with its ring as it lands
    for (var c = 0; c < st.coins.length; c++) {
      var cn = st.coins[c], a = s.tick - cn.t;
      if (a < 0) continue;
      var cy = a < 14 ? cn.y0 + (Lg.deck - 1 - cn.y0) * (a / 14) * (a / 14) : Lg.deck - 1;
      cx.fillStyle = '#7a5208'; cx.fillRect(Math.round(cn.x) - 1, Math.round(cy) - 1, 3, 2);
      cx.fillStyle = '#ffe264'; cx.fillRect(Math.round(cn.x), Math.round(cy) - 1, 1, 1);
      if (a >= 14 && a < 40) {
        var rr = 2 + (a - 14) * 0.5;
        cx.strokeStyle = 'rgba(255,240,180,' + (0.8 - (a - 14) / 32).toFixed(2) + ')'; cx.lineWidth = 1;
        cx.beginPath(); cx.ellipse(cn.x + 0.5, Lg.deck - 0.5, rr, rr / 3, 0, 0, Math.PI * 2); cx.stroke();
      }
    }
    // the gathering: facing him while the meeting sits; hands up for his motions and for being drafted; filing off after
    var walking = r.st === 'walk' || r.st === 'gone', off = walking ? r.runD : 0;
    for (var i = 0; i < Lg.seats.length; i++) {
      var sx = Lg.seats[i][0] + off, sy = Lg.seats[i][1], pose = 'stand', face = -1;
      if (r.st === 'gone' && sx > s.cam + K.W() + 30) continue;
      if (r.st === 'speech' && line === 'cm_favour') pose = 'hands';
      if (r.st === 'speech' && line === 'grunt_wages' && i === Lg.asker) pose = 'ask';
      if (r.st === 'draft') { pose = r.t > 40 && r.t < 130 ? 'hands' : 'stand'; face = r.t < 130 ? -1 : 1; }
      if (walking) { pose = 'file'; face = 1; sy -= Math.floor((r.runD + i * 5) / 6) % 2; }
      dspr('g' + i + '_' + pose, sx, sy, face < 0);
    }
    // his table, and him: speaking, the vote (both hands up), the laugh; stopped by Yazeed's word; his own vote on whether
    // Yazeed is there; drafting them all; walking off after them to the lorries
    dspr('cm_table', Lg.podium, Lg.deck);
    if (r.st === 'gone') return;
    var nm = 'cm_stand';
    if (r.st === 'speech') {
      if (line === 'cm_favour') nm = 'cm_vote';
      else if (line === 'cm_laugh') nm = 'cm_laugh' + [1, 2, 3, 2][Math.floor(s.tick / 5) % 4];
      else if (line && HIS[line]) nm = mouthOf(s, K) ? 'cm_speak' : 'cm_stand';
    } else if (r.st === 'heard') nm = r.t < 30 ? 'cm_speak' : 'cm_stand';
    else if (r.st === 'deny') nm = r.t < 60 ? 'cm_vote' : (r.t < 200 ? mouthOn(s, K, tk) : 'cm_stand');
    else if (r.st === 'draft') nm = r.t < 110 ? mouthOn(s, K, tk) : 'cm_stand';
    else if (r.st === 'walk') nm = Math.floor(r.runD / 7) % 2 ? 'cm_walk1' : 'cm_walk2';
    dspr(nm, r.x, r.y, false);
    // the stamp coming down: a red flash on the table
    if ((r.st === 'deny' && r.t >= 200 && r.t < 208) || (r.st === 'draft' && r.t >= 64 && r.t < 72)) { cx.fillStyle = '#e8402c'; cx.fillRect(Lg.podium + 6, Lg.deck - 15, 5, 2); }
  }
  // the steam over the pools (and over the vote), in front of whoever stands in it: the atlas's columns of steam, faint
  function drawSteam(s, K) {
    var tk = K.tick(), list = s.L.steam || [];
    for (var i = 0; i < list.length; i++) {
      var a = list[i][0], b = list[i][1];
      if (b < s.cam - 40 || a > s.cam + K.W() + 40) continue;
      for (var x = a + 14, k = 0; x < b - 10; x += 34, k++) {
        var al = 0.20 + 0.08 * Math.sin(tk / 40 + k * 1.7 + i);
        K.spr('steam' + (((tk >> 3) + k) % 3), x + Math.round(Math.sin(tk / 60 + k) * 3), 196, (k + i) % 2 === 1, al);
      }
    }
  }

  // ---------------------------------------------------------------- the hooks render.js calls
  function ground(s, paused, K) {
    if (!on(s) || !sheet()) return;
    cx = K.ctx();
    fresh(s);
    teacherFreed(s);
    var L = s.L, i;
    if (s.dham) {
      if (L.convoy && s.zone === 0) drawConvoy(s, K);
      for (i = 0; i < s.dham.cps.length; i++) drawCheckpoint(s, s.dham.cps[i], i, K);
      for (i = 0; i < s.props.length; i++) if (s.props[i].k === 'barrier' && !s.props[i].gone) drawBarrier(s, s.props[i], K);
      for (i = 0; i < s.dham.notes.length; i++) if (s.dham.notes[i].st === 'lie') drawNote(s.dham.notes[i], K.tick());
    }
    if (s.school) drawDoors(s, K, false);
    drawOffice(s, K);
    if (L.stage) drawVote(s, K);
  }
  function scene(s, paused, K) {
    if (!on(s) || !sheet()) return;
    cx = K.ctx();
    if (s.school) drawDoors(s, K, true);
    if (s.kids && s.kids.length) drawKids(s);
    if (s.dham) for (var i = 0; i < s.dham.notes.length; i++) if (s.dham.notes[i].st === 'fly') drawNote(s.dham.notes[i], K.tick());
    if (st.flying.length) drawFlying(s, paused);
  }
  function post(s, paused, K) {
    if (!on(s)) return;
    cx = K.ctx();
    drawSteam(s, K);
  }
  // Yazeed, while a child is out: his gun pointed at the ground (the torch's nozzle too)
  function yazeed(s, p, legs, K) {
    if (!on(s) || !s.calm || !sheet()) return false;
    var gun = p.weapon === 'hmg' ? 'hmg' : 'side';
    cx = K.ctx();
    if (legs === 'jump' || legs === 'fall') { K.spr('yazeed_' + legs + '_' + gun + '_ddiag', p.x, p.y, p.face < 0); return true; }
    if (legs !== 'stand' && legs !== 'pass' && legs !== 'run') return false;
    dspr('ylow_' + legs + '_' + gun, p.x, p.y, p.face < 0);
    return true;
  }
  // the teacher, drafted as his pupils' sergeant: tied by the office; freed, both hands up to his pupils; then after them
  function detainee(s, o, K) {
    var Sc = s.L.school;
    if (!on(s) || !Sc || Math.abs(o.px - Sc.teacher) > 2 || !sheet()) return false;
    cx = K.ctx();
    if (o.st === 'tied') dspr('sgt_tied', o.x, o.y);
    else if (o.st === 'freed') dspr('sgt_wave', o.x, o.y);
    else dspr((Math.floor(o.t / 7) % 2) ? 'sgt_walk1' : 'sgt_walk2', o.x, o.y, true);
    return true;
  }
  // a man the torch caught: blackened, the whites of his eyes, his hair smoking, running for it
  function scorched(s, e, K) {
    if (!sheet()) return false;
    cx = K.ctx();
    var base = e.k === 'rifle' ? 'rifle_' + (['worried', 'youth', 'angry', 'qat'].indexOf(e.look) >= 0 ? e.look : 'worried') : (e.k === 'cook' ? 'cook' : (e.k === 'bomber' ? 'bomber' : 'door'));
    var nm = 'sc_' + base + (Math.floor(e.walkD / 8) % 2 ? '_pass' : '_run');
    if (!FS.frames[nm]) return false;
    dspr(nm, e.x, e.y, e.face < 0);
    if (K.tick() % 4 === 0) K.part('wisp', e.x - e.face * 3 + (Math.random() - 0.5) * 6, e.y - 36, { life: 26, vx: -e.face * 20 + (Math.random() - 0.5) * 10, vy: -30 - Math.random() * 20 });
    return true;
  }
  // what a moment of Dhamar's looks like
  function misc(e, s, K) {
    if (!on(s)) return false;
    var k;
    if (e.t === 'bar_smash') {
      // the pole snaps: its arm goes up over the 4x4, turning
      st.flying.push({ x: e.x + 14, y: e.y - 18, vx: e.how === 'ram' ? 150 : 70 * (e.dir || 1), vy: -230, ang: 0, spin: 0.28, t: 0 });
      for (k = 0; k < 6; k++) K.part('clod', e.x + (Math.random() - 0.5) * 10, e.y - 14 - Math.random() * 6, { life: 24, vx: 40 + Math.random() * 140, vy: -80 - Math.random() * 100, g: 600, col: k % 2 ? '#c4281c' : '#f2eee4' });
      K.pop(e.x, e.y - 40, String(e.pts));
      K.shake(4);
      return true;
    }
    if (e.t === 'note_back') { K.pop(e.x, e.y - 18, '+' + e.pts, 's_lav'); return true; }
    if (e.t === 'cp_laugh') { K.shake(1); return true; }
    return e.t === 'cp_ask' || e.t === 'rally_deny' || e.t === 'rally_draft' || e.t === 'rally_walk';
  }
  // the vote's lines, in turn, while he is in the picture and holding his meeting (main.js says them when nobody else is
  // talking); after the laugh, the coin (main.js rings it as the line ends: o.coin)
  function talk(s, K) {
    if (!on(s) || !s.rally || s.rally.st !== 'speech') return null;
    var Lg = s.L.stage, r = s.rally, lines = Lg.lines, p = s.p;
    fresh(s);
    if (!lines || !lines.length || !Sim.onScreen(s, r.x, -8) || Math.abs(r.x - p.x) > 360) return null;
    if (s.tick - talkEnd < (talkLi === 0 ? 150 : 22)) return null;
    var id = lines[talkLi], v = Sound.lineOf(id);
    talkLi = (talkLi + 1) % lines.length;
    cur = { id: id, t0: s.tick };
    talkEnd = s.tick + (v ? Math.round(v.at[1] * 60) : 120);
    if (id === 'cm_laugh') st.coins.push({ x: r.x + 7, y0: r.y - 20, t: talkEnd - 4 });
    if (st.coins.length > 5) st.coins.shift();
    if (!v) return null;
    var o = { pri: 0.5 };
    if (id === 'grunt_wages') o.who = GATHER_WHO;
    if (id === 'cm_laugh') o.coin = { x: r.x + 7 };
    return { id: id, o: o };
  }
  function reset() { cur = null; talkEnd = -999; talkLi = 0; st.s = null; st.freedAt = -1; st.coins = []; st.flying = []; }

  Render.bosses.dhamar = { ground: ground, scene: scene, post: post, talk: talk, reset: reset, yazeed: yazeed, detainee: detainee, scorched: scorched, misc: misc };
})();
