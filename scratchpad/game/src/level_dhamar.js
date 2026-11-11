// level_dhamar.js - Dhamar, the Wadi (Mission 5), from game-direction's brief (draft 4) and the stage plan Khaled
// approved on 10 Nov; zones 1-3 built straight through as one test build (Khaled, 11 Nov 03:25: "let's go with your
// plan"); the pass and the Committee's meeting on the lorries (zone 4) come after a check-in with him.
// Zone 1, Qa' Jahran, on wheels: Salem drives the 4x4 north up the highway across the plain at harvest, Yazeed up in its
// roof ring with the gun (drive.js, the coast road's rules). Three of the Committee's checkpoints are the fights: a stamp
// hut, sandbags and a pole with speakers on the verge, a barrier across the road that breaks when the 4x4 goes through it
// or a grenade goes off by it (the gun up in the roof ring fires over it), and his men in the road; at each one somebody
// in the queue (men of the plateau, not the Zanabeel: scenery) asks about the wages and the
// speakers laugh back, and a banknote or two blows across the road (Yazeed doesn't stop for them: the 4x4 going through
// one counts it as wages returned). The convoy's lorries pass the other way on the far lane, loaded with the drafted.
// Salem stops at Dhamar's old gate; Yazeed walks.
// Zone 2, Dhamar: through the gate into the old town: the souq (a drafted cook among their men there leaves his gas torch
// behind when he gives up or goes down: the flamethrower, Khaled's "Yes" 11 Nov 03:33), an alley up to a roof, the school
// the Committee has made his recruiting office (its three classrooms padlocked along the yard and let out as Ibb's are:
// school.js), the Leader's silent screen on the office wall (a pointing finger; nothing breaks it), his painted face over
// the stamp window, and the teacher from Ibb held at the office, drafted as his own pupils' sergeant (the mission's
// somebody to free); past it the university's gate and the street out west. No money in this zone (the brief).
// Zone 3, Hammam Ali: the road down into the hot springs' valley, the village, the pools, the old bathhouse, the car
// park where the convoy waits; and on the ground beside it the Committee in person, holding his vote at his table with
// its microphones, the gathering's hands up through the steam: someone asks about the wages, he laughs, a coin rings on
// the stone, "Noted." He and the gathering are scenery (rally.js, as Ibb's rally): shots and the torch's flame pass them,
// nothing touches them. Once the car park is cleared and Yazeed comes up, "One man. Whole committee."; his hands up alone,
// "Motion denied."; he drafts the gathering ("Drafted. Report Tuesday.") and herds it off to the convoy, and the way on
// opens. The test build ends there, with "Good. A hot bath." (and so its par is the whole mission's, not these three zones').
// Only test builds have it (build.py --dhamar).
var LEVEL_DHAMAR = (function () {
  'use strict';
  var Z2 = 6200, Z3 = 8600, END = 10600;
  var L = {
    id: 'dhamar',
    name: 'The Wadi',
    art: 'dhamar',
    banner: 'THE WADI',
    music: 'dhamar', bossMusic: 'dhamar',      // (his own theme comes with the fight)
    speech: true,                              // (the Committee's lines and the mission's new ones: audio/speech_dhamar.mp3)
    lines: { start: [[10, 'ann_wadi', 4], [190, 'salem_checkpoint', 5]], clear: [[26, 'ann_complete', 8], [200, 'yazeed_bath', 6]] },      // (from a later checkpoint, the announcer's alone)
    freedNote: 'the teacher is still in the office',
    freedLine: 'teacher_pupils',               // (what the teacher says when he is freed)
    kidLine: 'yazeed_home_d',                  // (Yazeed to the first child out: Ibb's line, in this mission's lines)
    outLine: 'salem_stamp',                    // (Salem at the old gate, where the road ends: "The stamp said left.")
    birds: 'pigeon',
    bossFact: 'Pockets emptied in',
    width: END,
    height: 216,
    par: 330,
    start: 140,
    exitX: END - 50,                           // (the test's end: past the vote, once he has gone)
    restX: END - 10,
    endRight: END,
    ground: null,                              // (from the painting: GROUNDS.dhamar in the page, gen/stage_dhamar.json under Node)
    world: { Z1: 0, Z2: Z2, Z3: Z3, END: END, ROAD_Y: 184 },
    // one-way platforms: land on them from above, drop through with down + jump (the tops of things as painted:
    // mock/stage_dhamar.py; unit_dhamar.js checks the two agree)
    plats: [
      // the souq: the stalls' awnings, a low house's roof, the alley's steps up to the high roof
      { id: 'stall31', pts: [[6604, 134], [6674, 134]] },
      { id: 'souqroof1', pts: [[6762, 122], [6850, 122]] },
      { id: 'stall32', pts: [[6870, 134], [6940, 134]] },
      { id: 'stall33', pts: [[7064, 134], [7134, 134]] },
      { id: 'alley1', pts: [[7137, 171], [7150, 171]] },
      { id: 'alley2', pts: [[7149, 157], [7162, 157]] },
      { id: 'alley3', pts: [[7161, 143], [7174, 143]] },
      { id: 'alley4', pts: [[7173, 129], [7186, 129]] },
      { id: 'alleyroof', pts: [[7188, 86], [7280, 86]] },
      // the recruiting office: its stair, the walkway along the upper floor, the roof
      { id: 'schoolstep1', pts: [[7297, 171], [7309, 171]] },
      { id: 'schoolstep2', pts: [[7308, 156], [7320, 156]] },
      { id: 'schoolstep3', pts: [[7319, 141], [7331, 141]] },
      { id: 'schoolstep4', pts: [[7330, 126], [7342, 126]] },
      { id: 'walkway', pts: [[7342, 124], [7818, 124]] },
      { id: 'officeroof', pts: [[7344, 76], [7816, 76]] },
      // past it: a low roof, the university gate's lintel, another low roof
      { id: 'lowroof3', pts: [[7882, 120], [7962, 120]] },
      { id: 'unilintel', pts: [[8092, 70], [8238, 70]] },
      { id: 'lowroof4', pts: [[8272, 122], [8358, 122]] },
      // Hammam Ali: the village's roofs, the bathhouse's roof between its domes
      { id: 'vroof1', pts: [[8702, 122], [8786, 122]] },
      { id: 'vroof2', pts: [[8902, 118], [8978, 118]] },
      { id: 'vroof3', pts: [[9422, 122], [9508, 122]] },
      { id: 'bathroof1', pts: [[9624, 94], [9660, 94]] },
      { id: 'bathroof2', pts: [[9720, 94], [9754, 94]] }
    ],
    zones: [
      { x: 0, name: 'Qa\' Jahran', spawn: 140, drive: true },
      { x: Z2, name: 'Dhamar', spawn: Z2 + 96, parked: true },
      { x: Z3, name: 'Hammam Ali', spawn: Z3 + 40 }
    ],
    gates: [
      { id: 'gatefight', x: 6720, groups: ['G', 'G2'] },
      { id: 'souq', x: 7020, groups: ['S', 'S2'] },
      { id: 'alley', x: 7300, groups: ['A', 'A2'] },
      // (and every class let out: school.js. The gate holds the picture with all three classrooms in it and in reach on
      // the narrowest screen; the teacher at the stamp window beyond is freed once it opens)
      { id: 'school', x: 7560, groups: ['F', 'F2'], until: 'school' },
      { id: 'office', x: 8040, groups: ['O', 'O2'] },
      { id: 'uni', x: 8380, groups: ['U', 'U2'] },
      { id: 'edge', x: 8880, groups: ['V', 'V2'] },
      { id: 'village', x: 9200, groups: ['W', 'W2'] },
      { id: 'pools', x: 9500, groups: ['P', 'P2'] },
      { id: 'bath', x: 9900, groups: ['B', 'B2'] },
      { id: 'vote', x: 10500, groups: ['C', 'C2'], until: 'rally' }              // (and the Committee gone: rally.js)
    ],
    groups: {
      ROAD: { zone: 0, hold: true, noSurrender: true },                         // (whoever is standing on the highway)
      G: { zone: 1, trig: 6560 },
      G2: { zone: 1, after: 'G', delay: 30, lastManSurrenders: true },
      S: { zone: 1, trig: 6840 },
      S2: { zone: 1, after: 'S', delay: 40, lastManSurrenders: true },
      A: { zone: 1, trig: 7130 },
      A2: { zone: 1, after: 'A', delay: 40, lastManSurrenders: true },
      F: { zone: 1, trig: 7380 },
      F2: { zone: 1, after: 'F', delay: 40, lastManSurrenders: true },
      O: { zone: 1, trig: 7880 },
      O2: { zone: 1, after: 'O', delay: 40, lastManSurrenders: true },
      U: { zone: 1, trig: 8210 },
      U2: { zone: 1, after: 'U', delay: 40, lastManSurrenders: true },
      V: { zone: 2, trig: 8720 },
      V2: { zone: 2, after: 'V', delay: 40, lastManSurrenders: true },
      W: { zone: 2, trig: 9040 },
      W2: { zone: 2, after: 'W', delay: 40, lastManSurrenders: true },
      P: { zone: 2, trig: 9340 },
      P2: { zone: 2, after: 'P', delay: 40, lastManSurrenders: true },
      B: { zone: 2, trig: 9720 },
      B2: { zone: 2, after: 'B', delay: 40, lastManSurrenders: true },
      C: { zone: 2, trig: 10080 },
      C2: { zone: 2, after: 'C', delay: 40, lastManSurrenders: true }
    },
    // k: rifle | bomber | door. enter: 1 from the right edge, -1 from the left. door: out of the doorway at x.
    // (gives: what he leaves when he goes down or gives up: the drafted cook's gas torch, the flamethrower)
    spawns: [
      // ---- through the gate: one on the first stall's awning, two in the street; then out of the towers' doors
      { g: 'G', k: 'rifle', x: 6640, plat: 'stall31', post: 1, look: 'angry' },
      { g: 'G', k: 'rifle', x: 6700, post: 1, look: 'youth' },
      { g: 'G', k: 'rifle', x: 6760, post: 1, look: 'qat' },
      { g: 'G', k: 'bomber', enter: 1, delay: 80 },
      { g: 'G2', k: 'rifle', door: 1, x: 6617, delay: 0, look: 'worried' },
      { g: 'G2', k: 'rifle', door: 1, x: 6730, delay: 40, look: 'angry' },
      { g: 'G2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'G2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'youth' },
      { g: 'G2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the souq: on the low house's roof, on a stall, in the street, and the drafted cook among them; then out of
      //      the doors, and one from behind
      { g: 'S', k: 'rifle', x: 6930, plat: 'stall32', post: 1, look: 'angry' },
      { g: 'S', k: 'rifle', x: 6892, plat: 'stall32', post: 1, look: 'qat' },
      { g: 'S', k: 'cook', x: 6980, post: 1, look: 'drafted', gives: 'flame' },
      { g: 'S', k: 'rifle', x: 7040, post: 1, look: 'youth' },
      { g: 'S2', k: 'rifle', door: 1, x: 7002, delay: 0, look: 'worried' },
      { g: 'S2', k: 'bomber', enter: 1, delay: 30 },
      { g: 'S2', k: 'rifle', door: 1, x: 7002, delay: 90, look: 'angry' },
      { g: 'S2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- the alley: one on its steps, one on the high roof, one on the last stall; then a man with a door, and more
      { g: 'A', k: 'rifle', x: 7168, plat: 'alley3', post: 1, look: 'qat' },
      { g: 'A', k: 'rifle', x: 7240, plat: 'alleyroof', post: 1, look: 'angry' },
      { g: 'A', k: 'bomber', x: 7202, plat: 'alleyroof', post: 1 },
      { g: 'A', k: 'rifle', x: 7300, post: 1, look: 'youth' },
      { g: 'A2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'worried' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 60, look: 'angry' },
      { g: 'A2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the recruiting office: two on the walkway, one on the roof, one in the yard; then out of the office, and more
      { g: 'F', k: 'rifle', x: 7470, plat: 'walkway', post: 1, look: 'angry' },
      { g: 'F', k: 'rifle', x: 7640, plat: 'walkway', post: 1, look: 'youth' },
      { g: 'F', k: 'bomber', x: 7560, plat: 'officeroof', post: 1 },
      { g: 'F', k: 'rifle', x: 7662, post: 1, look: 'qat' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 60, look: 'angry' },
      { g: 'F2', k: 'door', enter: 1, delay: 40, tag: 'd' },
      { g: 'F2', k: 'rifle', enter: 1, delay: 40, dx: 34, behind: 'd', look: 'youth' },
      { g: 'F2', k: 'rifle', enter: -1, delay: 140, look: 'qat' },
      // ---- past the office: one on the low roof, two in the street; then out of two doors
      { g: 'O', k: 'rifle', x: 7920, plat: 'lowroof3', post: 1, look: 'qat' },
      { g: 'O', k: 'rifle', x: 8010, post: 1, look: 'angry' },
      { g: 'O', k: 'rifle', x: 8080, post: 1, look: 'worried' },
      { g: 'O2', k: 'rifle', door: 1, x: 7922, delay: 0, look: 'youth' },
      { g: 'O2', k: 'rifle', door: 1, x: 8020, delay: 40, look: 'angry' },
      { g: 'O2', k: 'bomber', enter: 1, delay: 70 },
      { g: 'O2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the university's gate: one up on its lintel, one on the low roof, one in the street; then a man with a door,
      //      out of the house, and one from behind
      { g: 'U', k: 'rifle', x: 8282, plat: 'lowroof4', post: 1, look: 'angry' },
      { g: 'U', k: 'rifle', x: 8344, plat: 'lowroof4', post: 1, look: 'youth' },
      { g: 'U', k: 'rifle', x: 8420, post: 1, look: 'qat' },
      { g: 'U2', k: 'rifle', door: 1, x: 8315, delay: 0, look: 'worried' },
      { g: 'U2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'U2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'angry' },
      { g: 'U2', k: 'rifle', enter: -1, delay: 120, look: 'youth' },
      // ---- Hammam Ali's edge: one on a roof, two on the road; then out of the doors
      { g: 'V', k: 'rifle', x: 8772, plat: 'vroof1', post: 1, look: 'qat' },
      { g: 'V', k: 'rifle', x: 8840, post: 1, look: 'angry' },
      { g: 'V', k: 'bomber', x: 8930, plat: 'vroof2', post: 1 },
      { g: 'V2', k: 'rifle', door: 1, x: 8870, delay: 90, look: 'youth' },
      { g: 'V2', k: 'rifle', door: 1, x: 8870, delay: 50, look: 'worried' },
      { g: 'V2', k: 'rifle', enter: 1, delay: 30, look: 'angry' },
      { g: 'V2', k: 'rifle', enter: -1, delay: 120, look: 'qat' },
      // ---- the village: on the road between the pools, a man with a door; then more from both ends
      { g: 'W', k: 'rifle', x: 9100, post: 1, look: 'angry' },
      { g: 'W', k: 'rifle', x: 9200, post: 1, look: 'youth' },
      { g: 'W', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'W', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'qat' },
      { g: 'W2', k: 'rifle', enter: -1, delay: 0, look: 'worried' },
      { g: 'W2', k: 'bomber', enter: 1, delay: 40 },
      { g: 'W2', k: 'rifle', enter: 1, delay: 80, look: 'angry' },
      { g: 'W2', k: 'rifle', enter: -1, delay: 130, look: 'youth' },
      // ---- the pools: one on the roof, two on the road beside the water; then out of the house, and from both ends
      { g: 'P', k: 'rifle', x: 9460, plat: 'vroof3', post: 1, look: 'qat' },
      { g: 'P', k: 'rifle', x: 9384, post: 1, look: 'angry' },
      { g: 'P', k: 'rifle', x: 9540, post: 1, look: 'worried' },
      { g: 'P2', k: 'rifle', door: 1, x: 9465, delay: 0, look: 'youth' },
      { g: 'P2', k: 'rifle', enter: 1, delay: 30, look: 'angry' },
      { g: 'P2', k: 'bomber', enter: 1, delay: 80 },
      { g: 'P2', k: 'rifle', enter: -1, delay: 130, look: 'qat' },
      // ---- the bathhouse: two on its roof between the domes, two in front of it; then from both ends, and a man with a door
      { g: 'B', k: 'rifle', x: 9786, post: 1, look: 'angry' },
      { g: 'B', k: 'bomber', x: 9860, post: 1 },
      { g: 'B', k: 'rifle', x: 9800, post: 1, look: 'youth' },
      { g: 'B', k: 'rifle', x: 9930, post: 1, look: 'qat' },
      { g: 'B2', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'B2', k: 'rifle', enter: -1, delay: 70, look: 'angry' },
      { g: 'B2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'B2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'youth' },
      { g: 'B2', k: 'rifle', enter: -1, delay: 140, look: 'qat' },
      // ---- the car park: among the lorries; then from both ends
      { g: 'C', k: 'rifle', x: 10280, post: 1, look: 'angry' },
      { g: 'C', k: 'bomber', x: 10340, post: 1 },
      { g: 'C', k: 'rifle', x: 10420, post: 1, look: 'qat' },
      { g: 'C2', k: 'rifle', enter: 1, delay: 0, look: 'youth' },
      { g: 'C2', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'C2', k: 'rifle', enter: 1, delay: 30, dx: 34, behind: 'd', look: 'worried' },
      { g: 'C2', k: 'rifle', enter: -1, delay: 110, look: 'angry' }
    ],
    props: [
      { k: 'crate', x: 6660, gives: 'gren', zone: 1 },
      { k: 'crate', x: 7230, plat: 'alleyroof', gives: 'hmg', zone: 1 },
      { k: 'detainee', x: 7640, zone: 1 },                   // the teacher, held at the office as its sergeant (in reach while the school's gate holds)
      { k: 'crate', x: 7920, plat: 'lowroof3', gives: 'gren', zone: 1 },
      { k: 'crate', x: 8330, plat: 'lowroof4', gives: 'hmg', zone: 1 },
      { k: 'crate', x: 8760, plat: 'vroof1', gives: 'gren', zone: 2 },
      { k: 'crate', x: 9480, plat: 'vroof3', gives: 'hmg', zone: 2 },
      { k: 'crate', x: 9990, gives: 'gren', zone: 2 }
    ],
    // ---- zone 1, on wheels: where Salem starts and where he stops (at the old gate)
    pickup: { x: 140, after: [] },
    park: { x: 6230 },
    //   men: n of them from x, gap apart (kinds cycles; march: a file on the move with its back to you)
    //   truck: block (parked across the road), run (driving ahead of you), charge (coming at you, horn going)
    //   rmine, drum, rbags (sandbags), crate (grenades), drones: n little ones with a mortar bomb each
    //   barrier: a checkpoint's pole across the road (it breaks: the 4x4 through it, or shots into it)
    road: [
      { x: 520, k: 'men', n: 2, gap: 30 },
      { x: 900, k: 'rmine' },
      { x: 1100, k: 'truck', mode: 'run', paint: 'sand' },
      // the first checkpoint (its hut at 1425, the speakers' pole at 1500)
      { x: 1400, k: 'rbags' },
      { x: 1440, k: 'men', n: 3, gap: 26, kinds: ['rifle', 'rifle', 'bomber'] },
      { x: 1530, k: 'barrier' },
      { x: 1600, k: 'drum', paint: 'oxide' },
      { x: 1900, k: 'drones', n: 2 },
      { x: 2200, k: 'truck', mode: 'block' },
      { x: 2480, k: 'men', n: 5, gap: 22, march: true },
      { x: 2760, k: 'rmine' },
      { x: 2860, k: 'rmine' },
      // the second checkpoint (hut 3125, pole 3200)
      { x: 3100, k: 'rbags' },
      { x: 3140, k: 'men', n: 4, gap: 24, kinds: ['rifle', 'bomber', 'rifle', 'door'] },
      { x: 3230, k: 'barrier' },
      { x: 3330, k: 'truck', mode: 'block', paint: 'sand' },
      { x: 3700, k: 'truck', mode: 'charge', nogun: true },
      { x: 3980, k: 'men', n: 5, gap: 26, kinds: ['rifle', 'rifle', 'bomber', 'rifle', 'rifle'] },
      { x: 4300, k: 'drones', n: 2 },
      { x: 4500, k: 'crate', gives: 'gren' },
      // the third checkpoint (hut 4825, pole 4900): the biggest
      { x: 4800, k: 'rbags' },
      { x: 4830, k: 'men', n: 5, gap: 22, kinds: ['rifle', 'bomber', 'rifle', 'door', 'rifle'] },
      { x: 4930, k: 'barrier' },
      { x: 5000, k: 'drum', paint: 'blue' },
      { x: 5018, k: 'drum', paint: 'oxide' },
      { x: 5120, k: 'truck', mode: 'block' },
      { x: 5420, k: 'truck', mode: 'charge', nogun: true, paint: 'sand' },
      { x: 5700, k: 'men', n: 3, gap: 26 },
      { x: 5900, k: 'rmine' }
    ],
    // the checkpoints on the highway (dhamar.js; render_dhamar.js draws the barrier, the queue and the goats): where the
    // stamp hut's window and the speakers' pole are; the barrier on the road; how many notes blow out when he laughs
    checkpoints: [
      { x: 1380, hut: 1425, pole: 1500, barrier: 1530, notes: 2 },
      { x: 3080, hut: 3125, pole: 3200, barrier: 3230, notes: 3 },
      { x: 4780, hut: 4825, pole: 4900, barrier: 4930, notes: 3 }
    ],
    // the convoy going the other way on the far lane, loaded with the drafted (render_dhamar.js; scenery: nothing hits it)
    convoy: { from: 600, to: 5800, every: 700 },
    // the recruiting office (school.js): its three classrooms' doors and how many children each holds; the yard's floor;
    // the teacher, held at the office, waits for them once freed and then goes after them
    school: { gate: 'school', y: 184, teacher: 7640, doors: [{ x: 7420, n: 4 }, { x: 7520, n: 5 }, { x: 7620, n: 4 }] },
    // the office's wall (render_dhamar.js): the Leader's silent screen (a pointing finger, nothing breaks it), his
    // painted face over the stamp window (no text), the window's counter
    office: { screen: [7656, 130], poster: [7750, 127], window: 7760 },
    // the vote at Hammam Ali (rally.js in its 'vote' style; render_dhamar.js draws him at his table with its microphones and
    // the gathering in the steam, as the storyboard: him at the left of his table facing right, the gathering beyond it
    // facing him, the convoy parked behind them): the ground, where he stands (chair) and his table (podium), where each of
    // the gathering stands (x, feet; the third one asks), what is said in turn while he is the nearest voice, Yazeed's word
    // when he comes up, and the Committee's as he denies it and drafts them all
    stage: { gate: 'vote', style: 'vote', x0: 10262, x1: 10520, deck: 184, chair: 10282, podium: 10318,
             seats: [[10356, 184], [10376, 185], [10396, 184], [10418, 186], [10438, 184], [10460, 185], [10482, 184]], asker: 2,
             lines: ['cm_minutes', 'cm_favour', 'cm_voted', 'grunt_wages', 'cm_laugh', 'cm_noted'],
             heard: 'yazeed_committee', deny: 'cm_denied', draft: 'cm_drafted' },
    // the hot pools' steam (render_dhamar.js): where it rises
    steam: [[9010, 9150], [9230, 9390], [9860, 9990], [10120, 10250], [10340, 10500]],
    // the convoy parked in the car park, behind the gathering (render_dhamar.js; scenery): where each lorry stands
    parked: [10566]
  };
  return L;
})();
if (typeof module !== 'undefined') {
  LEVEL_DHAMAR.ground = require('../gen/stage_dhamar.json').ground;      // (in the page main.js gives it GROUNDS.dhamar, the same)
  module.exports = LEVEL_DHAMAR;
}
