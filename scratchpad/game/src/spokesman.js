// spokesman.js - Brigadier Breaking («العميد عاجل»), the Zanabeel's spokesman, on Sumara pass (Ibb, zone 4): his fight
// on the lookout's five podiums, the catch, and the reveal after it, as the storyboard Khaled passed on 30 Oct (00:39,
// "Go ahead and finish the whole level").
//   The fight. He runs in from their van and speaks from a podium, every screen on the lookout showing him. He can be
//   hurt only when he is cut off: shoot the microphone on the podium he is speaking into and he is stunned mid-word ("WHAT?
//   SPEAK UP!") for a few seconds, every screen frozen on him; only then do shots and blasts hurt him, and a stun takes at
//   most a fifth of him. That podium is done (its screen goes to snow) and he leaps to another, over Yazeed (touching him
//   hurts). With two podiums left he shouts, an ear ringing, and the feedback runs along the ground from his microphone
//   (jump it), and he dashes along the floor between them (jump him); at the last one the lights go out and he reads by
//   torchlight, cornered; there he has spare microphones. Every second line calls a few of his men in. Shots pass through
//   him while he is not stunned, as they pass his screens; the podiums stop a low shot; a microphone he is not speaking
//   into is no target.
//   The catch (Khaled, 30 Oct 13:56: "too quick"): out of him, his men give up at once (and what they had fired is gone),
//   and he takes his time going down: he reels from the last shot, spins as his own microphone cable winds round him, and
//   goes over backwards behind his podium, tied up, where he stays (OFF AIR on the screen). Nothing else happens until that
//   has sunk in and Yazeed walks on.
//   The reveal. The screens come back on, all five: he is still speaking (statement E), though he lies there tied up with
//   his mouth shut, and on the screens the ear on the viewer's left is too big and there are two Yemens on the backdrop (a
//   close-up comes up on the left of the picture); Yazeed is held a moment to hear him, then free to go on (Khaled, 13:56).
//   The cables lead to their van; with Yazeed at it, its side door slides open on the back room: a rack
//   of machines with a button marked RENDER, and three of the Uncle's men in headphones, who come out with their hands up
//   (they are in nothing the game hits; walk up to capture them). Smash the rack and every screen in Ibb goes dark at once;
//   the Uncle on the radio; the cloud clears onto the Dhamar plateau; the way out opens (the level's last gate waits on
//   done()).
// The level says where: L.arena = { x0, x1, y, podiums: [x], van: { x0, x1, door: [x0, x1], roof, sill }, lines: { 1, 2, 3,
// E: [[id, ticks]] } } and the boss's group (BOSS, hold) with its gate; render_spokesman.js draws it all.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev;
  var SP = Sim.SP = {
    HP: 70, SEG: 14,                 // five lots: a stun takes one at most (with the pistol, not quite one: the last podium
                                     // has spare microphones)
    STUN: 130,                       // cut off: this long stunned, hurtable
    MIC_HITS: 3,                     // shots it takes to put his microphone out
    FIRST: 50, GAP: 24,              // a breath before his first line, and after each
    LEAP_T: 48, LEAP_H: 64,          // from podium to podium, over Yazeed
    DASH_V: 200, RUN_V: 170,         // (two podiums left) along the floor between them; running in from the van
    CALL: [0, 2, 2, 1], MEN_MAX: 4,  // men called in every second line, by phase; never more than this many of them about
    WAVE_V: 150, WAVE_H: 9, WAVE_AT: 34, WAVE_HW: 8,      // the feedback along the ground
    FIX: 70,                         // the last podium: a spare microphone clipped on
    REEL: 30, SPIN: 140, TOPPLE: 30, DIE: 180,           // tied up in his cable: reeling until REEL, spinning as it winds
                                     // until SPIN, going over backwards for TOPPLE; caught at DIE (3 s from the last shot)
    MIC_DX: 6, MIC_HW: 4, MIC_TOP: 29, MIC_BOT: 15,       // the live microphone: ahead of his podium, toward Yazeed; its height off the floor
    BEHIND: 3, BODY_HW: 7, BODY_TOP: 33,                  // him behind his podium; his box, stunned, above it
    POD_HW: 11, POD_H: 15,           // a podium stops a shot this low
    PTS: 8000, CAUGHT_PTS: 1000, GREN_DMG: 4,
    PASS_HINT: 8,                    // shots through him before the word about his microphone
    // the reveal
    SETTLE: 120, WALK: 32,           // caught: this long for it to sink in; then once Yazeed has walked on this far, the
    CLEAR_X: 176,                    // screens come back on (with him this far into the picture, clear of the close-up on
                                     // its left: render_spokesman.js draws it to x 158)
    HOLD: 400,                       // ... and Yazeed is held this long (the close-up up), to hear the start of statement E
    REACH: 100,                      // Yazeed this near the van's door: it opens (and they have room to come out to him)
    TECH_GAP: 24, RACK_HP: 6,        // the technicians out one after another; the rack's shots
    RADIO: 520, CLEAR_T: 240         // from the rack smashed to the cloud clearing; how long it takes
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function mine(b) { return !!b && b.kind === 'spokesman'; }
  function open(b) { return mine(b) && b.st !== 'dead'; }
  function fighting(b) { return mine(b) && b.st !== 'arrive' && b.st !== 'dying' && b.st !== 'dead'; }
  function floorY(s) { return s.L.arena.y; }
  function atPodium(b) { return b.st === 'ready' || b.st === 'speak' || b.st === 'after' || b.st === 'stun' || b.st === 'fix'; }
  function live(s) { var n = 0, P = s.spk.pods; for (var i = 0; i < P.length; i++) if (P[i].mic) n++; return n; }
  function phaseOf(s) { var n = live(s); return n >= 3 ? 1 : (n === 2 ? 2 : 3); }
  function micX(s, b) { return s.spk.pods[b.pod].x + b.face * SP.MIC_DX; }
  // the microphone he is speaking into (only while he speaks: between lines he is not on it)
  function hot(s, b) { return b.st === 'speak' && s.spk.pods[b.pod].mic; }

  function create(s) {
    var A = s.L.arena;
    s.spk = null;
    if (!A) return;
    s.spk = { pods: A.podiums.map(function (x) { return { x: x, mic: true }; }), waves: [], lineN: 0, li: [0, 0, 0, 0], passes: 0, said: {},
              dark: 0, fake: false, off: false, clear: 0, rv: null, van: { open: 0, t: 0, rack: SP.RACK_HP, smashed: false }, techs: 0 };
  }
  function done(s) { return !s.spk || (!!s.spk.rv && s.spk.rv.st === 'done'); }

  function intro(s) {
    var A = s.L.arena;
    s.boss = { kind: 'spokesman', label: 'BRIGADIER BREAKING', full: SP.HP, hp: SP.HP, floor: SP.HP, phase: 1, st: 'arrive', stT: 0, t: 0, hurtT: 99,
               x: Math.max(s.cam + s.viewW + 24, A.podiums[A.podiums.length - 1] + 40), y: floorY(s), pod: 2, from: -1, face: -1, cuts: 0,
               line: null, lineT: 0, hitOnce: false, t0: s.time, captured: false };
    ev(s, { t: 'boss_intro', k: 'spokesman', x: s.boss.x, y: floorY(s) - 30 });
  }
  function to(b, st) { b.st = st; b.stT = 0; }
  function standX(s, b, i) { return s.spk.pods[i].x - b.face * SP.BEHIND; }
  function faceYazeed(s, b, i) { b.face = s.p.x < s.spk.pods[i].x ? -1 : 1; }

  // ------------------------------------------------------------------ one tick
  function step(s) {
    if (!s.spk) return;
    var G = s.groups.BOSS, b = s.boss;
    if (!b && G && G.awake && !G.done && G.hold && s.mode === 'foot') { intro(s); b = s.boss; }
    stepWaves(s);
    if (mine(b)) stepBoss(s, b);
    // while he is about the podiums the screen comes up to the lookout's held screen, all five podiums in it (the camera
    // otherwise only follows Yazeed: one who hangs back would have the far podium off the picture)
    if (open(b) && s.camMax != null && s.cam < s.camMax) s.cam = Math.min(s.camMax, s.cam + T.CAM_V);
    // the lights: out at the last podium, back on once he is caught; the cloud clearing at the end
    var want = mine(b) && b.phase === 3 && b.st !== 'dying' && b.st !== 'dead' ? 1 : 0;
    s.spk.dark = clamp(s.spk.dark + (want ? 1 / 40 : -1 / 30), 0, 1);
    if (s.spk.rv) stepReveal(s, b);
  }

  function stepBoss(s, b) {
    var p = s.p, A = s.L.arena;
    b.t++; b.stT++; b.hurtT++;
    if (b.st === 'dead') { capture(s, b); return; }
    switch (b.st) {
      case 'arrive':
        // late for his own statement: running in from the van to the middle podium
        faceYazeed(s, b, b.pod);
        var tx = standX(s, b, b.pod);
        b.x = Math.max(tx, b.x - SP.RUN_V * DT); b.y = floorY(s);
        contact(s, b, 'spokesman');
        if (b.x <= tx) { land(s, b); b.stT = -SP.FIRST + SP.GAP; ev(s, { t: 'boss_start', k: 'spokesman' }); }
        break;
      case 'ready':
        faceYazeed(s, b, b.pod); b.x = standX(s, b, b.pod);
        if (b.stT >= SP.GAP) say(s, b);
        break;
      case 'speak':
        faceYazeed(s, b, b.pod); b.x = standX(s, b, b.pod);
        if (b.phase >= 2 && b.stT === SP.WAVE_AT) wave(s, b);
        if (b.stT >= b.lineT) to(b, 'after');
        break;
      case 'after':
        faceYazeed(s, b, b.pod); b.x = standX(s, b, b.pod);
        if (b.stT >= SP.GAP) {
          s.spk.lineN++;
          if (s.spk.lineN % 2 === 0) call(s, b);
          if (b.phase >= 3) to(b, 'ready');
          else move(s, b);
        }
        break;
      case 'stun':
        if (b.stT >= SP.STUN) {
          call(s, b);                                                                       // (his men come running)
          if (live(s) > 0) move(s, b);
          else { to(b, 'fix'); ev(s, { t: 'spk_spare', x: b.x, y: floorY(s) - 30 }); }      // (the last podium: he has a spare)
        }
        break;
      case 'fix':
        if (b.stT >= SP.FIX) { s.spk.pods[b.pod].mic = true; ev(s, { t: 'spk_fixed', x: micX(s, b), y: floorY(s) - 22 }); to(b, 'ready'); }
        break;
      case 'leap':
        var u = Math.min(1, b.stT / SP.LEAP_T);
        b.x = b.x0 + (b.x1 - b.x0) * u;
        b.y = floorY(s) - SP.LEAP_H * 4 * u * (1 - u);
        contact(s, b, 'spokesman');
        if (u >= 1) land(s, b);
        break;
      case 'dash':
        var dir = b.x1 > b.x ? 1 : -1;
        b.x += dir * SP.DASH_V * DT; b.y = floorY(s);
        contact(s, b, 'spokesman');
        if ((b.x1 - b.x) * dir <= 0) { b.x = b.x1; land(s, b); }
        break;
      case 'dying':
        // reeling from the last shot; spinning as the cable winds round him; over backwards, away from Yazeed
        if (b.stT >= SP.REEL && b.stT < SP.SPIN && (b.stT - SP.REEL) % 18 === 0) ev(s, { t: 'cable_wind', x: b.x, y: floorY(s) - 20 });
        if (b.stT === SP.SPIN) ev(s, { t: 'spk_fall', x: b.x, y: floorY(s) - 20 });
        if (b.stT === SP.SPIN + SP.TOPPLE) ev(s, { t: 'spk_topple', x: b.x - b.face * 20, y: floorY(s), dir: -b.face });
        if (b.stT >= SP.DIE) die(s, b);
        break;
    }
  }
  // speaking from his podium: the next line of what he says in this phase
  function say(s, b) {
    var L = s.L.arena.lines[b.phase], k = s.spk.li[b.phase]++ % L.length;
    b.line = L[k][0]; b.lineT = L[k][1];
    s.spk.micHits = 0;
    to(b, 'speak');
    ev(s, { t: 'spk_say', id: b.line, x: b.x, y: floorY(s) - 30, pod: b.pod, phase: b.phase });
  }
  function land(s, b) {
    b.y = floorY(s); b.from = -1;
    faceYazeed(s, b, b.pod); b.x = standX(s, b, b.pod);
    var ph = phaseOf(s);
    if (ph > b.phase) { b.phase = ph; ev(s, { t: 'boss_phase', k: 'spokesman', n: ph, x: b.x, y: floorY(s) - 40 }); }
    to(b, 'ready');
    ev(s, { t: 'spk_land', x: b.x, y: b.y });
  }
  // on to another podium that still has its microphone: over Yazeed if one lies beyond him, otherwise the nearest
  function move(s, b) {
    var P = s.spk.pods, p = s.p, best = -1, bs = 1e9;
    for (var i = 0; i < P.length; i++) {
      if (!P[i].mic || i === b.pod) continue;
      var over = (P[i].x - p.x) * (P[b.pod].x - p.x) < 0, d = Math.abs(P[i].x - P[b.pod].x) + (over ? 0 : 400) + s.rand() * 30;
      if (d < bs) { bs = d; best = i; }
    }
    if (best < 0) { to(b, 'ready'); return; }
    b.from = b.pod; b.pod = best; b.x0 = b.x; b.hitOnce = false;
    b.face = P[best].x > b.x ? 1 : -1;
    b.x1 = P[best].x - (p.x < P[best].x ? -1 : 1) * SP.BEHIND;
    if (b.phase >= 2) { to(b, 'dash'); ev(s, { t: 'spk_dash', x: b.x, y: b.y }); }
    else { to(b, 'leap'); ev(s, { t: 'spk_leap', x: b.x, y: b.y }); }
  }
  // his men, called in: from both sides, never too many of them about at once
  function call(s, b) {
    var n = SP.CALL[b.phase], about = 0, i;
    for (i = 0; i < s.enemies.length; i++) if (s.enemies[i].alive && s.enemies[i].hostile && s.enemies[i].g === 'BOSS') about++;
    n = Math.min(n, SP.MEN_MAX - about);
    if (n <= 0) return;
    var looks = ['angry', 'qat', 'youth', 'worried'];
    for (i = 0; i < n; i++) {
      var side = (s.spk.lineN / 2 + i) % 2 === 0 ? 1 : -1, k = (b.phase >= 2 && i === 1) ? 'bomber' : 'rifle';
      var x = side > 0 ? s.cam + s.viewW + 16 + i * 30 : s.cam - 16 - i * 30;
      var e = I.spawnEnemy(s, { g: 'BOSS', k: k, enter: side, look: looks[(s.spk.lineN + i) % 4] }, x);
      if (side < 0) { e.cd += 46; ev(s, { t: 'behind', k: k }); }
    }
    ev(s, { t: 'spk_call', n: n, first: !s.spk.said.call, x: b.x });
    s.spk.said.call = 1;
  }
  // touching him while he leaps or dashes hurts (once a move)
  function contact(s, b, why) {
    var p = s.p;
    if (b.hitOnce || p.dead || p.inv > 0 || s.status !== 'play') return;
    var pb = Sim.playerBox(p);
    if (b.x + SP.BODY_HW < pb.x0 || b.x - SP.BODY_HW > pb.x1 || b.y - SP.BODY_TOP > pb.y1 || b.y < pb.y0) return;
    if (I.hurtPlayer(s, b.x, why)) b.hitOnce = true;
  }
  // the feedback from his microphone, along the ground toward Yazeed: jump it
  function wave(s, b) {
    var x = micX(s, b);
    s.spk.waves.push({ x: x, dir: b.face, t: 0 });
    ev(s, { t: 'spk_wave', x: x, y: floorY(s) - 4 });
  }
  function stepWaves(s) {
    var W = s.spk.waves, p = s.p, fy = floorY(s);
    for (var i = W.length - 1; i >= 0; i--) {
      var w = W[i];
      w.t++; w.x += w.dir * SP.WAVE_V * DT;
      if (!p.dead && p.inv <= 0 && s.status === 'play' && Math.abs(w.x - p.x) < SP.WAVE_HW && p.y > fy - SP.WAVE_H) I.hurtPlayer(s, w.x, 'feedback');
      if (w.x < s.cam - 20 || w.x > s.cam + s.viewW + 20 || (s.boss && s.boss.st === 'dead')) W.splice(i, 1);
    }
  }

  // ------------------------------------------------------------------ cut off, hurt, caught
  function cut(s, b) {
    var x = micX(s, b);
    s.spk.pods[b.pod].mic = false;
    b.cuts++;
    b.floor = Math.max(0, SP.HP - SP.SEG * b.cuts);
    to(b, 'stun');
    ev(s, { t: 'spk_cut', x: x, y: floorY(s) - 22, n: b.cuts, pod: b.pod, dir: b.face });
  }
  function hurt(s, n) {
    var b = s.boss;
    if (!mine(b) || b.st !== 'stun') return false;
    var before = b.hp;
    b.hp = Math.max(b.floor, b.hp - n);
    b.hurtT = 0;
    if (b.hp <= 0) {
      b.hp = 0; to(b, 'dying'); s.spk.waves.length = 0;
      giveUp(s);
      ev(s, { t: 'boss_dying', k: 'spokesman', x: b.x, y: floorY(s) - 30 });
    }
    return b.hp < before;
  }
  // the last shot in him: his men give up there and then, and nothing of theirs is left flying (Yazeed watches him go down)
  function giveUp(s) {
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.alive && e.hostile && e.g === 'BOSS' && e.st !== 'shock') { e.st = 'shock'; e.stT = 0; }
    }
    for (i = 0; i < s.bullets.length; i++) if (!s.bullets[i].own) s.bullets[i].gone = true;
    for (i = 0; i < s.bombs.length; i++) if (!s.bombs[i].own) s.bombs[i].gone = true;
  }
  function die(s, b) {
    var G = s.groups.BOSS;
    to(b, 'dead');
    s.score += SP.PTS;
    s.stats.bossT = s.time - b.t0;
    G.hold = false;
    ev(s, { t: 'boss_dead', k: 'spokesman', x: b.x, y: floorY(s) - 40, pts: SP.PTS });
    s.spk.rv = { st: 'wait', t: 0, x0: null };
  }
  // tied up at his podium: walk up to him and he is yours
  function capture(s, b) {
    var p = s.p;
    if (b.captured || p.dead || s.status !== 'play') return;
    if (Math.abs(p.x - b.x) < 15 && Math.abs(p.y - b.y) < 26) {
      b.captured = true;
      s.score += SP.CAUGHT_PTS; s.stats.captures++;
      if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
      ev(s, { t: 'capture', x: b.x, y: b.y, pts: SP.CAUGHT_PTS, k: 'spokesman' });
    }
  }

  // ------------------------------------------------------------------ the reveal
  function stepReveal(s, b) {
    var rv = s.spk.rv, A = s.L.arena, V = A.van, p = s.p;
    rv.t++;
    switch (rv.st) {
      case 'wait':
        // caught: a moment for it to sink in; then, once Yazeed walks on (or is already at the van), the screens come back on
        // and he is held, to hear him
        if (rv.t === SP.SETTLE) rv.x0 = p.x;
        if (rv.t > SP.SETTLE && !p.dead && ((p.x >= rv.x0 + SP.WALK && p.x - s.cam >= SP.CLEAR_X) || p.x >= V.door[0] - 40)) {
          s.spk.fake = true; rv.st = 'rerender'; rv.t = 0; s.script = { mx: 0 };
          ev(s, { t: 'spk_rerender', x: A.podiums[2], y: floorY(s) - 60 });
        }
        break;
      case 'rerender':
        if (rv.t >= SP.HOLD) { s.script = null; rv.st = 'cables'; rv.t = 0; ev(s, { t: 'spk_cables', x: V.door[0], y: floorY(s) - 30 }); }
        break;
      case 'cables':
        if (!p.dead && p.x >= V.door[0] - SP.REACH) { rv.st = 'open'; rv.t = 0; ev(s, { t: 'van_open', x: V.door[0], y: V.sill - 10 }); }
        break;
      case 'open':
        s.spk.van.open = Math.min(1, s.spk.van.open + 1 / 24);
        break;
      case 'smashed':
        if (rv.t >= SP.RADIO) { rv.st = 'clearing'; rv.t = 0; ev(s, { t: 'spk_clearing' }); }
        break;
      case 'clearing':
        s.spk.clear = Math.min(1, rv.t / SP.CLEAR_T);
        if (rv.t >= SP.CLEAR_T) { rv.st = 'done'; rv.t = 0; ev(s, { t: 'spk_clear' }); }
        break;
    }
    // the technicians, out of the back room one after another once its door is open, whether or not the rack is smashed
    // by then (all three come out, and one is out to say they cannot before the Uncle has finished asking)
    if (rv.st !== 'wait' && rv.st !== 'rerender' && rv.st !== 'cables') {
      var vn = s.spk.van;
      vn.t = (vn.t || 0) + 1;
      if (vn.t >= 30 && s.spk.techs < 3 && (vn.t - 30) % SP.TECH_GAP === 0) tech(s, s.spk.techs++);
    }
  }
  // one of the Uncle's men out of the back room, hands going up: in nothing the game hits (not hostile); walk up to capture
  function tech(s, n) {
    var V = s.L.arena.van, G = s.groups.BOSS;
    var e = I.spawnEnemy(s, { g: 'BOSS', k: 'rifle', post: 1 }, V.door[0] + 6);
    G.hostile--;
    e.hostile = false; e.ext = 'spokesman'; e.tech = n; e.noKnife = true; e.st = 'out'; e.stT = 0; e.face = -1;
    e.to = V.door[0] - 18 - 20 * n;
    ev(s, { t: 'tech_out', x: e.x, y: e.y, n: n });
  }
  function man(s, e) {
    var p = s.p, L = s.L;
    if (e.tech == null) return;
    if (e.st === 'out') {
      e.x = Math.max(e.to, e.x - 40 * DT); e.walkD += 40 * DT; e.y = Sim.groundY(L, e.x);
      if (e.x <= e.to) { e.st = 'surr'; e.stT = 0; ev(s, { t: 'surrender', x: e.x, y: e.y, id: e.id, k: 'tech', n: e.tech }); }
      return;
    }
    if (e.st === 'surr') {
      e.face = p.x >= e.x ? 1 : -1;
      if (!e.captured && !p.dead && Math.abs(p.x - e.x) < 15 && Math.abs(p.y - e.y) < 26) {
        e.captured = true; e.stT = 0;
        s.score += 500; s.stats.captures++;
        ev(s, { t: 'capture', x: e.x, y: e.y, id: e.id, k: 'tech' });
      }
    }
  }

  // ------------------------------------------------------------------ what the rest of the game asks
  function shot(s, bl) {
    var b = s.boss, A = s.L.arena, fy, i;
    if (!s.spk || !A || !bl.own) return false;
    fy = floorY(s);
    // the rack in their van, once its door is open
    var rv = s.spk.rv, V = A.van;
    if (rv && rv.st === 'open' && s.spk.van.open >= 1 && bl.x >= V.door[0] + 1 && bl.x <= V.door[1] - 1 && bl.y >= V.roof + 5 && bl.y <= V.sill - 2) {
      ev(s, { t: 'hit', kind: 'metal', x: bl.x, y: bl.y });
      if (--s.spk.van.rack <= 0) smash(s);
      return true;
    }
    if (!fighting(b)) return podiumStops(s, bl, fy);
    // the microphone he is speaking into: cut him off
    if (hot(s, b)) {
      var mx = micX(s, b);
      if (Math.abs(bl.x - mx) <= SP.MIC_HW && bl.y >= fy - SP.MIC_TOP && bl.y <= fy - SP.MIC_BOT + 4) {
        if (++s.spk.micHits >= SP.MIC_HITS) cut(s, b);
        else ev(s, { t: 'spk_chip', x: mx, y: fy - 22, n: s.spk.micHits });
        return true;
      }
    }
    // him, stunned: hurt (a shot through him otherwise goes on, as through his screens)
    if (Math.abs(bl.x - b.x) <= SP.BODY_HW && bl.y >= b.y - SP.BODY_TOP && bl.y <= b.y - (atPodium(b) ? SP.POD_H : 0)) {
      if (b.st === 'stun') { ev(s, { t: 'hit', kind: 'body', x: bl.x, y: bl.y }); hurt(s, 1); return true; }
      if (b.st === 'speak' && !bl.passed) {
        bl.passed = true;
        if (++s.spk.passes === SP.PASS_HINT && !s.hinted.mic) { s.hinted.mic = 1; ev(s, { t: 'hint', k: 'mic' }); }
      }
    }
    return podiumStops(s, bl, fy);
  }
  function podiumStops(s, bl, fy) {
    var P = s.spk.pods;
    for (var i = 0; i < P.length; i++) {
      if (Math.abs(bl.x - P[i].x) <= SP.POD_HW && bl.y >= fy - SP.POD_H && bl.y <= fy) { ev(s, { t: 'hit', kind: 'wood', x: bl.x, y: bl.y }); return true; }
    }
    return false;
  }
  function smash(s) {
    var V = s.L.arena.van;
    s.spk.van.smashed = true; s.spk.off = true; s.spk.fake = false;
    s.spk.rv.st = 'smashed'; s.spk.rv.t = 0;
    ev(s, { t: 'spk_smash', x: (V.door[0] + V.door[1]) / 2, y: (V.roof + V.sill) / 2 });
  }
  function blast(s, x, y, r, kind, own) {
    var b = s.boss, fy;
    if (!s.spk || !own) return;
    fy = floorY(s);
    var rv = s.spk.rv, V = s.L.arena.van;
    if (rv && rv.st === 'open' && s.spk.van.open >= 1) {
      var nx = clamp(x, V.door[0], V.door[1]), ny = clamp(y, V.roof, V.sill);
      if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < r * r) { s.spk.van.rack -= 3; if (s.spk.van.rack <= 0) smash(s); }
      return;
    }
    if (!fighting(b)) return;
    if (hot(s, b)) {
      var mx = micX(s, b), my = fy - (SP.MIC_TOP + SP.MIC_BOT) / 2;
      if ((mx - x) * (mx - x) + (my - y) * (my - y) < (r + 3) * (r + 3)) { cut(s, b); return; }
    }
    if (b.st === 'stun') {
      var bx = clamp(x, b.x - SP.BODY_HW, b.x + SP.BODY_HW), by = clamp(y, b.y - SP.BODY_TOP, b.y - SP.POD_H);
      if ((bx - x) * (bx - x) + (by - y) * (by - y) < (r + 4) * (r + 4)) hurt(s, SP.GREN_DMG);
    }
  }
  function touch(s, x, y) {
    if (!s.spk) return false;
    var fy = floorY(s), P = s.spk.pods, b = s.boss;
    for (var i = 0; i < P.length; i++) if (Math.abs(x - P[i].x) <= SP.POD_HW && y >= fy - SP.POD_H && y <= fy) return true;
    if (mine(b) && b.st === 'stun' && Math.abs(x - b.x) <= SP.BODY_HW && y >= b.y - SP.BODY_TOP && y <= b.y) return true;
    return false;
  }
  // the gun's help (and AUTO): his microphone while he speaks into it, him while he is stunned, the rack once it shows
  function aim(s, m, consider) {
    if (!s.spk) return;
    var b = s.boss, fy = floorY(s), rv = s.spk.rv;
    if (rv && rv.st === 'open' && s.spk.van.open >= 1 && !s.spk.van.smashed) {
      var V = s.L.arena.van;
      consider((V.door[0] + V.door[1]) / 2, (V.roof + V.sill) / 2);
      return;
    }
    if (!fighting(b)) return;
    if (hot(s, b)) consider(micX(s, b), fy - (SP.MIC_TOP + SP.MIC_BOT) / 2 - 2);
    else if (b.st === 'stun') consider(b.x, b.y - 24);
  }

  Sim.ext.spokesman = { create: create, step: step, man: man, shot: shot, blast: blast, touch: touch, aim: aim, hurt: hurt, done: done,
                        open: open, fighting: fighting, hot: hot, micX: micX, atPodium: atPodium, live: live, floorY: floorY };
})();
if (typeof module !== 'undefined') module.exports = Sim;
