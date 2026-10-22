// sweep.js - the careful bot at every screen width the game can have, with both ways of firing: does it always get through?
'use strict';
const B = require('./bot.js');
let n = 0, clear = 0, fails = 0, worst = 0, tsum = 0, plates = 0, lives = 0, conts = 0, bad = [], boss = 0, bossMax = 0, bossMin = 1e9, zt = [0, 0, 0, 0, 0];
const by = {};
const noGren = process.argv.includes('nogren'), N = +(process.argv.find(a => /^\d+$/.test(a)) || 50);
const lanes = process.argv.includes('clear') ? [0.07, 0.09] : undefined;
const level = process.argv.includes('mocha') ? B.MOCHA : (process.argv.includes('zabid') ? B.ZABID : B.LEVEL);          // (node sweep.js 3 mocha: the Coffee Port; zabid: the Souq)
for (const vw of [384, 400, 416, 432, 449, 468]) {
  for (const auto of [false, true]) {
    for (let seed = 1; seed <= N; seed++) {
      const o = B.run(B.smartBot({ auto, noGren }), { level, seed: seed * 17 + vw, viewW: vw, lanes, continues: 6, seconds: 700, name: 'sweep ' + vw + (auto ? ' auto ' : ' hold ') + seed });
      n++;
      if (o.s.status === 'clear') { clear++; tsum += o.r.time; worst = Math.max(worst, o.r.time); boss += o.r.bossT; bossMax = Math.max(bossMax, o.r.bossT); bossMin = Math.min(bossMin, o.r.bossT); o.zoneTimes.forEach((t, i) => { zt[i] += t; }); } else bad.push([vw, auto, seed, o.s.status, Math.round(o.s.p.x), o.s.zone]);
      fails += o.s.failsafe; plates += o.r.plates; lives += o.r.deaths; conts += o.r.continues;
      for (const k in o.s.stats.hurtBy) by[k] = (by[k] || 0) + o.s.stats.hurtBy[k];
    }
  }
}
console.log((level === B.MOCHA ? 'The Coffee Port, ' : (level === B.ZABID ? 'The Souq, ' : 'The Strait, ')) + (lanes ? 'nothing over the picture: ' : 'thumbs over the picture: ') + (noGren ? 'never throwing a grenade: ' : '') + clear + '/' + n + ' finished; mean ' + (tsum / clear).toFixed(1) + ' s, slowest ' + worst.toFixed(1) + ' s; per game ' + (plates / n).toFixed(2) + ' plates, ' + (lives / n).toFixed(2) + ' lives, ' + (conts / n).toFixed(2) + ' continues; failsafe ' + fails);
console.log('boss fight: mean ' + (boss / Math.max(1, clear)).toFixed(1) + ' s, from ' + bossMin.toFixed(1) + ' to ' + bossMax.toFixed(1) + '; zones reached at ' + zt.map(t => (t / Math.max(1, clear)).toFixed(0)).join(', ') + ' s');
console.log('hurt by: ' + Object.keys(by).sort((a, b) => by[b] - by[a]).map(k => k + ' ' + (by[k] / n).toFixed(2)).join(', '));
if (bad.length) console.log('NOT FINISHED:', JSON.stringify(bad.slice(0, 20)));
