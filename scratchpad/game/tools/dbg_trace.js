const B = require('./bot.js'); const Sim = B.Sim, LEVEL = B.LEVEL;
const vw = +process.argv[2], seed = +process.argv[3], auto = process.argv[4] === 'auto', noGren = process.argv.includes('nogren'), from = +process.argv[5] || 0, n = +process.argv[6] || 40;
const bot = B.smartBot({ auto, noGren });
let s = Sim.create(LEVEL, { viewW: vw, seed });
for (let k = 0; k < from + n; k++) {
  const i = bot(s);
  if (k >= from) console.log(k, 'in', JSON.stringify([i.mx, i.my, i.fire ? 1 : 0, i.jump ? 1 : 0, i.grenade ? 1 : 0]), 'p', s.p.x.toFixed(1), s.p.y.toFixed(1), 'plat', s.p.plat, 'air', s.p.air ? 1 : 0, 'face', s.p.face, 'cam', s.cam.toFixed(0),
    'foes', s.enemies.filter(e => e.alive && e.hostile && Sim.onScreen(s, e.x, 0)).map(e => e.k[0] + Math.round(e.x) + ',' + Math.round(e.y) + ':' + e.st + (Sim.staged(s, e) ? '' : '(lane)')).join(' '), 'eb', s.bullets.filter(b => !b.own && !b.gone).length);
  Sim.step(s, i);
  if (s.status === 'over') s = Sim.continueZone(s);
}
