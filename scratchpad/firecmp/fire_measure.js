// fire_measure.js - how much the ordinary enemies shoot, with the same seeded bots, for one copy of the game's sources
// (game-features-R5, 23 Oct: "sooner and more often"). On foot (the Strait, the Coffee Port): the smart bot, phone-sized,
// 10 seeds; in Taiz: the pilot bot, 10 seeds. Shots and attacks a minute by everyone but the bosses, how long a man takes
// from being seen to starting to aim (his warning), and what it costs the bot: plates, lives, continues, clears, time.
// Usage: node fire_measure.js <game dir> [seeds]
'use strict';
const path = require('path');
const G = process.argv[2], N = +(process.argv[3] || 10);
const B = require(path.join(G, 'tools/bot.js')), Sim = B.Sim;
require(path.join(G, 'src/fly.js'));
const TAIZ = require(path.join(G, 'src/level_taiz.js'));
const BOSS = new Set(['cmdr', 'qm', 'cgun', 'launcher', 'boat', 'roaster', 'tailor']);
const ATTACK = new Set(['eshot', 'lob', 'rpg_fire', 'mortar_fire', 'sam_launch', 'fling']);
const AIM = new Set(['aim', 'lean', 'wind', 'scoop', 'tell', 'lock', 'load']);
const med = a => { const b = a.slice().sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : NaN; };
function measure(name, mk, botOf, opts) {
  const tot = { shots: 0, attacks: 0, mins: 0, plates: 0, deaths: 0, conts: 0, clears: 0, time: 0, firstAim: [] };
  for (let seed = 1; seed <= N; seed++) {
    let s = mk(seed), conts = 0;
    const bot = botOf(seed), seenAt = {}, aimed = {};
    for (let t = 0; t < opts.seconds * 60; t++) {
      const inp = bot(s); inp.viewW = s.viewW; inp.viewH = s.viewH;
      Sim.step(s, inp);
      for (const e of s.events) {
        if (!ATTACK.has(e.t) || BOSS.has(e.k)) continue;
        tot.attacks++; if (e.t === 'eshot') tot.shots++;
      }
      for (const e of s.enemies) {
        if (!e.alive || !e.hostile || BOSS.has(e.k) || e.boss) continue;
        if (e.seen && seenAt[e.id] == null && s.status === 'play' && !s.p.dead) seenAt[e.id] = s.tick;
        if (seenAt[e.id] != null && !aimed[e.id] && AIM.has(e.st)) { aimed[e.id] = 1; tot.firstAim.push((s.tick - seenAt[e.id]) / 60); }
      }
      if (s.status === 'over') { if (conts >= 3) break; conts++; s = Sim.continueZone(s, s.viewW); }
      if (s.status === 'clear') break;
    }
    tot.mins += s.time / 60; tot.plates += s.stats.plates; tot.deaths += s.stats.deaths; tot.conts += conts; tot.clears += s.status === 'clear' ? 1 : 0; tot.time += s.time;
  }
  console.log((name + ':').padEnd(13) + ' shots/min ' + (tot.shots / tot.mins).toFixed(1).padStart(5) + '  attacks/min ' + (tot.attacks / tot.mins).toFixed(1).padStart(5) +
    '  seen->aim median ' + med(tot.firstAim).toFixed(2) + 's (n ' + tot.firstAim.length + ')  plates lost ' + (tot.plates / N).toFixed(1) + '  lives lost ' + (tot.deaths / N).toFixed(2) +
    '  continues ' + (tot.conts / N).toFixed(2) + '  cleared ' + tot.clears + '/' + N + '  time ' + (tot.time / N).toFixed(0) + 's');
}
// on foot: the smart bot (FIRE held), a phone's picture
for (const [name, lv] of [['the Strait', B.LEVEL], ['Coffee Port', B.MOCHA]]) {
  measure(name, seed => Sim.create(lv, { viewW: 468, seed, lanes: [0.18, 0.25] }), () => B.smartBot({}), { seconds: 400 });
}
// on foot again: the smart bot a quarter of a second late on everything (a person's reactions): what a player takes
const late = (bot, n) => { const q = []; return (s) => { q.push(bot(s)); return q.length > n ? q.shift() : { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false }; }; };
for (const [name, lv] of [['Strait late', B.LEVEL], ['Port late', B.MOCHA]]) {
  measure(name, seed => Sim.create(lv, { viewW: 468, seed, lanes: [0.18, 0.25] }), () => late(B.smartBot({}), 15), { seconds: 400 });
}
// Taiz: the pilot (aim stick), going for the hostages
const SRC = require('fs').readFileSync(path.join(G, 'tools/unit_taiz.js'), 'utf8');
const X = Sim.ext.fly, F = Sim.F, ZM = TAIZ.zoom || 1, VH = Math.round(216 * ZM);
const pilot = eval('(' + SRC.slice(SRC.indexOf('function pilot(opt) {'), SRC.indexOf('function fuzz(seed)')) + ')');
measure('Taiz', seed => Sim.create(TAIZ, { viewW: Math.round(468 * ZM), viewH: VH, seed, lanes: [0.18, 0.25] }), () => pilot({ stick: true }), { seconds: 600 });
