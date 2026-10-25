// guard_audit.js - one copy of the game's sources (guard/var/<name>), played by the same seeded bots as fire_audit.js and
// fire_measure.js (phone-sized, the thumbs' strips 0.18 / 0.25 unless LANES is given): for every ordinary enemy who comes
// into the picture, did he get an attack off before he died; how many of the bot's shots glanced off a guarded man; and
// what the run cost the bot (armour plates, lives, continues, clears, time). The Strait and the Coffee Port and Ibb's
// painted zones on foot, in hold fire and auto fire; Taiz with its pilot.
// Usage: node guard_audit.js <game dir> [seeds] [laneL,laneR]
'use strict';
const path = require('path');
const G = path.resolve(process.argv[2]), N = +(process.argv[3] || 8);
const LANES = (process.argv[4] || '0.18,0.25').split(',').map(Number);
const B = require(path.join(G, 'tools/bot.js')), Sim = B.Sim;
require(path.join(G, 'src/fly.js'));
const TAIZ = require(path.join(G, 'src/level_taiz.js'));
const IBB = require(path.join(G, 'src/level_ibb.js'));
const BOSS = new Set(['cmdr', 'qm', 'cgun', 'launcher', 'boat', 'roaster', 'tailor']);
const FIRED = new Set(['burst', 'fire', 'throw', 'fling', 'shot', 'fired']);
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '-';
const med = a => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : NaN; };
const out = {};
function audit(name, mk, botOf, seconds) {
  let n = 0, fired = 0, killedFirst = 0, lifeT = [], glance = 0;
  const cost = { plates: 0, deaths: 0, conts: 0, clears: 0, time: 0, mins: 0, eshots: 0 };
  for (let seed = 1; seed <= N; seed++) {
    let s = mk(seed), conts = 0;
    const bot = botOf(seed), rec = {};
    for (let t = 0; t < seconds * 60; t++) {
      const inp = bot(s); inp.viewW = s.viewW; inp.viewH = s.viewH;
      Sim.step(s, inp);
      for (const ev of s.events) {
        if (ev.t === 'hit' && ev.kind === 'guard') glance++;
        if (ev.t === 'eshot' && !BOSS.has(ev.k)) cost.eshots++;
      }
      for (const e of s.enemies) {
        if (BOSS.has(e.k) || e.boss || e.intro || e.k === 'drone' || e.k === 'crate' || e.k === 'light') continue;
        let r = rec[e.id];
        if (!r && e.alive && e.hostile && e.seen && s.status === 'play' && !s.p.dead) r = rec[e.id] = { k: e.k, seen: s.tick, shot: null, dead: null };
        if (!r || r.dead != null) continue;
        if (r.shot == null && (FIRED.has(e.st) || e.enterShot || e.snapT != null)) r.shot = s.tick;
        if (!e.alive || !e.hostile) { r.dead = s.tick; continue; }
      }
      if (s.status === 'over') { if (conts >= 3) break; conts++; s = Sim.continueZone(s, s.viewW); }
      if (s.status === 'clear') break;
    }
    for (const id in rec) {
      const r = rec[id]; n++;
      if (r.shot != null) fired++;
      else if (r.dead != null) killedFirst++;
      if (r.dead != null) lifeT.push((r.dead - r.seen) / 60);
    }
    cost.mins += s.time / 60; cost.plates += s.stats.plates; cost.deaths += s.stats.deaths; cost.conts += conts; cost.clears += s.status === 'clear' ? 1 : 0; cost.time += s.time;
  }
  const row = { n, fired: Math.round(100 * fired / n), killedFirst: Math.round(100 * killedFirst / n), life: +med(lifeT).toFixed(2), glancePerRun: +(glance / N).toFixed(1),
    eshotsPerMin: +(cost.eshots / cost.mins).toFixed(1), plates: +(cost.plates / N).toFixed(1), deaths: +(cost.deaths / N).toFixed(2), conts: +(cost.conts / N).toFixed(2), clears: cost.clears + '/' + N, time: Math.round(cost.time / N) };
  out[name] = row;
  console.log((name + ':').padEnd(22) + ' enemies ' + String(n).padStart(4) + '  got an attack off ' + (row.fired + '%').padStart(4) + '  killed first ' + (row.killedFirst + '%').padStart(4) +
    '  alive in view ' + row.life.toFixed(2) + 's  glances/run ' + String(row.glancePerRun).padStart(5) + '  their shots/min ' + String(row.eshotsPerMin).padStart(5) +
    '  plates ' + row.plates + '  lives ' + row.deaths + '  continues ' + row.conts + '  cleared ' + row.clears + '  time ' + row.time + 's');
}
if (!process.env.ONLY_TAIZ) for (const [name, lv, secs] of [['Strait', B.LEVEL, 400], ['Coffee Port', B.MOCHA, 400], ['Ibb 1-2', IBB, 300]]) for (const auto of [false, true]) {
  audit(name + (auto ? ' auto' : ' hold'), seed => Sim.create(lv, { viewW: 468, seed, lanes: LANES }), () => B.smartBot({ auto }), secs);
}
const SRC = require('fs').readFileSync(path.join(G, 'tools/unit_taiz.js'), 'utf8');
const X = Sim.ext.fly, F = Sim.F, ZM = TAIZ.zoom || 1, VH = Math.round(216 * ZM);
const pilot = eval('(' + SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)')) + ')');
audit('Taiz pilot', seed => Sim.create(TAIZ, { viewW: Math.round(468 * ZM), viewH: VH, seed, lanes: LANES }), () => pilot({ stick: true }), 600);
if (process.env.JSON_OUT) require('fs').writeFileSync(process.env.JSON_OUT, JSON.stringify(out, null, 1));
