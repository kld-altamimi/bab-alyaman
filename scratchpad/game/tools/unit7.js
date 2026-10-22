// unit7.js - skipping (build 13): every mission can be started at any of its checkpoints and finished from there, and a
// skip to the next checkpoint in the middle of a run (the pause menu's) keeps the score, the clock and the lives and
// plays on to the end. B.run checks the game's rules on every step, as for every other bot run.
'use strict';
const B = require('./bot.js');
const Sim = B.Sim;
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const THUMBS = [0.18, 0.25];
const LEVELS = [B.LEVEL, B.MOCHA, B.ZABID];

// ---- a run started at a checkpoint begins there, with what came before it out of the way
for (const L of LEVELS) {
  for (let z = 1; z < L.zones.length; z++) {
    const s = Sim.create(L, { viewW: 468, seed: 5, zone: z, lanes: THUMBS });
    const before = Object.keys(s.groups).filter(k => s.groups[k].zone < z), after = Object.keys(s.groups).filter(k => s.groups[k].zone >= z);
    const gatesBefore = L.gates.filter(g => g.groups.every(id => L.groups[id].zone < z)).map(g => g.id);
    const nDet = L.props.filter(o => o.k === 'detainee').length;
    const good = s.zone === z && s.time === 0 && s.score === 0 && s.p.lives === Sim.T.LIVES &&
      before.every(k => s.groups[k].done) && after.every(k => !s.groups[k].done) &&
      gatesBefore.every(id => s.gates.find(g => g.id === id).done) &&
      !s.enemies.some(e => L.groups[e.g].zone < z) && !s.props.some(o => o.k !== 'detainee' && L.props.find(q => q.x === o.x && q.k === o.k && q.zone < z)) &&
      s.stats.detainees === nDet && (z === 0 || s.p.inv > 0);
    const where = s.mode === 'drive' ? 'in the pickup' : 'on foot at x=' + Math.round(s.p.x);
    ok(good, `${L.banner}: started at ${L.zones[z].name}, ${where}: earlier groups and gates done, nobody from before, ${nDet} held in the whole mission`);
  }
}
{
  const s3 = Sim.create(B.LEVEL, { viewW: 468, seed: 5, zone: 3, lanes: THUMBS }), s4 = Sim.create(B.LEVEL, { viewW: 468, seed: 5, zone: 4, lanes: THUMBS });
  ok(s3.mode === 'drive' && s3.car.st === 'drive' && s4.mode === 'foot' && s4.car.st === 'park', 'the Strait from the coast road starts in the pickup, from the battery on foot with the pickup parked');
}

// ---- from every checkpoint, at three widths, the careful bot finishes
const times = [];
for (const L of LEVELS) {
  for (let z = 0; z < L.zones.length; z++) {
    const res = [];
    for (const [vw, seed] of [[384, 1], [449, 2], [468, 3]]) {
      res.push(B.run(B.smartBot({}), { level: L, zone: z, seed, viewW: vw, continues: 3, seconds: 600, lanes: THUMBS, name: L.id + ' from ' + z }));
    }
    const t = res.map(o => o.r.time.toFixed(0) + ' s');
    ok(res.every(o => o.s.status === 'clear'), `${L.banner}: from ${L.zones[z].name} the bot finishes at 384, 449 and 468 wide (${t.join(', ')}${res.some(o => o.r.continues) ? '; continues ' + res.map(o => o.r.continues).join('/') : ''})`);
    times.push([L.id, z, res.map(o => o.r.time)]);
  }
}

// ---- skipping ahead in the middle of a run, as the pause menu does it
function skip(s, viewW) {
  return Sim.create(s.L, { zone: s.zone + 1, score: s.score, time: s.time, stats: s.stats, viewW: viewW, seed: (s.tick * 7919 + 101) >>> 0, radio: s.radio, lanes: THUMBS, lives: s.p.lives });
}
for (const L of LEVELS) {
  for (const [vw, seed, every] of [[468, 7, 9], [384, 8, 4]]) {
    // (a fresh bot after each skip, as a person looks about afresh: the bot's errands belong to the stretch it was in)
    let bot = B.smartBot({});
    let s = Sim.create(L, { viewW: vw, seed, lanes: THUMBS }), kept = true, skips = 0, prevCam = { cam: s.cam };
    for (let i = 0; i < 600 * 60 && s.status !== 'clear'; i++) {
      Sim.step(s, bot(s));
      B.check(s, prevCam, L.id + ' skipping');
      prevCam = { cam: s.cam };
      if (s.status === 'over') { s = Sim.continueZone(s, vw); prevCam = { cam: s.cam }; continue; }
      // every so many seconds of play, skip to the next checkpoint (until the last)
      if (s.status === 'play' && s.zone + 1 < L.zones.length && i > 0 && i % (every * 60) === 0) {
        const was = { score: s.score, time: s.time, lives: s.p.lives, stats: s.stats, zone: s.zone };
        s = skip(s, vw); skips++; bot = B.smartBot({});
        prevCam = { cam: s.cam };
        if (!(s.zone === was.zone + 1 && s.score === was.score && s.time === was.time && s.p.lives === (was.lives || Sim.T.LIVES) && s.stats === was.stats)) kept = false;
      }
    }
    ok(s.status === 'clear' && kept && skips === L.zones.length - 1,
      `${L.banner} at ${vw} wide: skipped ahead ${skips} times (every ${every} s), the score, clock and lives came along each time, and the bot finished (${s.time.toFixed(0)} s, ${s.score} points)`);
  }
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL SKIPPING CHECKS OK');
process.exitCode = fails ? 1 : 0;
