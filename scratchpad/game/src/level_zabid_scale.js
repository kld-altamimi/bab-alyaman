// level_zabid.js - The Souq: Zabid, on foot. The road in to the old town's gate, where the Dhanabs have a checkpoint and
// have piled a barricade in the gateway; the spice market inside the walls, stalls and sacks and balconies, and the
// market's own gate barricaded too; up a stair and over the rooftops, the roofs for ground and the gaps between the
// houses to jump; down into the yard of the covered market, barricaded a third time; and the long vaulted hall, where
// the Dhanabs' Weighmaster sits in one pan of the souq's Great Scale with the stolen spice in the other.
// The ground and the tops of things are as tools/stage_zabid.py paints them (unit8.js checks): flat at 184 but on the
// rooftops, where the ground is the roofs, gaps and all (walls: a step up of more than 7 px is a wall).
var LEVEL_ZABID = (function () {
  'use strict';
  var TG = 0, SS = 1280, RT = 2560, CM = 3880, END = 4864;      // the town gate, the spice stalls, the rooftops, the covered market
  var L = {
    id: 'zabid',
    name: 'The Souq',
    art: 'zabid',
    banner: 'THE SOUQ',
    music: 'souq', bossMusic: 'scale',
    sea: false,
    birds: 'pigeon',             // (outdoors here it is pigeons, not gulls)
    lines: { start: [[10, 'ann_souq', 4], [200, 'yazeed_souq', 1]], clear: [[26, 'ann_complete', 8], [215, 'yazeed_lunch', 8]] },
    freedNote: 'a shopkeeper is still tied up behind his counter',
    bossFact: 'Scale broken in',
    width: END,
    height: 216,
    par: 300,                    // seconds, for the Ace medal (about twice the careful bot's time)
    start: 96,
    exitX: END - 80,
    restX: END - 54,
    endRight: END,
    walls: true,                 // the rooftops: steps of more than STEP_UP are walls, edges are drops
    ground: null,                // (from the painting: GROUNDS.zabid in the page, gen/stage_zabid.json under Node)
    pits: [[2762, 2798], [2986, 3014], [3294, 3334]],
    world: { TG: TG, SS: SS, RT: RT, CM: CM, ROAD_Y: 184 },
    // one-way platforms: land on them from above, drop through with down + jump
    plats: [
      // the road: the spice seller's cart, the checkpoint's booth, the scaffold against the town wall
      { id: 'cart', pts: [[422, 158], [482, 158]] },
      { id: 'booth', pts: [[652, 127], [702, 127]] },
      { id: 'wc1', pts: [[1046, 166], [1070, 166]] },
      { id: 'wc2', pts: [[1068, 146], [1096, 146]] },
      { id: 'wallwalk', pts: [[1096, 120], [1180, 120]] },
      { id: 'b1back', pts: [[1236, 176], [1290, 176]] },
      // the market: balconies, and crates up to them
      { id: 'balc1', pts: [[1420, 118], [1500, 118]] },
      { id: 'balc2', pts: [[1790, 112], [1880, 112]] },
      { id: 'balc3', pts: [[2236, 120], [2304, 120]] },
      { id: 'cr1', pts: [[1380, 166], [1408, 166]] },
      { id: 'cr2', pts: [[1398, 144], [1424, 144]] },
      { id: 'cr3', pts: [[1752, 164], [1780, 164]] },
      { id: 'cr4', pts: [[1768, 140], [1794, 140]] },
      { id: 'cr5', pts: [[2200, 166], [2226, 166]] },
      { id: 'cr6', pts: [[2214, 146], [2238, 146]] },
      { id: 'b2back', pts: [[2436, 176], [2488, 176]] },
      // the rooftops: water tanks, stair-heads, a pigeon coop
      { id: 'tank1', pts: [[2621, 116], [2643, 116]] },
      { id: 'shead1', pts: [[2858, 114], [2902, 114]] },
      { id: 'tank2', pts: [[3063, 106], [3085, 106]] },
      { id: 'coop', pts: [[3150, 119], [3190, 119]] },
      { id: 'shead2', pts: [[3398, 116], [3442, 116]] },
      { id: 'tank3', pts: [[3491, 112], [3513, 112]] },
      // the covered market's yard: the step behind its barricade
      { id: 'b3back', pts: [[3806, 176], [3858, 176]] },
      // the Great Scale's spice pan: it rides up and down with the beam (scale.js moves it; dyn: each game has its own)
      { id: 'span', dyn: true, pts: [[4219, 176], [4261, 176]] }
    ],
    zones: [
      { x: TG, name: 'The town gate', spawn: 96 },
      { x: SS, name: 'The spice stalls', spawn: SS - 24 },
      { x: RT, name: 'The rooftops', spawn: RT - 14 },
      { x: CM, name: 'The covered market', spawn: CM - 30, indoor: true }
    ],
    // a gate with a wall waits for its barricade as well as its men
    gates: [
      { id: 't0', x: 680, groups: ['A', 'A2', 'B'] },
      { id: 't1', x: 1186, groups: ['W', 'W2'], wall: 'b1' },
      { id: 's0', x: 1760, groups: ['C', 'C2'] },
      { id: 's1', x: 2380, groups: ['D', 'D2'], wall: 'b2' },
      { id: 'r0', x: 2920, groups: ['E', 'E2'] },
      { id: 'r1', x: 3470, groups: ['F', 'F2'] },
      { id: 'r2', x: 3750, groups: ['G', 'G2'], wall: 'b3' },
      { id: 'gB', x: CM + 466, groups: ['BOSS'] }
    ],
    groups: {
      A: { zone: 0, trig: 250 },
      A2: { zone: 0, after: 'A', delay: 30 },
      B: { zone: 0, after: 'A2', delay: 40, lastManSurrenders: true },
      W: { zone: 0, trig: 1000 },
      W2: { zone: 0, wall: 'b1', delay: 16, lastManSurrenders: true },          // (when the barricade goes, the men behind it come through)
      C: { zone: 1, trig: 1560 },
      C2: { zone: 1, after: 'C', delay: 40, lastManSurrenders: true },
      D: { zone: 1, trig: 2170 },
      D2: { zone: 1, wall: 'b2', delay: 16, lastManSurrenders: true },
      E: { zone: 2, trig: 2700 },
      E2: { zone: 2, after: 'E', delay: 40, lastManSurrenders: true },
      F: { zone: 2, trig: 3280 },
      F2: { zone: 2, after: 'F', delay: 40, lastManSurrenders: true },
      G: { zone: 2, trig: 3610 },
      G2: { zone: 2, wall: 'b3', delay: 16, lastManSurrenders: true },
      BOSS: { zone: 3, hold: true, trig: CM + 230, noSurrender: true }
    },
    // k: rifle | bomber | door | cook. enter: 1 from the right edge, -1 from the left. door: out of the doorway at x.
    // A man at a post (post: 1) must stand inside the middle of his gate's held screen at every width, or he stays
    // guarded for ever: from 133 px left of the gate to 106 px right of it. unit8.js checks.
    // Behind a barricade the men are covered by it (covered: 1): they come up over it to shoot.
    spawns: [
      // ---- the checkpoint on the road
      { g: 'A', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'A', k: 'rifle', enter: 1, delay: 50, look: 'youth' },
      { g: 'A', k: 'bomber', enter: 1, delay: 140 },
      { g: 'A2', k: 'rifle', x: 680, plat: 'booth', post: 1, look: 'qat' },
      { g: 'A2', k: 'rifle', x: 762, post: 1, covered: 1, look: 'angry' },
      { g: 'A2', k: 'door', enter: 1, delay: 20, tag: 'd' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 20, dx: 34, behind: 'd', look: 'worried' },
      { g: 'B', k: 'bomber', x: 660, plat: 'booth', post: 1 },
      { g: 'B', k: 'cook', enter: 1, delay: 30 },
      { g: 'B', k: 'rifle', enter: -1, delay: 90, look: 'angry' },
      { g: 'B', k: 'rifle', enter: 1, delay: 160, look: 'youth' },
      // ---- the town gate: men on the scaffold, men behind the barricade in the gateway
      { g: 'W', k: 'rifle', x: 1124, plat: 'wallwalk', post: 1, look: 'youth' },
      { g: 'W', k: 'rifle', x: 1166, plat: 'wallwalk', post: 1, look: 'qat' },
      { g: 'W', k: 'rifle', x: 1254, plat: 'b1back', post: 1, covered: 1, look: 'angry' },
      { g: 'W', k: 'bomber', x: 1270, plat: 'b1back', post: 1, covered: 1 },
      { g: 'W', k: 'rifle', x: 1284, plat: 'b1back', post: 1, covered: 1, look: 'worried' },
      { g: 'W', k: 'rifle', enter: -1, delay: 120, look: 'angry' },
      { g: 'W2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'W2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'youth' },
      { g: 'W2', k: 'cook', enter: 1, delay: 60 },
      { g: 'W2', k: 'rifle', enter: 1, delay: 120, look: 'qat' },
      // ---- the middle of the spice market: the balcony over the street, the doors
      { g: 'C', k: 'rifle', x: 1812, plat: 'balc2', post: 1, look: 'angry' },
      { g: 'C', k: 'bomber', x: 1858, plat: 'balc2', post: 1 },
      { g: 'C', k: 'rifle', door: 1, x: 1708, delay: 30, look: 'youth' },
      { g: 'C', k: 'rifle', enter: 1, delay: 90, look: 'qat' },
      { g: 'C', k: 'cook', door: 1, x: 1964, delay: 150 },
      { g: 'C', k: 'rifle', enter: -1, delay: 220, look: 'worried' },
      { g: 'C2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'C2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'angry' },
      { g: 'C2', k: 'cook', door: 1, x: 1708, delay: 60 },
      { g: 'C2', k: 'bomber', enter: 1, delay: 130 },
      { g: 'C2', k: 'rifle', door: 1, x: 1964, delay: 170, look: 'youth' },
      // ---- the market's gate: the balcony by it, the barricade
      { g: 'D', k: 'rifle', x: 2262, plat: 'balc3', post: 1, look: 'qat' },
      { g: 'D', k: 'rifle', x: 2452, plat: 'b2back', post: 1, covered: 1, look: 'angry' },
      { g: 'D', k: 'bomber', x: 2466, plat: 'b2back', post: 1, covered: 1 },
      { g: 'D', k: 'rifle', x: 2480, plat: 'b2back', post: 1, covered: 1, look: 'youth' },
      { g: 'D', k: 'rifle', door: 1, x: 2290, delay: 60, look: 'worried' },
      { g: 'D', k: 'cook', enter: -1, delay: 160 },
      { g: 'D2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'D2', k: 'cook', enter: 1, delay: 0, dx: 38, behind: 'd' },
      { g: 'D2', k: 'rifle', enter: 1, delay: 70, look: 'angry' },
      { g: 'D2', k: 'rifle', door: 1, x: 2290, delay: 120, look: 'qat' },
      // ---- the rooftops: the first stair-head, the gap beyond it
      { g: 'E', k: 'rifle', x: 2884, plat: 'shead1', post: 1, look: 'youth' },
      { g: 'E', k: 'bomber', x: 2962, post: 1 },
      { g: 'E', k: 'rifle', door: 1, x: 2880, delay: 40, look: 'angry' },
      { g: 'E', k: 'rifle', enter: 1, delay: 100, look: 'qat' },
      { g: 'E', k: 'rifle', door: 1, x: 2880, delay: 170, look: 'worried' },
      { g: 'E2', k: 'cook', door: 1, x: 2880, delay: 0 },
      { g: 'E2', k: 'rifle', door: 1, x: 2880, delay: 50, look: 'angry' },
      { g: 'E2', k: 'bomber', enter: 1, delay: 90 },
      { g: 'E2', k: 'rifle', door: 1, x: 2880, delay: 140, look: 'youth' },
      // ---- the second stair-head and the tank by it
      { g: 'F', k: 'rifle', x: 3424, plat: 'shead2', post: 1, look: 'qat' },
      { g: 'F', k: 'rifle', x: 3502, plat: 'tank3', post: 1, look: 'worried' },
      { g: 'F', k: 'bomber', x: 3540, post: 1 },
      { g: 'F', k: 'rifle', door: 1, x: 3420, delay: 50, look: 'angry' },
      { g: 'F', k: 'cook', door: 1, x: 3420, delay: 150 },
      { g: 'F2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'youth' },
      { g: 'F2', k: 'bomber', door: 1, x: 3420, delay: 60 },
      { g: 'F2', k: 'rifle', enter: 1, delay: 140, look: 'angry' },
      // ---- the covered market's gate
      { g: 'G', k: 'rifle', x: 3820, plat: 'b3back', post: 1, covered: 1, look: 'angry' },
      { g: 'G', k: 'bomber', x: 3834, plat: 'b3back', post: 1, covered: 1 },
      { g: 'G', k: 'rifle', x: 3850, plat: 'b3back', post: 1, covered: 1, look: 'qat' },
      { g: 'G', k: 'rifle', enter: -1, delay: 80, look: 'youth' },
      { g: 'G', k: 'door', enter: -1, delay: 200 },
      { g: 'G2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'G2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'worried' },
      { g: 'G2', k: 'cook', enter: 1, delay: 70 },
      { g: 'G2', k: 'rifle', enter: 1, delay: 130, look: 'angry' }
    ],
    props: [
      // the road
      { k: 'crate', x: 262, gives: 'hmg', zone: 0 },
      { k: 'spice', x: 440, plat: 'cart', col: 'red', zone: 0 },
      { k: 'spice', x: 466, plat: 'cart', col: 'yel', zone: 0 },
      { k: 'spice', x: 618, col: 'red', zone: 0 },
      { k: 'drum', x: 716, paint: 'blue', zone: 0 },
      { k: 'cover', x: 750, x0: 724, x1: 778, top: 164, art: 'zbags', zone: 0 },
      { k: 'spice', x: 806, col: 'org', zone: 0 },
      { k: 'detainee', x: 922, look: 'shop_tea', gives: 'gren', zone: 0 },
      { k: 'crate', x: 1084, plat: 'wc2', gives: 'gren', zone: 0 },
      { k: 'spice', x: 1144, plat: 'wallwalk', col: 'yel', zone: 0 },
      { k: 'spice', x: 1244, plat: 'b1back', col: 'red', zone: 0 },
      { k: 'drum', x: 1170, paint: 'oxide', zone: 0 },        // (the first barricade has a drum by it, to show what a drum does to one; the others do not)
      { k: 'cover', bar: 'b1', x: 1219, x0: 1196, x1: 1290, top: 154, hp: 30, art: 'barr', zone: 0 },
      // the spice market
      { k: 'spice', x: 1352, col: 'red', zone: 1 },
      { k: 'crate', x: 1462, plat: 'balc1', gives: 'hmg', zone: 1 },
      { k: 'detainee', x: 1566, look: 'shop_spice', gives: 'gren', zone: 1 },
      { k: 'spice', x: 1644, col: 'yel', zone: 1 },
      { k: 'spice', x: 1700, col: 'red', zone: 1 },
      { k: 'spice', x: 1746, col: 'org', zone: 1 },
      { k: 'spice', x: 1836, plat: 'balc2', col: 'red', zone: 1 },
      { k: 'spice', x: 1906, col: 'yel', zone: 1 },
      { k: 'drum', x: 2010, paint: 'blue', zone: 1 },
      { k: 'detainee', x: 2104, look: 'shop_cloth', gives: 'hmg', zone: 1 },
      { k: 'spice', x: 2272, col: 'red', zone: 1 },
      { k: 'spice', x: 2332, col: 'org', zone: 1 },
      { k: 'spice', x: 2440, plat: 'b2back', col: 'yel', zone: 1 },
      { k: 'cover', bar: 'b2', x: 2413, x0: 2390, x1: 2488, top: 154, hp: 36, art: 'barr', zone: 1 },
      // the rooftops
      { k: 'crate', x: 2632, plat: 'tank1', gives: 'gren', zone: 2 },
      { k: 'spice', x: 2842, col: 'red', zone: 2 },
      { k: 'spice', x: 2928, col: 'red', zone: 2 },
      { k: 'detainee', x: 3120, zone: 2 },
      { k: 'crate', x: 3170, plat: 'coop', gives: 'hmg', zone: 2 },
      { k: 'spice', x: 3384, col: 'yel', zone: 2 },
      { k: 'spice', x: 3470, col: 'red', zone: 2 },
      { k: 'spice', x: 3834, plat: 'b3back', col: 'red', zone: 2 },
      { k: 'cover', bar: 'b3', x: 3783, x0: 3760, x1: 3858, top: 154, hp: 40, art: 'barr', zone: 2 },
      // the covered market
      { k: 'crate', x: CM + 150, gives: 'hmg', zone: 3 }
    ],
    // ---- the covered market: the Great Scale, the beam on its post a little left of the middle of the held screen
    scale: {
      x: CM + 422, y: 64,                          // the top of the column, where the beam turns (left of where the hall's
                                                   // near pier passes in front at the held screen, so it hides nothing)
      arm: 64, chain: 96,                          // half the beam; the chains, from its ends to the pans' floors
      pan: 'span'                                  // the spice pan's platform
    }
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL_ZABID;
