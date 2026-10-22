// fuzz.js [N] - random thumbs through the whole mission, every tick checked against the rules that must always hold
'use strict';
const B = require('./bot.js');
const N = +(process.argv.find(a => /^\d+$/.test(a)) || 120);
const level = process.argv.includes('zabid') ? B.ZABID : (process.argv.includes('mocha') ? B.MOCHA : undefined);      // (node fuzz.js 40 zabid: the Souq)
for (const lanes of [undefined, [0.07, 0.09]]) {
  let n = 0, clears = 0, overs = 0, plates = 0, deaths = 0, conts = 0, time = 0, by = {}, first = 0, fails = 0, zones = [0, 0, 0, 0, 0], stuck = [];
  for (let seed = 1; seed <= N; seed++) {
    const o = B.run(B.fuzzBot(seed), { level, seed: seed * 3, seconds: 900, viewW: [468, 384, 432][seed % 3], name: 'fuzz ' + seed, continues: 8, lanes });
    n++;
    if (o.s.status === 'clear') { clears++; time += o.r.time; if (o.r.continues === 0) first++; } else stuck.push([seed, o.s.status, o.s.zone, Math.round(o.s.p.x), o.s.mode]);
    if (o.s.status === 'over') overs++;
    zones[o.s.zone]++;
    fails += o.s.failsafe; plates += o.r.plates; deaths += o.r.deaths; conts += o.r.continues;
    for (const k in o.s.stats.hurtBy) by[k] = (by[k] || 0) + o.s.stats.hurtBy[k];
  }
  console.log((lanes ? 'nothing over the picture' : 'thumbs over the picture') + ': ' + n + ' games of random thumbs, every tick checked: no rule broken. ' + clears + ' finished (' + first + ' without a continue), ' + overs + ' ran out of continues');
  console.log('   per game ' + (plates / n).toFixed(1) + ' plates, ' + (deaths / n).toFixed(1) + ' lives, ' + (conts / n).toFixed(2) + ' continues; finishers took ' + (time / Math.max(1, clears)).toFixed(0) + ' s; failsafe ' + fails + '; ended in zone ' + zones.join('/'));
  console.log('   hurt by: ' + Object.keys(by).sort((a, b) => by[b] - by[a]).slice(0, 14).map(k => k + ' ' + (by[k] / n).toFixed(2)).join(', '));
  if (stuck.length) console.log('   not finished:', JSON.stringify(stuck.slice(0, 12)));
}
