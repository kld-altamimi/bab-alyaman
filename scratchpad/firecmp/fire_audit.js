// fire_audit.js - why a player may feel nobody shoots at him (Khaled, 23 Oct 00:30): for every ordinary enemy who comes
// into the picture, did he get a shot off before he died, and how long did he have? Same seeded bots as fire_measure.js,
// in hold-fire and auto-fire. Also: what held each one back while he was alive and in the picture (still walking in, in a
// thumb's lane, too far away, waiting out his first-shot delay, aiming), counted in ticks.
// Usage: node fire_audit.js <game dir> [seeds]
'use strict';
const path = require('path');
const G = process.argv[2], N = +(process.argv[3] || 6);
const B = require(path.join(G, 'tools/bot.js')), Sim = B.Sim, T = Sim.T;
require(path.join(G, 'src/fly.js'));
const TAIZ = require(path.join(G, 'src/level_taiz.js'));
const BOSS = new Set(['cmdr', 'qm', 'cgun', 'launcher']);
const FIRED = new Set(['burst', 'fire', 'throw', 'fling', 'shot', 'fired']);
const AIMING = new Set(['aim', 'lean', 'wind', 'scoop', 'lock', 'load', 'tell']);
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '-';
const med = a => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : NaN; };
function audit(name, mk, botOf, seconds) {
  const per = {}, held = { walking: 0, lane: 0, far: 0, delay: 0, aiming: 0, other: 0 };
  let n = 0, fired = 0, killedFirst = 0, lifeT = [], toShot = [];
  for (let seed = 1; seed <= N; seed++) {
    let s = mk(seed), conts = 0;
    const bot = botOf(seed), rec = {};
    for (let t = 0; t < seconds * 60; t++) {
      const inp = bot(s); inp.viewW = s.viewW; inp.viewH = s.viewH;
      Sim.step(s, inp);
      for (const e of s.enemies) {
        if (BOSS.has(e.k) || e.boss || e.intro || e.k === 'drone' || e.k === 'crate' || e.k === 'light') continue;
        let r = rec[e.id];
        if (!r && e.alive && e.hostile && e.seen && s.status === 'play' && !s.p.dead) r = rec[e.id] = { k: e.k, seen: s.tick, shot: null, dead: null };
        if (!r || r.dead != null) continue;
        if (r.shot == null && FIRED.has(e.st)) r.shot = s.tick;
        if (!e.alive || !e.hostile) { r.dead = s.tick; continue; }
        if (r.shot != null || s.p.dead || !e.seen) continue;
        // (alive, in the picture, not yet fired: what is holding him?)
        const ad = Math.abs(s.p.x - e.x);
        if (AIMING.has(e.st)) held.aiming++;
        else if (s.mode === 'foot' && !Sim.staged(s, e)) held.lane++;
        else if (s.mode === 'foot' && ad >= T.SIGHT) held.far++;
        else if (e.moving && (e.moveT || 0) <= 80) held.walking++;
        else if (e.cd > 0) held.delay++;
        else held.other++;
      }
      if (s.status === 'over') { if (conts >= 3) break; conts++; s = Sim.continueZone(s, s.viewW); }
      if (s.status === 'clear') break;
    }
    for (const id in rec) {
      const r = rec[id]; n++;
      per[r.k] = per[r.k] || { n: 0, fired: 0 }; per[r.k].n++;
      if (r.shot != null) { fired++; per[r.k].fired++; toShot.push((r.shot - r.seen) / 60); }
      else if (r.dead != null) killedFirst++;
      if (r.dead != null) lifeT.push((r.dead - r.seen) / 60);
    }
  }
  const tot = Object.values(held).reduce((a, b) => a + b, 0) || 1;
  console.log((name + ':').padEnd(24) + ' enemies ' + String(n).padStart(4) + '  got a shot off ' + pct(fired, n).padStart(4) + '  killed before any ' + pct(killedFirst, n).padStart(4) +
    '  alive in view (median) ' + med(lifeT).toFixed(2) + 's  seen->first shot ' + med(toShot).toFixed(2) + 's');
  console.log(' '.repeat(25) + 'held back by: ' + Object.keys(held).map(k => k + ' ' + pct(held[k], tot)).join(', ') + '   by kind: ' + Object.keys(per).map(k => k + ' ' + per[k].fired + '/' + per[k].n).join(', '));
}
for (const [name, lv] of [['Strait', B.LEVEL], ['Coffee Port', B.MOCHA]]) for (const auto of [false, true]) {
  audit(name + (auto ? ', auto fire' : ', hold fire'), seed => Sim.create(lv, { viewW: 468, seed, lanes: [0.18, 0.25] }), () => B.smartBot({ auto }), 400);
}
const SRC = require('fs').readFileSync(path.join(G, 'tools/unit_taiz.js'), 'utf8');
const X = Sim.ext.fly, F = Sim.F, ZM = TAIZ.zoom || 1, VH = Math.round(216 * ZM);
const pilot = eval('(' + SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)')) + ')');
audit('Taiz, pilot', seed => Sim.create(TAIZ, { viewW: Math.round(468 * ZM), viewH: VH, seed, lanes: [0.18, 0.25] }), () => pilot({ stick: true }), 600);
