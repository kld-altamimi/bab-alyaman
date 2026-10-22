// unit_taiz.js - Taiz by Apache (fly.js and the test range, level_taiz.js), checked without a screen:
// the level's own sense (every man on his roof, staged at his fight at every width, nothing starting inside stone),
// rules that must hold every tick (the Apache inside the picture and out of the stone, the camera only going on, the
// counts adding up), a pilot bot that flies the whole range, random thumbs that must break nothing, and the same seed
// giving the same game.
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
let fails = 0;
function ok(c, msg) { if (!c) { fails++; console.log('FAIL ' + msg); } }

// ------------------------------------------------------------------ the level
(function level() {
  const L = TAIZ, s = Sim.create(L, { viewW: WW(468), viewH: VH });
  const rt = X.route(L);
  ok(s.mode === 'fly', 'mode is fly');
  for (let i = 1; i < L.zones.length; i++) ok(L.zones[i].u > L.zones[i - 1].u, 'zones in order ' + i);
  for (let i = 1; i < L.gates.length; i++) ok(L.gates[i].u > L.gates[i - 1].u, 'gates in order ' + L.gates[i].id);
  for (const k in L.groups) { const g = L.groups[k]; if (g.trigU != null) { const gate = L.gates.find(q => q.groups.includes(k)); ok(!gate || g.trigU < gate.u, 'group ' + k + ' wakes before its fight'); } }
  ok(Math.abs(L.gates[L.gates.length - 1].u - rt.len) < 1, 'the last fight is at the end of the route');
  // every platform lies on top of stone
  // (a roof's stair-head stands on it: stone over that end of the roof is the stair-head)
  const stair = (x, y) => L.fly.doors.some(d => d.kind === 'roof' && x >= d.x0 && x <= d.x1 && Math.abs(y - d.y) < 3);
  for (const pl of L.plats) for (const q of pl.pts) ok(X.rockAt(L, q[0], q[1] + 1.5) && (stair(q[0], q[1]) || !X.rockAt(L, q[0], q[1] - 1.5)), 'platform ' + pl.id + ' on stone at ' + q);
  // every man stands on his platform, and is staged at his fight at both widths (posted men must be able to fight)
  for (const q of L.fly.spawns) {
    if (q.k === 'drone' || q.k === 'truck' || q.k === 'launcher') continue;       // (they come in, drive along with the camera, or roll out of the keep)
    // (on a platform, or with none, on the ground: the street, the road)
    const pi = q.plat ? L.plats.findIndex(p => p.id === q.plat) : -1, y = q.win ? q.win[1] : (q.plat ? (pi >= 0 ? Sim.platY(L.plats[pi], q.x) : null) : Sim.groundY(L, q.x));
    ok((pi >= 0 || !q.plat) && y !== null, 'spawn ' + q.g + ' ' + q.k + ' x=' + q.x + ' on ' + (q.plat || 'the ground'));
    // (a door he comes out of is one the stage has; a hatch or a run along starts on his platform or the ground)
    if (q.from && q.from.indexOf('door:') === 0) ok(L.fly.doors.some(d => d.id === q.from.slice(5)), 'spawn ' + q.g + ' door ' + q.from);
    const gate = L.gates.find(g => g.groups.includes(q.g));
    for (const vw of [WW(384), WW(468)]) for (const lanes of [[0.18, 0.25], [0.07, 0.09]]) {
      const c = X.at(rt, gate.u), cam = c.x - vw / 2, camY = c.y - VH / 2, h = Sim.KIND[q.k].h, cy = y - h / 2;
      const inX = q.x >= cam + vw * lanes[0] - 6 && q.x <= cam + vw * (1 - lanes[1]) + 6, inY = cy >= camY + 12 && cy <= camY + VH - 12;
      ok(inX && inY, 'spawn ' + q.g + ' ' + q.k + ' x=' + q.x + ' staged at ' + gate.id + ' (width ' + vw + ', lanes ' + lanes + ')');
      // (the gun does not point up: the Apache must be able to get above him, the top of the picture letting it)
      ok(cy >= camY + F.EDGE_T + F.GUN_AT[1] + 6, 'spawn ' + q.g + ' ' + q.k + ' x=' + q.x + ' can be shot from above at ' + gate.id);
    }
  }
  // each checkpoint's Apache starts in the open
  for (let z = 0; z < L.zones.length; z++) {
    const sz = Sim.create(L, { viewW: WW(384), viewH: VH, zone: z }), h = sz.heli;
    let clear = true;
    for (const [dx, dy] of [[-F.HW, 0], [F.HW, 0], [0, F.HB], [0, -F.HT]]) if (X.rockAt(L, h.x + dx, h.y + dy)) clear = false;
    ok(clear || z === 0, 'zone ' + z + ' starts in the open at ' + h.x.toFixed(0) + ',' + h.y.toFixed(0));
  }
  console.log('route ' + rt.len.toFixed(0) + ' px; zones at u = ' + L.zones.map(z => z.u.toFixed(0)).join(', ') + '; fights at u = ' + L.gates.map(g => g.id + ' ' + g.u.toFixed(0)).join(', '));
  // the three tied up on the roofs (22 Oct): each on his roof, in his zone, in the open, and at one of the fights (where the
  // camera holds) in the picture at every width, with room above him for the Apache to come down over him
  const caps = L.props.filter(q => q.k === 'detainee');
  ok(caps.length === 3 && s.stats.detainees === 3, 'three tied up on the roofs (' + caps.length + ')');
  for (const q of caps) {
    const pi = L.plats.findIndex(p => p.id === q.plat), y = pi >= 0 ? Sim.platY(L.plats[pi], q.x) : null;
    ok(y !== null, 'captive x=' + q.x + ' on his roof ' + q.plat);
    if (y === null) continue;
    const z = L.zones.reduce((a, zz, i) => (zz.u <= X.uOf(rt, q.x, y) ? i : a), 0);
    ok(z === q.zone, 'captive x=' + q.x + ' in zone ' + q.zone + ' (by the route: ' + z + ')');
    let sky = true;
    for (let dy = 6; dy <= F.HANDS + F.RESCUE_UP; dy += 4) for (const dx of [-12, 0, 12]) if (X.rockAt(L, q.x + dx, y - dy)) sky = false;
    ok(sky, 'captive x=' + q.x + ': open sky over him');
    for (const vw of [WW(384), WW(468)]) {
      // (where the camera may be: from where it first shows him, at every step along the route, to where he is gone again)
      const seen = (u) => { const c = X.at(rt, u), cam = c.x - vw / 2, camY = c.y - VH / 2; return { cam, camY, in: q.x >= cam + 12 && q.x <= cam + vw - 12 && y - 50 >= camY + 10 && y <= camY + VH - 20 }; };
      const hx = q.x - F.ROPE_AT[0], hy = y - F.HANDS - 40 - F.ROPE_AT[1];
      let fine = 0, shown = 0;
      for (let u = 0; u <= rt.len; u += 8) {
        const v = seen(u);
        if (!v.in) continue;
        shown++;
        // (well in the picture, clear of the thumbs, and the Apache able to be over him there)
        if (q.x >= v.cam + vw * 0.2 && q.x <= v.cam + vw * 0.8 && hx >= v.cam + F.EDGE_X && hx <= v.cam + vw - F.EDGE_X && hy >= v.camY + F.EDGE_T && hy <= v.camY + VH - F.EDGE_B &&
            ![[-F.HW, 0], [F.HW, 0], [0, F.HB], [0, -F.HT]].some(([dx, dy]) => X.rockAt(L, hx + dx, hy + dy))) fine++;
      }
      const gate = L.gates.find(g => seen(g.u).in);
      ok(gate && fine * 8 >= 120, 'captive x=' + q.x + ' (width ' + vw + '): in the picture at fight ' + (gate && gate.id) + ', and reachable from the air over ' + fine * 8 + ' px of the way');
    }
  }
})();

