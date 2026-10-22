'use strict';
const { make, pilot, step } = require('./lib.js');
const W = +process.argv[2] || 702;
const s = make({ zone: 0, viewW: W, seed: 4 }), bot = pilot();
let crate = null;
for (let t = 0; t < 60 * 40; t++) {
  step(s, bot(s));
  const c = s.enemies.find(e => e.k === 'crate' && e.g === 'B2');
  if (c && !crate) { crate = c.id; }
  const cc = s.enemies.find(e => e.id === crate);
  for (const e of s.events) if (['crate_open', 'drone_up', 'oops', 'group_done', 'go'].includes(e.t) || (e.t === 'die' && (e.k === 'crate' || e.k === 'drone'))) console.log((t / 60).toFixed(2), e.t, e.g || e.gate || '', e.k || '', Math.round(e.x || 0));
  if (cc && t % 30 === 0 && t > 60 * 15) console.log('   crate', cc.st, 'alive', cc.alive, 'seen', cc.seen, 'hp', cc.hp, 'awake', s.groups.B2.awake);
}
