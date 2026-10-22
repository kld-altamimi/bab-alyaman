// tailor.js - the Tailor: the Zanabeel's tailor has the end of the covered market for his shop, and he hides among his own
// dummies. They stand on wheeled stands, every one of them in his clothes, and he stands among them as stiff as they
// are. It is the cup-and-ball trick: at the start he shows himself, then the stands are swapped about, two at a time,
// and you have to keep your eye on him. From his place he throws at you (scissors at chest height: get down; a spray
// of pins; later a measuring tape along the floor that yanks you to him: jump it), and a throw gives him away to anyone
// watching. Spice gives him away too: dummies don't sneeze. Shots don't go through a dummy, so you have to get to
// him; and a dummy shot by mistake springs its pins back at you (a second shot knocks it over, and it is stood up and
// dressed again at the next shuffle). Hit him and he is caught out: he gives up the pose, flapping, and every round
// counts until the shuffle starts again. Two thirds through a fifth dummy rolls in; one third, the stands are covered
// with sheets for the shuffles. At the end his own tape winds round him, the dummies fall over (they were stuffed with
// stolen chillies), and he gives up.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var TL = Sim.TL = {
    HP: 54,
    FIG_HW: 8, FIG_H: 38, STAND_H: 7,             // a figure: half its width, its height from the top of its stand; the stand
    FIGS: [0, 4, 5, 5],                           // figures in play, by phase
    SWAPS: [0, 3, 5, 6], SWAP_T: [0, 40, 31, 27], // a shuffle: how many swaps, how long each takes
    SHOW: 70,                                     // at the start he shows himself (the ball under the cup)
    HUNT_REST: [0, 96, 84, 72],                   // between his throws
    TELL: { scissors: 32, pins: 30, tape: 38 },
    SCISSORS_V: 196, PIN_V: 150, PINS: 3, PIN_SPREAD: 0.16,
    TAPE_V: 280, TAPE_MAX: 160, TAPE_HOLD: 10, TAPE_Y: 5,
    SNEEZE: 84, SNEEZE_IMM: 160,
    CAUGHT: 72, CATCH_HITS: 9,                    // caught out: rounds count until he has taken this many, or this long has gone
    BACKFIRE_PINS: 3, BACKFIRE_V: 122, BACKFIRE_SPREAD: 0.2,
    HUNT_MAX: 720,                                // not found in this long, he has them shuffled anyway
    STUN: 64, DIE: 110, COVER_T: 26,
    GREN_DMG: 5, PTS: 6000, BOSS_PTS: 500, CHILLIES: 3
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function mine(b) { return !!b && b.kind === 'tailor'; }
  function open(b) { return mine(b) && b.st !== 'intro' && b.st !== 'dying' && b.st !== 'dead'; }
  // the fight proper: not while he is showing himself at the start (shots then only stop in the stands)
  function fighting(b) { return open(b) && b.st !== 'show'; }
  function floorY(s) { return groundY(s.L, s.L.tailor.slots[0]); }
  function real(s) { var f = s.tailor.figs; for (var i = 0; i < f.length; i++) if (f[i].real) return f[i]; return null; }
  // a figure's box: from the top of its stand to the top of its head (a dummy knocked over has none)
  function figBox(s, f) {
    var fy = floorY(s) - TL.STAND_H;
    return { x0: f.x - TL.FIG_HW, x1: f.x + TL.FIG_HW, y0: fy - TL.FIG_H, y1: fy + TL.STAND_H };
  }
  function inBox(x, y, b, pad) { pad = pad || 0; return x >= b.x0 - pad && x <= b.x1 + pad && y >= b.y0 - pad && y <= b.y1 + pad; }
  function standing(f) { return f.st === 'dressed' || f.st === 'bare' || f.st === 'him'; }
  // what is out in the open: the real one up out of his pose (caught, sneezing, throwing)
  function shown(b) { return b.st === 'caught' || b.st === 'sneeze' || b.st === 'tell' || b.st === 'throw' || b.st === 'show'; }

  function create(s) {
    var C = s.L.tailor;
    if (!C) return;
    s.boss = null;
    var tl = s.tailor = { figs: [], shuffle: null, tape: null, cover: 0, coverWant: false, sacks: [], said: {}, n: TL.FIGS[1] };
    // the stands, in their places; he is in the one the level says (all of them are him, as far as anyone can see)
    for (var k = 0; k < C.slots.length; k++) {
      tl.figs.push({ id: k, slot: k, x: C.slots[k], x0: C.slots[k], x1: C.slots[k], real: k === C.start, st: k === C.start ? 'him' : (k < tl.n ? 'dressed' : 'off'),
                     hurtT: 99, wob: 0, depth: 0, roll: -1 });
    }
    stock(s);
  }
  // the spice sacks along the front of his shop: put back at the start of the fight and at each phase
  function stock(s) {
    var C = s.L.tailor, fy = floorY(s), cols = ['red', 'yel', 'org'];
    for (var k = 0; k < C.sacks.length; k++) {
      var have = false;
      for (var j = 0; j < s.props.length; j++) { var o = s.props[j]; if (!o.gone && o.k === 'spice' && Math.abs(o.x - C.sacks[k]) < 2) have = true; }
      if (!have) s.props.push({ id: s.nextId++, k: 'spice', x: C.sacks[k], y: fy, plat: -1, t: 0, st: 'idle', gone: false, col: cols[k % 3], tailor: true });
    }
  }

  function intro(s) {
    var f = real(s);
    s.boss = { kind: 'tailor', full: TL.HP, label: 'THE TAILOR', x: f.x, y: floorY(s), vx: 0, hp: TL.HP, phase: 1, st: 'intro', stT: 0, t: 0, hurtT: 99,
               cd: 0, next: 0, face: -1, t0: s.time, huntT: 0, sneezeImm: 0, pendingPhase: 0, caughtN: 0, attack: null };
    ev(s, { t: 'boss_intro', k: 'tailor', x: f.x, y: floorY(s) - 40 });
    stock(s);
  }

  function hurt(s, n) {
    var b = s.boss;
    if (!open(b)) return;
    b.hp -= n; b.hurtT = 0;
    if (b.hp <= 0) {
      b.hp = 0; to(b, 'dying'); s.tailor.shuffle = null; s.tailor.tape = null;
      ev(s, { t: 'boss_dying', k: 'tailor', x: b.x, y: b.y - 30 });
      return;
    }
    var ph = b.hp <= TL.HP / 3 ? 3 : (b.hp <= TL.HP * 2 / 3 ? 2 : 1);
    if (ph > b.phase) { b.phase = ph; b.pendingPhase = ph; }
  }
  function to(b, st) { b.st = st; b.stT = 0; }

  // ---- the shuffle: a run of swaps, two stands at a time changing places (one passes in front of the other)
  function startShuffle(s, b) {
    var tl = s.tailor, n = tl.n, swaps = [], k, live = [];
    for (k = 0; k < tl.figs.length; k++) {
      var f = tl.figs[k];
      if (f.slot >= n) continue;
      live.push(f.slot);
      if (f.st === 'bare' || f.st === 'down') { f.st = 'dressed'; f.wob = 0; ev(s, { t: 'redress', x: f.x, y: floorY(s) - 24 }); }      // (stood up and dressed again)
    }
    var me = real(s).slot, ns = TL.SWAPS[b.phase];
    for (k = 0; k < ns; k++) {
      // every other swap moves him, so he never just sits still while the others go round him
      var a = (k % 2 === 0) ? me : Math.floor(s.rand() * n), c = Math.floor(s.rand() * (n - 1));
      if (c >= a) c++;
      swaps.push([a, c]);
      if (a === me) me = c; else if (c === me) me = a;
    }
    tl.shuffle = { swaps: swaps, k: 0, t: 0, T: TL.SWAP_T[b.phase] };
    if (b.phase >= 3) { tl.coverWant = true; ev(s, { t: 'cover', x: tl.figs[0].x }); }
    to(b, 'shuffle');
    ev(s, { t: 'shuffle', n: swaps.length });
  }
  function figAt(s, slot) { var f = s.tailor.figs; for (var i = 0; i < f.length; i++) if (f[i].slot === slot && f[i].st !== 'off') return f[i]; return null; }
  function stepShuffle(s, b) {
    var tl = s.tailor, sh = tl.shuffle, C = s.L.tailor;
    // (in the last phase the sheets are thrown over first, and only taken off when it is done)
    if (tl.coverWant && tl.cover < TL.COVER_T) { tl.cover++; return; }
    if (sh.k >= sh.swaps.length) {
      if (tl.cover > 0) { if (tl.cover === TL.COVER_T) ev(s, { t: 'uncover', x: tl.figs[0].x }); tl.coverWant = false; tl.cover--; if (tl.cover > 0) return; }
      tl.shuffle = null;
      to(b, 'hunt'); b.cd = 40; b.huntT = 0;
      return;
    }
    var sw = sh.swaps[sh.k], fa = figAt(s, sw[0]), fb = figAt(s, sw[1]);
    if (sh.t === 0) { fa.x0 = fa.x; fa.x1 = C.slots[sw[1]]; fb.x0 = fb.x; fb.x1 = C.slots[sw[0]]; fa.depth = 1; fb.depth = -1; ev(s, { t: 'swap', x: (fa.x + fb.x) / 2 }); }
    sh.t++;
    var u = Math.min(1, sh.t / sh.T), e = u * u * (3 - 2 * u);
    fa.x = fa.x0 + (fa.x1 - fa.x0) * e; fb.x = fb.x0 + (fb.x1 - fb.x0) * e;
    if (u >= 1) { fa.slot = sw[1]; fb.slot = sw[0]; fa.x = fa.x1; fb.x = fb.x1; fa.depth = fb.depth = 0; sh.k++; sh.t = 0; }
  }

  function step(s) {
    var C = s.L.tailor;
    if (!C || !s.tailor) return;
    var tl = s.tailor, p = s.p, G = s.groups.BOSS;
    if (!s.boss && G && G.awake && !G.done && G.hold && s.mode === 'foot') intro(s);
    var b = s.boss, live = !p.dead && s.status === 'play';
    for (var i = 0; i < tl.figs.length; i++) {
      var f = tl.figs[i];
      f.hurtT++;
      if (f.wob > 0) f.wob--;
      if (f.roll >= 0) {                                         // (a spare rolling in from the side to its place)
        var u = Math.min(1, ++f.roll / 50);
        f.x = f.x0 + (f.x1 - f.x0) * u * (2 - u);
        if (u >= 1) f.roll = -1;
      }
    }
    stepTape(s);
    if (b) stepBoss(s, b, live);
  }

  function stepBoss(s, b, live) {
    var tl = s.tailor, me = real(s);
    b.t++; b.stT++; b.hurtT++;
    if (b.sneezeImm > 0) b.sneezeImm--;
    b.x = me.x;
    if (b.st === 'dead') return;
    // caught in a cloud of spice, the one who sneezes is him
    if ((b.st === 'hunt' || b.st === 'tell') && b.sneezeImm <= 0) {
      for (var i = 0; i < s.clouds.length; i++) {
        var c = s.clouds[i];
        if (c.str >= 0.35 && I.inCloud(c, me.x, floorY(s) - TL.STAND_H - 22, 6)) { to(b, 'sneeze'); ev(s, { t: 'sneeze', who: 'boss', x: me.x, y: floorY(s) - TL.STAND_H }); break; }
      }
    }
    switch (b.st) {
      case 'intro':
        // he shows himself (a wave and a word from the one that is him), then stands stock still among them
        if (b.stT === 20) to(b, 'show');
        break;
      case 'show':
        if (b.stT >= TL.SHOW) { b.t0 = s.time; ev(s, { t: 'boss_start', k: 'tailor' }); startShuffle(s, b); }
        break;
      case 'shuffle':
        stepShuffle(s, b);
        break;
      case 'hunt':
        if (!live) break;
        b.huntT++;
        if (b.huntT >= TL.HUNT_MAX) { startShuffle(s, b); break; }
        if (--b.cd <= 0) {
          var kinds = b.phase === 1 ? ['scissors'] : (b.phase === 2 ? ['scissors', 'pins'] : ['scissors', 'pins', 'tape']);
          b.attack = kinds[b.next++ % kinds.length];
          to(b, 'tell');
          ev(s, { t: 'tell', k: 'tl_' + b.attack, x: me.x, y: floorY(s) - 40 });
        }
        break;
      case 'tell':
        if (b.stT >= TL.TELL[b.attack]) { throwAt(s, b, me); to(b, 'throw'); }
        break;
      case 'throw':
        if (b.stT >= 18) { to(b, 'hunt'); b.cd = TL.HUNT_REST[b.phase]; }
        break;
      case 'sneeze':
        if (b.stT % 28 === 8) ev(s, { t: 'achoo', x: me.x, y: floorY(s) - TL.STAND_H - 30, face: s.p.x < me.x ? -1 : 1 });
        if (b.stT >= TL.SNEEZE) { to(b, 'hunt'); b.cd = 30; b.sneezeImm = TL.SNEEZE_IMM; }
        break;
      case 'caught':
        if (b.stT >= TL.CAUGHT || b.caughtHits >= TL.CATCH_HITS) {
          if (b.pendingPhase) { to(b, 'stun'); phase(s, b); }
          else startShuffle(s, b);
        }
        break;
      case 'stun':
        if (b.stT >= TL.STUN) startShuffle(s, b);
        break;
      case 'dying':
        if (b.stT % 12 === 4) ev(s, { t: 'tape_wind', x: me.x, y: floorY(s) - 26 });
        if (b.stT >= TL.DIE) die(s, b);
        break;
    }
  }
  // a phase reached: a pickup out of the shop, a fifth dummy in, and the sacks put back
  function phase(s, b) {
    var tl = s.tailor, me = real(s), fy = floorY(s);
    b.pendingPhase = 0;
    s.pickups.push({ id: s.nextId++, k: b.phase === 2 ? 'gren' : 'hmg', x: me.x, y: fy - 40, vx: -60 - s.rand() * 40, vy: -170, air: true, t: 0, gone: false });
    if (TL.FIGS[b.phase] > tl.n) {
      for (var i = 0; i < tl.figs.length; i++) {
        var f = tl.figs[i];
        if (f.st === 'off') { f.st = 'dressed'; f.x = s.cam + s.viewW + 20; f.x0 = f.x; f.x1 = s.L.tailor.slots[f.slot]; f.roll = 0; ev(s, { t: 'roll_in', x: f.x1 }); }
      }
      tl.n = TL.FIGS[b.phase];
    }
    stock(s);
    ev(s, { t: 'boss_phase', k: 'tailor', n: b.phase, x: me.x, y: fy - 40 });
  }

  // ---- what he throws, from where he stands
  function throwAt(s, b, me) {
    var p = s.p, fy = floorY(s), dir = p.x < me.x ? -1 : 1, hx = me.x + dir * 8, hy = fy - TL.STAND_H - 26;
    if (b.attack === 'scissors') {
      // at chest height, where his chest is when he stands: down on your knees and they go over
      var a = clamp(Math.atan2((p.y - 27) - hy, Math.max(30, Math.abs(p.x - hx))), -0.25, 0.25);
      s.bullets.push({ x: hx, y: hy, vx: dir * Math.cos(a) * TL.SCISSORS_V, vy: Math.sin(a) * TL.SCISSORS_V, life: T.E_BULLET_LIFE, own: false, src: 'tailor scissors', art: 'tl_scissors', spin: dir });
      ev(s, { t: 'snip', x: hx, y: hy });
    } else if (b.attack === 'pins') {
      fan(s, hx, hy, p, TL.PINS, TL.PIN_V, TL.PIN_SPREAD, 'tailor pins');
      ev(s, { t: 'pins', x: hx, y: hy });
    } else {
      s.tailor.tape = { x0: hx, dir: dir, len: 0, st: 'out', t: 0 };
      ev(s, { t: 'tape', x: hx, y: fy - TL.TAPE_Y });
    }
  }
  function fan(s, x, y, p, n, v, spread, src) {
    var a = Math.atan2((p.y - 17) - y, p.x - x);
    for (var k = 0; k < n; k++) {
      var aa = a + (k - (n - 1) / 2) * spread;
      s.bullets.push({ x: x, y: y, vx: Math.cos(aa) * v, vy: Math.sin(aa) * v, life: T.E_BULLET_LIFE, own: false, src: src, art: 'tl_pin' });
    }
  }
  // the measuring tape: out along the floor at ankle height, and whoever it catches is hauled in to him
  function stepTape(s) {
    var tp = s.tailor.tape, p = s.p;
    if (!tp) return;
    tp.t++;
    if (tp.st === 'out') {
      tp.len += TL.TAPE_V * DT;
      var tipX = tp.x0 + tp.dir * tp.len, ty = floorY(s) - TL.TAPE_Y;
      if (!p.dead && p.inv <= 0 && s.mode === 'foot') {
        var pb = Sim.playerBox(p);
        if (ty >= pb.y0 && ty <= pb.y1 && (tp.dir > 0 ? tipX >= pb.x0 : tipX <= pb.x1) && Math.min(tp.x0, tipX) <= pb.x1 && Math.max(tp.x0, tipX) >= pb.x0) {
          if (I.hurtPlayer(s, tp.x0, 'tailor tape') && !p.dead) { p.knockT = 16; p.knockV = -tp.dir * 230; }
          ev(s, { t: 'yank', x: p.x, y: p.y });
          tp.st = 'hold'; tp.t = 0;
        }
      }
      if (tp.len >= TL.TAPE_MAX) { tp.st = 'hold'; tp.t = 0; }
    } else if (tp.st === 'hold') {
      if (tp.t >= TL.TAPE_HOLD) tp.st = 'back';
    } else {
      tp.len -= TL.TAPE_V * 1.4 * DT;
      if (tp.len <= 0) s.tailor.tape = null;
    }
  }

  // ---- the end: his own tape winds round him, and the dummies go over (stuffed with stolen chillies)
  function die(s, b) {
    var G = s.groups.BOSS, tl = s.tailor, me = real(s), fy = floorY(s), i;
    to(b, 'dead');
    s.score += TL.PTS;
    s.stats.bossT = s.time - b.t0;
    G.hold = false;
    ev(s, { t: 'boss_dead', k: 'tailor', x: me.x, y: fy - 40, pts: TL.PTS });
    for (i = 0; i < tl.figs.length; i++) {
      var f = tl.figs[i];
      if (f.real || !standing(f)) continue;
      f.st = 'down'; f.fall = (f.x < me.x ? -1 : 1);
      ev(s, { t: 'topple', x: f.x, y: fy - 20 });
      I.addCloud(s, f.x, fy - 24, 18, 'red', 150, 0);
      for (var k = 0; k < TL.CHILLIES; k++) {
        s.pickups.push({ id: s.nextId++, k: 'chilli', x: f.x, y: fy - 30, vx: (s.rand() - 0.5) * 220, vy: -160 - s.rand() * 120, air: true, t: 0, gone: false });
      }
    }
    me.st = 'empty';
    // and he hops down off his stand, wrapped up like a parcel
    var w = I.spawnEnemy(s, { g: 'BOSS', k: 'rifle', post: 1 }, me.x);
    G.hostile--;
    w.hostile = false; w.ext = 'tailor'; w.wrapped = true; w.noKnife = true; w.look = 'tailor';
    w.st = 'stagger'; w.stT = 0; w.air = false; w.face = -1; w.vx = 0; w.y = fy;
  }
  function man(s, e) {
    var p = s.p, L = s.L, dx = p.x - e.x;
    if (!e.wrapped) return;
    if (e.st === 'stagger') {
      if (e.stT < 48) { if (e.stT % 12 === 0) ev(s, { t: 'wrap_hop', x: e.x, y: e.y }); e.x -= 20 * DT; e.walkD += 20 * DT; e.y = groundY(L, e.x); }
      else { e.st = 'daze'; e.stT = 0; }
      return;
    }
    if (e.st === 'daze') {
      if (e.stT > 40) { e.st = 'surr'; e.stT = 0; ev(s, { t: 'surrender', x: e.x, y: e.y, id: e.id, k: 'tailor' }); }
      return;
    }
    if (e.st === 'surr') {
      e.face = dx >= 0 ? 1 : -1;
      if (!e.captured && !p.dead && Math.abs(dx) < 15 && Math.abs(p.y - e.y) < 26) {
        e.captured = true; e.stT = 0;
        s.score += TL.BOSS_PTS;
        s.stats.captures++;
        if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
        ev(s, { t: 'capture', x: e.x, y: e.y, id: e.id, pts: TL.BOSS_PTS });
      }
      if (e.captured && e.stT > 70) {
        // (off he hops, the way he came)
        e.x -= 30 * DT; e.y = groundY(L, e.x); e.walkD += 30 * DT; e.face = -1;
        if (e.x < s.cam - 24) { e.alive = false; e.st = 'gone'; e.deadT = 999; }
      }
    }
  }

  // ------------------------------------------------------------------ what the rest of the game asks
  // figures in the order a shot meets them: the one passing in front first
  function order(s) {
    var f = s.tailor.figs.slice();
    f.sort(function (a, c) { return c.depth - a.depth; });
    return f;
  }
  function shot(s, bl) {
    var tl = s.tailor, b = s.boss;
    if (!tl) return false;
    var figs = order(s);
    for (var i = 0; i < figs.length; i++) {
      var f = figs[i];
      if (!standing(f) || !inBox(bl.x, bl.y, figBox(s, f), 1)) continue;
      f.hurtT = 0;
      // (before the fight, under a sheet, or as he dies: they only stop a shot)
      if (!b || !fighting(b) || tl.cover > 0) { ev(s, { t: 'hit', kind: 'cloth', x: bl.x, y: bl.y }); return true; }
      if (f.real) {
        ev(s, { t: 'hit', kind: 'body', x: bl.x, y: bl.y });
        var was = b.st;
        if (was === 'caught') b.caughtHits++;
        hurt(s, 1);
        if (b.st !== 'dying' && (was === 'hunt' || was === 'tell' || was === 'throw' || was === 'sneeze')) caught(s, b);
        return true;
      }
      if (f.st === 'dressed') {
        // a dummy shot by mistake: its clothes tear, and the pins in them spring back at whoever shot it
        f.st = 'bare'; f.wob = 12;
        fan(s, f.x - (bl.vx > 0 ? 6 : -6), floorY(s) - TL.STAND_H - 24, s.p, TL.BACKFIRE_PINS, TL.BACKFIRE_V, TL.BACKFIRE_SPREAD, 'dummy pins');
        ev(s, { t: 'shred', x: f.x, y: floorY(s) - TL.STAND_H - 24, first: !tl.said.shred });
        tl.said.shred = 1;
        return true;
      }
      // shot again, it goes over (and is stood up again at the next shuffle)
      f.st = 'down'; f.fall = bl.vx > 0 ? 1 : -1;
      ev(s, { t: 'topple', x: f.x, y: floorY(s) - 20 });
      return true;
    }
    return false;
  }
  function caught(s, b) {
    var tl = s.tailor;
    tl.tape = null;
    to(b, 'caught');
    b.caughtN++; b.caughtHits = 1;
    ev(s, { t: 'caught', x: b.x, y: floorY(s) - 44, n: b.caughtN });
  }
  // the gun's help (and AUTO) only goes for him with a clear line to him: it does not fire through a dummy for you
  function aim(s, m, consider) {
    var b = s.boss, tl = s.tailor;
    if (!tl || !b || !open(b) || tl.cover > 0 || !shown(b)) return;
    var me = real(s), fb = figBox(s, me), dir = me.x >= m.sx ? 1 : -1, far = (me.x - m.sx) * dir;
    for (var i = 0; i < tl.figs.length; i++) {
      var f = tl.figs[i], d = (f.x - m.sx) * dir;
      if (!f.real && standing(f) && d > -TL.FIG_HW && d < far) return;
    }
    consider(me.x, (fb.y0 + fb.y1) / 2 - 4);
  }
  function touch(s, x, y) {
    var tl = s.tailor;
    if (!tl) return false;
    for (var i = 0; i < tl.figs.length; i++) if (standing(tl.figs[i]) && inBox(x, y, figBox(s, tl.figs[i]), 2)) return true;
    return false;
  }
  function blast(s, x, y, r, kind, own) {
    var tl = s.tailor, b = s.boss;
    if (!tl || !own || !b || !fighting(b)) return;
    for (var i = 0; i < tl.figs.length; i++) {
      var f = tl.figs[i];
      if (!standing(f)) continue;
      var fb = figBox(s, f), nx = clamp(x, fb.x0, fb.x1), ny = clamp(y, fb.y0, fb.y1);
      if ((nx - x) * (nx - x) + (ny - y) * (ny - y) >= (r + 4) * (r + 4)) continue;
      if (f.real) {
        var was = b.st;
        if (was === 'caught') b.caughtHits += TL.GREN_DMG;
        hurt(s, TL.GREN_DMG);
        if (b.st !== 'dying' && (was === 'hunt' || was === 'tell' || was === 'throw' || was === 'sneeze')) { caught(s, b); b.caughtHits = TL.GREN_DMG; }
      }
      else if (tl.cover <= 0) { f.st = 'down'; f.fall = f.x < x ? -1 : 1; ev(s, { t: 'topple', x: f.x, y: floorY(s) - 20 }); }      // (a blast just knocks a dummy over: no pins)
    }
  }

  Sim.ext.tailor = { create: create, step: step, man: man, shot: shot, aim: aim, touch: touch, blast: blast, hurt: hurt, open: open, fighting: fighting,
                     real: real, figBox: figBox, standing: standing, shown: shown, floorY: floorY };
})();
if (typeof module !== 'undefined') module.exports = Sim;
