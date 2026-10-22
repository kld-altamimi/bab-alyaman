// drive.js - the coast road. Salem drives the armoured truck, Yazeed rides up in its roof ring with the gun, and the player has both: the stick is the
// pedal (faster, slower), JUMP is a hop, FIRE is the gun over the cab, BOMB lobs a grenade ahead.
// The rule of the road: the gun fires over the heads of men on the tarmac, so the bumper is for them and for their pickups;
// rifle fire rings off the car, and what hurts it is anything that goes bang: mines, dynamite, drums, the heavy guns on
// the pickups, the little drones.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev, groundY = Sim.groundY;
  var D = Sim.D = {
    V_SLOW: 118, V_CRUISE: 205, V_FAST: 296, ACC: 250, BRAKE: 400,
    HOP_V: 300, HOP_CUT: 120, GRAV: 880,
    REAR: 46, FRONT: 48, TALL: 50, WHEEL: 29,          // the body's box about the middle of the car; where the wheels are
    BED: -22, STAND: 31,                              // where Yazeed stands: up in the roof ring, behind the middle of the car
    CAM: 0.25,                                        // the car sits a quarter of the way across the screen
    ARRIVE_V: 250,
    GREN_VX: 230, GREN_VY: -40, GREN_T: 0.454,         // thrown flat and hard from a moving car, so it comes down where he can still see
    PANIC: 128, MAN_SIGHT: 300,
    TRUCK_HP: 8, TRUCK_HW: 44, TRUCK_H: 38, TRUCK_RUN_V: 128, TRUCK_CHARGE_V: -150, HEAVY_V: 235, GUNNER_HP: 2,
    DRONE_V: 320, DRONE_R: 26,
    FLIP_PTS: 500, CRUSH_PTS: 400, GUNNER_PTS: 150, TRUCK_PTS: 300, DRONE_PTS: 200, STRIKE_PTS: 1000, STRIKE_N: 6
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  // staged: in the middle of the screen, clear of the thumbs, where a truck or a drone may start an attack, and where his
  // shots can hurt it. Out in the edge lanes it is still coming in: his shots glance off it (and it flashes).
  function staged(s, x) { return x >= s.cam + s.viewW * s.laneL - 10 && x <= s.cam + s.viewW * (1 - s.laneR) + 10; }
  function onScreen(s, x) { return x >= s.cam - 10 && x <= s.cam + s.viewW + 10; }

  // ------------------------------------------------------------------ setting up
  function create(s, opts) {
    var L = s.L, zone = s.zone, i;
    s.car = { st: 'away', x: -200, y: 0, vx: 0, vy: 0, air: false, ang: 0, spin: 0, wheel: 0, hopBuf: 0, hopHeld: false, t: 0, waitT: 0, stopT: 0, squash: 0 };
    s.trucks = []; s.drones = []; s.roadI = 0; s.ramLog = [];
    if (!L.road) return;
    var c = s.car, zr = -1, zb = -1;
    for (i = 0; i < L.zones.length; i++) { if (L.zones[i].drive) zr = i; if (L.zones[i].battery) zb = i; }
    if (zone === zr) {
      c.st = 'drive'; c.x = L.pickup.x; c.y = groundY(L, c.x); c.vx = 60;
      s.mode = 'drive';
      s.p.footW = 'side'; s.p.footA = 0; s.p.weapon = 'hmg'; s.p.inv = 90;
      seat(s);
      s.cam = Math.max(0, c.x - s.viewW * D.CAM);
    } else if (zb >= 0 && zone >= zb) {
      c.st = 'park'; c.x = L.park.x; c.y = groundY(L, c.x);
      s.roadI = L.road.length;
    }
  }
  function seat(s) {
    var p = s.p, c = s.car;
    p.x = c.x + D.BED; p.y = c.y - D.STAND; p.vx = c.vx; p.vy = 0; p.face = 1; p.plat = -2; p.crouch = false; p.air = false;
  }
  function carBox(c) { return { x0: c.x - D.REAR, x1: c.x + D.FRONT, y0: c.y - D.TALL, y1: c.y }; }

  function mount(s) {
    var p = s.p, c = s.car;
    s.mode = 'drive'; c.st = 'drive'; c.vx = 40; c.t = 0;
    p.footW = p.weapon; p.footA = p.ammo; p.weapon = 'hmg'; p.aim = 'fwd'; p.air = false; p.dropT = 0; p.jumpBuf = 0;
    seat(s);
    ev(s, { t: 'mount', x: c.x, y: c.y });
    if (!s.hinted.drive) { s.hinted.drive = 1; ev(s, { t: 'hint', k: 'drive' }); }
  }
  function dismount(s) {
    var p = s.p, c = s.car;
    s.mode = 'foot'; c.st = 'park'; c.vx = 0;
    p.weapon = p.footW || 'side'; p.ammo = p.footA || 0;
    p.x = c.x + D.BED - 8; p.y = c.y - D.STAND; p.vx = 0; p.vy = -190; p.air = true; p.plat = -2; p.face = 1; p.aim = 'fwd'; p.inv = Math.max(p.inv, 50); p.jumpHeld = false;
    ev(s, { t: 'dismount', x: c.x, y: c.y });
  }

  // ------------------------------------------------------------------ the player at the wheel and the gun
  function player(s, inp) {
    var p = s.p, c = s.car, L = s.L;
    p.fireT++; p.throwT++; p.hurtT++; p.landT++; p.knifeT++;
    if (p.inv > 0) p.inv--;
    if (p.fireCd > 0) p.fireCd--;
    if (p.grenCd > 0) p.grenCd--;
    c.t++;
    if (c.squash > 0) c.squash--;
    if (p.dead) {
      if (p.dead === 1) {                         // this is the tick it went up
        c.air = true; c.vy = -260; c.spin = 0.2; c.st = 'wreck';
        I.explode(s, c.x, c.y - 14, 40, 'truck', true);
      }
      p.dead++;
      c.vx *= 0.985;
      c.x += c.vx * DT;
      if (c.air) {
        c.vy += D.GRAV * DT; c.y += c.vy * DT; c.ang += c.spin;
        var gy0 = groundY(L, c.x);
        if (c.vy > 0 && c.y >= gy0) { c.y = gy0; c.air = false; c.vx *= 0.35; c.spin = 0; c.ang = Math.round(c.ang / Math.PI) * Math.PI; ev(s, { t: 'thud', x: c.x, y: c.y }); }      // it settles on its wheels or on its roof
      }
      if (p.dead > T.DEATH_T) {
        p.lives--;
        if (p.lives <= 0) { s.status = 'over'; ev(s, { t: 'over' }); return; }
        p.dead = 0; p.plates = T.PLATES; p.inv = T.RESPAWN_INV;
        p.grenades = Math.max(p.grenades, T.GREN_MAX);
        c.x = Math.max(c.x, s.cam + s.viewW * D.CAM); c.y = groundY(L, c.x);
        c.vx = D.V_CRUISE * 0.6; c.vy = 0; c.air = false; c.ang = 0; c.spin = 0; c.st = c.x >= L.park.x - 260 ? 'stop' : 'drive';
        ev(s, { t: 'respawn', x: c.x, y: c.y });
      }
      seat(s);
      return;
    }
    var driving = c.st === 'drive';
    var mx = driving ? (inp.mx > 0 ? 1 : (inp.mx < 0 ? -1 : 0)) : 0, my = inp.my < 0 ? -1 : 0;
    var jump = driving && !!inp.jump, fire = driving && !!inp.fire, gren = driving && !!inp.grenade;
    var jumpPressed = jump && !s.prev.jump, grenPressed = gren && !s.prev.grenade;
    s.prev.jump = jump; s.prev.fire = fire; s.prev.grenade = gren;

    // the pedal
    var want = mx > 0 ? D.V_FAST : (mx < 0 ? D.V_SLOW : D.V_CRUISE);
    if (c.st === 'stop') {
      var left = L.park.x - c.x;
      want = left > 1.5 ? Math.max(26, Math.min(c.vx, Math.sqrt(2 * D.BRAKE * 0.7 * left))) : 0;
    }
    if (c.vx < want) c.vx = Math.min(want, c.vx + D.ACC * DT); else c.vx = Math.max(want, c.vx - D.BRAKE * DT);
    c.pedal = mx;

    // the hop
    if (jumpPressed) c.hopBuf = 6; else if (c.hopBuf > 0) c.hopBuf--;
    if (c.hopBuf > 0 && !c.air && driving) {
      c.vy = -D.HOP_V; c.air = true; c.hopHeld = true; c.hopBuf = 0;
      ev(s, { t: 'hop', x: c.x, y: c.y });
    }
    if (c.air) {
      if (c.hopHeld && !jump) { c.hopHeld = false; if (c.vy < -D.HOP_CUT) c.vy = -D.HOP_CUT; }
      c.vy += D.GRAV * DT;
    }
    c.x += c.vx * DT;
    var gy = groundY(L, c.x);
    if (c.air) {
      c.y += c.vy * DT;
      if (c.vy > 0 && c.y >= gy) { ev(s, { t: 'car_land', x: c.x, y: gy, v: c.vy }); c.y = gy; c.air = false; c.vy = 0; c.squash = 7; }
    } else c.y = gy;
    c.wheel += c.vx * DT;
    c.ang = c.air ? clamp(c.vy / 900, -0.16, 0.16) : 0;

    // the end of the road: Salem stops at the barrier and Yazeed gets down
    if (driving && c.x >= L.park.x - 260) { c.st = 'stop'; ev(s, { t: 'road_end' }); }
    if (c.st === 'stop' && c.vx <= 0.5 && !c.air) { if (++c.stopT > 26) { dismount(s); return; } }
    seat(s);

    // the gun over the cab: level, or up at 45 degrees with the stick pushed up
    p.aim = my < 0 ? 'diag' : 'fwd';
    var pull = fire;
    if (!pull && inp.auto && driving) pull = !!Sim.assist(s, Sim.muzzle(p), true);
    if (pull && p.fireCd <= 0 && driving) {
      var m = Sim.muzzle(p), d = Sim.assist(s, m, false);
      var a = (s.rand() - 0.5) * 2 * T.HMG_SPREAD, cs = Math.cos(a), sn = Math.sin(a);
      d = { dx: d.dx * cs - d.dy * sn, dy: d.dx * sn + d.dy * cs };
      var hide = Math.ceil(Math.sqrt((m.x - m.sx) * (m.x - m.sx) + (m.y - m.sy) * (m.y - m.sy)) / (T.BULLET_V * DT));
      s.bullets.push({ x: m.sx, y: m.sy, vx: d.dx * T.BULLET_V + c.vx, vy: d.dy * T.BULLET_V, life: T.BULLET_LIFE, own: true, hmg: true, age: 0, free: 0, hide: hide });
      p.fireCd = T.HMG_CD; p.fireT = 0;
      s.stats.shots++;
      ev(s, { t: 'shot', w: 'hmg', x: m.x, y: m.y, dx: d.dx, dy: d.dy, aim: p.aim, face: 1 });
    }
    if (grenPressed && p.grenCd <= 0 && p.grenades > 0) {
      p.grenades--; p.grenCd = T.GREN_CD; p.throwT = 0;
      s.stats.grenades++;
      s.bombs.push({ id: s.nextId++, kind: 'gren', own: true, x: p.x + 8, y: p.y - 30, vx: c.vx + D.GREN_VX, vy: D.GREN_VY, air: true, fuse: T.GREN_FUSE + 24, bounced: 1, t: 0 });      // (no bounce: it goes off where it lands)
      ev(s, { t: 'throw', x: p.x, y: p.y });
    }
  }

  function camera(s, maxCam) {
    var c = s.car, target = Math.min(c.x - s.viewW * D.CAM, maxCam);
    if (s.p.dead) return;
    if (target > s.cam) s.cam += Math.min(target - s.cam, Math.max(3.2, c.vx * DT + 2.6));
  }

  // ------------------------------------------------------------------ what is on the road
  function spawn(s, it) {
    var L = s.L, i, x;
    if (it.k === 'men') {
      for (i = 0; i < it.n; i++) {
        x = it.x + i * (it.gap || 24);
        var kind = (it.kinds && it.kinds[i % it.kinds.length]) || 'rifle';
        var e = I.spawnEnemy(s, { g: 'ROAD', k: kind, post: 1, look: ['worried', 'youth', 'angry', 'qat'][(i + (it.x >> 3)) % 4] }, x);
        e.ext = 'drive'; e.face = -1; e.st = 'wait'; e.cd = (kind === 'bomber' ? 2 : Math.round((10 + Math.floor(s.rand() * 40) + i * 6) * T.FIRST));          // (R5: T.FIRST, T.GAP, sim.js) e.noKnife = true;
        if (it.march) { e.march = true; e.cd = 9999; }
      }
      if (!s.hinted.ram) { s.hinted.ram = 1; ev(s, { t: 'hint', k: 'ram' }); }
    } else if (it.k === 'truck') {
      var mode = it.mode || 'block';
      s.trucks.push({ id: s.nextId++, x: it.x, y: groundY(L, it.x), vx: 0, face: mode === 'run' ? 1 : -1, mode: mode, hp: D.TRUCK_HP, gun: it.nogun ? 0 : D.GUNNER_HP, gst: 'idle', gT: 0,
                      gcd: Math.round((20 + Math.floor(s.rand() * 30)) * T.FIRST), shots: 0, st: 'ok', vy: 0, ang: 0, spin: 0, paint: it.paint || 'olive', hurtT: 99, t: 0, wheel: 0, seen: false });
      if (mode === 'charge') ev(s, { t: 'horn', k: 'truck', x: it.x });
      if (!s.hinted.truck) { s.hinted.truck = 1; ev(s, { t: 'hint', k: 'truck' }); }
    } else if (it.k === 'drones') {
      for (i = 0; i < it.n; i++) addDrone(s, s.cam + s.viewW + 30 + i * 46, 30 + i * 12, i);
      if (!s.hinted.drone) { s.hinted.drone = 1; ev(s, { t: 'hint', k: 'drone' }); }
    } else {
      // things that stand on the tarmac: mines, drums, sandbags, crates
      var o = { id: s.nextId++, k: it.k, x: it.x, y: groundY(L, it.x), plat: -1, t: 0, st: 'idle', gone: false };
      if (it.k === 'drum') { o.hp = 2; o.paint = it.paint || 'oxide'; o.fuse = -1; }
      if (it.k === 'rmine') { o.fuse = -1; if (!s.hinted.mine) { s.hinted.mine = 1; ev(s, { t: 'hint', k: 'mine' }); } }
      if (it.k === 'crate') o.gives = it.gives || 'gren';
      s.props.push(o);
    }
  }
  function addDrone(s, x, y, i, foot) {
    var d = { id: s.nextId++, x: x, y: y, st: 'in', t: 0, wait: i * 30, off: (foot ? -40 : 84) + i * (foot ? 80 : 34), hy: (foot ? 64 : 46) + i * 13, tx: 0, ty: 0, ht: 0, foot: !!foot };
    s.drones.push(d);
    return d;
  }

  // a man on the road: he stands his ground and shoots until the car is nearly on him, then thinks again
  function man(s, e) {
    var c = s.car, L = s.L, p = s.p, dx = e.x - c.x, K = Sim.KIND[e.k], live = s.mode === 'drive' && !p.dead;
    e.seen = Sim.onScreen(s, e.x, -6);
    if (e.st === 'panic') {
      e.face = 1; e.moving = 1;
      e.x += K.lane * DT; e.y = groundY(L, e.x); e.walkD += K.lane * DT;
      return;
    }
    if (live && e.k !== 'door' && dx > 0 && dx < D.PANIC + (c.vx - D.V_CRUISE) * 0.3 + (e.id % 5) * 7) {
      e.st = 'panic'; e.stT = 0; e.lit = false;
      ev(s, { t: 'panic', x: e.x, y: e.y, k: e.k, id: e.id });
      return;
    }
    e.face = dx >= 0 ? -1 : 1;
    e.moving = 0;
    if (e.march) {                                // a platoon on the march, in step, backs to the car until it hears it
      e.face = 1; e.moving = 1; e.x += 30 * DT; e.y = groundY(L, e.x); e.walkD += 30 * DT;
      return;
    }
    if (!live || !e.seen) return;                 // (out here they fire from wherever they stand: there is no time to wait until they are well on)
    if (e.k === 'rifle') {
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (dx > 0 && dx < D.MAN_SIGHT) { e.st = 'aim'; e.stT = 0; ev(s, { t: 'tell', k: 'rifle', x: e.x, y: e.y }); }
      } else if (e.st === 'aim') {
        if (e.stT >= 20) { e.st = 'burst'; e.stT = 0; e.shots = 0; }
      } else if (e.st === 'burst') {
        if (e.stT % 8 === 1) { I.enemyFire(s, e, false, 26); if (++e.shots >= 3) { e.st = 'cool'; e.stT = 0; e.cd = Math.round((40 + Math.floor(s.rand() * 40)) * T.GAP); } }
      } else if (e.st === 'cool') { if (e.stT > 14) { e.st = 'wait'; e.stT = 0; } }
    } else if (e.k === 'bomber') {
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (dx > 170) { e.st = 'wind'; e.stT = 0; e.lit = true; ev(s, { t: 'tell', k: 'bomber', x: e.x, y: e.y }); }
      } else if (e.st === 'wind') {
        if (e.stT >= 22) {
          // thrown to come down where the car will be when the fuse runs out
          var Tf = 0.92, tx = c.x + c.vx * (Tf + T.DYN_FUSE * DT) + 6, sy = e.y - 40, ty = groundY(L, tx) - 2;
          var vx = (tx - (e.x - e.face * 4)) / Tf, vy = (ty - sy - 0.5 * T.DYN_G * Tf * Tf) / Tf;
          s.bombs.push({ id: s.nextId++, kind: 'dyn', own: false, x: e.x - e.face * 4, y: sy, vx: vx, vy: vy, air: true, fuse: T.DYN_FUSE, bounced: 0, t: 0 });
          e.lit = false; e.st = 'throw'; e.stT = 0;
          ev(s, { t: 'lob', x: e.x, y: sy });
        }
      } else if (e.st === 'throw') { if (e.stT > 18) { e.st = 'wait'; e.stT = 0; e.cd = Math.round(110 * T.GAP); } }
    }
  }

  function gunnerX(t) { return t.x - t.face * 20; }
  function truckGone(s, t, pts, how) {
    t.st = 'gone';
    if (pts) s.score += pts;
    ev(s, { t: 'truck_dead', x: t.x, y: t.y, how: how, face: t.face, paint: t.paint, pts: pts || 0 });
    I.explode(s, t.x, t.y - 10, 42, 'truck', true);
  }
  function dropGunner(s, t, how) {
    if (t.gun <= 0) return;
    t.gun = 0;
    s.score += D.GUNNER_PTS; s.stats.kills++;
    s.streak++; if (s.streak > s.stats.streakBest) s.stats.streakBest = s.streak;
    ev(s, { t: 'gunner_down', x: gunnerX(t), y: t.y - 22, face: t.face, how: how, pts: D.GUNNER_PTS });
  }
  function stepTrucks(s) {
    var c = s.car, L = s.L, p = s.p, i;
    for (i = 0; i < s.trucks.length; i++) {
      var t = s.trucks[i];
      t.t++; t.hurtT++;
      if (t.st === 'flip') {
        t.vy += D.GRAV * DT; t.x += t.vx * DT; t.y += t.vy * DT; t.ang += t.spin;
        if (t.vy > 0 && t.y >= groundY(L, t.x)) { t.y = groundY(L, t.x); truckGone(s, t, 0, 'flip'); }
        else if (t.x < s.cam - 140) t.st = 'gone';
        continue;
      }
      if (t.st !== 'ok') continue;
      var lim = s.cam + s.viewW * (1 - s.laneR) - 50;
      if (!t.seen && t.x < s.cam + s.viewW + 30) { t.seen = true; if (t.mode === 'run') t.vx = D.TRUCK_RUN_V; if (t.mode === 'charge') t.vx = D.TRUCK_CHARGE_V; }
      if (t.mode === 'run' && t.seen) { if (t.x < lim) t.x = Math.min(lim, t.x + t.vx * DT); t.wheel += t.vx * DT; }
      else if (t.mode === 'charge' && t.seen) { t.x += t.vx * DT; t.wheel += t.vx * DT; }
      t.y = groundY(L, t.x);
      if (t.gun > 0 && !p.dead && s.mode === 'drive') {
        var dxc = t.x - c.x;
        if (t.gst === 'idle') {
          if (t.gcd > 0) t.gcd--;
          else if (staged(s, t.x) && dxc > 70 && dxc < 340) { t.gst = 'tell'; t.gT = 0; ev(s, { t: 'tell', k: 'heavy', x: gunnerX(t), y: t.y - 46 }); }
        } else if (t.gst === 'tell') {
          if (++t.gT >= 28) { t.gst = 'burst'; t.gT = 0; t.shots = 0; }
        } else if (t.gst === 'burst') {
          if (t.gT++ % 7 === 0) {
            var mx = gunnerX(t) - 28, my = t.y - 43, ax = (c.x + 6) - mx, ay = (c.y - 18) - my, al = Math.sqrt(ax * ax + ay * ay) || 1;
            s.bullets.push({ x: mx, y: my, vx: ax / al * D.HEAVY_V + t.vx, vy: ay / al * D.HEAVY_V, life: 170, own: false, heavy: true, src: 'gun truck' });
            ev(s, { t: 'eshot', k: 'heavy', x: mx, y: my, face: -1 });
            if (++t.shots >= 4) { t.gst = 'idle'; t.gcd = Math.round((84 + Math.floor(s.rand() * 40)) * T.GAP); }
          }
        }
      }
      if (t.x < s.cam - 140) t.st = 'gone';
    }
  }

  function popDrone(s, d, pts) {
    if (d.st === 'gone') return;
    d.st = 'gone';
    if (pts) { s.score += D.DRONE_PTS; s.stats.kills++; }
    ev(s, { t: 'drone_down', x: d.x, y: d.y, pts: pts ? D.DRONE_PTS : 0 });
    I.explode(s, d.x, d.y, 16, 'kdrone', true);
  }
  function stepDrones(s) {
    var c = s.car, p = s.p, L = s.L, i, drive = s.mode === 'drive';
    for (i = 0; i < s.drones.length; i++) {
      var d = s.drones[i];
      if (d.st === 'gone') continue;
      d.t++;
      var tx = drive ? c.x : p.x, ty = drive ? c.y - 18 : p.y - 16, tvx = drive ? c.vx : p.vx, gone = p.dead || s.status !== 'play';
      if (d.st === 'in' || d.st === 'hover') {
        var hx = d.foot ? clamp(tx + d.off, s.cam + s.viewW * s.laneL + 16, s.cam + s.viewW * (1 - s.laneR) - 16) : tx + d.off, hy = d.hy + Math.sin(d.t / 9) * 3;
        var vmax = (drive ? Math.abs(tvx) : 0) + 150;
        d.x += clamp(hx - d.x, -vmax * DT, vmax * DT);
        d.y += clamp(hy - d.y, -100 * DT, 100 * DT);
        if (d.st === 'in' && Math.abs(hx - d.x) < 8 && Math.abs(hy - d.y) < 8 && d.t > d.wait) { d.st = 'hover'; d.ht = 34 + Math.floor(s.rand() * 26); }
        else if (d.st === 'hover' && !gone && --d.ht <= 0 && staged(s, d.x)) { d.st = 'tell'; d.tt = 0; ev(s, { t: 'tell', k: 'drone', x: d.x, y: d.y }); }
      }
      if (d.st === 'tell') {
        // it holds its place over the target and shows where it means to come down
        var hx2 = d.foot ? d.x : tx + d.off;
        d.x += clamp(hx2 - d.x, -400 * DT, 400 * DT);
        var dist = Math.sqrt((tx - d.x) * (tx - d.x) + (ty - d.y) * (ty - d.y)), tt = dist / D.DRONE_V;
        d.tx = tx + tvx * tt * (drive ? 1 : 0.5); d.ty = groundY(L, d.tx) - (drive ? 14 : 12);
        if (++d.tt >= (d.foot ? 54 : 34)) {
          d.st = 'dive'; var ddx = d.tx - d.x, ddy = d.ty - d.y, dl = Math.sqrt(ddx * ddx + ddy * ddy) || 1;
          d.vx = ddx / dl * D.DRONE_V; d.vy = ddy / dl * D.DRONE_V;
          ev(s, { t: 'dive', x: d.x, y: d.y });
        }
      } else if (d.st === 'dive') {
        d.x += d.vx * DT; d.y += d.vy * DT;
        var hit = d.y >= groundY(L, d.x) - 6;
        if (drive) { var b = carBox(c); if (d.x > b.x0 - 4 && d.x < b.x1 + 4 && d.y > b.y0 - 4) hit = true; }
        else if (!p.dead) { var pb = Sim.playerBox(p); if (d.x > pb.x0 - 5 && d.x < pb.x1 + 5 && d.y > pb.y0 - 4 && d.y < pb.y1) hit = true; }
        if (hit) { d.st = 'gone'; ev(s, { t: 'drone_hit', x: d.x, y: d.y }); I.explode(s, d.x, d.y, D.DRONE_R, 'kdrone', false); }
      }
      if (d.x < s.cam - 120 || d.y > L.height + 30) d.st = 'gone';
    }
  }

  // ------------------------------------------------------------------ the bumper
  function collide(s) {
    var c = s.car, p = s.p, L = s.L, i, j, b = carBox(c);
    if (p.dead || c.st === 'wreck') return;
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.ext || !e.alive || !e.hostile) continue;
      if (e.x + e.hw > b.x0 + 8 && e.x - e.hw < b.x1 && e.y - e.h < b.y1 && e.y > b.y0 + 4) {
        I.killEnemy(s, e, 1, 'ram');
        e.vx = c.vx * 0.85 + 50 + s.rand() * 60; e.vy = -230 - s.rand() * 90;
        s.ramLog.push(s.tick);
      }
    }
    for (i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.gone) continue;
      if (o.k === 'rmine' && o.fuse < 0) {
        if (!c.air && (Math.abs(c.x - D.WHEEL - o.x) < 9 || Math.abs(c.x + D.WHEEL - o.x) < 9)) o.fuse = 1;
        else for (j = 0; j < s.enemies.length; j++) { var m = s.enemies[j]; if (m.ext && m.alive && !m.air && Math.abs(m.x - o.x) < 6) { o.fuse = 1; break; } }
      } else if (o.k === 'drum' && o.fuse < 0) {
        if (o.x > b.x0 && o.x < b.x1 + 4 && c.y > o.y - 22) o.fuse = 1;
      } else if (o.k === 'crate') {
        if (o.x > b.x0 && o.x < b.x1 + 4 && c.y > o.y - 26) {
          o.gone = true;
          if (o.gives === 'gren') p.grenades = Math.min(99, p.grenades + 5);
          s.score += 50;
          ev(s, { t: 'pickup', k: o.gives, x: o.x, y: o.y });
          ev(s, { t: 'smash', k: 'crate', x: o.x, y: o.y });
        }
      } else if (o.k === 'rbags') {
        if (o.x > b.x0 && o.x < b.x1 + 4 && c.y > o.y - 16) { o.gone = true; ev(s, { t: 'smash', k: 'bags', x: o.x, y: o.y }); }
      }
    }
    for (i = 0; i < s.trucks.length; i++) {
      var t = s.trucks[i];
      if (t.st !== 'ok' || t.x - D.TRUCK_HW > b.x1 || t.x + D.TRUCK_HW < b.x0) continue;
      if (c.air && c.vy > 40 && c.y <= t.y - 16 && c.y >= t.y - D.TRUCK_H - 12) {
        // come down on its roof
        dropGunner(s, t, 'ram');
        s.stats.flips++;
        c.vy = -235; c.y = t.y - D.TRUCK_H - 12;
        truckGone(s, t, D.CRUSH_PTS, 'crush');
        s.stopT = 3;
      } else if (c.y > t.y - 28) {
        dropGunner(s, t, 'ram');
        t.st = 'flip'; t.vy = -320;
        t.vx = t.mode === 'charge' ? -80 : c.vx + 86;
        t.spin = (t.mode === 'charge' ? -1 : 1) * 0.2;
        s.score += D.FLIP_PTS; s.stats.flips++;
        c.vx *= 0.84;
        s.stopT = 4;
        ev(s, { t: 'flip', x: t.x, y: t.y, mode: t.mode, pts: D.FLIP_PTS });
      }
    }
    // a whole file of men at once
    while (s.ramLog.length && s.tick - s.ramLog[0] > 80) s.ramLog.shift();
    if (s.ramLog.length >= D.STRIKE_N) {
      s.ramLog.length = 0;
      s.score += D.STRIKE_PTS;
      if (s.radio < 3) { s.radio++; ev(s, { t: 'radio', n: s.radio }); }
      ev(s, { t: 'strike', x: c.x + 60, y: c.y - 50, pts: D.STRIKE_PTS });
    }
  }

  function step(s, inp) {
    var c = s.car, L = s.L, p = s.p, i;
    if (!L.road) return;
    if (c.st === 'away') {
      var ready = true;
      for (i = 0; i < s.gates.length; i++) if (L.pickup.after.indexOf(s.gates[i].id) >= 0 && !s.gates[i].done) ready = false;
      if (ready && p.x > L.pickup.x - 330) { c.st = 'arrive'; c.x = s.cam - 70; c.y = groundY(L, Math.max(0, c.x)); c.vx = D.ARRIVE_V; ev(s, { t: 'horn', k: 'shass', x: c.x }); }
    } else if (c.st === 'arrive') {
      // he pulls up beside Yazeed, wherever along the last of the beach Yazeed has got to
      c.stopX = clamp(p.x + 14, L.pickup.x, L.pickup.x + 50);
      var left = c.stopX - c.x;
      var want = left > 1.5 ? Math.max(24, Math.min(D.ARRIVE_V, Math.sqrt(2 * D.BRAKE * 0.6 * left))) : 0;
      c.vx = want; c.x += c.vx * DT; c.y = groundY(L, Math.max(0, c.x)); c.wheel += c.vx * DT;
      if (want === 0) { c.st = 'wait'; c.waitT = 0; ev(s, { t: 'car_wait', x: c.x, y: c.y }); }
    }
    if (c.st === 'wait' || c.st === 'arrive' || c.st === 'away') {
      // nothing beyond the car until he is in it
      var wall = c.st === 'wait' ? c.x + 40 : L.pickup.x + 66;
      if (p.x > wall && s.mode === 'foot') { p.x = wall; if (p.vx > 0) p.vx = 0; }
      if (c.st === 'wait') {
        c.waitT++;
        if (!p.dead && s.status === 'play' && Math.abs(p.x - c.x) < 46 && p.y > c.y - 70) mount(s);
        else if (c.waitT === 300 && !s.hinted.mount) { s.hinted.mount = 1; ev(s, { t: 'hint', k: 'mount' }); }
      }
    }
    if (s.mode === 'drive') {
      while (s.roadI < L.road.length && L.road[s.roadI].x < s.cam + s.viewW + 80) spawn(s, L.road[s.roadI++]);
      for (i = 0; i < s.props.length; i++) {
        var mo = s.props[i];
        if (mo.k === 'rmine' && !mo.gone && !mo.seen && mo.x < s.cam + s.viewW * (1 - s.laneR) + 40) { mo.seen = true; ev(s, { t: 'spot', k: 'rmine', x: mo.x, y: mo.y }); }
      }
      stepTrucks(s);
      stepDrones(s);
      collide(s);
    } else stepDrones(s);
  }

  // ------------------------------------------------------------------ what the rest of the game asks
  // a shot of theirs arriving while he is in the car: rifle rounds ring off it, the heavy ones do not
  function hitCar(s, b) {
    var c = s.car, p = s.p, bx = carBox(c);
    if (p.dead || b.x < bx.x0 || b.x > bx.x1 || b.y < bx.y0 - 6 || b.y > bx.y1) return false;
    if (b.heavy && p.inv <= 0) I.hurtPlayer(s, b.x - b.vx, b.src || 'heavy gun');
    else ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y });
    return true;
  }
  // one of his shots: has it found a gunner, a pickup or a drone?
  function shot(s, b) {
    var i;
    for (i = 0; i < s.trucks.length; i++) {
      var t = s.trucks[i];
      if (t.st !== 'ok' || !onScreen(s, t.x)) continue;
      var gx = gunnerX(t), onGun = t.gun > 0 && b.x > gx - 8 && b.x < gx + 8 && b.y > t.y - 62 && b.y < t.y - 34;
      if (!staged(s, t.x) && (onGun || (b.x > t.x - D.TRUCK_HW && b.x < t.x + D.TRUCK_HW && b.y > t.y - D.TRUCK_H && b.y < t.y))) {
        ev(s, { t: 'hit', kind: 'guard', x: b.x, y: b.y });
        return true;
      }
      if (onGun) {
        ev(s, { t: 'hit', kind: 'body', x: b.x, y: b.y });
        if (--t.gun <= 0) { t.gun = 1; dropGunner(s, t, 'shot'); }
        return true;
      }
      if (b.x > t.x - D.TRUCK_HW && b.x < t.x + D.TRUCK_HW && b.y > t.y - D.TRUCK_H && b.y < t.y) {
        ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y });
        t.hurtT = 0;
        if (--t.hp <= 0) truckGone(s, t, D.TRUCK_PTS, 'shot');
        return true;
      }
    }
    for (i = 0; i < s.drones.length; i++) {
      var d = s.drones[i];
      if (d.st === 'gone' || !onScreen(s, d.x)) continue;
      if (Math.abs(b.x - d.x) < 11 && Math.abs(b.y - d.y) < 8) {
        if (!staged(s, d.x)) { ev(s, { t: 'hit', kind: 'guard', x: b.x, y: b.y }); return true; }
        popDrone(s, d, true); return true;
      }
    }
    return false;
  }
  function aim(s, m, consider) {
    var i;
    for (i = 0; i < s.trucks.length; i++) { var t = s.trucks[i]; if (t.st === 'ok' && t.gun > 0 && staged(s, t.x)) consider(gunnerX(t), t.y - 48); }
    for (i = 0; i < s.drones.length; i++) { var d = s.drones[i]; if (d.st !== 'gone' && staged(s, d.x)) consider(d.x, d.y); }
  }
  // a grenade of his in the air: has it touched something of theirs?
  function touch(s, x, y) {
    var i;
    for (i = 0; i < s.trucks.length; i++) { var t = s.trucks[i]; if (t.st === 'ok' && x > t.x - D.TRUCK_HW && x < t.x + D.TRUCK_HW && y > t.y - D.TRUCK_H - 14 && y < t.y) return true; }
    for (i = 0; i < s.drones.length; i++) { var d = s.drones[i]; if (d.st !== 'gone' && Math.abs(x - d.x) < 11 && Math.abs(y - d.y) < 9) return true; }
    return false;
  }
  function blast(s, x, y, r, kind, own) {
    var c = s.car, i;
    if (s.mode === 'drive' && !own && !s.p.dead) {
      var nx = clamp(x, c.x - D.REAR, c.x + D.FRONT), ny = clamp(y, c.y - D.TALL, c.y);
      if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < (r - 3) * (r - 3)) I.hurtPlayer(s, x, kind);
    }
    for (i = 0; i < s.trucks.length; i++) {
      var t = s.trucks[i];
      if (t.st !== 'ok' || (own && !staged(s, t.x))) continue;          // (his grenades do not hurt one still coming in)
      var tx = clamp(x, t.x - D.TRUCK_HW, t.x + D.TRUCK_HW), ty = clamp(y, t.y - D.TRUCK_H, t.y);
      if ((tx - x) * (tx - x) + (ty - y) * (ty - y) >= (r + 4) * (r + 4)) continue;
      t.hurtT = 0;
      if (own) dropGunner(s, t, 'blast');
      t.hp -= own ? 4 : 3;
      if (t.hp <= 0) truckGone(s, t, own ? D.TRUCK_PTS : 0, 'blast');
    }
    for (i = 0; i < s.drones.length; i++) {
      var d = s.drones[i];
      if (d.st !== 'gone' && (d.x - x) * (d.x - x) + (d.y - y) * (d.y - y) < (r + 8) * (r + 8)) popDrone(s, d, own);
    }
  }
  function sweep(s) {
    s.trucks = s.trucks.filter(function (t) { return t.st !== 'gone'; });
    s.drones = s.drones.filter(function (d) { return d.st !== 'gone'; });
  }

  Sim.ext.drive = { create: create, player: player, camera: camera, step: step, man: man, hitCar: hitCar, shot: shot, aim: aim, touch: touch, blast: blast, sweep: sweep,
                    carBox: carBox, gunnerX: gunnerX, addDrone: addDrone, popDrone: popDrone, staged: staged };
})();
if (typeof module !== 'undefined') module.exports = Sim;
