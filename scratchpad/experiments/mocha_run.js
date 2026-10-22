'use strict';
const path = require('path');
const B = require(path.join(__dirname, '../game/tools/bot.js'));
const seeds = (process.argv[2] || '1').split(',').map(Number), vw = +(process.argv[3] || 468), trace = process.argv[4] !== 'quiet';
for (const seed of seeds) {
  const t0 = Date.now();
  let o;
  try { o = B.run(B.smartBot({}), { level: B.MOCHA, seed, viewW: vw, continues: 3, seconds: 700, trace: true, name: 'mocha' + seed, lanes: [0.18, 0.25] }); }
  catch (e) { console.log('seed ' + seed + ': ' + e.message); continue; }
  if (trace) console.log(o.log.join('\n'));
  const r = o.r, s = o.s;
  console.log('seed ' + seed + ' ' + vw + ': ' + s.status + ' x=' + Math.round(s.p.x) + ' zone ' + s.zone + ' time ' + r.time.toFixed(1) + ' score ' + r.score + ' kills ' + r.kills + ' freed ' + r.freed + '/' + r.detainees +
    ' plates ' + r.plates + ' lives ' + r.deaths + ' cont ' + r.continues + ' boss ' + (r.bossT || 0).toFixed(1) + ' hurtBy ' + JSON.stringify(s.stats.hurtBy) + ' failsafe ' + s.failsafe + ' zones ' + o.zoneTimes.map(t => t.toFixed(0)).join(',') + ' (' + (Date.now() - t0) + ' ms)');
}
