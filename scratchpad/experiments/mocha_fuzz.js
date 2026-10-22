'use strict';
const B = require('../game/tools/bot.js');
let n = 0, clears = 0, overs = 0, fails = 0, maxZone = [0, 0, 0, 0];
const t0 = Date.now();
for (let seed = 1; seed <= +(process.argv[2] || 120); seed++) {
  try {
    const o = B.run(B.fuzzBot(seed), { level: B.MOCHA, seed: seed * 3, seconds: 300, viewW: seed % 2 ? 468 : 384, name: 'fuzz ' + seed, continues: 3, lanes: seed % 3 ? [0.18, 0.25] : [0.07, 0.09] });
    n++; maxZone[o.s.zone]++;
    if (o.s.status === 'clear') clears++;
    if (o.s.status === 'over') overs++;
    fails += o.s.failsafe;
  } catch (e) { console.log('seed ' + seed + ': ' + e.message.slice(0, 300)); }
}
console.log(n + ' mashing games on Mocha, every tick checked; ' + clears + ' cleared, ' + overs + ' out of continues; furthest zone ' + maxZone.join('/') + '; failsafe ' + fails + '; ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s');
