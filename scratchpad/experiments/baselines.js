// baselines.js - the bot baselines: seeded runs of every released mission (the Strait, the Coffee Port, Taiz by Apache,
// Ibb) whose end states must not change when the engine is reorganised. A change that is meant to move play re-records
// them; a change that is not must leave them as they are.
//   node baselines.js            compares today's sources with baselines.json and lists what moved (exit 1 if anything did)
//   node baselines.js --record   writes baselines.json from today's sources (say in the commit why they moved)
// The Strait's and the Coffee Port's runs are baseline.js's and baseline_mocha.js's (same seeds, same hashes); Taiz flies
// with unit_taiz.js's pilot (tools/taiz_bot.js); Ibb walks with bot.js's smart bot as unit_ibb.js does.
'use strict';
const path = require('path'), fs = require('fs'), crypto = require('crypto');
const tools = path.join(__dirname, '../game/tools');
const B = require(path.join(tools, 'bot.js'));
try { require(path.join(tools, '../src/sandal.js')); } catch (e) {}      // (Ibb: the sandal at Jibla, loaded as the page loads it)
const TB = require(path.join(tools, 'taiz_bot.js'));
const IBB = require(path.join(tools, '../src/level_ibb.js'));
const WW = TB.WW;
const h12 = s => crypto.createHash('md5').update(s).digest('hex').slice(0, 12);

const RUNS = [
  // the Strait (baseline.js)
  ['strait 7', () => { const o = B.run(B.smartBot({ auto: false }), { seed: 7, viewW: 468, continues: 3, seconds: 400 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['strait 11 auto', () => { const o = B.run(B.smartBot({ auto: true }), { seed: 11, viewW: 384, continues: 3, seconds: 400 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['strait 23', () => { const o = B.run(B.smartBot({ auto: false }), { seed: 23, viewW: 449, continues: 3, seconds: 400 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['strait fuzz', () => { const o = B.run(B.fuzzBot(5), { seed: 15, seconds: 120, continues: 3 }); return [B.snap(o.s), o.s]; }],
  // the Coffee Port (baseline_mocha.js)
  ['mocha 7', () => { const o = B.run(B.smartBot({ auto: false }), { level: B.MOCHA, seed: 7, viewW: 468, continues: 3, seconds: 400, lanes: [0.18, 0.25] }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['mocha 11 auto', () => { const o = B.run(B.smartBot({ auto: true }), { level: B.MOCHA, seed: 11, viewW: 384, continues: 3, seconds: 400, lanes: [0.18, 0.25] }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['mocha 23', () => { const o = B.run(B.smartBot({ auto: false }), { level: B.MOCHA, seed: 23, viewW: 449, continues: 3, seconds: 400, lanes: [0.18, 0.25] }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['mocha fuzz', () => { const o = B.run(B.fuzzBot(5), { level: B.MOCHA, seed: 15, seconds: 120, continues: 3 }); return [B.snap(o.s), o.s]; }],
  // Taiz by Apache (unit_taiz.js's pilot runs: both widths, both lane settings, the aim stick and FIRE held)
  ['taiz pilot 468 stick', () => { const o = TB.run(TB.pilot({ stick: true }), { viewW: WW(468), lanes: [0.18, 0.25], seed: 1, seconds: 600, continues: 3 }); return [TB.hashOf(o.s) + ' ' + o.s.status + ' ' + o.s.score, o.s]; }],
  ['taiz pilot 384 stick', () => { const o = TB.run(TB.pilot({ stick: true }), { viewW: WW(384), lanes: [0.18, 0.25], seed: 2, seconds: 600, continues: 3 }); return [TB.hashOf(o.s) + ' ' + o.s.status + ' ' + o.s.score, o.s]; }],
  ['taiz pilot 449', () => { const o = TB.run(TB.pilot({ stick: false }), { viewW: WW(449), lanes: [0.07, 0.09], seed: 3, seconds: 600, continues: 3 }); return [TB.hashOf(o.s) + ' ' + o.s.status + ' ' + o.s.score, o.s]; }],
  ['taiz pilot 468', () => { const o = TB.run(TB.pilot({ stick: false }), { viewW: WW(468), lanes: [0.07, 0.09], seed: 5, seconds: 600, continues: 3 }); return [TB.hashOf(o.s) + ' ' + o.s.status + ' ' + o.s.score, o.s]; }],
  ['taiz fuzz', () => { const o = TB.run(TB.fuzz(100), { viewW: WW(384), seed: 50, seconds: 180, continues: 2 }); return [TB.hashOf(o.s), o.s]; }],
  // Ibb (unit_ibb.js's walks: the whole range on foot, with continues)
  ['ibb 7', () => { const o = B.run(B.smartBot({ auto: false }), { level: IBB, seed: 7, seconds: 480, continues: 9 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['ibb 11 auto', () => { const o = B.run(B.smartBot({ auto: true }), { level: IBB, seed: 11, seconds: 480, continues: 9 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['ibb 23', () => { const o = B.run(B.smartBot({ auto: false }), { level: IBB, seed: 23, seconds: 480, continues: 9 }); return [B.snap(o.s) + ' ' + o.s.status + ' ' + o.r.total, o.s]; }],
  ['ibb fuzz', () => { const o = B.run(B.fuzzBot(5), { level: IBB, seed: 15, seconds: 120, continues: 3 }); return [B.snap(o.s), o.s]; }]
];

function play() {
  const out = {};
  for (const [name, fn] of RUNS) {
    const t0 = Date.now(), [state, s] = fn();
    const st = s.stats || {};
    out[name] = { hash: h12(state), status: s.status, time: +s.time.toFixed(1), score: s.score, deaths: st.deaths, kills: st.kills, ms: Date.now() - t0 };
  }
  return out;
}

const file = path.join(__dirname, 'baselines.json');
const now = play();
const line = (n, r) => (n + ':').padEnd(24) + r.hash + '  ' + String(r.status).padEnd(6) + ' ' + String(r.time).padStart(6) + 's  score ' + String(r.score).padStart(5) + '  kills ' + String(r.kills == null ? '-' : r.kills).padStart(3) + '  deaths ' + (r.deaths == null ? '-' : r.deaths);
if (process.argv.includes('--record')) {
  fs.writeFileSync(file, JSON.stringify({ recorded: new Date().toISOString(), note: process.argv.slice(process.argv.indexOf('--record') + 1).join(' ') || '', runs: now }, null, 1) + '\n');
  for (const n in now) console.log(line(n, now[n]));
  console.log('recorded ' + Object.keys(now).length + ' runs to ' + path.basename(file));
} else {
  const base = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')).runs : {};
  let moved = 0;
  for (const n in now) {
    const b = base[n];
    const same = b && b.hash === now[n].hash;
    if (!same) moved++;
    console.log((same ? 'same   ' : (b ? 'MOVED  ' : 'NEW    ')) + line(n, now[n]) + (b && !same ? '   (was ' + b.hash + ' ' + b.status + ' ' + b.time + 's score ' + b.score + ')' : ''));
  }
  console.log(moved ? moved + ' of ' + Object.keys(now).length + ' runs moved from the baselines' : 'all ' + Object.keys(now).length + ' runs as recorded');
  process.exit(moved ? 1 : 0);
}
