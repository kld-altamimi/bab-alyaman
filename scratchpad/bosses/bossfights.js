// bossfights.js - the pilot bot through the castle (from its checkpoint) on several seeds and widths: how long each boss
// fight lasts, and what hurts the Apache during it
'use strict';
const { make, pilot, step } = require('./lib.js');
const rows = [];
for (const W of [576, 702, 780]) for (let seed = 1; seed <= 6; seed++) {
  let s = make({ zone: 3, viewW: W, seed }); const bot = pilot();
  let fight = null, t0 = 0, hurt0 = {}; const per = {};
  for (let t = 0; t < 60 * 400; t++) {
    step(s, bot(s));
    for (const e of s.events) {
      if (e.t === 'boss_intro') { fight = e.k; t0 = t; hurt0 = Object.assign({}, s.stats.hurtBy); }
      if (e.t === 'boss_dead' && fight) {
        const d = {}; for (const k in s.stats.hurtBy) { const n = s.stats.hurtBy[k] - (hurt0[k] || 0); if (n) d[k] = n; }
        per[fight] = { secs: +((t - t0) / 60).toFixed(1), hurt: d }; fight = null;
      }
    }
    if (s.status === 'over') { per.over = fight || 'before'; break; }
    if (s.status === 'clear') break;
  }
  rows.push({ W, seed, per });
}
for (const r of rows) console.log(r.W, r.seed, JSON.stringify(r.per));
