// effect.js - the same seeded bot runs of the Strait and the Coffee Port, printed as one JSON line of totals:
// clears, game overs, continues, lives lost, refills seen, and the zone each run ended in. Run once on the sources before
// the refill and once after, then compare. Usage: node effect.js <tools dir> <label>
'use strict';
const path = require('path');
const B = require(path.join(process.argv[2], 'bot.js'));
const label = process.argv[3] || '';
const out = {};
for (const [name, level] of [['strait', undefined], ['mocha', B.MOCHA]]) {
  const t = { runs: 0, clears: 0, overs: 0, continues: 0, deaths: 0, refills: 0, coastToBattery: 0, reachedCoast: 0, endZones: {} };
  for (let seed = 1; seed <= 24; seed++) {
    for (const bot of ['smart', 'fuzz']) {
      const brain = bot === 'smart' ? B.smartBot({ auto: seed % 2 === 0 }) : B.fuzzBot(5);
      const opts = { seed, viewW: [468, 384, 449][seed % 3], continues: 3, seconds: bot === 'smart' ? 400 : 200 };
      if (level) { opts.level = level; opts.lanes = [0.18, 0.25]; }
      const o = B.run(brain, opts);
      t.runs++; t.deaths += o.r.deaths || 0; t.continues += o.r.continues || 0; t.refills += o.evCount.refill || 0;
      if (o.s.status === 'clear') t.clears++;
      if (o.s.status === 'over') t.overs++;
      if (name === 'strait') { const z = o.s.zone; if (z >= 3) t.reachedCoast++; if (z >= 4) t.coastToBattery++; }
      t.endZones[o.s.zone] = (t.endZones[o.s.zone] || 0) + 1;
    }
  }
  out[name] = t;
}
console.log(label, JSON.stringify(out));
