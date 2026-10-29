// level_ibb.js - Ibb, the Green Valleys (Mission 4), built zone by zone (Khaled, 24 Oct: he plays each one as it is
// painted). Zone 1, Wadi al-Sahul: the valley road up from Taiz, the morning after rain. The billboard at the start plays
// statement C; the Zanabeel's checkpoint across the road (sandbags, a booth with their flag, a set on a crate playing the
// first lines of statement A); a stone farmhouse (its yard wall, its store, its roof); a roadside shop (its awning, its
// roof, its set playing the next lines); a minibus that has given up, which turns out to be full of them; the bridge over
// the wadi (their sandbags on it, a man on its parapet); a petrol station at the town's edge (its canopy, its kiosk, a set
// playing the warning again). The screens are scenery (render_ibb.js): the nearest one in the picture is the one heard,
// shots pass them and nothing breaks them (Khaled, 24 Oct). Zone 2, Jibla: Queen Arwa's old town on its mountainside,
// the valley's asphalt breaking up over the setts at its edge, the street along its foot, the town and the mosque up the
// slope behind (the mosque is background only: nothing is staged near it). Houses with a stepped alley up to a roof; the
// school, the Zanabeel's "course" now, its yard open to the street, sets playing statement B, the walkway along its upper
// floor, and the teacher tied to the flagpole (the mission's somebody to free); more houses and a second alley; a last
// house; the souq under its awnings; the ruin of Dar al-Izz, Queen Arwa's palace; the way out between field walls. The
// classrooms are padlocked until the school's fight is over; then Yazeed opens each and the class runs home, his gun
// pointed at the ground while they are out (school.js; Khaled, 29 Oct: the storyboard "All good", the children redrawn
// in the cast's style), and the school's gate waits for every class to be out and away. Zone 3, the terraces (Khaled, 29
// Oct 20:11: "Looks great"): the path out of town climbs the terraced mountainside a field wall at a time (each step a
// wall to hop up), past a field hut, across the stream below the falls on a slab bridge, past a boulder and a farmhouse,
// through a hamlet on the top terrace (a tower house, a stepped alley up to a roof, the cistern, a last house), to the
// Zanabeel's relay station (its fence, its cabin, its mast) and their stage beside it: the deck, the blue curtain, their
// emblem and flag, the chairs set out for an audience, the camera, the podium. The Spokesman is there, giving statement
// D to five of his men in the chairs, who clap; once the station is cleared and Yazeed comes up to the chairs, "Nice
// beret.", the jump (no trousers under the podium) and his dash for the pass (rally.js; Khaled, 29 Oct 21:36: "The story
// board looks great"); the station's gate waits for him to be gone. The path runs on past the stage to the pass. Each
// zone is about half as long again since 29 Oct (Khaled, 21:36: "the zones in this mission are a bit short"), and they
// are painted as one picture, so the joins are seamless. Zone 4, Sumara pass (Khaled, 29 Oct 23:11: "Great, continue to
// next"): the highway climbing to the pass in cloud, cut into the mountainside (the rock above, a retaining wall, kerbs
// painted black and white, a crash barrier on the drop's side, the next hairpin below, the valley full of cloud); their
// post in a shipping container with sandbags across the road, a tea shack with a tin awning, the summit's rock, marker and
// flag; then the lookout at the top, where they have set out five podiums with a screen each for the Spokesman and parked
// their broadcast van. Three fights; then his (spokesman.js, as the storyboard Khaled passed on 30 Oct 00:39: "Go ahead
// and finish the whole level"): cut off at his microphone, podium by podium, caught in his own cable; the screens back
// on with him still speaking (the ear, two Yemens); the back room in their van, three of the Uncle's men and a rack
// marked RENDER; every screen dark; the cloud clearing onto the Dhamar plateau. The mission opens with Salem dropping
// Yazeed under the billboard (opening.js).
// Only test builds have it (build.py --ibb).
// The ground is the road, flat at 184, until the terraces, where it climbs in steps of 16 (walls: true: a step of more
// than 7 is a wall); it comes from the painting (GROUNDS.ibb in the page, gen/stage_ibb.json under Node), as the
// platforms do (the tops of things as mock/stage_ibb_*.py paint them; unit_ibb.js checks that the two agree).
var LEVEL_IBB = (function () {
  'use strict';
  var Z1 = 0, Z2 = 2080, Z3 = 4080, Z4 = 6200, END = 8200;    // where the zones start, and where the painting ends
  var VERGE = 160;                       // the gravel verge behind the road: the screens stand on it
  var L = {
    id: 'ibb',
    name: 'The Green Valleys',
    art: 'ibb',
    banner: 'THE GREEN VALLEYS',
    music: 'ibb', bossMusic: 'spokesman',    // (the Green Valleys' theme, 24 Oct; the Spokesman's own for his fight, 30 Oct)
    speech: true,                        // (his lines come in a file of their own, fetched with the mission: audio.js)
    birds: 'pigeon',
    lines: { start: [], clear: [[26, 'ann_complete', 8]] },
    freedNote: 'the teacher is still at the flagpole',         // (the brief's; the teacher comes with zone 2)
    bossFact: 'Statement interrupted in',
    width: END,
    height: 216,
    par: 360,
    start: 96,
    exitX: END - 90,                     // (past the van at the lookout's far end, once the reveal is over)
    restX: END - 10,
    endRight: END,
    walls: true,                         // (the terraces: a step up of more than 7 px is a wall)
    ground: null,                        // (from the painting: GROUNDS.ibb in the page, gen/stage_ibb.json under Node)
    world: { Z1: Z1, Z2: Z2, Z3: Z3, Z4: Z4, END: END, ROAD_Y: 184 },
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
      // the bridge: its parapet's top rail, their sandbags on it; the petrol station: its canopy, its kiosk's roof
      { id: 'parapet', pts: [[1302, 152], [1598, 152]] },
      { id: 'bridgebags', pts: [[1426, 162], [1466, 162]] },
      { id: 'canopy', pts: [[1665, 102], [1781, 102]] },
      { id: 'kiosk', pts: [[1799, 129], [1872, 129]] },
      // Jibla: the first house's roof, the alley's steps up to the second's, the school's steps, its walkway and roof,
      // the upper street's alley (climbing to the left) up to the fourth house's roof, the low wall at the gap, the last
      // roof; the souq's roofs and awnings; the ruin's broken tops (the long front, the low stretch, the fallen stones)
      { id: 'h1roof', pts: [[2137, 85], [2219, 85]] },
      { id: 'alleyA1', pts: [[2222, 157], [2237, 157]] },
      { id: 'alleyA2', pts: [[2234, 143], [2249, 143]] },
      { id: 'alleyA3', pts: [[2246, 129], [2261, 129]] },
      { id: 'alleyA4', pts: [[2258, 115], [2273, 115]] },
      { id: 'h2roof', pts: [[2277, 85], [2367, 85]] },
      { id: 'schoolstep1', pts: [[2468, 157], [2483, 157]] },
      { id: 'schoolstep2', pts: [[2480, 145], [2495, 145]] },
      { id: 'schoolstep3', pts: [[2492, 133], [2507, 133]] },
      { id: 'walkway', pts: [[2504, 122], [2824, 122]] },
      { id: 'schoolroof', pts: [[2508, 78], [2824, 78]] },
      { id: 'h4roof', pts: [[2851, 85], [2939, 85]] },
      { id: 'alleyB4', pts: [[2944, 115], [2959, 115]] },
      { id: 'alleyB3', pts: [[2956, 129], [2971, 129]] },
      { id: 'alleyB2', pts: [[2968, 143], [2983, 143]] },
      { id: 'alleyB1', pts: [[2980, 157], [2995, 157]] },
      { id: 'lowwall', pts: [[3084, 149], [3186, 149]] },
      { id: 'h6roof', pts: [[3191, 85], [3285, 85]] },
      { id: 'souqroofA', pts: [[3293, 85], [3389, 85]] },
      { id: 'souqawn1', pts: [[3295, 135], [3387, 135]] },
      { id: 'souqroofC', pts: [[3507, 85], [3611, 85]] },
      { id: 'souqawn2', pts: [[3509, 135], [3609, 135]] },
      { id: 'ruinwall', pts: [[3719, 99], [3775, 99]] },
      { id: 'rubble', pts: [[3825, 151], [3839, 151]] },
      { id: 'ruinlow', pts: [[3831, 129], [3877, 129]] },
      // the terraces: the field hut's roof, the boulder, the farmhouse's roof; the hamlet's steps up to a roof, the
      // cistern's rim, the last house's roof; the relay station's cabin and the deck on its mast, the stage
      { id: 'hutroof', pts: [[4316, 129], [4367, 129]] },
      { id: 'boulder', pts: [[4628, 126], [4652, 126]] },
      { id: 'farmroof', pts: [[5024, 78], [5093, 78]] },
      { id: 'hamstep1', pts: [[5192, 101], [5209, 101]] },
      { id: 'hamstep2', pts: [[5206, 90], [5223, 90]] },
      { id: 'hamstep3', pts: [[5220, 79], [5237, 79]] },
      { id: 'hamroof', pts: [[5238, 77], [5303, 77]] },
      { id: 'birkarim', pts: [[5316, 108], [5443, 108]] },
      { id: 'lastroof', pts: [[5456, 79], [5515, 79]] },
      { id: 'cabinroof', pts: [[5664, 79], [5733, 79]] },
      { id: 'mastdeck', pts: [[5766, 78], [5794, 78]] },
      { id: 'stagedeck', pts: [[5897, 109], [6031, 109]] },
      // the pass: their sandbags across the road by the container, the tea shack's roof and its awning, the summit's rock
      { id: 'cpnest', pts: [[6784, 98], [6820, 98]] },
      { id: 'shackroof', pts: [[7060, 79], [7123, 79]] },
      { id: 'shackawn', pts: [[7083, 87], [7153, 87]] },
      { id: 'summitrock', pts: [[7397, 89], [7423, 89]] }
    ],
    zones: [
      { x: Z1, name: 'Wadi al-Sahul', spawn: 96 },
      { x: Z2, name: 'Jibla', spawn: Z2 + 30 },
      { x: Z3, name: 'The terraces', spawn: Z3 + 30 },
      { x: Z4, name: 'Sumara pass', spawn: Z4 + 30 }
    ],
    gates: [
      { id: 'cp', x: 560, groups: ['A', 'A2'] },
      { id: 'farm', x: 800, groups: ['B', 'B2'] },
      { id: 'shop', x: 1000, groups: ['C', 'C2'] },
      { id: 'bus', x: 1170, groups: ['D', 'D2'] },
      { id: 'bridge', x: 1500, groups: ['M', 'M2'] },
      { id: 'petrol', x: 1820, groups: ['N', 'N2'] },
      { id: 'alley', x: 2360, groups: ['E', 'E2'] },
      { id: 'school', x: 2680, groups: ['F', 'F2'], until: 'school' },          // (and every class let out: school.js)
      { id: 'upper', x: 3000, groups: ['G', 'G2'] },
      { id: 'lasthouse', x: 3340, groups: ['H', 'H2'] },
      { id: 'souq', x: 3580, groups: ['O', 'O2'] },
      { id: 'palace', x: 3860, groups: ['P', 'P2'] },
      { id: 'hut', x: 4380, groups: ['I', 'I2'] },
      { id: 'falls', x: 4720, groups: ['J', 'J2'] },
      { id: 'farm2', x: 5060, groups: ['K', 'K2'] },
      { id: 'hamlet', x: 5300, groups: ['R', 'R2'] },
      { id: 'cistern', x: 5560, groups: ['S', 'S2'] },
      { id: 'station', x: 5850, groups: ['L', 'L2'], until: 'rally' },         // (and the Spokesman gone: rally.js)
      { id: 'post', x: 6800, groups: ['T', 'T2'] },
      { id: 'shack', x: 7180, groups: ['U', 'U2'] },
      { id: 'summit', x: 7470, groups: ['V', 'V2'] },
      { id: 'arena', x: 7840, groups: ['BOSS'] },                                // (the held screen centred on the five podiums)
      { id: 'van', x: 8100, groups: ['BOSS'], until: 'spokesman', quiet: true }  // (and the reveal over: spokesman.js)
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
      M: { zone: 0, trig: 1330 },
      M2: { zone: 0, after: 'M', delay: 40, lastManSurrenders: true },
      N: { zone: 0, trig: 1660 },
      N2: { zone: 0, after: 'N', delay: 40, lastManSurrenders: true },
      E: { zone: 1, trig: 2190 },
      E2: { zone: 1, after: 'E', delay: 40, lastManSurrenders: true },
      F: { zone: 1, trig: 2500 },
      F2: { zone: 1, after: 'F', delay: 40, lastManSurrenders: true },
      G: { zone: 1, trig: 2830 },
      G2: { zone: 1, after: 'G', delay: 40, lastManSurrenders: true },
      H: { zone: 1, trig: 3190 },
      H2: { zone: 1, after: 'H', delay: 30, lastManSurrenders: true },
      O: { zone: 1, trig: 3420 },
      O2: { zone: 1, after: 'O', delay: 40, lastManSurrenders: true },
      P: { zone: 1, trig: 3700 },
      P2: { zone: 1, after: 'P', delay: 40, lastManSurrenders: true },
      I: { zone: 2, trig: 4220 },
      I2: { zone: 2, after: 'I', delay: 40, lastManSurrenders: true },
      J: { zone: 2, trig: 4540 },
      J2: { zone: 2, after: 'J', delay: 40, lastManSurrenders: true },
      K: { zone: 2, trig: 4880 },
      K2: { zone: 2, after: 'K', delay: 40, lastManSurrenders: true },
      R: { zone: 2, trig: 5150 },
      R2: { zone: 2, after: 'R', delay: 40, lastManSurrenders: true },
      S: { zone: 2, trig: 5400 },
      S2: { zone: 2, after: 'S', delay: 40, lastManSurrenders: true },
      L: { zone: 2, trig: 5660 },
      L2: { zone: 2, after: 'L', delay: 40, lastManSurrenders: true },
      T: { zone: 3, trig: 6620 },
      T2: { zone: 3, after: 'T', delay: 40, lastManSurrenders: true },
      U: { zone: 3, trig: 7000 },
      U2: { zone: 3, after: 'U', delay: 40, lastManSurrenders: true },
      V: { zone: 3, trig: 7290 },
      V2: { zone: 3, after: 'V', delay: 40, lastManSurrenders: true },
      BOSS: { zone: 3, hold: true, trig: 7660, noSurrender: true }
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
      // ---- the bridge: one behind their sandbags, one on the parapet, one on the road; a bomber comes over; then a man
      //      with a door, and from both ends
      { g: 'M', k: 'rifle', x: 1446, plat: 'bridgebags', post: 1, look: 'angry' },
      { g: 'M', k: 'rifle', x: 1530, plat: 'parapet', post: 1, look: 'qat' },
      { g: 'M', k: 'rifle', x: 1584, post: 1, look: 'youth' },
      { g: 'M', k: 'bomber', enter: 1, delay: 90 },
      { g: 'M2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'M2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'worried' },
      { g: 'M2', k: 'bomber', enter: 1, delay: 70 },
      { g: 'M2', k: 'rifle', enter: -1, delay: 120, look: 'angry' },
      // ---- the petrol station: on the canopy, on the kiosk's roof, a bomber on the forecourt, one by the sign; then out of
      //      the kiosk, and from both ends
      { g: 'N', k: 'rifle', x: 1722, plat: 'canopy', post: 1, look: 'worried' },
      { g: 'N', k: 'rifle', x: 1846, plat: 'kiosk', post: 1, look: 'angry' },
      { g: 'N', k: 'bomber', x: 1760, post: 1 },
      { g: 'N', k: 'rifle', x: 1890, post: 1, look: 'qat' },
      { g: 'N2', k: 'rifle', door: 1, x: 1815, delay: 0, look: 'youth' },
      { g: 'N2', k: 'rifle', enter: 1, delay: 30, look: 'angry' },
      { g: 'N2', k: 'rifle', door: 1, x: 1815, delay: 70, look: 'qat' },
      { g: 'N2', k: 'rifle', enter: -1, delay: 120, look: 'worried' },
      // ---- Jibla, the alley: one on its steps, one on the roof it climbs to, one in the street; then out of the tall house
      { g: 'E', k: 'rifle', x: 2252, plat: 'alleyA3', post: 1, look: 'angry' },
      { g: 'E', k: 'rifle', x: 2328, plat: 'h2roof', post: 1, look: 'qat' },
      { g: 'E', k: 'rifle', x: 2430, post: 1, look: 'youth' },
      { g: 'E', k: 'bomber', enter: 1, delay: 80 },
      { g: 'E2', k: 'rifle', door: 1, x: 2397, delay: 0, look: 'worried' },
      { g: 'E2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'E2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'angry' },
      { g: 'E2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the school: two on the walkway, one on the roof, one in the yard; then out of the office, and more
      { g: 'F', k: 'rifle', x: 2590, plat: 'walkway', post: 1, look: 'angry' },
      { g: 'F', k: 'rifle', x: 2734, plat: 'walkway', post: 1, look: 'youth' },
      { g: 'F', k: 'bomber', x: 2676, plat: 'schoolroof', post: 1 },
      { g: 'F', k: 'rifle', x: 2766, post: 1, look: 'qat' },
      { g: 'F2', k: 'rifle', door: 1, x: 2811, delay: 0, look: 'worried' },
      { g: 'F2', k: 'rifle', door: 1, x: 2811, delay: 60, look: 'angry' },
      { g: 'F2', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 40, dx: 34, behind: 'd', look: 'youth' },
      { g: 'F2', k: 'rifle', enter: -1, delay: 140, look: 'qat' },
      // ---- the upper street: on the roof, on the alley's steps, out of two doors
      { g: 'G', k: 'rifle', x: 2900, plat: 'h4roof', post: 1, look: 'qat' },
      { g: 'G', k: 'rifle', x: 2963, plat: 'alleyB3', post: 1, look: 'angry' },
      { g: 'G', k: 'rifle', x: 3080, post: 1, look: 'worried' },
      { g: 'G2', k: 'rifle', door: 1, x: 2878, delay: 0, look: 'youth' },
      { g: 'G2', k: 'rifle', door: 1, x: 3037, delay: 40, look: 'angry' },
      { g: 'G2', k: 'bomber', enter: 1, delay: 70 },
      { g: 'G2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the last house: one on its roof, two in the street; then more from the souq
      { g: 'H', k: 'rifle', x: 3240, plat: 'h6roof', post: 1, look: 'angry' },
      { g: 'H', k: 'rifle', x: 3274, post: 1, look: 'youth' },
      { g: 'H', k: 'rifle', x: 3312, post: 1, look: 'qat' },
      { g: 'H2', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'H2', k: 'bomber', enter: 1, delay: 50 },
      { g: 'H2', k: 'rifle', enter: 1, delay: 100, look: 'angry' },
      // ---- the souq: one on an awning, one on the roof over it, a bomber among the stalls, one in the street; then out of
      //      the tall house, a man with a door, and one from behind
      { g: 'O', k: 'rifle', x: 3540, plat: 'souqawn2', post: 1, look: 'qat' },
      { g: 'O', k: 'rifle', x: 3592, plat: 'souqroofC', post: 1, look: 'angry' },
      { g: 'O', k: 'bomber', x: 3474, post: 1 },
      { g: 'O', k: 'rifle', x: 3646, post: 1, look: 'youth' },
      { g: 'O2', k: 'rifle', door: 1, x: 3432, delay: 0, look: 'worried' },
      { g: 'O2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'O2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'angry' },
      { g: 'O2', k: 'rifle', door: 1, x: 3432, delay: 80, look: 'qat' },
      { g: 'O2', k: 'rifle', enter: -1, delay: 130, look: 'youth' },
      // ---- Dar al-Izz: one on the long front's broken top, a bomber on the low stretch, two at its foot; then out of its
      //      gateway, and from both ends
      { g: 'P', k: 'rifle', x: 3746, plat: 'ruinwall', post: 1, look: 'qat' },
      { g: 'P', k: 'bomber', x: 3856, plat: 'ruinlow', post: 1 },
      { g: 'P', k: 'rifle', x: 3790, post: 1, look: 'worried' },
      { g: 'P', k: 'rifle', x: 3912, post: 1, look: 'angry' },
      { g: 'P2', k: 'rifle', door: 1, x: 3748, delay: 0, look: 'youth' },
      { g: 'P2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'P2', k: 'rifle', door: 1, x: 3748, delay: 60, look: 'angry' },
      { g: 'P2', k: 'bomber', door: 1, x: 3748, delay: 100 },
      { g: 'P2', k: 'rifle', enter: -1, delay: 140, look: 'worried' },
      // ---- the terraces, the field hut: one on its roof, one on each terrace; a bomber comes down the path; then out of the
      //      hut, and from both ends (from below, a man stops at the foot of the wall above him and shoots up)
      { g: 'I', k: 'rifle', x: 4348, plat: 'hutroof', post: 1, look: 'qat' },
      { g: 'I', k: 'rifle', x: 4280, post: 1, look: 'angry' },
      { g: 'I', k: 'rifle', x: 4450, post: 1, look: 'youth' },
      { g: 'I', k: 'bomber', enter: 1, delay: 80 },
      { g: 'I2', k: 'rifle', door: 1, x: 4333, delay: 0, look: 'worried' },
      { g: 'I2', k: 'rifle', enter: 1, delay: 40, look: 'angry' },
      { g: 'I2', k: 'rifle', door: 1, x: 4333, delay: 90, look: 'qat' },
      { g: 'I2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- the falls: one on the boulder, two on the terrace above; then a man with a door down the path, and more
      { g: 'J', k: 'rifle', x: 4640, plat: 'boulder', post: 1, look: 'angry' },
      { g: 'J', k: 'rifle', x: 4740, post: 1, look: 'worried' },
      { g: 'J', k: 'bomber', x: 4800, post: 1 },
      { g: 'J2', k: 'rifle', enter: 1, delay: 0, look: 'qat' },
      { g: 'J2', k: 'door', enter: 1, delay: 50, tag: 'd' },
      { g: 'J2', k: 'rifle', enter: 1, delay: 50, dx: 34, behind: 'd', look: 'youth' },
      { g: 'J2', k: 'rifle', enter: -1, delay: 130, look: 'angry' },
      // ---- the farmhouse: on its roof, on the terrace below it, on the top; then out of its door, and from both ends
      { g: 'K', k: 'rifle', x: 5064, plat: 'farmroof', post: 1, look: 'youth' },
      { g: 'K', k: 'rifle', x: 4952, post: 1, look: 'qat' },
      { g: 'K', k: 'rifle', x: 5130, post: 1, look: 'angry' },
      { g: 'K2', k: 'rifle', door: 1, x: 5041, delay: 0, look: 'worried' },
      { g: 'K2', k: 'bomber', door: 1, x: 5041, delay: 50 },
      { g: 'K2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'K2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- the hamlet: one on the alley's first step, a bomber on the roof it climbs to, one on the cistern's rim, one on
      //      the path; then out of the tower house and the house beside it, and from both ends
      { g: 'R', k: 'rifle', x: 5200, plat: 'hamstep1', post: 1, look: 'youth' },
      { g: 'R', k: 'bomber', x: 5276, plat: 'hamroof', post: 1 },
      { g: 'R', k: 'rifle', x: 5340, plat: 'birkarim', post: 1, look: 'qat' },
      { g: 'R', k: 'rifle', x: 5384, post: 1, look: 'angry' },
      { g: 'R2', k: 'rifle', door: 1, x: 5155, delay: 0, look: 'worried' },
      { g: 'R2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'R2', k: 'rifle', door: 1, x: 5255, delay: 80, look: 'angry' },
      { g: 'R2', k: 'rifle', enter: -1, delay: 130, look: 'youth' },
      // ---- the cistern: one on its rim, one on the last roof, a bomber and one on the path; then a man with a door, and
      //      from both ends
      { g: 'S', k: 'rifle', x: 5440, plat: 'birkarim', post: 1, look: 'angry' },
      { g: 'S', k: 'rifle', x: 5490, plat: 'lastroof', post: 1, look: 'qat' },
      { g: 'S', k: 'bomber', x: 5550, post: 1 },
      { g: 'S', k: 'rifle', x: 5604, post: 1, look: 'worried' },
      { g: 'S2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'S2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'youth' },
      { g: 'S2', k: 'rifle', enter: 1, delay: 60, look: 'angry' },
      { g: 'S2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the relay station: on the cabin's roof, on the mast's deck, by the camera, a bomber on the stage; then out of
      //      the cabin, and from both ends
      { g: 'L', k: 'rifle', x: 5728, plat: 'cabinroof', post: 1, look: 'angry' },
      { g: 'L', k: 'rifle', x: 5780, plat: 'mastdeck', post: 1, look: 'qat' },
      { g: 'L', k: 'rifle', x: 5800, post: 1, look: 'worried' },
      { g: 'L', k: 'bomber', x: 5912, plat: 'stagedeck', post: 1 },
      { g: 'L2', k: 'rifle', door: 1, x: 5720, delay: 0, look: 'youth' },
      { g: 'L2', k: 'rifle', enter: -1, delay: 30, look: 'angry' },
      { g: 'L2', k: 'rifle', door: 1, x: 5720, delay: 60, look: 'qat' },
      { g: 'L2', k: 'rifle', enter: 1, delay: 100, look: 'worried' },
      // ---- the pass, their post: one behind the sandbags across the road, a bomber in front of the container, one by the
      //      drum; then out of the container, a man with a door, and one from behind
      { g: 'T', k: 'rifle', x: 6800, plat: 'cpnest', post: 1, look: 'angry' },
      { g: 'T', k: 'bomber', x: 6730, post: 1 },
      { g: 'T', k: 'rifle', x: 6870, post: 1, look: 'qat' },
      { g: 'T2', k: 'rifle', door: 1, x: 6690, delay: 0, look: 'youth' },
      { g: 'T2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'T2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'worried' },
      { g: 'T2', k: 'rifle', door: 1, x: 6690, delay: 80, look: 'angry' },
      { g: 'T2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the tea shack: one on its roof, one on its awning, one on the road; a bomber comes down the road; then out of
      //      its door, and from both ends
      { g: 'U', k: 'rifle', x: 7100, plat: 'shackroof', post: 1, look: 'qat' },
      { g: 'U', k: 'rifle', x: 7146, plat: 'shackawn', post: 1, look: 'youth' },
      { g: 'U', k: 'rifle', x: 7250, post: 1, look: 'angry' },
      { g: 'U', k: 'bomber', enter: 1, delay: 80 },
      { g: 'U2', k: 'rifle', door: 1, x: 7074, delay: 0, look: 'worried' },
      { g: 'U2', k: 'rifle', enter: 1, delay: 30, look: 'qat' },
      { g: 'U2', k: 'rifle', door: 1, x: 7074, delay: 80, look: 'angry' },
      { g: 'U2', k: 'rifle', enter: -1, delay: 130, look: 'youth' },
      // ---- the summit: one on the rock, a bomber by their flag, one at the top of the road; then down from the lookout,
      //      a man with a door, and one from behind
      { g: 'V', k: 'rifle', x: 7410, plat: 'summitrock', post: 1, look: 'angry' },
      { g: 'V', k: 'bomber', x: 7484, post: 1 },
      { g: 'V', k: 'rifle', x: 7540, post: 1, look: 'worried' },
      { g: 'V2', k: 'rifle', enter: 1, delay: 0, look: 'youth' },
      { g: 'V2', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'V2', k: 'rifle', enter: 1, delay: 40, dx: 34, behind: 'd', look: 'qat' },
      { g: 'V2', k: 'rifle', enter: -1, delay: 120, look: 'angry' }
    ],
    props: [
      { k: 'crate', x: 340, gives: 'gren', zone: 0 },
      { k: 'crate', x: 734, plat: 'store', gives: 'hmg', zone: 0 },
      { k: 'crate', x: 1838, plat: 'kiosk', gives: 'gren', zone: 0 },
      { k: 'crate', x: 2300, plat: 'h2roof', gives: 'gren', zone: 1 },
      { k: 'detainee', x: 2656, zone: 1 },                   // the teacher, tied to his own flagpole
      { k: 'crate', x: 2920, plat: 'h4roof', gives: 'hmg', zone: 1 },
      { k: 'crate', x: 3340, plat: 'souqroofA', gives: 'gren', zone: 1 },
      { k: 'crate', x: 4324, plat: 'hutroof', gives: 'gren', zone: 2 },
      { k: 'crate', x: 5084, plat: 'farmroof', gives: 'hmg', zone: 2 },
      { k: 'crate', x: 5482, plat: 'lastroof', gives: 'gren', zone: 2 },
      { k: 'crate', x: 7066, plat: 'shackroof', gives: 'gren', zone: 3 },
      { k: 'crate', x: 7330, gives: 'hmg', zone: 3 }
    ],
    // the stage on the top of the terraces (rally.js; render_ibb.js draws it): its deck, his podium on it, the chairs his
    // audience sits in (the back row's three, then the front row's two: x where the hips come, y the seat; painted chairs,
    // mock/stage_ibb_z3.py), the statement he gives; the station's gate waits for him
    stage: { gate: 'station', x0: 5896, x1: 6032, deck: 109, podium: 5991,
             seats: [[5825, 104], [5849, 104], [5873, 104], [5842, 109], [5866, 109]],
             lines: ['sp_important', 'sp_D2', 'sp_D3', 'sp_D4', 'sp_D5', 'sp_D6', 'sp_D7', 'sp_important', 'sp_D9', 'sp_end'] },
    // the school's three classrooms (school.js): where their doors are, how many children each holds; the yard's floor;
    // the teacher, at his flagpole, waits for them once freed and then goes after them
    school: { gate: 'school', y: 184, teacher: 2656, doors: [{ x: 2554, n: 5 }, { x: 2654, n: 4 }, { x: 2754, n: 5 }] },
    // the lookout at the top of the pass: its floor, the five podiums they have set out for him, each with its screen on a
    // stand behind it (his fight on them: spokesman.js; render_spokesman.js draws it all), their van at the far end
    arena: { x0: 7550, x1: 8160, y: 120, podiums: [7680, 7760, 7840, 7920, 8000], van: { x0: 8072, x1: 8152, door: [8096, 8118], roof: 75, sill: 106 },
             // what he says from his podiums, by phase ([line, ticks it lasts]): calm, putting statement A right; shouting the
             // warning (C); at the last podium in the dark, reading by torchlight. And what the screens say once he is caught (E)
             lines: { 1: [['sp_important', 95], ['sp_A4', 178], ['sp_A6', 132], ['sp_A7', 126], ['sp_A8', 82], ['sp_A5', 188]],
                      2: [['sp_C3', 198], ['sp_C4', 90], ['sp_C5', 90], ['sp_C6', 88], ['sp_C7', 143]],
                      3: [['sp_A11', 107], ['sp_end', 88], ['sp_D9', 97], ['sp_important', 95]],
                      E: ['sp_important', 'sp_E2', 'sp_E3', 'sp_E4', 'sp_E5', 'sp_E6', 'sp_E7', 'sp_ops', 'sp_E9', 'sp_end'] } },
    // the opening: Salem's 4x4 up the road from off the left of the picture, stopping under the billboard (opening.js)
    opening: { from: -90, stop: 176 },
    // Yazeed's word at a place (main.js): the Queen Arwa mosque over the low wall in Jibla's upper street (the back layer's
    // mosque is in the middle of the picture with Yazeed here)
    remarks: [{ x: 3040, id: 'yazeed_mosque' }],
    // his screens: the billboard (statement C, the warning, whole) and the sets, each with the lines it plays (statement A
    // is told in pieces, a few lines a set, through the zones); they stand on the verge behind the road
    screens: [
      { x: 120, size: 'board', zone: 0, gy: VERGE + 4, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 548, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_important', 'sp_A2', 'sp_A3', 'sp_A4'] },
      { x: 860, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_A5', 'sp_A6', 'sp_A7', 'sp_A8'] },
      { x: 1940, size: 'tv', zone: 0, gy: VERGE + 10, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 2172, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_ops', 'sp_end', 'sp_A11'] },
      { x: 2600, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_important', 'sp_B2', 'sp_B3'] },
      { x: 2712, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_B4', 'sp_B5', 'sp_B6', 'sp_end'] },
      { x: 3230, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4'] },
      { x: 3460, size: 'tv', zone: 1, gy: VERGE + 10, lines: ['sp_important', 'sp_A2', 'sp_A3', 'sp_A4', 'sp_A5', 'sp_A6'] },
      { x: 4136, size: 'tv', zone: 2, gy: 174, lines: ['sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 4860, size: 'tv', zone: 2, gy: 126, lines: ['sp_A7', 'sp_A8', 'sp_A11'] },
      { x: 5592, size: 'tv', zone: 2, gy: 110, lines: ['sp_important', 'sp_B2', 'sp_B3', 'sp_B4'] },
      { x: 6644, size: 'tv', zone: 3, gy: 110, lines: ['sp_important', 'sp_C2', 'sp_C3', 'sp_C4', 'sp_C5', 'sp_C6', 'sp_C7', 'sp_end'] },
      { x: 7036, size: 'tv', zone: 3, gy: 110, lines: ['sp_B4', 'sp_B5', 'sp_B6', 'sp_end'] }
    ]
  };
  return L;
})();
if (typeof module !== 'undefined') {
  LEVEL_IBB.ground = require('../gen/stage_ibb.json').ground;      // (in the page main.js gives it GROUNDS.ibb, the same)
  module.exports = LEVEL_IBB;
}
