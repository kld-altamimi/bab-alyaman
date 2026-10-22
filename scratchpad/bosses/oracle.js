// oracle.js - can a boss attack be dodged at all? From a game state at the moment an attack starts, search the stick
// (9 directions, re-chosen every D ticks) for a way through the attack with no hit from the boss, after a reaction time
// in which the Apache keeps doing what it was doing. Other enemies' shots are taken out, so only the boss counts.
'use strict';
const { copy, step, F } = require('./lib.js');
const DIRS = []; for (let ax = -1; ax <= 1; ax++) for (let ay = -1; ay <= 1; ay++) DIRS.push({ ax, ay });
const BOSS_CAUSES = { cgun: ['castle gun', 'flak', 'drone'], launcher: ['launcher', 'launcher gun', 'launcher missile'] };
function hitsBy(s, causes) { let n = 0; for (const c of causes) n += s.stats.hurtBy[c] || 0; return n; }
function isolate(s, boss) {
  // only the boss's own fire stays in the air: its heavy rounds and flak, its drones' dives, its missile and gun
  s.bullets = s.bullets.filter(b => b.own || b.src === 'castle gun' || b.src === 'launcher gun');
  s.missiles = s.missiles.filter(q => q.from === boss.id);
  if (s.shells) s.shells = s.shells.filter(q => q.from === boss.id);
}
function prep(s0) { const s = copy(s0); s.p.plates = 99; s.p.inv = 0; return s; }
// search: returns { hits: the fewest hits from the boss over the horizon, path }
function search(s0, o) {
  const boss = s0.enemies.find(e => e.k === o.k && e.alive), causes = BOSS_CAUSES[o.k];
  let s = prep(s0); const base = hitsBy(s, causes);
  const hold = Object.assign({}, o.holdInput || { ax: 0, ay: 0 }, { fire: false, gun: false, grenade: false, jump: false });
  for (let t = 0; t < o.react; t++) { step(s, Object.assign({}, hold)); isolate(s, boss); if (o.after) o.after(s); }
  let beam = [{ s, hits: hitsBy(s, causes) - base, path: [] }];
  const steps = Math.ceil((o.horizon - o.react) / o.D);
  for (let k = 0; k < steps; k++) {
    const next = new Map();
    for (const b of beam) for (const d of DIRS) {
      if (o.noJumpOpts === false) {}
      const c = copy(b.s);
      for (let t = 0; t < o.D; t++) { step(c, { ax: d.ax, ay: d.ay, fire: false, gun: false, grenade: false, jump: !!(o.flares && d.ax === 0 && d.ay === 0 && k === 0) }); isolate(c, boss); if (o.after) o.after(c); }
      const hits = hitsBy(c, causes) - base;
      if (hits > (o.maxHits || 0)) continue;
      const h = c.heli, key = Math.round(h.x / 6) + ',' + Math.round(h.y / 6) + ',' + Math.round(h.vx / 45) + ',' + Math.round(h.vy / 45) + ',' + hits;
      const old = next.get(key);
      if (!old || old.hits > hits) next.set(key, { s: c, hits, path: b.path.concat([d.ax + ',' + d.ay]) });
    }
    beam = [...next.values()];
    if (!beam.length) return { hits: Infinity, steps: k };
    beam.sort((a, b) => a.hits - b.hits);
    if (beam.length > o.width) { // keep a spread: the fewest hits first, then spread out over the picture
      const keep = [], seen = new Set();
      for (const b of beam) { const g = Math.round(b.s.heli.x / 24) + ',' + Math.round(b.s.heli.y / 24) + ',' + b.hits; if (!seen.has(g)) { seen.add(g); keep.push(b); } }
      for (const b of beam) { if (keep.length >= o.width) break; if (!keep.includes(b)) keep.push(b); }
      beam = keep.slice(0, o.width);
    }
  }
  const best = beam[0];
  return { hits: best.hits, path: best.path, at: [Math.round(best.s.heli.x), Math.round(best.s.heli.y)] };
}
module.exports = { search, isolate, hitsBy, BOSS_CAUSES };