// ------------------------------------------------------------------ the people tied up on the roofs
(function captives() {
  const L = TAIZ, vw = WW(468), rt = X.route(L);
  // the Apache put over him (and kept from harm: this is about the rope), at the fight where he is in the picture
  const over = (z, dx, up) => {
    const s = Sim.create(L, { viewW: vw, viewH: VH, zone: z, seed: 3, stats: z === 0 ? { kills: 0, captures: 0, freed: 0, detainees: 0, shots: 0, hits: 0, plates: 0, deaths: 0, continues: 0, grenades: 0, streakBest: 0, hurtBy: {}, rescued: [] } : undefined });
    s.heli.st = 'fly'; s.p.inv = 1e9;
    const o = s.props.find(q => q.k === 'detainee' && q.st === 'tied');
    let best = null;
    for (const g of L.gates) { const c = X.at(rt, g.u); if (o.x > c.x - vw * 0.3 && o.x < c.x + vw * 0.3 && (!best || Math.abs(c.x - o.x) < Math.abs(X.at(rt, best.u).x - o.x))) best = g; }
    s.u = best.u; Sim.step(s, { viewW: vw, viewH: VH });
    const h = s.heli; h.x = o.x - F.ROPE_AT[0] + dx; h.y = o.y - F.HANDS - up - F.ROPE_AT[1]; h.vx = h.vy = 0; h.tilt = 0;
    return { s, o };
  };
  const hold = (s, n) => { const ev = []; for (let t = 0; t < n; t++) { Sim.step(s, { viewW: vw, viewH: VH }); for (const e of s.events) ev.push(e); } return ev; };
  for (const z of [0, 1, 2]) {
    const { s, o } = over(z, 0, 50), r0 = s.p.grenades, sc0 = s.score;
    const ev = hold(s, F.RESCUE_T + 4);
    ok(o.st === 'lift' && s.stats.freed === 1 && s.p.grenades === r0 + F.RESCUE_ROCKETS && s.score - sc0 >= 500, 'zone ' + z + ': held over him, he takes the rope (' + o.st + ', freed ' + s.stats.freed + ', rockets ' + r0 + ' -> ' + s.p.grenades + ')');
    ok(ev.some(e => e.t === 'freed') && ev.some(e => e.t === 'pickup' && e.k === 'rockets') && ev.some(e => e.t === 'rope_down'), 'zone ' + z + ': the rope going down, him freed, five rockets');
    hold(s, F.LIFT_T + 2);
    ok(o.gone && o.st === 'aboard', 'zone ' + z + ': and up it into the Apache');
  }
  // only over him: off to the side, or too high, nothing; held over him a while and away, the rope goes back up
  { const { s, o } = over(0, F.RESCUE_DX + 14, 50); hold(s, 120); ok(o.st === 'tied' && !o.rope, 'off to the side: no rope'); }
  { const { s, o } = over(0, 0, F.RESCUE_UP + 30); hold(s, 120); ok(o.st === 'tied' && !o.rope, 'too high over him: no rope'); }
  { const { s, o } = over(0, 0, 50); hold(s, F.RESCUE_T >> 1); const r = o.rope; s.heli.x += 120; hold(s, F.RESCUE_T); ok(r > 0.4 && o.st === 'tied' && o.rope === 0, 'over him a while, then off: the rope back up (' + r.toFixed(2) + ' -> ' + o.rope + ')'); }
  // a continue: whoever was freed before it is not there to be freed again
  {
    const { s, o } = over(0, 0, 50); hold(s, F.RESCUE_T + F.LIFT_T + 6);
    s.status = 'over';
    const c = Sim.continueZone(s, vw);
    ok(c.stats.freed === 1 && !c.props.some(q => q.k === 'detainee' && q.px === o.px), 'after a continue he is not tied up there again (freed ' + c.stats.freed + ')');
  }
  // all three: the Liberator; fewer: not
  {
    const st = { kills: 0, captures: 0, freed: 0, detainees: 0, shots: 0, hits: 0, plates: 0, deaths: 0, continues: 0, grenades: 0, streakBest: 0, hurtBy: {}, rescued: [] };
    let last = null;
    for (const z of [0, 1, 2]) {
      const s = Sim.create(L, { viewW: vw, viewH: VH, zone: z, seed: 3, stats: st });
      s.heli.st = 'fly'; s.p.inv = 1e9;
      const o = s.props.find(q => q.k === 'detainee' && q.st === 'tied' && q.px > (z ? L.props[z - 1].x : 0));
      s.u = X.uOf(rt, o.x, o.y); Sim.step(s, { viewW: vw, viewH: VH });
      s.heli.x = o.x - F.ROPE_AT[0]; s.heli.y = o.y - F.HANDS - 50 - F.ROPE_AT[1];
      if (z === 1) ok(!Sim.results(s).liberator, 'one of three: no Liberator');
      hold(s, F.RESCUE_T + 4);
      last = s;
    }
    ok(last.stats.freed === 3 && Sim.results(last).liberator, 'all three: the Liberator (' + last.stats.freed + ' of ' + last.stats.detainees + ')');
  }
})();

