// taiz_bot.js - Taiz by Apache without a screen, shared by unit_taiz.js and experiments/baselines.js:
// the rules that must hold every tick (check), the pilot bot that flies the whole range, random thumbs (fuzz),
// run() that plays the range with continues, and hashOf, a run's end state in twelve characters.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
try { require(path.join(__dirname, '../src/tailor.js')); } catch (e) {}
require(path.join(__dirname, '../src/fly.js'));
const TAIZ = require(path.join(__dirname, '../src/level_taiz.js'));
const X = Sim.ext.fly, F = Sim.F, ZM = TAIZ.zoom || 1, VH = Math.round(216 * ZM);
const WW = w => Math.round(w * ZM);          // (a picture w wide on the screen shows this much of the world)

// ------------------------------------------------------------------ rules for every tick
function check(s, prev, where) {
  const p = s.p, h = s.heli, bad = [];
  const fin = v => typeof v === 'number' && isFinite(v);
  if (!fin(h.x) || !fin(h.y) || !fin(h.vx) || !fin(h.vy) || !fin(p.x) || !fin(p.y)) bad.push('Apache not finite');
  if (s.status === 'play' && h.st === 'fly' && !p.dead) {
    // (the camera moves after the Apache does, by up to CAM_V a tick: it is put back inside on the next)
    if (h.x < s.cam + F.EDGE_X - 4 || h.x > s.cam + s.viewW - F.EDGE_X + 4) bad.push('Apache off the picture x=' + h.x.toFixed(1) + ' cam=' + s.cam.toFixed(1));
    if (h.y < s.camY + F.EDGE_T - 4 || h.y > s.camY + VH - F.EDGE_B + 4) bad.push('Apache off the picture y=' + h.y.toFixed(1) + ' camY=' + s.camY.toFixed(1));
    for (const [dx, dy] of [[-F.HW, 0], [F.HW, 0], [0, F.HB], [0, -F.HT]]) if (X.rockAt(s.L, h.x + dx, h.y + dy)) { bad.push('Apache in stone at ' + h.x.toFixed(1) + ',' + h.y.toFixed(1)); break; }
  }
  if (s.u < prev.u - 1e-9) bad.push('camera went back along the route');
  if (p.plates < 0 || p.plates > Sim.T.PLATES || p.lives < 0 || p.grenades < 0 || p.grenades > F.ROCKETS + F.RESCUE_ROCKETS * s.stats.detainees) bad.push('bad counters');
  if (s.stats.freed > s.stats.detainees || s.stats.freed !== (s.stats.rescued || []).length) bad.push('freed ' + s.stats.freed + ' of ' + s.stats.detainees + ', rescued ' + JSON.stringify(s.stats.rescued));
  if (s.bullets.length > 400 || s.enemies.length > 90 || s.missiles.length > 20 || s.rockets.length > 30 || s.flares.length > 60) bad.push('too many things');
  const count = {};
  for (const e of s.enemies) {
    if (!fin(e.x) || !fin(e.y)) bad.push('enemy not finite ' + JSON.stringify({ k: e.k, g: e.g, x: e.x, y: e.y, st: e.st, alive: e.alive, plat: e.plat }));
    if (e.alive && e.hostile) count[e.g] = (count[e.g] || 0) + 1;
  }
  for (const k in s.groups) if ((count[k] || 0) !== s.groups[k].hostile) bad.push('group ' + k + ' count ' + s.groups[k].hostile + ' but ' + (count[k] || 0) + ' hostile');
  for (const q of s.missiles) if (!fin(q.x) || !fin(q.y)) bad.push('missile not finite');
  if (s.locking && !s.enemies.some(e => e.id === s.locking && e.alive && (e.st === 'lock' || e.st === 'aim'))) bad.push('a lock-on with nobody locking');
  if (bad.length) throw new Error(where + ' tick ' + s.tick + ': ' + bad.join('; '));
}

