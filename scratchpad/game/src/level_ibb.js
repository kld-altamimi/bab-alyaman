// level_ibb.js - Ibb, the Green Valleys (Mission 4), built zone by zone (Khaled, 24 Oct: he plays each one as it is
// painted). Zone 1, Wadi al-Sahul: the valley road up from Taiz, the morning after rain. The billboard at the start plays
// statement C; the Zanabeel's checkpoint across the road (sandbags, a booth with their flag, a set on a crate playing the
// first lines of statement A); a stone farmhouse (its yard wall, its store, its roof); a roadside shop (its awning, its
// roof, its set playing the next lines); a minibus that has given up, which turns out to be full of them. The screens are
// scenery (render_ibb.js): the nearest one in the picture is the one heard, shots pass them and nothing breaks them
// (Khaled, 24 Oct). The mission ends at the end of the zones painted so far. Only test builds have it (build.py --ibb).
// The ground is the road: flat, the walk line at 184. Platforms are the tops of things as mock/stage_ibb_z1.py paints
// them (gen/stage_ibb.json; unit_ibb.js checks that the two agree).
var LEVEL_IBB = (function () {
  'use strict';
  var Z1 = 0, END = 1280;                // where the zones start (one so far), and where the painted road ends
  var VERGE = 160;                       // the gravel verge behind the road: the screens stand on it
  var L = {
    id: 'ibb',
    name: 'The Green Valleys',
    art: 'ibb',
    banner: 'THE GREEN VALLEYS',
    music: 'ibb', bossMusic: 'ibb',      // (the Green Valleys' theme, 24 Oct; the Spokesman's own comes with his fight)
    speech: true,                        // (his lines come in a file of their own, fetched with the mission: audio.js)
    birds: 'pigeon',
    lines: { start: [], clear: [[26, 'ann_complete', 8]] },
    freedNote: 'the teacher is still at the flagpole',         // (the brief's; the teacher comes with zone 2)
    width: END,
    height: 216,
    par: 60,
    start: 96,
    exitX: END - 40,
    restX: END - 20,
    endRight: END,
    ground: { step: 4, y: [184] },
    world: { Z1: Z1, END: END, ROAD_Y: 184 },
    // one-way platforms: land on them from above, drop through with down + jump
    plats: [
      // the checkpoint: the sandbags on the road, the booth's roof (from the sandbags)
      { id: 'sandbags', pts: [[464, 162], [512, 162]] },
      { id: 'booth', pts: [[484, 118], [538, 116]] },
      // the farmhouse: the yard wall, the store's roof, the house's roof
      { id: 'yardwall', pts: [[726, 141], [778, 141]] },
      { id: 'store', pts: [[696, 125], [749, 125]] },
      { id: 'house', pts: [[613, 84], [695, 84]] },
      // the shop: its awning, its roof
      { id: 'awning', pts: [[810, 137], [958, 137]] },
      { id: 'shoproof', pts: [[817, 119], [951, 119]] },
      // the minibus: the luggage on its rack, the jerrycans by its back door
      { id: 'busrack', pts: [[1112, 127], [1164, 125], [1196, 129]] },
      { id: 'cans', pts: [[1214, 162], [1221, 162]] }
    ],
    zones: [
      { x: Z1, name: 'Wadi al-Sahul', spawn: 96 }
    ],
    gates: [
      { id: 'cp', x: 560, groups: ['A', 'A2'] },
      { id: 'farm', x: 800, groups: ['B', 'B2'] },
      { id: 'shop', x: 1000, groups: ['C', 'C2'] },
      { id: 'bus', x: 1170, groups: ['D', 'D2'] }
    ],
    groups: {
      A: { zone: 0, trig: 300 },
      A2: { zone: 0, after: 'A', delay: 30, lastManSurrenders: true },
      B: { zone: 0, trig: 640 },
      B2: { zone: 0, after: 'B', delay: 40, lastManSurrenders: true },
      C: { zone: 0, trig: 840 },
      C2: { zone: 0, after: 'C', delay: 40, lastManSurrenders: true },
      D: { zone: 0, trig: 1010 },
      D2: { zone: 0, after: 'D', delay: 30, lastManSurrenders: true }
    },
    // k: rifle | bomber | door. enter: 1 from the right edge, -1 from the left. door: out of the doorway at x.
    // A man at a post stands inside the middle of his gate's held screen: 133 px left of the gate to 106 right of it.
    spawns: [
      // ---- the checkpoint: one on the sandbags, one on the booth, one by the drums; then out of the booth
      { g: 'A', k: 'rifle', x: 486, plat: 'sandbags', post: 1, look: 'angry' },
      { g: 'A', k: 'rifle', x: 516, plat: 'booth', post: 1, look: 'qat' },
      { g: 'A', k: 'rifle', x: 594, post: 1, look: 'youth' },
      { g: 'A', k: 'bomber', enter: 1, delay: 90 },
      { g: 'A2', k: 'rifle', door: 1, x: 499, delay: 0, look: 'worried' },
      { g: 'A2', k: 'door', enter: 1, delay: 20, tag: 'd' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 20, dx: 34, behind: 'd', look: 'angry' },
      { g: 'A2', k: 'rifle', door: 1, x: 499, delay: 80, look: 'youth' },
      { g: 'A2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the farmhouse: on its roof, on the store, on the yard wall, in the road; then out of its door
      { g: 'B', k: 'rifle', x: 684, plat: 'house', post: 1, look: 'qat' },
      { g: 'B', k: 'bomber', x: 730, plat: 'store', post: 1 },
      { g: 'B', k: 'rifle', x: 768, plat: 'yardwall', post: 1, look: 'youth' },
      { g: 'B', k: 'rifle', x: 862, post: 1, look: 'angry' },
      { g: 'B2', k: 'rifle', door: 1, x: 649, delay: 0, look: 'worried' },
      { g: 'B2', k: 'rifle', door: 1, x: 649, delay: 60, look: 'angry' },
      { g: 'B2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'B2', k: 'rifle', enter: -1, delay: 110, look: 'youth' },
      // ---- the shop: on the awning, on its roof, in the road; then out of the shop, a man with a door
      { g: 'C', k: 'rifle', x: 894, plat: 'awning', post: 1, look: 'angry' },
      { g: 'C', k: 'rifle', x: 938, plat: 'shoproof', post: 1, look: 'worried' },
      { g: 'C', k: 'rifle', x: 1046, post: 1, look: 'qat' },
      { g: 'C', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'C', k: 'rifle', enter: 1, delay: 40, dx: 36, behind: 'd', look: 'youth' },
      { g: 'C2', k: 'rifle', door: 1, x: 916, delay: 0, look: 'youth' },
      { g: 'C2', k: 'bomber', enter: 1, delay: 30 },
      { g: 'C2', k: 'rifle', door: 1, x: 916, delay: 70, look: 'angry' },
      { g: 'C2', k: 'rifle', enter: -1, delay: 120, look: 'worried' },
      // ---- the minibus: one on the rack; then they keep coming out of it
      { g: 'D', k: 'rifle', x: 1150, plat: 'busrack', post: 1, look: 'qat' },
      { g: 'D', k: 'rifle', x: 1104, post: 1, look: 'angry' },
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 0, look: 'youth' },
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 40, look: 'worried' },
      { g: 'D2', k: 'bomber', door: 1, x: 1149, delay: 80 },
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 120, look: 'angry' },
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 160, look: 'qat' },
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 200, look: 'youth' }
    ],
    props: [
      { k: 'crate', x: 340, gives: 'gren', zone: 0 },
      { k: 'crate', x: 734, plat: 'store', gives: 'hmg', zone: 0 }
    ],
    // his screens: the billboard (statement C, the warning, whole) and the sets, each with the lines it plays (statement A
    // is told in pieces, a few lines a set, through the zones); they stand on the verge behind the road
    screens: [
      { x: 120, size: 'board', zone: 0, gy: VERGE + 4, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 548, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_important', 'sp_A2', 'sp_A3', 'sp_A4'] },
      { x: 860, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_A5', 'sp_A6', 'sp_A7', 'sp_A8'] }
    ]
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL_IBB;