// ------------------------------------------------------------------ the opening, on foot
(function opening() {
  const L = TAIZ, FULL = [WW(468), VH], OP = Sim.OP;
  const mk = () => Sim.create(L, { viewW: FULL[0], viewH: FULL[1], seed: 7 });
  const step = (s, inp) => { inp = Object.assign({ viewW: s.viewW, viewH: s.viewH }, inp || {}); Sim.step(s, inp); };
  // left alone: the Apache comes in, the five run, it lands and waits for him (on foot, at the usual size)
  let s = mk();
  ok(s.intro && s.zoom === 1 && s.viewW === Math.round(FULL[0] / ZM) && s.yaz, 'a fresh start opens on foot at the usual size (' + s.viewW + 'x' + s.viewH + ')');
  ok(s.enemies.filter(e => e.intro && e.alive).length === L.fly.intro.men.length, 'five of them across the street');
  for (let t = 0; t < OP.LANDED + 120; t++) step(s, {});
  ok(s.intro && s.intro.st === 'wait' && s.heli.st === 'landed', 'it lands and waits (' + (s.intro && s.intro.st) + ')');
  ok(s.enemies.every(e => !e.intro || !e.alive) && s.groups.Z0.hostile === 0, 'and the five are gone through the doors');
  ok(s.viewW === Math.round(FULL[0] / ZM) && s.cam === 0, 'still on foot at the usual size, the camera on the street');
  // a button in the first part goes straight to the landing
  s = mk();
  for (let t = 0; t < 20; t++) step(s, {});
  step(s, { fire: true });
  ok(s.intro.st === 'wait' && s.enemies.every(e => !e.intro || !e.alive), 'a button skips to the Apache waiting in the street');
  // walked to (the arrow held): he climbs in, it lifts off, the picture draws back, and the mission is on
  let seen = { board: 0, lift: 0, zoom: 0 }, zs = [];
  for (let t = 0; t < 900 && s.intro; t++) { step(s, { mx: 1 }); if (s.intro) { seen[s.intro.st] = 1; if (s.intro.st === 'zoom') zs.push(s.zoom); } }
  ok(!s.intro && s.heli.st === 'fly' && s.zoom === ZM && s.viewW === FULL[0] && s.viewH === FULL[1] && s.u < 3, 'walked to, it takes him and lifts off, and the picture is the Apache\'s (' + s.viewW + 'x' + s.viewH + ', zoom ' + s.zoom + ')');
  ok(seen.board && seen.lift && seen.zoom && zs.every((z, i) => i === 0 || z >= zs[i - 1]) && zs[0] < 1.05, 'boarding, lift-off, and the zoom drawing back smoothly (' + zs.length + ' steps)');
  const h = s.heli;
  ok(![[-F.HW, 0], [F.HW, 0], [0, F.HB], [0, -F.HT]].some(([dx, dy]) => X.rockAt(L, h.x + dx, h.y + dy)) && X.inView(s, h.x, h.y, -20), 'and the Apache starts in the open, in the picture');
  // the way up, shown (Khaled, 21 Oct: "after lift off, its not clear that I need to go upward, maybe have the camera guide
  // me there"): left alone, the camera goes on up the route by itself to where it levels out over the roofs, the way-up
  // sign with it; the Apache kept in the picture, out of the stone
  {
    const G = L.fly.guide, u0 = s.u, cy0 = s.camY;
    let bad = [], t = 0;
    for (; t < 600 && s.guide; t++) {
      const pr = { u: s.u };
      step(s, {});
      try { check(s, pr, 'guide'); } catch (err) { bad.push(err.message); }
    }
    ok(G && !s.guide && Math.abs(s.u - G.u) < 2 && t > 200 && t < 420, 'the camera leads the way up to the roofs by itself (u ' + u0.toFixed(0) + ' -> ' + s.u.toFixed(0) + ' of ' + (G && G.u.toFixed(0)) + ' in ' + (t / 60).toFixed(1) + ' s, the picture ' + (cy0 - s.camY).toFixed(0) + ' px up)');
    ok(bad.length === 0, 'the Apache, left alone, kept in the picture and out of the stone meanwhile' + (bad.length ? ': ' + bad.slice(0, 3).join('; ') : ''));
    for (let k = 0; k < 120; k++) step(s, {});
    ok(Math.abs(s.u - G.u) < 2, 'and there it waits for the Apache (u ' + s.u.toFixed(0) + ')');
  }
  // a continue from the start does not play it again
  const c = Sim.continueZone(s, FULL[0]);
  ok(!c.intro && c.heli.st === 'in', 'a continue from the first checkpoint comes in flying');
})();

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

