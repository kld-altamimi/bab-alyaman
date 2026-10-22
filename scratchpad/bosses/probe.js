// probe.js - can a Taiz sim state be cloned (structuredClone) and stepped on identically? And what does the state hold?
'use strict';
const path = require('path'), SRC = path.join(__dirname, '../game/src/');
const Sim = require(SRC + 'sim.js'); require(SRC + 'drive.js'); require(SRC + 'boss.js'); require(SRC + 'roaster.js');
try { require(SRC + 'tailor.js'); } catch (e) {}
require(SRC + 'fly.js');
const TAIZ = require(SRC + 'level_taiz.js');
const ZM = TAIZ.zoom, VH = Math.round(216 * ZM), VW = Math.round(468 * ZM);
const s = Sim.create(TAIZ, { viewW: VW, viewH: VH, seed: 3, zone: 3 });
const fns = [];
(function walk(o, p, seen) { if (!o || typeof o !== 'object' || seen.has(o)) return; seen.add(o); for (const k in o) { const v = o[k]; if (typeof v === 'function') fns.push(p + '.' + k); else walk(v, p + '.' + k, seen); } })(s, 's', new Set());
console.log('functions inside the state:', fns.slice(0, 10), fns.length);
const inp = { mx: 1, my: 0, fire: true, viewW: VW, viewH: VH };
for (let t = 0; t < 120; t++) Sim.step(s, inp);
let c; try { c = structuredClone(s); } catch (e) { console.log('clone failed:', e.message); process.exit(1); }
const h = x => JSON.stringify([x.tick, x.u, x.heli.x, x.heli.y, x.score, x.p.lives, x.p.plates, x.enemies.length, x.bullets.length]);
for (let t = 0; t < 600; t++) { const i2 = { mx: (t >> 5) % 3 - 1, my: (t >> 6) % 3 - 1, fire: true, viewW: VW, viewH: VH }; Sim.step(s, i2); Sim.step(c, Object.assign({}, i2)); }
console.log('same after 600 ticks:', h(s) === h(c), h(s));
console.log('state keys:', Object.keys(s).join(' '));
console.log('L shared?', c.L === s.L, 'zone', s.zone, 'u', s.u.toFixed(0), 'heli', s.heli.x.toFixed(0), s.heli.y.toFixed(0));
