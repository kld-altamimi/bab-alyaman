// level_ibb.js - Ibb, the Green Valleys (Mission 4), while it is being built: a test range for the Spokesman's screens,
// laid out on the Coffee Port's quay and warehouses (borrowed: Ibb's own stage comes with stage 3 of its plan). The
// billboard that opens the mission plays statement C; the shops' sets, by the fights further on, play a few lines each;
// the nearest one in the picture is the one heard (render_ibb.js). Nothing breaks them: they are scenery (Khaled, 24 Oct:
// people want to hear him; the speakers on poles, and their mechanic, were dropped the same day). Six ordinary fights,
// and somebody tied up at the end. Only test builds have it (build.py --ibb); the live game does not.
var LEVEL_IBB = (function () {
  'use strict';
  var Q = 0, WH = 1232, END = 2464;
  var L = {
    id: 'ibb',
    name: 'The Green Valleys',
    art: 'mocha',                      // (borrowed for the range)
    banner: 'THE GREEN VALLEYS',
    music: 'mocha', bossMusic: 'mocha',
    speech: true,                      // (his lines come in a file of their own, fetched with the mission: audio.js)
    birds: 'pigeon',
    lines: { start: [], clear: [[26, 'ann_complete', 8]] },
    freedNote: 'somebody is still tied up in the warehouse',
    width: END,
    height: 216,
    par: 180,
    start: 96,
    exitX: END - 44,
    restX: END - 20,
    endRight: END,
    ground: { step: 4, y: [184] },
    world: { Q: Q, WH: WH, ROAD_Y: 184 },
    plats: [
      // the quay (as the Coffee Port has it): the sacks, the dhow on its trestles, the crane
      { id: 'pile1', pts: [[182, 164], [248, 164]] },
      { id: 'pile1top', pts: [[198, 150], [232, 150]] },
      { id: 'step1', pts: [[370, 162], [396, 162]] },
      { id: 'deck', pts: [[404, 138], [520, 137], [600, 136]] },
      { id: 'poop', pts: [[600, 124], [648, 124]] },
      { id: 'crate2', pts: [[688, 166], [714, 166]] },
      { id: 'crane', pts: [[716, 142], [802, 142]] },
      { id: 'cab', pts: [[740, 108], [794, 108]] },
      // the warehouses: the steps of sacks up to the gallery, the pile by the hoist
      { id: 'sk1', pts: [[1436, 166], [1470, 166]] },
      { id: 'sk2', pts: [[1462, 148], [1500, 148]] },
      { id: 'gallery', pts: [[1500, 122], [1966, 122]] },
      { id: 'pile3', pts: [[1650, 158], [1700, 158]] },
      { id: 'pile2', pts: [[2180, 162], [2242, 162]] }
    ],
    zones: [
      { x: Q, name: 'The quay', spawn: 96 },
      { x: WH, name: 'The warehouses', spawn: WH - 40, indoor: true }
    ],
    gates: [
      { id: 'a', x: 560, groups: ['A'] },
      { id: 'b', x: 900, groups: ['B'] },
      { id: 'c', x: 1110, groups: ['C'] },
      { id: 'd', x: 1420, groups: ['D'] },
      { id: 'e', x: 2120, groups: ['E'] },
      { id: 'f', x: 2380, groups: ['F'] }
    ],
    groups: {
      A: { zone: 0, trig: 260 },
      B: { zone: 0, trig: 680, lastManSurrenders: true },
      C: { zone: 0, trig: 940, lastManSurrenders: true },
      D: { zone: 1, trig: 1260 },
      E: { zone: 1, trig: 1850, lastManSurrenders: true },
      F: { zone: 1, trig: 2160, lastManSurrenders: true }
    },
    // (a man at a post stands inside the middle of his gate's held screen: 133 px left of the gate to 106 right of it)
    spawns: [
      // ---- at the dhow's bow: three at their posts, one more walking in
      { g: 'A', k: 'rifle', x: 432, post: 1, look: 'worried' },
      { g: 'A', k: 'rifle', x: 492, post: 1, look: 'youth' },
      { g: 'A', k: 'rifle', x: 548, plat: 'deck', post: 1, look: 'qat' },
      { g: 'A', k: 'rifle', enter: 1, delay: 110, look: 'angry' },
      // ---- by the crane: one on its arm and a bomber in its cab, two on the quay, one from behind
      { g: 'B', k: 'rifle', x: 774, plat: 'crane', post: 1, look: 'angry' },
      { g: 'B', k: 'bomber', x: 780, plat: 'cab', post: 1 },
      { g: 'B', k: 'rifle', x: 812, post: 1, look: 'worried' },
      { g: 'B', k: 'rifle', x: 876, post: 1, look: 'youth' },
      { g: 'B', k: 'rifle', enter: -1, delay: 140, look: 'qat' },
      // ---- the stall's set, and the men watching it
      { g: 'C', k: 'rifle', x: 992, post: 1, look: 'qat' },
      { g: 'C', k: 'rifle', x: 1074, post: 1, look: 'angry' },
      { g: 'C', k: 'rifle', enter: 1, delay: 50, look: 'worried' },
      // ---- the warehouses: a set by the steps of sacks
      { g: 'D', k: 'rifle', x: 1300, post: 1, look: 'youth' },
      { g: 'D', k: 'rifle', x: 1386, post: 1, look: 'worried' },
      { g: 'D', k: 'rifle', x: 1482, plat: 'sk2', post: 1, look: 'angry' },
      { g: 'D', k: 'bomber', enter: 1, delay: 80 },
      // ---- a set under the gallery, and the men past its end
      { g: 'E', k: 'rifle', x: 2040, post: 1, look: 'worried' },
      { g: 'E', k: 'rifle', x: 2098, post: 1, look: 'qat' },
      { g: 'E', k: 'rifle', x: 2124, post: 1, look: 'angry' },
      { g: 'E', k: 'bomber', enter: 1, delay: 70 },
      // ---- the man they are holding
      { g: 'F', k: 'rifle', x: 2252, post: 1, look: 'youth' },
      { g: 'F', k: 'rifle', x: 2312, post: 1, look: 'worried' },
      { g: 'F', k: 'rifle', enter: 1, delay: 40, look: 'qat' },
      { g: 'F', k: 'rifle', enter: -1, delay: 160, look: 'angry' }
    ],
    props: [
      { k: 'crate', x: 330, gives: 'gren', zone: 0 },
      { k: 'crate', x: 1560, plat: 'gallery', gives: 'hmg', zone: 1 },
      { k: 'detainee', x: 2338, zone: 1 }
    ],
    // his screens: the billboard (statement C, the warning, whole) and the shops' sets, each with the lines it plays
    screens: [
      { x: 120, size: 'board', zone: 0, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 1032, size: 'tv', zone: 0, lines: ['sp_important', 'sp_B2', 'sp_B3'] },
      { x: 1338, size: 'tv', zone: 1, lines: ['sp_B4', 'sp_B5', 'sp_B6', 'sp_end'] },
      { x: 1890, size: 'tv', zone: 1, lines: ['sp_important', 'sp_D2', 'sp_D3', 'sp_D4', 'sp_D5', 'sp_D6'] },
      { x: 2282, size: 'tv', zone: 1, lines: ['sp_A2', 'sp_A3', 'sp_A4', 'sp_A6', 'sp_A7', 'sp_A8', 'sp_A11'] }
    ]
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL_IBB;
