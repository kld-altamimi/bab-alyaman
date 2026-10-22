// launcher_bot.js - the pilot bot against the timed Launcher (from the keep's checkpoint) and the castle (from its own):
// how long each boss fight lasts, what hurts the Apache, how much of the clock is left when the Launcher goes
'use strict';
delete require.cache[require.resolve('./lib.js')];
const { make, pilot, step, BG } = require('./lib.js');
const zone = +(process.argv[2] || 4), rows = [];
for (const W of [576, 702, 780]) for (let seed = 1; seed <= 5; seed++) {
  let s = make({ zone, viewW: W, seed }); const bot = pilot();
  let fight = null, t0 = 0, hurt0 = {}; const per = {}; let left = null;
  for (let t = 0; t < 60 * 400; t++) {
    step(s, bot(s));
    const L = s.enemies.find(e => e.k === 'launcher' && e.alive);
    if (L && L.clock != null) left = L.clock;
    for (const e of s.events) {
      if (e.t === 'boss_intro') { fight = e.k; t0 = t; hurt0 = Object.assign({}, s.stats.hurtBy); }
      if (e.t === 'boss_dead' && fight) {
        const d = {}; for (const k in s.stats.hurtBy) { const n = s.stats.hurtBy[k] - (hurt0[k] || 0); if (n) d[k] = n; }
        per[fight] = { secs: +((t - t0) / 60).toFixed(1), hurt: d }; if (fight === 'launcher') per[fight].clockLeft = +(left / 60).toFixed(1); fight = null;
      }
      if (e.t === 'got_away') per.got_away = true;
      if (e.t === 'recount') per.recount = true;
    }
    if (s.status === 'over') { per.over = fight || 'after'; break; }
    if (s.status === 'clear' || s.ending) break;
  }
  rows.push({ W, seed, per });
}
for (const r of rows) console.log(r.W, r.seed, JSON.stringify(r.per));
