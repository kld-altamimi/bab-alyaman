// pace.js - where the time goes in a careful run: fighting, walking, or standing at a shut gate with nobody to fight
'use strict';
const B = require('./bot.js'); const Sim = B.Sim, LEVEL = B.LEVEL;
for (const [vw, auto] of [[449, false], [384, false], [449, true]]) {
  const bot = B.smartBot({ auto });
  let s = Sim.create(LEVEL, { viewW: vw, seed: 20261012 });
  let fight = 0, walk = 0, idleHeld = 0, idleRuns = [], cur = 0, firstFoe = -1, kills = [], onscreen = [], laneOnly = 0;
  for (let k = 0; k < 60 * 200 && s.status === 'play'; k++) {
    Sim.step(s, bot(s));
    const foes = s.enemies.filter(e => e.alive && e.hostile && Sim.onScreen(s, e.x, 0));
    const staged = foes.filter(e => e.post || (e.x >= s.cam + vw * Sim.T.LANE_L && e.x <= s.cam + vw * (1 - Sim.T.LANE_R)));
    if (foes.length && firstFoe < 0) firstFoe = s.time;
    onscreen.push(foes.length);
    if (foes.length) { fight++; if (!staged.length) laneOnly++; if (cur) { idleRuns.push(cur); cur = 0; } }
    else if (s.holdX != null && Math.abs(s.cam - s.camMax) < 1) { idleHeld++; cur++; }
    else { walk++; if (cur) { idleRuns.push(cur); cur = 0; } }
    for (const e of s.events) if (e.t === 'die' || e.t === 'surrender') kills.push(s.time);
  }
  const gaps = kills.slice(1).map((t, i) => t - kills[i]);
  const mx = Math.max.apply(null, onscreen), avg = onscreen.reduce((a, b) => a + b, 0) / onscreen.length;
  console.log(vw + ' wide, ' + (auto ? 'auto' : 'hold') + ': ' + s.time.toFixed(1) + ' s in all. Men on screen ' + (fight / 60).toFixed(1) + ' s (of which only in the edge lanes ' + (laneOnly / 60).toFixed(1) + ' s), walking on ' + (walk / 60).toFixed(1) + ' s, held at a gate with no one in sight ' + (idleHeld / 60).toFixed(1) + ' s');
  console.log('   waits at a gate: ' + idleRuns.filter(v => v > 6).map(v => (v / 60).toFixed(1)).join(', ') + ' s; first man seen at ' + firstFoe.toFixed(1) + ' s; ' + kills.length + ' men dealt with, longest gap between two ' + Math.max.apply(null, gaps).toFixed(1) + ' s; at most ' + mx + ' on screen, ' + avg.toFixed(1) + ' on average');
}
