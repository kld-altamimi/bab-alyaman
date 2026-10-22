// cg_test.js - the Castle Gun's three attacks (flak, sweep, barrage), each forced from a grid of places the Apache could be
// in the bastion fight: from how many of them can it be dodged at all, after a reaction time?
'use strict';
const { make, copy, pilot, step, X, F, BG, Sim } = require('./lib.js');
const { search } = require('./oracle.js');
const W = +process.argv[2] || 702, REACT = +(process.argv[3] || 12), ONLY = process.argv[4] || '';
// into the fight: the pilot flies from the castle checkpoint until the gun is up and tracking
let s = make({ zone: 3, viewW: W, seed: 3 });
const bot = pilot();
for (let t = 0; t < 60 * 200; t++) { const inp = bot(s); step(s, inp); const g = s.enemies.find(e => e.k === 'cgun' && e.alive); if (g && g.st === 'track' && !g.hidden) break; }
const g0 = s.enemies.find(e => e.k === 'cgun');
console.log('view', W, 'x', s.viewH, '| the gun at', Math.round(g0.x), Math.round(g0.y), '| camera', Math.round(s.cam), Math.round(s.camY), '| heli', Math.round(s.heli.x), Math.round(s.heli.y));
s.enemies = s.enemies.filter(e => e.k !== 'drone');
const freeze = c => { const g = c.enemies.find(e => e.k === 'cgun' && e.alive); if (g && g.st === 'track') g.stT = 0; c.enemies.forEach(e => { if (e.k !== 'cgun' && e.k !== 'drone') e.stT = 0; }); };
const ATT = { flak: { horizon: 90, hp: 140 }, sweep: { horizon: 170, hp: 140 }, barrage: { horizon: 110, hp: 30 } };
const out = {};
for (const a of Object.keys(ATT)) {
  if (ONLY && a !== ONLY) continue;
  const res = [];
  for (let y = s.camY + F.EDGE_T + 10; y <= s.camY + s.viewH - F.EDGE_B - 10; y += 36)
    for (let x = s.cam + F.EDGE_X + 10; x <= s.cam + s.viewW - F.EDGE_X - 10; x += 56) {
      const c = copy(s), h = c.heli;
      if (X.rockAt(c.L, x, y) || X.rockAt(c.L, x - F.HW, y) || X.rockAt(c.L, x + F.HW, y) || X.rockAt(c.L, x, y + F.HB)) continue;
      h.x = x; h.y = y; h.vx = 0; h.vy = 0;
      const g = c.enemies.find(e => e.k === 'cgun');
      g.hp = ATT[a].hp; g.phase = a === 'barrage' ? 3 : 1; g.plan = []; g.st = a; g.stT = 0; g.shots = 0;
      if (a === 'sweep') Sim.cgSweepPlan(g, h);
      const r = search(c, { k: 'cgun', react: REACT, horizon: ATT[a].horizon, D: 6, width: +(process.env.BEAM || 200), after: freeze });
      res.push({ x: Math.round(x - g.x), y: Math.round(y - g.y), hits: r.hits });
    }
  const ok = res.filter(r => r.hits === 0).length;
  out[a] = { places: res.length, dodgeable: ok, share: Math.round(100 * ok / res.length) + '%' };
  console.log(a + ': dodgeable from ' + ok + ' of ' + res.length + ' places (reaction ' + REACT + ' ticks)');
  // a map, the gun at the bottom middle: '.' dodgeable, 'X' not
  const ys = [...new Set(res.map(r => r.y))].sort((p, q) => p - q), xs = [...new Set(res.map(r => r.x))].sort((p, q) => p - q);
  for (const yy of ys) console.log('   ' + String(yy).padStart(5) + ' ' + xs.map(xx => { const r = res.find(q => q.x === xx && q.y === yy); return r ? (r.hits === 0 ? '.' : 'X') : ' '; }).join(' '));
  console.log('         ' + xs.map(xx => (Math.abs(xx) < 28 ? '^' : ' ')).join(' ') + '   (^ = over the gun)');
}
require('fs').writeFileSync(__dirname + '/cg2_' + W + '_' + REACT + '_' + (ONLY || 'all') + '.json', JSON.stringify(out));