// ------------------------------------------------------------------ a pilot
// Flies ahead of the middle of the picture along the route, high over the roofs (and out from the rock on the climb),
// keeps the trigger down, drops flares when a missile is on the way, sends rockets at the guns.
function pilot(opt) {
  opt = opt || {};
  let flareWait = 0, rocketWait = 0;
  return function (s) {
    const h = s.heli, rt = X.route(s.L), c = X.ahead(rt, s.u), held = s.holdU != null && s.u >= s.holdU - 2;
    const lead = held ? 0 : Math.abs(c.dx) * s.viewW * F.LEAD + Math.abs(c.dy) * F.LEAD_UP + 40;
    // ahead along the route, and off to its left-hand side: above it going along (over the roofs), out from the rock going up
    // (going down, into the souq or under the bridge: along the route itself)
    const k = c.dy > 0.3 ? 0 : (opt.low ? -10 : 80) - 10 * Math.abs(c.dy);
    let tx = c.x + c.dx * lead + c.dy * k, ty = c.y + c.dy * lead - c.dx * k;
    if (held && Math.abs(c.dy) > Math.abs(c.dx)) ty -= 30;
    // in a fight: the gun reaches ahead and down, and down behind, but not up: keep them all ahead of it and under it
    // (left of the leftmost, over the highest)
    if (held) {
      let left = null, top = null;
      for (const e of s.enemies) if (e.alive && e.hostile && e.k !== 'drone' && e.st !== 'panic' && X.inView(s, e.x, e.y, 0)) { if (left === null || e.x < left) left = e.x; const t = e.y - e.h; if (top === null || t < top) top = t; }
      if (left !== null) tx = Math.max(s.cam + F.EDGE_X + 12, Math.min(tx, left - 90));
      if (top !== null) ty = Math.min(ty, top - 44);
      ty = Math.max(ty, s.camY + F.EDGE_T + 6);
    }
    // somebody tied up on a roof in the picture: down over him until he is up the rope (opt.noRescue: leave him)
    if (!opt.noRescue) for (const o of s.props) {
      if (o.k !== 'detainee' || o.gone || o.st !== 'tied' || !X.inView(s, o.x, o.y - 30, -16)) continue;
      tx = o.x - F.ROPE_AT[0]; ty = o.y - F.HANDS - 50 - F.ROPE_AT[1];
      break;
    }
    // (something in the way ahead: go over it)
    for (let k = 1; k <= 4; k++) if (X.rockAt(s.L, h.x + Math.sign(tx - h.x || 1) * (F.HW + 12 * k), h.y + F.HB + 4)) { ty = Math.min(ty, h.y - 30); break; }
    let ax = Math.max(-1, Math.min(1, (tx - h.x) / 50)), ay = Math.max(-1, Math.min(1, (ty - h.y) / 40));
    // (stone overhead on the way up, a ledge over the nose or the tail: out from under it, to the side that is clear)
    if (ay < 0) {
      const over = dx => [-2, -8, -F.HT - 4, -F.HT - 12].some(dy => X.rockAt(s.L, h.x + dx, h.y + dy));
      const nose = over(F.HW + 2) || over(F.HW * 0.5), tail = over(-F.HW - 2) || over(-F.HW * 0.5);
      if (nose && !tail) ax = -1; else if (tail && !nose) ax = 1;
    }
    let jump = false, grenade = false;
    if (flareWait > 0) flareWait--; if (rocketWait > 0) rocketWait--;
    // flares in the last moments of a lock-on (they are still fresh when it fires), or at a missile on its way
    const threat = s.locking && s.lockT > (opt.lateFlares ? 90 : 30) || s.missiles.some(q => !q.decoy && Math.hypot(q.x - h.x, q.y - h.y) < 200);
    if (threat && flareWait <= 0 && !opt.noFlares) { jump = true; flareWait = 20; }
    // out of the way of a drone that has picked its moment, and of a missile with no flare to chase
    if (!opt.noDodge) {
      for (const e of s.enemies) if (e.alive && e.k === 'drone' && (e.st === 'tell' || e.st === 'dive')) { ay = e.y < h.y ? 1 : -1; if (h.y > s.camY + VH - 46) ay = -1; if (h.y < s.camY + 50) ay = 1; }
      for (const q of s.missiles) if (!q.decoy && Math.hypot(q.x - h.x, q.y - h.y) < 120 && (h.flareCd > 0 || q.kind === 'rpg')) ay = q.y < h.y ? 1 : -1;
      // out of the ring where a shell is coming down (a mortar's, the Castle Gun's flak)
      // (a shell marked near it: off to whichever side has least coming down on it; a shell right on it has no 'away')
      const shells = (s.shells || []).filter(q => q.t > -10);
      if (shells.some(q => Math.hypot(q.tx - h.x, q.ty - h.y) < (q.kind === 'flak' ? 30 : F.MORTAR_R) + 44)) {
        let best = null;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, -1], [0, 1], [0.7, -0.7], [-0.7, -0.7], [0.7, 0.7], [-0.7, 0.7]]) {
          const px = h.x + dx * 90, py = h.y + dy * 60;
          if (py < s.camY + F.EDGE_T + 4 || py > s.camY + VH - F.EDGE_B - 4 || px < s.cam + F.EDGE_X || px > s.cam + s.viewW - F.EDGE_X || X.rockAt(s.L, px, py)) continue;
          let danger = 0; for (const q of shells) danger += Math.max(0, 80 - Math.hypot(q.tx - px, q.ty - py));
          if (!best || danger < best.d) best = { dx, dy, d: danger };
        }
        if (best) { ax = best.dx; ay = best.dy; }
      }
      // (the Castle Gun's sweep: off to the side of the gun that its red wedge leaves clear)
      for (const g of s.enemies) if (g.alive && g.k === 'cgun' && g.st === 'sweep' && g.sweepTo != null) { const safe = g.sweepDir < 0 ? -1 : 1; if ((h.x - g.x) * safe < 120) ax = safe; }
    }
    if (!opt.noRockets && rocketWait <= 0 && s.enemies.some(e => e.alive && e.hostile && e.k === 'aa' && X.inView(s, e.x, e.y, -10) && Math.abs(e.y - 12 - h.y) < 40 && e.x > h.x)) { grenade = true; rocketWait = 30; }
    // on the aim stick: at the nearest thing the gun can reach (or nothing, and not firing); else FIRE held, and the gun finds its own
    if (opt.stick) {
      const m = X.muzzle(h);
      let best = null, bd = 1e9;
      for (const e of s.enemies) {
        if (!e.alive || !e.hostile || e.st === 'panic' || e.emerge > 0 || e.hidden || !X.inView(s, e.x, e.y - e.h / 2, -4)) continue;
        const low = e.k === 'sam' && e.covered;            // (his head over the parapet: last)
        const dx = e.x - m.x, dy = (low ? e.y - 10 : e.y - e.h * 0.55) - m.y, d = Math.hypot(dx, dy), a = Math.atan2(dy, dx);
        if (a < -F.GUN_UP || a > F.GUN_BACK || d > 520) continue;
        if (d * (low ? 2.5 : 1) < bd) { bd = d * (low ? 2.5 : 1); best = [dx / d, dy / d]; }
      }
      return { mx: 0, my: 0, ax: ax, ay: ay, fire: false, gun: !!best, gx: best ? best[0] : 0, gy: best ? best[1] : 0, jump: jump, grenade: grenade, auto: false };
    }
    return { mx: 0, my: 0, ax: ax, ay: ay, fire: true, jump: jump, grenade: grenade, auto: false };
  };
}
function fuzz(seed) {
  let a = seed >>> 0;
  const r = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  let hold = 0, cur = null;
  return function () {
    if (hold-- <= 0) { hold = Math.floor(r() * 40); cur = { mx: Math.floor(r() * 3) - 1, my: Math.floor(r() * 3) - 1, fire: r() < 0.7, jump: r() < 0.1, grenade: r() < 0.08, auto: r() < 0.3 }; if (r() < 0.5) { cur.ax = r() * 2 - 1; cur.ay = r() * 2 - 1; } if (r() < 0.4) { const g = r() * Math.PI * 2; cur.gun = true; cur.gx = Math.cos(g); cur.gy = Math.sin(g); } }
    return cur;
  };
}
function run(bot, o) {
  let s = Sim.create(TAIZ, { viewW: o.viewW || WW(468), viewH: VH, seed: o.seed || 1, lanes: o.lanes || [0.18, 0.25] });
  let prev = { u: s.u }, conts = 0;
  const N = (o.seconds || 600) * 60, log = [];
  let launches = 0, decoys = 0, shotDown = 0;
  for (let t = 0; t < N; t++) {
    const inp = bot(s);
    inp.viewW = s.viewW; inp.viewH = s.viewH;
    Sim.step(s, inp);
    for (const e of s.events) {
      if (o.log && ['checkpoint', 'life_lost', 'go', 'qanya', 'scatter', 'sam_launch', 'decoyed', 'failsafe', 'clear', 'over', 'freed'].includes(e.t)) log.push((t / 60).toFixed(1) + 's ' + e.t + (e.gate ? ' ' + e.gate : '') + (e.name ? ' ' + e.name : '') + (e.why ? ' ' + e.why : '') + (e.t === 'sam_launch' && e.decoy ? ' (at the flares)' : ''));
      if (e.t === 'sam_launch') launches++;
      if (e.t === 'decoyed' || (e.t === 'sam_launch' && e.decoy)) decoys++;
      if (e.t === 'sam_boom' && e.shot) shotDown++;
    }
    check(s, prev, o.name || 'run');
    prev = { u: s.u };
    if (s.status === 'over') {
      if (conts >= (o.continues || 0)) break;
      conts++;
      s = Sim.continueZone(s, s.viewW);
      prev = { u: s.u };
    }
    if (s.status === 'clear' && s.clearT > 340) break;
  }
  return { s, conts, log, launches, decoys, shotDown };
}
const hashOf = s => require('crypto').createHash('md5').update(JSON.stringify([s.tick, s.u.toFixed(3), s.heli.x.toFixed(3), s.heli.y.toFixed(3), s.score, s.status, s.p.lives, s.stats.kills, s.scattered])).digest('hex').slice(0, 12);

module.exports = { check, pilot, fuzz, run, hashOf, TAIZ, WW, VH, Sim };
