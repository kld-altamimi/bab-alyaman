// sim.js - the game as pure logic: no drawing, no sound, no clock of its own.
// step(state, input) advances one sixtieth of a second and leaves a list of events for whoever draws and plays.
// It runs the same in a browser and under Node, which is how the bots test it.
var Sim = (function () {
  'use strict';
  var DT = 1 / 60;

  // every number here is a starting value, to be tuned by playing
  var T = {
    RUN: 112, CROUCH_RUN: 44, JUMP_V: 350, JUMP_CUT: 128, GRAV: 940, MAX_FALL: 430,
    COYOTE: 6, JUMP_BUF: 7, DROP_T: 16,
    P_HW: 6, P_H: 34, P_HC: 22,
    SIDE_CD: 9, SIDE_TAP: 4, HMG_CD: 4, HMG_AMMO: 200, HMG_SPREAD: 0.035,
    BULLET_V: 450, BULLET_LIFE: 72,                    // (long enough to reach the far edge of the widest picture)
    ASSIST_COS: Math.cos(20 * Math.PI / 180), ASSIST_RANGE: 330,
    GREN_MAX: 10, GREN_CD: 32, GREN_VX: 150, GREN_VY: -125, GREN_G: 720, GREN_FUSE: 80, GREN_R: 34,
    DYN_G: 700, DYN_R: 30, DYN_FUSE: 20,
    E_BULLET_V: 172, E_BULLET_LIFE: 190,
    PLATES: 3, LIVES: 3, INV: 84, RESPAWN_INV: 150, DEATH_T: 72,
    CAM_LEAD: 0.32, CAM_V: 3.2,
    SIGHT: 310,
    // on a phone the edges of the picture sit under the thumbs, so the fight is staged in the middle:
    // Yazeed holds at HOLD of the way across while a gate is shut, and nobody stops to fight inside the two lanes
    HOLD: 0.5, LANE_L: 0.18, LANE_R: 0.25,
    DRUM_FUSE: 54,
    SETTLE: 28,
    // ordinary enemies sooner and more often, in every mission (game-features-R5; Khaled, 23 Oct 00:15: "modest"): the wait
    // before a man's first shot is FIRST of what it was, the rest between his bursts GAP of it. The warnings before he fires
    // (aiming, leaning out, winding up) stay as they were, and so do the bosses
    FIRST: 0.67, GAP: 0.75,
    DIAG: Math.SQRT1_2,
    DOOR_HITS: 14, DOOR_TURN: 14, BASH_REACH: 24, BASH_CD: 50,
    // Mocha: the cook's ladle, up close and at a distance; the roasting house's steam vents; men coming out of doors
    SWING_REACH: 26, SWING_CD: 56, BEAN_G: 420, BEAN_VX: 118,
    VENT_HISS: 42, VENT_BLAST: 38, VENT_W: 10, VENT_H: 66, EMERGE: 22,
    KNIFE_REACH: 20, KNIFE_CD: 18,
    // the Souq: walls in the ground (the rooftops), clouds of chilli out of burst spice sacks and the sneezing they bring
    // on, and the barricades the Dhanabs shut each market with
    STEP_UP: 7,
    CLOUD_R: 30, CLOUD_GROW: 22, CLOUD_LIFE: 270, CLOUD_FADE: 70, CLOUD_DRIFT: 7,
    SNEEZE_T: 132, SNEEZE_IMM: 70, SNEEZE_EVERY: 34,
    P_SNEEZE: 50, P_SNEEZE_SLOW: 22, P_SNEEZE_IMM: 100,
    BAR_GREN: 10, BAR_DRUM: 60, BAR_MINE: 30, BAR_W: 46, BAR_AUTO: 150, BAR_PRESS: 150, SACK_NEAR: 48
  };

  var KIND = {
    rifle: { hw: 6, h: 34, hp: 1, score: 100, speed: 44, rush: 82, lane: 132 },
    bomber: { hw: 6, h: 34, hp: 1, score: 150, speed: 36, lane: 112 },
    door: { hw: 7, h: 36, hp: 3, score: 300, speed: 34, lane: 78 },
    cmdr: { hw: 8, h: 40, hp: 9, score: 500, speed: 40, lane: 60 },
    cook: { hw: 8, h: 38, hp: 4, score: 300, speed: 38, rush: 66, lane: 70 }
  };
  // the car section and the boss are written in files of their own and hook themselves in here
  var X = {};

  function rngMake(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // ------------------------------------------------------------------ the ground and what stands on it
  function groundY(L, x) {
    var g = L.ground, i = x / g.step, n = g.y.length - 1;
    if (i <= 0) return g.y[0];
    if (i >= n) return g.y[n];
    var a = Math.floor(i), f = i - a;
    return g.y[a] * (1 - f) + g.y[a + 1] * f;
  }
  function platY(pl, x) {
    var p = pl.pts, n = p.length;
    if (x < p[0][0] || x > p[n - 1][0]) return null;
    for (var i = 1; i < n; i++) {
      if (x <= p[i][0]) {
        var f = (x - p[i - 1][0]) / (p[i][0] - p[i - 1][0]);
        return p[i - 1][1] + (p[i][1] - p[i - 1][1]) * f;
      }
    }
    return p[n - 1][1];
  }
  function platIndex(L, id) {
    for (var i = 0; i < L.plats.length; i++) if (L.plats[i].id === id) return i;
    return -1;
  }
  function surfaceY(L, plat, x) { return plat < 0 ? groundY(L, x) : platY(L.plats[plat], x); }
  // the highest surface a falling body passes through this tick
  function landing(L, x, yPrev, yNow, ignore) {
    var best = -2, by = 1e9, gy = groundY(L, x);
    if (yNow >= gy) { best = -1; by = gy; }
    for (var i = 0; i < L.plats.length; i++) {
      if (i === ignore) continue;
      var py = platY(L.plats[i], x);
      if (py === null) continue;
      if (yPrev <= py + 3 && yNow >= py && py < by) { best = i; by = py; }
    }
    return best === -2 ? null : { plat: best, y: by };
  }
  // keep a walker on its surface; false when it has walked off an edge
  function follow(L, e) {
    var y = surfaceY(L, e.plat, e.x);
    if (y !== null) { e.y = y; return true; }
    var gy = groundY(L, e.x);
    if (Math.abs(gy - e.y) <= 5) { e.plat = -1; e.y = gy; return true; }
    for (var j = 0; j < L.plats.length; j++) {
      var qy = platY(L.plats[j], e.x);
      if (qy !== null && Math.abs(qy - e.y) <= 5) { e.plat = j; e.y = qy; return true; }
    }
    return false;
  }

  // ------------------------------------------------------------------ making a game
  function create(L, opts) {
    opts = opts || {};
    // a level with a platform that moves (the Souq's scale) gets a copy of its platforms of its own for this game
    if (L.plats && L.plats.some(function (q) { return q.dyn; })) {
      var L2 = {};
      for (var lk in L) L2[lk] = L[lk];
      L2.plats = L.plats.map(function (q) { return q.dyn ? { id: q.id, dyn: true, pts: q.pts.map(function (pt) { return pt.slice(); }) } : q; });
      L = L2;
    }
    var zone = opts.zone || 0;
    var s = {
      L: L, tick: 0, rand: rngMake(opts.seed == null ? 12345 : opts.seed),
      viewW: opts.viewW || 468, viewH: opts.viewH || 216,     // (viewH: the picture's height in the world; larger than 216 only where a level zooms out: Taiz)
      status: 'play', clearT: 0, mode: 'foot', stopT: 0,
      cam: 0, camY: 0, u: 0, zone: zone,        // (camY, u: Taiz's camera goes up as well as along, following a route; elsewhere 0)
      p: null, enemies: [], bullets: [], bombs: [], props: [], pickups: [],
      groups: {}, gates: [], events: [],
      prev: { fire: false, jump: false, grenade: false },
      score: opts.score || 0, zoneScore: opts.score || 0,
      time: opts.time || 0,
      stats: opts.stats || { kills: 0, captures: 0, freed: 0, detainees: 0, shots: 0, hits: 0, plates: 0, deaths: 0, continues: 0, grenades: 0, streakBest: 0, hurtBy: {},
                             knifed: 0, ranOver: 0, flips: 0, bossT: 0, rescued: [] },          // (rescued: where each one freed so far was held)
      streak: 0, radio: opts.radio || 0,
      laneL: opts.lanes ? opts.lanes[0] : T.LANE_L, laneR: opts.lanes ? opts.lanes[1] : T.LANE_R,
      nextId: 1, alarmed: false, boatLine: false, mineSpotted: false, failsafe: 0, gateWait: 0, coverHits: 0, doorHits: 0, quietT: 0, hinted: {}, holdX: null, doorAt: 0, coverAt: 0,
      clouds: [], bars: [], barHits: 0, barAt: 0, barPress: 0
    };
    var sx = L.zones[zone].spawn;
    s.p = {
      x: sx, y: groundY(L, sx), vx: 0, vy: 0, face: 1, air: false, plat: -1, crouch: false, aim: 'fwd',
      jumpBuf: 0, coyote: 0, jumpHeld: false, dropT: 0, dropPlat: -9, knockT: 0, knockV: 0,
      weapon: 'side', ammo: 0, fireCd: 0, fireT: 99, knifeT: 99, grenades: T.GREN_MAX, grenCd: 0, throwT: 99,
      plates: T.PLATES, lives: opts.lives || T.LIVES, inv: zone ? 90 : 0, dead: 0, hurtT: 99, landT: 99, runD: 0, stepD: 0, idleT: 0,
      sneezeT: 0, sneezeImm: 0
    };
    s.cam = Math.max(0, Math.min(sx - s.viewW * 0.3, L.endRight - s.viewW));
    if (zone === 0) s.cam = 0;
    var k, i;
    for (k in L.groups) {
      var g = L.groups[k];
      s.groups[k] = { id: k, awake: false, awakeT: 0, pending: [], hostile: 0, done: g.zone < zone, zone: g.zone, afterT: -1, hold: !!g.hold && g.zone >= zone };
    }
    for (i = 0; i < L.gates.length; i++) {
      var gt = L.gates[i], past = true;
      for (var j = 0; j < gt.groups.length; j++) if (!s.groups[gt.groups[j]].done) past = false;
      s.gates.push({ id: gt.id, x: gt.x, groups: gt.groups, done: past, wall: gt.wall || null });
      if (!past && s.holdX == null) s.holdX = gt.x;
    }
    for (i = 0; i < L.spawns.length; i++) {
      var sp = L.spawns[i], G = s.groups[sp.g];
      if (G.done) continue;
      if (sp.enter || sp.door) G.pending.push({ sp: sp, at: sp.delay || 0 });
      else { spawnEnemy(s, sp, sp.x); }
      // (men who walk in are made when their group wakes; men at posts stand there from the start)
    }
    var nDet = 0;                                   // (everyone held anywhere in the mission, whichever zone this starts in)
    for (i = 0; i < L.props.length; i++) if (L.props[i].k === 'detainee') nDet++;
    s.stats.detainees = Math.max(s.stats.detainees, nDet);
    for (i = 0; i < L.props.length; i++) {
      var pr = L.props[i];
      if (pr.zone < zone) continue;
      // (somebody freed before a continue is not tied up there again, to be counted twice: 22 Oct)
      if (pr.k === 'detainee' && s.stats.rescued && s.stats.rescued.indexOf(pr.x) >= 0) continue;
      var plat = pr.plat ? platIndex(L, pr.plat) : -1;
      var o = { id: s.nextId++, k: pr.k, x: pr.x, y: surfaceY(L, plat, pr.x), plat: plat, t: 0, st: 'idle', gone: false };
      if (pr.k === 'drum') { o.hp = 2; o.paint = pr.paint; o.fuse = -1; }
      if (pr.k === 'mine') { o.fuse = -1; }
      if (pr.k === 'crate') { o.gives = pr.gives; }
      if (pr.k === 'rmine') { o.fuse = -1; }
      if (pr.k === 'detainee') { o.st = 'tied'; o.vy = 0; o.px = pr.x; if (pr.look) { o.look = pr.look; o.cx = o.x; o.cy = o.y; } if (pr.gives) o.gives = pr.gives; }      // (cx, cy: where his counter stays)
      if (pr.k === 'cover') {
        o.x0 = pr.x0; o.x1 = pr.x1; o.top = pr.top; o.openT = 0; o.art = pr.art || null;
        // (a barricade: cover that can be worn down, and that nobody gets past while it stands)
        if (pr.bar) { o.bar = pr.bar; o.hp = o.hp0 = pr.hp || 40; o.hurtT = 99; s.bars.push(o); }
      }
      if (pr.k === 'vent') { o.every = pr.every || 150; o.phase = pr.phase || 0; o.st = 'idle'; }
      if (pr.k === 'spice') { o.col = pr.col || 'red'; }
      s.props.push(o);
    }
    for (var xk in X) if (X[xk].create) X[xk].create(s, opts);
    return s;
  }

  function spawnEnemy(s, sp, x) {
    var L = s.L, K = KIND[sp.k], plat = sp.plat ? platIndex(L, sp.plat) : -1;
    var e = {
      id: s.nextId++, k: sp.k, g: sp.g, x: x, y: surfaceY(L, plat, x), vx: 0, vy: 0, plat: plat, air: false,
      face: sp.enter === -1 ? 1 : -1, hw: K.hw, h: K.h, hp: K.hp, alive: true, hostile: true, post: !!sp.post, look: sp.look || 'worried',
      st: sp.post ? 'wait' : 'walk', stT: 0, cd: Math.round((16 + Math.floor(s.rand() * 34)) * T.FIRST), band: 0, shots: 0, turnT: 0,
      hurtT: 99, deadT: 0, walkD: 0, seen: false, lit: false, captured: false, offT: 0,
      tag: sp.tag || null, behind: sp.behind || null, covered: !!sp.covered, moving: 0, slot: 0
    };
    s.slotN = ((s.slotN || 0) + 1) % 5;
    e.slot = s.slotN * 12;
    if (sp.covered) e.cd += Math.round(60 * T.FIRST);
    if (sp.k === 'rifle') e.band = 96 + s.rand() * 78;
    // his first attack gets made: once he has begun to aim (or to wind up) the first time, nothing stops him until it's
    // made, and he flashes meanwhile, as at the edge (Khaled, 23 Oct: "still feels no one is trying to shoot me": most
    // of them died the moment they stepped in, before they could aim)
    if (sp.k === 'rifle' || sp.k === 'bomber') e.first = true;
    if (sp.k === 'bomber') e.band = 150 + s.rand() * 60;
    if (sp.k === 'door') { e.band = 8; e.cd = Math.round((60 + Math.floor(s.rand() * 30)) * T.FIRST); e.door = T.DOOR_HITS; e.bashCd = 0; }
    if (sp.k === 'cook') { e.band = 70 + s.rand() * 40; e.cd = Math.round((40 + Math.floor(s.rand() * 30)) * T.FIRST); e.swingCd = 0; }
    s.enemies.push(e);
    s.groups[sp.g].hostile++;
    return e;
  }

  function ev(s, o) { s.events.push(o); }

  // ------------------------------------------------------------------ the player
  function playerBox(p) {
    var h = p.crouch ? T.P_HC : T.P_H;
    return { x0: p.x - T.P_HW, x1: p.x + T.P_HW, y0: p.y - h, y1: p.y };
  }
  // where each gun's muzzle sits, measured off the drawn frames: forward of the feet, above the feet
  var MUZZLE = {
    side: { fwd: [18, 23], crouch: [18, 11], up: [8, 43], down: [8, 5], diag: [14, 37], ddiag: [13, 12] },
    hmg: { fwd: [32, 19], crouch: [32, 7], up: [11, 49], down: [8, -11], diag: [22, 39], ddiag: [22, 4] }
  };
  // x, y: the mouth of the gun, where the flash is drawn. sx, sy: where the shot itself starts, back along its line inside
  // the man, so that somebody standing on the muzzle is still hit.
  function muzzle(p) {
    var M = MUZZLE[p.weapon] || MUZZLE.side, a, k;
    if (p.aim === 'up') { a = M.up; return { x: p.x + p.face * a[0], y: p.y - a[1], dx: 0, dy: -1, sx: p.x + p.face * a[0], sy: p.y - 28 }; }
    if (p.aim === 'down') { a = M.down; return { x: p.x + p.face * a[0], y: p.y - a[1], dx: 0, dy: 1, sx: p.x + p.face * a[0], sy: p.y - 12 }; }
    if (p.aim === 'diag') { a = M.diag; k = a[0] - 2; return { x: p.x + p.face * a[0], y: p.y - a[1], dx: p.face * T.DIAG, dy: -T.DIAG, sx: p.x + p.face * 2, sy: p.y - a[1] + k }; }
    if (p.aim === 'ddiag') { a = M.ddiag; k = a[0] - 2; return { x: p.x + p.face * a[0], y: p.y - a[1], dx: p.face * T.DIAG, dy: T.DIAG, sx: p.x + p.face * 2, sy: p.y - a[1] - k }; }
    a = p.crouch ? M.crouch : M.fwd;
    return { x: p.x + p.face * a[0], y: p.y - a[1], dx: p.face, dy: 0, sx: p.x + p.face * 2, sy: p.y - a[1], low: p.crouch };
  }
  function onScreen(s, x, pad) { return x >= s.cam - pad && x <= s.cam + s.viewW + pad; }

  // where a shot will go: straight, unless something hostile sits within 20 degrees of straight
  function assist(s, m, findOnly) {
    var best = null, bd = 1e9, i;
    function consider(tx, ty) {
      var ex = tx - m.sx, ey = ty - m.sy, d = Math.sqrt(ex * ex + ey * ey);       // measured from where the shot starts
      if (d < 4 || d > T.ASSIST_RANGE) return;
      if (s.mode === 'drive' && ty > m.sy + 5) return;                 // from the back of the car the gun does not point down at the road
      if ((ex * m.dx + ey * m.dy) / d >= T.ASSIST_COS && d < bd) { bd = d; best = { dx: ex / d, dy: ey / d }; }
    }
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.st === 'shock' || !onScreen(s, e.x, -2)) continue;
      if (ducked(e)) continue;                                   // head down behind the bags: nothing to aim at
      if (!inReach(s, e.x)) continue;                            // out at the edge, still coming in
      if (doorTop(e) && (e.x - m.sx) * e.face < 0) {
        // a door facing us: aim at what shows over the top of it, from above or once he has lowered it; otherwise at the door, which will not last for ever
        if ((doorUp(e) && m.dy <= 0) || m.low) consider(e.x, e.y - 12);
        else consider(e.x, e.y - 32);
        continue;
      }
      consider(e.x, e.y - (e.covered ? 27 : e.h * 0.56));
    }
    for (i = 0; i < s.bombs.length; i++) {
      var b = s.bombs[i];
      if (!b.own && b.air && !b.gone) consider(b.x, b.y);
    }
    // (the Souq) aiming low, a sack of spice with a Dhanab beside it is worth a shot: it is what the crouch is for
    if (m.low) for (i = 0; i < s.props.length; i++) if (s.props[i].k === 'spice' && !s.props[i].gone && sackGuarded(s, s.props[i])) consider(s.props[i].x, s.props[i].y - 7);
    for (var xk in X) if (X[xk].aim) X[xk].aim(s, m, consider);
    if (findOnly) return best;
    return best || { dx: m.dx, dy: m.dy };
  }

  function shoot(s) {
    var p = s.p, m = muzzle(p), d = assist(s, m, false), hmg = p.weapon === 'hmg';
    if (hmg) {
      var a = (s.rand() - 0.5) * 2 * T.HMG_SPREAD, c = Math.cos(a), sn = Math.sin(a);
      d = { dx: d.dx * c - d.dy * sn, dy: d.dx * sn + d.dy * c };
    }
    // the shot is aimed from the muzzle but starts at the chest, so a man standing on the muzzle is still hit
    var bx0 = m.sx, by0 = m.sy, free = 0;
    for (var ci = 0; ci < s.props.length; ci++) {
      var cv = s.props[ci];
      if (cv.k === 'cover' && p.x >= cv.x0 - 6 && p.x <= cv.x1 + 6) free = cv.id;      // fired from behind it: it does not stop its own side
    }
    var hide = Math.ceil(Math.sqrt((m.x - bx0) * (m.x - bx0) + (m.y - by0) * (m.y - by0)) / (T.BULLET_V * DT));
    s.bullets.push({ x: bx0, y: by0, vx: d.dx * T.BULLET_V, vy: d.dy * T.BULLET_V, life: T.BULLET_LIFE, own: true, hmg: hmg, age: 0, free: free, hide: hide });
    p.fireCd = hmg ? T.HMG_CD : T.SIDE_CD;
    p.fireT = 0;
    s.stats.shots++;
    ev(s, { t: 'shot', w: p.weapon, x: m.x, y: m.y, dx: d.dx, dy: d.dy, aim: p.aim, face: p.face });
    if (hmg) {
      p.ammo--;
      if (p.ammo <= 0) { p.weapon = 'side'; p.ammo = 0; ev(s, { t: 'weapon_empty' }); }
    }
  }

  // a sack with a Dhanab beside it (one who could be fought: on the screen, not still coming in)
  function sackGuarded(s, o) {
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.alive && e.hostile && !e.ext && e.st !== 'sneeze' && Math.abs(e.x - o.x) < T.SACK_NEAR && Math.abs(e.y - o.y) < 40 && inReach(s, e.x)) return true;
    }
    return false;
  }
  // (the Souq) left to itself the gun also works at a barricade standing close in front, once it is on the screen
  function barAhead(s) {
    var p = s.p;
    if (p.face < 0 || p.aim === 'up' || p.aim === 'down') return false;
    for (var i = 0; i < s.bars.length; i++) {
      var o = s.bars[i], dx = o.x0 - p.x;
      if (!o.gone && dx > 0 && dx < T.BAR_AUTO && onScreen(s, o.x0, -12)) return true;
    }
    return false;
  }

  // the jambiya: with somebody at arm's length, the trigger is a slash instead of a shot
  function knifeTarget(s) {
    var p = s.p, best = null, bd = 1e9;
    if (s.mode !== 'foot') return null;
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.st === 'shock' || e.noKnife || !inReach(s, e.x)) continue;
      var fx = (e.x - p.x) * p.face;
      if (fx < -5 || fx > T.KNIFE_REACH + e.hw || Math.abs(e.y - p.y) > 22) continue;
      if (fx < bd) { bd = fx; best = e; }
    }
    return best;
  }
  function knife(s, e) {
    var p = s.p, what = 'body';
    p.fireCd = T.KNIFE_CD; p.knifeT = 0;
    if (doorTop(e) && (p.x - e.x) * e.face > 0) {
      // a door in the way takes the blade: four cuts will see it off
      what = 'door';
      s.doorHits++; if (!s.doorAt) s.doorAt = s.tick;
      e.door -= 4;
      if (e.door <= 0) { e.door = 1; breakDoor(s, e, p.face); }
    } else {
      s.stats.hits++;
      hurtEnemy(s, e, 3, p.face, 'knife');
    }
    s.stats.shots++;
    ev(s, { t: 'slash', x: p.x + p.face * 15, y: p.y - (p.crouch ? 10 : 20), face: p.face, hit: what });
  }

  // a checkpoint fills Yazeed back up: lives to the starting three (extra lives stay) and the armour plates, which are the
  // 4x4's and the Apache's armour too, to full (Khaled, 22 Oct: more players through the Strait's coast road)
  function refill(s) {
    var p = s.p;
    if (!p || p.dead) return;
    var lives = Math.max(0, T.LIVES - p.lives), plates = Math.max(0, T.PLATES - p.plates);
    if (!lives && !plates) return;
    p.lives += lives; p.plates += plates;
    ev(s, { t: 'refill', x: p.x, y: p.y, lives: lives, plates: plates });
  }
  function hurtPlayer(s, fromX, why) {
    var p = s.p;
    if (p.inv > 0 || p.dead || s.status !== 'play') return false;
    s.stats.hurtBy[why] = (s.stats.hurtBy[why] || 0) + 1;
    p.plates--;
    p.hurtT = 0;
    s.stats.plates++;
    s.streak = 0;
    if (p.plates <= 0) {
      p.dead = 1;
      p.vx = (fromX < p.x ? 1 : -1) * 50;
      p.vy = -190;
      p.air = true; p.plat = -2; p.crouch = false;
      s.stats.deaths++;
      ev(s, { t: 'life_lost', x: p.x, y: p.y, why: why });
    } else {
      p.inv = T.INV;
      ev(s, { t: 'plate_lost', x: p.x, y: p.y, left: p.plates });
      if (p.plates === 1) ev(s, { t: 'low_armour' });
    }
    return true;
  }

  function stepPlayer(s, inp) {
    var p = s.p, L = s.L;
    p.fireT++; p.throwT++; p.hurtT++; p.landT++;
    if (p.inv > 0) p.inv--;
    if (p.fireCd > 0) p.fireCd--;
    if (p.grenCd > 0) p.grenCd--;
    if (p.dropT > 0) p.dropT--;
    if (p.sneezeT > 0) p.sneezeT--;
    if (p.sneezeImm > 0) p.sneezeImm--;

    if (p.dead) {
      p.dead++;
      if (p.air) {
        p.vy = Math.min(T.MAX_FALL, p.vy + T.GRAV * DT);
        var py0 = p.y;
        p.x += p.vx * DT;
        if (L.walls && groundY(L, p.x) < p.y - 1) { p.x -= p.vx * DT; p.vx = 0; }          // (thrown against a wall: down it)
        p.y += p.vy * DT;
        var ld = p.vy >= 0 ? landing(L, p.x, py0, p.y, -9) : null;
        if (ld) { p.y = ld.y; p.vy = 0; p.vx = 0; p.air = false; p.plat = ld.plat; ev(s, { t: 'thud', x: p.x, y: p.y }); }
      }
      if (p.dead > T.DEATH_T) {
        p.lives--;
        if (p.lives <= 0) { s.status = 'over'; ev(s, { t: 'over' }); return; }
        p.dead = 0; p.plates = T.PLATES; p.inv = T.RESPAWN_INV;   // the gun in hand and its ammo come back with you (Khaled, 19 Oct)
        p.grenades = Math.max(p.grenades, T.GREN_MAX);
        p.x = Math.max(s.cam + 30, Math.min(p.x, s.cam + s.viewW - 30));
        p.y = groundY(L, p.x) - 70; p.vx = 0; p.vy = 0; p.air = true; p.plat = -2; p.face = 1;
        ev(s, { t: 'respawn', x: p.x, y: p.y });
      }
      return;
    }

    var walking = s.status === 'clear';
    var mx = walking ? (p.x < (L.restX || L.exitX + 12) ? 1 : 0) : (inp.mx > 0 ? 1 : (inp.mx < 0 ? -1 : 0));
    var my = walking ? 0 : (inp.my > 0 ? 1 : (inp.my < 0 ? -1 : 0));
    var jump = !walking && !!inp.jump, fire = !walking && !!inp.fire, gren = !walking && !!inp.grenade;
    var jumpPressed = jump && !s.prev.jump, firePressed = fire && !s.prev.fire, grenPressed = gren && !s.prev.grenade;
    s.prev.jump = jump; s.prev.fire = fire; s.prev.grenade = gren;

    if (jumpPressed) p.jumpBuf = T.JUMP_BUF; else if (p.jumpBuf > 0) p.jumpBuf--;
    p.crouch = !p.air && my > 0;
    if (mx) p.face = mx;
    p.vx = mx * (p.crouch ? T.CROUCH_RUN : T.RUN);
    if (p.sneezeT > T.P_SNEEZE - T.P_SNEEZE_SLOW) p.vx *= 0.45;                             // (the Souq: doubled up with a sneeze)
    if (p.knockT > 0) { p.knockT--; p.vx = p.knockV * (p.knockT + 4) / 16; }           // shoved: for a moment the stick does nothing
    // straight up with the stick straight up, 45 degrees with it pushed up and along; in the air the same two downward
    p.aim = my < 0 ? (mx ? 'diag' : 'up') : (p.air && my > 0 ? (mx ? 'ddiag' : 'down') : 'fwd');

    if (p.jumpBuf > 0 && (!p.air || p.coyote > 0)) {
      p.jumpBuf = 0; p.coyote = 0;
      if (my > 0 && !p.air && p.plat >= 0) {
        p.dropPlat = p.plat; p.dropT = T.DROP_T; p.air = true; p.plat = -2; p.vy = 60; p.crouch = false;
        ev(s, { t: 'drop' });
      } else {
        p.vy = -T.JUMP_V; p.air = true; p.plat = -2; p.jumpHeld = true; p.crouch = false;
        ev(s, { t: 'jump', x: p.x, y: p.y });
      }
    }
    if (p.air) {
      if (p.jumpHeld && !jump) { p.jumpHeld = false; if (p.vy < -T.JUMP_CUT) p.vy = -T.JUMP_CUT; }
      p.vy = Math.min(T.MAX_FALL, p.vy + T.GRAV * DT);
    }

    var prevY = p.y, px0 = p.x;
    p.x += p.vx * DT;
    var lo = s.cam + 9, hi = Math.min(s.cam + s.viewW - 9, L.exitX + 60);
    // a shut gate stops the screen, not the man: he can walk on across it, as far as the lane the next lot will come in by
    if (s.holdX != null) hi = Math.min(hi, s.cam + s.viewW * (1 - s.laneR) - 4);
    // a barricade stops the man: nobody gets past one while it stands, over it or round it
    for (var bi = 0; bi < s.bars.length; bi++) { var br = s.bars[bi]; if (!br.gone && px0 <= br.x0) hi = Math.min(hi, br.x0 - 8); }
    if (p.x < lo) { p.x = lo; if (p.vx < 0) p.vx = 0; }
    if (p.x > hi) { p.x = hi; if (p.vx > 0) p.vx = 0; }
    // the rooftops: a step up of more than STEP_UP is a wall, walked or jumped into, until his feet are over the top of it
    if (L.walls && p.x !== px0 && groundY(L, p.x) < p.y - (p.air ? 0.001 : T.STEP_UP)) { p.x = px0; p.vx = 0; }

    if (!p.air) {
      var ledge = L.walls && p.plat < 0 && groundY(L, p.x) > p.y + T.STEP_UP;               // (walked off the edge of a roof)
      if (ledge || !follow(L, p)) { p.air = true; p.plat = -2; p.coyote = T.COYOTE; p.vy = 0; }
      else if (p.vx) {
        var d = Math.abs(p.vx) * DT;
        p.runD += d; p.stepD += d;
        if (p.stepD > 21) { p.stepD = 0; ev(s, { t: 'step', x: p.x, y: p.y }); }
      } else { p.runD = 0; }
    } else {
      if (p.coyote > 0) p.coyote--;
      p.y += p.vy * DT;
      if (p.vy >= 0) {
        var hit = landing(L, p.x, prevY, p.y, p.dropT > 0 ? p.dropPlat : -9);
        if (hit) {
          p.y = hit.y; p.plat = hit.plat; p.air = false; p.landT = 0; p.jumpHeld = false;
          ev(s, { t: 'land', x: p.x, y: p.y, v: p.vy });
          p.vy = 0;
        }
      }
    }
    p.idleT = (mx || p.air || fire) ? 0 : p.idleT + 1;

    // firing: held, tapped, or left to the gun when auto-fire is on (not in the middle of a sneeze)
    var sneezing = p.sneezeT > 0;
    var want = fire && !sneezing, blade = (fire || inp.auto) && !walking && !sneezing ? knifeTarget(s) : null;
    p.knifeT++;
    if (!want && inp.auto && !walking && !sneezing) want = !!blade || !!assist(s, muzzle(p), true) || (s.bars.length > 0 && barAhead(s));
    if (want && p.fireCd <= 0) { if (blade) knife(s, blade); else shoot(s); }
    else if (firePressed && !blade && !sneezing && p.weapon === 'side' && p.fireCd <= T.SIDE_CD - T.SIDE_TAP - 1) shoot(s);

    if (grenPressed && !sneezing && p.grenCd <= 0 && p.grenades > 0) {
      p.grenades--; p.grenCd = T.GREN_CD; p.throwT = 0;
      s.stats.grenades++;
      var up = p.aim === 'up', dg = p.aim === 'diag';           // lobbed high with the stick up, long and high at 45 degrees
      s.bombs.push({
        id: s.nextId++, kind: 'gren', own: true, x: p.x + p.face * 6, y: p.y - (p.crouch ? 20 : 32),
        vx: p.face * (up ? 60 : (dg ? 128 : T.GREN_VX)) + p.vx * 0.45, vy: up ? -360 : (dg ? -262 : T.GREN_VY), air: true, fuse: up || dg ? T.GREN_FUSE + 30 : T.GREN_FUSE, bounced: 0, t: 0
      });
      ev(s, { t: 'throw', x: p.x, y: p.y });
    }
  }

  // ------------------------------------------------------------------ the Scorpion's men
  function groupOf(s, e) { return s.groups[e.g]; }

  function standDown(s, e) {            // he stops being a threat, one way or another
    if (!e.hostile) return;
    e.hostile = false;
    var G = groupOf(s, e);
    G.hostile--;
    lastMan(s, G);
  }

  function lastMan(s, G) {
    if (G.hostile !== 1 || G.pending.length) return;
    var flag = s.L.groups[G.id].lastManSurrenders;
    if (s.L.groups[G.id].noSurrender) return;
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.g !== G.id || !e.alive || !e.hostile) continue;
      if ((e.k === 'door' && e.door > 0) || e.air || e.st === 'stagger' || e.st === 'sneeze') return;
      if (!flag && s.rand() > 0.3) return;
      if (e.k === 'bomber' && e.lit) return;
      e.st = 'shock'; e.stT = 0;
      return;
    }
  }

  function killEnemy(s, e, dirx, how) {
    if (!e.alive) return;
    var K = KIND[e.k];
    e.alive = false; e.st = 'dead'; e.deadT = 0; e.stT = 0; e.how = how;
    e.vx = (dirx >= 0 ? 1 : -1) * (how === 'blast' ? 110 : 64); e.vy = how === 'blast' ? -230 : -150; e.air = true; e.plat = -2;
    var pts = K.score * (how === 'knife' ? 2 : 1);
    s.score += pts;
    s.stats.kills++;
    if (how === 'knife') s.stats.knifed++;
    if (how === 'ram') s.stats.ranOver++;
    s.streak++;
    if (s.streak > s.stats.streakBest) s.stats.streakBest = s.streak;
    if (s.streak > 0 && s.streak % 6 === 0 && s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
    ev(s, { t: 'die', k: e.k, x: e.x, y: e.y, face: e.face, how: how, id: e.id, door: e.k === 'door' && e.door > 0, pts: pts, look: e.look });
    if (e.k === 'bomber' && e.lit) {
      // he had already lit it
      s.bombs.push({ id: s.nextId++, kind: 'dyn', own: false, x: e.x, y: e.y - 20, vx: e.vx * 0.3, vy: -60, air: true, fuse: 26, bounced: 0, t: 0, loose: true });
    }
    standDown(s, e);
  }

  function breakDoor(s, e, dirx) {
    if (!(e.door > 0)) return;
    e.door = 0; e.st = 'stagger'; e.stT = 0; e.moving = 0; e.lit = false;
    s.score += 100;
    var G = groupOf(s, e);
    if (!G.awake) { G.awake = true; G.awakeT = 0; }
    ev(s, { t: 'door_break', x: e.x, y: e.y, face: e.face, dir: dirx >= 0 ? 1 : -1, id: e.id });
  }

  function hurtEnemy(s, e, dmg, dirx, how) {
    var G = groupOf(s, e);
    if (!G.awake) { G.awake = true; G.awakeT = 0; }
    e.hp -= dmg;
    e.hurtT = 0;
    if (e.hp <= 0) killEnemy(s, e, dirx, how);
  }

  // a man with a door: held up, it covers him to the eyes; dropped while he fires over it, to the chest. Either way it is in front of him only.
  function doorUp(e) { return e.k === 'door' && e.door > 0 && (e.st === 'walk' || e.st === 'wait' || e.st === 'bashw' || e.st === 'bash'); }
  function doorLow(e) { return e.k === 'door' && e.door > 0 && (e.st === 'lean' || e.st === 'fire' || e.st === 'rec'); }
  function doorTop(e) { return doorUp(e) ? 28 : (doorLow(e) ? 18 : 0); }
  // a man behind cover keeps his head down until he comes up to aim; down, only a blast can reach him
  function ducked(e) { return !!e.covered && e.alive && e.hostile && (e.st === 'wait' || e.st === 'walk' || e.st === 'cool'); }
  // The fight is staged in the middle of the screen, clear of the thumbs (inMiddle). A man out in either edge lane is
  // still coming in: he is guarded (he flashes, and nothing hurts him: shots glance off him) and he starts no attack.
  // His shots themselves fly on to the edge of the screen. (Build 9 dropped them where the lane began, which looked like
  // an invisible wall; build 10 let them kill a man the moment he showed, which left nobody a chance to fight.)
  // inReach: where a man can be hurt: the middle. staged: where a man may start an attack of his own: a posted man
  // anywhere in the middle, a walker only once he is properly in.
  function inMiddle(s, x) { return x >= s.cam + s.viewW * s.laneL - 10 && x <= s.cam + s.viewW * (1 - s.laneR) + 10; }
  function inReach(s, x) { return inMiddle(s, x); }
  // (and a man making his first attack: see spawnEnemy)
  function guarded(s, e) { return !!e && e.alive && e.hostile && ((!e.ext && (!inMiddle(s, e.x) || e.emerge > 0)) || (e.first && (e.st === 'aim' || e.st === 'wind'))); }
  function staged(s, e) { return e.post ? inMiddle(s, e.x) : (e.x >= s.cam + s.viewW * s.laneL - 1 && e.x <= s.cam + s.viewW * (1 - s.laneR) + 1); }

  function enemyFire(s, e, aimed, yOff) {
    var p = s.p, mx = e.x + e.face * (e.k === 'rifle' ? 30 : 18), my = e.y - yOff, dx = e.face, dy = 0;
    if (aimed) {
      var tx = p.x - mx, ty = (p.y - 17) - my, d = Math.sqrt(tx * tx + ty * ty) || 1;
      dx = tx / d; dy = ty / d;
      var lim = 0.64;                               // about 40 degrees off level
      if (Math.abs(dy) > lim) { dy = dy < 0 ? -lim : lim; dx = (dx < 0 ? -1 : 1) * Math.sqrt(1 - lim * lim); }
      if ((dx < 0 ? -1 : 1) !== e.face) { dx = e.face; dy = 0; }
    }
    s.bullets.push({ x: mx, y: my, vx: dx * T.E_BULLET_V, vy: dy * T.E_BULLET_V, life: T.E_BULLET_LIFE, own: false,
                     src: e.k + (aimed ? ' aimed' : ' level') + ((e.x - p.x) * p.face > 0 ? ' in front' : ' from behind') });
    ev(s, { t: 'eshot', k: e.k, x: mx, y: my, face: e.face });
  }

  // while he is up, the bags in front of him stop less: a standing shot goes over them
  function upFromCover(s, e) {
    for (var i = 0; i < s.props.length; i++) { var o = s.props[i]; if (o.k === 'cover' && !o.gone && e.x >= o.x0 && e.x <= o.x1) o.openT = 3; }
  }

  function approach(s, e, speed) {
    var p = s.p, dx = p.x - e.x, ad = Math.abs(dx), dir = dx >= 0 ? 1 : -1, moved = 0;
    if (ad > e.band + 10) moved = dir;
    else if (ad < e.band - 46) moved = ad < 8 ? (e.moving || -e.face) : -dir;      // right under or over him: keep going the way he was
    if (moved && e.behind) {
      // stay in the lee of the man with the door for as long as he stands
      for (var q = 0; q < s.enemies.length; q++) {
        var lead = s.enemies[q];
        if (lead.alive && lead.hostile && lead.g === e.g && lead.tag === e.behind) {
          var gap = (e.x - lead.x) * -lead.face;
          if (moved === lead.face && gap < 20) moved = 0;
          break;
        }
      }
    }
    // the two edges of the screen are for walking through, not for standing in
    var inL = s.cam + s.viewW * s.laneL + e.slot, inR = s.cam + s.viewW * (1 - s.laneR) - e.slot;
    if (e.x > inR) { moved = -1; speed = KIND[e.k].lane; } else if (e.x < inL) { moved = 1; speed = KIND[e.k].lane; }
    else if (!e.arrived) { e.arrived = true; e.cd = Math.min(e.cd, 4 + Math.floor(s.rand() * 10)); }
    // nor is the far side of somebody else's sandbags: only the man posted there may use them. A walker who finds them
    // between himself and Yazeed keeps coming until he is through.
    // (it only matters while Yazeed is on the outside of them: once he is in among the bags they stop nothing of his)
    // (a barricade is another matter: nobody comes through that while it stands; see below)
    var bags = null, ci, cv;
    if (!e.covered && e.plat === -1) {
      for (ci = 0; ci < s.props.length; ci++) {
        cv = s.props[ci];
        if (cv.k !== 'cover' || cv.gone || cv.bar || (p.x >= cv.x0 - 6 && p.x <= cv.x1 + 6)) continue;
        var inside = e.x > cv.x0 - 10 && e.x < cv.x1 + 10;
        var across = Math.abs(p.y - e.y) < 30 && ((p.x < cv.x0 && e.x >= cv.x1 + 10) || (p.x > cv.x1 && e.x <= cv.x0 - 10));
        if (inside || across) bags = cv;
      }
      if (bags) moved = dir;                      // through, never stopping or backing up behind them
    }
    if (moved) {
      var nx = e.x + moved * speed * DT, intoBags = false;
      if (!e.covered && !bags && e.plat === -1) {
        for (ci = 0; ci < s.props.length; ci++) {
          cv = s.props[ci];
          if (cv.k === 'cover' && !cv.gone && nx > cv.x0 - 10 && nx < cv.x1 + 10 && (nx - p.x) * moved > 0 && !(p.x >= cv.x0 - 6 && p.x <= cv.x1 + 6)) intoBags = true;
        }
      }
      // don't back off into an edge or behind the bags, and don't walk off a ledge
      if (!intoBags && !(moved < 0 && nx < inL && e.x >= inL) && !(moved > 0 && nx > inR && e.x <= inR) && !barred(s, e, nx)) {
        if (!stepTo(s, e, nx)) moved = 0;
        else e.walkD += speed * DT;
      } else moved = 0;
    }
    return moved;
  }
  // a step along his surface; false (and he stays put) where it ends: a platform's edge, or on the rooftops a step up or
  // down that is a wall or a drop
  function stepTo(s, e, nx) {
    var keep = e.x, L = s.L;
    if (L.walls && e.plat < 0 && Math.abs(groundY(L, nx) - e.y) > T.STEP_UP) return false;
    e.x = nx;
    if (!follow(L, e)) { e.x = keep; return false; }
    return true;
  }
  // a standing barricade between him and where he is going: the far side of it is as far as he comes
  function barred(s, e, nx) {
    for (var i = 0; i < s.bars.length; i++) {
      var o = s.bars[i];
      if (o.gone || e.covered) continue;
      if (e.x >= o.x0 + T.BAR_W - 16 && nx < o.x0 + T.BAR_W - 16) return true;     // (from behind it: as far as its back)
      if (e.x <= o.x0 - 10 && nx > o.x0 - 10) return true;                            // (from Yazeed's side: as far as its face)
    }
    return false;
  }

  function stepEnemy(s, e) {
    var p = s.p, L = s.L, G = groupOf(s, e);
    e.stT++; e.hurtT++;
    if (e.ext && e.alive && X[e.ext] && X[e.ext].man) { X[e.ext].man(s, e); return; }
    if (!e.alive) {
      e.deadT++;
      if (e.air) {
        var y0 = e.y;
        e.vy = Math.min(T.MAX_FALL, e.vy + T.GRAV * DT);
        e.x += e.vx * DT; e.y += e.vy * DT;
        var ld = e.vy >= 0 ? landing(L, e.x, y0, e.y, -9) : null;
        if (ld) { e.y = ld.y; e.air = false; e.vx = 0; e.vy = 0; ev(s, { t: 'thud', x: e.x, y: e.y }); }
      }
      return;
    }
    var dx = p.x - e.x, ad = Math.abs(dx);
    e.seen = G.awake && onScreen(s, e.x, -6);
    if (e.emerge > 0) { e.emerge--; e.face = dx >= 0 ? 1 : -1; return; }          // still in the doorway
    if (e.sneezeImm > 0) e.sneezeImm--;
    if (e.st === 'sneeze') {
      // the Souq: a fit of sneezing in a cloud of chilli. He is in no state to do anything else; behind cover he is
      // doubled up over the top of it, and a door is no use to a man sneezing into it
      if (e.covered) upFromCover(s, e);
      if (e.stT % T.SNEEZE_EVERY === 6) ev(s, { t: 'achoo', x: e.x, y: e.y - e.h + 4, id: e.id, k: e.k, face: e.face });
      if (e.stT >= T.SNEEZE_T) { e.st = e.post ? 'wait' : 'walk'; e.stT = 0; e.sneezeImm = T.SNEEZE_IMM; e.cd = Math.max(e.cd, 24); }
      return;
    }

    if (e.st === 'shock') {              // the last man, weighing his options
      if (e.stT === 1) ev(s, { t: 'drop_weapon', x: e.x, y: e.y, id: e.id });
      if (e.stT > 16) { e.st = 'surr'; e.stT = 0; standDown(s, e); ev(s, { t: 'surrender', x: e.x, y: e.y, id: e.id }); }
      return;
    }
    if (e.st === 'surr') {
      e.face = dx >= 0 ? 1 : -1;
      if (!e.captured && !p.dead && Math.abs(dx) < 15 && Math.abs(p.y - e.y) < 26) {
        e.captured = true; e.stT = 0;
        s.score += KIND[e.k].score * 2;
        s.stats.captures++;
        if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
        ev(s, { t: 'capture', x: e.x, y: e.y, id: e.id });
      }
      if (e.captured && e.stT > 70) {
        e.x -= 34 * DT; follow(L, e); e.walkD += 34 * DT; e.face = -1; e.moving = -1;
        if (e.x < s.cam - 24) { e.alive = false; e.st = 'gone'; e.deadT = 999; }
      }
      return;
    }
    if (!G.awake) return;
    if (!e.seen) {
      // men walking in from the edge keep walking; men at their posts wait to be seen
      if (!e.post) {
        var sp0 = KIND[e.k].lane * DT;
        if (L.walls) {
          // (on the rooftops he keeps to his roof: no stepping off a ledge to get in)
          if (e.x > s.cam + s.viewW - 6) { e.face = -1; if (stepTo(s, e, e.x - sp0)) { e.walkD += sp0; e.moving = -1; } }
          else if (e.x < s.cam + 6) { e.face = 1; if (stepTo(s, e, e.x + sp0)) { e.walkD += sp0; e.moving = 1; } }
        }
        else if (e.x > s.cam + s.viewW - 6) { e.face = -1; e.x -= sp0; follow(L, e); e.walkD += sp0; e.moving = -1; }
        else if (e.x < s.cam + 6) { e.face = 1; e.x += sp0; follow(L, e); e.walkD += sp0; e.moving = 1; }
      }
      return;
    }
    if (!s.alarmed && !p.dead) { s.alarmed = true; ev(s, { t: 'alarm', x: e.x, y: e.y }); }
    if (p.dead || s.status !== 'play') { if (e.st !== 'walk' && e.st !== 'wait') { e.st = e.post ? 'wait' : 'walk'; e.stT = 0; } return; }

    var K = KIND[e.k], home = e.post ? 'wait' : 'walk';
    if (e.k === 'rifle') {
      if (e.st === 'walk' || e.st === 'wait') {
        e.face = dx >= 0 ? 1 : -1;
        var mv = e.st === 'walk' ? approach(s, e, ad > e.band + 60 ? K.rush : K.speed) : 0;
        e.moving = mv;
        e.moveT = mv ? (e.moveT || 0) + 1 : 0;
        if (e.cd > 0) e.cd--;
        if (e.cd <= 0 && ad < T.SIGHT && staged(s, e) && (!mv || e.first || e.moveT > 80 || Math.abs(p.y - e.y) > 22)) { e.st = 'aim'; e.stT = 0; e.moveT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'rifle', x: e.x, y: e.y }); }
      } else if (e.st === 'aim') {
        if (e.covered) upFromCover(s, e);
        if (e.stT >= 24) { e.st = 'burst'; e.stT = 0; e.shots = 0; e.first = false; }
      } else if (e.st === 'burst') {
        if (e.covered) upFromCover(s, e);
        if (e.stT % 8 === 1) {
          var level = Math.abs(p.y - e.y) < 14;
          enemyFire(s, e, !level, 26);
          e.shots++;
          if (e.shots >= 3) { e.st = 'cool'; e.stT = 0; e.cd = Math.round(((e.covered ? 110 : 44) + Math.floor(s.rand() * 50)) * T.GAP); }
        }
      } else if (e.st === 'cool') {
        if (e.stT > 14) { e.st = home; e.stT = 0; }
      }
    } else if (e.k === 'bomber') {
      if (e.st === 'walk' || e.st === 'wait') {
        e.face = dx >= 0 ? 1 : -1;
        var mv2 = e.st === 'walk' ? approach(s, e, K.speed) : 0;
        e.moving = mv2;
        if (e.cd > 0) e.cd--;
        if (!mv2 && e.cd <= 0 && ad < T.SIGHT && ad > 26 && staged(s, e)) { e.st = 'wind'; e.stT = 0; e.lit = true; ev(s, { t: 'tell', k: 'bomber', x: e.x, y: e.y }); }
      } else if (e.st === 'wind') {
        if (e.stT >= 38) {
          e.first = false;
          var Tf = 0.86 + ad / 640, tx = p.x + p.vx * 0.22, sy = e.y - 40, ty = p.y - 2;
          var vx = (tx - (e.x - e.face * 4)) / Tf, vy = (ty - sy - 0.5 * T.DYN_G * Tf * Tf) / Tf;
          if (vx > 270) vx = 270; if (vx < -270) vx = -270;
          s.bombs.push({ id: s.nextId++, kind: 'dyn', own: false, x: e.x - e.face * 4, y: sy, vx: vx, vy: vy, air: true, fuse: T.DYN_FUSE, bounced: 0, t: 0 });
          e.lit = false; e.st = 'throw'; e.stT = 0;
          ev(s, { t: 'lob', x: e.x, y: sy });
        }
      } else if (e.st === 'throw') {
        if (e.stT > 18) { e.st = home; e.stT = 0; e.cd = Math.round((95 + Math.floor(s.rand() * 45)) * T.GAP); }
      }
    } else if (e.k === 'door') {
      var wantFace = dx >= 0 ? 1 : -1;
      if (e.st === 'stagger') {                    // the door has just gone: he looks at his hands
        if (e.stT > 30) { e.st = 'walk'; e.stT = 0; e.cd = Math.round((14 + Math.floor(s.rand() * 16)) * T.FIRST); e.band = 64 + s.rand() * 44; e.arrived = true; }
      } else if (e.door <= 0) {
        // without it he is a man with a pistol and a grudge
        if (e.st === 'walk' || e.st === 'wait') {
          e.face = wantFace;
          e.moving = approach(s, e, 46);
          if (e.cd > 0) e.cd--;
          if (e.cd <= 0 && ad < T.SIGHT && staged(s, e)) { e.st = 'aim'; e.stT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'rifle', x: e.x, y: e.y }); }
        } else if (e.st === 'aim') {
          if (e.stT >= 18) { e.st = 'burst'; e.stT = 0; e.shots = 0; }
        } else if (e.st === 'burst') {
          if (e.stT % 10 === 1) {
            enemyFire(s, e, Math.abs(p.y - e.y) >= 14, 27);
            if (++e.shots >= 2) { e.st = 'cool'; e.stT = 0; e.cd = Math.round((46 + Math.floor(s.rand() * 40)) * T.GAP); }
          }
        } else { if (e.stT > 12) { e.st = 'walk'; e.stT = 0; } }
      } else if (e.st === 'walk' || e.st === 'wait') {
        if (wantFace !== e.face) { e.moving = 0; if (++e.turnT > T.DOOR_TURN) { e.face = wantFace; e.turnT = 0; } }
        else {
          e.turnT = 0;
          e.moving = e.st === 'walk' ? approach(s, e, K.speed) : 0;
        }
        if (e.cd > 0) e.cd--;
        if (e.bashCd > 0) e.bashCd--;
        var close = ad < T.BASH_REACH && Math.abs(p.y - e.y) < 30;
        if (wantFace === e.face && close && e.bashCd <= 0 && inMiddle(s, e.x)) { e.st = 'bashw'; e.stT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'bash', x: e.x, y: e.y }); }
        else if (e.cd <= 0 && wantFace === e.face && ad < 230 && ad > 30 && staged(s, e)) { e.st = 'lean'; e.stT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'door', x: e.x, y: e.y }); }
      } else if (e.st === 'bashw') {               // the door goes back over his shoulder...
        if (e.stT >= 18) {
          e.st = 'bash'; e.stT = 0;
          var fx = (p.x - e.x) * e.face, landed = false;
          if (fx > -4 && fx < T.BASH_REACH + 8 && Math.abs(p.y - e.y) < 30 && !p.dead && hurtPlayer(s, e.x, 'door shove')) {
            landed = true;
            if (!p.dead) { p.knockT = 12; p.knockV = e.face * 260; }
          }
          ev(s, { t: 'bash', x: e.x + e.face * 12, y: e.y - 16, face: e.face, hit: landed });
        }
      } else if (e.st === 'bash') {                // ...and comes down where Yazeed was
        if (e.stT >= 18) { e.st = home; e.stT = 0; e.bashCd = T.BASH_CD; }
      } else if (e.st === 'lean') {
        if (e.stT >= 20) { e.st = 'fire'; e.stT = 0; }
      } else if (e.st === 'fire') {
        if (e.stT === 2 || e.stT === 12 || e.stT === 22) enemyFire(s, e, false, 30);
        if (e.stT >= 30) { e.st = 'rec'; e.stT = 0; }
      } else if (e.st === 'rec') {
        if (e.stT >= 14) { e.st = home; e.stT = 0; e.cd = Math.round((70 + Math.floor(s.rand() * 45)) * T.GAP); }
      }
    } else if (e.k === 'cook') {
      // Mocha's cooks: a pot for a helmet and a ladle for everything else. At a distance he flings a ladleful of hot
      // beans (three, in a fan, falling as they go); up close he swings it.
      if (e.st === 'walk' || e.st === 'wait') {
        e.face = dx >= 0 ? 1 : -1;
        var mv4 = e.st === 'walk' ? approach(s, e, ad > e.band + 60 ? K.rush : K.speed) : 0;
        e.moving = mv4;
        if (e.cd > 0) e.cd--;
        if (e.swingCd > 0) e.swingCd--;
        var reach = ad < T.SWING_REACH && Math.abs(p.y - e.y) < 30;
        if (reach && e.swingCd <= 0 && inMiddle(s, e.x)) { e.st = 'swingw'; e.stT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'swing', x: e.x, y: e.y }); }
        else if (e.cd <= 0 && ad < 230 && ad > 44 && staged(s, e) && Math.abs(p.y - e.y) < 60) { e.st = 'scoop'; e.stT = 0; e.moving = 0; ev(s, { t: 'tell', k: 'scoop', x: e.x, y: e.y }); }
      } else if (e.st === 'scoop') {                // the ladle goes back, full...
        if (e.stT >= 28) { flingBeans(s, e); e.st = 'fling'; e.stT = 0; }
      } else if (e.st === 'fling') {                // ...and over
        if (e.stT >= 16) { e.st = home; e.stT = 0; e.cd = Math.round((96 + Math.floor(s.rand() * 50)) * T.GAP); }
      } else if (e.st === 'swingw') {
        if (e.stT >= 16) {
          e.st = 'swing'; e.stT = 0;
          var fx2 = (p.x - e.x) * e.face, hit2 = false;
          if (fx2 > -4 && fx2 < T.SWING_REACH + 8 && Math.abs(p.y - e.y) < 30 && !p.dead && hurtPlayer(s, e.x, 'ladle')) {
            hit2 = true;
            if (!p.dead) { p.knockT = 10; p.knockV = e.face * 220; }
          }
          ev(s, { t: 'swing', x: e.x + e.face * 14, y: e.y - 20, face: e.face, hit: hit2 });
        }
      } else if (e.st === 'swing') {
        if (e.stT >= 16) { e.st = home; e.stT = 0; e.swingCd = T.SWING_CD; }
      }
    }
  }

  // three hot beans from the ladle, lobbed at where Yazeed is: the middle one lands on him, the others short and long
  function flingBeans(s, e) {
    var p = s.p, mx = e.x + e.face * 12, my = e.y - 34, ad = Math.max(30, Math.abs(p.x - mx));
    var tt = ad / T.BEAN_VX, ty = (p.y - 10) - my;
    for (var k = -1; k <= 1; k++) {
      var vx = e.face * T.BEAN_VX * (1 + k * 0.22), vy = (ty - 0.5 * T.BEAN_G * tt * tt) / tt - 12 * k;
      s.bullets.push({ x: mx, y: my, vx: vx, vy: vy, g: T.BEAN_G, life: 200, own: false, bean: true, src: 'cook beans' });
    }
    ev(s, { t: 'fling', x: mx, y: my, face: e.face });
  }

  // ------------------------------------------------------------------ things that go off
  // the first thing under a point: a platform top or the ground
  function floorUnder(L, x, y) {
    var best = groundY(L, x);
    for (var i = 0; i < L.plats.length; i++) { var py = platY(L.plats[i], x); if (py !== null && py >= y - 3 && py < best) best = py; }
    return best;
  }

  function explode(s, x, y, r, kind, own) {
    var i, p = s.p, fl = floorUnder(s.L, x, y);
    ev(s, { t: 'explode', x: x, y: y, r: r, kind: kind, air: fl - y > 15, floor: fl });
    // (the Strait: a blast by the wreck of the dhow gets a word from Yazeed)
    var bl = s.L.boatLine;
    if (bl && !s.boatLine && (kind === 'gren' || kind === 'dyn') && x > bl[0] && x < bl[1] && y > 110) { s.boatLine = true; ev(s, { t: 'boat' }); }
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.st === 'shock' || guarded(s, e)) continue;
      var ex = e.x - x, ey = (e.y - e.h * 0.5) - y;
      if (ex * ex + ey * ey >= (r + 9) * (r + 9)) continue;
      // a grenade or a stick going off on the door's side of him takes the door, not the man. A drum is another matter.
      if (doorTop(e) && (x - e.x) * e.face > 2 && r < 38) { breakDoor(s, e, ex); continue; }
      hurtEnemy(s, e, 3, ex, 'blast');
    }
    if (!own && !p.dead && s.mode === 'foot') {
      var px = p.x - x, py = (p.y - 16) - y;
      if (px * px + py * py < (r + 1) * (r + 1)) hurtPlayer(s, x, kind);
    }
    for (var xk in X) if (X[xk].blast) X[xk].blast(s, x, y, r, kind, own);
    for (i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.gone) continue;
      if (o.k === 'spice') {                       // (the Souq: a blast bursts any sack near it)
        var sx2 = o.x - x, sy2 = (o.y - 8) - y;
        if (sx2 * sx2 + sy2 * sy2 < (r + 10) * (r + 10)) burstSack(s, o);
        continue;
      }
      if (o.bar) {                                 // a barricade: a grenade knocks a lump out of it, a drum most of it
        var dmg = kind === 'drum' ? T.BAR_DRUM : (kind === 'mine' ? T.BAR_MINE : (own && kind === 'gren' ? T.BAR_GREN : 0));
        if (dmg) {
          var nx2 = Math.max(o.x0, Math.min(o.x0 + T.BAR_W, x)), ny2 = Math.max(o.top, Math.min(o.y, y));
          if ((nx2 - x) * (nx2 - x) + (ny2 - y) * (ny2 - y) < (r + 6) * (r + 6)) hitBar(s, o, dmg, x < o.x0 ? 1 : -1, kind);
        }
        continue;
      }
      if ((o.k !== 'drum' && o.k !== 'mine' && o.k !== 'rmine') || o.fuse >= 0) continue;
      var ox = o.x - x, oy = (o.y - 8) - y;
      if (ox * ox + oy * oy < (r + 12) * (r + 12)) o.fuse = 7;
    }
    for (i = 0; i < s.bombs.length; i++) {
      var b = s.bombs[i];
      if (b.gone) continue;
      var bx = b.x - x, by = b.y - y;
      if (bx * bx + by * by < r * r && b.chain == null && !b.nochain) b.chain = 3;
    }
  }

  // ------------------------------------------------------------------ the Souq: chilli in the air, and barricades
  // a sack of spice burst by a shot or a blast: a cloud of it, which swells, drifts on the breeze and thins out
  function burstSack(s, o) {
    if (o.gone) return;
    o.gone = true;
    addCloud(s, o.x, o.y - 14, T.CLOUD_R, o.col, T.CLOUD_LIFE);
    ev(s, { t: 'spice_burst', x: o.x, y: o.y - 10, col: o.col });
  }
  function addCloud(s, x, y, R, col, life, vx) {
    var c = { id: s.nextId++, x: x, y: y, R: R, r: 0, t: 0, life: life, col: col || 'red', vx: vx == null ? T.CLOUD_DRIFT : vx, str: 0 };
    s.clouds.push(c);
    return c;
  }
  // how much of a cloud there is at its age: 0 to 1, swelling at first and thinning out at the end
  function cloudStr(c) { return Math.min(1, c.t / T.CLOUD_GROW) * Math.min(1, (c.life - c.t) / T.CLOUD_FADE); }
  function inCloud(c, x, y, pad) { var dx = x - c.x, dy = y - c.y, rr = c.r + (pad || 0); return dx * dx + dy * dy < rr * rr; }
  function stepClouds(s) {
    var p = s.p, i, j;
    for (i = s.clouds.length - 1; i >= 0; i--) {
      var c = s.clouds[i];
      c.t++;
      if (c.t >= c.life) { s.clouds.splice(i, 1); continue; }
      c.str = cloudStr(c);
      c.r = c.R * (0.45 + 0.55 * Math.min(1, c.t / T.CLOUD_GROW));
      c.x += c.vx * DT;
      if (c.str < 0.35) continue;                                 // (thinning out: nothing in it to sneeze at)
      // a Dhanab caught in it doubles up sneezing
      for (j = 0; j < s.enemies.length; j++) {
        var e = s.enemies[j];
        if (!e.alive || !e.hostile || e.ext || e.emerge > 0 || e.sneezeImm > 0 || e.st === 'sneeze' || e.st === 'shock' || e.st === 'surr' || e.st === 'stagger') continue;
        if (!inCloud(c, e.x, e.y - e.h * 0.5, e.hw + 2)) continue;
        if (e.k === 'bomber' && e.lit) {
          // the stick he had lit goes down at his feet
          s.bombs.push({ id: s.nextId++, kind: 'dyn', own: false, x: e.x - e.face * 3, y: e.y - 22, vx: -e.face * 20, vy: -60, air: true, fuse: 34, bounced: 0, t: 0, loose: true });
          e.lit = false;
          ev(s, { t: 'fumble', x: e.x, y: e.y - 22 });
        }
        e.st = 'sneeze'; e.stT = 0; e.moving = 0;
        ev(s, { t: 'sneeze', who: 'man', k: e.k, x: e.x, y: e.y, id: e.id });
      }
      // and Yazeed, if he walks into it
      if (!p.dead && s.mode === 'foot' && s.status === 'play' && p.sneezeImm <= 0 && inCloud(c, p.x, p.y - 17, 4)) {
        p.sneezeT = T.P_SNEEZE; p.sneezeImm = T.P_SNEEZE_IMM;
        ev(s, { t: 'sneeze', who: 'p', x: p.x, y: p.y });
        if (!s.hinted.sneeze) { s.hinted.sneeze = 1; ev(s, { t: 'hint', k: 'sneeze' }); }
      }
    }
  }
  // a barricade worn down by a shot, the knife or a blast; when it goes, the way is open and whoever it hid is not hidden
  function hitBar(s, o, dmg, dirx, how) {
    if (o.gone) return;
    o.hp -= dmg; o.hurtT = 0;
    ev(s, { t: 'bar_hit', x: o.x, y: o.top + 8, left: Math.max(0, o.hp), how: how || 'shot' });
    if (o.hp <= 0) breakBar(s, o, dirx);
  }
  function breakBar(s, o, dirx) {
    o.gone = true; o.hp = 0;
    s.score += 300;
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.covered && e.x >= o.x0 - 10 && e.x <= o.x1 + 10) e.covered = false;          // (nothing to hide behind now)
    }
    ev(s, { t: 'bar_break', x: o.x, y: o.y, x0: o.x0, top: o.top, bar: o.bar, dir: dirx >= 0 ? 1 : -1, pts: 300 });
  }
  function barGone(s, id) {
    for (var i = 0; i < s.bars.length; i++) if (s.bars[i].bar === id && !s.bars[i].gone) return false;
    return true;
  }

  function stepBombs(s) {
    var L = s.L, i, j;
    for (i = 0; i < s.bombs.length; i++) {
      var b = s.bombs[i];
      if (b.gone) continue;
      b.t++;
      var G = b.kind === 'gren' ? T.GREN_G : (b.g || T.DYN_G), boom = false;
      if (b.air) {
        var y0 = b.y;
        b.vy += G * DT;
        b.x += b.vx * DT; b.y += b.vy * DT;
        if (b.vy > 0) {
          var ld = landing(L, b.x, y0, b.y, -9);
          if (ld) {
            b.y = ld.y;
            if (b.kind === 'gren' && !b.bounced) {
              b.bounced = 1; b.vy = -b.vy * 0.34; b.vx *= 0.5;
              ev(s, { t: 'bounce', x: b.x, y: b.y });
            } else if (b.kind === 'gren' || b.impact) boom = true;
            else { b.air = false; b.vx = 0; b.vy = 0; ev(s, { t: 'dyn_land', x: b.x, y: b.y }); }
          }
        }
        if (b.own) {
          for (j = 0; j < s.enemies.length; j++) {
            var e = s.enemies[j];
            if (!e.alive || !e.hostile || !inReach(s, e.x)) continue;
            if (b.x > e.x - e.hw - 3 && b.x < e.x + e.hw + 3 && b.y > e.y - e.h && b.y < e.y + 2) { boom = true; break; }
          }
          for (var xk in X) if (!boom && X[xk].touch && X[xk].touch(s, b.x, b.y)) boom = true;
        }
        if (b.kind === 'gren' && --b.fuse <= 0) boom = true;
        if (b.kind === 'dyn' && b.loose && --b.fuse <= 0) boom = true;
      } else {
        if (--b.fuse <= 0) boom = true;
      }
      if (b.chain != null && --b.chain <= 0) boom = true;       // set off by another blast
      if (b.y > L.height + 40 || b.x < s.cam - 80 || b.x > s.cam + s.viewW + 120) { b.gone = true; continue; }
      if (boom) {
        b.gone = true;
        explode(s, b.x, b.y - 2, b.r || (b.kind === 'gren' ? T.GREN_R : T.DYN_R), b.boom || b.kind, b.own);
      }
    }
  }

  function inBox(x, y, x0, y0, x1, y1) { return x >= x0 && x <= x1 && y >= y0 && y <= y1; }
  // their shots stop in a barricade's pile as his do (theirs do it no harm)
  function barStops(s, b) {
    for (var i = 0; i < s.bars.length; i++) {
      var o = s.bars[i];
      if (!o.gone && b.x >= o.x0 && b.x <= o.x0 + T.BAR_W && b.y >= o.top + 2) return true;
    }
    return false;
  }

  function stepBullets(s) {
    var L = s.L, p = s.p, i, j, k;
    for (i = 0; i < s.bullets.length; i++) {
      var b = s.bullets[i];
      if (b.gone) continue;
      b.age = (b.age || 0) + 1;
      if (b.g) b.vy += b.g * DT;                         // (a bean falls as it flies)
      for (k = 0; k < 2 && !b.gone; k++) {
        b.x += b.vx * DT * 0.5; b.y += b.vy * DT * 0.5;
        if (b.own) {
          // his shots fly on to the edge of the screen (they are dropped there, below)
          for (j = 0; j < s.enemies.length && !b.gone; j++) {
            var e = s.enemies[j];
            if (!e.alive || !e.hostile || e.st === 'shock' || e.hidden || !onScreen(s, e.x, 0)) continue;        // (hidden: right down out of sight, Taiz's missile man locking on)
            if (!inBox(b.x, b.y, e.x - e.hw - 1, e.y - (ducked(e) ? 18 : e.h), e.x + e.hw + 1, e.y)) continue;
            if (guarded(s, e)) { b.gone = true; ev(s, { t: 'hit', kind: 'guard', x: b.x, y: b.y }); continue; }     // still coming in: it glances off
            var dt = doorTop(e);
            if (dt && b.vx !== 0 && (b.vx > 0 ? 1 : -1) === -e.face && b.y > e.y - dt) {
              b.gone = true;
              s.stats.hits++;
              s.doorHits++; if (!s.doorAt) s.doorAt = s.tick;
              ev(s, { t: 'hit', kind: 'door', x: b.x, y: b.y, left: e.door - 1 });
              if (--e.door <= 0) { e.door = 1; breakDoor(s, e, b.vx); }
            } else {
              b.gone = true;
              s.stats.hits++;
              ev(s, { t: 'hit', kind: 'body', x: b.x, y: b.y });
              hurtEnemy(s, e, 1, b.vx, 'shot');
            }
          }
          for (j = 0; j < s.props.length && !b.gone; j++) {
            var o = s.props[j];
            if (o.gone) continue;
            if (o.k === 'cover') {
              if (b.free !== o.id && b.x >= o.x0 && b.x <= o.x1 && b.y >= o.top + (o.openT > 0 ? 9 : 0)) {
                b.gone = true;
                if (o.bar) {
                  // a barricade: the shot knocks a little out of it (where it hits the pile itself)
                  if (b.x <= o.x0 + T.BAR_W) { s.stats.hits++; s.barHits++; if (!s.barAt) s.barAt = s.tick; ev(s, { t: 'hit', kind: 'wood', x: b.x, y: b.y }); hitBar(s, o, 1, b.vx); }
                  else ev(s, { t: 'hit', kind: 'bags', x: b.x, y: b.y });
                } else { s.coverHits++; if (!s.coverAt) s.coverAt = s.tick; ev(s, { t: 'hit', kind: 'bags', x: b.x, y: b.y }); }
              }
              continue;
            }
            if (o.k === 'spice' && inBox(b.x, b.y, o.x - 7, o.y - 15, o.x + 7, o.y)) { b.gone = true; s.stats.hits++; burstSack(s, o); continue; }
            if (o.k === 'drum' && inBox(b.x, b.y, o.x - 7, o.y - 26, o.x + 7, o.y)) {      // a little taller than it is drawn: a level shot from standing must not sail over
              b.gone = true; s.stats.hits++;
              ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y });
              if (--o.hp <= 0 && o.fuse < 0) { o.fuse = T.DRUM_FUSE; ev(s, { t: 'drum_lit', x: o.x, y: o.y }); }
            } else if (o.k === 'mine' && inBox(b.x, b.y, o.x - 11, o.y - 24, o.x + 11, o.y)) {
              b.gone = true; s.stats.hits++;
              if (o.fuse < 0) o.fuse = 1;
            }
          }
          for (j = 0; j < s.bombs.length && !b.gone; j++) {
            var d = s.bombs[j];
            if (d.gone || d.own || !d.air) continue;
            if (Math.abs(b.x - d.x) < 6 && Math.abs(b.y - d.y) < 6) {
              b.gone = true; s.stats.hits++;
              d.gone = true;
              explode(s, d.x, d.y, d.r || T.DYN_R, d.boom || (d.kind === 'bbomb' ? 'bbomb' : 'dyn'), d.kind === 'bbomb');      // (the boss's bombs burst harmlessly when shot)
            }
          }
          for (var xk in X) if (!b.gone && X[xk].shot && X[xk].shot(s, b)) { b.gone = true; s.stats.hits++; }
        } else if (s.mode === 'drive') {
          if (X.drive.hitCar(s, b)) b.gone = true;
        } else if (s.mode === 'fly') {
          if (X.fly.hitHeli(s, b)) b.gone = true;
        } else if (s.bars.length && barStops(s, b)) {
          b.gone = true;
          ev(s, { t: 'hit', kind: 'wood', x: b.x, y: b.y });
        } else if (!p.dead && p.inv <= 0) {
          var bx = playerBox(p);
          if (inBox(b.x, b.y, bx.x0, bx.y0, bx.x1, bx.y1)) {
            b.gone = true;
            hurtPlayer(s, b.x - b.vx, b.src || 'bullet');
          }
        }
        if (!b.gone && b.y >= groundY(L, b.x)) {
          b.gone = true;
          ev(s, { t: 'hit', kind: b.bean ? 'bean' : 'sand', x: b.x, y: b.y });
        }
        // (Taiz: the mountain, the walls and the houses stop a shot, his and theirs)
        if (!b.gone && L.fly && X.fly.rock(s, b.x, b.y)) {
          b.gone = true;
          ev(s, { t: 'hit', kind: 'stone', x: b.x, y: b.y });
        }
        // a bean coming down on a platform stops there too
        if (!b.gone && b.bean && b.vy > 0) {
          for (j = 0; j < L.plats.length; j++) {
            var py2 = platY(L.plats[j], b.x);
            if (py2 !== null && b.y >= py2 && b.y - b.vy * DT * 0.5 <= py2 + 1) { b.gone = true; ev(s, { t: 'hit', kind: 'bean', x: b.x, y: py2 }); break; }
          }
        }
      }
      if (--b.life <= 0 || b.x < s.cam - 6 || b.x > s.cam + s.viewW + 6 || b.y < s.camY - 30 || (L.fly && b.y > s.camY + s.viewH + 30)) b.gone = true;
    }
  }

  function stepProps(s) {
    var p = s.p, L = s.L, i;
    for (i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.gone) continue;
      o.t++;
      var near = !p.dead && s.mode === 'foot' && Math.abs(p.x - o.x) < 13 && Math.abs(p.y - o.y) < 26;
      if (o.k === 'cover') { if (o.openT > 0) o.openT--; if (o.bar) o.hurtT++; continue; }
      if (o.k === 'vent') {
        // a grating over the roasting house's steam: it hisses (a warning), then blows a column of steam, then rests
        var c = (s.tick + o.phase) % o.every, st = c < T.VENT_HISS ? 'hiss' : (c < T.VENT_HISS + T.VENT_BLAST ? 'blast' : 'idle');
        if (st !== o.st) {
          o.st = st; o.t = 0;
          if (onScreen(s, o.x, 30) && st !== 'idle') ev(s, { t: st === 'hiss' ? 'vent_hiss' : 'vent_blast', x: o.x, y: o.y });
        }
        if (st === 'blast' && !p.dead && s.mode === 'foot' && Math.abs(p.x - o.x) < T.VENT_W && p.y > o.y - T.VENT_H && p.y <= o.y + 1 && hurtPlayer(s, o.x + (p.x < o.x ? 1 : -1), 'steam') && !s.hinted.vent) {
          s.hinted.vent = 1; ev(s, { t: 'hint', k: 'vent' });
        }
        continue;
      }
      if (o.k === 'crate') {
        if (near && s.status === 'play') {
          o.gone = true;
          if (o.gives === 'gren') p.grenades = Math.min(99, p.grenades + 5);
          else { p.weapon = o.gives; p.ammo = T.HMG_AMMO; }
          s.score += 50;
          ev(s, { t: 'pickup', k: o.gives, x: o.x, y: o.y });
        }
      } else if (o.k === 'mine') {
        if (!s.mineSpotted && Math.abs(p.x - o.x) < 190) { s.mineSpotted = true; ev(s, { t: 'spot', x: o.x, y: o.y }); }
        if (o.fuse < 0 && !p.dead && !p.air && s.mode === 'foot' && Math.abs(p.x - o.x) < 12 && Math.abs(p.y - o.y) < 8) o.fuse = 1;
        if (o.fuse >= 0 && --o.fuse <= 0) { o.gone = true; s.score += 50; explode(s, o.x, o.y - 8, 42, 'mine', false); }
      } else if (o.k === 'rmine') {
        if (o.fuse >= 0 && --o.fuse <= 0) { o.gone = true; s.score += 50; explode(s, o.x, o.y - 4, 30, 'mine', false); }
      } else if (o.k === 'drum') {
        if (o.fuse >= 0 && --o.fuse <= 0) { o.gone = true; s.score += 50; explode(s, o.x, o.y - 10, 40, 'drum', false); }
      } else if (o.k === 'spice') {
        // (the first sack seen with a Dhanab near it: a word on what it is for)
        if (!s.hinted.spice && !p.dead && Math.abs(p.x - o.x) < 210 && inMiddle(s, o.x)) {
          for (var si = 0; si < s.enemies.length; si++) {
            var se = s.enemies[si];
            if (se.alive && se.hostile && !se.ext && Math.abs(se.x - o.x) < 46 && Math.abs(se.y - o.y) < 40 && inMiddle(s, se.x)) { s.hinted.spice = 1; ev(s, { t: 'hint', k: 'spice' }); break; }
          }
        }
      } else if (o.k === 'detainee') {
        if (o.st === 'tied') {
          if (near && s.status === 'play') {
            o.st = 'freed'; o.t = 0;
            s.stats.freed++;
            (s.stats.rescued || (s.stats.rescued = [])).push(o.px);
            s.score += 500;
            if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
            ev(s, o.look ? { t: 'freed', x: o.x, y: o.y, look: o.look } : { t: 'freed', x: o.x, y: o.y });
            s.pickups.push({ id: s.nextId++, k: o.gives === 'hmg' ? 'hmg' : 'gren', x: o.x + 12, y: o.y - 24, vx: 46, vy: -170, air: true, t: 0, gone: false });
          }
        } else if (o.st === 'freed') {
          if (o.t > 76) { o.st = 'run'; o.t = 0; o.air = false; o.vy = 0; }
        } else if (o.st === 'run') {
          o.x -= 58 * DT;
          if (!o.air) {
            if (!follow(L, o)) { o.air = true; o.vy = 0; o.plat = -2; }
          } else {
            var y0 = o.y;
            o.vy = Math.min(T.MAX_FALL, o.vy + T.GRAV * DT);
            o.y += o.vy * DT;
            var ld = landing(L, o.x, y0, o.y, -9);
            if (ld) { o.y = ld.y; o.plat = ld.plat; o.air = false; o.vy = 0; }
          }
          if (o.x < s.cam - 26) o.gone = true;
        }
      }
    }
    for (i = 0; i < s.pickups.length; i++) {
      var q = s.pickups[i];
      if (q.gone) continue;
      q.t++;
      if (q.air) {
        var qy = q.y;
        q.vy += T.GRAV * 0.7 * DT;
        q.x += q.vx * DT; q.y += q.vy * DT;
        var l2 = q.vy > 0 ? landing(L, q.x, qy, q.y, -9) : null;
        if (l2) { q.y = l2.y; q.air = false; q.vx = 0; q.vy = 0; }
      }
      if (!p.dead && q.t > 14 && s.mode === 'foot' && Math.abs(p.x - q.x) < 13 && Math.abs((p.y - 14) - (q.y - 6)) < 24) {
        q.gone = true;
        if (q.k === 'gren') { p.grenades = Math.min(99, p.grenades + 5); }
        if (q.k === 'hmg') { p.weapon = 'hmg'; p.ammo = T.HMG_AMMO; }
        var worth = q.k === 'bean' || q.k === 'chilli' ? 50 : 100;      // (the roast coffee the Big Roaster leaves behind, the Tailor's dummies' chillies: points, nothing more)
        s.score += worth;
        ev(s, { t: 'pickup', k: q.k, x: q.x, y: q.y, pts: worth });
      }
      if (q.x < s.cam - 30) q.gone = true;
    }
  }

  // ------------------------------------------------------------------ who is awake, and where the camera may go
  function stepGroups(s) {
    var L = s.L, p = s.p, k, i;
    for (k in s.groups) {
      var G = s.groups[k], def = L.groups[k];
      if (G.done) continue;
      if (!G.awake) {
        if (G.afterT < 0 && ((def.trig != null && p.x >= def.trig) || (def.after && s.groups[def.after].done) || (def.wall && barGone(s, def.wall)))) G.afterT = def.delay || 0;
        if (G.afterT >= 0 && --G.afterT <= 0) G.awake = true;
        if (!G.awake) continue;
        G.awakeT = 0;
      }
      G.awakeT++;
      for (i = G.pending.length - 1; i >= 0; i--) {
        if (G.awakeT >= G.pending[i].at) {
          var sp = G.pending[i].sp;
          G.pending.splice(i, 1);
          if (sp.door) {
            // out of a doorway in the back wall: he steps into the light, and until he is out nothing touches him
            var nd = spawnEnemy(s, sp, sp.x);
            nd.emerge = T.EMERGE; nd.arrived = true; nd.cd = Math.max(nd.cd, T.EMERGE + Math.round(T.SETTLE * T.FIRST)); nd.face = s.p.x >= sp.x ? 1 : -1;
            ev(s, { t: 'emerge', x: sp.x, y: nd.y, k: sp.k });
            continue;
          }
          var ex = sp.enter === -1 ? s.cam - 16 - (sp.dx || 0) : s.cam + s.viewW + 16 + (sp.dx || 0);
          if (L.pits) ex = offPits(L, ex, sp.enter === -1 ? -1 : 1);          // (on the rooftops: on a roof, not down a gap)
          var ne = spawnEnemy(s, sp, ex);
          if (sp.enter === -1) { ne.cd += 46; ev(s, { t: 'behind', k: sp.k }); }
        }
      }
      if (!G.pending.length && G.hostile <= 0 && !G.hold) {
        G.done = true;
        ev(s, { t: 'group_done', g: k });
      }
    }
    // men left behind off the left edge are no longer anyone's problem
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.alive && e.hostile && e.x < s.cam - 40) { standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; }
    }
    var gate = null;
    for (i = 0; i < s.gates.length; i++) {
      var gt = s.gates[i];
      if (gt.done) continue;
      var all = true;
      for (var j = 0; j < gt.groups.length; j++) if (!s.groups[gt.groups[j]].done) all = false;
      if (gt.wall && !barGone(s, gt.wall)) all = false;            // (and a barricade across the way has to go first)
      if (all) { gt.done = true; s.gateWait = 0; ev(s, { t: 'go', gate: gt.id }); continue; }
      gate = gt;
      break;
    }
    // a gate with nobody left to fight on screen must not hold the player for ever
    if (gate && s.cam >= gate.x - s.viewW * T.HOLD - 1) {
      var live = 0, waiting = 0;
      for (i = 0; i < gate.groups.length; i++) {
        var GG = s.groups[gate.groups[i]];
        if (GG.done) continue;
        waiting += GG.pending.length + (GG.awake ? 0 : 1) + (GG.hold ? 1 : 0);
      }
      for (i = 0; i < s.enemies.length; i++) {
        var en = s.enemies[i];
        if (en.alive && en.hostile && gate.groups.indexOf(en.g) >= 0 && onScreen(s, en.x, 40)) live++;
      }
      s.gateWait = (live || waiting || (gate.wall && !barGone(s, gate.wall))) ? 0 : s.gateWait + 1;      // (a barricade still up is Yazeed's to break, not the failsafe's)
      if (s.gateWait > 420) {
        s.failsafe++;
        for (i = 0; i < s.enemies.length; i++) {
          var z = s.enemies[i];
          if (z.alive && z.hostile && gate.groups.indexOf(z.g) >= 0) { standDown(s, z); z.alive = false; z.st = 'gone'; z.deadT = 999; }
        }
        ev(s, { t: 'failsafe', gate: gate.id });
        s.gateWait = 0;
      }
    }
    s.holdX = gate ? gate.x : null;
    // the screen stops with the gate's line at HOLD of the way across, whatever the screen's width
    var maxCam = gate ? Math.min(gate.x - s.viewW * T.HOLD, L.endRight - s.viewW) : L.endRight - s.viewW;
    if (s.mode === 'drive') X.drive.camera(s, maxCam);
    else {
      var target = p.x - s.viewW * T.CAM_LEAD;
      if (target > maxCam) target = maxCam;
      if (target > s.cam) s.cam += Math.min(T.CAM_V, target - s.cam);
    }
    s.camMax = maxCam;

    var z2 = s.zone;
    while (z2 + 1 < L.zones.length && p.x >= L.zones[z2 + 1].x) z2++;
    if (z2 !== s.zone) { s.zone = z2; s.zoneScore = s.score; ev(s, { t: 'checkpoint', zone: z2, name: L.zones[z2].name }); refill(s); }
  }
  // the rooftops: a man walking in where there is a gap between two houses comes in on the roof beyond it instead
  function offPits(L, x, dir) {
    for (var i = 0; i < L.pits.length; i++) {
      var q = L.pits[i];
      if (x > q[0] - 10 && x < q[1] + 10) return dir > 0 ? q[1] + 12 : q[0] - 12;
    }
    return x;
  }

  // ------------------------------------------------------------------ one sixtieth of a second
  function step(s, inp) {
    s.events.length = 0;
    if (inp.viewW && inp.viewW !== s.viewW) s.viewW = inp.viewW;
    if (inp.viewH && inp.viewH !== s.viewH) s.viewH = inp.viewH;
    if (inp.lanes) { s.laneL = inp.lanes[0]; s.laneR = inp.lanes[1]; }
    if (s.status === 'over') return s;
    if (s.stopT > 0) { s.stopT--; return s; }                // a crash holds the picture for a few frames
    s.tick++;
    if (s.status === 'play') s.time += DT;
    if (s.mode === 'drive') X.drive.player(s, inp); else if (s.mode === 'fly') X.fly.player(s, inp); else stepPlayer(s, inp);
    if (s.status === 'over') return s;
    var i, xk;
    for (i = 0; i < s.enemies.length; i++) stepEnemy(s, s.enemies[i]);
    stepBullets(s);
    stepBombs(s);
    stepProps(s);
    if (s.clouds.length) stepClouds(s);
    for (xk in X) if (X[xk].step) X[xk].step(s, inp);
    // (Taiz: who wakes, where the camera may go and which checkpoint has been reached go by the route, not by x)
    if (s.L.fly) X.fly.groups(s); else stepGroups(s);
    // a nudge for someone who has not found a control yet (on foot)
    if (s.status === 'play' && !s.p.dead && !s.L.fly) {
      var above = false, any = false;
      for (i = 0; i < s.enemies.length; i++) {
        var he = s.enemies[i];
        if (!he.alive || !he.hostile || !onScreen(s, he.x, 0)) continue;
        any = true;
        if (he.y < s.p.y - 26) above = true;
      }
      s.quietT = any ? s.quietT + 1 : 0;
      for (i = 0; i < s.events.length; i++) if (s.events[i].t === 'die' || s.events[i].t === 'surrender') s.quietT = 0;
      if (s.quietT > 330 && above && !s.hinted.up) { s.hinted.up = 1; ev(s, { t: 'hint', k: 'up' }); }
      // only after a good two seconds of bullets wasted on it
      if (s.doorHits >= 6 && s.tick - s.doorAt > 100 && !s.hinted.door) { s.hinted.door = 1; ev(s, { t: 'hint', k: 'door' }); }
      if (s.coverHits >= 8 && s.tick - s.coverAt > 130 && !s.hinted.cover) { s.hinted.cover = 1; ev(s, { t: 'hint', k: 'cover' }); }
      if (s.barHits >= 10 && s.tick - s.barAt > 90 && !s.hinted.bar) { s.hinted.bar = 1; ev(s, { t: 'hint', k: 'bar' }); }
      // (or after a while pressed up against one, not knowing what to do about it)
      if (s.bars.length && !s.hinted.bar) {
        var pressed = false;
        for (i = 0; i < s.bars.length; i++) if (!s.bars[i].gone && s.p.x >= s.bars[i].x0 - 12 && s.p.x <= s.bars[i].x0) pressed = true;
        s.barPress = pressed ? s.barPress + 1 : 0;
        if (s.barPress > T.BAR_PRESS) { s.hinted.bar = 1; ev(s, { t: 'hint', k: 'bar' }); }
      }
      // the first fall down a gap between two roofs
      if (s.L.pits && !s.hinted.gap && !s.p.air && s.p.plat < 0) {
        for (i = 0; i < s.L.pits.length; i++) if (s.p.x > s.L.pits[i][0] && s.p.x < s.L.pits[i][1]) { s.hinted.gap = 1; ev(s, { t: 'hint', k: 'gap' }); }
      }
    }
    if (s.status === 'play' && !s.p.dead && s.p.x >= s.L.exitX) {
      var open = true;
      for (i = 0; i < s.gates.length; i++) if (!s.gates[i].done) open = false;
      if (open) { s.status = 'clear'; s.clearT = 0; ev(s, { t: 'clear' }); }
    }
    if (s.status === 'clear') s.clearT++;
    // sweep
    if (s.tick % 20 === 0) {
      s.bullets = s.bullets.filter(function (b) { return !b.gone; });
      s.bombs = s.bombs.filter(function (b) { return !b.gone; });
      s.pickups = s.pickups.filter(function (b) { return !b.gone; });
      s.props = s.props.filter(function (b) { return !b.gone; });
      s.enemies = s.enemies.filter(function (e) { return e.alive || e.deadT < 80; });
      for (xk in X) if (X[xk].sweep) X[xk].sweep(s);
    }
    return s;
  }

  // start the current zone again after the last life goes
  function continueZone(s, viewW) {
    var st = s.stats;
    st.continues++;
    return create(s.L, { zone: s.zone, score: s.zoneScore, time: s.time, stats: st, viewW: viewW || s.viewW, viewH: s.viewH, seed: (s.tick * 7919) >>> 0, radio: s.radio, lanes: [s.laneL, s.laneR], lives: 0 });
  }

  function results(s) {
    var L = s.L, st = s.stats, timeBonus = Math.max(0, Math.round((L.par - s.time) * 20));
    var clean = st.deaths === 0 && st.continues === 0;
    return {
      time: s.time, score: s.score, timeBonus: timeBonus, cleanBonus: clean ? 2000 : 0, total: s.score + timeBonus + (clean ? 2000 : 0),
      kills: st.kills, captures: st.captures, freed: st.freed, detainees: st.detainees, plates: st.plates, deaths: st.deaths, continues: st.continues,
      knifed: st.knifed, ranOver: st.ranOver, flips: st.flips, bossT: st.bossT,
      accuracy: st.shots ? st.hits / st.shots : 0, shots: st.shots,
      liberator: st.detainees > 0 && st.freed >= st.detainees,
      ace: st.continues === 0,     // Ace: the mission done without a continue (Khaled, 19 Oct)
      par: L.par
    };
  }

  return {
    DT: DT, T: T, KIND: KIND, create: create, step: step, continueZone: continueZone, results: results,
    groundY: groundY, platY: platY, surfaceY: surfaceY, muzzle: muzzle, playerBox: playerBox, doorUp: doorUp, doorLow: doorLow, doorTop: doorTop, ducked: ducked, staged: staged, inReach: inReach, inMiddle: inMiddle, guarded: guarded, assist: assist, onScreen: onScreen,
    knifeTarget: knifeTarget,
    // for the files that add to the game: the car section and the boss
    ext: X,
    _: { ev: ev, refill: refill, explode: explode, hurtPlayer: hurtPlayer, killEnemy: killEnemy, hurtEnemy: hurtEnemy, spawnEnemy: spawnEnemy, standDown: standDown, groupOf: groupOf,
         landing: landing, follow: follow, floorUnder: floorUnder, inBox: inBox, platIndex: platIndex, enemyFire: enemyFire, stepPlayer: stepPlayer,
         addCloud: addCloud, burstSack: burstSack, hitBar: hitBar, barGone: barGone, inCloud: inCloud, offPits: offPits }
  };
})();
if (typeof module !== 'undefined') module.exports = Sim;
