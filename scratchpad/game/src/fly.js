// fly.js - Taiz, by Apache (Khaled, 21 Oct: "start with riding the apache ... the entire (or most of) the level ... add
// vertically"). Salem flies the black Apache and Yazeed sits in the front seat with the chin gun; the player has both.
// Second cut (Khaled 03:53 after the first: "a bit floaty ... always point to the right with the ability to fly back and
// forth ... an aim stick to the gun to kill enemies front and behind, with very limited upward aim ... increase the rate
// of fire ... a ramping up beat before firing a missile at me to prompt me to use the flare"; 03:55 "the level is so
// cramped ... more zoomed out"):
// - The stick flies it, tightly: it is up to speed and stopped again in a few frames. It always faces right; flown back,
//   it reverses with its nose lifted.
// - The chin gun turns under the nose from a little above level ahead, round through straight down, to a little below
//   level behind (no higher: the barrel would be in the nose, or the belly). On a phone the right-hand stick aims it and
//   fires it (nudged onto anything close to where it points); FIRE (the key) leaves it to find the nearest thing itself,
//   and so does auto-fire.
// - BOMB sends a rocket down the nose. JUMP lets go of flares: any missile in the air goes after them, and so does one
//   launched while they burn. A missile man's lock-on is heard as a beat that quickens, then a long tone, then the launch.
// - The picture is larger than on foot (the level's zoom: s.viewW and s.viewH are its world size).
// The camera follows a route (L.fly.route), up as well as along: it moves on when the Apache pushes forward along it,
// and holds at a fight (a gate, by its distance along the route) until the fight is won. Checkpoints, who wakes up and
// the end of the mission all go by that distance (s.u), not by x. The Zanabeel scream «قنية سودا!» when it finds them,
// and at night a man caught in its searchlight for long enough throws his hands up and runs.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var T = Sim.T, DT = Sim.DT, I = Sim._, ev = I.ev;
  var F = Sim.F = {
    VX: 180, VX_BACK: 150, VY: 160,              // top speeds forward, back, and up or down (px/s)
    ACC: 1050, STOP: 1300,                       // getting up to speed; stopping when the stick is let go (px/s/s): tight, not floaty
    TILT: 0.24, TILT_LAG: 0.16,                  // nose down at full speed (radians), and how quickly the airframe follows the stick
    HW: 44, HT: 14, HB: 11,                      // its box (for being hit, and for touching stone): half its length, above and below
    EDGE_X: 62, EDGE_T: 30, EDGE_B: 22,          // how near the edges of the picture it may fly (the teaser's Apache: its nose is 59 ahead of its middle)
    GUIDE_B: 140,                                // (while the camera shows the way up at the start: the Apache taken up with it, above the left thumb)
    GUN_AT: [45, 11], LAMP_AT: [57, 3], POD_AT: [18, 4], TAIL_AT: [-30, 6],  // the chin turret, the searchlight on the nose, the rocket pod, where the flares go
    GUN_CD: 3, GUN_V: 560, GUN_LIFE: 70, GUN_SPREAD: 0.035, GUN_RANGE: 420,     // (20 rounds a second, each bursting where it lands)
    GUN_UP: 0.12, GUN_BACK: Math.PI - 0.26,      // the gun's reach: 7 degrees above level ahead, round under the nose, to 15 degrees below level behind
    GUN_SLEW: 0.16, AIM_SLEW: 0.42, AIM_ASSIST: 0.2,   // how fast it turns by itself, and on the stick; how far off the stick's line it will take a target
    ROCKETS: 12, ROCKET_CD: 16, ROCKET_V: 170, ROCKET_ACC: 820, ROCKET_MAX: 520, ROCKET_R: 30, ROCKET_LIFE: 110, ROCKET_HIT: 6,
    ROCKET_TURN: 6, RLOCK_T: 24, RLOCK_RANGE: 540,   // the rockets are guided: the pod locks on by itself (a beep at each of RLOCK_BEEPS, locked at RLOCK_T)
    FLARE_CD: 240, FLARE_LIFE: 140, FLARE_N: 3,
    CHIP: 5,                                     // rifle hits it shrugs off before one of them costs a plate
    LEAD: 0.12, LEAD_UP: 48, CAM_V: 4,           // the camera moves on once the Apache is this far ahead of the middle of the picture
    SIGHT: 380, RIFLE_V: 220,
    AA_HP: 24, AA_TELL: 34, AA_SHOTS: 6, AA_EVERY: 5, AA_V: 320, AA_COOL: 110, AA_RANGE: 430, AA_AIMED: 0.3,
    SAM_LOCK: 120, SAM_SOLID: 20, SAM_UP: 50,    // the lock-on (down behind his parapet), its last part (up, one long tone), and how long he stays up after it
    SAM_V: 190, SAM_TURN: 2.5, SAM_LIFE: 300, SAM_R: 24, SAM_RELOAD: 300, SAM_RANGE: 400, SAM_HP: 6,
    DRONE_V: 220, DRONE_HOVER: 64, DRONE_TELL: 34, DRONE_WAIT: 240, DRONE_OFF: 110,  // (a drone that cannot find its place goes anyway after DRONE_WAIT)
    EMERGE: 30,                                  // a man coming out onto a roof: out of the dark, and nothing yet
    DOOR_T: 14, RISE_T: 24, WALK_V: 66,          // out of a doorway (out of its dark), up through a hatch, then along to his post (px/s)
    CRATE_OPEN: 22, CRATE_GAP: 84,               // a crate of drones: its lid up, then one drone; and the next, a while after
    TRUCK_V: 175, TRUCK_ACC: 260, TRUCK_RANGE: 380, TRUCK_SHOTS: 5, TRUCK_EVERY: 6, TRUCK_COOL: 70, TRUCK_TELL: 18,   // the pickups (the chase)
    TRUCK_MIN: 0.6, TRUCK_ROCKET: 3,             // (running, never slower than this much of the chase's pace; a rocket hits one three times as hard)
    RPG_AIM: 46, RPG_V: 210, RPG_COOL: 210, RPG_RANGE: 380, RPG_R: 22,          // a rocket-propelled grenade: aimed, then straight, and it can be shot down
    SNIPE_AIM: 66, SNIPE_V: 760, SNIPE_COOL: 170, SNIPE_RANGE: 470,            // a sniper in a window: out of sight, then his laser on it for a second, then one round
    MORTAR_LOAD: 26, MORTAR_FUSE: 86, MORTAR_R: 30, MORTAR_COOL: 180,          // a mortar: a shell up, and where it will burst marked until it does
    LIGHT_LEN: 440, LIGHT_HALF: 0.075, LIGHT_SWEEP: 0.009, SPOT_T: 24, SPOT_LOSE: 50,   // a searchlight on the ground: in its beam long enough, it has the Apache
    SCREAM_GAP: 420,                             // the least time between two screams of «قنية سودا!»
    PANIC_T: 22,                                 // how long a man must stand in the searchlight before he runs
    BEAM_LEN: 280, BEAM_HALF: 0.2,               // the searchlight's reach and half its width (radians)
    // the people they keep tied up on the roofs (Khaled, 22 Oct 22:49: "there aren't any hostages to save in Taiz"; he chose
    // a rescue from the air): held over one, no further to the side than RESCUE_DX and no higher over his hands than
    // RESCUE_UP, the Apache lets a rope down to him in RESCUE_T (and takes it back up half as fast again when it moves off);
    // he goes up it in LIFT_T. ROPE_AT: where it hangs from, under the airframe; HANDS: how far up him he takes it
    RESCUE_DX: 30, RESCUE_UP: 72, RESCUE_T: 40, LIFT_T: 34, ROPE_AT: [-4, 11], HANDS: 30, RESCUE_ROCKETS: 5
  };
  F.RLOCK_BEEPS = [0, 8, 16];
  // what the rockets would sooner have (the pod locks on to the most worth it ahead of the nose, the nearest of equals)
  var WORTH = { aa: 3, truck: 3, sam: 2.4, drone: 2, rifle: 1, rpg: 1.6, mortar: 2, sniper: 1.8, light: 2.4, crate: 2.2, cgun: 4, launcher: 4 };
  // (and above all, the armour: guns and machines first; a man only when there is nothing of the kind in reach. Khaled,
  // 21 Oct 15:01: "the locking should prioritize high armor enemies (equipment and stationary guns)")
  var HARD = { aa: 1, truck: 1, sam: 1, mortar: 1, light: 1, crate: 1, cgun: 1, launcher: 1 };
  // the beat of a lock-on: a beep, the next a little sooner each time, until the long tone (ticks from its start)
  F.BEATS = (function () { var t = 0, gap = 26, out = []; while (t < F.SAM_LOCK - F.SAM_SOLID - 3) { out.push(Math.round(t)); t += gap; gap = Math.max(5, gap * 0.8); } return out; })();
  // the Zanabeel the air brings: the anti-aircraft gun on its emplacement, the man with a missile on his shoulder, the drone
  Sim.KIND.aa = { hw: 13, h: 22, hp: F.AA_HP, score: 400, speed: 0, lane: 0 };
  Sim.KIND.sam = { hw: 6, h: 34, hp: F.SAM_HP, score: 300, speed: 0, lane: 0 };
  Sim.KIND.drone = { hw: 8, h: 10, hp: 1, score: 200, speed: 0, lane: 0 };
  Sim.KIND.crate = { hw: 11, h: 12, hp: 8, score: 250, speed: 0, lane: 0 };
  Sim.KIND.truck = { hw: 38, h: 34, hp: 45, score: 600, speed: 0, lane: 0 };      // (a chase: the gun takes a couple of seconds over each)
  Sim.KIND.rpg = { hw: 6, h: 34, hp: 2, score: 250, speed: 0, lane: 0 };
  Sim.KIND.sniper = { hw: 5, h: 16, hp: 1, score: 300, speed: 0, lane: 0 };
  Sim.KIND.mortar = { hw: 9, h: 20, hp: 3, score: 300, speed: 0, lane: 0 };
  Sim.KIND.light = { hw: 9, h: 22, hp: 6, score: 300, speed: 0, lane: 0 };
  // the two bosses: the Castle Gun on the bastion, and the missile launcher they keep in the keep (Khaled, 21 Oct 15:01:
  // "there shouldn't be an Apache at the end, it should be something else"; he chose the launcher)
  Sim.KIND.cgun = { hw: 30, h: 34, hp: 210, score: 3000, speed: 0, lane: 0 };          // (22 Oct: its attacks all escapable now, so it lasts long enough to learn)
  Sim.KIND.launcher = { hw: 72, h: 44, hp: 480, score: 6000, speed: 0, lane: 0 };      // (against the clock since 22 Oct: tougher)
  var BG = Sim.BG = {
    CG_RISE: 44, CG_TRACK: [0, 56, 42, 30], CG_FLAK_V: 330, CG_FLAK_R: 30, CG_SWEEP_N: 8, CG_SWEEP_EVERY: 5, CG_SWEEP_TELL: 44, CG_HEAVY_V: 300,
    // (Khaled, 22 Oct, playing it: its hits could not be avoided. Every attack now has one rule that gets you out of it: a
    // flak shell bursts where the Apache was, its mark up for at least CG_FLAK_MIN; the sweep swings and glows first, and
    // can't fire lower than CG_LOW above level, so low beside the bastion is out of it; the barrage leaves one side clear;
    // and after each sweep the barrels are too hot to fire for CG_COOL)
    CG_FLAK_MIN: 45, CG_LOW: 0.5, CG_COOL: 120, CG_BARRAGE_FUSE: 62,
    // (Khaled again, 22 Oct 21:26: the sweep still shot "the full sky", impossible to dodge. Now it sweeps only from the far
    // side up to CG_OVER past straight up: the sky on the Apache's side of the gun is clear, and a red wedge shows the rest)
    CG_OVER: 0.16,
    LN_OPEN: 40, LN_ROLL_V: 56, LN_RAISE: [0, 780, 600, 450], LN_LOWER: 40, LN_LOAD: 80, LN_MAX: 1.22, LN_LEN: 104, LN_PIVOT: [62, -30],
    LN_MG_AT: [-56, -46], LN_MG_EVERY: [0, 240, 210, 180], LN_MG_SHOTS: 4, LN_MG_V: 300, LN_SMOKE_T: 130, LN_SMOKE_CD: [0, 600, 480, 420], LN_SHUF: 34,
    // the count (Khaled, 22 Oct: a timed boss): its length, when the missile is all the way up, when the crew lose count,
    // how long they argue and how much they put back on, and how long the engine burns on the rail at nought
    LN_CLOCK: 40 * 60, LN_UP_AT: 10 * 60, LN_RECOUNT_AT: 15 * 60, LN_ARGUE: 150, LN_RECOUNT_ADD: 8 * 60, LN_IGNITE: 180, LOST_T: 170,
    BIG_V: 150, BIG_CLIMB: 40, BIG_TURN: 1.5, BIG_LIFE: 480, BIG_R: 40, BIG_HP: 4,
    DAWN_T: 320, LAND_AUTO: 900, SETTLE_T: 50
  };
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function VH(s) { return s.viewH || 216; }        // the picture's height, in the world

  // ------------------------------------------------------------------ the route, and the stone
  // (worked out once for a level and kept on it: the level is the same for every game)
  // (each corner is rounded off, CORNER px either side of it, so the camera turns from along to up rather than jolting)
  var CORNER = 90;
  function route(L) {
    if (L._route) return L._route;
    var P = L.fly.route, R = [P[0]], cum = [0], i, k;
    for (i = 1; i < P.length - 1; i++) {
      var a = P[i - 1], b = P[i], c = P[i + 1];
      var l1 = Math.hypot(b[0] - a[0], b[1] - a[1]), l2 = Math.hypot(c[0] - b[0], c[1] - b[1]), r = Math.min(CORNER, l1 / 2, l2 / 2);
      var p0 = [b[0] - (b[0] - a[0]) / l1 * r, b[1] - (b[1] - a[1]) / l1 * r], p2 = [b[0] + (c[0] - b[0]) / l2 * r, b[1] + (c[1] - b[1]) / l2 * r];
      for (k = 0; k <= 8; k++) {              // a quadratic curve from p0 to p2, pulled towards the corner
        var t = k / 8, w0 = (1 - t) * (1 - t), w1 = 2 * t * (1 - t), w2 = t * t;
        R.push([w0 * p0[0] + w1 * b[0] + w2 * p2[0], w0 * p0[1] + w1 * b[1] + w2 * p2[1]]);
      }
    }
    R.push(P[P.length - 1]);
    for (i = 1; i < R.length; i++) cum.push(cum[i - 1] + Math.hypot(R[i][0] - R[i - 1][0], R[i][1] - R[i - 1][1]));
    L._route = { pts: R, cum: cum, len: cum[cum.length - 1] };
    return L._route;
  }
  // the point u along the route, and the way the route is going there
  function at(rt, u) {
    var R = rt.pts, n = R.length, i = 1;
    u = clamp(u, 0, rt.len);
    while (i < n - 1 && rt.cum[i] < u) i++;
    var seg = rt.cum[i] - rt.cum[i - 1] || 1, f = clamp((u - rt.cum[i - 1]) / seg, 0, 1);
    var dx = (R[i][0] - R[i - 1][0]) / seg, dy = (R[i][1] - R[i - 1][1]) / seg;
    return { x: R[i - 1][0] + (R[i][0] - R[i - 1][0]) * f, y: R[i - 1][1] + (R[i][1] - R[i - 1][1]) * f, dx: dx, dy: dy };
  }
  // the way the route is going from u, looking a little ahead (round a corner, the way it goes after it): the camera moves
  // on when the Apache is ahead of the middle of the picture that way
  var LOOK = 80;
  function ahead(rt, u) {
    var c = at(rt, u), a = at(rt, Math.min(rt.len, u + LOOK)), dx = a.x - c.x, dy = a.y - c.y, d = Math.sqrt(dx * dx + dy * dy);
    if (d < 1) return { x: c.x, y: c.y, dx: c.dx, dy: c.dy };
    return { x: c.x, y: c.y, dx: dx / d, dy: dy / d };
  }
  // how far along the route a point is (the nearest place on it)
  function uOf(rt, x, y) {
    var R = rt.pts, best = 0, bd = 1e18;
    for (var i = 1; i < R.length; i++) {
      var ax = R[i - 1][0], ay = R[i - 1][1], dx = R[i][0] - ax, dy = R[i][1] - ay, l2 = dx * dx + dy * dy || 1;
      var f = clamp(((x - ax) * dx + (y - ay) * dy) / l2, 0, 1), qx = ax + dx * f, qy = ay + dy * f, d = (x - qx) * (x - qx) + (y - qy) * (y - qy);
      if (d < bd) { bd = d; best = rt.cum[i - 1] + f * Math.sqrt(l2); }
    }
    return best;
  }
  // the checkpoints, the fights and the triggers may be given as a place on the route (at: [x, y]) rather than as a
  // distance along it (u): the distance is worked out once, the same for every game
  function prep(L) {
    if (L._prep) return;
    var rt = route(L), k;
    function U(o, key, atKey) { if (o[key] == null && o[atKey]) o[key] = uOf(rt, o[atKey][0], o[atKey][1]); }
    L.zones.forEach(function (z) { U(z, 'u', 'at'); });
    L.gates.forEach(function (g) { U(g, 'u', 'at'); if (g.chase) g.chase.u0 = uOf(rt, g.chase.from[0], g.chase.from[1]); });
    for (k in L.groups) U(L.groups[k], 'trigU', 'trigAt');
    (L.fly.light || []).forEach(function (q) { U(q, 'u', 'at'); });
    if (L.fly.guide) U(L.fly.guide, 'u', 'to');
    L._doors = {};
    (L.fly.doors || []).forEach(function (d) { L._doors[d.id] = d; });
    L._prep = true;
  }
  function rocks(L) {
    if (L._rocks) return L._rocks;
    L._rocks = (L.fly.rock || []).map(function (P) {
      var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (var i = 0; i < P.length; i++) { x0 = Math.min(x0, P[i][0]); x1 = Math.max(x1, P[i][0]); y0 = Math.min(y0, P[i][1]); y1 = Math.max(y1, P[i][1]); }
      return { pts: P, x0: x0, y0: y0, x1: x1, y1: y1 };
    });
    return L._rocks;
  }
  function inPoly(P, x, y) {
    var c = false;
    for (var i = 0, j = P.length - 1; i < P.length; j = i++) {
      var xi = P[i][0], yi = P[i][1], xj = P[j][0], yj = P[j][1];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  }
  function rockAt(L, x, y) {
    var R = rocks(L);
    for (var i = 0; i < R.length; i++) { var r = R[i]; if (x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1 && inPoly(r.pts, x, y)) return true; }
    return y >= Sim.groundY(L, x);
  }
  function rock(s, x, y) { return rockAt(s.L, x, y); }
  // stone between two points (looked for at a few places along the line)
  function blocked(L, x0, y0, x1, y1) {
    for (var k = 1; k < 8; k++) { var f = k / 8; if (rockAt(L, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)) return true; }
    return false;
  }
  // the Apache's box touching stone: its nose, its tail, its belly, the top of its mast
  function heliRock(L, x, y) {
    var w = F.HW;
    return rockAt(L, x - w, y) || rockAt(L, x + w, y) || rockAt(L, x - w * 0.55, y + F.HB) || rockAt(L, x + w * 0.55, y + F.HB) ||
           rockAt(L, x, y + F.HB) || rockAt(L, x, y - F.HT) || rockAt(L, x - w * 0.5, y - F.HT * 0.6) || rockAt(L, x + w * 0.5, y - F.HT * 0.6);
  }
  function heliBox(h) { return { x0: h.x - F.HW, x1: h.x + F.HW, y0: h.y - F.HT, y1: h.y + F.HB }; }
  function inView(s, x, y, pad) { return x >= s.cam - pad && x <= s.cam + s.viewW + pad && y >= s.camY - pad && y <= s.camY + VH(s) + pad; }
  // the middle of the picture, clear of the thumbs: where they may start an attack
  function staged(s, x, y) { return x >= s.cam + s.viewW * s.laneL - 6 && x <= s.cam + s.viewW * (1 - s.laneR) + 6 && y >= s.camY + 8 && y <= s.camY + VH(s) + 4; }
  // how dark it is u along the route: 0 day, 1 deep night (the level's light: [{ u (or at: [x, y]), d }, ...])
  function dark(L, u) {
    var K = L.fly.light, i;
    if (!K || !K.length) return 0;
    prep(L);
    if (u <= K[0].u) return K[0].d;
    for (i = 1; i < K.length; i++) if (u <= K[i].u) { var f = (u - K[i - 1].u) / (K[i].u - K[i - 1].u || 1); return K[i - 1].d + (K[i].d - K[i - 1].d) * f; }
    return K[K.length - 1].d;
  }

  // ------------------------------------------------------------------ setting up
  function create(s, opts) {
    var L = s.L, i;
    s.heli = null; s.missiles = []; s.rockets = []; s.flares = []; s.shells = []; s.chaseT = 0; s.chaseOn = false; s.chaseEnd = false; s.spotT = 0; s.guide = null; s.lost = null;
    if (!L.fly) return;
    prep(L);
    var rt = route(L), z = L.zones[s.zone];
    s.mode = 'fly';
    s.u = z.u || 0;
    var c = at(rt, s.u);
    s.cam = c.x - s.viewW / 2; s.camY = c.y - VH(s) / 2;
    var sp = z.pos || [c.x - s.viewW * 0.22, c.y - 6];
    s.heli = { x: sp[0], y: sp[1], vx: 0, vy: 0, face: 1, turnT: 0, tilt: 0, st: 'fly', t: 0, spin: 0, ang: 0, gunA: 0.3, flareCd: 0, rocketCd: 0, side: 0,
               chip: 0, beam: 0.62, target: null, aiming: false, wreckT: 0, inY: sp[1], rlock: 0, rlockT: 0 };
    var p = s.p;
    p.x = s.heli.x; p.y = s.heli.y; p.face = 1; p.weapon = 'chin'; p.grenades = F.ROCKETS; p.air = true; p.plat = -2;
    s.zoom = L.zoom || 1; s.intro = null; s.yaz = null;
    if (s.zone === 0 && L.fly.intro && !opts.stats) startIntro(s, L.fly.intro);          // a mission begun from the start: the opening, on foot
    else if (s.zone === 0 && L.fly.arrive) { s.heli.x = s.cam - 70; s.heli.y = sp[1] - 24; s.heli.vx = F.VX; s.heli.st = 'in'; }      // (a continue: it comes in from the left, over the roofs)
    s.gates.forEach(function (g, k) { g.u = L.gates[k].u; });
    s.holdU = null;
    s.screamT = -9999; s.locking = 0; s.lockT = 0; s.scattered = 0;
    // the men at their posts on the roofs and the ledges, the guns, the missile men; drones come later, when they are woken
    for (i = 0; i < L.fly.spawns.length; i++) {
      var q = L.fly.spawns[i], G = s.groups[q.g];
      if (G.done) continue;
      if (q.k === 'drone' || q.enter || (q.from && q.k !== 'crate')) { G.pending.push({ sp: q, at: q.delay || 0 }); continue; }
      place(s, q);
    }
  }
  // a man (or a gun) at his post: on a roof or a ledge (a platform, so that he has something to fall on), or at q.y
  function place(s, q) {
    var L = s.L, x = q.x, pl = q.plat ? L.plats[I.platIndex(L, q.plat)] : null;
    if (pl) x = clamp(x, pl.pts[0][0], pl.pts[pl.pts.length - 1][0]);          // (on his roof, whatever the level says)
    var e = I.spawnEnemy(s, { g: q.g, k: q.k, post: 1, look: q.look || 'angry', plat: q.plat }, x);
    e.ext = 'fly'; e.air = false;
    if (!q.plat) { e.y = q.y != null ? q.y : Sim.groundY(L, x); e.plat = -1; }          // (in the street, or on the road)
    e.px = e.x; e.py = e.y;
    e.face = q.face || -1; e.st = 'wait'; e.stT = 0; e.cd = (q.k === 'rifle' ? 4 + Math.floor(s.rand() * 10) : Math.round((20 + Math.floor(s.rand() * 40)) * T.FIRST)) + (q.cd || 0);      // (R5: T.FIRST and T.GAP, sim.js; the bosses keep theirs)
    e.u = uOf(route(L), e.x, e.y); e.bar = -Math.PI / 2; e.beamT = 0; e.brave = q.k !== 'rifle' || e.id % 3 !== 0; if (q.k === 'rifle') e.first = true;      // (23 Oct: two in three riflemen stand their ground; the first burst gets made, as on foot)
    if (q.k === 'sam') e.cd = Math.round((8 + Math.floor(s.rand() * 16)) * T.FIRST) + (q.cd || 0);          // (the missile man does not hang about)
    if (q.k === 'crate') { e.left = q.n || 3; e.lid = 0; e.brave = true; e.oops = !!q.oops; }
    if (q.k === 'truck') { e.y = groundAt(L, x); e.st = 'park'; e.vx = 0; e.paint = q.paint || 'olive'; e.lead = q.lead || 0.6; e.gst = 'wait'; e.gT = 0; e.gcd = Math.round((30 + Math.floor(s.rand() * 30)) * T.FIRST); e.wheel = 0; e.ang = slopeAt(L, x); e.brave = true; e.face = 1; e.load = q.load || null; }
    if (q.k === 'sniper') { e.x = q.win[0]; e.y = q.win[1]; e.plat = -1; e.px = e.x; e.py = e.y; e.st = 'hide'; e.hidden = true; e.cd = Math.round((30 + Math.floor(s.rand() * 50)) * T.FIRST); e.brave = true; }
    if (q.k === 'light') { e.beam = -Math.PI / 2 + (q.beam || -0.5); e.dir = q.dir || 1; e.lk = 0; e.lose = 0; e.brave = true; }
    if (q.k === 'mortar' || q.k === 'rpg') e.brave = true;
    if (q.k === 'cgun') { e.st = 'cover'; e.hidden = true; e.brave = true; e.bar = -2.6; e.rise = 0; e.phase = 1; e.plan = []; e.boss = true; e.face = -1; }
    if (q.k === 'launcher') { e.st = 'hide'; e.hidden = true; e.brave = true; e.boss = true; e.face = -1; e.phase = 1; e.stopX = q.stop || e.x; e.raise = 0; e.missile = true; e.door = 0; e.wheel = 0; e.shufT = 0;
      e.mgst = 'wait'; e.mgcd = 60; e.mgT = 0; e.shots = 0; e.gunA = Math.PI; e.smokeT = 0; e.smokeCd = 0; e.lk = 0; e.ramT = 0; }
    // how he gets to his post: out of a door and along, up through a hatch, along from further off
    var how = q.from || '', d = how.indexOf('door:') === 0 ? L._doors[how.slice(5)] : null;
    if (d || how.indexOf('run:') === 0) {
      var sx = d ? d.x : +how.slice(4);
      e.x = sx; e.y = standY(L, e, sx);
      e.goX = e.px; e.st = 'out'; e.emerge = d ? F.DOOR_T : 0; e.entry = d ? 'door' : 'run';
      e.face = e.goX >= e.x ? 1 : -1;
    } else if (how === 'hatch') { e.emerge = F.RISE_T; e.entry = 'hatch'; }
    return e;
  }
  // the ground under a pickup, and its slope (the road, the street)
  function groundAt(L, x) { return Sim.groundY(L, clamp(x, 0, L.width)); }
  function slopeAt(L, x) { return Math.atan2(groundAt(L, x + 12) - groundAt(L, x - 12), 24); }
  // where a man walking stands at x: on his roof or ledge while it goes on under him, else the ground
  function standY(L, e, x) {
    if (e.plat >= 0) { var py = Sim.platY(L.plats[e.plat], x); if (py !== null) return py; }
    return Sim.groundY(L, clamp(x, 0, L.width));
  }
  // a flight of drones (or anything else that comes in), from the edge of the picture ahead
  function arrive(s, q) {
    if (q.k !== 'drone') {
      var m = place(s, q);
      if (!q.from) { m.emerge = F.EMERGE; ev(s, { t: 'emerge', x: m.x, y: m.y, k: m.k }); }
      else ev(s, { t: 'enter', x: m.x, y: m.y, k: m.k, how: m.entry });
      m.cd = Math.max(m.cd, (m.emerge || 0) + Math.round(16 * T.FIRST));
      return;
    }
    // a flight of drones, in from ahead (or from behind) at about the Apache's height: they are seen coming
    var n = q.n || 1, h = s.heli, hy = h ? h.y : s.camY + VH(s) / 2;
    for (var k = 0; k < n; k++) {
      var e = droneOut(s, q.g, k, n);
      var y = clamp(hy - 16 + k * 24, s.camY + 30, s.camY + VH(s) - 50);
      if (q.from === 'left') { e.x = s.cam - 24 - k * 30; e.y = y; e.side = -1; }
      else { e.x = s.cam + s.viewW + 24 + k * 30; e.y = y; }
      e.wait = k * 26;
    }
  }
  function droneOut(s, g, k, n) {
    var e = I.spawnEnemy(s, { g: g, k: 'drone', post: 1, look: 'drone' }, 0);
    e.ext = 'fly'; e.air = false; e.plat = -2;
    e.st = 'in'; e.stT = 0; e.wait = 0; e.hx = 0; e.hy = 0; e.off = (k - (n - 1) / 2) * 52; e.u = s.u; e.brave = true; e.side = 1;
    return e;
  }

  // ------------------------------------------------------------------ the opening (Khaled, 05:23: "make the teaser part of the
  // intro ... apache comes in, scares the zanabeel then player walks and enters it, camera zooms out and we continue")
  // Yazeed on foot in the street at night, five of the Zanabeel across it with their guns on him. The Apache comes in over
  // the roofs with its searchlight on; it finds them, «قنية سودا!», and they run for the doors with their hands up. It sets
  // down in the street; Yazeed walks to it (the stick) and climbs in; it lifts off, and the picture draws back to the
  // Apache's (the level's zoom) as it flies on to where the mission starts. A button in the first part skips to the landing.
  var OP = { IN: 80, FIND: 150, SCREAM: 196, RUN: 210, LAND: 250, LANDED: 330, WALK_V: 96, BOARD: 26, LIFT: 44, ZOOM: 110 };
  function startIntro(s, Q) {
    var L = s.L, h = s.heli, p = s.p, Lz = L.zoom || 1, k;
    s.zoom = 1; s.fullW = s.viewW; s.fullH = s.viewH;
    s.viewW = Math.round(s.fullW / Lz); s.viewH = Math.round(s.fullH / Lz);
    s.intro = { t: 0, st: 'show', Q: Q, boardT: 0, liftT: 0, zoomT: 0, from: null, lastW: s.viewW, lastH: s.viewH };
    s.cam = 0; s.camY = Q.street - s.viewH + 14;
    s.yaz = { x: Q.yazeed, y: Q.street, face: 1, st: 'stand', walkD: 0, t: 0, a: 1 };
    h.st = 'off'; h.x = -130; h.y = Q.street - 176; h.vx = 0; h.vy = 0; h.tilt = 0; h.beam = 0.05; h.inY = h.y;
    p.x = s.yaz.x; p.y = s.yaz.y;
    var looks = ['angry', 'youth', 'qat', 'worried', 'angry'];
    for (k = 0; k < Q.men.length; k++) {
      var mx = Q.men[k], e = I.spawnEnemy(s, { g: 'Z0', k: 'rifle', post: 1, look: looks[k % looks.length] }, mx), best = Q.doors[0];
      for (var d = 0; d < Q.doors.length; d++) if (Math.abs(Q.doors[d] - mx - 10) < Math.abs(best - mx - 10)) best = Q.doors[d];
      e.ext = 'fly'; e.intro = true; e.first = false; e.plat = -1; e.y = Q.street; e.st = 'aim'; e.stT = 0; e.face = -1; e.px = e.x; e.py = e.y; e.u = 0; e.exitX = best; e.brave = false;
    }
  }
  function introMan(s, e) {
    var O = s.intro, sp = 74 * DT;
    if (!O || e.st === 'aim') return;
    if (e.st === 'panic') {
      // hands up, away to the nearest door; in through it (or out of the picture), gone
      var dx = e.exitX - e.x;
      e.face = dx >= 0 ? 1 : -1; e.moving = e.face;
      if (Math.abs(dx) <= sp || e.x < s.cam - 30 || e.x > s.cam + s.viewW + 30) {
        e.moving = 0; I.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999;
        if (Math.abs(dx) <= sp) ev(s, { t: 'enter', x: e.x, y: e.y, how: 'door' });
      } else { e.x += e.face * sp; e.walkD += sp; }
    }
  }
  // (the picture's size given with the thumbs is the Apache's: taken as that, unless it is the opening's own given back)
  function opening(s, inp) {
    var O = s.intro;
    if (inp.viewW && inp.viewW !== O.lastW) s.fullW = inp.viewW;
    if (inp.viewH && inp.viewH !== O.lastH) s.fullH = inp.viewH;
    openingStep(s, inp);
    O.lastW = s.viewW; O.lastH = s.viewH;
  }
  function openingStep(s, inp) {
    var O = s.intro, Q = O.Q, h = s.heli, p = s.p, L = s.L, y = s.yaz, i, e;
    O.t++;
    var Lz = L.zoom || 1, flying = s.status === 'play';
    var ax = inp.ax != null ? inp.ax : inp.mx, btn = !!(inp.fire || inp.jump || inp.grenade || inp.gun);
    var landX = Q.land, landY = Q.street - 19, hoverX = Q.men[1] - 120, hoverY = Q.street - 150;
    if (O.st === 'show') {
      // a button skips to the Apache waiting in the street
      if (btn && !O.held && O.t > 10) { skipShow(s); return; }
      O.held = btn;
      if (O.t >= OP.IN && h.st === 'off') { h.st = 'arrive'; h.vx = 150; ev(s, { t: 'heli_in', x: h.x, y: h.y }); }
      if (h.st === 'arrive') {
        h.vx = Math.max(24, Math.min(150, (hoverX - h.x) * 1.6)); h.x += h.vx * DT; h.y += (hoverY - h.y) * 0.04;
        h.tilt += (F.TILT * h.vx / F.VX - h.tilt) * F.TILT_LAG;
        if (h.x > hoverX - 6) { h.st = 'hover'; h.vx = 0; }
      } else if (h.st === 'hover') { h.y += (hoverY - h.y) * 0.05 + Math.sin(O.t / 14) * 0.15; h.tilt *= 0.9; }
      // the searchlight: down onto the men across the street
      var mx0 = Q.men[2], aim = Math.atan2(Q.street - 20 - (h.y + 3), mx0 - (h.x + 57));
      if (h.st !== 'off') h.beam += clamp((O.t > OP.FIND - 30 ? aim : 0.25) - h.beam, -0.025, 0.025);
      if (O.t === OP.FIND) for (i = 0; i < s.enemies.length; i++) { e = s.enemies[i]; if (e.intro && e.alive) ev(s, { t: 'startle', x: e.x, y: e.y, id: e.id }); }
      if (O.t === OP.SCREAM) { var m0 = firstMan(s); if (m0) ev(s, { t: 'qanya', x: m0.x, y: m0.y - m0.h, id: m0.id, k: 'rifle' }); }
      if (O.t >= OP.RUN && O.t < OP.RUN + 40 && (O.t - OP.RUN) % 8 === 0) {
        var mm = null;
        for (i = 0; i < s.enemies.length; i++) { e = s.enemies[i]; if (e.intro && e.alive && e.st === 'aim') { mm = e; break; } }
        if (mm) { mm.st = 'panic'; mm.stT = 0; ev(s, { t: 'scatter', x: mm.x, y: mm.y, id: mm.id, k: 'rifle', pts: 0 }); }
      }
      if (O.t >= OP.LAND) {
        // down into the street where they stood
        h.st = 'land';
        h.x += clamp(landX - h.x, -60 * DT, 60 * DT); h.y += clamp(landY - h.y, -70 * DT, 52 * DT);
        h.tilt += (clamp((landX - h.x) * 0.004, -0.1, 0.1) - h.tilt) * 0.1;
        h.beam += clamp(0.45 - h.beam, -0.02, 0.02);
        if (Math.abs(h.x - landX) < 1 && Math.abs(h.y - landY) < 1 && O.t > OP.LANDED - 20) landed(s);
      }
    } else if (O.st === 'wait') {
      // the player walks Yazeed to it (the stick, or the arrows)
      h.y = landY; h.tilt *= 0.9;
      var go = clamp(ax || 0, -1, 1), bx = h.x + 12;
      if (Math.abs(go) > 0.2) {
        var nx = clamp(y.x + go * OP.WALK_V * DT, s.cam + 10, bx);
        y.face = go > 0 ? 1 : -1; y.walkD += Math.abs(nx - y.x); y.x = nx; y.st = 'walk';
      } else y.st = 'stand';
      if (y.x >= bx - 1) { O.st = 'board'; O.boardT = 0; y.st = 'board'; y.face = 1; ev(s, { t: 'board', x: y.x, y: y.y }); }
    } else if (O.st === 'board') {
      // up into the front seat
      O.boardT++;
      y.a = Math.max(0, 1 - O.boardT / OP.BOARD); y.y = Q.street - Math.min(18, O.boardT * 1.2);
      if (O.boardT >= OP.BOARD + 20) { O.st = 'lift'; O.liftT = 0; y.st = 'gone'; h.st = 'lift'; ev(s, { t: 'liftoff', x: h.x, y: h.y }); }
    } else if (O.st === 'lift') {
      O.liftT++;
      h.y = landY - 46 * smooth(O.liftT / OP.LIFT); h.tilt += (-0.04 - h.tilt) * 0.1;
      if (O.liftT >= OP.LIFT) { O.st = 'zoom'; O.zoomT = 0; O.from = { cx: s.cam + s.viewW / 2, cy: s.camY + s.viewH / 2, hx: h.x, hy: h.y }; }
    } else if (O.st === 'zoom') {
      // the picture draws back to the Apache's as it flies on to where the mission starts
      O.zoomT++;
      var f = smooth(O.zoomT / OP.ZOOM), rt = route(L), c = at(rt, 0), z = L.zones[0], sp = z.pos || [c.x - s.fullW * 0.22, c.y - 6];
      s.zoom = 1 + (Lz - 1) * f;
      var cx2 = O.from.cx + (c.x - O.from.cx) * f, cy2 = O.from.cy + (c.y - O.from.cy) * f;
      var hf = smooth(Math.min(1, O.zoomT / (OP.ZOOM * 0.85)));
      var nhx = O.from.hx + (sp[0] - O.from.hx) * hf, nhy = O.from.hy + (sp[1] - O.from.hy) * hf;
      h.vx = (nhx - h.x) / DT; h.vy = (nhy - h.y) / DT; h.x = nhx; h.y = nhy;
      h.tilt += (clamp(F.TILT * h.vx / F.VX, -F.TILT, F.TILT) - h.tilt) * F.TILT_LAG;
      s.viewW = Math.round(s.fullW * s.zoom / Lz); s.viewH = Math.round(s.fullH * s.zoom / Lz);
      s.cam = cx2 - s.viewW / 2; s.camY = cy2 - s.viewH / 2;
      if (O.zoomT >= OP.ZOOM) {
        s.zoom = Lz; s.viewW = s.fullW; s.viewH = s.fullH; s.u = 0; s.cam = c.x - s.viewW / 2; s.camY = c.y - s.viewH / 2;
        s.intro = null; s.yaz = null;
        h.st = 'fly'; h.vx = Math.min(h.vx, F.VX * 0.6); h.vy = 0;
        p.x = h.x; p.y = h.y;
        ev(s, { t: 'heli_ready' });
        startGuide(s);
        return;
      }
      p.x = h.x; p.y = h.y;
      return;
    }
    if (O.st !== 'zoom') { s.viewW = Math.round(s.fullW / Lz); s.viewH = Math.round(s.fullH / Lz); }
    // the camera stays on the street, along with Yazeed if he walks out of it
    if (y && O.st !== 'zoom') { s.cam = Math.max(0, Math.min(s.cam, y.x - 60)); s.cam = Math.max(s.cam, y.x + 60 - s.viewW, 0); s.camY = Q.street - s.viewH + 14; }
    p.x = y ? y.x : h.x; p.y = y ? y.y : h.y;
  }
  function smooth(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
  // the way up, shown: once the Apache is the player's at the start, the camera goes on up the route by itself to where
  // the way levels out over the roofs, and the way-up sign flashes (Khaled, 21 Oct: "after lift off, its not clear that I
  // need to go upward, maybe have the camera guide me there")
  function startGuide(s) {
    var G = s.L.fly.guide;
    if (!G || s.zone !== 0) return;
    prep(s.L);
    if (s.u >= G.u - 1) return;
    s.guide = { u: s.u, u1: G.u, v: G.v };
    ev(s, { t: 'go', dir: 'up', quiet: true });
  }
  function firstMan(s) { for (var i = 0; i < s.enemies.length; i++) if (s.enemies[i].intro && s.enemies[i].alive) return s.enemies[i]; return null; }
  function landed(s) {
    var O = s.intro, h = s.heli;
    O.st = 'wait'; h.st = 'landed'; h.x = O.Q.land; h.y = O.Q.street - 19; h.vx = 0; h.vy = 0; h.tilt = 0;
    ev(s, { t: 'landed', x: h.x, y: h.y });
  }
  function skipShow(s) {
    var O = s.intro, h = s.heli;
    for (var i = 0; i < s.enemies.length; i++) { var e = s.enemies[i]; if (e.intro && e.alive) { I.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; } }
    h.beam = 0.45;
    landed(s);
  }

  // ------------------------------------------------------------------ the Apache
  function player(s, inp) {
    var p = s.p, h = s.heli, L = s.L;
    if (!h) return;
    p.fireT++; p.hurtT++; h.t++;
    if (p.inv > 0) p.inv--;
    if (p.fireCd > 0) p.fireCd--;
    if (h.flareCd > 0) h.flareCd--;
    if (h.rocketCd > 0) h.rocketCd--;
    if (p.dead) { down(s); return; }
    if (s.intro) { opening(s, inp); return; }
    if (h.st === 'settle' || h.st === 'landed') { p.x = h.x; p.y = h.y; h.beam += clamp(0.5 - h.beam, -0.02, 0.02); return; }
    if (h.st === 'in') {
      // the opening: in from the left over the town, slowing into the picture
      var tx = s.cam + s.viewW * 0.28;
      h.vx = Math.max(40, Math.min(F.VX, (tx - h.x) * 2.2)); h.x += h.vx * DT; h.y += (h.inY - h.y) * 0.03;
      h.tilt += (F.TILT * h.vx / F.VX - h.tilt) * F.TILT_LAG;
      if (h.x >= tx - 2) { h.st = 'fly'; ev(s, { t: 'heli_ready' }); startGuide(s); }
      p.x = h.x; p.y = h.y;
      return;
    }
    var flying = s.status === 'play';
    var ax = inp.ax != null ? inp.ax : inp.mx, ay = inp.ay != null ? inp.ay : inp.my;
    if (!flying) { ax = 0.6; ay = -0.25; }                    // (the end: it flies on out of the picture)
    var fire = flying && !!inp.fire, jump = flying && !!inp.jump, gren = flying && !!inp.grenade;
    var jumpPressed = jump && !s.prev.jump, grenPressed = gren && !s.prev.grenade;
    s.prev.jump = jump; s.prev.fire = fire; s.prev.grenade = gren;

    // the stick: a speed to get to, quickly; let go, and it stops as quickly. Back is a little slower than forward.
    ax = clamp(ax || 0, -1, 1); ay = clamp(ay || 0, -1, 1);
    var tvx = ax * (ax < 0 ? F.VX_BACK : F.VX), tvy = ay * F.VY;
    var rx = Math.abs(tvx) > Math.abs(h.vx) * 0.98 || tvx * h.vx < 0 ? F.ACC : F.STOP, ry = Math.abs(tvy) > Math.abs(h.vy) * 0.98 || tvy * h.vy < 0 ? F.ACC : F.STOP;
    if (tvx * h.vx < 0) rx = F.STOP;                          // (turning about: it brakes first)
    if (tvy * h.vy < 0) ry = F.STOP;
    h.vx += clamp(tvx - h.vx, -rx * DT, rx * DT);
    h.vy += clamp(tvy - h.vy, -ry * DT, ry * DT);
    // along, then up or down, each stopped by stone and by the edges of the picture (at the end it flies off as it likes)
    var x0 = h.x, y0 = h.y;
    h.x += h.vx * DT;
    if (flying) {
      var lo = s.cam + F.EDGE_X, hi = s.cam + s.viewW - F.EDGE_X;
      if (h.x < lo) { h.x = lo; if (h.vx < 0) h.vx = 0; }
      if (h.x > hi) { h.x = hi; if (h.vx > 0) h.vx = 0; }
      if (heliRock(L, h.x, h.y)) { h.x = x0; if (Math.abs(h.vx) > 90) ev(s, { t: 'scrape', x: h.x + (h.vx > 0 ? F.HW : -F.HW), y: h.y }); h.vx = 0; }
    }
    h.y += h.vy * DT;
    if (flying) {
      var top = s.camY + F.EDGE_T, bot = s.camY + VH(s) - (s.guide ? F.GUIDE_B : F.EDGE_B);
      if (h.y < top) { h.y = top; if (h.vy < 0) h.vy = 0; }
      if (h.y > bot) { h.y = bot; if (h.vy > 0) h.vy = 0; }
      if (heliRock(L, h.x, h.y)) { h.y = y0; if (Math.abs(h.vy) > 90) ev(s, { t: 'scrape', x: h.x, y: h.y + (h.vy > 0 ? F.HB : -F.HT) }); h.vy = 0; }
      // (the edge of the picture may have pushed it into stone: up and out)
      for (var k = 0; k < 40 && heliRock(L, h.x, h.y); k++) h.y -= 1;
    }
    // the nose: down going forward, up going back or stopping, level in a hover; the airframe a moment behind the stick
    var tilt = F.TILT * h.vx / (h.vx >= 0 ? F.VX : F.VX_BACK) * (h.vx >= 0 ? 1 : 0.8) + 0.06 * ax;
    h.tilt += (clamp(tilt, -F.TILT, F.TILT) - h.tilt) * F.TILT_LAG;
    p.x = h.x; p.y = h.y; p.face = 1; p.vx = h.vx; p.vy = h.vy;

    // the chin gun (on the aim stick; or held, or left to fire itself, finding its own target), the rockets, the flares
    gun(s, inp, flying, fire);
    podLock(s, inp, flying);
    if (grenPressed && h.rocketCd <= 0 && p.grenades > 0) rocketOut(s);
    if (jumpPressed && h.flareCd <= 0) flaresOut(s);
    // the searchlight looks where the gun looks, or ahead and down
    var bw = h.aiming || h.target ? h.gunA : 0.62;
    h.beam += clamp(bw - h.beam, -0.07, 0.07);
  }
  // shot down: it spins, smokes and comes down; in a while another one comes in
  function down(s) {
    var p = s.p, h = s.heli, L = s.L;
    if (p.dead === 1) { h.st = 'down'; h.spin = 0.16; h.vy = Math.min(h.vy, -40); h.aiming = false; h.target = null; ev(s, { t: 'heli_down', x: h.x, y: h.y }); }
    p.dead++;
    if (h.st === 'down') {
      h.vy = Math.min(260, h.vy + 330 * DT); h.vx *= 0.99;
      h.x += h.vx * DT; h.y += h.vy * DT; h.ang += h.spin;
      if (heliRock(L, h.x, h.y) || h.y > s.camY + VH(s) + 40) {
        h.st = 'wreck'; h.wreckT = 0;
        I.explode(s, h.x, h.y, 34, 'heli', true);
      }
    }
    if (p.dead > T.DEATH_T) {
      p.lives--;
      if (p.lives <= 0) { s.status = 'over'; ev(s, { t: 'over' }); return; }
      p.dead = 0; p.plates = T.PLATES; p.inv = T.RESPAWN_INV; p.grenades = Math.max(p.grenades, F.ROCKETS >> 1);
      var sp = clearSpot(s, at(route(L), s.u));
      h.x = sp[0]; h.y = sp[1]; h.vx = 0; h.vy = 0; h.ang = 0; h.spin = 0; h.tilt = 0; h.face = 1; h.turnT = 0; h.st = 'fly'; h.chip = 0;
      p.x = h.x; p.y = h.y;
      ev(s, { t: 'respawn', x: h.x, y: h.y, heli: true });
    }
  }
  // somewhere in the open, inside the picture, near the route's point c (behind it first): where a new Apache comes in
  function clearSpot(s, c) {
    var L = s.L, xs = [-0.22, -0.12, 0, -0.3, 0.12, 0.22], top = s.camY + F.EDGE_T + 4, bot = s.camY + VH(s) - F.EDGE_B - 4, i, y;
    for (i = 0; i < xs.length; i++) {
      var x = clamp(c.x + s.viewW * xs[i], s.cam + F.EDGE_X + 4, s.cam + s.viewW - F.EDGE_X - 4);
      for (y = clamp(c.y - 10, top, bot); y >= top; y -= 4) if (!heliRock(L, x, y)) return [x, y];
      for (y = clamp(c.y - 10, top, bot); y <= bot; y += 4) if (!heliRock(L, x, y)) return [x, y];
    }
    return [clamp(c.x - s.viewW * 0.22, s.cam + F.EDGE_X + 4, s.cam + s.viewW - 60), top];
  }
  // a place on the airframe (o: forward of its middle, below it), as it is tilted now
  function bodyAt(h, o) {
    var c = Math.cos(h.tilt), sn = Math.sin(h.tilt), lx = o[0] * c - o[1] * sn, ly = o[0] * sn + o[1] * c;
    return { x: h.x + lx * h.face, y: h.y + ly };
  }
  // where the chin gun turns, under the nose (its shots leave from the end of the barrel); the searchlight on the nose
  function muzzle(h) { return bodyAt(h, F.GUN_AT); }
  function lamp(h) { return bodyAt(h, F.LAMP_AT); }
  // an angle into the gun's reach (from straight ahead, 0, clockwise: down is pi/2, straight back pi): a little above level
  // ahead, round under the nose, to a little below level behind. Pointed up ahead it stops at its top; up behind, at the
  // back of its reach.
  function reach(a) {
    if (a < -F.GUN_UP) return a > -Math.PI / 2 ? -F.GUN_UP : F.GUN_BACK;
    return a > F.GUN_BACK ? F.GUN_BACK : a;
  }
  // the gun: on the aim stick it points where the stick does (nudged onto a target close to that line) and fires; on FIRE
  // or auto-fire it turns to the nearest thing it can reach and fires at it (FIRE fires at nothing too)
  function gun(s, inp, flying, fire) {
    var p = s.p, h = s.heli, m = muzzle(h), L = s.L, cands = [], i;
    function consider(x, y, w) {
      var dx = x - m.x, dy = y - m.y, d = Math.sqrt(dx * dx + dy * dy);
      if (d < 6 || d > F.GUN_RANGE) return;
      var a = Math.atan2(dy, dx);
      if (a < -F.GUN_UP || a > F.GUN_BACK) return;
      if (blocked(L, m.x, m.y, x, y)) return;
      cands.push({ a: a, x: x, y: y, d: d, w: d * w });
    }
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.ext !== 'fly' || e.st === 'panic' || e.emerge > 0 || !inView(s, e.x, e.y - e.h / 2, -4)) continue;
      // (a missile man down behind his parapet: only his head shows, and the gun takes him last; locking on, not even that)
      if (e.k === 'sam' && e.covered) { if (!e.hidden) consider(e.x, e.y - 10, 2.5); continue; }
      consider(e.x, e.y - e.h * 0.55, e.k === 'drone' ? 0.6 : 1);
    }
    // (not the missiles: shots do not stop them. That is what the flares are for)
    var manual = flying && !!inp.gun && (inp.gx || inp.gy), want, best = null, pull;
    if (manual) {
      // where the stick points, and if something worth shooting lies close to that line, at it
      var aimA = reach(Math.atan2(inp.gy, inp.gx)), bd = 1e9;
      for (i = 0; i < cands.length; i++) { var off = Math.abs(cands[i].a - aimA); if (off < F.AIM_ASSIST && off * 400 + cands[i].d < bd) { bd = off * 400 + cands[i].d; best = cands[i]; } }
      want = best ? best.a : aimA;
      pull = true;
    } else {
      for (i = 0; i < cands.length; i++) if (!best || cands[i].w < best.w) best = cands[i];
      want = best ? best.a : clamp(h.tilt + 0.3, -0.1, 0.6);
      pull = flying && (fire || (!!inp.auto && !!best));
    }
    h.target = best; h.aiming = !!manual;
    h.gunA += clamp(want - h.gunA, -(manual ? F.AIM_SLEW : F.GUN_SLEW), manual ? F.AIM_SLEW : F.GUN_SLEW);
    if (!pull || p.fireCd > 0) return;
    var a = h.gunA + (s.rand() - 0.5) * 2 * F.GUN_SPREAD, dx = Math.cos(a), dy = Math.sin(a);
    s.bullets.push({ x: m.x + dx * 8, y: m.y + dy * 8, vx: dx * F.GUN_V + h.vx * 0.5, vy: dy * F.GUN_V + h.vy * 0.5, life: F.GUN_LIFE, own: true, hmg: true, hedp: true, age: 0, free: 0, hide: 1 });
    p.fireCd = F.GUN_CD; p.fireT = 0;
    s.stats.shots++;
    ev(s, { t: 'shot', w: 'chin', x: m.x + dx * 12, y: m.y + dy * 12, dx: dx, dy: dy, face: 1, aim: 'chin' });
  }
  // the rocket pod's seeker: it locks on by itself to what is most worth a rocket ahead of the nose (above it, below it, not
  // behind), the aim stick saying which when it points near one; a short run of beeps as the marker closes on it, then the
  // locked tone. It keeps what it has unless something clearly better comes along.
  function podLock(s, inp, flying) {
    var h = s.heli, p = s.p, L = s.L, pod = bodyAt(h, F.POD_AT), best = null, bw = 1e9, i;
    var aimA = flying && inp.gun && (inp.gx || inp.gy) ? Math.atan2(inp.gy, inp.gx) : null;
    if (flying && p.grenades > 0) for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.ext !== 'fly' || e.st === 'panic' || e.emerge > 0 || e.hidden || e.smokeT > 0) continue;
      var tx = e.x, ty = e.y - e.h * 0.5;
      if (!inView(s, tx, ty, -4)) continue;
      var dx = tx - pod.x, dy = ty - pod.y, d = Math.sqrt(dx * dx + dy * dy), a = Math.atan2(dy, dx);
      if (d < 30 || d > F.RLOCK_RANGE || Math.abs(a) > 1.75 || blocked(L, pod.x, pod.y, tx, ty)) continue;
      var w = d / (WORTH[e.k] || 1.2) / (e.k === 'sam' && e.covered ? 0.6 : 1) + (HARD[e.k] ? 0 : 1e5);
      if (aimA !== null) { var off = a - aimA; while (off > Math.PI) off -= 2 * Math.PI; while (off < -Math.PI) off += 2 * Math.PI; w *= 1 + Math.abs(off) * 3; }
      if (e.id === h.rlock) w *= 0.7;
      if (w < bw) { bw = w; best = e; }
    }
    if (!best) { if (h.rlock) ev(s, { t: 'rlock_off' }); h.rlock = 0; h.rlockT = 0; return; }
    if (best.id !== h.rlock) { h.rlock = best.id; h.rlockT = 0; }
    var bi = F.RLOCK_BEEPS.indexOf(h.rlockT);
    if (bi >= 0) ev(s, { t: 'rlock', n: bi, x: best.x, y: best.y - best.h * 0.5 });
    if (h.rlockT === F.RLOCK_T) ev(s, { t: 'rlocked', x: best.x, y: best.y - best.h * 0.5, id: best.id });
    if (h.rlockT <= F.RLOCK_T) h.rlockT++;
  }
  function rocketOut(s) {
    var p = s.p, h = s.heli, dx = Math.cos(h.tilt), dy = Math.sin(h.tilt) + 0.04;
    h.side = 1 - h.side;
    var pod = bodyAt(h, F.POD_AT), y = pod.y - 1 + h.side * 2, tgt = h.rlock && h.rlockT > F.RLOCK_T ? h.rlock : 0;
    s.rockets.push({ x: pod.x, y: y, vx: Math.max(0, h.vx) + dx * F.ROCKET_V, vy: h.vy * 0.4 + dy * F.ROCKET_V, dx: dx, dy: dy, t: 0, gone: false, tgt: tgt });
    p.grenades--; h.rocketCd = F.ROCKET_CD; p.throwT = 0;
    s.stats.grenades++;
    ev(s, { t: 'rocket', x: pod.x + 4, y: y, face: 1, guided: !!tgt });
  }
  // flares: three, thrown back and out; every missile in the air goes after them
  function flaresOut(s) {
    var h = s.heli, first = s.flares.length;
    h.flareCd = F.FLARE_CD;
    for (var k = 0; k < F.FLARE_N; k++) {
      var tl = bodyAt(h, F.TAIL_AT);
      s.flares.push({ x: tl.x, y: tl.y, vx: -(40 + k * 34) + h.vx * 0.3, vy: -60 + k * 50, t: 0, gone: false });
    }
    ev(s, { t: 'flare', x: h.x, y: h.y });
    for (var i = 0; i < s.missiles.length; i++) {
      var q = s.missiles[i];
      if (q.gone || q.decoy || q.kind === 'rpg' || q.kind === 'icbm' || q.kind === 'dud') continue;
      q.decoy = true; q.fl = first + (i % F.FLARE_N);
      ev(s, { t: 'decoyed', x: q.x, y: q.y });
    }
  }
  // a flare still burning, for a missile just launched to go after (the one most recently thrown)
  function liveFlare(s) {
    for (var i = s.flares.length - 1; i >= 0; i--) if (!s.flares[i].gone) return i;
    return null;
  }

  // ------------------------------------------------------------------ the Zanabeel
  function heliOK(s) { return s.heli && !s.p.dead && s.heli.st === 'fly' && s.status === 'play'; }
  // he has seen enough: hands up, and away from it (no longer anyone's target, and worth a little)
  function scatter(s, e) {
    var h = s.heli;
    e.st = 'panic'; e.stT = 0; e.face = h && h.x > e.x ? -1 : 1; e.lit = false;
    if (s.locking === e.id) s.locking = 0;
    I.standDown(s, e);
    s.scattered++; s.score += 100;
    ev(s, { t: 'scatter', x: e.x, y: e.y, id: e.id, k: e.k, pts: 100 });
  }
  function man(s, e) {
    var h = s.heli, p = s.p, G = I.groupOf(s, e), L = s.L;
    e.seen = inView(s, e.x, e.y - e.h / 2, 0);
    // (the last of a group thinking it over, as on foot: from the air there is nobody to give himself up to, so a man runs
    // for it, and a gun or a drone simply carries on where it was; so does a missile man in the middle of his lock-on)
    if (e.st === 'shock') {
      if (e.k === 'rifle' || (e.k === 'sam' && s.locking !== e.id)) { scatter(s, e); return; }
      e.st = e.was || 'wait'; e.stT = e.wasT || 0;
    }
    e.was = e.st; e.wasT = e.stT;
    if (e.intro) { introMan(s, e); return; }
    if (e.k === 'drone') { drone(s, e); return; }
    if (e.emerge > 0) { e.emerge--; if (h && e.st !== 'out') e.face = h.x >= e.x ? 1 : -1; return; }
    if (e.st === 'out') {
      // along to his post (shot at on the way, and not yet shooting)
      var dxo = e.goX - e.x, so = F.WALK_V * DT;
      if (Math.abs(dxo) <= so) { e.x = e.goX; e.st = 'wait'; e.stT = 0; e.moving = 0; e.cd = Math.round((10 + Math.floor(s.rand() * 24)) * T.FIRST); }
      else { e.face = dxo > 0 ? 1 : -1; e.moving = e.face; e.x += e.face * so; e.walkD += so; }
      var ty0 = standY(L, e, e.x);
      e.y += clamp(ty0 - e.y, -1.5, 1.5);
      if (e.st === 'wait') e.y = ty0;
      return;
    }
    if (e.k === 'crate') { crate(s, e, G); return; }
    if (e.k === 'truck') { truck(s, e, G); return; }
    if (e.k === 'cgun') { castleGun(s, e, G); return; }
    if (e.k === 'launcher') { launcher(s, e, G); return; }
    if (e.k === 'light') { light(s, e, G); return; }
    if (e.st === 'panic') { flee(s, e); return; }
    // (a man at his post acts once he is in the picture, without waiting for his fight to wake: the chin gun was killing
    // most of them before it did; 23 Oct)
    if (!e.seen || (!G.awake && !e.post)) return;
    var dx = h.x - e.x, dy = h.y - e.y, d = Math.sqrt(dx * dx + dy * dy);
    if (e.k !== 'aa') e.face = dx >= 0 ? 1 : -1;
    // the first of them to see it says what it is: «قنية سودا!», the black jinn (and if he is not one of the brave ones, he
    // is off before he has finished saying it)
    if (!G.screamed && heliOK(s) && d < F.SIGHT + 40 && staged(s, e.x, e.y - e.h / 2)) {
      G.screamed = true;
      if (s.tick - s.screamT > F.SCREAM_GAP) {
        s.screamT = s.tick;
        ev(s, { t: 'qanya', x: e.x, y: e.y - e.h, id: e.id, k: e.k });
        if (!e.brave && e.k === 'rifle') { scatter(s, e); return; }
      }
    }
    // at night the searchlight finds him; a man who is not one of the brave ones throws his hands up and runs
    if (!e.brave && heliOK(s) && dark(L, s.u) > 0.5 && inBeam(s, e.x, e.y - 16)) {
      if (++e.beamT >= F.PANIC_T) { scatter(s, e); return; }
    } else if (e.beamT > 0) e.beamT--;
    if (!heliOK(s)) { if (e.st !== 'wait') { e.st = e.k === 'sniper' ? 'hide' : 'wait'; e.stT = 0; if (s.locking === e.id) s.locking = 0; } if (e.k === 'sniper') e.hidden = true; return; }
    var shown = staged(s, e.x, e.y - e.h / 2);
    // (a searchlight has the Apache: they all know where it is, and are quicker about it)
    if (s.spotT > 0 && e.cd > 0 && e.st !== 'hide') e.cd--;
    if (e.k === 'rifle') {
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < F.SIGHT && !blocked(L, e.x, e.y - 26, h.x, h.y)) { e.st = 'aim'; e.stT = 0; }
      } else if (e.st === 'aim') {
        if (e.stT >= 24) { e.st = 'burst'; e.stT = 0; e.shots = 0; e.first = false; }
      } else if (e.st === 'burst') {
        if (e.stT % 8 === 1) {
          var mx = e.x + e.face * 14, my = e.y - 26, tx = h.x - mx, ty = h.y - my, tl = Math.sqrt(tx * tx + ty * ty) || 1, sp = (s.rand() - 0.5) * 0.08;
          var ux = tx / tl, uy = ty / tl, cs = Math.cos(sp), sn = Math.sin(sp);
          s.bullets.push({ x: mx, y: my, vx: (ux * cs - uy * sn) * F.RIFLE_V, vy: (ux * sn + uy * cs) * F.RIFLE_V, life: 200, own: false, chip: true, src: 'rifle' });
          ev(s, { t: 'eshot', k: 'rifle', x: mx, y: my, face: e.face });
          if (++e.shots >= 3) { e.st = 'cool'; e.stT = 0; e.cd = Math.round((50 + Math.floor(s.rand() * 50)) * T.GAP); }
        }
      } else if (e.st === 'cool') { if (e.stT > 14) { e.st = 'wait'; e.stT = 0; } }
    } else if (e.k === 'aa') {
      // the barrels follow it; a burst once they have it, aimed where it is going
      // (the barrels go no lower than level: with the Apache below the gun, it can only wait for it to come up)
      var lead = d / F.AA_V, ax0 = e.x, ay0 = e.y - 16, txa = h.x + h.vx * lead * 0.7 - ax0, tya = h.y + h.vy * lead * 0.7 - ay0;
      var raw = Math.atan2(tya, txa), want = clamp(raw, -Math.PI + 0.12, -0.12), aimed = tya < -8 && Math.abs(raw - e.bar) < F.AA_AIMED;
      e.bar += clamp(want - e.bar, -0.05, 0.05);
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < F.AA_RANGE && tya < -8 && !blocked(L, ax0, ay0 - 6, h.x, h.y)) { e.st = 'aim'; e.stT = 0; ev(s, { t: 'tell', k: 'aa', x: e.x, y: e.y - e.h }); }
      } else if (e.st === 'aim') {
        if (e.stT >= F.AA_TELL && aimed) { e.st = 'burst'; e.stT = 0; e.shots = 0; }
        else if (e.stT > F.AA_TELL * 3) { e.st = 'wait'; e.stT = 0; e.cd = 40; }
      } else if (e.st === 'burst') {
        if (e.stT % F.AA_EVERY === 1) {
          var bx = ax0 + Math.cos(e.bar) * 16, by = ay0 + Math.sin(e.bar) * 16;
          s.bullets.push({ x: bx, y: by, vx: Math.cos(e.bar) * F.AA_V, vy: Math.sin(e.bar) * F.AA_V, life: 140, own: false, heavy: true, src: 'anti-aircraft gun' });
          ev(s, { t: 'eshot', k: 'aa', x: bx, y: by, ang: e.bar });
          if (++e.shots >= F.AA_SHOTS) { e.st = 'cool'; e.stT = 0; e.cd = Math.round((F.AA_COOL + Math.floor(s.rand() * 40)) * T.GAP); }
        }
      } else if (e.st === 'cool') { if (e.stT > 10) { e.st = 'wait'; e.stT = 0; } }
    } else if (e.k === 'sam') {
      // the man with a missile. Down behind his parapet only his head shows (the gun takes him last); he locks on from right
      // down out of sight (nothing but a rocket's blast reaches him then): a beat that quickens; then up with the launcher on
      // his shoulder for the last of it (one long tone), and it goes, after the flares if any are burning. He stays up a
      // moment after it, then down to reload.
      e.covered = e.st !== 'aim' && e.st !== 'fired';
      e.hidden = e.st === 'lock';                                   // (right down while he locks on: shots go over him; a rocket's blast does not)
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < F.SAM_RANGE && !s.locking && !blocked(L, e.x, e.y - 30, h.x, h.y)) { e.st = 'lock'; e.stT = 0; e.lk = 0; s.locking = e.id; s.lockT = 0; ev(s, { t: 'lock_on', x: e.x, y: e.y - 30, id: e.id }); }
      } else if (e.st === 'lock' || e.st === 'aim') {
        s.lockT = e.lk;
        var bi = F.BEATS.indexOf(e.lk);
        if (bi >= 0) ev(s, { t: 'lock', n: bi, of: F.BEATS.length, x: e.x, y: e.y });
        if (e.lk === F.SAM_LOCK - F.SAM_SOLID) { e.st = 'aim'; e.stT = 0; ev(s, { t: 'lock', n: F.BEATS.length, of: F.BEATS.length, solid: true, x: e.x, y: e.y }); }
        if (e.lk >= F.SAM_LOCK) {
          var a0 = Math.atan2(h.y - (e.y - 32), h.x - e.x), fl = liveFlare(s);
          s.missiles.push({ x: e.x + Math.cos(a0) * 10, y: e.y - 32 + Math.sin(a0) * 10, ang: a0, v: 60, t: 0, gone: false, decoy: fl !== null, fl: fl, from: e.id });
          ev(s, { t: 'sam_launch', x: e.x, y: e.y - 32, decoy: fl !== null });
          e.st = 'fired'; e.stT = 0; s.locking = 0; s.lockT = 0;
        }
        e.lk++;
      } else if (e.st === 'fired') { if (e.stT > F.SAM_UP) { e.st = 'cool'; e.stT = 0; e.cd = Math.round((F.SAM_RELOAD + Math.floor(s.rand() * 60)) * T.GAP); } }
      else if (e.st === 'cool') { if (e.stT > 30) { e.st = 'wait'; e.stT = 0; } }
    } else if (e.k === 'rpg') {
      // the RPG: down on one knee with it on his shoulder (the tell), then it goes, straight at where the Apache was. A
      // rocket-propelled grenade can be shot down.
      var rx = e.x + e.face * 8, ry = e.y - 26;
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < F.RPG_RANGE && !blocked(L, rx, ry, h.x, h.y)) { e.st = 'aim'; e.stT = 0; ev(s, { t: 'tell', k: 'rpg', x: e.x, y: e.y - e.h }); }
      } else if (e.st === 'aim') {
        e.aimA = Math.atan2(h.y - ry, h.x - rx);
        if (e.stT >= F.RPG_AIM) {
          s.missiles.push({ kind: 'rpg', x: rx + Math.cos(e.aimA) * 8, y: ry + Math.sin(e.aimA) * 8, ang: e.aimA, v: F.RPG_V, t: 0, gone: false, decoy: false, from: e.id });
          ev(s, { t: 'rpg_fire', x: rx, y: ry, face: e.face });
          e.st = 'cool'; e.stT = 0; e.cd = Math.round((F.RPG_COOL + Math.floor(s.rand() * 70)) * T.GAP);
        }
      } else if (e.st === 'cool') { if (e.stT > 24) { e.st = 'wait'; e.stT = 0; } }
    } else if (e.k === 'sniper') {
      // a sniper in a window: in the dark of the room (nothing to shoot at), then at the window with his laser on the
      // Apache for a second (shoot him then), then one round, and back into the dark
      if (e.st === 'wait') { e.st = 'hide'; e.stT = 0; }                 // (put back after the Apache went down: back in the dark)
      e.hidden = e.st === 'hide';
      var sx0 = e.x, sy0 = e.y - 10;
      if (e.st === 'hide') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < F.SNIPE_RANGE && !blocked(L, sx0, sy0, h.x, h.y)) { e.st = 'aim'; e.stT = 0; ev(s, { t: 'snipe_aim', x: sx0, y: sy0 }); }
      } else if (e.st === 'aim') {
        e.lx = h.x; e.ly = h.y;
        if (e.stT >= F.SNIPE_AIM) {
          var ta = Math.atan2(h.y - sy0, h.x - sx0);
          s.bullets.push({ x: sx0 + Math.cos(ta) * 6, y: sy0 + Math.sin(ta) * 6, vx: Math.cos(ta) * F.SNIPE_V, vy: Math.sin(ta) * F.SNIPE_V, life: 90, own: false, heavy: true, src: 'sniper' });
          ev(s, { t: 'eshot', k: 'sniper', x: sx0, y: sy0, ang: ta });
          e.st = 'shot'; e.stT = 0;
        }
      } else if (e.st === 'shot') { if (e.stT > 16) { e.st = 'hide'; e.stT = 0; e.cd = Math.round((F.SNIPE_COOL + Math.floor(s.rand() * 90)) * T.GAP); } }
    } else if (e.k === 'mortar') {
      // a mortar: a shell dropped down the tube, and up it goes; where it will burst is marked (where the Apache was, and a
      // little ahead of it) until it does
      if (e.st === 'wait') {
        if (e.cd > 0) e.cd--;
        else if (shown && d < 520) { e.st = 'load'; e.stT = 0; ev(s, { t: 'mortar_load', x: e.x, y: e.y }); }
      } else if (e.st === 'load') {
        if (e.stT >= F.MORTAR_LOAD) {
          var tx2 = clamp(h.x + h.vx * 0.35, s.cam + 40, s.cam + s.viewW - 40), ty2 = clamp(h.y + h.vy * 0.2, s.camY + 30, s.camY + VH(s) - 30);
          s.shells.push({ x: e.x + e.face * 3, y: e.y - 16, tx: tx2, ty: ty2, t: 0, gone: false, from: e.id });
          ev(s, { t: 'mortar_fire', x: e.x, y: e.y - 16, tx: tx2, ty: ty2 });
          e.st = 'cool'; e.stT = 0; e.cd = Math.round((F.MORTAR_COOL + Math.floor(s.rand() * 70)) * T.GAP);
        }
      } else if (e.st === 'cool') { if (e.stT > 20) { e.st = 'wait'; e.stT = 0; } }
    }
  }
  // ------------------------------------------------------------------ the bosses
  // a boss's fight starts when the camera is held at its fight (its men may be awake before that)
  function atFight(s, e) { return !!s.gateNow && s.gateNow.groups.indexOf(e.g) >= 0 && s.u >= s.holdU - 4 && s.groups[e.g].awake; }
  // the boss's bar in the HUD (render.js draws s.boss's)
  function bossBar(s, e, label) {
    var K = Sim.KIND[e.k];
    s.boss = { kind: e.k, label: label, hp: Math.max(0, e.hp), full: K.hp, phase: e.phase, hurtT: e.hurtT, st: e.alive ? 'fight' : 'dead', x: e.x, y: e.y };
  }
  function phaseOf(e, K) { return e.hp > K.hp * 0.66 ? 1 : (e.hp > K.hp * 0.33 ? 2 : 3); }
  // THE CASTLE GUN: a great twin gun the Zanabeel have hauled up onto the bastion, under a tarp until the Apache comes. It
  // turns after it (slowly); it fires flak (a shell that bursts where the Apache was: the place is marked), and sweeps the
  // sky with its heavy rounds (from the far side towards the Apache, after a warning, never low: under its lowest round,
  // beside the bastion, is out of it); then its barrels are too hot to fire for a while. Hurt, its shield comes off and it
  // is quicker, and its crew sends up drones; at the last it fires flak all round the Apache at once, but for one side.
  function castleGun(s, e, G) {
    var h = s.heli, ok = heliOK(s), K = Sim.KIND.cgun, mx, my;
    if (e.st === 'cover') { e.hidden = true; e.hp = K.hp; if (atFight(s, e)) { e.st = 'rise'; e.stT = 0; ev(s, { t: 'boss_intro', k: 'cgun', x: e.x, y: e.y }); } return; }
    bossBar(s, e, 'CASTLE GUN');
    if (e.st === 'rise') { e.rise = Math.min(1, e.stT / BG.CG_RISE); if (e.stT >= BG.CG_RISE + 10) { e.st = 'track'; e.stT = 0; e.hidden = false; } return; }
    var ph = phaseOf(e, K);
    if (ph !== e.phase) { e.phase = ph; e.plan = []; ev(s, { t: 'boss_phase', k: 'cgun', n: ph, x: e.x, y: e.y - 20 }); }
    // the barrels: from the trunnion, turning after the Apache, no lower than level either way
    var px = e.x, py = e.y - 24, want = ok ? clamp(Math.atan2(h.y - py, h.x - px), -Math.PI + 0.15, -0.15) : -Math.PI / 2;
    if (e.st !== 'sweep' && e.st !== 'cool') e.bar += clamp(angDiff(want, e.bar), -0.03 - 0.01 * e.phase, 0.03 + 0.01 * e.phase);
    mx = px + Math.cos(e.bar) * 30; my = py + Math.sin(e.bar) * 30;
    if (e.st === 'cool') {
      // too hot to fire: the barrels up and steaming until they cool (whatever else is going on)
      e.bar += clamp(angDiff(-Math.PI / 2, e.bar), -0.02, 0.02);
      if (e.stT >= BG.CG_COOL) { e.st = 'track'; e.stT = 0; ev(s, { t: 'cooled', x: mx, y: my }); }
      return;
    }
    if (!ok) { if (e.st !== 'track') { e.st = 'track'; e.stT = 0; } return; }
    if (e.st === 'track') {
      if (e.stT >= BG.CG_TRACK[e.phase]) {
        if (!e.plan.length) e.plan = e.phase === 1 ? ['flak', 'flak', 'sweep'] : (e.phase === 2 ? ['flak', 'flak', 'call', 'flak', 'sweep'] : ['barrage', 'sweep', 'flak']);
        e.st = e.plan.shift(); e.stT = 0; e.shots = 0;
        // (from the far side, towards the Apache: it is seen coming)
        if (e.st === 'sweep') { sweepPlan(e, h); ev(s, { t: 'tell', k: 'cgun', x: mx, y: my }); }
      }
    } else if (e.st === 'flak') {
      // (where the Apache is now, not where it is going: flying on is enough, if it sees the mark in time)
      if (e.stT === 1) flak(s, e, mx, my, h.x, h.y);
      if (e.stT >= 22) { e.st = 'track'; e.stT = 0; }
    } else if (e.st === 'barrage') {
      // five at once: on the Apache, above and below it, and to one side of it; the other side, towards the middle of the
      // picture, is clear
      if (e.stT === 1) {
        var side = h.x > s.cam + s.viewW / 2 ? 1 : -1, k, offs = [[0, 0], [side * 64, -34], [side * 64, 34], [0, -64], [0, 64]];
        for (k = 0; k < offs.length; k++) flak(s, e, mx, my, h.x + offs[k][0], h.y + offs[k][1], k ? 2 : 0, BG.CG_BARRAGE_FUSE);
      }
      if (e.stT >= 40) { e.st = 'track'; e.stT = 0; }
    } else if (e.st === 'sweep') {
      // the warning: the barrels swing over to the far side (and glow); then across the sky, firing as they go, never low
      if (e.stT <= BG.CG_SWEEP_TELL) e.bar += clamp(angDiff(e.sweepFrom, e.bar), -0.12, 0.12);
      else {
        if (e.stT === BG.CG_SWEEP_TELL + 1) e.bar = e.sweepFrom;
        else e.bar += (e.sweepTo - e.sweepFrom) / ((BG.CG_SWEEP_N - 1) * BG.CG_SWEEP_EVERY);
        if ((e.stT - BG.CG_SWEEP_TELL) % BG.CG_SWEEP_EVERY === 1) {
          for (var t2 = -1; t2 <= 1; t2 += 2) {
            var bx = mx - Math.sin(e.bar) * t2 * 3, by = my + Math.cos(e.bar) * t2 * 3;
            s.bullets.push({ x: bx, y: by, vx: Math.cos(e.bar) * BG.CG_HEAVY_V, vy: Math.sin(e.bar) * BG.CG_HEAVY_V, life: 150, own: false, heavy: true, src: 'castle gun' });
          }
          ev(s, { t: 'eshot', k: 'aa', x: mx, y: my, ang: e.bar });
          if (++e.shots >= BG.CG_SWEEP_N) { e.st = 'cool'; e.stT = 0; ev(s, { t: 'overheat', x: mx, y: my }); }
        }
      }
    } else if (e.st === 'call') {
      // the crew sends up two drones from behind the gun
      if (e.stT === 10) for (var d = 0; d < 2; d++) { var dr = droneOut(s, e.g, d, 2); dr.x = e.x + (d ? 26 : -26); dr.y = e.y - 10; dr.wait = 10 + d * 20; dr.from = e.id; ev(s, { t: 'drone_up', x: dr.x, y: dr.y }); }
      if (e.stT >= 30) { e.st = 'track'; e.stT = 0; }
    }
  }
  // a sweep's plan: from low on the far side of the gun (away from the Apache) up to a little past straight up, and no
  // further (the Apache's side of the sky is clear)
  function sweepPlan(e, h) {
    var left = h.x < e.x;           // (the Apache on the left: the sweep starts low on the right and comes up over the top)
    e.sweepDir = left ? -1 : 1;
    e.sweepFrom = left ? -BG.CG_LOW : -Math.PI + BG.CG_LOW;
    e.sweepTo = left ? -Math.PI / 2 - BG.CG_OVER : -Math.PI / 2 + BG.CG_OVER;
  }
  // a flak shell, out of the barrels and bursting at the marked place (wait: ticks before it goes)
  function flak(s, e, mx, my, tx, ty, wait, minFuse) {
    tx = clamp(tx, s.cam + 30, s.cam + s.viewW - 30); ty = clamp(ty, s.camY + 26, s.camY + VH(s) - 30);
    var d = Math.sqrt((tx - mx) * (tx - mx) + (ty - my) * (ty - my));
    s.shells.push({ kind: 'flak', x: mx, y: my, sx: mx, sy: my, tx: tx, ty: ty, t: -(wait || 0), fuse: Math.max(minFuse || BG.CG_FLAK_MIN, Math.round(d / BG.CG_FLAK_V * 60) + 18), gone: false, from: e.id });
    if (!wait) ev(s, { t: 'flak', x: mx, y: my, tx: tx, ty: ty });
  }
  // THE LAUNCHER: the Zanabeel's pride, kept in the keep: a great eight-wheeled missile truck, its missile for friendly
  // territory, not for the Apache (Khaled, 22 Oct, playing the first cut, where it fired at the Apache: "doesn't make sense
  // ... maybe the last one could be a timed boss where I need to kill it before it launches a missile into friendly
  // territories"). When the Apache comes the keep's gate opens, it rolls out into the courtyard, its jacks go down and the
  // count to the launch starts, the missile rising as it runs (the count waits while the Apache is down). With 15 seconds
  // left the crew lose count, argue, and start again from further back (Khaled's pick, 22 Oct). At nought the engine
  // lights: a few seconds more to finish it on its rail; then the missile goes, and the mission is lost (Continue starts
  // the fight again, from the keep). The man on the cab has a machine gun; the crew puts up smoke when the rocket pod locks
  // on to it (the lock is lost in it). Rockets hit it three times as hard. Destroyed, it goes up in a run of bangs, its
  // missile cooking off into the sky, and burns down to nothing, leaving the courtyard for the landing.
  function lnNose(e) {
    var a = Math.PI + e.raise * BG.LN_MAX, px = e.x + BG.LN_PIVOT[0], py = e.y + BG.LN_PIVOT[1];
    return { x: px + Math.cos(a) * BG.LN_LEN, y: py + Math.sin(a) * BG.LN_LEN, a: a, px: px, py: py };
  }
  Sim.lnNose = lnNose;
  Sim.cgSweepPlan = sweepPlan;
  function launcher(s, e, G) {
    var h = s.heli, ok = heliOK(s), K = Sim.KIND.launcher, n;
    if (e.st === 'hide') { e.hidden = true; e.hp = K.hp; if (atFight(s, e)) { e.st = 'open'; e.stT = 0; ev(s, { t: 'boss_intro', k: 'launcher', x: e.stopX, y: e.y }); } return; }
    bossBar(s, e, 'LAUNCHER');
    if (e.st === 'open') {
      e.door = Math.min(1, e.stT / BG.LN_OPEN);
      if (e.stT >= BG.LN_OPEN) { e.st = 'roll'; e.stT = 0; e.hidden = false; ev(s, { t: 'roll', x: e.x, y: e.y }); }
      return;
    }
    var ph = phaseOf(e, K);
    if (ph !== e.phase) { e.phase = ph; ev(s, { t: 'boss_phase', k: 'launcher', n: ph, x: e.x, y: e.y - 30 }); }
    if (e.st === 'roll') {
      var nx0 = Math.max(e.stopX, e.x - BG.LN_ROLL_V * DT);
      e.wheel += e.x - nx0; e.x = nx0;
      if (e.x <= e.stopX) { e.st = 'count'; e.stT = 0; e.clock = BG.LN_CLOCK; e.argue = 0; e.lastSec = 0; ev(s, { t: 'countdown', x: e.x, y: e.y - 40, secs: BG.LN_CLOCK / 60 }); }
    }
    s.boss.clock = e.st === 'count' || e.st === 'ignite' ? Math.max(0, e.clock) : null; s.boss.argue = e.argue > 0; s.boss.ign = e.st === 'ignite';
    if (e.smokeT > 0) e.smokeT--;
    if (e.smokeCd > 0) e.smokeCd--;
    if (e.ramT > 0) e.ramT--;
    if (e.st === 'spent') return;           // (the missile is away: nothing more to do here)
    if (ok) {
      // (flown into: it is a truck)
      var hb = heliBox(h);
      if (!e.ramT && hb.x1 > e.x - K.hw && hb.x0 < e.x + K.hw && hb.y1 > e.y - K.h && hb.y0 < e.y) { e.ramT = 60; I.hurtPlayer(s, e.x, 'launcher'); }
      // the crew's smoke, the moment the rocket pod has it: the lock is lost in it
      if (h.rlock === e.id && h.rlockT > 4 && e.smokeCd <= 0 && e.st !== 'roll') { e.smokeT = BG.LN_SMOKE_T; e.smokeCd = BG.LN_SMOKE_CD[e.phase]; ev(s, { t: 'smoke', x: e.x, y: e.y - 20 }); }
      lnGun(s, e);
    }
    if (e.st === 'count') {
      if (e.argue > 0) {
        // the crew have lost count: the clock stands while they argue, then goes back
        if (--e.argue === 0) { e.clock += BG.LN_RECOUNT_ADD; ev(s, { t: 'recount', add: BG.LN_RECOUNT_ADD / 60, x: e.x - 40, y: e.y - 50 }); }
      } else if (ok) e.clock--;
      e.raise = Math.max(e.raise, clamp(1 - (e.clock - BG.LN_UP_AT) / (BG.LN_CLOCK - BG.LN_UP_AT), 0, 1));
      if (!e.recounted && e.clock <= BG.LN_RECOUNT_AT) { e.recounted = true; e.argue = BG.LN_ARGUE; ev(s, { t: 'lost_count', x: e.x - 40, y: e.y - 50 }); }
      var sec = Math.ceil(e.clock / 60);
      if (sec !== e.lastSec) { e.lastSec = sec; if (sec <= 10 && !e.argue) ev(s, { t: 'count_tick', n: sec, x: e.x, y: e.y }); }
      if (e.clock <= 0) { e.st = 'ignite'; e.stT = 0; n = lnNose(e); ev(s, { t: 'ignite', x: n.px, y: n.py }); }
    } else if (e.st === 'ignite') {
      // nought: the engine lights and burns on the rail for a moment (the last chance); then away it goes
      if (e.stT >= BG.LN_IGNITE) {
        n = lnNose(e);
        s.missiles.push({ kind: 'icbm', x: n.x, y: n.y, ang: n.a, v: 40, t: 0, gone: false, decoy: true, from: e.id });
        e.missile = false; e.st = 'spent'; e.stT = 0;
        ev(s, { t: 'big_launch', x: n.x, y: n.y, ang: n.a, away: true });
        if (!s.lost) s.lost = { t: 0, why: 'launch' };
        ev(s, { t: 'got_away', x: n.x, y: n.y });
      }
    }
  }
  // the man on the cab with the machine gun: a moment to swing round, then a burst at the Apache
  function lnGun(s, e) {
    var h = s.heli, gx = e.x + BG.LN_MG_AT[0], gy = e.y + BG.LN_MG_AT[1], dx = h.x - gx, dy = h.y - gy;
    e.gunA = Math.atan2(dy, dx);
    if (e.st === 'roll') return;
    if (e.mgst === 'wait') { if (--e.mgcd <= 0 && Math.abs(dx) < 520) { e.mgst = 'tell'; e.mgT = 0; ev(s, { t: 'tell', k: 'truck', x: gx, y: gy - 24 }); } }
    else if (e.mgst === 'tell') { if (++e.mgT >= 18) { e.mgst = 'burst'; e.mgT = 0; e.shots = 0; } }
    else if (e.mgst === 'burst') {
      if (e.mgT++ % 5 === 0) {
        var a = e.gunA + (s.rand() - 0.5) * 0.09;
        s.bullets.push({ x: gx + Math.cos(a) * 12, y: gy + Math.sin(a) * 12, vx: Math.cos(a) * BG.LN_MG_V, vy: Math.sin(a) * BG.LN_MG_V, life: 130, own: false, chip: true, src: 'launcher gun' });
        ev(s, { t: 'eshot', k: 'truck', x: gx, y: gy, ang: a });
        if (++e.shots >= BG.LN_MG_SHOTS) { e.mgst = 'wait'; e.mgcd = BG.LN_MG_EVERY[e.phase] + Math.floor(s.rand() * 30); }
      }
    }
  }
  // a man who has had enough (Khaled, 21 Oct 15:01: "surrendering enemies are still awkward, maybe make them run and jump off
  // buildings"): hands up and away from it as fast as he can go along his roof; at its edge, over he goes, arms up, down
  // onto whatever roof is under him (and on again) or out of the bottom of the picture; in the street, off out of it
  var FLEE_V = 112, FLEE_G = 760;
  function flee(s, e) {
    var L = s.L;
    if (e.air) {
      e.vy = Math.min(420, e.vy + FLEE_G * DT);
      var ox = e.x, oy = e.y;
      e.x += e.vx * DT; e.y += e.vy * DT; e.spin += e.face * 0.11;
      if (rockAt(L, e.x + e.face * 4, e.y - 14)) { e.x = ox; e.vx = 0; }            // (a wall in the way: down it, not through it)
      if (e.vy > 0) {
        var land = landingAt(L, e.x, oy, e.y);
        if (land) { e.air = false; e.y = land.y; e.plat = land.plat; e.vx = 0; e.vy = 0; e.spin = 0; e.turned = false; ev(s, { t: 'land_man', x: e.x, y: e.y, id: e.id }); return; }
      }
      if (e.y > s.camY + VH(s) + 50) fled(e);
      return;
    }
    e.moving = e.face;
    var nx = e.x + e.face * FLEE_V * DT, py = e.plat >= 0 ? Sim.platY(L.plats[e.plat], nx) : Sim.groundY(L, clamp(nx, 0, L.width));
    if (py === null) {
      // the edge of his roof: over it, if the way is clear. A wall there (a taller house, a tower): back the other way; and if
      // that is no better, in at a door (out of sight)
      if (rockAt(L, e.x + e.face * 22, e.y - 14)) { if (e.turned) { fled(e); return; } e.turned = true; e.face = -e.face; return; }
      e.air = true; e.vx = e.face * 96; e.vy = -170; e.spin = 0; e.plat = -1;
      ev(s, { t: 'leap', x: e.x, y: e.y, id: e.id });
      return;
    }
    if (e.plat < 0) {
      if (rockAt(L, nx + e.face * 6, e.y - 14)) { fled(e); return; }        // (in at a door in the wall he has come to)
      if (py > e.y + 6) { e.air = true; e.vx = e.face * FLEE_V; e.vy = 0; e.spin = 0; return; }   // (off a step)
    }
    e.x = nx; e.y = py; e.walkD += FLEE_V * DT;
    if (!inView(s, e.x, e.y - 18, 60)) fled(e);
  }
  // a roof (or the street) under a man falling from y0 to y1 at x
  function landingAt(L, x, y0, y1) {
    for (var i = 0; i < L.plats.length; i++) { var py = Sim.platY(L.plats[i], x); if (py !== null && py >= y0 - 0.5 && py <= y1 + 0.5) return { y: py, plat: i }; }
    var gy = Sim.groundY(L, clamp(x, 0, L.width));
    return gy >= y0 - 0.5 && gy <= y1 + 0.5 ? { y: gy, plat: -1 } : null;
  }
  function fled(e) { e.alive = false; e.st = 'gone'; e.deadT = 999; }
  function angDiff(a, b) { var d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }
  // a pickup with a gun in the back (Khaled, 05:38: "us chasing enemy pickups while they try shooting us"). Parked until its
  // fight wakes, then up the road ahead of the Apache, each keeping its own place in the picture, weaving; the gunner turns
  // round and fires back. At the end of the chase the ones that are left get away up the road.
  function truck(s, e, G) {
    var h = s.heli, L = s.L, ok = heliOK(s);
    e.rollV = e.vx;
    // parked with the engine running until the chase is on (the moment the fight before it is over): then away up the road
    if (e.st === 'park') { if (G.awake && s.chaseOn) { e.st = 'drive'; e.stT = 0; ev(s, { t: 'truck_go', x: e.x, y: e.y }); } return; }
    var run = s.chaseEnd || !s.chaseOn;           // (at the end of the road the ones left get away)
    var tx = run ? s.cam + s.viewW + 160 : s.cam + s.viewW * e.lead + Math.sin((s.tick + e.id * 47) / 46) * 26;
    e.vx += clamp((tx - e.x) * 2.2 - e.vx, -F.TRUCK_ACC * DT, F.TRUCK_ACC * DT);
    // (ahead of its place in the picture it eases off, but it never stops: they are running, and the Apache gains on them)
    e.vx = clamp(e.vx, run ? 0 : F.TRUCK_MIN * (s.chaseV || 60) * Math.min(1, e.stT / 30), F.TRUCK_V);
    e.x += e.vx * DT; e.wheel += e.vx * DT;
    e.y = groundAt(L, e.x); e.ang += (slopeAt(L, e.x) - e.ang) * 0.2;
    if (run && e.x > s.cam + s.viewW + 60) { I.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; ev(s, { t: 'truck_away', x: e.x, y: e.y }); return; }
    // the gunner
    var gx = e.x - 20, gy = e.y - 30, dx = h.x - gx, dy = h.y - gy, d = Math.sqrt(dx * dx + dy * dy);
    e.gT++;
    if (!ok) { e.gst = 'wait'; return; }
    if (e.gst === 'wait') {
      if (e.gcd > 0) e.gcd -= s.spotT > 0 ? 2 : 1;
      else if (d < F.TRUCK_RANGE && dy < 10 && staged(s, e.x, e.y - 20) && !blocked(L, gx, gy, h.x, h.y)) { e.gst = 'tell'; e.gT = 0; ev(s, { t: 'tell', k: 'truck', x: gx, y: gy - 30 }); }
    } else if (e.gst === 'tell') {
      if (e.gT >= F.TRUCK_TELL) { e.gst = 'burst'; e.gT = 0; e.shots = 0; }
    } else if (e.gst === 'burst') {
      if (e.gT % F.TRUCK_EVERY === 1) {
        var sp = (s.rand() - 0.5) * 0.1, a = Math.atan2(dy, dx) + sp;
        s.bullets.push({ x: gx + Math.cos(a) * 12, y: gy + Math.sin(a) * 12, vx: Math.cos(a) * 300, vy: Math.sin(a) * 300, life: 120, own: false, chip: true, src: 'pickup gun' });
        ev(s, { t: 'eshot', k: 'truck', x: gx, y: gy, ang: a });
        if (++e.shots >= F.TRUCK_SHOTS) { e.gst = 'cool'; e.gT = 0; e.gcd = Math.round((F.TRUCK_COOL + Math.floor(s.rand() * 40)) * T.GAP); }
      }
    } else if (e.gst === 'cool') { if (e.gT > 12) e.gst = 'wait'; }
    e.gunA = Math.atan2(dy, dx);
  }
  // a searchlight on a roof or a wall: its beam sweeps the sky; held on the Apache for a moment, it has it (and the guns
  // know where it is: they are all quicker while it does) until it gets out of the beam for a while
  function light(s, e, G) {
    var h = s.heli, L = s.L, ok = heliOK(s), bx = e.x, by = e.y - 16;
    if (!G.awake) return;
    var dh = h ? Math.sqrt((h.x - bx) * (h.x - bx) + (h.y - by) * (h.y - by)) : 1e9, ah = h ? Math.atan2(h.y - by, h.x - bx) : 0;
    var on = ok && e.seen && dh < F.LIGHT_LEN && Math.abs(angDiff(ah, e.beam)) < F.LIGHT_HALF + 0.03 && !blocked(L, bx, by, h.x, h.y);
    if (e.st !== 'track') {
      e.st = 'sweep';
      e.beam += e.dir * F.LIGHT_SWEEP;
      if (e.beam < -Math.PI + 0.4) { e.beam = -Math.PI + 0.4; e.dir = 1; }
      if (e.beam > -0.4) { e.beam = -0.4; e.dir = -1; }
      if (on) { if (++e.lk >= F.SPOT_T) { e.st = 'track'; e.stT = 0; e.lose = 0; ev(s, { t: 'spotted', x: bx, y: by }); } }
      else if (e.lk > 0) e.lk--;
    } else {
      // on it: the beam follows the Apache, a little behind it
      if (ok) e.beam += clamp(angDiff(ah, e.beam), -0.028, 0.028);
      s.spotT = 20;
      if (on) e.lose = 0; else if (++e.lose > F.SPOT_LOSE || !ok) { e.st = 'sweep'; e.lk = 0; e.dir = h && h.x > bx ? 1 : -1; ev(s, { t: 'unspotted', x: bx, y: by }); }
    }
  }
  // a crate of drones on a roof: when its fight is on and the Apache is about, its lid goes up and a drone rises out of
  // it; then the next, a while after (two in the air at most). Empty, it is no longer anything to worry about.
  function crate(s, e, G) {
    var ok = heliOK(s), up = 0, i;
    if (e.st === 'wait') {
      if (G.awake && e.seen && ok && e.left > 0) { e.st = 'open'; e.stT = e.oops && !e.oopsed ? F.CRATE_OPEN - 4 : 0; ev(s, { t: 'crate_open', x: e.x, y: e.y }); }      // (the one that goes wrong: at once)
    } else if (e.st === 'open') {
      if (e.stT >= F.CRATE_OPEN) {
        var d = droneOut(s, e.g, 0, 1);
        d.x = e.x; d.y = e.y - 8; d.wait = 12; d.from = e.id;
        d.off = ((e.left % 3) - 1) * 40;
        e.left--; e.st = e.left > 0 ? 'reload' : 'empty'; e.stT = 0;
        ev(s, { t: 'drone_up', x: e.x, y: e.y - 8 });
        if (e.oops && !e.oopsed) {
          // (Khaled's pick, 22 Oct: the first out of this one goes the wrong way, into one of its own crew)
          e.oopsed = true; d.st = 'oops'; d.stT = 0; d.tgt = 0; I.standDown(s, d);          // (no threat to the Apache: the gun leaves it be)
          var bd = 1e9;
          for (i = 0; i < s.enemies.length; i++) { var m2 = s.enemies[i]; if (m2.alive && m2.hostile && m2.k === 'rifle' && m2.st !== 'panic' && !(m2.emerge > 0)) { var dd = Math.abs(m2.x - e.x) + Math.abs(m2.y - e.y); if (dd < 240 && dd < bd) { bd = dd; d.tgt = m2.id; } } }
        }
        if (e.st === 'empty') I.standDown(s, e);
      }
    } else if (e.st === 'reload') {
      for (i = 0; i < s.enemies.length; i++) { var q = s.enemies[i]; if (q.alive && q.k === 'drone' && q.from === e.id) up++; }
      if (e.stT >= F.CRATE_GAP && up < 2 && ok) { e.st = 'open'; e.stT = 0; ev(s, { t: 'crate_open', x: e.x, y: e.y }); }
    }
    e.lid += clamp((e.st === 'open' || e.st === 'empty' ? 1 : 0) - e.lid, -0.12, 0.12);
  }
  function drone(s, e) {
    var h = s.heli, L = s.L, ok = heliOK(s);
    if (e.st === 'oops') {
      // up out of its crate as they all come, then off the wrong way and into one of its own (or, with nobody near, into
      // the roof): a puff, and him flung
      var tg = null, i2;
      for (i2 = 0; i2 < s.enemies.length; i2++) if (s.enemies[i2].id === e.tgt) tg = s.enemies[i2];
      if (e.stT < 10) { e.y -= 60 * DT; return; }
      if (e.stT < 34) { e.x += Math.sin(e.stT * 0.5) * 0.8; return; }             // (a moment wobbling about, lost)
      var ox = tg && tg.alive ? tg.x : e.x - 300, oy = tg && tg.alive ? tg.y - tg.h * 0.6 : e.y + 80;
      e.x += clamp(ox - e.x, -120 * DT, 120 * DT); e.y += clamp(oy - e.y, -100 * DT, 100 * DT);
      if (tg && tg.alive && Math.abs(tg.x - e.x) < 8 && Math.abs(oy - e.y) < 10) {
        ev(s, { t: 'oops', x: e.x, y: e.y }); I.hurtEnemy(s, tg, 99, e.x < tg.x ? 1 : -1, 'blast'); I.hurtEnemy(s, e, 99, 0, 'blast'); return;
      }
      if (e.stT > 150 || rockAt(L, e.x, e.y + 4)) { ev(s, { t: 'oops', x: e.x, y: e.y }); I.hurtEnemy(s, e, 99, 0, 'blast'); }
      return;
    }
    if (e.st === 'in' || e.st === 'hover') {
      // (it takes up station off the Apache's nose, level with its gun, or off its tail and below, for one that came from
      // behind: where the gun can reach it, which does not point up; in the middle of the picture, clear of the thumbs)
      var x0 = s.cam + s.viewW * s.laneL + 12, x1 = s.cam + s.viewW * (1 - s.laneR) - 12;
      var hx = clamp(h.x + e.off + (e.side || 1) * F.DRONE_OFF, x0, x1), hy = clamp(h.y + (e.side < 0 ? 50 : 10), s.camY + 24, s.camY + VH(s) - 40) + Math.sin((e.stT + e.id * 13) / 9) * 4;
      if (rockAt(L, hx, hy)) hx = clamp(2 * h.x - hx, x0, x1);          // (not in the rock: the other side of it)
      e.x += clamp(hx - e.x, -160 * DT, 160 * DT); e.y += clamp(hy - e.y, -120 * DT, 120 * DT);
      if (e.st === 'in' && e.stT > e.wait && Math.abs(hx - e.x) < 10 && Math.abs(hy - e.y) < 10) { e.st = 'hover'; e.stT = 0; }
      else if (e.st === 'hover' && ok && e.stT > F.DRONE_HOVER && (staged(s, e.x, e.y) || e.stT > F.DRONE_WAIT)) {
        // it picks its spot (where the Apache is now) and shows it: an Apache that moves is not there when it arrives
        e.st = 'tell'; e.stT = 0; e.tx = h.x; e.ty = h.y;
        ev(s, { t: 'tell', k: 'drone', x: e.x, y: e.y });
      }
      else if (e.st === 'in' && e.stT > F.DRONE_WAIT) { e.st = 'hover'; e.stT = F.DRONE_HOVER; }
    } else if (e.st === 'tell') {
      if (e.stT >= F.DRONE_TELL) {
        var dx = e.tx - e.x, dy = e.ty - e.y, dl = Math.sqrt(dx * dx + dy * dy) || 1;
        e.vx = dx / dl * F.DRONE_V; e.vy = dy / dl * F.DRONE_V; e.st = 'dive'; e.stT = 0;
        ev(s, { t: 'dive', x: e.x, y: e.y });
      }
    } else if (e.st === 'dive') {
      e.x += e.vx * DT; e.y += e.vy * DT;
      var b = heliBox(h), hit = ok && e.x > b.x0 - 4 && e.x < b.x1 + 4 && e.y > b.y0 - 4 && e.y < b.y1 + 8;
      if (hit || rockAt(L, e.x, e.y) || !inView(s, e.x, e.y, 60)) {
        e.alive = false; e.st = 'gone'; e.deadT = 999; I.standDown(s, e);
        ev(s, { t: 'drone_hit', x: e.x, y: e.y });
        if (hit || inView(s, e.x, e.y, 0)) I.explode(s, e.x, e.y, 24, 'kdrone', false);
      }
    }
  }
  function inBeam(s, x, y) {
    var h = s.heli, m = lamp(h), dx = x - m.x, dy = y - m.y, d = Math.sqrt(dx * dx + dy * dy);
    if (d > F.BEAM_LEN || d < 4) return false;
    var da = Math.atan2(dy, dx) - h.beam;
    while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI;
    return Math.abs(da) < F.BEAM_HALF;
  }

  // ------------------------------------------------------------------ rockets, missiles, flares
  function step(s) {
    var L = s.L, h = s.heli, i, j;
    if (!h) return;
    // a lock-on whose man is gone (or who has stopped aiming) is over
    if (s.locking) {
      var lk = null;
      for (i = 0; i < s.enemies.length; i++) if (s.enemies[i].id === s.locking) lk = s.enemies[i];
      if (!lk || !lk.alive || !lk.hostile || (lk.st !== 'lock' && lk.st !== 'aim')) { s.locking = 0; s.lockT = 0; ev(s, { t: 'lock_off' }); }
    }
    for (i = 0; i < s.rockets.length; i++) {
      var r = s.rockets[i];
      if (r.gone) continue;
      r.t++;
      var sp = Math.sqrt(r.vx * r.vx + r.vy * r.vy), nsp = Math.min(F.ROCKET_MAX, sp + F.ROCKET_ACC * DT);
      if (r.tgt && r.t > 3) {
        // guided: it turns after what the pod locked on to (if that is gone, it flies on straight)
        var tg = null;
        for (j = 0; j < s.enemies.length; j++) if (s.enemies[j].id === r.tgt) tg = s.enemies[j];
        if (tg && tg.alive && tg.hostile && !(tg.smokeT > 0)) {
          var ra = Math.atan2(r.vy, r.vx), want = Math.atan2(tg.y - tg.h * 0.5 - r.y, tg.x - r.x), dra = want - ra;
          while (dra > Math.PI) dra -= 2 * Math.PI; while (dra < -Math.PI) dra += 2 * Math.PI;
          ra += clamp(dra, -F.ROCKET_TURN * DT, F.ROCKET_TURN * DT);
          r.dx = Math.cos(ra); r.dy = Math.sin(ra); r.vx = r.dx * sp; r.vy = r.dy * sp;
        } else r.tgt = 0;
      }
      r.vx += r.dx * (nsp - sp); r.vy += r.dy * (nsp - sp);
      for (var k = 0; k < 2 && !r.gone; k++) {
        r.x += r.vx * DT * 0.5; r.y += r.vy * DT * 0.5;
        var boom = rockAt(L, r.x, r.y);
        for (j = 0; j < s.enemies.length && !boom; j++) {
          var e = s.enemies[j];
          if (!e.alive || !e.hostile || e.ext !== 'fly' || e.st === 'panic') continue;
          if (r.x > e.x - e.hw - 2 && r.x < e.x + e.hw + 2 && r.y > e.y - e.h - 2 && r.y < e.y + 2) { boom = true; s.stats.hits++; I.hurtEnemy(s, e, F.ROCKET_HIT * (e.k === 'truck' || e.k === 'launcher' ? F.TRUCK_ROCKET : 1), r.vx, 'blast'); }
        }
        if (boom) { r.gone = true; I.explode(s, r.x, r.y, F.ROCKET_R, 'rocket', true); }
      }
      if (!r.gone && (r.t > F.ROCKET_LIFE || !inView(s, r.x, r.y, 40))) r.gone = true;
    }
    // the chin gun's rounds burst where they land (a flash and a pop: they hurt only what they hit)
    for (i = 0; i < s.bullets.length; i++) {
      var hb = s.bullets[i];
      if (hb.hedp && hb.gone && !hb.popped) { hb.popped = true; if (hb.life > 0 && inView(s, hb.x, hb.y, -2)) ev(s, { t: 'hedp', x: hb.x, y: hb.y }); }
    }
    for (i = 0; i < s.flares.length; i++) {
      var f = s.flares[i];
      if (f.gone) continue;
      f.t++; f.vy += 110 * DT; f.vx *= 0.985; f.x += f.vx * DT; f.y += f.vy * DT;
      if (f.t > F.FLARE_LIFE) f.gone = true;
    }
    for (i = 0; i < s.missiles.length; i++) {
      var q = s.missiles[i];
      if (q.gone) continue;
      q.t++;
      if (q.kind === 'dud') {
        // (the launcher's missile, cooking off as it burns: away into the sky in a spiral, and pop)
        q.ang += q.spin; q.v = Math.min(260, q.v + 9); q.x += Math.cos(q.ang) * q.v * DT; q.y += Math.sin(q.ang) * q.v * DT - 1.2;
        if (q.t > 66) { q.gone = true; ev(s, { t: 'firework', x: q.x, y: q.y }); }
        continue;
      }
      if (q.kind === 'icbm') {
        // (the launcher's missile, away: up off its rail and out of the picture, for somewhere else; it is no danger here)
        q.v = Math.min(420, q.v + 5); q.ang += clamp(-Math.PI / 2 - q.ang, -0.006, 0.006);
        q.x += Math.cos(q.ang) * q.v * DT; q.y += Math.sin(q.ang) * q.v * DT;
        if (q.t > 240) q.gone = true;
        continue;
      }
      var big = q.kind === 'big';
      q.v = big ? Math.min(BG.BIG_V, q.v + 3) : Math.min(F.SAM_V, q.v + 6);
      // what it chases: the Apache, or a flare it has seen (and once a flare has burnt out, nothing: it goes on straight).
      // (an RPG chases nothing: it goes where it was pointed; the launcher's climbs straight off its rail first)
      var tx = null, ty = null;
      if (q.kind === 'rpg') q.v = F.RPG_V;
      else if (big && q.t < BG.BIG_CLIMB) tx = null;
      else if (q.decoy) { var fl = s.flares[q.fl]; if (fl && !fl.gone) { tx = fl.x; ty = fl.y; } }
      else if (heliOK(s)) { tx = h.x; ty = h.y; }
      if (tx !== null) {
        var want = Math.atan2(ty - q.y, tx - q.x), da = want - q.ang, turn = big ? BG.BIG_TURN : F.SAM_TURN;
        while (da > Math.PI) da -= 2 * Math.PI; while (da < -Math.PI) da += 2 * Math.PI;
        q.ang += clamp(da, -turn * DT, turn * DT);
      }
      q.x += Math.cos(q.ang) * q.v * DT; q.y += Math.sin(q.ang) * q.v * DT;
      var b = heliBox(h), onIt = heliOK(s) && !q.decoy && q.x > b.x0 - 3 && q.x < b.x1 + 3 && q.y > b.y0 - 3 && q.y < b.y1 + 3;
      var nearFlare = q.decoy && tx !== null && Math.abs(tx - q.x) < 6 && Math.abs(ty - q.y) < 6;
      if (onIt || nearFlare || rockAt(L, q.x, q.y) || q.t > (big ? BG.BIG_LIFE : F.SAM_LIFE)) {
        q.gone = true;
        ev(s, { t: 'sam_boom', x: q.x, y: q.y, onIt: onIt, k: q.kind || 'sam' });
        if (q.kind === 'rpg') I.explode(s, q.x, q.y, onIt ? F.RPG_R : 14, 'rpg', false);
        else if (big) I.explode(s, q.x, q.y, onIt ? BG.BIG_R : 24, 'big', false);
        else I.explode(s, q.x, q.y, onIt ? F.SAM_R : 16, 'sam', false);
      } else if (!inView(s, q.x, q.y, big ? 160 : 80)) q.gone = true;
    }
    // mortar shells: up out of the picture, then down on where they were marked, bursting there
    for (i = 0; i < s.shells.length; i++) {
      var sh = s.shells[i];
      if (sh.gone) continue;
      sh.t++;
      if (sh.kind === 'flak') {
        if (sh.t === 0) ev(s, { t: 'flak', x: sh.sx, y: sh.sy, tx: sh.tx, ty: sh.ty });
        if (sh.t > 0) { var ff = Math.min(1, sh.t / (sh.fuse - 18)); sh.x = sh.sx + (sh.tx - sh.sx) * ff; sh.y = sh.sy + (sh.ty - sh.sy) * ff; }
        if (sh.t >= sh.fuse) { sh.gone = true; ev(s, { t: 'mortar_boom', x: sh.tx, y: sh.ty, k: 'flak' }); I.explode(s, sh.tx, sh.ty, BG.CG_FLAK_R, 'flak', false); }
        continue;
      }
      if (sh.t >= F.MORTAR_FUSE) { sh.gone = true; ev(s, { t: 'mortar_boom', x: sh.tx, y: sh.ty }); I.explode(s, sh.tx, sh.ty, F.MORTAR_R, 'mortar', false); }
    }
    if (s.spotT > 0) s.spotT--;
    // machines that have just been killed go up: a drone in a puff (harmless to the Apache: it was shot), a gun with a bang
    // and its wreck left standing on its emplacement
    for (i = 0; i < s.enemies.length; i++) {
      var de = s.enemies[i];
      if (de.alive || de.ext !== 'fly' || de.boomed) continue;
      if (de.k === 'drone') { de.boomed = true; de.st = 'gone'; de.deadT = 999; I.explode(s, de.x, de.y - 5, 16, 'kdrone', true); }
      else if (de.k === 'aa') { de.boomed = true; I.explode(s, de.x, de.y - 12, 30, 'aa', true); }
      else if (de.k === 'crate') { de.boomed = true; I.explode(s, de.x, de.y - 6, 20, 'crate', true); }
      if (de.k === 'aa' || de.k === 'crate') { de.air = false; de.vx = 0; de.vy = 0; de.x = de.px; de.y = de.py; }
      if (de.k === 'cgun') {
        // the Castle Gun goes up in a run of bangs, and stays, its barrels down
        de.air = false; de.vx = 0; de.vy = 0; de.x = de.px; de.y = de.py; de.deadT = 0;
        if (de.dieT == null) { de.dieT = 0; ev(s, { t: 'boss_dying', k: 'cgun', x: de.x, y: de.y - 20 }); if (s.boss) s.boss.st = 'dying'; }
        de.dieT++;
        if (de.dieT % 9 === 1 && de.dieT < 60) I.explode(s, de.x + (s.rand() - 0.5) * 50, de.y - 10 - s.rand() * 30, 22, 'cgun', true);
        if (de.dieT === 64) { I.explode(s, de.x, de.y - 20, 48, 'cgun', true); ev(s, { t: 'boss_dead', k: 'cgun', x: de.x, y: de.y }); if (s.boss) s.boss.st = 'dead'; s.boss = null; }
        continue;
      }
      if (de.k === 'launcher') {
        // the launcher goes up in a run of bangs along its length; its missile, if it has one up, cooks off into the sky; then
        // the big one, and it burns down to nothing (the courtyard is wanted for the landing)
        de.air = false; de.vx = 0; de.vy = 0; de.deadT = 0;            // (kept: it takes longer than the dead usually last, and the gate it came out of is drawn from it)
        if (de.dieT == null) { de.dieT = 0; de.smokeT = 0; ev(s, { t: 'boss_dying', k: 'launcher', x: de.x, y: de.y - 20 }); if (s.boss) s.boss.st = 'dying'; if (s.locking === de.id) { s.locking = 0; s.lockT = 0; } }
        de.dieT++;
        if (de.dieT % 7 === 1 && de.dieT < 84) I.explode(s, de.x + (s.rand() - 0.5) * 130, de.y - 8 - s.rand() * 34, 22, 'launcher', true);
        if (de.dieT === 30 && de.missile) {
          var nz = lnNose(de);
          s.missiles.push({ kind: 'dud', x: nz.x, y: nz.y, ang: nz.a, v: 40, t: 0, gone: false, decoy: true, spin: 0.16 });
          de.missile = false; ev(s, { t: 'cookoff', x: nz.x, y: nz.y });
        }
        if (de.dieT === 90) { I.explode(s, de.x, de.y - 24, 56, 'launcher', true); ev(s, { t: 'boss_dead', k: 'launcher', x: de.x, y: de.y }); if (s.boss) s.boss.st = 'dead'; s.boss = null; }
        continue;
      }
      if (de.k === 'truck') {
        // a pickup that has had it: a bang, and it rolls to a stop on the road, burning
        if (!de.wreck) { de.wreck = true; de.vx = Math.max(0, Math.min(140, de.rollV || 80)); I.explode(s, de.x, de.y - 18, 36, 'truck', true); }
        de.air = false; de.vy = 0; de.vx *= 0.965; de.x += de.vx * DT; de.y = groundAt(L, de.x); de.ang = slopeAt(L, de.x);
      }
    }
    rescue(s);
  }
  // ------------------------------------------------------------------ the people tied up on the roofs
  // (Khaled, 22 Oct 22:49: "there aren't any hostages to save in Taiz"; he chose a rescue from the air, three of them.) One
  // on a roof in the lower town, one beside the old city's gate, one in the village, each with a lantern by him. Hold the
  // Apache low over one: a rope goes down to him, he takes it and goes up it into the Apache (he climbs out with Yazeed in
  // the courtyard at the end). Each is 500 and five rockets ("Take this"), and all three is the Liberator. (The roofs being
  // stone, the Apache can come down over him only as far as his roof lets it: low beside him counts as well.)
  function ropeAt(h) { return bodyAt(h, F.ROPE_AT); }
  // is the Apache where the rope reaches him (b: where it hangs from)?
  function overHim(b, o) { var dx = b.x - o.x, dy = (o.y - F.HANDS) - b.y; return Math.abs(dx) <= F.RESCUE_DX && dy >= -F.HANDS - 12 && dy <= F.RESCUE_UP; }
  function rescue(s) {
    var h = s.heli, p = s.p, ok = heliOK(s) && !s.intro && !s.ending && !s.lost, b = ok ? ropeAt(h) : null, i;
    for (i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.k !== 'detainee' || o.gone) continue;
      if (o.st === 'tied') {
        // (the first time one is well in the picture, a word on what to do)
        if (!o.seen && inView(s, o.x, o.y - 24, -60)) { o.seen = true; ev(s, { t: 'captive', x: o.x, y: o.y }); }
        var over = !!b && overHim(b, o), was = o.rope || 0;
        o.rope = clamp(was + (over ? 1 : -1.5) / F.RESCUE_T, 0, 1);
        if (over && !was) ev(s, { t: 'rope_down', x: b.x, y: b.y });
        if (o.rope >= 1) {
          o.st = 'lift'; o.t = 0;
          s.stats.freed++;
          (s.stats.rescued || (s.stats.rescued = [])).push(o.px);
          s.score += 500;
          p.grenades = Math.min(99, p.grenades + F.RESCUE_ROCKETS);
          ev(s, { t: 'freed', x: o.x, y: o.y });
          ev(s, { t: 'pickup', k: 'rockets', x: o.x, y: o.y - 24 });
        }
      } else if (o.st === 'lift') {
        // (up the rope; o.t is counted with the other things standing in the level)
        if (o.t >= F.LIFT_T || !ok) { o.st = 'aboard'; o.gone = true; }
      }
    }
  }

  // ------------------------------------------------------------------ what the rest of the game asks
  // one of theirs arriving at the Apache: a rifle round chips at it (a plate goes after enough of them); a heavy one hurts
  function hitHeli(s, b) {
    var h = s.heli, p = s.p;
    if (!h || p.dead || h.st !== 'fly') return false;
    var bx = heliBox(h);
    if (b.x < bx.x0 || b.x > bx.x1 || b.y < bx.y0 || b.y > bx.y1) return false;
    if (p.inv > 0) { ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y }); return true; }
    if (b.chip) {
      ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y });
      if (++h.chip >= F.CHIP) { h.chip = 0; I.hurtPlayer(s, b.x - b.vx, b.src || 'rifle'); }
    } else I.hurtPlayer(s, b.x - b.vx, b.src || 'heavy gun');
    return true;
  }
  // one of his shots: nothing of the Apache's own to stop here (a missile is not stopped by shots, second cut: the flares are
  // the answer to it, and the lock-on's beat says when)
  function shot(s, b) {
    // (an RPG can be shot down; a missile cannot)
    for (var i = 0; i < s.missiles.length; i++) {
      var q = s.missiles[i];
      if (q.gone || (q.kind !== 'rpg' && q.kind !== 'big')) continue;
      var rr = q.kind === 'big' ? 10 : 7;
      if (Math.abs(b.x - q.x) < rr && Math.abs(b.y - q.y) < rr) {
        if (q.kind === 'big' && --q.hp > 0) { ev(s, { t: 'hit', kind: 'metal', x: b.x, y: b.y }); return true; }
        var pts = q.kind === 'big' ? 400 : 50;
        q.gone = true; s.score += pts; ev(s, { t: 'sam_boom', x: q.x, y: q.y, shot: true, pts: pts, k: q.kind }); I.explode(s, q.x, q.y, q.kind === 'big' ? 26 : 12, q.kind, true); return true;
      }
    }
    return false;
  }
  function blast(s, x, y, r, kind, own) {
    var h = s.heli, p = s.p;
    if (own || !h || p.dead || h.st !== 'fly') return;
    var nx = clamp(x, h.x - F.HW, h.x + F.HW), ny = clamp(y, h.y - F.HT, h.y + F.HB);
    if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < (r - 2) * (r - 2)) I.hurtPlayer(s, x, kind === 'sam' ? 'missile' : (kind === 'kdrone' ? 'drone' : (kind === 'big' ? 'launcher missile' : kind)));
  }

  // ------------------------------------------------------------------ who wakes, where the camera goes, the checkpoints, the end
  function groups(s) {
    var L = s.L, p = s.p, rt = route(L), k, i;
    if (s.intro) { s.dark = dark(L, 0); return; }            // (the opening keeps its own camera, and nobody wakes)
    for (k in s.groups) {
      var G = s.groups[k], def = L.groups[k];
      if (G.done) continue;
      if (!G.awake) {
        if (G.afterT < 0 && ((def.trigU != null && s.u >= def.trigU) || (def.after && s.groups[def.after].done))) G.afterT = def.delay || 0;
        if (G.afterT >= 0 && --G.afterT <= 0) G.awake = true;
        if (!G.awake) continue;
        G.awakeT = 0;
      }
      G.awakeT++;
      for (i = G.pending.length - 1; i >= 0; i--) if (G.awakeT >= G.pending[i].at) { var sp = G.pending[i].sp; G.pending.splice(i, 1); arrive(s, sp); }
      if (!G.pending.length && G.hostile <= 0 && !G.hold) { G.done = true; ev(s, { t: 'group_done', g: k }); }
    }
    // left well behind (below, on the climb): no longer anyone's problem
    for (i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.alive && e.hostile && e.ext === 'fly' && e.u < s.u - 400 && !inView(s, e.x, e.y, 30)) { I.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; }
    }
    var gate = null, gi = -1;
    for (i = 0; i < s.gates.length; i++) {
      var gt = s.gates[i];
      if (gt.done) continue;
      var all = true;
      for (var j = 0; j < gt.groups.length; j++) if (!s.groups[gt.groups[j]].done) all = false;
      if (all) { gt.done = true; s.gateWait = 0; ev(s, { t: 'go', gate: gt.id, dir: dirAt(rt, gt.u) }); continue; }
      gate = gt; gi = i;
      break;
    }
    // a chase (the hillside road): once it is on, the camera goes up the road by itself at the chase's pace, taking the
    // Apache with it, to the end of the road (the fight's own point); the pickups keep ahead of it, and at the end the
    // ones left get away
    s.gateNow = gate;
    var ch = gate ? L.gates[gi].chase : null;
    s.chaseOn = false;
    if (ch && s.u >= ch.u0 - 2 && s.groups[gate.groups[0]].awake) {
      s.chaseOn = true; s.chaseV = ch.v;
      if (!s.chaseT) { s.chaseU = s.u; ev(s, { t: 'chase', x: p.x, y: p.y }); }
      s.chaseT++;
      if (!p.dead) { s.chaseU = Math.min(gate.u, s.chaseU + ch.v * DT); s.u = Math.max(s.u, s.chaseU); }
      if (s.u >= gate.u - 1) s.chaseEnd = true;
    }
    // a fight with nobody left in it must not hold the Apache for ever
    if (gate && s.u >= gate.u - 1) {
      var live = 0, waiting = 0;
      for (i = 0; i < gate.groups.length; i++) { var GG = s.groups[gate.groups[i]]; if (!GG.done) waiting += GG.pending.length + (GG.awake ? 0 : 1); }
      for (i = 0; i < s.enemies.length; i++) { var en = s.enemies[i]; if (en.alive && en.hostile && gate.groups.indexOf(en.g) >= 0 && inView(s, en.x, en.y, 40)) live++; }
      s.gateWait = live || waiting ? 0 : s.gateWait + 1;
      if (s.gateWait > 420) {
        s.failsafe++;
        for (i = 0; i < s.enemies.length; i++) { var z = s.enemies[i]; if (z.alive && z.hostile && gate.groups.indexOf(z.g) >= 0) { I.standDown(s, z); z.alive = false; z.st = 'gone'; z.deadT = 999; } }
        ev(s, { t: 'failsafe', gate: gate.id });
        s.gateWait = 0;
      }
    }
    s.holdU = gate ? gate.u : null;
    var maxU = gate ? Math.min(gate.u, rt.len) : rt.len;
    if (s.guide) {
      if (!p.dead && s.status === 'play') { s.guide.u = Math.min(s.guide.u1, s.guide.u + s.guide.v * DT); s.u = Math.max(s.u, Math.min(maxU, s.guide.u)); }
      if (s.u >= s.guide.u1 - 1) s.guide = null;
    }
    if (!p.dead && s.heli && s.heli.st === 'fly') {
      var c = ahead(rt, s.u), ld = (p.x - c.x) * c.dx + (p.y - c.y) * c.dy, need = Math.abs(c.dx) * s.viewW * F.LEAD + Math.abs(c.dy) * F.LEAD_UP;
      if (ld > need && s.u < maxU) s.u = Math.min(maxU, s.u + Math.min(F.CAM_V, (ld - need) * 0.25 + 0.6));
    }
    if (s.status === 'clear') s.u = Math.min(rt.len, s.u + 1.2);
    var c2 = at(rt, s.u);
    s.cam = c2.x - s.viewW / 2; s.camY = c2.y - VH(s) / 2;
    var z2 = s.zone;
    while (z2 + 1 < L.zones.length && s.u >= L.zones[z2 + 1].u) z2++;
    if (z2 !== s.zone) { s.zone = z2; s.zoneScore = s.score; ev(s, { t: 'checkpoint', zone: z2, name: L.zones[z2].name }); I.refill(s); }
    // the launcher's missile got away: a moment to watch it go, then the mission is lost (Continue: the keep again)
    if (s.lost && s.status === 'play') { if (++s.lost.t >= BG.LOST_T) { s.status = 'over'; ev(s, { t: 'over', why: s.lost.why }); } }
    if (s.status === 'play' && !p.dead && !s.lost && s.u >= rt.len - 2 && !gate && !s.boss) {          // (a boss still going up: after it)
      if (L.fly.landing && !s.ending) { s.ending = { st: 'dawn', t: 0, t2: 0 }; ev(s, { t: 'dawn', x: L.fly.landing.pad, y: L.fly.landing.y }); }
      else if (!L.fly.landing) { s.status = 'clear'; s.clearT = 0; ev(s, { t: 'clear' }); }
    }
    if (s.ending) ending(s);
    s.dark = dark(L, s.u);
  }
  // the end: dawn comes up over Taiz; the Apache is brought down into the castle's courtyard (or, after a while, it
  // brings itself down), sets down, and Yazeed climbs out and walks off towards the keep
  function ending(s) {
    var E = s.ending, h = s.heli, Q = s.L.fly.landing, p = s.p;
    E.t++;
    s.dawn = smooth(E.t / BG.DAWN_T);
    if (E.st === 'dawn') {
      if (h.st === 'fly' && !p.dead && ((h.x > Q.x0 && h.x < Q.x1 && h.y > Q.y - 80) || E.t > BG.LAND_AUTO)) { E.st = 'settle'; E.t2 = 0; E.hx = h.x; E.hy = h.y; h.st = 'settle'; ev(s, { t: 'settle', x: h.x, y: h.y }); }
    } else if (E.st === 'settle') {
      E.t2++;
      var f = smooth(E.t2 / BG.SETTLE_T);
      h.x = E.hx + (Q.pad - E.hx) * f; h.y = E.hy + (Q.y - 19 - E.hy) * f; h.vx = 0; h.vy = 0; h.tilt *= 0.9;
      p.x = h.x; p.y = h.y;
      if (E.t2 >= BG.SETTLE_T) {
        E.st = 'out'; E.t2 = 0; h.st = 'landed'; s.yaz = { x: h.x + 12, y: Q.y - 18, face: 1, st: 'board', walkD: 0, t: 0, a: 0 };
        // (and after him, whoever was lifted off the roofs on the way: out one by one, a few steps off the other way, and a wave)
        E.men = [];
        var nm = Math.min(3, (s.stats.rescued || []).length);
        for (var mk = 0; mk < nm; mk++) E.men.push({ x: h.x - 4, y: Q.y - 18, a: 0, st: 'wait', t: -(30 + mk * 20), walkD: 0, to: h.x - 80 - mk * 24 });     // (clear of its tail)
        ev(s, { t: 'touchdown', x: h.x, y: h.y });
      }
    } else if (E.st === 'out') {
      E.t2++;
      var y = s.yaz;
      if (E.t2 < 22) { y.a = E.t2 / 22; y.y = Q.y - 18 + E.t2 * 18 / 22; y.st = 'board'; }
      else { y.a = 1; y.y = Q.y; y.st = 'walk'; y.face = 1; y.x += 46 * DT; y.walkD += 46 * DT; }
      for (var mi = 0; E.men && mi < E.men.length; mi++) {
        var m = E.men[mi];
        if (++m.t < 0) continue;
        if (m.t < 22) { m.st = 'board'; m.a = m.t / 22; m.y = Q.y - 18 + m.t * 18 / 22; }
        else if (m.x > m.to) { m.st = 'walk'; m.a = 1; m.y = Q.y; m.x = Math.max(m.to, m.x - 34 * DT); m.walkD += 34 * DT; }
        else { m.st = 'wave'; m.a = 1; m.y = Q.y; }
      }
      if (E.t2 === 100) { s.status = 'clear'; s.clearT = 0; ev(s, { t: 'clear' }); }
    }
  }
  function dirAt(rt, u) { var c = at(rt, u + 4); return Math.abs(c.dy) > Math.abs(c.dx) ? (c.dy < 0 ? 'up' : 'down') : (c.dx < 0 ? 'left' : 'right'); }
  function sweep(s) {
    s.rockets = s.rockets.filter(function (r) { return !r.gone; });
    s.missiles = s.missiles.filter(function (q) { return !q.gone; });
    s.shells = s.shells.filter(function (q) { return !q.gone; });
    // (flares stay in the list while a missile may still be chasing one by its place in it)
    if (!s.missiles.some(function (q) { return q.decoy; })) s.flares = s.flares.filter(function (f) { return !f.gone; });
  }

  Sim.OP = OP;
  Sim.ext.fly = { create: create, player: player, man: man, step: step, hitHeli: hitHeli, shot: shot, blast: blast, groups: groups, sweep: sweep, rock: rock,
                  route: route, at: at, ahead: ahead, uOf: uOf, rockAt: rockAt, rocks: rocks, heliBox: heliBox, inView: inView, dark: dark, muzzle: muzzle, lamp: lamp, inBeam: inBeam,
                  reach: reach, bodyAt: bodyAt, standY: standY, ropeAt: ropeAt, overHim: overHim, F: F };
})();
if (typeof module !== 'undefined') module.exports = Sim;
