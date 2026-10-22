const { make, copy, pilot, step } = require('./lib.js');
const s = make({ zone: 3 }), bot = pilot();
for (let t = 0; t < 900; t++) step(s, bot(s));
let t0 = Date.now(); for (let i = 0; i < 200; i++) copy(s); console.log('copy ms', (Date.now() - t0) / 200);
t0 = Date.now(); const c = copy(s); for (let i = 0; i < 600; i++) step(c, { ax: 0, ay: 0 }); console.log('step ms', (Date.now() - t0) / 600);
console.log('u', s.u.toFixed(0), 'hold', s.holdU, 'enemies', s.enemies.length, 'heli', s.heli.x.toFixed(0), s.heli.y.toFixed(0), 'boss', s.boss && s.boss.k);
