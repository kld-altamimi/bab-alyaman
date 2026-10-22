// roaster.js - the Big Roaster: the Scorpion's quartermaster has bolted the port's great copper coffee roaster onto a
// tank. It holds the yard in front of the old lighthouse, with him in the open cab at the back, stoking.
// It can be shot anywhere. Its turns: a spray of hot beans from the drum's spout, flat and high (get down) or, once it
// is hurt, flat and low (jump it); a lob of roast bombs (they throw a shadow where they will land: step aside); steam
// from the grille at anyone who stands close in front of it (back off); once the chimney has gone, a pour of burning
// beans rolling along the ground (jump it); and when the drum has cracked, a lunge across the yard to a line it shows
// first (be behind the line). A third of the way through it sheds grenades, two thirds a heavy MG. When it has had
// enough the drum bursts, it rains roast coffee, and the quartermaster climbs out with his hands up.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var R = Sim.R = {
    HP: 300, HW: 56, TOP: 74,                     // half its length, and how tall it stands (to the top of the hopper)
    BODY: 40,                                     // the hull and tracks: what pushes Yazeed back, and what a low shot hits
    SPEED: [0, 26, 32, 40],                       // how fast it shuffles about, by phase
    REST: [0, 92, 76, 62],                        // ticks between one thing and the next
    SPOUT: [-48, -46],                            // the drum's spout, from the middle of the tracks (it faces left)
    GRILLE: [-58, -14],                           // where the steam comes out
    BEAN_V: 190, SPRAY_TELL: 44, SPRAY_N: [0, 3, 3, 4], SPRAY_GAP: 12, HIGH: 31, LOW: 7,
    LOB_TELL: 34, LOBS: [0, 2, 3, 4], LOB_R: 22, LOB_G: 520,
    STEAM_TELL: 28, STEAM_T: 40, STEAM_REACH: 78, STEAM_H: 30, CLOSE: 74,
    POUR_TELL: 40, POUR_V: 112, POUR_H: 12, POUR_W: 14,
    LUNGE_BACK: 34, LUNGE_TELL: 46, LUNGE_V: 230, LUNGE_STOP: 150,
    INTRO: 170, STUN: 84, DIE: 96,
    GREN_DMG: 5, PTS: 6000, BOSS_PTS: 1000, BEANS: 14
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function mine(b) { return !!b && b.kind === 'roaster'; }
  function open(b) { return mine(b) && b.st !== 'intro' && b.st !== 'dying' && b.st !== 'dead'; }
  // the stretch of the yard it may use: the level's, kept clear of the thumbs' lanes
  function bounds(s) {
    var L = s.L.roaster;
    return [Math.max(L.left, s.cam + s.viewW * s.laneL) + R.HW, Math.min(L.right, s.cam + s.viewW * (1 - s.laneR) + 30) - R.HW + 20];
  }
  function front(b) { return b.x - R.HW; }
  function hitBox(b, x, y, pad) {
    pad = pad || 0;
    if (x < b.x - R.HW - pad || x > b.x + R.HW + pad || y > b.y + pad || y < b.y - R.TOP - pad) return false;
    // (above the hull only the drum and the cab stand up: the front corner above the hull is empty)
    if (y < b.y - R.BODY && x < b.x - 46) return false;
    return true;
  }

  function create(s) {
    if (!s.L.roaster) return;
    s.boss = null; s.waves = [];
  }

  function intro(s) {
    var L = s.L.roaster;
    s.boss = { kind: 'roaster', full: R.HP, label: 'ROASTER', x: L.enter[0], y: L.enter[1], vx: 0, hp: R.HP, phase: 1, st: 'intro', stT: 0, t: 0, hurtT: 99,
               cd: 0, next: 0, face: -1, n: 0, hi: true, t0: s.time, lungeTo: 0, tread: 0, heat: 0, steamT: 0, closeT: 0, rock: 0 };
    ev(s, { t: 'boss_intro', k: 'roaster', x: s.boss.x, y: s.boss.y });
  }

  function hurt(s, n) {
    var b = s.boss;
    if (!open(b)) return;
    b.hp -= n; b.hurtT = 0;
    if (b.hp <= 0) {
      b.hp = 0; b.st = 'dying'; b.stT = 0; b.vx = 0;
      s.waves.length = 0;
      ev(s, { t: 'boss_dying', k: 'roaster', x: b.x, y: b.y - 40 });
      return;
    }
    var ph = b.hp <= R.HP / 3 ? 3 : (b.hp <= R.HP * 2 / 3 ? 2 : 1);
    if (ph > b.phase) { b.phase = ph; b.pendingStun = true; }
  }

  function to(b, st, extra) { b.st = st; b.stT = 0; if (extra) for (var k in extra) b[k] = extra[k]; }
  function rest(b) { to(b, 'idle'); b.cd = R.REST[b.phase]; }

  function step(s) {
    var L = s.L.roaster;
    if (!L) return;
    var G = s.groups.BOSS, p = s.p;
    if (!s.boss) { if (G && G.awake && !G.done && G.hold && s.mode === 'foot') intro(s); else return; }
    var b = s.boss;
    if (!mine(b)) return;
    stepWaves(s);
    if (b.st === 'dead') return;
    b.t++; b.stT++; b.hurtT++;
    var bd = bounds(s), left = bd[0], right = bd[1], live = !p.dead && s.status === 'play', mx0 = b.x;
    b.y = groundY(s.L, clamp(b.x, 0, s.L.width - 1));
    // a part has just gone: it shudders, and something useful falls off it (not in the middle of a lunge)
    if (b.pendingStun && b.st !== 'lunge' && b.st !== 'dying') {
      b.pendingStun = false; to(b, 'stun');
      s.pickups.push({ id: s.nextId++, k: b.phase === 2 ? 'gren' : 'hmg', x: front(b) - 10, y: b.y - 60, vx: -70 - s.rand() * 40, vy: -150, air: true, t: 0, gone: false });
      ev(s, { t: 'boss_phase', k: 'roaster', n: b.phase, x: b.x + (b.phase === 2 ? 30 : -6), y: b.y - (b.phase === 2 ? 92 : 56) });
    }
    switch (b.st) {
      case 'intro':
        // it rolls down from behind the lighthouse to where it means to fight
        var hx = clamp(L.home, left, right);
        b.vx = -Math.max(30, Math.min(90, (b.x - hx) * 1.2));
        b.x += b.vx * DT;
        if (b.x <= hx || b.stT >= R.INTRO) { b.x = Math.min(b.x, hx); to(b, 'idle'); b.cd = 50; b.t0 = s.time; b.vx = 0; ev(s, { t: 'boss_start', k: 'roaster' }); }
        break;
      case 'idle':
        // it keeps its distance: about a third of a screen from him, and never closer to the left than it must
        var want = clamp(live ? p.x + 200 : b.x, left, right), v = R.SPEED[b.phase] * DT;
        b.vx = clamp(want - b.x, -v, v) / DT;
        b.x += b.vx * DT;
        var close = live && front(b) - p.x < R.CLOSE && Math.abs(p.y - b.y) < 40;
        b.closeT = close ? b.closeT + 1 : 0;
        if (live && b.closeT > 26) { to(b, 'steamtell'); b.closeT = 0; ev(s, { t: 'tell', k: 'steam', x: front(b), y: b.y - 14 }); break; }
        if (live && --b.cd <= 0) {
          var menu = b.phase === 1 ? ['spray', 'lob', 'spray'] : (b.phase === 2 ? ['spray', 'pour', 'lob', 'spray'] : ['lunge', 'spray', 'pour', 'lob']);
          var pick = menu[b.next++ % menu.length];
          b.n = 0;
          if (pick === 'spray') {
            // high (get down) to begin with; once hurt it mixes in low ones (jump them)
            b.hi = b.phase === 1 ? true : (b.next % 2 === 0);
            to(b, 'spraytell');
            ev(s, { t: 'tell', k: b.hi ? 'spray_hi' : 'spray_lo', x: b.x + R.SPOUT[0], y: b.y + R.SPOUT[1] });
          } else if (pick === 'lob') { to(b, 'lobtell'); ev(s, { t: 'tell', k: 'lob', x: b.x, y: b.y - R.TOP }); }
          else if (pick === 'pour') { to(b, 'pourtell'); ev(s, { t: 'tell', k: 'pour', x: b.x + R.SPOUT[0], y: b.y + R.SPOUT[1] }); }
          else { to(b, 'back'); }
        }
        break;
      case 'spraytell':
        b.vx = 0;
        if (b.stT >= R.SPRAY_TELL) to(b, 'spray', { n: 0 });
        break;
      case 'spray':
        // flat volleys of three beans, close together, at one height: over a man who is down, or under a man in the air
        if (b.stT % R.SPRAY_GAP === 1 && b.n < R.SPRAY_N[b.phase]) {
          b.n++;
          var sx = b.x + R.SPOUT[0], sy = b.y - (b.hi ? R.HIGH : R.LOW);
          for (var k = 0; k < 3; k++) {
            s.bullets.push({ x: sx - k * 7, y: sy + (k === 1 ? -1 : 0), vx: -R.BEAN_V * (1 - k * 0.03), vy: 0, life: 200, own: false, bean: true, hot: true, src: 'roaster beans' });
          }
          ev(s, { t: 'rspray', x: sx, y: sy, hi: b.hi });
        }
        if (b.n >= R.SPRAY_N[b.phase] && b.stT > R.SPRAY_GAP * R.SPRAY_N[b.phase] + 6) rest(b);
        break;
      case 'lobtell':
        b.vx = 0;
        if (b.stT >= R.LOB_TELL) to(b, 'lob', { n: 0 });
        break;
      case 'lob':
        // roast bombs out of the hopper, at him and either side of him
        if (b.stT % 10 === 1 && b.n < R.LOBS[b.phase]) {
          var spread = [0, -46, 40, -86, 78][b.n], tx = clamp((live ? p.x + p.vx * 0.4 : b.x - 160) + spread, s.cam + 20, front(b) - 30);
          var hx0 = b.x - 4, hy0 = b.y - R.TOP - 2, tt = 1.15, vx0 = (tx - hx0) / tt, vy0 = ((b.y - 4) - hy0 - 0.5 * R.LOB_G * tt * tt) / tt;
          s.bombs.push({ id: s.nextId++, kind: 'bbomb', own: false, x: hx0, y: hy0, vx: vx0, vy: vy0, air: true, fuse: 9999, bounced: 0, t: 0, impact: true, r: R.LOB_R, g: R.LOB_G, art: 'roastbomb' });
          ev(s, { t: 'rlob', x: hx0, y: hy0 });
          b.n++;
        }
        if (b.n >= R.LOBS[b.phase] && b.stT > 30) rest(b);
        break;
      case 'steamtell':
        b.vx = 0;
        if (b.stT >= R.STEAM_TELL) { to(b, 'steam'); ev(s, { t: 'steam_jet', x: front(b), y: b.y - 14 }); }
        break;
      case 'steam':
        // a jet of steam along the ground in front of the grille
        if (live && p.inv <= 0) {
          var f0 = front(b);
          if (p.x > f0 - R.STEAM_REACH && p.x < f0 + 6 && p.y > b.y - R.STEAM_H) I.hurtPlayer(s, f0, 'roaster steam');
        }
        if (b.stT >= R.STEAM_T) rest(b);
        break;
      case 'pourtell':
        b.vx = 0;
        if (b.stT >= R.POUR_TELL) {
          to(b, 'pour');
          s.waves.push({ x: front(b) - 6, y: b.y, vx: -R.POUR_V * (b.phase >= 3 ? 1.15 : 1), t: 0 });
          ev(s, { t: 'pour', x: front(b), y: b.y });
        }
        break;
      case 'pour':
        if (b.stT >= 30) rest(b);
        break;
      case 'back':
        // the lunge: it backs up to the far side, shows where it will stop, revs, and goes
        b.vx = 60;
        b.x = Math.min(right, b.x + b.vx * DT);
        if (b.x >= right || b.stT >= R.LUNGE_BACK) {
          b.lungeTo = clamp(Math.max(left, s.cam + s.viewW * s.laneL + R.LUNGE_STOP), left, right);
          to(b, 'lungetell'); b.vx = 0;
          ev(s, { t: 'tell', k: 'lunge', x: b.lungeTo - R.HW, y: b.y });
        }
        break;
      case 'lungetell':
        if (b.stT >= R.LUNGE_TELL) { to(b, 'lunge'); ev(s, { t: 'lunge', x: b.x, y: b.y }); }
        break;
      case 'lunge':
        b.vx = -R.LUNGE_V;
        b.x += b.vx * DT;
        if (b.x <= b.lungeTo) { b.x = b.lungeTo; b.vx = 0; to(b, 'brake'); ev(s, { t: 'brake', x: front(b), y: b.y }); }
        break;
      case 'brake':
        if (b.stT >= 40) rest(b);
        break;
      case 'stun':
        b.vx = 0;
        b.rock = Math.sin(b.stT * 0.9);
        if (b.stT % 14 === 4) I.explode(s, b.x + (s.rand() - 0.5) * 70, b.y - 20 - s.rand() * 40, 12, 'kdrone', true);
        if (b.stT >= R.STUN) { b.rock = 0; to(b, 'idle'); b.cd = 30; }
        break;
      case 'dying':
        b.vx = 0;
        b.rock = Math.sin(b.stT * 1.3) * 1.5;
        if (b.stT % 8 === 2) I.explode(s, b.x + (s.rand() - 0.5) * 90, b.y - 10 - s.rand() * 54, 12, 'kdrone', true);
        if (b.stT >= R.DIE) die(s, b);
        break;
    }
    // nobody walks through it: whoever is in its way is put in front of it, and the lunge hurts
    if (b.st !== 'dead' && !p.dead && s.mode === 'foot' && p.y > b.y - R.BODY - 2) {
      var lim = front(b) - 7;
      if (p.x > lim && p.x < b.x + R.HW) {
        var was = p.x;
        p.x = lim;
        if (p.x < s.cam + 9) p.x = s.cam + 9;
        if (b.st === 'lunge' && p.inv <= 0 && I.hurtPlayer(s, b.x, 'roaster lunge') && !p.dead) { p.knockT = 12; p.knockV = -240; }
        if (Math.abs(p.x - was) > 0.01) p.vx = Math.min(p.vx, 0);
      }
    }
    b.tread += b.x - mx0;
  }

  // burning beans rolling along the ground: jump them
  function stepWaves(s) {
    var p = s.p;
    for (var i = s.waves.length - 1; i >= 0; i--) {
      var w = s.waves[i];
      w.t++;
      w.x += w.vx * DT;
      w.y = groundY(s.L, clamp(w.x, 0, s.L.width - 1));
      if (!p.dead && p.inv <= 0 && s.mode === 'foot' && Math.abs(p.x - w.x) < R.POUR_W / 2 + 5 && p.y > w.y - R.POUR_H) I.hurtPlayer(s, w.x + 20, 'roaster pour');
      if (w.x < s.cam - 30) s.waves.splice(i, 1);
    }
  }

  function die(s, b) {
    var G = s.groups.BOSS;
    to(b, 'dead');
    s.score += R.PTS;
    s.stats.bossT = s.time - b.t0;
    G.hold = false;
    ev(s, { t: 'boss_dead', k: 'roaster', x: b.x, y: b.y - 50, pts: R.PTS });
    I.explode(s, b.x - 10, b.y - 50, 46, 'drum', true);
    I.explode(s, b.x - 40, b.y - 16, 40, 'drum', true);
    I.explode(s, b.x + 30, b.y - 30, 40, 'drum', true);
    // the drum bursts: roast coffee all over the yard
    for (var i = 0; i < R.BEANS; i++) {
      var a = (i / (R.BEANS - 1)) * 2 - 1;
      s.pickups.push({ id: s.nextId++, k: 'bean', x: b.x - 6 + a * 10, y: b.y - 70, vx: a * 150 - 30 + (s.rand() - 0.5) * 30, vy: -220 - s.rand() * 120, air: true, t: 0, gone: false });
    }
    // and the quartermaster climbs out of the cab with his hands up
    var e = I.spawnEnemy(s, { g: 'BOSS', k: 'cmdr', post: 1 }, b.x + 30);
    G.hostile--;
    e.hostile = false; e.ext = 'roaster'; e.look = 'quartermaster'; e.qm = true; e.noKnife = true;
    e.st = 'fall'; e.stT = 0; e.air = true; e.plat = -2; e.y = b.y - 62; e.vx = -70; e.vy = -200; e.face = -1;
    s.qm = e;
  }

  // the quartermaster, once he is out: on the ground, dazed, then hands up for the walk back
  function man(s, e) {
    var p = s.p, L = s.L, dx = p.x - e.x;
    if (e.st === 'fall') {
      e.vy = Math.min(T.MAX_FALL, e.vy + T.GRAV * DT);
      e.x += e.vx * DT; e.y += e.vy * DT;
      var gy = groundY(L, e.x);
      if (e.vy > 0 && e.y >= gy) { e.y = gy; e.air = false; e.vx = 0; e.vy = 0; e.st = 'daze'; e.stT = 0; e.plat = -1; ev(s, { t: 'thud', x: e.x, y: e.y }); }
      return;
    }
    if (e.st === 'daze') {
      if (e.stT > 54) { e.st = 'surr'; e.stT = 0; ev(s, { t: 'surrender', x: e.x, y: e.y, id: e.id, k: 'quartermaster' }); }
      return;
    }
    if (e.st === 'surr') {
      e.face = dx >= 0 ? 1 : -1;
      if (!e.captured && !p.dead && Math.abs(dx) < 15 && Math.abs(p.y - e.y) < 26) {
        e.captured = true; e.stT = 0;
        s.score += R.BOSS_PTS;
        s.stats.captures++;
        if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
        ev(s, { t: 'capture', x: e.x, y: e.y, id: e.id, pts: R.BOSS_PTS });
      }
      if (e.captured && e.stT > 70) {
        e.x -= 34 * DT; e.y = groundY(L, e.x); e.walkD += 34 * DT; e.face = -1; e.moving = -1;
        if (e.x < s.cam - 24) { e.alive = false; e.st = 'gone'; e.deadT = 999; }
      }
    }
  }

  // ------------------------------------------------------------------ what the rest of the game asks
  function shot(s, bl) {
    var b = s.boss;
    if (!open(b) || !hitBox(b, bl.x, bl.y, 1)) return false;
    ev(s, { t: 'hit', kind: 'metal', x: bl.x, y: bl.y });
    hurt(s, 1);
    return true;
  }
  function aim(s, m, consider) {
    var b = s.boss;
    if (!open(b)) return;
    consider(b.x - 14, b.y - 44);                  // the drum
    consider(b.x - 30, b.y - 20);                  // and the hull, for a man who is down
  }
  function touch(s, x, y) { var b = s.boss; return !!(open(b) && hitBox(b, x, y, 2)); }
  function blast(s, x, y, r, kind, own) {
    var b = s.boss;
    if (!own || !open(b) || kind === 'kdrone' || kind === 'bbomb') return;        // (its own bombs, shot down, do it no harm)
    var nx = clamp(x, b.x - R.HW, b.x + R.HW), ny = clamp(y, b.y - R.TOP, b.y);
    if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < (r + 4) * (r + 4)) hurt(s, R.GREN_DMG);
  }
  function sweep(s) { /* (the waves sweep themselves) */ }

  Sim.ext.roaster = { create: create, step: step, man: man, shot: shot, aim: aim, touch: touch, blast: blast, sweep: sweep, hurt: hurt, bounds: bounds, open: open, front: front };
})();
if (typeof module !== 'undefined') module.exports = Sim;
