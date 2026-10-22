// level_mocha.js - The Coffee Port: Mocha, on foot from one end to the other. The quay with a dhow up on trestles and a
// dockside crane; the coffee warehouses, seen with their front wall cut away, men coming out of the doors at the back;
// the roasting house, its steam vents and its catwalk over the drums; and the old lighthouse on the point, where the
// Scorpion's quartermaster keeps the Big Roaster.
// The ground is the stone of the quay and the floors of the buildings: flat, the walk line at 184. Platforms are the tops
// of things as tools/stage_mocha.py paints them (unit6.js checks that the two agree).
var LEVEL_MOCHA = (function () {
  'use strict';
  var Q = 0, WH = 1232, RH = 2464, PT = 3584, END = 4480;      // where the quay, the warehouses, the roasting house and the point start
  var L = {
    id: 'mocha',
    name: 'The Coffee Port',
    art: 'mocha',
    banner: 'THE COFFEE PORT',
    music: 'mocha', bossMusic: 'roaster',
    sea: true,
    lines: { start: [[10, 'ann_mocha', 4], [200, 'yazeed_coffee', 1]], clear: [[26, 'ann_complete', 8], [215, 'yazeed_cup', 8]] },
    freedNote: 'somebody is still tied up among the sacks',
    bossFact: 'Roaster put out in',
    width: END,
    height: 216,
    par: 240,                  // seconds, for the Ace medal (the careful bot takes about 105: the Strait's par is twice its time)
    start: 96,                 // where the skiff puts Yazeed on the quay
    exitX: END - 80,
    restX: END - 54,
    endRight: END,
    ground: { step: 4, y: [184] },
    world: { Q: Q, WH: WH, RH: RH, PT: PT, ROAD_Y: 184 },
    fires: [[2580, 166], [2900, 166], [3110, 166], [3420, 166]],     // the roasters' fireboxes: sparks come out of their doors
    // one-way platforms: land on them from above, drop through with down + jump
    plats: [
      // the quay: a pile of sacks on a pallet, a dhow up on trestles (a crate to step up from), the dockside crane
      { id: 'pile1', pts: [[182, 164], [248, 164]] },
      { id: 'pile1top', pts: [[198, 150], [232, 150]] },
      { id: 'step1', pts: [[370, 162], [396, 162]] },
      { id: 'deck', pts: [[404, 138], [520, 137], [600, 136]] },
      { id: 'poop', pts: [[600, 124], [648, 124]] },
      { id: 'crate2', pts: [[688, 166], [714, 166]] },
      { id: 'crane', pts: [[716, 142], [802, 142]] },
      { id: 'cab', pts: [[740, 108], [794, 108]] },
      // the warehouses: two steps of sacks up to the gallery along the back wall; a pile by the hoist
      { id: 'sk1', pts: [[1436, 166], [1470, 166]] },
      { id: 'sk2', pts: [[1462, 148], [1500, 148]] },
      { id: 'gallery', pts: [[1500, 122], [1966, 122]] },
      { id: 'pile3', pts: [[1650, 158], [1700, 158]] },          // (a way up in the middle of the fight, as well as at the end)
      { id: 'pile2', pts: [[2180, 162], [2242, 162]] },
      // the roasting house: crates up to the catwalk over the drums
      { id: 'cr1', pts: [[2618, 166], [2648, 166]] },
      { id: 'cr2', pts: [[2642, 146], [2678, 146]] },
      { id: 'catwalk', pts: [[2678, 118], [3252, 118]] },
      { id: 'cart1', pts: [[2836, 152], [2880, 152]] },          // bean carts under it: the catwalk is too high to jump to from the floor
      { id: 'cart2', pts: [[3196, 152], [3236, 152]] }
    ],
    zones: [
      { x: Q, name: 'The quay', spawn: 96 },
      { x: WH, name: 'The warehouses', spawn: WH - 40, indoor: true },
      { x: RH, name: 'The roasting house', spawn: RH - 40, indoor: true },
      { x: PT, name: 'The old lighthouse', spawn: PT - 30 }
    ],
    gates: [
      { id: 'q0', x: 560, groups: ['A', 'A2', 'B'] },
      { id: 'q1', x: 850, groups: ['W', 'W2'] },
      { id: 'w0', x: 1700, groups: ['C', 'C2'] },
      { id: 'w1', x: 2200, groups: ['D', 'D2'] },
      { id: 'r0', x: 2860, groups: ['E', 'E2'] },
      { id: 'r1', x: 3330, groups: ['F', 'F2'] },
      { id: 'gB', x: 4010, groups: ['BOSS'] }
    ],
    groups: {
      A: { zone: 0, trig: 250 },
      A2: { zone: 0, after: 'A', delay: 30 },
      B: { zone: 0, after: 'A2', delay: 40, lastManSurrenders: true },
      W: { zone: 0, trig: 720 },
      W2: { zone: 0, after: 'W', delay: 40, lastManSurrenders: true },
      C: { zone: 1, trig: 1450 },
      C2: { zone: 1, after: 'C', delay: 40, lastManSurrenders: true },
      D: { zone: 1, trig: 1990 },
      D2: { zone: 1, after: 'D', delay: 40, lastManSurrenders: true },
      E: { zone: 2, trig: 2640 },
      E2: { zone: 2, after: 'E', delay: 40, lastManSurrenders: true },
      F: { zone: 2, trig: 3110 },
      F2: { zone: 2, after: 'F', delay: 40, lastManSurrenders: true },
      BOSS: { zone: 3, hold: true, trig: PT + 230, noSurrender: true }
    },
    // k: rifle | bomber | door | cook. enter: 1 from the right edge, -1 from the left. door: out of the doorway at x.
    // A man at a post (post: 1) must stand inside the middle of his gate's held screen at every width, or he stays
    // guarded for ever: from 133 px left of the gate to 106 px right of it (384 wide, thumbs over the picture). unit6.js checks.
    spawns: [
      // ---- the quay: the dhow on its trestles
      { g: 'A', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'A', k: 'rifle', enter: 1, delay: 50, look: 'youth' },
      { g: 'A', k: 'bomber', enter: 1, delay: 130 },
      { g: 'A2', k: 'rifle', x: 470, plat: 'deck', post: 1, look: 'qat' },
      { g: 'A2', k: 'rifle', x: 566, plat: 'deck', post: 1, look: 'angry' },
      { g: 'A2', k: 'door', enter: 1, delay: 20, tag: 'd' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 20, dx: 34, behind: 'd', look: 'worried' },
      { g: 'B', k: 'bomber', x: 626, plat: 'poop', post: 1 },
      { g: 'B', k: 'cook', enter: 1, delay: 30 },
      { g: 'B', k: 'rifle', enter: -1, delay: 90, look: 'angry' },
      { g: 'B', k: 'rifle', enter: 1, delay: 160, look: 'youth' },
      // ---- the crane, the fish crates and a wall of sacks
      { g: 'W', k: 'rifle', x: 776, plat: 'cab', post: 1, look: 'youth' },
      { g: 'W', k: 'bomber', x: 732, plat: 'crane', post: 1 },
      { g: 'W', k: 'rifle', x: 930, post: 1, covered: 1, look: 'worried' },
      { g: 'W', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'W', k: 'rifle', enter: 1, delay: 40, dx: 36, behind: 'd', look: 'qat' },
      { g: 'W2', k: 'cook', enter: 1, delay: 0 },
      { g: 'W2', k: 'rifle', enter: -1, delay: 60, look: 'angry' },
      { g: 'W2', k: 'rifle', enter: 1, delay: 120, look: 'worried' },
      { g: 'W2', k: 'bomber', enter: 1, delay: 200 },
      // ---- the warehouses: the gallery, and the doors in the back wall
      { g: 'C', k: 'rifle', x: 1610, plat: 'gallery', post: 1, look: 'angry' },
      { g: 'C', k: 'rifle', door: 1, x: 1566, delay: 30, look: 'youth' },
      { g: 'C', k: 'cook', door: 1, x: 1846, delay: 90 },
      { g: 'C', k: 'bomber', enter: 1, delay: 150 },
      { g: 'C', k: 'rifle', enter: -1, delay: 220, look: 'qat' },
      { g: 'C2', k: 'rifle', x: 1800, plat: 'gallery', post: 1, look: 'worried' },
      { g: 'C2', k: 'rifle', door: 1, x: 1846, delay: 0, look: 'angry' },
      { g: 'C2', k: 'door', enter: 1, delay: 50, tag: 'd' },
      { g: 'C2', k: 'cook', enter: 1, delay: 50, dx: 38, behind: 'd' },
      { g: 'C2', k: 'rifle', door: 1, x: 1566, delay: 140, look: 'youth' },
      // ---- the hoist and the scales
      { g: 'D', k: 'rifle', x: 2280, post: 1, covered: 1, look: 'qat' },
      { g: 'D', k: 'cook', door: 1, x: 2124, delay: 20 },
      { g: 'D', k: 'rifle', enter: 1, delay: 60, look: 'angry' },
      { g: 'D', k: 'rifle', enter: 1, delay: 130, look: 'youth' },
      { g: 'D', k: 'bomber', enter: -1, delay: 200 },
      { g: 'D2', k: 'rifle', door: 1, x: 2124, delay: 0, look: 'worried' },
      { g: 'D2', k: 'rifle', door: 1, x: 2124, delay: 60, look: 'qat' },
      { g: 'D2', k: 'cook', enter: 1, delay: 30 },
      { g: 'D2', k: 'bomber', x: 2212, plat: 'pile2', post: 1 },
      // ---- the roasting house: the catwalk, and the vents in the floor
      { g: 'E', k: 'rifle', x: 2780, plat: 'catwalk', post: 1, look: 'angry' },
      { g: 'E', k: 'bomber', x: 2930, plat: 'catwalk', post: 1 },
      { g: 'E', k: 'cook', enter: 1, delay: 40 },
      { g: 'E', k: 'rifle', enter: 1, delay: 110, look: 'worried' },
      { g: 'E2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'E2', k: 'cook', enter: 1, delay: 0, dx: 38, behind: 'd' },
      { g: 'E2', k: 'rifle', enter: -1, delay: 80, look: 'youth' },
      { g: 'E2', k: 'rifle', x: 2950, plat: 'catwalk', post: 1, look: 'qat' },
      { g: 'F', k: 'cook', enter: 1, delay: 0 },
      { g: 'F', k: 'cook', enter: 1, delay: 100 },
      { g: 'F', k: 'rifle', door: 1, x: 3300, delay: 40, look: 'angry' },
      { g: 'F', k: 'bomber', enter: 1, delay: 170 },
      { g: 'F', k: 'rifle', enter: -1, delay: 230, look: 'worried' },
      { g: 'F2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'youth' },
      { g: 'F2', k: 'rifle', door: 1, x: 3300, delay: 70, look: 'qat' },
      { g: 'F2', k: 'cook', enter: 1, delay: 120 }
    ],
    props: [
      { k: 'crate', x: 300, gives: 'gren', zone: 0 },
      { k: 'drum', x: 664, paint: 'blue', zone: 0 },
      { k: 'crate', x: 768, plat: 'crane', gives: 'hmg', zone: 0 },
      { k: 'cover', x: 930, x0: 904, x1: 956, top: 164, art: 'sacks_cover', zone: 0 },
      { k: 'drum', x: 1060, paint: 'oxide', zone: 0 },
      { k: 'crate', x: 1530, plat: 'gallery', gives: 'hmg', zone: 1 },
      { k: 'detainee', x: 1730, plat: 'gallery', zone: 1 },
      { k: 'drum', x: 2020, paint: 'oxide', zone: 1 },
      { k: 'cover', x: 2280, x0: 2254, x1: 2306, top: 164, art: 'sacks_cover', zone: 1 },
      { k: 'vent', x: 2706, every: 150, phase: 0, zone: 2 },
      { k: 'vent', x: 2794, every: 150, phase: 75, zone: 2 },
      { k: 'drum', x: 3000, paint: 'blue', zone: 2 },
      { k: 'vent', x: 3086, every: 160, phase: 40, zone: 2 },
      { k: 'detainee', x: 3160, plat: 'catwalk', zone: 2 },
      { k: 'vent', x: 3176, every: 160, phase: 120, zone: 2 },
      { k: 'crate', x: 3236, gives: 'gren', zone: 2 },
      { k: 'vent', x: 3420, every: 140, phase: 20, zone: 2 },
      { k: 'crate', x: PT + 150, gives: 'hmg', zone: 3 }
    ],
    // ---- the old lighthouse: the Big Roaster comes down the slipway from behind it
    roaster: {
      left: PT + 216, right: PT + 666,             // the widest the fight can be
      enter: [END + 60, 184],                      // where it rolls in from
      home: PT + 560                               // where it likes to sit
    }
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL_MOCHA;
