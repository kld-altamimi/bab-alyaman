// dump_layout.js - Taiz's layout for the map page, from the level itself: the route, the checkpoints, the fights (gates)
// and who is in each, every enemy where he stands (or where he comes in), the solid stone, the houses that are only
// scenery, the doors, the bosses and the landing. World pixels, the same as the captured pictures.
// Usage: node dump_layout.js <game dir> <out.json>
'use strict';
const path = require('path');
const fs = require('fs');
const G = process.argv[2], OUT = process.argv[3];
const Sim = require(path.join(G, 'src/sim.js'));
for (const f of ['drive', 'boss', 'roaster', 'tailor', 'fly']) { try { require(path.join(G, 'src', f + '.js')); } catch (e) { if (f !== 'tailor') throw e; } }
const L = require(path.join(G, 'src/level_taiz.js'));
const ST = require(path.join(G, 'gen/stage_taiz.json'));
const W = L.width, H = L.height;

const groundY = (x) => { const g = ST.ground; const i = Math.max(0, Math.min(g.y.length - 1, Math.floor(x / g.step))); return g.y[i]; };
const along = (pts, x) => {
  for (let i = 0; i + 1 < pts.length; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
    if (x >= x0 && x <= x1) return y0 + (y1 - y0) * ((x - x0) / Math.max(1, x1 - x0));
  }
  return pts[pts.length - 1][1];
};
const plat = (id) => (L.plats || []).find((p) => p.id === id);
const doorById = (id) => L.fly.doors.find((d) => d.id === id);
const gateOf = (g) => L.gates.find((gt) => gt.groups.indexOf(g) >= 0);

const spawns = L.fly.spawns.map((s) => {
  let x = s.x, y = null, how = '';
  if (s.plat && plat(s.plat)) { y = plat(s.plat).pts[0][1]; how = 'roof'; }
  if (s.win) { x = s.win[0]; y = s.win[1]; how = 'window'; }
  if (typeof s.from === 'string' && s.from.indexOf('door:') === 0) { const d = doorById(s.from.slice(5)); if (d) { x = x != null ? x : d.x; y = d.y; how = 'door'; } }
  else if (s.from === 'hatch') how = 'hatch';
  const gt = gateOf(s.g);
  if (s.k === 'truck') { y = along(ST.road, x); how = 'road'; }
  if (s.k === 'drone') { x = gt ? gt.at[0] + 60 : 0; y = gt ? gt.at[1] - 90 : 0; how = 'flies in'; }
  if (s.k === 'launcher') { y = ST.world.TOP; how = 'rolls out of the keep'; }
  if (x == null) x = gt ? gt.at[0] : 0;
  if (y == null) y = groundY(x);
  return { k: s.k, x: Math.round(x), y: Math.round(y), g: s.g, gate: gt ? gt.id : null, n: s.n || 1, how: how };
});

const gates = L.gates.map((g) => {
  const counts = {};
  spawns.filter((s) => s.gate === g.id).forEach((s) => { counts[s.k] = (counts[s.k] || 0) + (s.n || 1); });
  return { id: g.id, x: g.at[0], y: g.at[1], groups: g.groups, counts: counts };
});

const piece = (name) => { const pl = ST.place.find((p) => p.p === name), r = ST.pieces[name]; return pl && r ? { name: name, x: pl.x, y: pl.y, w: r[2], h: r[3] } : null; };
const out = {
  W, H,
  zones: L.zones.map((z, i) => ({ i, name: z.name, x: z.at[0], y: z.at[1] })),
  route: L.fly.route,
  gates,
  spawns,
  rock: L.fly.rock,
  scenery: (L.fly.scenery || []).map(piece).filter(Boolean),
  doors: L.fly.doors.map((d) => ({ x: d.x, y: d.y, kind: d.kind })),
  landing: L.fly.landing,
  bridge: ST.info && ST.info.bridge,
  souq: ST.world.SOUQ
};
fs.writeFileSync(OUT, JSON.stringify(out));
const kinds = {}; spawns.forEach((s) => { kinds[s.k] = (kinds[s.k] || 0) + s.n; });
console.log('layout:', spawns.length, 'spawn lines', JSON.stringify(kinds), gates.length, 'fights', out.rock.length, 'stone shapes', fs.statSync(OUT).size, 'bytes');
