// oops_test.js - the old city's crate (B2): its first drone goes the wrong way into one of its own crew
'use strict';
const { make, pilot, step } = require('./lib.js');
for (const W of [576, 702, 780]) {
  const s = make({ zone: 0, viewW: W, seed: 4 }), bot = pilot();
  let out = null, kills = [];
  for (let t = 0; t < 60 * 120 && !out; t++) {
    const inp = bot(s);
    step(s, inp);
    for (const e of s.events) {
      if (e.t === 'oops') out = { t: (t / 60).toFixed(1), at: [Math.round(e.x), Math.round(e.y)] };
    }
  }
  const d = s.enemies.find(e => e.k === 'drone' && e.st === 'oops');
  const victim = out ? s.enemies.filter(e => e.k === 'rifle' && !e.alive && Math.abs(e.x - out.at[0]) < 40).map(e => e.look + '@' + Math.round(e.x)) : [];
  console.log(W, out ? 'oops at ' + out.t + ' s, ' + JSON.stringify(out.at) + ', down: ' + (victim.join(' ') || 'nobody (into the roof)') : 'no oops seen');
}
