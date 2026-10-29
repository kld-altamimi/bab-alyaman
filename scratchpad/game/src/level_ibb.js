// level_ibb.js - Ibb, the Green Valleys (Mission 4), built zone by zone (Khaled, 24 Oct: he plays each one as it is
// painted). Zone 2, Jibla (below), follows. Zone 1, Wadi al-Sahul: the valley road up from Taiz, the morning after rain. The billboard at the start plays
// statement C; the Zanabeel's checkpoint across the road (sandbags, a booth with their flag, a set on a crate playing the
// first lines of statement A); a stone farmhouse (its yard wall, its store, its roof); a roadside shop (its awning, its
// roof, its set playing the next lines); a minibus that has given up, which turns out to be full of them. The screens are
// scenery (render_ibb.js): the nearest one in the picture is the one heard, shots pass them and nothing breaks them
// (Khaled, 24 Oct). Zone 2, Jibla: Queen Arwa's old town on its mountainside, the street along its foot, the town and
// the mosque up the slope behind (the mosque is background only: nothing is staged near it). Houses with a stepped alley
// up to a roof; the school, the Zanabeel's "course" now, its yard open to the street, sets playing statement B, the
// walkway along its upper floor, and the teacher tied to the flagpole (the mission's somebody to free); more houses and a
// second alley; a last shop; the way out toward the terraces. The classrooms are padlocked until the school's fight is
// over; then Yazeed opens each and the class runs home, his gun pointed at the ground while they are out (school.js;
// Khaled, 29 Oct: the storyboard "All good", the children redrawn in the cast's style), and the school's gate waits for
// every class to be out and away. Zone 3, the terraces (Khaled, 29 Oct 20:11: "Looks great": on from Jibla): the path
// out of town climbs the terraced mountainside a field wall at a time (each step a wall to hop up), past a field hut,
// across the stream below the falls on a slab bridge, past a boulder and a farmhouse, up to the Zanabeel's relay station
// on the top (its fence, its cabin, its mast) and their stage beside it: the deck, the blue curtain, their emblem and
// flag, the chairs set out for an audience, the camera, the podium. (The Spokesman's scene there comes once Khaled has
// seen its storyboard.) The mission ends at the end of the zones painted so far. Only test builds have it
// (build.py --ibb).
// The ground is the road, flat at 184, until the terraces, where it climbs in steps of 16 (walls: true: a step of more
// than 7 is a wall); it comes from the painting (GROUNDS.ibb in the page, gen/stage_ibb.json under Node), as the
// platforms do (the tops of things as mock/stage_ibb_z*.py paint them; unit_ibb.js checks that the two agree).
var LEVEL_IBB = (function () {
  'use strict';
  var Z1 = 0, Z2 = 1280, Z3 = 2640, END = 4080;    // where the zones start (three so far), and where the painting ends
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
    par: 160,
    start: 96,
    exitX: END - 40,
    restX: END - 20,
    endRight: END,
    walls: true,                         // (the terraces: a step up of more than 7 px is a wall)
    ground: null,                        // (from the painting: GROUNDS.ibb in the page, gen/stage_ibb.json under Node)
    world: { Z1: Z1, Z2: Z2, Z3: Z3, END: END, ROAD_Y: 184 },
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
      { id: 'cans', pts: [[1214, 162], [1221, 162]] },
      // Jibla: the first house's roof, the alley's steps up to the second's, the school's steps, its walkway and roof,
      // the upper street's alley (climbing to the left) up to the fourth house's roof, the low wall at the gap, the last roof
      { id: 'h1roof', pts: [[1337, 85], [1419, 85]] },
      { id: 'alleyA1', pts: [[1422, 157], [1437, 157]] },
      { id: 'alleyA2', pts: [[1434, 143], [1449, 143]] },
      { id: 'alleyA3', pts: [[1446, 129], [1461, 129]] },
      { id: 'alleyA4', pts: [[1458, 115], [1473, 115]] },
      { id: 'h2roof', pts: [[1477, 85], [1567, 85]] },
      { id: 'schoolstep1', pts: [[1668, 157], [1683, 157]] },
      { id: 'schoolstep2', pts: [[1680, 145], [1695, 145]] },
      { id: 'schoolstep3', pts: [[1692, 133], [1707, 133]] },
      { id: 'walkway', pts: [[1704, 122], [2024, 122]] },
      { id: 'schoolroof', pts: [[1708, 78], [2024, 78]] },
      { id: 'h4roof', pts: [[2051, 85], [2139, 85]] },
      { id: 'alleyB4', pts: [[2144, 115], [2159, 115]] },
      { id: 'alleyB3', pts: [[2156, 129], [2171, 129]] },
      { id: 'alleyB2', pts: [[2168, 143], [2183, 143]] },
      { id: 'alleyB1', pts: [[2180, 157], [2195, 157]] },
      { id: 'lowwall', pts: [[2284, 149], [2386, 149]] },
      { id: 'h6roof', pts: [[2391, 85], [2485, 85]] },
      // the terraces: the field hut's roof, the boulder, the farmhouse's roof, the relay station's cabin and the deck on its
      // mast, the stage
      { id: 'hutroof', pts: [[2876, 129], [2927, 129]] },
      { id: 'boulder', pts: [[3188, 126], [3212, 126]] },
      { id: 'farmroof', pts: [[3584, 78], [3653, 78]] },
      { id: 'cabinroof', pts: [[3704, 79], [3773, 79]] },
      { id: 'mastdeck', pts: [[3806, 78], [3834, 78]] },
      { id: 'stagedeck', pts: [[3937, 109], [4071, 109]] }
    ],
    zones: [
      { x: Z1, name: 'Wadi al-Sahul', spawn: 96 },
      { x: Z2, name: 'Jibla', spawn: Z2 + 30 },
      { x: Z3, name: 'The terraces', spawn: Z3 + 30 }
    ],
    gates: [
      { id: 'cp', x: 560, groups: ['A', 'A2'] },
      { id: 'farm', x: 800, groups: ['B', 'B2'] },
      { id: 'shop', x: 1000, groups: ['C', 'C2'] },
      { id: 'bus', x: 1170, groups: ['D', 'D2'] },
      { id: 'alley', x: 1560, groups: ['E', 'E2'] },
      { id: 'school', x: 1880, groups: ['F', 'F2'], until: 'school' },          // (and every class let out: school.js)
      { id: 'upper', x: 2200, groups: ['G', 'G2'] },
      { id: 'out', x: 2540, groups: ['H', 'H2'] },
      { id: 'hut', x: 2940, groups: ['I', 'I2'] },
      { id: 'falls', x: 3280, groups: ['J', 'J2'] },
      { id: 'farm2', x: 3620, groups: ['K', 'K2'] },
      { id: 'station', x: 3900, groups: ['L', 'L2'] }
    ],
    groups: {
      A: { zone: 0, trig: 300 },
      A2: { zone: 0, after: 'A', delay: 30, lastManSurrenders: true },
      B: { zone: 0, trig: 640 },
      B2: { zone: 0, after: 'B', delay: 40, lastManSurrenders: true },
      C: { zone: 0, trig: 840 },
      C2: { zone: 0, after: 'C', delay: 40, lastManSurrenders: true },
      D: { zone: 0, trig: 1010 },
      D2: { zone: 0, after: 'D', delay: 30, lastManSurrenders: true },
      E: { zone: 1, trig: 1390 },
      E2: { zone: 1, after: 'E', delay: 40, lastManSurrenders: true },
      F: { zone: 1, trig: 1700 },
      F2: { zone: 1, after: 'F', delay: 40, lastManSurrenders: true },
      G: { zone: 1, trig: 2030 },
      G2: { zone: 1, after: 'G', delay: 40, lastManSurrenders: true },
      H: { zone: 1, trig: 2390 },
      H2: { zone: 1, after: 'H', delay: 30, lastManSurrenders: true },
      I: { zone: 2, trig: 2780 },
      I2: { zone: 2, after: 'I', delay: 40, lastManSurrenders: true },
      J: { zone: 2, trig: 3100 },
      J2: { zone: 2, after: 'J', delay: 40, lastManSurrenders: true },
      K: { zone: 2, trig: 3440 },
      K2: { zone: 2, after: 'K', delay: 40, lastManSurrenders: true },
      L: { zone: 2, trig: 3700 },
      L2: { zone: 2, after: 'L', delay: 40, lastManSurrenders: true }
    },
    // k: rifle | bomber | door. enter: 1 from the right edge, -1 from the left. door: out of the doorway at x.
    // A man at a post stands inside the middle of his gate's held screen, outside the lanes the others walk in by, at every
    // width: 133 px left of the gate to 106 right of it, and near the end, where the screen stops at the level's end
    // rather than at the gate, inside that screen's middle (unit_ibb.js works it out for each gate).
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
      { g: 'D2', k: 'rifle', door: 1, x: 1149, delay: 200, look: 'youth' },
      // ---- Jibla, the alley: one on its steps, one on the roof it climbs to, one in the street; then out of the tall house
      { g: 'E', k: 'rifle', x: 1452, plat: 'alleyA3', post: 1, look: 'angry' },
      { g: 'E', k: 'rifle', x: 1528, plat: 'h2roof', post: 1, look: 'qat' },
      { g: 'E', k: 'rifle', x: 1630, post: 1, look: 'youth' },
      { g: 'E', k: 'bomber', enter: 1, delay: 80 },
      { g: 'E2', k: 'rifle', door: 1, x: 1597, delay: 0, look: 'worried' },
      { g: 'E2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'E2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'angry' },
      { g: 'E2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the school: two on the walkway, one on the roof, one in the yard; then out of the office, and more
      { g: 'F', k: 'rifle', x: 1790, plat: 'walkway', post: 1, look: 'angry' },
      { g: 'F', k: 'rifle', x: 1934, plat: 'walkway', post: 1, look: 'youth' },
      { g: 'F', k: 'bomber', x: 1876, plat: 'schoolroof', post: 1 },
      { g: 'F', k: 'rifle', x: 1966, post: 1, look: 'qat' },
      { g: 'F2', k: 'rifle', door: 1, x: 2011, delay: 0, look: 'worried' },
      { g: 'F2', k: 'rifle', door: 1, x: 2011, delay: 60, look: 'angry' },
      { g: 'F2', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 40, dx: 34, behind: 'd', look: 'youth' },
      { g: 'F2', k: 'rifle', enter: -1, delay: 140, look: 'qat' },
      // ---- the upper street: on the roof, on the alley's steps, out of two doors
      { g: 'G', k: 'rifle', x: 2100, plat: 'h4roof', post: 1, look: 'qat' },
      { g: 'G', k: 'rifle', x: 2163, plat: 'alleyB3', post: 1, look: 'angry' },
      { g: 'G', k: 'rifle', x: 2280, post: 1, look: 'worried' },
      { g: 'G2', k: 'rifle', door: 1, x: 2078, delay: 0, look: 'youth' },
      { g: 'G2', k: 'rifle', door: 1, x: 2237, delay: 40, look: 'angry' },
      { g: 'G2', k: 'bomber', enter: 1, delay: 70 },
      { g: 'G2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the way out: one on the last roof, two in the street; then more from the terraces
      { g: 'H', k: 'rifle', x: 2440, plat: 'h6roof', post: 1, look: 'angry' },
      { g: 'H', k: 'rifle', x: 2474, post: 1, look: 'youth' },
      { g: 'H', k: 'rifle', x: 2512, post: 1, look: 'qat' },
      { g: 'H2', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'H2', k: 'bomber', enter: 1, delay: 50 },
      { g: 'H2', k: 'rifle', enter: 1, delay: 100, look: 'angry' },
      // ---- the terraces, the field hut: one on its roof, one on each terrace; a bomber comes down the path; then out of the
      //      hut, and from both ends (from below, a man stops at the foot of the wall above him and shoots up)
      { g: 'I', k: 'rifle', x: 2908, plat: 'hutroof', post: 1, look: 'qat' },
      { g: 'I', k: 'rifle', x: 2840, post: 1, look: 'angry' },
      { g: 'I', k: 'rifle', x: 3010, post: 1, look: 'youth' },
      { g: 'I', k: 'bomber', enter: 1, delay: 80 },
      { g: 'I2', k: 'rifle', door: 1, x: 2893, delay: 0, look: 'worried' },
      { g: 'I2', k: 'rifle', enter: 1, delay: 40, look: 'angry' },
      { g: 'I2', k: 'rifle', door: 1, x: 2893, delay: 90, look: 'qat' },
      { g: 'I2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- the falls: one on the boulder, two on the terrace above; then a man with a door down the path, and more
      { g: 'J', k: 'rifle', x: 3200, plat: 'boulder', post: 1, look: 'angry' },
      { g: 'J', k: 'rifle', x: 3300, post: 1, look: 'worried' },
      { g: 'J', k: 'bomber', x: 3360, post: 1 },
      { g: 'J2', k: 'rifle', enter: 1, delay: 0, look: 'qat' },
      { g: 'J2', k: 'door', enter: 1, delay: 50, tag: 'd' },
      { g: 'J2', k: 'rifle', enter: 1, delay: 50, dx: 34, behind: 'd', look: 'youth' },
      { g: 'J2', k: 'rifle', enter: -1, delay: 130, look: 'angry' },
      // ---- the farmhouse: on its roof, on the terrace below it, on the top; then out of its door, and from both ends
      { g: 'K', k: 'rifle', x: 3624, plat: 'farmroof', post: 1, look: 'youth' },
      { g: 'K', k: 'rifle', x: 3512, post: 1, look: 'qat' },
      { g: 'K', k: 'rifle', x: 3690, post: 1, look: 'angry' },
      { g: 'K2', k: 'rifle', door: 1, x: 3601, delay: 0, look: 'worried' },
      { g: 'K2', k: 'bomber', door: 1, x: 3601, delay: 50 },
      { g: 'K2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'K2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- the relay station: on the cabin's roof, on the mast's deck, by the chairs, a bomber on the stage; then out of
      //      the cabin, and from both ends
      { g: 'L', k: 'rifle', x: 3768, plat: 'cabinroof', post: 1, look: 'angry' },
      { g: 'L', k: 'rifle', x: 3820, plat: 'mastdeck', post: 1, look: 'qat' },
      { g: 'L', k: 'rifle', x: 3880, post: 1, look: 'worried' },
      { g: 'L', k: 'bomber', x: 3952, plat: 'stagedeck', post: 1 },
      { g: 'L2', k: 'rifle', door: 1, x: 3760, delay: 0, look: 'youth' },
      { g: 'L2', k: 'rifle', enter: -1, delay: 30, look: 'angry' },
      { g: 'L2', k: 'rifle', door: 1, x: 3760, delay: 60, look: 'qat' },
      { g: 'L2', k: 'rifle', enter: 1, delay: 100, look: 'worried' }
    ],
    props: [
      { k: 'crate', x: 340, gives: 'gren', zone: 0 },
      { k: 'crate', x: 734, plat: 'store', gives: 'hmg', zone: 0 },
      { k: 'crate', x: 1500, plat: 'h2roof', gives: 'gren', zone: 1 },
      { k: 'detainee', x: 1856, zone: 1 },                   // the teacher, tied to his own flagpole
      { k: 'crate', x: 2120, plat: 'h4roof', gives: 'hmg', zone: 1 },
      { k: 'crate', x: 2884, plat: 'hutroof', gives: 'gren', zone: 2 },
      { k: 'crate', x: 3644, plat: 'farmroof', gives: 'hmg', zone: 2 }
    ],
    // the stage on the top of the terraces (render_ibb.js draws the podium on its deck; the Spokesman's scene there comes
    // with Khaled's yes to its storyboard)
    stage: { x0: 3936, x1: 4072, deck: 109, podium: 4031 },
    // the school's three classrooms (school.js): where their doors are, how many children each holds; the yard's floor;
    // the teacher, at his flagpole, waits for them once freed and then goes after them
    school: { gate: 'school', y: 184, teacher: 1856, doors: [{ x: 1754, n: 5 }, { x: 1854, n: 4 }, { x: 1954, n: 5 }] },
    // his screens: the billboard (statement C, the warning, whole) and the sets, each with the lines it plays (statement A
    // is told in pieces, a few lines a set, through the zones); they stand on the verge behind the road
    screens: [
      { x: 120, size: 'board', zone: 0, gy: VERGE + 4, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 548, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_important', 'sp_A2', 'sp_A3', 'sp_A4'] },
      { x: 860, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_A5', 'sp_A6', 'sp_A7', 'sp_A8'] },
      { x: 1372, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_ops', 'sp_end', 'sp_A11'] },
      { x: 1800, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_important', 'sp_B2', 'sp_B3'] },
      { x: 1912, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_B4', 'sp_B5', 'sp_B6', 'sp_end'] },
      { x: 2430, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4'] },
      { x: 2696, size: 'tv', zone: 2, gy: 174, lines: ['sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 3420, size: 'tv', zone: 2, gy: 126, lines: ['sp_A7', 'sp_A8', 'sp_A11'] }
    ]
  };
  return L;
})();
if (typeof module !== 'undefined') {
  LEVEL_IBB.ground = require('../gen/stage_ibb.json').ground;      // (in the page main.js gives it GROUNDS.ibb, the same)
  module.exports = LEVEL_IBB;
}