// the pilot, at both widths and with both lane settings
for (const [vw, lanes, seed, stick] of [[WW(468), [0.18, 0.25], 1, true], [WW(384), [0.18, 0.25], 2, true], [WW(449), [0.07, 0.09], 3, false], [WW(468), [0.07, 0.09], 5, false]]) {
  const o = run(pilot({ stick }), { viewW: vw, lanes, seed, seconds: 600, continues: 3, log: true, name: 'pilot ' + vw });
  const st = o.s.stats;
  console.log('pilot ' + vw + (stick ? ' (aim stick)' : ' (FIRE held)') + ': ' + o.s.status + ' at ' + o.s.time.toFixed(1) + 's, zone ' + o.s.zone + ', score ' + o.s.score + ', kills ' + st.kills + ', scattered ' + o.s.scattered +
              ', deaths ' + st.deaths + ', continues ' + o.conts + ', plates lost ' + st.plates + ' ' + JSON.stringify(st.hurtBy) + ', rockets ' + st.grenades + ', failsafe ' + o.s.failsafe + ', missiles ' + o.launches + ' (' + o.decoys + ' to flares, ' + o.shotDown + ' shot down)' +
              ', freed ' + st.freed + ' of ' + st.detainees + (Sim.results(o.s).liberator ? ' (Liberator)' : ''));
  if (vw === WW(468) && stick) console.log('  ' + o.log.join('\n  '));
  ok(o.s.status === 'clear', 'pilot ' + vw + ' clears the range');
  ok(st.freed === 3, 'pilot ' + vw + ' lifts all three off the roofs (' + st.freed + ')');
}
// left on the roofs: no Liberator, and the results say somebody is still waiting on a roof
{
  const o = run(pilot({ stick: true, noRescue: true }), { viewW: WW(468), seed: 6, seconds: 600, continues: 3 });
  ok(o.s.status === 'clear' && o.s.stats.freed < 3 && !Sim.results(o.s).liberator, 'not going for them: not all three lifted out by chance, no Liberator (' + o.s.status + ', freed ' + o.s.stats.freed + ')');
  console.log('pilot leaving them: ' + o.s.status + ' at ' + o.s.time.toFixed(1) + 's, freed ' + o.s.stats.freed + ' of ' + o.s.stats.detainees);
}
// no flares, and no dodging: the missiles and the drones must matter
for (const o2 of [{ noFlares: true }, { noFlares: true, stick: true }, { lateFlares: true, stick: true }, { noDodge: true }, { noFlares: true, noDodge: true }]) {
  const o = run(pilot(o2), { viewW: WW(468), seed: 4, seconds: 600, continues: 5 });
  console.log('pilot ' + JSON.stringify(o2) + ': ' + o.s.status + ' at ' + o.s.time.toFixed(0) + 's, zone ' + o.s.zone + ', deaths ' + o.s.stats.deaths + ' ' + JSON.stringify(o.s.stats.hurtBy) + ', missiles ' + o.launches + ' (' + o.decoys + ' to flares, ' + o.shotDown + ' shot down)');
}
// random thumbs: nothing breaks
for (let k = 0; k < 6; k++) { const o = run(fuzz(100 + k), { viewW: WW([384, 468, 420][k % 3]), seed: 50 + k, seconds: 180, continues: 2, name: 'fuzz ' + k }); }
console.log('fuzz: 6 x 3 minutes, no rule broken');
// the same seed, the same game
{
  const a = run(pilot({ stick: true }), { viewW: WW(468), seed: 9, seconds: 200 }), b = run(pilot({ stick: true }), { viewW: WW(468), seed: 9, seconds: 200 });
  ok(hashOf(a.s) === hashOf(b.s), 'same seed, same game');
}
console.log(fails ? fails + ' FAILED' : 'unit_taiz: all passed');
process.exit(fails ? 1 : 0);
