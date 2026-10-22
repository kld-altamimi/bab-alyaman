// baseline.js - seeded runs of the Strait whose end state must not change when the engine is reorganised.
'use strict';
const path = require('path');
const B = require(path.join(process.argv[2] || '../game/tools', 'bot.js'));
const out = [];
for (const [seed, vw, auto] of [[7, 468, false], [11, 384, true], [23, 449, false]]) {
  const o = B.run(B.smartBot({ auto }), { seed, viewW: vw, continues: 3, seconds: 400 });
  out.push(B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total);
}
const fz = B.run(B.fuzzBot(5), { seed: 15, seconds: 120, continues: 3 });
out.push(B.snap(fz.s));
console.log(out.map(s => require('crypto').createHash('md5').update(s).digest('hex').slice(0, 12) + ' ' + s.slice(0, 80)).join('\n'));
