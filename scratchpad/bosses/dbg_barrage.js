'use strict';
const { make, copy, pilot, step, X, F, BG } = require('./lib.js');
const { search } = require('./oracle.js');
let s = make({ zone: 3, viewW: 702, seed: 3 }); const bot = pilot();
for (let t = 0; t < 60 * 200; t++) { step(s, bot(s)); const g = s.enemies.find(e => e.k === 'cgun' && e.alive); if (g && g.st === 'track' && !g.hidden) break; }
s.enemies = s.enemies.filter(e => e.k !== 'drone');
const freeze = c => { const g = c.enemies.find(e => e.k === 'cgun' && e.alive); if (g && g.st === 'track') g.stT = 0; c.enemies.forEach(e => { if (e.k !== 'cgun' && e.k !== 'drone') e.stT = 0; }); };
for (const [x, y] of [[6864, 256], [6864, 148], [6808, 292]]) for (const react of [0, 15]) {
  const c = copy(s), h = c.heli; h.x = x; h.y = y; h.vx = 0; h.vy = 0;
  const g = c.enemies.find(e => e.k === 'cgun'); g.hp = 30; g.phase = 3; g.plan = []; g.st = 'barrage'; g.stT = 0;
  const r = search(c, { k: 'cgun', react, horizon: 110, D: 6, width: 300, after: freeze, maxHits: 1 });
  // where the shells will burst
  const c2 = copy(c); step(c2, { ax: 0, ay: 0 }); step(c2, { ax: 0, ay: 0 }); step(c2, { ax: 0, ay: 0 });
  console.log('at', x, y, 'react', react, '-> fewest hits', r.hits, 'ends at', r.at, '| bursts', c2.shells.filter(q => q.kind === 'flak').map(q => [Math.round(q.tx - x), Math.round(q.ty - y), q.fuse]).join(' '), '| rock right?', [1, 2, 3, 4].map(k => X.rockAt(c.L, x + F.HW + 20 * k, y) ? 1 : 0).join(''));
}
