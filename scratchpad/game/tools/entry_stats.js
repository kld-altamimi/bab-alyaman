// entry_stats.js - do the Scorpion's men get a chance? The careful bot plays the mission; for every man (and every truck
// on the coast road) it notes when he first shows on the screen, whether he gets as far as starting an attack, and how
// long he lasts. usage: node entry_stats.js GAME_DIR seeds [range ...]  (no range: as the game is; a range needs a sim.js
// with T.SHOT_RANGE, as the experiment of 13 Oct had)
'use strict';
const path = require('path');
const GAME = path.resolve(process.argv[2]);
const B = require(path.join(GAME, 'tools/bot.js'));
const Sim = require(path.join(GAME, 'src/sim.js'));
const N = +process.argv[3] || 2;
const ranges = process.argv.slice(4).map(Number);
const ATTACK = new Set(['aim', 'fire', 'burst', 'wind', 'throw', 'lean', 'bashw', 'bash']);
const pct = (a, q) => { if (!a.length) return NaN; const b = a.slice().sort((x, y) => x - y); return b[Math.min(b.length - 1, Math.floor(q * b.length))]; };
for (const R of (ranges.length ? ranges : [0])) {
  if (R && Sim.T.SHOT_RANGE !== undefined) { Sim.T.SHOT_RANGE = R; Sim.T.HMG_RANGE = Math.round(R * 1.15); }
  const men = [], trucks = [];
  let n = 0, plates = 0, deaths = 0, tsum = 0, clear = 0, spentMid = 0, spent = 0;
  for (const vw of [384, 449, 468]) for (const auto of [false, true]) for (let seed = 1; seed <= N; seed++) {
    const bot = B.smartBot({ auto });
    const seen = new Map(), tseen = new Map();
    const watch = s => {
      for (const e of s.events) if (e.t === 'spent') { spent++; if ((e.x - s.cam) / s.viewW < 0.85) spentMid++; }
      for (const e of s.enemies) {
        if (e.ext || !e.k || e.k === 'cmdr') continue;
        let r = seen.get(e.id);
        const on = e.x >= s.cam && e.x <= s.cam + s.viewW;
        if (!r && on && e.alive && e.hostile) { r = { t0: s.tick, x0: (e.x - s.cam) / s.viewW, attacked: false, out: null }; seen.set(e.id, r); }
        if (!r || r.out != null) continue;
        if (ATTACK.has(e.st)) r.attacked = true;
        if (!e.alive || !e.hostile) { r.out = s.tick - r.t0; r.xOut = (e.x - s.cam) / s.viewW; }
      }
      for (const t of (s.trucks || [])) {
        let r = tseen.get(t.id);
        const on = t.x >= s.cam && t.x <= s.cam + s.viewW;
        if (!r && on && t.st === 'ok') { r = { t0: s.tick, attacked: false, out: null }; tseen.set(t.id, r); }
        if (!r || r.out != null) continue;
        if (t.gst && t.gst !== 'idle') r.attacked = true;
        if (t.st !== 'ok') r.out = s.tick - r.t0;
      }
      return bot(s);
    };
    const o = B.run(watch, { seed: seed * 17 + vw, viewW: vw, continues: 6, seconds: 700, name: 'entry ' + R + ' ' + vw });
    n++; plates += o.r.plates; deaths += o.r.deaths;
    if (o.s.status === 'clear') { clear++; tsum += o.r.time; }
    for (const r of seen.values()) if (r.out != null) men.push(r);
    for (const r of tquick(tseen)) trucks.push(r);
  }
  function tquick(m) { return [...m.values()].filter(r => r.out != null); }
  const early = men.filter(r => r.out <= 45).length, att = men.filter(r => r.attacked).length;
  const tAtt = trucks.filter(r => r.attacked).length;
  console.log(`${R ? 'range ' + R + ' px' : 'as the game is'}: ${clear}/${n} finished, mean ${(tsum / Math.max(1, clear)).toFixed(1)} s, ${(plates / n).toFixed(2)} plates and ${(deaths / n).toFixed(2)} lives lost a game`);
  console.log(`   men: ${men.length} taken out; ${(early / men.length * 100).toFixed(0)}% within 0.75 s of showing on screen; ${(att / men.length * 100).toFixed(0)}% started an attack first; ` +
              `on screen a median ${(pct(men.map(r => r.out), 0.5) / 60).toFixed(2)} s; taken out a median ${(pct(men.map(r => r.xOut), 0.5) * 100).toFixed(0)}% of the way across`);
  console.log(`   trucks: ${trucks.length} stopped; ${(tAtt / Math.max(1, trucks.length) * 100).toFixed(0)}% had their gunner start firing first; on screen a median ${(pct(trucks.map(r => r.out), 0.5) / 60).toFixed(2)} s`
              + (spent ? `; tracers burnt out on screen ${(spent / n).toFixed(0)} a game, ${(spentMid / spent * 100).toFixed(0)}% before 85% across` : ''));
}
