// render_spokesman.js - how Brigadier Breaking's fight on Sumara pass looks (spokesman.js), and what comes after it; it
// plugs into render.js as Render.bosses.spokesman.
//   The lookout: five podiums, each with its screen on a pole behind it. The screens show him: mouthing soundlessly
//   before the fight; speaking with him (his mouth with his line) while he speaks; frozen on his face while he is
//   stunned; snow on a podium he has been cut off at; dark but for his own at the last podium, in the dark; then, once he
//   is caught, the rendered him (the ear, two Yemens), and at the end, nothing.
//   Him: at his podium (the podium in front of him), its microphone ahead of him toward Yazeed, or shot off it; stunned
//   with a hand to his ear; shouting with an ear ringing (two podiums left); reading by torchlight (the last); leaping
//   between podiums and dashing along the floor; tied up in his own cable. The feedback running along the ground.
//   The dark at the last podium: everything dimmed but his screen, his torch and what it lights; shots and flashes
//   still show.
//   The reveal: a close-up of the screen for a moment (the billboard's size), the van's side door sliding open on the
//   back room (the rack's lights, the red button), the three technicians, the rack smashed; the cloud clearing onto the
//   Dhamar plateau (a picture of its own, behind the lookout).
(function () {
  'use strict';
  var SP = Sim.SP, X = Sim.ext.spokesman;
  var FS = null, IMI = null, PLATEAU = null, cx = null;
  var PS_LIFT = 46;                    // a podium's screen: its mount's foot this far above the floor
  var mics = [], closeT = 0, sayKey = null, sayT = 0, said = {}, wasSt = '';
  var SAY = { mic: 'SHOOT HIS MICROPHONE!', hit: 'NOW! HIT HIM!', wave: 'JUMP IT!', dash: 'JUMP HIM!', cables: 'FOLLOW THE CABLES', rack: 'SMASH THE RACK!' };

  function sheet() {
    if (!FS) FS = (typeof ATLAS !== 'undefined' && ATLAS.ibb) || null;
    if (!IMI) IMI = Render.image('ibb');
    return !!(FS && IMI);
  }
  function ispr(name, x, y, flip) {
    var f = FS.frames[name];
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    if (flip) {
      cx.save(); cx.translate(x + 1, y); cx.scale(-1, 1);
      cx.drawImage(IMI, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
      cx.restore();
    } else cx.drawImage(IMI, f[0], f[1], f[2], f[3], x - f[4], y - f[5], f[2], f[3]);
  }
  // the same, turned about its anchor (his feet) by ang
  function isprRot(name, x, y, ang, flip) {
    var f = FS.frames[name];
    if (!f) return;
    cx.save(); cx.translate(Math.round(x), Math.round(y)); cx.rotate(ang);
    if (flip) cx.scale(-1, 1);
    cx.drawImage(IMI, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
    cx.restore();
  }
  function hash(a, b) { var t = (a * 374761393 + b * 668265263) | 0; t = Math.imul(t ^ (t >>> 13), 1274126177); return ((t ^ (t >>> 16)) >>> 0) / 4294967296; }
  function mine(s) { return s.boss && s.boss.kind === 'spokesman' ? s.boss : null; }

  // his mouth: with the line being said (if it is one of his), frame by frame; otherwise on its own
  function lineMouth(s, K, pre) {
    var sub = K.sub();
    if (sub && sub.id && sub.id.indexOf(pre) === 0 && sub.t0 != null) {
      var v = Sound.lineOf(sub.id), k = Math.floor((s.tick - sub.t0) * 15 / 60);
      if (v && v.m) return k < v.m.length ? +v.m.charAt(k) : 0;
    }
    return -1;
  }
  function idleMouth(s, i) { var h = hash(Math.floor(s.tick / 5), 40 + i * 31); return h < 0.35 ? 0 : (h < 0.65 ? 1 : 2); }

  // ---------------------------------------------------------------- the podium screens
  function screenPic(s, b, i, K) {
    var spk = s.spk, pod = spk.pods[i], tick = K.tick();
    if (spk.off) return 'dark';
    if (spk.fake) {
      var fm = lineMouth(s, K, 'sp_');
      if (fm < 0) fm = 0;
      return fm === 0 && (tick + i * 37) % 170 < 6 ? 'pfb' : 'pf' + fm;
    }
    if (b && (b.st === 'dying' || b.st === 'dead')) return 'snow';
    var stunned = b && b.st === 'stun';
    if (!pod.mic && !(stunned && b.pod === i) && !(b && b.st === 'fix' && b.pod === i)) return 'snow';
    if (stunned) return 'frozen';
    if (b && spk.dark > 0.5 && b.pod !== i) return 'dark';
    if (b && b.st === 'speak') { var m = lineMouth(s, K, 'sp_'); return 'ps' + (m < 0 ? idleMouth(s, 0) : m); }
    if (b) return (tick + i * 53) % 200 < 6 ? 'psb' : 'ps0';
    var mm = idleMouth(s, i);
    return mm === 0 && (tick + i * 53) % 200 < 6 ? 'psb' : 'ps' + mm;
  }
  function drawScreen(s, b, i, K) {
    var A = s.L.arena, x = A.podiums[i], y = A.y, top = y - PS_LIFT - 40, pic = screenPic(s, b, i, K);
    // the pole behind the podium, its feet on the gravel
    cx.fillStyle = '#16181c'; cx.fillRect(x - 1, top + 40, 3, y - top - 40); cx.fillRect(x - 6, y - 1, 13, 1); cx.fillRect(x - 4, y - 2, 9, 1);
    cx.fillStyle = '#4a4e56'; cx.fillRect(x - 1, top + 40, 1, y - top - 41);
    if (pic === 'dark') { cx.fillStyle = '#08090c'; cx.fillRect(x - 24, top + 2, 48, 32); }
    else if (pic === 'snow') ispr('psn' + ((K.tick() >> 2) & 1), x - 24, top + 2);
    else if (pic === 'frozen') {
      ispr('ps1', x - 24, top + 2);
      if ((K.tick() >> 4) % 2) { cx.fillStyle = '#fafafa'; cx.fillRect(x - 21, top + 5, 2, 6); cx.fillRect(x - 17, top + 5, 2, 6); }
    } else ispr(pic, x - 24, top + 2);
    ispr('ps_box', x - 26, top);
  }

  // ---------------------------------------------------------------- him
  function himFrame(s, b, K) {
    var t = b.stT, tick = K.tick();
    switch (b.st) {
      case 'stun': return 'spk_stun';
      case 'fix': return (t >> 3) % 2 ? 'spk_stun' : 'spk_bl';
      case 'dying': return t < SP.REEL ? ((t >> 2) % 2 ? 'spk_stun' : 'spk_h2') : 'spk_caught';
      case 'dead': return 'spk_caught';
    }
    var m = b.st === 'speak' ? lineMouth(s, K, 'sp_') : 0;
    if (m < 0) m = idleMouth(s, 7);
    if (b.phase >= 3) return 'spk_read' + (m > 0 ? 1 : 0);
    if (b.phase === 2) return 'spk_h' + m;
    return m === 0 && (tick % 180) < 6 ? 'spk_bl' : 'spk_m' + m;
  }
  // at his podium (drawn on the picture, before anyone in front of it), the podiums over him
  function drawHimAtPodium(s, b, K) {
    var name = himFrame(s, b, K), fl = b.face < 0;
    if (b.st === 'dying' || b.st === 'dead') { drawCaught(s, b, K); return; }
    ispr(name, b.x, b.y, fl);
    if (b.phase === 2 && (b.st === 'speak' || b.st === 'ready' || b.st === 'after')) {
      // the ring round his ear
      var r = (K.tick() >> 3) % 2;
      ispr('spk_ring', b.x + (fl ? 9 : -9) + (r ? (fl ? 1 : -1) : 0), b.y - 25 - r, fl);
    }
  }
  // caught (Khaled, 30 Oct 13:56: his going down was too quick): he reels from the last shot, then spins round and round as
  // his own cable winds about him (more turns of it each time), then goes over backwards about his feet, away from Yazeed,
  // and lies there tied up behind his podium
  function drawCaught(s, b, K) {
    var t = b.st === 'dead' ? SP.DIE : b.stT, x = Math.round(b.x), y = Math.round(b.y), fl = b.face < 0, k;
    if (t < SP.REEL) { ispr(himFrame(s, b, K), x + ((t >> 1) % 2 ? 1 : -1), y, fl); return; }
    if (t < SP.SPIN) {
      var turns = Math.min(5, 1 + Math.floor((t - SP.REEL) / 18)), round = Math.floor((t - SP.REEL) / 7) % 2 === 1;
      ispr('spk_caught', x, y, round ? !fl : fl);
      cx.fillStyle = '#16161a';
      for (k = 0; k < turns; k++) cx.fillRect(x - 7, y - 30 + k * 4, 14, 1);
      return;
    }
    var u = Math.min(1, (t - SP.SPIN) / SP.TOPPLE), ang = u * u * Math.PI / 2 * (fl ? 1 : -1);
    isprRot('spk_caught', x, y - Math.round(7 * u * u), ang, fl);
    if (b.st === 'dead' && !b.captured && (K.tick() >> 4) % 2) K.text('s_lav', T('WALK IN'), x - (fl ? -18 : 18), y - 30, 'c');
  }
  function drawPodiums(s, b, K) {
    var A = s.L.arena, P = s.spk.pods;
    for (var i = 0; i < P.length; i++) {
      // (a podium faces Yazeed; the microphone ahead of it)
      var face = s.p.x < P[i].x ? -1 : 1;
      if (b && b.pod === i && X.atPodium(b)) face = b.face;
      ispr(P[i].mic || (b && b.st === 'fix' && b.pod === i && b.stT > 50) ? 'podium' : 'podium_bare', P[i].x, A.y, face < 0);
    }
  }
  function drawMics(paused) {
    for (var i = mics.length - 1; i >= 0; i--) {
      var m = mics[i];
      if (!paused) { m.t++; m.vy += 520 / 60; m.x += m.vx / 60; m.y += m.vy / 60; if (m.y > m.floor) { m.y = m.floor; m.vy *= -0.3; m.vx *= 0.6; } }
      ispr('mic_off', m.x, m.y, m.vx < 0);
      if (m.t > 160) mics.splice(i, 1);
    }
  }

  // ---------------------------------------------------------------- the van's back room
  function drawVan(s, K) {
    var V = s.L.arena.van, u = s.spk.van.open, smashed = s.spk.van.smashed, tick = K.tick();
    if (u <= 0) return;
    var x0 = V.door[0], x1 = V.door[1], top = V.roof + 3, sill = V.sill - 1, w = x1 - x0, slid = Math.round(w * u);
    // the inside, as much of it as the door has uncovered
    var ox = x1 - slid;
    cx.fillStyle = '#0e0e12'; cx.fillRect(ox, top, slid + 1, sill - top + 1);
    cx.fillStyle = '#1e2026'; cx.fillRect(ox + 2, top + 2, Math.max(0, slid - 3), sill - top - 4);
    // the rack: its lights, and the button marked RENDER
    for (var j = 0; j < 5; j++) for (var i = 0; i < 4; i++) {
      var lx = x0 + 4 + i * 4, ly = top + 4 + j * 4;
      if (lx < ox + 1) continue;
      var on = !smashed && hash(i * 7 + j, tick >> 3) < 0.7;
      cx.fillStyle = on ? ((i + j) % 3 ? '#5ae678' : '#f04632') : '#2a2a30';
      cx.fillRect(lx, ly, 1, 1);
    }
    if (x0 + 6 >= ox) {
      cx.fillStyle = '#3c3c42'; cx.fillRect(x0 + 6, sill - 9, 7, 5);
      cx.fillStyle = smashed ? '#501e1a' : ((tick >> 4) % 2 ? '#dc281e' : '#ff4a3a'); cx.fillRect(x0 + 7, sill - 8, 5, 3);
    }
    // the door, slid back along the side over the body behind it
    var dx = x0 - slid;
    cx.fillStyle = '#cec9bc'; cx.fillRect(dx, top, w, sill - top + 1);
    cx.fillStyle = '#9a968c'; cx.fillRect(dx, top, 1, sill - top + 1); cx.fillRect(dx + w - 1, top, 1, sill - top + 1);
    cx.fillStyle = '#9c2a1e'; cx.fillRect(dx, V.roof + 24, w, 5);
    cx.fillStyle = '#e8b83c'; cx.fillRect(dx, V.roof + 26, w, 1);
    if (smashed && tick % 6 < 3) { cx.fillStyle = 'rgba(60,60,64,0.6)'; cx.fillRect(x0, top - 2, w, 3); }
  }

  // ---------------------------------------------------------------- render.js asks
  function ground(s, paused, K) {
    if (!s.spk || !sheet()) return;
    cx = K.ctx();
    var A = s.L.arena, cam = s.cam, W = K.W(), b = mine(s);
    if (A.x1 + 60 < cam || A.x0 - 60 > cam + W) return;
    for (var i = 0; i < A.podiums.length; i++) if (A.podiums[i] + 30 >= cam && A.podiums[i] - 30 <= cam + W) drawScreen(s, b, i, K);
    if (b && (X.atPodium(b) || b.st === 'dying' || b.st === 'dead')) drawHimAtPodium(s, b, K);
    drawPodiums(s, b, K);
    drawMics(paused);
    drawVan(s, K);
  }
  // him on the move (over everyone), and the feedback along the ground
  function draw(s, b, paused, K) {
    if (!sheet()) return;
    cx = K.ctx();
    var fy = X.floorY(s), tick = K.tick();
    if (b.st === 'arrive' || b.st === 'dash') ispr('spk_run' + (Math.floor(tick / 5) % 2), b.x, b.y, b.st === 'arrive' || b.x1 < b.x);
    else if (b.st === 'leap') ispr('spk_jump', b.x, b.y, b.x1 < b.x0);
    for (var i = 0; i < s.spk.waves.length; i++) {
      var w = s.spk.waves[i], x = Math.round(w.x);
      // a shriek along the ground: a jagged line, bright at its front
      for (var k = 0; k < 26; k++) {
        var xx = x - w.dir * k, a = Math.max(0, 1 - k / 26);
        var yy = fy - 3 - Math.round(Math.sin((xx + tick * 3) * 0.9) * 3 * a);
        cx.fillStyle = k < 4 ? '#ffffff' : (k % 3 ? '#a8f0ff' : '#5ac8e8');
        cx.fillRect(xx, yy, 1, 1);
        if (k < 10) cx.fillRect(xx, yy + 1, 1, 1);
      }
    }
  }
  // the dark at the last podium: everything dimmed, his screen and his torch lit
  function post(s, paused, K) {
    if (!s.spk || s.spk.dark <= 0 || !sheet()) return;
    cx = K.ctx();
    var b = mine(s), W = K.W(), d = s.spk.dark;
    cx.fillStyle = 'rgba(4,6,14,' + (0.66 * d).toFixed(3) + ')';
    cx.fillRect(Math.floor(s.cam) - 2, -10, W + 4, K.H + 20);
    if (!b) return;
    drawScreen(s, b, b.pod, K);
    if (b.st === 'speak' || b.st === 'ready' || b.st === 'after' || b.st === 'stun' || b.st === 'fix') {
      // his torch: a cone of light on the page and his face (still on him while he is cut off, and while he clips on a
      // spare: he is to be seen to be shot)
      var fl = b.face < 0, tx = b.x + (fl ? -6 : 6), ty = b.y - 24;
      cx.fillStyle = 'rgba(255,236,170,' + (0.22 * d).toFixed(3) + ')';
      cx.beginPath(); cx.moveTo(tx, ty); cx.lineTo(tx + (fl ? -26 : 26), ty - 18); cx.lineTo(tx + (fl ? -30 : 30), ty + 6); cx.closePath(); cx.fill();
      drawHimAtPodium(s, b, K);
      ispr(s.spk.pods[b.pod].mic ? 'podium' : 'podium_bare', s.spk.pods[b.pod].x, s.L.arena.y, b.face < 0);
    }
  }
  // the Dhamar plateau, behind the lookout, as the cloud clears (before the picture the lookout is painted on)
  function behind(s, paused, K) {
    if (!s.spk || s.spk.clear <= 0) return;
    if (!PLATEAU) PLATEAU = Render.image('i_plateau');
    if (!PLATEAU) return;
    cx = K.ctx();
    var W = K.W();
    cx.globalAlpha = Math.min(1, s.spk.clear);
    cx.drawImage(PLATEAU, Math.round((W - PLATEAU.width) / 2), 0);
    cx.globalAlpha = 1;
  }

  function events(e, s, K) {
    switch (e.t) {
      case 'boss_intro': K.shake(2); said = {}; sayKey = null; wasSt = ''; mics.length = 0; closeT = 0; break;
      case 'boss_phase':
        K.pop(e.x, e.y - 20, T(e.n === 2 ? 'TWO PODIUMS LEFT' : 'THE LAST PODIUM'), 's_lav');
        K.shake(5); K.flash(1);
        break;
      case 'boss_dying': K.shake(6); K.flash(2); break;
      case 'boss_dead':
        K.pop(e.x, e.y - 30, String(e.pts), 'm_org');
        K.shake(10); K.flash(3);
        break;
    }
  }
  function misc(e, s, K) {
    var k;
    switch (e.t) {
      case 'spk_say': if (!said.mic) say('mic', 110); return true;
      case 'spk_chip':
        K.part('spark', e.x, e.y, { life: 5, name: 'fx_spark2' });
        for (k = 0; k < 2; k++) K.part('ember', e.x, e.y, { life: 8, vx: (Math.random() - 0.5) * 120, vy: -60 - Math.random() * 60, g: 500 });
        return true;
      case 'spk_cut':
        // the microphone shot off its stalk, flying
        mics.push({ x: e.x, y: e.y - 4, vx: e.dir * 70 + (Math.random() - 0.5) * 30, vy: -160, t: 0, floor: s.L.arena.y - 1 });
        for (k = 0; k < 5; k++) K.part('spark', e.x + (Math.random() - 0.5) * 6, e.y + (Math.random() - 0.5) * 6, { life: 6, name: 'fx_spark2' });
        K.pop(e.x - e.dir * 6, e.y - 30, T('WHAT?'), 'b_org');
        K.shake(4);
        say('hit', 70);
        return true;
      case 'spk_land': K.part('puff', e.x - 5, e.y - 2, { life: 8 }); K.part('puff', e.x + 5, e.y - 2, { life: 8, flip: true }); return true;
      case 'spk_leap': K.part('puff', e.x, e.y - 2, { life: 8 }); return true;
      case 'spk_dash': K.part('puff', e.x, e.y - 2, { life: 8 }); say('dash', 50); return true;
      case 'spk_wave': say('wave', 50); return true;
      case 'spk_spare': K.pop(e.x, e.y - 20, T('A SPARE!'), 's_lav'); return true;
      case 'spk_fixed': K.part('spark', e.x, e.y, { life: 4, name: 'fx_spark2' }); return true;
      case 'cable_wind': for (k = 0; k < 3; k++) K.part('clod', e.x + (Math.random() - 0.5) * 16, e.y + (Math.random() - 0.5) * 16, { life: 10, vx: (Math.random() - 0.5) * 80, vy: -30, g: 200, col: '#26262c' }); return true;
      case 'spk_fall': K.shake(2); return true;
      case 'spk_topple':
        // down on the floor behind his podium: a thud and the dust
        K.shake(6); K.flash(1);
        for (k = 0; k < 4; k++) K.part('puff', e.x + (k - 1.5) * 9, e.y - 2, { life: 9 + k, flip: k % 2 === 1 });
        return true;
      case 'spk_rerender': closeT = SP.HOLD; K.flash(2); return true;
      case 'spk_cables': say('cables', 160); return true;
      case 'van_open': K.part('puff', e.x, e.y, { life: 10 }); return true;
      case 'tech_out': if (e.n === 0) say('rack', 160); return true;
      case 'spk_smash':
        for (k = 0; k < 10; k++) K.part('spark', e.x + (Math.random() - 0.5) * 18, e.y + (Math.random() - 0.5) * 22, { life: 6 + Math.random() * 6, name: k % 2 ? 'fx_spark' : 'fx_spark2' });
        for (k = 0; k < 4; k++) K.part('smoke', e.x + (Math.random() - 0.5) * 12, e.y - 10, { life: 40, vx: -8, vy: -30 });
        K.shake(8); K.flash(3);
        return true;
      case 'spk_call': case 'spk_clearing': case 'spk_clear': case 'tech_say': return true;
    }
    return false;
  }

  // ---- the word on the screen, and the close-up when the screens come back on
  function say(key, n) { said[key] = (said[key] || 0) + 1; if (said[key] <= 2) { sayKey = key; sayT = n; } }
  function hud(s, b, K, paused) {
    if (!sheet()) return;
    cx = K.ctx();
    var W = K.W(), mid = Math.floor(W / 2);
    if (closeT > 0) {
      // the close-up: the screen at the billboard's size, his mouth with the line, on the left of the picture (Khaled,
      // 30 Oct 13:56: in the middle it covered everything); up while Yazeed is held to hear him
      if (!paused) closeT--;
      var a = Math.min(1, Math.min(closeT, SP.HOLD - closeT) / 12), m = lineMouth(s, K, 'sp_');
      cx.globalAlpha = a;
      var x0 = 10, y0 = 38;
      cx.fillStyle = '#16181c'; cx.fillRect(x0 - 4, y0 - 4, 152, 104);
      cx.fillStyle = '#4a4e56'; cx.fillRect(x0 - 4, y0 - 4, 152, 1);
      ispr('bf' + (m < 0 ? 0 : m), x0, y0);
      cx.globalAlpha = 1;
    }
    if (!paused && sayT > 0) sayT--;
    if (sayKey && sayT > 0 && (K.tick() >> 2) % 2 && closeT <= 0) K.text('b_org', T(SAY[sayKey]), mid, 70, 'c');
  }
  // the Uncle's men, out of the back room
  function man(s, e, K) {
    if (e.tech == null || !sheet()) return false;
    cx = K.ctx();
    var walking = e.st === 'out', y = e.y - (walking && Math.floor(e.walkD / 6) % 2 ? 1 : 0);
    ispr('tech' + e.tech + (walking ? '_stand' : '_up'), e.x, y, e.face < 0);
    // (WALK IN over the one nearest Yazeed only: three of them side by side would run their words together)
    if (e.st === 'surr' && !e.captured && (K.tick() >> 4) % 2 && nearestTech(s) === e) K.text('s_lav', T('WALK IN'), e.x, e.y - 48, 'c');
    return true;
  }
  function nearestTech(s) {
    var best = null, bd = 1e9;
    for (var i = 0; i < s.enemies.length; i++) {
      var q = s.enemies[i];
      if (q.tech == null || q.st !== 'surr' || q.captured) continue;
      var d = Math.abs(q.x - s.p.x);
      if (d < bd) { bd = d; best = q; }
    }
    return best;
  }
  function reset() { mics.length = 0; closeT = 0; sayKey = null; sayT = 0; said = {}; }

  Render.bosses.spokesman = { ground: ground, draw: draw, post: post, behind: behind, events: events, misc: misc, hud: hud, man: man, reset: reset };
})();
