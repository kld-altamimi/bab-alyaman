// bot.js - play the simulation without a screen: bots that try to win, bots that mash, and checks that must always hold.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
require(path.join(__dirname, '../src/roaster.js'));
try { require(path.join(__dirname, '../src/tailor.js')); } catch (e) {}
try { require(path.join(__dirname, '../src/fly.js')); } catch (e) {}          // (Taiz: loaded so the other missions are checked with it in place)
const LEVEL = require(path.join(__dirname, '../src/level.js'));
LEVEL.ground = require(path.join(__dirname, '../gen/ground.json'));
const MOCHA = require(path.join(__dirname, '../src/level_mocha.js'));
let ZABID = null;
try {
  ZABID = require(path.join(__dirname, '../src/level_zabid.js'));
  ZABID.ground = require(path.join(__dirname, '../gen/stage_zabid.json')).ground;
} catch (e) { ZABID = null; }
const LEVELS = { m1: LEVEL, mocha: MOCHA };
if (ZABID) LEVELS.zabid = ZABID;
const T = Sim.T;

function mulberry(a) { return function () { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------ what must always be true
function check(s, prev, where) {
  const p = s.p, bad = [];
  const fin = v => typeof v === 'number' && isFinite(v);
  if (!fin(p.x) || !fin(p.y) || !fin(p.vx) || !fin(p.vy)) bad.push('player not finite');
  const gy = Sim.groundY(s.L, p.x);
  if (p.y > gy + 0.01) bad.push('player below ground ' + (p.y - gy).toFixed(2));
  if (s.mode === 'foot') {
    if (!p.dead && (p.x < s.cam + 9 - 0.01 || p.x > s.cam + s.viewW - 9 + 0.01) && s.status === 'play') bad.push('player off screen x=' + p.x.toFixed(1) + ' cam=' + s.cam.toFixed(1));
    if (!p.air && !p.dead) { const sy = Sim.surfaceY(s.L, p.plat, p.x); if (sy === null || Math.abs(sy - p.y) > 0.01) bad.push('player not on its surface'); }
  } else {
    const c = s.car;
    if (!fin(c.x) || !fin(c.y) || !fin(c.vx) || !fin(c.vy)) bad.push('car not finite');
    if (c.y > Sim.groundY(s.L, c.x) + 0.01) bad.push('car below the road');
    if (!p.dead && c.st !== 'wreck' && (c.x < s.cam - 1 || c.x > s.cam + s.viewW + 1)) bad.push('car off screen x=' + c.x.toFixed(1) + ' cam=' + s.cam.toFixed(1));
  }
  for (const t of s.trucks) if (!fin(t.x) || !fin(t.y)) bad.push('truck not finite');
  for (const d of s.drones) if (!fin(d.x) || !fin(d.y)) bad.push('drone not finite');
  if (s.boss && (!fin(s.boss.x) || !fin(s.boss.y) || s.boss.hp < 0)) bad.push('boss not finite');
  if (s.trucks.length > 12 || s.drones.length > 12) bad.push('too many machines');
  if (s.cam < prev.cam - 1e-9) bad.push('camera went back');
  if (s.cam > Math.max(0, s.L.endRight - s.viewW) + 1e-6 && s.cam > prev.cam) bad.push('camera past the end');
  if (p.plates < 0 || p.plates > T.PLATES || p.lives < 0 || p.lives > T.LIVES || p.grenades < 0 || p.ammo < 0) bad.push('bad counters');
  if (s.bullets.length > 400 || s.enemies.length > 40 || s.bombs.length > 60) bad.push('too many things: ' + s.bullets.length + ' bullets ' + s.enemies.length + ' enemies ' + s.bombs.length + ' bombs');
  const count = {};
  for (const e of s.enemies) {
    if (!fin(e.x) || !fin(e.y)) bad.push('enemy not finite');
    if (e.alive && e.hostile) count[e.g] = (count[e.g] || 0) + 1;
    if (e.alive && !e.air && e.y > Sim.groundY(s.L, e.x) + 0.01) bad.push('enemy below ground');
  }
  for (const k in s.groups) if ((count[k] || 0) !== s.groups[k].hostile) bad.push('group ' + k + ' count ' + s.groups[k].hostile + ' but ' + (count[k] || 0) + ' hostile');
  for (const b of s.bullets) if (!fin(b.x) || !fin(b.y)) bad.push('bullet not finite');
  for (const b of s.bombs) if (!fin(b.x) || !fin(b.y)) bad.push('bomb not finite');
  if (bad.length) throw new Error(where + ' tick ' + s.tick + ': ' + bad.join('; '));
}

// ------------------------------------------------------------------ bots
function idleBot() { return () => ({ mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false }); }
function runnerBot(auto) { return () => ({ mx: 1, my: 0, fire: !auto, jump: false, grenade: false, auto: !!auto }); }

function fuzzBot(seed) {
  const r = mulberry(seed);
  let cur = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false }, left = 0;
  return () => {
    if (--left <= 0) {
      left = 2 + Math.floor(r() * 26);
      cur = { mx: r() < 0.62 ? 1 : (r() < 0.5 ? -1 : 0), my: r() < 0.2 ? -1 : (r() < 0.25 ? 1 : 0), fire: r() < 0.7, jump: r() < 0.35, grenade: r() < 0.12, auto: r() < 0.3 };
    }
    return cur;
  };
}

// a bot that plays the way a careful person would: dodge first, then shoot, then get on
function smartBot(opts) {
  opts = opts || {};
  const auto = !!opts.auto, noGren = !!opts.noGren;
  let jumpHold = 0, grenWait = 0, goal = null, hop = 0, stuckX = 0, stuckT = 0, tgtId = 0, tgtT = 0, capT = 0, dropT = 0;
  let hopHold = 0, bossGren = 0, side = 1;
  // ---- in the back of the pickup: hop what goes bang, throw at what cannot be hopped, point the gun up at what flies
  function driveBot(s) {
    const p = s.p, c = s.car, D = Sim.D, L = s.L, inp = { mx: 0, my: 0, fire: !auto, jump: false, grenade: false, auto: auto };
    if (p.dead || c.st !== 'drive') return inp;
    if (grenWait > 0) grenWait--;
    let hop = false;
    const air = 2 * D.HOP_V / D.GRAV;
    for (const o of s.props) {
      if (o.gone) continue;
      const dw = o.x - (c.x + D.WHEEL);
      if (o.k === 'rmine' && dw > 4 && dw < 22 + c.vx * 0.07) hop = true;
      if (o.k === 'drum' && o.fuse < 0) {
        const dd = o.x - c.x, reach = (c.vx + D.GREN_VX) * D.GREN_T - 12;
        if (!noGren && p.grenades > 0 && grenWait <= 0 && Math.abs(dd - reach) < 18) { inp.grenade = true; grenWait = 40; }
        if (dd - D.FRONT > 2 && dd - D.FRONT < 14 + c.vx * 0.06) hop = true;
      }
      if (o.k === 'drum' && o.fuse >= 0) { const dd = o.x - c.x; if (dd > -60 && dd < 120 && o.fuse < 16) hop = true; }      // one already burning: be in the air when it goes
    }
    for (const b of s.bombs) {
      if (b.own || b.gone) continue;
      // when and where will it go off, and where shall we be?
      let te, bx = b.x;
      if (b.air) { let x = b.x, y = b.y, vy = b.vy, k = 0; for (; k < 240; k++) { vy += (b.g || T.DYN_G) * Sim.DT; x += b.vx * Sim.DT; y += vy * Sim.DT; if (vy > 0 && y >= Sim.groundY(L, x)) break; } bx = x; te = k / 60 + (b.impact ? 0 : b.fuse / 60); }
      else te = b.fuse / 60;
      const cx = c.x + c.vx * te;
      if (bx > cx - D.REAR - 34 && bx < cx + D.FRONT + 34 && te < air * 0.52) hop = true;
    }
    for (const b of s.bullets) {
      if (b.own || b.gone || !b.heavy) continue;
      const dx = b.x - (c.x + D.FRONT), tt = dx / Math.max(60, c.vx - b.vx);
      if (dx > -20 && tt < 0.26) hop = true;
    }
    // the gun: up at 45 degrees when something flies in that part of the sky
    const m = { x: p.x + 22, y: p.y - 39 };
    for (const d of s.drones) {
      if (d.st === 'gone') continue;
      const ang = Math.atan2(m.y - d.y, d.x - m.x) * 180 / Math.PI;
      if (ang > 22 && ang < 68) inp.my = -1;
    }
    if (hop && !c.air) hopHold = 18;
    if (hopHold > 0) { inp.jump = true; hopHold--; }
    return inp;
  }
  // ---- under the flying boat
  function bossBot(s, inp) {
    const p = s.p, b = s.boss, L = s.L, Bc = Sim.B, bd = Sim.ext.boss.bounds(s);
    let flee = 0, duck = false;
    if (bossGren > 0) bossGren--;
    // what is falling, and where
    for (const o of s.bombs) {
      if (o.own || o.gone || !o.air) continue;
      let x = o.x, y = o.y, vy = o.vy, k = 0;
      for (; k < 240; k++) { vy += (o.g || T.DYN_G) * Sim.DT; x += o.vx * Sim.DT; y += vy * Sim.DT; if (vy > 0 && y >= Sim.groundY(L, x)) break; }
      if (Math.abs(x - p.x) < (o.r || T.DYN_R) + 16 && k < 50) flee = x >= p.x ? -1 : 1;
    }
    for (const o of s.bullets) {
      if (o.own || o.gone || o.vy <= 4) continue;
      const t = ((p.y - 17) - o.y) / o.vy, xi = o.x + o.vx * t;
      if (t > 0 && t < 0.7 && Math.abs(xi - p.x) < 15) flee = xi >= p.x ? -1 : 1;
    }
    for (const d of s.drones) {
      if (d.st === 'gone') continue;
      if ((d.st === 'tell' || d.st === 'dive') && Math.abs(d.tx - p.x) < 34) flee = d.tx >= p.x ? -1 : 1;
    }
    if (b.st === 'swooptell' && b.stT > 26) duck = true;
    if (b.st === 'swoop') duck = true;
    const lo = s.cam + 14, hi = s.cam + s.viewW * (1 - s.laneR) - 8;
    if (flee) { if (flee < 0 && p.x <= lo + 4) flee = 1; else if (flee > 0 && p.x >= hi - 4) flee = -1; }
    if (duck) { inp.my = 1; inp.mx = 0; return; }
    // where to stand: under it, or behind it while it bombs
    let want = b.x;
    if (b.st === 'bomb' || b.st === 'bombtell') want = b.x - b.dir * 46;
    want = Math.max(lo, Math.min(hi, want));
    const dx = b.x - p.x, ad = Math.abs(dx), face = dx >= 0 ? 1 : -1;
    const steep = Math.atan2((p.y - 30) - b.y, Math.max(1, ad)) * 180 / Math.PI;
    // a little drone in the sights comes first
    let pest = null;
    for (const d of s.drones) if (d.st !== 'gone' && Math.abs(d.x - p.x) < 150) pest = d;
    if (flee) { inp.mx = flee; inp.my = -1; }
    else if (pest) {
      const pdx = pest.x - p.x, pst = Math.atan2((p.y - 30) - pest.y, Math.max(1, Math.abs(pdx))) * 180 / Math.PI;
      if (pst > 62) { inp.my = -1; inp.mx = 0; if (Math.abs(pdx) > 12) inp.mx = pdx > 0 ? 1 : -1; }
      else { inp.my = -1; inp.mx = pdx >= 0 ? 1 : -1; }
    }
    else if (ad < 26) {
      inp.my = -1; inp.mx = 0;
      if (p.face !== face && ad > 6) inp.mx = face;
      if (!noGren && p.grenades > 0 && bossGren <= 0 && ad < 30 && Sim.ext.boss.open(b)) { inp.grenade = true; bossGren = 46; }
    } else if (steep > 30 && steep < 60) { inp.mx = face; inp.my = -1; }
    else { inp.mx = Math.abs(want - p.x) > 6 ? (want > p.x ? 1 : -1) : 0; inp.my = -1; if (!inp.mx && p.face !== face) inp.mx = face; }
  }
  // ---- in front of the Big Roaster: keep a little way off its front, shoot, throw over the top, and dodge
  function roasterBot(s, inp) {
    const p = s.p, b = s.boss, RR = Sim.R, L = s.L, f = Sim.ext.roaster.front(b);
    let flee = 0, duck = false, jump = false;
    if (bossGren > 0) bossGren--;
    for (const o of s.bombs) {
      if (o.own || o.gone || !o.air) continue;
      let x = o.x, y = o.y, vy = o.vy, k = 0;
      for (; k < 240; k++) { vy += (o.g || T.DYN_G) * Sim.DT; x += o.vx * Sim.DT; y += vy * Sim.DT; if (vy > 0 && y >= Sim.groundY(L, x)) break; }
      if (Math.abs(x - p.x) < (o.r || T.DYN_R) + 16 && k < 50) flee = x >= p.x ? -1 : 1;
    }
    for (const o of s.bullets) {
      if (o.own || o.gone || !o.hot) continue;
      const dx = o.x - p.x;
      if (dx < -10 || dx > 64) continue;
      if (o.y < p.y - 23) duck = true; else if (dx < 40) jump = true;
    }
    for (const w of s.waves) { const dx = w.x - p.x; if (dx > -6 && dx < 34) jump = true; }
    const lo = s.cam + 14;
    let want = null;
    if (b.st === 'steamtell' || b.st === 'steam') want = Math.min(p.x, f - RR.STEAM_REACH - 16);
    if (b.st === 'back' || b.st === 'lungetell' || b.st === 'lunge' || b.st === 'brake') want = Math.min(p.x, (b.lungeTo ? b.lungeTo - RR.HW : f - 120) - 26);
    inp.my = 0;
    if (want !== null) inp.mx = p.x > want + 2 ? -1 : 0;
    else if (flee) inp.mx = (flee < 0 && p.x <= lo + 4) ? 1 : flee;
    else {
      const gap = f - p.x;
      inp.mx = gap < 96 ? -1 : (gap > 150 ? 1 : 0);
      if (!inp.mx && p.face !== 1) inp.mx = 1;
      if (!noGren && p.grenades > 0 && bossGren <= 0 && gap > 44 && gap < 100 && p.face === 1 && !duck) { inp.grenade = true; inp.my = -1; inp.mx = 1; bossGren = 40; }
    }
    if (p.x <= lo && inp.mx < 0) inp.mx = 0;
    if (duck && !jump) { inp.my = 1; inp.mx = 0; }
    if (jump && !p.air) hopHold = 14;
    if (hopHold > 0) { inp.jump = true; hopHold--; }
  }
  // ---- the Tailor: the bot keeps track of him through the shuffles (it knows which he is), stands in the gap beside his
  // stand on whichever side nobody is in the way, and fires only when it is him the shot will meet first. A guessing bot
  // (opts.guess) picks one of them after each shuffle instead, and learns which are dummies the hard way.
  let suspect = -1, suspectAt = -1, gseed = 7;
  const rng = () => { gseed = (gseed * 16807) % 2147483647; return gseed / 2147483647; };
  function tailorBot(s, inp) {
    const p = s.p, b = s.boss, X = Sim.ext.tailor, tl = s.tailor, slots = s.L.tailor.slots;
    let duck = false, jump = false;
    if (bossGren > 0) bossGren--;
    const lo = s.cam + 14, hi = s.cam + s.viewW * (1 - s.laneR) - 8;
    const figs = tl.figs.filter(f => X.standing(f)), me = X.real(s);
    let tgt = me;
    if (opts.guess && !X.shown(b) && b.st !== 'caught') {
      // (a new guess after every shuffle, and whenever the one guessed turns out to be a dummy)
      if (b.st === 'shuffle') suspect = -1;
      else if (suspect < 0 || suspectAt !== b.t0 || !X.standing(tl.figs[suspect]) || tl.figs[suspect].st === 'bare') {
        const pool = figs.filter(f => f.st !== 'bare');
        suspect = pool.length ? pool[Math.floor(rng() * pool.length)].id : -1; suspectAt = b.t0;
      }
      tgt = suspect >= 0 ? tl.figs[suspect] : null;
    }
    // his throws: scissors coming at chest height, get down; pins lower or coming down on us, jump them
    for (const o of s.bullets) {
      if (o.own || o.gone) continue;
      const dx = o.x - p.x;
      if (Math.abs(dx) < 10) { if (o.y > p.y - 36 && o.y < p.y - 21) duck = true; else if (o.y >= p.y - 21 && o.y < p.y + 2) jump = true; continue; }
      if (Math.sign(o.vx) !== -Math.sign(dx) || Math.abs(o.vx) < 1) continue;
      const t = -dx / o.vx, yi = o.y + o.vy * t;
      if (t > 0.7 || yi < p.y - 38 || yi > p.y + 2) continue;
      if (yi < p.y - 21) { if (t < 0.3) duck = true; } else if (t < 0.28) jump = true;
    }
    // the tape along the floor: jump it as it comes
    const tp = tl.tape;
    if (tp && tp.st === 'out') { const tip = tp.x0 + tp.dir * tp.len; if (Math.abs(tip - p.x) < 46 && (p.x - tip) * tp.dir > -8) jump = true; }
    // where to stand: in the gap beside the one we are after, on a side with no stand between us and him
    let want;
    const busy = b.st === 'shuffle' || b.st === 'stun' || tl.cover > 0;
    if (tgt && X.standing(tgt) && !busy) {
      const side = d => {
        let next = null;
        for (const f of figs) if (f !== tgt && (f.x - tgt.x) * d > 0 && (!next || Math.abs(f.x - tgt.x) < Math.abs(next.x - tgt.x))) next = f;
        const x = next && Math.abs(next.x - tgt.x) < 64 ? (next.x + tgt.x) / 2 : tgt.x + d * 26;
        return x >= lo && x <= hi ? x : null;
      };
      const l = side(-1), r = side(1);
      want = l === null ? r : (r === null ? l : (Math.abs(p.x - l) <= Math.abs(p.x - r) ? l : r));
      if (want === null) want = p.x;
    } else want = Math.max(lo, slots[0] - 44);                 // (while they shuffle: off to one side, out of the way)
    want = Math.min(hi, want);
    // not into a cloud of our own making
    inp.my = 0;
    inp.mx = Math.abs(want - p.x) > 3 ? (want > p.x ? 1 : -1) : 0;
    for (const c of s.clouds) {
      if (c.str < 0.3) continue;
      const cdx = c.x - p.x;
      if (Math.abs((p.y - 17) - c.y) < c.r + 10 && Math.abs(cdx) < c.r + 16 && Math.sign(cdx) === inp.mx) inp.mx = 0;
    }
    // face him, and fire only if the first stand the shot meets is his
    const face = tgt ? (tgt.x >= p.x ? 1 : -1) : 1;
    if (!inp.mx && p.face !== face) inp.mx = face;
    let first = null;
    if (!busy || X.shown(b)) {
      const mx = p.x + p.face * 2;                             // (a shot leaves from the middle of him, not the muzzle)
      for (const f of figs) if ((f.x + p.face * 8 - mx) * p.face >= 0 && (!first || (f.x - first.x) * p.face < 0)) first = f;
    }
    inp.fire = !!(first && first === tgt && Math.abs(first.x - p.x) < 150 && tl.cover <= 0);
    if (!noGren && p.grenades > 0 && bossGren <= 0 && b.st === 'caught' && p.face === face && Math.abs(me.x - p.x) > 44 && Math.abs(me.x - p.x) < 100) { inp.grenade = true; inp.my = -1; bossGren = 50; }
    if (p.x <= lo && inp.mx < 0) inp.mx = 0;
    if (duck && !jump && !p.air) { inp.my = 1; inp.mx = 0; }
    if (jump && !p.air && jumpHold <= 0) jumpHold = 14;
    if (jumpHold > 0) { inp.jump = true; jumpHold--; }
  }
  // ---- a way up to the platform somebody is tied up on: a platform at a time, as far as a jump goes
  function surfaceOf(L, i, x) { return i < 0 ? Sim.groundY(L, x) : Sim.platY(L.plats[i], Math.max(L.plats[i].pts[0][0], Math.min(L.plats[i].pts[L.plats[i].pts.length - 1][0], x))); }
  function routeUp(L, from, to, win) {
    // (from the ground, only what can be got at: win is the stretch of ground he can walk to)
    const ends = i => i < 0 ? win : [L.plats[i].pts[0][0], L.plats[i].pts[L.plats[i].pts.length - 1][0]];
    const prev = { [from]: null }, q = [from];
    while (q.length) {
      const a = q.shift();
      if (a === to) break;
      const ea = ends(a);
      for (let bI = 0; bI < L.plats.length; bI++) {
        if (bI in prev) continue;
        const eb = ends(bI), gapX = Math.max(eb[0] - ea[1], ea[0] - eb[1], 0), mid = (eb[0] + eb[1]) / 2;
        const rise = surfaceOf(L, a, mid) - surfaceOf(L, bI, mid);
        if (rise > 54 || rise < 4 || gapX > 30) continue;
        prev[bI] = a; q.push(bI);
      }
    }
    if (!(to in prev)) return null;
    const path = [];
    for (let n = to; n !== null; n = prev[n]) path.unshift(n);
    return path;
  }
  function climb(s, inp, target) {
    // target: the platform index to be on. Returns true while there is climbing to do.
    const p = s.p, L = s.L;
    if (p.air) {
      // over the one we are making for: come straight down on it
      if (climbTo >= 0) { const q = L.plats[climbTo].pts, a = q[0][0] + 5, b2 = q[q.length - 1][0] - 5; inp.mx = p.x < a ? 1 : (p.x > b2 ? -1 : 0); }
      else inp.mx = climbDir;
      return true;
    }
    if (p.plat === target) return false;
    const path = routeUp(L, p.plat, target, [s.cam + 12, s.cam + s.viewW * (1 - s.laneR) - 6]);
    if (!path || path.length < 2) {
      // nothing goes up from here: down to the ground and try from there
      if (p.plat >= 0) { inp.my = 1; if (dropT <= 0) { jumpHold = 3; dropT = 30; } return true; }
      return false;
    }
    const nx = path[1], pts = L.plats[nx].pts, x0 = pts[0][0], x1 = pts[pts.length - 1][0];
    // stand under the near end of the next one (or at the end of this one) and jump on toward its middle
    const near = p.x < x0 ? x0 + 4 : (p.x > x1 ? x1 - 4 : null);
    climbDir = (x0 + x1) / 2 > p.x ? 1 : -1; climbTo = nx;
    if (near === null || Math.abs(near - p.x) < 16) { inp.mx = climbDir; jumpHold = Math.max(jumpHold, 20); }
    else inp.mx = near > p.x ? 1 : -1;
    return true;
  }
  let climbDir = 1, climbTo = -1;
  return (s) => {
    const p = s.p, L = s.L, inp = { mx: 0, my: 0, fire: !auto, jump: false, grenade: false, auto: auto };
    if (s.mode === 'drive') return driveBot(s);
    if (p.dead || s.status !== 'play') return inp;
    if (s.boss && Sim.ext.boss.open(s.boss)) { bossBot(s, inp); if (noGren) inp.grenade = false; return inp; }
    if (s.boss && Sim.ext.roaster.open(s.boss)) { roasterBot(s, inp); if (noGren) inp.grenade = false; return inp; }
    if (s.boss && Sim.ext.tailor && Sim.ext.tailor.open(s.boss)) { tailorBot(s, inp); if (noGren) inp.grenade = false; return inp; }
    if (grenWait > 0) grenWait--;
    const gren = noGren ? 0 : p.grenades;
    const foes = s.enemies.filter(e => e.alive && e.hostile && Sim.onScreen(s, e.x, 0) && Sim.inReach(s, e.x));      // men out at the edge are nobody's target yet
    const surr = s.enemies.filter(e => e.alive && e.st === 'surr' && !e.captured && Sim.onScreen(s, e.x, 0));
    const gy = Sim.groundY(L, p.x);
    // --- danger first
    let duck = false, flee = 0, jumpNow = false;
    for (const b of s.bullets) {
      if (b.own || b.gone) continue;
      const dx = b.x - p.x, coming = Math.abs(dx) < 14 || (b.vx > 0 && dx < 0) || (b.vx < 0 && dx > 0);
      if (!coming || Math.abs(dx) > 78) continue;
      const tHit = Math.abs(dx) / Math.max(1, Math.abs(b.vx)), yAt = b.y + b.vy * tHit;
      if (yAt < p.y - 36 || yAt > p.y + 2) continue;
      if (Math.abs(b.vy) < 8 && !p.air && yAt < p.y - 23) duck = true;
      else if (Math.abs(dx) < 46) jumpNow = true;
    }
    for (const b of s.bombs) {
      if (b.own || b.gone) continue;
      let lx = b.x;
      if (b.air) {
        // where it comes down
        let x = b.x, y = b.y, vy = b.vy;
        for (let i = 0; i < 200; i++) { vy += T.DYN_G * Sim.DT; x += b.vx * Sim.DT; y += vy * Sim.DT; if (vy > 0 && y >= Sim.groundY(L, x) - (p.y < gy - 6 ? gy - p.y : 0)) break; }
        lx = x;
      }
      if (Math.abs(lx - p.x) < T.DYN_R + 16) flee = lx >= p.x ? -1 : 1;
    }
    for (const o of s.props) {
      if (o.gone) continue;
      if (o.k === 'drum' && o.fuse >= 0 && Math.abs(o.x - p.x) < 62) flee = o.x >= p.x ? -1 : 1;      // a burning drum: get clear
      if (o.k !== 'mine') continue;
      const dx = o.x - p.x;
      if (dx > 0 && dx < 26 && !p.air) jumpNow = true;
    }
    // --- a vent about to blow, or blowing: not into it, and out of it
    let ventStop = 0;
    for (const o of s.props) {
      if (o.k !== 'vent' || o.gone || o.st === 'idle') continue;
      const dx = o.x - p.x;
      if (Math.abs(dx) < Sim.T.VENT_W + 2 && !p.air && p.plat < 0) flee = dx >= 0 ? -1 : 1;
      else if (Math.abs(dx) < 30) ventStop = dx > 0 ? 1 : -1;
    }
    // --- pick someone
    let tgt = null, td = 1e9;
    for (const e of foes) { const d = Math.abs(e.x - p.x) + Math.abs(e.y - p.y) * 0.5; if (d < td) { td = d; tgt = e; } }
    // can the gun bear on the man we are after? (someone else being in its sights does not count)
    let inCone = false;
    if (tgt) {
      const m = Sim.muzzle(p), ex = tgt.x - m.sx, ey = (tgt.y - (tgt.covered ? 27 : tgt.h * 0.56)) - m.sy, dd = Math.hypot(ex, ey) || 1;
      inCone = dd < T.ASSIST_RANGE && (ex * m.dx + ey * m.dy) / dd >= T.ASSIST_COS && !Sim.ducked(tgt);
    }
    // --- errands: the detainee, a man with his hands up
    if (!goal) {
      const det = s.props.find(o => o.k === 'detainee' && o.st === 'tied' && !o.gone);
      // (on the Souq's rooftops, only one this side of where the held screen stops him)
      const reach = !L.walls || !det || s.holdX == null || det.x < s.cam + s.viewW * (1 - s.laneR) - 8;
      if (det && reach && Sim.onScreen(s, det.x, -12) && foes.length <= 1) goal = { k: 'detainee', o: det };
    }
    if (goal && goal.k === 'detainee' && (goal.o.st !== 'tied' || goal.o.gone)) goal = null;
    const loot = s.pickups.find(q => !q.gone && !q.air && Sim.onScreen(s, q.x, -10) && Math.abs(q.y - p.y) < 30);

    if (duck) { inp.my = 1; if (flee) inp.mx = flee; }
    else if (flee) { inp.mx = flee; if (p.x <= s.cam + 14 && flee < 0) inp.mx = 1; }
    else if (goal && goal.k === 'detainee' && L.id !== 'm1') {
      const o = goal.o;
      if (!climb(s, inp, o.plat)) inp.mx = Math.abs(o.x - p.x) > 2 ? (o.x > p.x ? 1 : -1) : 0;
    }
    else if (goal && goal.k === 'detainee') {
      const o = goal.o;
      if (p.plat >= 0 && L.plats[p.plat].id === 'roof') inp.mx = o.x > p.x ? 1 : -1;
      else if (p.plat >= 0 && L.plats[p.plat].id === 'deck') {
        // run at the roof and jump
        if (p.x > 748) inp.mx = -1; else { inp.mx = -1; if (!p.air) jumpNow = true; }
      } else if (!p.air) {
        if (p.x < 742) inp.mx = 1; else if (p.x > 800) inp.mx = -1; else jumpNow = true;
      } else {
        // in the air: steer for the roof if high enough, else for the deck
        inp.mx = (p.y < 150 && p.x > 708) ? -1 : (p.x < 706 ? 1 : (p.y < 128 ? -1 : 0));
      }
      if (jumpNow) jumpHold = 22;
    } else if (surr.length && !foes.length && capT < 260 && Math.abs(surr[0].y - p.y) < 60) {
      // walk into the man with his hands up; if he is under us, step off; if it takes too long, leave him
      capT++;
      const c = surr[0], cdx = c.x - p.x;
      inp.mx = Math.abs(cdx) > 3 ? (cdx > 0 ? 1 : -1) : 0;
      if (c.y > p.y + 14 && !p.air && p.plat >= 0 && Math.abs(cdx) < 24) { inp.my = 1; if (dropT <= 0) { jumpHold = 3; dropT = 30; } }
      if (c.y < p.y - 14 && !p.air && Math.abs(cdx) < 60) jumpNow = true;
    } else if (tgt) {
      const dx = tgt.x - p.x, ad = Math.abs(dx), face = dx >= 0 ? 1 : -1;
      const above = tgt.y < p.y - 16;
      if (tgt.id === tgtId) tgtT++; else { tgtId = tgt.id; tgtT = 0; }
      if (tgtT > 200 && ad > 40 && ad < 132 && grenWait <= 0 && p.grenades > 0 && p.face === face) { inp.grenade = true; grenWait = 70; }
      // how steeply would the gun have to point to bear on him?
      const m0 = Sim.muzzle(p), tyy = tgt.y - (tgt.covered ? 27 : tgt.h * 0.56), steep = Math.atan2((p.y - 26) - tyy, Math.max(1, ad)) * 180 / Math.PI;
      if (tgt.k === 'cook' && ad < 70 && Math.abs(tgt.y - p.y) < 20) {
        const cornered = (face > 0 && p.x <= s.cam + 16) || (face < 0 && p.x >= s.cam + s.viewW * (1 - s.laneR) - 10);
        if (tgt.st === 'swingw' && ad < 44) { jumpNow = true; inp.mx = cornered ? face : -face; }
        else if (ad < 56) inp.mx = cornered ? 0 : -face;
        if (!inp.mx && p.face !== face) inp.mx = face;
      } else if (tgt.k === 'door' && Sim.doorTop(tgt) && tgt.face === -face && Math.abs(tgt.y - p.y) < 16) {
        // a door facing us: wear it down from a distance, throw if we have one, and stay out of its reach
        if (ad < 132 && ad > 44 && grenWait <= 0 && p.grenades > 0 && p.face === face) { inp.grenade = true; grenWait = 60; }
        const cornered = (face > 0 && p.x <= s.cam + 16) || (face < 0 && p.x >= s.cam + s.viewW * (1 - s.laneR) - 10);
        if (tgt.st === 'bashw' && ad < 46) { jumpNow = true; inp.mx = cornered ? face : -face; }
        else if (ad < 62) { inp.mx = -face; if (cornered) { inp.mx = face; if (!p.air && ad < 40) { jumpNow = true; jumpHold = 26; } } }
        else if (ad > 124) inp.mx = face;
        else if (p.face !== face) inp.mx = face;
      } else if (Sim.ducked(tgt)) {
        if (ad < 132 && ad > 40 && grenWait <= 0 && p.grenades > 0 && p.face === face) { inp.grenade = true; grenWait = 50; }
        inp.mx = ad > 112 ? face : (ad < 64 ? -face : 0);
        if (!inp.mx && p.face !== face) inp.mx = face;
      } else if (above && !inCone && steep > 27 && steep < 63 && ad > 34) {
        // up and along: the 45 degree shot
        inp.mx = face; inp.my = -1;
      } else if (above && !inCone && steep >= 63 && ad < 30) {
        inp.my = -1;
        if (p.face !== face && ad > 4) inp.mx = face;
      } else if (tgt.y > p.y + 16 && !inCone) {
        // he is below: come down to him
        inp.mx = ad > 10 ? face : 0;
        if (p.air && ad < 30) inp.my = 1;
        if (!p.air && p.plat >= 0 && (ad < 40 || stuckT > 30)) { inp.my = 1; if (dropT <= 0) { jumpHold = 3; dropT = 30; } }      // or the way on is shut: step down to him
      } else if (above && !inCone) {
        // get under a different angle: back off or jump and shoot
        if (ad < 70) inp.mx = -face; else if (ad > 170) inp.mx = face; else if (p.face !== face) inp.mx = face;
        if (!p.air && hop <= 0) { jumpNow = true; hop = 34; }
      } else {
        // is there a wall of sandbags between us? then shooting is wasted: close in and throw, or walk round into it
        let wall = null;
        for (const o of s.props) if (o.k === 'cover' && !o.gone && ((o.x0 > p.x + 6 && o.x0 < tgt.x) || (o.x1 < p.x - 6 && o.x1 > tgt.x)) && Math.abs(p.y - tgt.y) < 14) wall = o;
        if (wall) {
          if (ad < 128 && ad > 40 && grenWait <= 0 && gren > 0 && p.face === face) { inp.grenade = true; grenWait = 50; }
          inp.mx = (ad > 110 || gren <= 0) ? face : 0;
          if (!inp.mx && p.face !== face) inp.mx = face;
        } else {
          const want = tgt.k === 'bomber' ? 110 : 128;
          inp.mx = ad > want + 30 ? face : 0;
          if (!inp.mx && p.face !== face) inp.mx = face;
        }
      }
      if (p.x <= s.cam + 14 && inp.mx < 0) inp.mx = 0;
    } else if (s.car && s.car.st === 'wait' && !foes.length) {
      inp.mx = s.car.x > p.x ? 1 : -1;                    // Salem is waiting
    } else if (loot && !foes.length) {
      inp.mx = Math.abs(loot.x - p.x) > 3 ? (loot.x > p.x ? 1 : -1) : 0;
    } else if (s.holdX != null && s.cam >= s.camMax - 1) {
      // the screen has stopped and nobody is here yet: wait about the middle of it, as a person would
      inp.mx = p.x < s.holdX - 6 ? 1 : (p.x > s.holdX + 40 ? -1 : 0);
    } else {
      inp.mx = 1;
    }
    if (ventStop && inp.mx === ventStop) inp.mx = 0;
    // the Souq: keep out of the chilli, jump the gaps between the roofs and out of one fallen into
    if (s.clouds.length && !flee) {
      for (const c of s.clouds) {
        if (c.str < 0.3) continue;
        const cdx = c.x - p.x;
        if (Math.abs((p.y - 17) - c.y) < c.r + 10 && Math.abs(cdx) < c.r + 16 && Math.sign(cdx) === inp.mx) inp.mx = 0;
      }
    }
    if (L.walls && !p.air && !duck) {
      const pit = L.pits && p.plat < 0 && L.pits.find(q => p.x >= q[0] - 2 && p.x <= q[1] + 2 && p.y > Sim.groundY(L, q[0] - 8) + 20);
      if (pit) {
        // down in a gap: out again, towards wherever we were going (or on, if nowhere)
        const out = inp.mx || (tgt ? Math.sign(tgt.x - p.x) || 1 : 1);
        inp.mx = out; jumpHold = Math.max(jumpHold, 26);
      } else if (inp.mx) {
        const ahead = Sim.groundY(L, p.x + inp.mx * 16);
        if (p.plat < 0 && (ahead > p.y + 7 || ahead < p.y - 7)) jumpHold = Math.max(jumpHold, 26);      // a gap or a step up: over it
      }
    }
    if (hop > 0) hop--;
    if (dropT > 0) dropT--;
    if (!surr.length) capT = 0;
    if (jumpNow && !p.air) jumpHold = Math.max(jumpHold, 14);
    if (jumpHold > 0) { inp.jump = true; jumpHold--; }
    if (noGren) inp.grenade = false;
    // unstick: if nothing has moved for a while with no one to fight, hop
    if (Math.abs(p.x - stuckX) < 1) stuckT++; else { stuckT = 0; stuckX = p.x; }
    if (stuckT > 240 && !foes.length) { inp.mx = 1; inp.jump = (s.tick % 40) < 16; }
    return inp;
  };
}

function run(bot, opts) {
  opts = opts || {};
  let s = Sim.create(opts.level || LEVEL, { viewW: opts.viewW || 468, seed: opts.seed || 1, lanes: opts.lanes, zone: opts.zone || 0 });
  const maxTicks = (opts.seconds || 600) * 60, log = [], evCount = {};
  let prev = { cam: s.cam }, continues = 0, zoneTimes = [0];
  for (let i = 0; i < maxTicks; i++) {
    const inp = bot(s);
    Sim.step(s, inp);
    for (const e of s.events) {
      evCount[e.t] = (evCount[e.t] || 0) + 1;
      if (opts.trace && ['plate_lost', 'life_lost', 'checkpoint', 'go', 'freed', 'capture', 'surrender', 'clear', 'over', 'failsafe', 'pickup', 'weapon_empty', 'boat', 'mount', 'dismount', 'flip', 'strike', 'boss_intro', 'boss_start', 'boss_phase', 'boss_dying', 'boss_dead'].includes(e.t)) log.push((s.time).toFixed(1) + 's ' + e.t + (e.name ? ' ' + e.name : '') + (e.gate ? ' ' + e.gate : '') + (e.k ? ' ' + e.k : '') + ' x=' + Math.round(s.p.x));
      if (e.t === 'checkpoint') zoneTimes.push(s.time);
    }
    if (opts.check !== false) check(s, prev, opts.name || 'run');
    prev = { cam: s.cam };
    if (s.status === 'over') {
      if (!opts.continues || continues >= opts.continues) break;
      continues++;
      s = Sim.continueZone(s);
      prev = { cam: s.cam };
    }
    if (s.status === 'clear' && s.clearT > 60) break;
  }
  return { s, log, evCount, r: Sim.results(s), zoneTimes };
}

function snap(s) { return JSON.stringify([s.tick, s.p.x.toFixed(4), s.p.y.toFixed(4), s.score, s.cam.toFixed(4), s.enemies.map(e => [e.id, e.x.toFixed(3), e.st]), s.bullets.length, s.stats]); }

module.exports = { run, smartBot, runnerBot, fuzzBot, idleBot, check, snap, Sim, LEVEL, MOCHA, ZABID, LEVELS };

if (require.main === module) {
  const line = (name, o) => {
    const r = o.r, s = o.s;
    console.log((name + ':').padEnd(26) + (s.status + (s.status === 'clear' ? '' : ' at x=' + Math.round(s.p.x) + ' zone ' + s.zone)).padEnd(24) +
      ' time ' + r.time.toFixed(1).padStart(6) + 's  score ' + String(r.score).padStart(5) + '  kills ' + String(r.kills).padStart(2) + '  captures ' + r.captures + '  freed ' + r.freed + '/' + r.detainees +
      '  plates lost ' + String(r.plates).padStart(2) + '  lives lost ' + r.deaths + '  continues ' + r.continues + '  accuracy ' + (r.accuracy * 100).toFixed(0) + '%' + (s.failsafe ? '  FAILSAFE x' + s.failsafe : ''));
  };
  const t0 = Date.now();
  const first = run(smartBot(), { trace: true, name: 'smart', continues: 3 });
  console.log(first.log.join('\n'));
  line('smart, hold fire, 468', first);
  line('smart, auto-fire, 468', run(smartBot({ auto: true }), { name: 'smart-auto', continues: 3 }));
  line('smart, hold fire, 384', run(smartBot(), { name: 'smart-384', viewW: 384, continues: 3 }));
  line('smart, auto-fire, 384', run(smartBot({ auto: true }), { name: 'smart-auto-384', viewW: 384, continues: 3 }));
  line('hold right and fire', run(runnerBot(false), { name: 'runner', continues: 0 }));
  line('hold right, auto-fire', run(runnerBot(true), { name: 'runner-auto', continues: 0 }));
  line('stand still', run(idleBot(), { name: 'idle', seconds: 120 }));
  // many games with the careful bot: how hard is it, and what does the damage
  for (const [label, auto, vw] of [['careful bot, hold fire', false, 468], ['careful bot, auto-fire', true, 468], ['careful bot, hold, narrow', false, 384]]) {
    let n = 0, clear = 0, time = 0, plates = 0, deaths = 0, conts = 0, cap = 0, freed = 0, by = {}, slow = 0;
    for (let seed = 1; seed <= 40; seed++) {
      const o = run(smartBot({ auto }), { seed: seed * 11, viewW: vw, continues: 3, seconds: 300 });
      n++;
      if (o.s.status === 'clear') { clear++; time += o.r.time; slow = Math.max(slow, o.r.time); }
      plates += o.r.plates; deaths += o.r.deaths; conts += o.r.continues; cap += o.r.captures; freed += o.r.freed;
      for (const k in o.s.stats.hurtBy) by[k] = (by[k] || 0) + o.s.stats.hurtBy[k];
    }
    console.log(label + ': ' + clear + '/' + n + ' finished, mean ' + (time / Math.max(1, clear)).toFixed(0) + ' s (slowest ' + slow.toFixed(0) + '), per game ' + (plates / n).toFixed(1) + ' plates, ' + (deaths / n).toFixed(1) + ' lives, ' + (conts / n).toFixed(2) + ' continues, ' + (cap / n).toFixed(1) + ' captures, ' + (freed / n).toFixed(1) + ' freed');
    console.log('   hurt by: ' + Object.keys(by).sort((a, b) => by[b] - by[a]).map(k => k + ' ' + (by[k] / n).toFixed(2)).join(', '));
  }
  // the same game twice must be the same game
  const a = run(smartBot(), { seed: 7 }), b = run(smartBot(), { seed: 7 });
  console.log('same seed, same inputs, same game: ' + (snap(a.s) === snap(b.s)));
  // mash
  let n = 0, clears = 0, overs = 0, fails = 0, plates = 0, deaths = 0, conts = 0, time = 0, firstLife = 0;
  for (let seed = 1; seed <= 300; seed++) {
    const o = run(fuzzBot(seed), { seed: seed * 3, seconds: 240, viewW: seed % 2 ? 468 : 384, name: 'fuzz ' + seed, continues: 3 });
    n++;
    if (o.s.status === 'clear') { clears++; time += o.r.time; if (o.r.continues === 0) firstLife++; }
    if (o.s.status === 'over') overs++;
    fails += o.s.failsafe; plates += o.r.plates; deaths += o.r.deaths; conts += o.r.continues;
  }
  console.log('mashing: ' + n + ' games of up to 240 s with random thumbs, every tick checked: no rule broken.');
  console.log('   ' + clears + ' finished (' + firstLife + ' without a continue), ' + overs + ' ran out of continues; per game: ' + (plates / n).toFixed(1) + ' plates lost, ' + (deaths / n).toFixed(1) + ' lives lost, ' + (conts / n).toFixed(2) + ' continues; finishers took ' + (time / Math.max(1, clears)).toFixed(0) + ' s; gate failsafe fired ' + fails + ' times');
  console.log('took ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s');
}
