// boss.js - the battery's pride: a fishing boat the Commander has taught to fly. It hovers over the lava rise on four
// rotors, and he works it from the watchtower with a television remote.
// It can be shot wherever it is. What it does, in turn: a bombing run (get behind it), three aimed shots from the gun in
// its chin (keep moving), a pair of little drones (shoot them or step aside), and, once it is hurt, a low pass with the
// horn going (get down). A third of the way through it sheds grenades, two thirds a heavy MG. When it has had enough it
// comes down on the launcher it was guarding, and the Commander would like a word.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var B = Sim.B = {
    HP: 280, HW: 38, HH: 13, HOVER: 62,
    SPEED: [0, 44, 56, 70],                        // how fast it drifts after him, by phase
    REST: [0, 100, 84, 66],                        // ticks between one thing and the next
    BOMB_V: 98, BOMB_GAP: 24, BOMBS: [0, 3, 4, 5], BOMB_R: 24, BOMB_G: 560, BOMB_TELL: 36,
    GUN_V: 120, GUN_TELL: 40, GUN_SHOTS: [0, 2, 2, 3], GUN_GAP: 18,
    SWOOP_V: 260, SWOOP_TELL: 62, SWOOP_Y: 37,
    INTRO: 130, STUN: 90,
    GREN_DMG: 5, PTS: 5000, CMDR_PTS: 1000,
    GUN: [25, 10], BARREL: 15                      // where the gun hangs under the bow, and how long it is
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function bounds(s) {
    var L = s.L.boss;
    return [Math.max(L.left, s.cam + s.viewW * s.laneL) + B.HW - 6, Math.min(L.right, s.cam + s.viewW * (1 - s.laneR)) - B.HW + 6];
  }
  // where his shots land on the boat: anywhere on the screen (it keeps to the middle anyway, but for its low passes)
  function reach(s, x) { return x >= s.cam - 10 && x <= s.cam + s.viewW + 10; }
  // (s.boss is whichever boss the level has: this file looks after the boat, kind 'boat', and nothing else)
  function mine(b) { return !!b && b.kind === 'boat'; }
  function open(b) { return mine(b) && b.st !== 'intro' && b.st !== 'dying' && b.st !== 'dead'; }

  function create(s) {
    if (!s.L.boss) return;
    s.boss = null; s.cmdr = null;
    s.site = { launcher: 'ok' };
    if (s.groups.BOSS && s.groups.BOSS.done) s.site.launcher = 'wreck';
  }

  function intro(s) {
    var L = s.L.boss, G = s.groups.BOSS;
    s.boss = { kind: 'boat', full: B.HP, label: 'BOAT', x: L.rise[0], y: L.rise[1], x0: L.rise[0], y0: L.rise[1], vx: 0, hp: B.HP, phase: 1, st: 'intro', stT: 0, t: 0, hurtT: 99, cd: 0, next: 0, dir: -1, n: 0, tilt: 0, t0: s.time, lowY: 0, face: -1 };
    var e = I.spawnEnemy(s, { g: 'BOSS', k: 'cmdr', post: 1 }, L.tower[0] + L.towerW / 2);
    G.hostile--;                                   // he is nobody's target: the boat is
    e.hostile = false; e.ext = 'boss'; e.st = 'watch'; e.y = L.tower[1]; e.plat = -2; e.face = -1; e.noKnife = true; e.shoutT = 0;
    s.cmdr = e;
    ev(s, { t: 'boss_intro', x: s.boss.x, y: s.boss.y });
  }

  function hurt(s, n) {
    var b = s.boss;
    if (!open(b)) return;
    b.hp -= n; b.hurtT = 0;
    if (b.hp <= 0) {
      b.hp = 0; b.st = 'dying'; b.stT = 0; b.vx = 0; b.vy = -40;
      ev(s, { t: 'boss_dying', x: b.x, y: b.y });
      return;
    }
    var ph = b.hp <= B.HP / 3 ? 3 : (b.hp <= B.HP * 2 / 3 ? 2 : 1);
    if (ph > b.phase) {
      b.phase = ph; b.pendingStun = true;
    }
  }

  function step(s) {
    var L = s.L.boss;
    if (!L) return;
    var G = s.groups.BOSS, p = s.p;
    if (!s.boss) { if (G && G.awake && !G.done && G.hold && s.mode === 'foot') intro(s); else return; }
    if (!mine(s.boss)) return;
    var b = s.boss, bd = bounds(s), left = bd[0], right = bd[1], gy = groundY(s.L, clamp(b.x, 0, s.L.width - 1));
    if (b.st === 'dead') return;
    b.t++; b.stT++; b.hurtT++;
    var hover = B.HOVER + Math.sin(b.t / 14) * 4, live = !p.dead && s.status === 'play';
    // a part has just gone: it staggers, and something useful falls off it. (Not in the middle of a low pass.)
    if (b.pendingStun && b.st !== 'swoop' && b.st !== 'swooptell' && b.st !== 'dying') {
      b.pendingStun = false; b.st = 'stun'; b.stT = 0; b.vx = 0;
      s.pickups.push({ id: s.nextId++, k: b.phase === 2 ? 'gren' : 'hmg', x: clamp(b.x, left, right), y: b.y + 12, vx: (s.rand() - 0.5) * 60, vy: -90, air: true, t: 0, gone: false });
      ev(s, { t: 'boss_phase', n: b.phase, x: b.x, y: b.y });
    }
    switch (b.st) {
      case 'intro':
        var u = Math.min(1, b.stT / B.INTRO), k = u * u * (3 - 2 * u), hx = clamp((left + right) / 2 + 30, left, right);
        b.x = b.x0 + (hx - b.x0) * k; b.y = b.y0 + (B.HOVER - b.y0) * k;
        if (b.stT >= B.INTRO) { b.st = 'idle'; b.stT = 0; b.cd = 50; b.t0 = s.time; ev(s, { t: 'boss_start' }); }
        break;
      case 'idle':
        var tx = clamp(live ? p.x : b.x, left, right), v = B.SPEED[b.phase] * DT;
        b.x += clamp(tx - b.x, -v, v);
        b.y += clamp(hover - b.y, -1.2, 1.2);
        b.tilt = clamp((tx - b.x) / 60, -1, 1);
        if (live && --b.cd <= 0) {
          var menu = b.phase === 1 ? ['bomb', 'gun'] : (b.phase === 2 ? ['bomb', 'gun', 'launch'] : ['swoop', 'bomb', 'launch', 'gun']);
          var pick = menu[b.next++ % menu.length];
          b.stT = 0; b.n = 0;
          if (pick === 'bomb') { b.st = 'bombtell'; b.dir = p.x >= b.x ? 1 : -1; if (Math.abs(p.x - b.x) < 24) b.dir = b.x > (left + right) / 2 ? -1 : 1; b.face = b.dir; ev(s, { t: 'tell', k: 'bomb', x: b.x, y: b.y, dir: b.dir }); }
          else if (pick === 'gun') { b.st = 'guntell'; b.face = p.x >= b.x ? 1 : -1; ev(s, { t: 'tell', k: 'bgun', x: b.x, y: b.y }); }
          else if (pick === 'launch') { b.st = 'launch'; }
          else {
            b.st = 'swooptell'; b.dir = p.x < (left + right) / 2 ? -1 : 1;      // it starts from the side he is not on
            b.x0 = b.x; b.y0 = b.y; b.lowY = groundY(s.L, clamp(p.x, 0, s.L.width - 1)) - B.SWOOP_Y; b.face = -b.dir;
            ev(s, { t: 'tell', k: 'swoop', x: b.x, y: b.y, dir: b.dir });
          }
        }
        break;
      case 'bombtell':
        b.y += clamp(hover - b.y, -1.2, 1.2);
        b.tilt = b.dir * 0.6;
        if (b.stT >= B.BOMB_TELL) { b.st = 'bomb'; b.stT = 0; b.n = 0; }
        break;
      case 'bomb':
        b.x += b.dir * B.BOMB_V * DT;
        b.y += clamp(hover - b.y, -1.2, 1.2);
        b.tilt = b.dir;
        if (b.stT % B.BOMB_GAP === 1 && b.n < B.BOMBS[b.phase]) {
          b.n++;
          s.bombs.push({ id: s.nextId++, kind: 'bbomb', own: false, x: b.x, y: b.y + 14, vx: b.dir * 24, vy: 30, air: true, fuse: 9999, bounced: 0, t: 0, impact: true, r: B.BOMB_R, g: B.BOMB_G });
          ev(s, { t: 'bomb_drop', x: b.x, y: b.y + 14 });
        }
        if (b.n >= B.BOMBS[b.phase] || b.x <= left || b.x >= right) { b.x = clamp(b.x, left, right); if (b.n >= B.BOMBS[b.phase] || b.stT > 30) { b.st = 'idle'; b.stT = 0; b.cd = B.REST[b.phase]; } }
        break;
      case 'guntell':
        b.y += clamp(hover - b.y, -1.2, 1.2);
        b.tilt = clamp((p.x - b.x) / 80, -1, 1) * 0.5;
        if (b.stT >= B.GUN_TELL) { b.st = 'gun'; b.stT = 0; b.n = 0; }
        break;
      case 'gun':
        b.y += clamp(hover - b.y, -1.2, 1.2);
        if (b.stT % B.GUN_GAP === 1 && live) {
          var px0 = b.x + b.face * B.GUN[0], py0 = b.y + B.GUN[1], ax = p.x - px0, ay = (p.y - 17) - py0, al = Math.sqrt(ax * ax + ay * ay) || 1;
          var gx = px0 + ax / al * B.BARREL, gyy = py0 + ay / al * B.BARREL;
          s.bullets.push({ x: gx, y: gyy, vx: ax / al * B.GUN_V, vy: ay / al * B.GUN_V, life: 260, own: false, big: true, src: 'boss gun' });
          ev(s, { t: 'eshot', k: 'boss', x: gx, y: gyy, face: ax >= 0 ? 1 : -1 });
          b.n++;
        }
        if (b.n >= B.GUN_SHOTS[b.phase] || !live) { b.st = 'idle'; b.stT = 0; b.cd = B.REST[b.phase]; }
        break;
      case 'launch':
        b.y += clamp(hover - b.y, -1.2, 1.2);
        if (b.stT === 10 || (b.stT === 34 && b.phase >= 3)) {      // one little drone, two once it is badly hurt
          var d = Sim.ext.drive.addDrone(s, b.x + (b.n ? 14 : -14), b.y + 12, b.n, true);
          d.wait = 0; b.n++;
          ev(s, { t: 'launch', x: d.x, y: d.y });
        }
        if (b.stT >= 54) { b.st = 'idle'; b.stT = 0; b.cd = B.REST[b.phase]; }
        break;
      case 'swooptell':
        // out to one side and down to head height, horn going
        var su = Math.min(1, b.stT / B.SWOOP_TELL), sk = su * su * (3 - 2 * su), sx = b.dir < 0 ? left - 26 : right + 26;
        b.x = b.x0 + (sx - b.x0) * sk; b.y = b.y0 + (b.lowY - b.y0) * sk;
        b.tilt = -b.dir * 0.8;
        if (b.stT >= B.SWOOP_TELL) { b.st = 'swoop'; b.stT = 0; b.vx = -b.dir * B.SWOOP_V; ev(s, { t: 'swoop', x: b.x, y: b.y, dir: -b.dir }); }
        break;
      case 'swoop':
        b.x += b.vx * DT;
        b.tilt = b.vx > 0 ? 1 : -1;
        if (live && p.inv <= 0) {
          var pb = Sim.playerBox(p);
          if (pb.x1 > b.x - B.HW && pb.x0 < b.x + B.HW && pb.y0 < b.y + B.HH && pb.y1 > b.y - B.HH) I.hurtPlayer(s, b.x - b.vx, 'boss low pass');
        }
        if ((b.vx > 0 && b.x >= right + 26) || (b.vx < 0 && b.x <= left - 26)) { b.st = 'climb'; b.stT = 0; b.x0 = b.x; b.y0 = b.y; }
        break;
      case 'climb':
        var cu = Math.min(1, b.stT / 44), ck = cu * cu * (3 - 2 * cu), cx = b.x0 < (left + right) / 2 ? left + 20 : right - 20;
        b.x = b.x0 + (cx - b.x0) * ck; b.y = b.y0 + (B.HOVER - b.y0) * ck;
        b.tilt = 0;
        if (b.stT >= 44) { b.st = 'idle'; b.stT = 0; b.cd = B.REST[b.phase]; }
        break;
      case 'stun':
        b.y += clamp(hover + 6 - b.y, -1.5, 1.5);
        b.x += Math.sin(b.stT * 0.9) * 0.8;
        b.x = clamp(b.x, left, right);
        b.tilt = Math.sin(b.stT * 0.5) * 0.8;
        if (b.stT % 16 === 4) I.explode(s, b.x + (s.rand() - 0.5) * 50, b.y + (s.rand() - 0.5) * 14, 12, 'kdrone', true);
        if (b.stT >= B.STUN) { b.st = 'idle'; b.stT = 0; b.cd = 30; }
        break;
      case 'dying':
        // it makes for the launcher, burning, and does not quite clear it
        var lx = L.launcher[0] + 40, ly = groundY(s.L, lx) - 30;
        b.vy = (b.vy || 0) + 150 * DT;
        b.x += clamp(lx - b.x, -70 * DT, 70 * DT);
        b.y += b.vy * DT;
        b.tilt = Math.sin(b.stT * 0.35) * 1.2;
        if (b.stT % 9 === 2) I.explode(s, b.x + (s.rand() - 0.5) * 56, b.y + (s.rand() - 0.5) * 18, 12, 'kdrone', true);
        if (b.y >= ly) {
          b.y = ly; b.st = 'dead';
          s.site.launcher = 'wreck';
          s.score += B.PTS;
          s.stats.bossT = s.time - b.t0;
          G.hold = false;
          ev(s, { t: 'boss_dead', x: b.x, y: b.y, pts: B.PTS });
          I.explode(s, b.x, groundY(s.L, b.x) - 10, 46, 'drum', true);
          I.explode(s, b.x - 34, groundY(s.L, b.x) - 6, 40, 'drum', true);
          I.explode(s, b.x + 30, groundY(s.L, b.x) - 14, 40, 'drum', true);
          // the little ones go with it
          for (var i = 0; i < s.drones.length; i++) Sim.ext.drive.popDrone(s, s.drones[i], false);
          if (s.cmdr && s.cmdr.alive) { var c = s.cmdr; c.st = 'fall'; c.stT = 0; c.air = true; c.vx = -66; c.vy = -170; }
        }
        break;
    }
  }

  // the Commander: on his tower while it flies, on the sand with his hands up when it does not
  function man(s, e) {
    var p = s.p, L = s.L, dx = p.x - e.x;
    if (e.st === 'watch') { e.face = dx >= 0 ? 1 : -1; e.shoutT++; return; }
    if (e.st === 'fall') {
      e.vy = Math.min(T.MAX_FALL, e.vy + T.GRAV * DT);
      e.x += e.vx * DT; e.y += e.vy * DT;
      var gy = groundY(L, e.x);
      if (e.vy > 0 && e.y >= gy) { e.y = gy; e.air = false; e.vx = 0; e.vy = 0; e.st = 'daze'; e.stT = 0; e.plat = -1; ev(s, { t: 'thud', x: e.x, y: e.y }); }
      return;
    }
    if (e.st === 'daze') {
      if (e.stT > 54) { e.st = 'surr'; e.stT = 0; ev(s, { t: 'surrender', x: e.x, y: e.y, id: e.id }); }
      return;
    }
    if (e.st === 'surr') {
      e.face = dx >= 0 ? 1 : -1;
      if (!e.captured && !p.dead && Math.abs(dx) < 15 && Math.abs(p.y - e.y) < 26) {
        e.captured = true; e.stT = 0;
        s.score += B.CMDR_PTS;
        s.stats.captures++;
        if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
        ev(s, { t: 'capture', x: e.x, y: e.y, id: e.id, pts: B.CMDR_PTS });
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
    if (!open(b) || !reach(s, b.x)) return false;
    if (bl.x < b.x - B.HW || bl.x > b.x + B.HW || bl.y < b.y - B.HH || bl.y > b.y + B.HH + 4) return false;
    ev(s, { t: 'hit', kind: 'metal', x: bl.x, y: bl.y });
    hurt(s, 1);
    return true;
  }
  function aim(s, m, consider) { var b = s.boss; if (open(b) && reach(s, b.x)) consider(b.x, b.y + 4); }
  function touch(s, x, y) { var b = s.boss; return !!(open(b) && x > b.x - B.HW && x < b.x + B.HW && y > b.y - B.HH && y < b.y + B.HH + 4); }
  function blast(s, x, y, r, kind, own) {
    var b = s.boss;
    if (!own || !open(b) || kind === 'kdrone' || kind === 'bbomb') return;
    var nx = clamp(x, b.x - B.HW, b.x + B.HW), ny = clamp(y, b.y - B.HH, b.y + B.HH);
    if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < (r + 4) * (r + 4)) hurt(s, B.GREN_DMG);
  }

  Sim.ext.boss = { create: create, step: step, man: man, shot: shot, aim: aim, touch: touch, blast: blast, hurt: hurt, bounds: bounds, open: open };
})();
if (typeof module !== 'undefined') module.exports = Sim;
