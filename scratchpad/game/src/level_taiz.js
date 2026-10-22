// level_taiz.js - The Castle: Taiz, by Apache. THE FULL LEVEL (21 Oct, Khaled 05:23: "let's design the full level ... refer
// to the teaser ... drop dusk ... a nice mix of verticality and horizontality ... no need for a sharp upward cliff unless
// for a short section ... aesthetically pleasing"; "enemies appear out of the blue, they need to enter logically").
// The stage is painted (tools/export_taiz.py: its pieces on one sheet, and where everything is in gen/stage_taiz.json: the
// ground, the stone, the roofs and ledges men stand on, the doors they come out of, the windows that are lit at night).
// It is night all the way, as in the teaser. The way climbs, but mostly along: over the roofs of the lower town, up over
// the old city's gate, down into the souq between the tall houses, up the terraces, along the hillside road and under its
// bridge, through the village, a short climb up the face of the castle rock, and along the castle walls to the keep.
// Seen from further back than the missions on foot (zoom 1.5: the picture shows half as much again each way).
// How the men come: the ones at their posts are there already (on guard on the roofs, at the guns); the rest come out
// of the doors on the roofs (the little stair rooms), out of the houses' street doors, up through the hatches in the gate's
// and the castle's towers, or along the road; the drones are launched from crates on the roofs, or come in from ahead.
var LEVEL_TAIZ = (function () {
  'use strict';
  var ST = typeof STAGE_TAIZ !== 'undefined' ? STAGE_TAIZ : require('../gen/stage_taiz.json');
  var W = ST.world;
  // houses painted as solid that are only scenery here: no stone to fly into, nobody on their roofs (their street doors
  // still let men out into the street in front of them). The tall house on the souq's far side (Khaled, 21 Oct: "in the
  // valley of the two towers, it's still not clear that the one on the right isn't a background ... maybe modify it and
  // have it be a background"): the camera's way up out of the souq runs across it, so it reads as one to fly through.
  var BACKDROP = ['h191'];
  function backdropRock(P) {
    for (var i = 0; i < ST.place.length; i++) {
      var q = ST.place[i], r = ST.pieces[q.p];
      if (BACKDROP.indexOf(q.p) < 0 || !r) continue;
      var inside = P.every(function (pt) { return pt[0] >= q.x - 4 && pt[0] <= q.x + r[2] + 4 && pt[1] >= q.y - 4 && pt[1] <= q.y + r[3] + 4; });
      if (inside) return true;
    }
    return false;
  }
  // the platforms men stand on (not the stalls' awnings; the terraces' ends kept off their sampled steps)
  var plats = Object.keys(ST.plats).filter(function (k) { return !/^stall/.test(k) && BACKDROP.indexOf(k) < 0; }).map(function (k) {
    var p = ST.plats[k];
    if (/^terr/.test(k)) p = [[p[0][0] + 8, p[0][1]], [p[1][0] - 8, p[1][1]]];
    return { id: k, pts: p };
  });

  // the camera's way through the level (fly.js): along and up, with the corners rounded off
  var ROUTE = [
    [1000, 1060],     // the street of the lower town, under the first roofs (the opening)
    [1320, 890],      // up over the roofs
    [2840, 890],      // along them
    [3030, 820],      // up over the old city's gate
    [3290, 820],      // over the tall house on the far side of it
    [3430, 1070],     // down into the souq, between the tall houses
    [3560, 1070],
    [3660, 860],      // up out of it, over the tall house on its far side
    [4320, 745],      // up the terraces
    [4600, 795],      // the hillside road: down to it a little, so the road (and the pickups on it) runs through the
    [5240, 680],      //   lower part of the picture, not along its bottom edge under the thumbs
    [5460, 760],      // the bridge: low enough to see under it
    [5680, 600],      // up again
    [6140, 560],      // the village
    [6240, 270],      // up the face of the castle rock
    [7180, 270],      // along the castle walls
    [7350, 300]       // to the keep: a little lower, so the courtyard (and what comes out of the keep into it) is well up in
  ];                  //   the picture, clear of the thumbs

  // each fight holds the camera where its point on the route reaches the middle of the picture
  var gates = [
    { id: 'a', at: [1560, 890], groups: ['A', 'A2'] },                 // the first roofs
    { id: 'b', at: [2120, 890], groups: ['B', 'B2', 'B3'] },           // the gun on the roof, and a crate of drones
    { id: 'c', at: [3030, 820], groups: ['C', 'C2', 'C3'] },           // the gate
    { id: 'd', at: [3470, 1070], groups: ['D', 'D2', 'D3'] },          // the souq
    { id: 'e', at: [4100, 783], groups: ['E', 'E2', 'E3'] },           // the terraces
    // the hillside road: a chase. From its start the camera goes up the road by itself, after the pickups, to its end
    { id: 'f', at: [5180, 690], groups: ['F', 'F2'], chase: { from: [4140, 776], v: 72 } },
    { id: 'g', at: [5460, 760], groups: ['G', 'G2', 'G3'] },           // the bridge
    { id: 'h', at: [5920, 575], groups: ['H', 'H2', 'H3'] },           // the village
    { id: 'i', at: [6219, 330], groups: ['I', 'I2'] },                 // the climb
    { id: 'j', at: [6600, 270], groups: ['J', 'J2', 'J3'] },           // the walls
    { id: 'k', at: [6920, 270], groups: ['K', 'K2'] },                 // the bastion: the Castle Gun
    { id: 'm', at: [7350, 300], groups: ['M'] }                        // the keep: the launcher
  ];
  // A: the first of a fight wakes when the camera gets to trigAt; the rest follow on, each when the one before is done
  var groups = {}, wake = { A: [1330, 890], B: [1900, 890], C: [2800, 890], D: [3150, 820], E: [3800, 832], F: null,
                            G: [5250, 680], H: [5700, 599], I: [6150, 530], J: [6300, 270], K: [6760, 270], M: [7180, 270] };
  var zoneOf = { A: 0, B: 0, C: 1, D: 1, E: 1, F: 2, G: 2, H: 2, I: 3, J: 3, K: 3, M: 3 };
  groups.Z0 = { zone: 0, noSurrender: true };            // (the five in the street in the opening: fly.js runs them)
  // (the pickups wake as the terraces' fight ends, not at a point on the way: the chase starts right after it)
  var wakeF = { after: 'E3', delay: 30 };
  gates.forEach(function (g) {
    g.groups.forEach(function (k, n) {
      var f = k.charAt(0);
      groups[k] = n === 0 ? { zone: zoneOf[f], trigAt: wake[f] } : { zone: zoneOf[f], after: g.groups[n - 1], delay: 24 };
    });
  });
  groups.F = { zone: zoneOf.F, after: wakeF.after, delay: wakeF.delay };

  var L = {
    id: 'taiz',
    name: 'The Castle',
    art: 'taiz',
    banner: 'THE CASTLE',
    music: 'taiz', bossMusic: 'taizboss',             // (the night flight's theme; the Castle Gun and the launcher share theirs)
    lines: { start: [[10, 'ann_taiz', 4]], clear: [[26, 'ann_complete', 8]] },          // (Salem's lines come with the Apache: main.js)
    freedNote: 'somebody is still waiting on a roof',
    zoom: 1.5,                  // (the picture is half as wide and half as tall again as on foot: the Apache needs room)
    width: W.W, height: W.H,
    par: 420,
    exitX: 1e9,                 // (the end is the end of the route: fly.js)
    endRight: W.W,
    ground: ST.ground,
    plats: plats,
    zones: [
      // (indoor: no gulls over the rotor)
      { name: 'The lower town', spawn: 900, at: [1000, 1060], pos: [900, 1000], indoor: true },
      { name: 'The old city', spawn: 2700, at: [2800, 890], pos: [2690, 860], indoor: true },
      { name: 'The hillside road', spawn: 4250, at: [4330, 739], pos: [4240, 700], indoor: true },
      { name: 'The castle', spawn: 6050, at: [6140, 560], pos: [6050, 470], indoor: true }
    ],
    gates: gates,
    groups: groups,
    spawns: [],                 // (the generic ones: none. The Apache's are below)
    props: [],
    fly: {
      arrive: true,             // (a continue from the first checkpoint: the Apache comes in from the left, over the street)
      // the opening, on foot in the street: Yazeed, the five across the street from him, the doors they run for, where the
      // Apache sets down (fly.js)
      intro: { yazeed: ST.intro.yazeed, men: ST.intro.men, doors: ST.intro.doors, land: 330, street: W.STREET },
      // the end: down into the castle's courtyard, at dawn (where it may come down, and where it sets down)
      landing: { x0: 7282, x1: 7418, y: W.TOP, pad: 7350 },
      route: ROUTE,
      // once the Apache is the player's, the camera shows the way up over the first roofs (fly.js startGuide)
      guide: { to: [1320, 890], v: 80 },
      rock: ST.rock.filter(function (P) { return !backdropRock(P); }),
      scenery: BACKDROP,
      doors: ST.doors,
      stage: ST,
      // night all the way (dawn comes with the end: later)
      light: [{ at: ROUTE[0], d: 1 }, { at: ROUTE[ROUTE.length - 1], d: 1 }],
      // k: rifle | aa | sam | rpg | mortar | sniper | light (a searchlight) | truck (a pickup with a gun) | drone | crate.
      // plat: the roof, ledge or wall he stands on (none: the ground, the street or the road). from: how he gets to his post:
      // 'door:<id>' (out of that door, and along), 'hatch' (up through a hatch at his post), 'run:<x>' (along from x); none:
      // he is there already. A crate launches n drones, one after another. A sniper is in a window: win, its sill.
      spawns: [
        // ---- the first roofs of the lower town: three on guard, two more up the stair
        { g: 'A', k: 'rifle', x: 1415, plat: 'h107', look: 'worried' },
        { g: 'A', k: 'rifle', x: 1500, plat: 'h109', look: 'youth' },
        { g: 'A', k: 'rifle', x: 1630, plat: 'h113', look: 'angry' },
        { g: 'A2', k: 'rifle', x: 1512, plat: 'h109', look: 'qat', from: 'door:h109_roof', delay: 0 },
        { g: 'A2', k: 'rifle', x: 1490, plat: 'h109', look: 'angry', from: 'door:h109_roof', delay: 46 },
        // ---- a gun on the roof, and a crate of drones
        { g: 'B', k: 'aa', x: 1984, plat: 'h137' },
        { g: 'B', k: 'rifle', x: 2066, plat: 'h139', look: 'youth' },
        { g: 'B', k: 'rifle', x: 2178, plat: 'h149', look: 'angry' },
        { g: 'B', k: 'light', x: 2200, plat: 'h149', look: 'worried', beam: -0.6, dir: -1 },
        { g: 'B2', k: 'crate', x: 2118, plat: 'h139', n: 3, delay: 0 },
        { g: 'B3', k: 'rifle', x: 2188, plat: 'h149', look: 'qat', from: 'door:h149_roof', delay: 0 },
        { g: 'B3', k: 'rifle', x: 2090, plat: 'h139', look: 'worried', from: 'run:2045', delay: 30 },
        // ---- the old city's gate: men on its towers and over its arch, a missile man up through a hatch
        { g: 'C', k: 'rifle', x: 2938, plat: 'gate_10', look: 'angry' },
        { g: 'C', k: 'rifle', x: 3004, plat: 'gate_wall', look: 'youth' },
        { g: 'C', k: 'rifle', x: 3112, plat: 'gate_180', look: 'worried' },
        { g: 'C2', k: 'sam', x: 3128, plat: 'gate_180', look: 'qat', from: 'hatch', delay: 0 },
        { g: 'C2', k: 'rpg', x: 2960, plat: 'gate_10', look: 'qat', from: 'hatch', delay: 40 },
        { g: 'C3', k: 'drone', n: 2, delay: 0 },
        { g: 'C3', k: 'rifle', x: 3050, plat: 'gate_wall', look: 'angry', from: 'run:3076', delay: 20 },
        // ---- the souq: out into the street from the houses either side
        { g: 'D', k: 'rifle', x: 3300, look: 'worried' },
        { g: 'D', k: 'rifle', x: 3400, look: 'angry' },
        { g: 'D', k: 'rifle', x: 3530, look: 'youth' },
        { g: 'D2', k: 'rifle', x: 3292, look: 'qat', from: 'door:h181_street', delay: 0 },
        { g: 'D2', k: 'rifle', x: 3560, look: 'angry', from: 'door:h191_street', delay: 30 },
        { g: 'D2', k: 'sniper', win: [3426, 1040], x: 3426, look: 'qat' },
        { g: 'D3', k: 'sniper', win: [3554, 1035], x: 3554, look: 'angry' },
        { g: 'D3', k: 'sam', x: 3460, look: 'worried', from: 'door:h191_street', delay: 30 },
        { g: 'D3', k: 'drone', n: 2, low: true, delay: 60 },
        // ---- the terraces
        { g: 'E', k: 'sam', x: 3930, plat: 'h211', look: 'youth' },
        { g: 'E', k: 'rifle', x: 4094, plat: 'h223', look: 'angry' },
        { g: 'E', k: 'mortar', x: 4208, plat: 'h227', look: 'worried' },
        { g: 'E2', k: 'rifle', x: 4078, plat: 'h223', look: 'qat', from: 'door:h223_roof', delay: 0 },
        { g: 'E2', k: 'rifle', x: 4172, plat: 'terr3', look: 'youth', from: 'door:h227_street', delay: 30 },
        { g: 'E3', k: 'crate', x: 4240, plat: 'h227', n: 3, delay: 0 },
        // ---- the hillside road: the chase. Three pickups with guns in the back, away up the road, firing back
        { g: 'F', k: 'truck', x: 4420, paint: 'olive', lead: 0.36 },     // (just past the right of the picture while the
        { g: 'F', k: 'truck', x: 4500, paint: 'sand', lead: 0.52 },      //  terraces are fought over: they are off up the
        { g: 'F', k: 'truck', x: 4580, paint: 'olive', lead: 0.68 },     //  road the moment that is done, the Apache after them)
        { g: 'F2', k: 'drone', n: 2, delay: 0 },
        // ---- the bridge: men on the deck, more running down the road from the village
        { g: 'G', k: 'rifle', x: 5330, plat: 'bridge', look: 'angry' },
        { g: 'G', k: 'rifle', x: 5430, plat: 'bridge', look: 'youth' },
        { g: 'G', k: 'sam', x: 5590, plat: 'bridge', look: 'qat' },
        { g: 'G2', k: 'rifle', x: 5520, plat: 'bridge', look: 'worried', from: 'run:5700', delay: 0 },
        { g: 'G2', k: 'rpg', x: 5560, plat: 'bridge', look: 'angry', from: 'run:5740', delay: 20 },
        { g: 'G3', k: 'drone', n: 2, low: true, delay: 0 },
        // ---- the village under the castle rock
        { g: 'H', k: 'aa', x: 6018, plat: 'h241' },
        { g: 'H', k: 'rifle', x: 5865, plat: 'h239', look: 'youth' },
        { g: 'H', k: 'rifle', x: 5756, plat: 'h233', look: 'angry' },
        { g: 'H2', k: 'rifle', x: 5998, plat: 'h241', look: 'qat', from: 'door:h241_roof', delay: 0 },
        { g: 'H2', k: 'rifle', x: 5745, plat: 'h233', look: 'worried', from: 'door:h233_roof', delay: 26 },
        { g: 'H2', k: 'rifle', x: 5940, look: 'angry', from: 'door:h239_street', delay: 50 },
        { g: 'H3', k: 'rpg', x: 5880, plat: 'h239', look: 'qat', from: 'hatch', delay: 0 },
        { g: 'H3', k: 'crate', x: 5770, plat: 'h233', n: 2, delay: 10 },
        // ---- up the face of the rock: a missile man on the first tower, drones off the walls
        { g: 'I', k: 'sam', x: 6334, plat: 'c_6320', look: 'angry', from: 'hatch' },
        { g: 'I', k: 'light', x: 6364, plat: 'c_6320', look: 'youth', beam: -0.9, dir: -1 },
        { g: 'I2', k: 'drone', n: 3, delay: 0 },
        // ---- the walls
        { g: 'J', k: 'aa', x: 6580, plat: 'c_6550' },
        { g: 'J', k: 'rifle', x: 6436, plat: 'c_6380', look: 'angry' },
        { g: 'J', k: 'rifle', x: 6505, plat: 'c_6380', look: 'worried' },
        { g: 'J', k: 'rifle', x: 6690, plat: 'c_6610', look: 'youth' },
        { g: 'J2', k: 'mortar', x: 6462, plat: 'c_6380', look: 'qat', from: 'hatch', delay: 0 },
        { g: 'J', k: 'light', x: 6740, plat: 'c_6610', look: 'angry', beam: -0.3, dir: 1 },
        { g: 'J2', k: 'sam', x: 6650, plat: 'c_6610', look: 'angry', from: 'hatch', delay: 30 },
        { g: 'J2', k: 'rifle', x: 6728, plat: 'c_6610', look: 'worried', from: 'run:6830', delay: 50 },
        { g: 'J3', k: 'crate', x: 6620, plat: 'c_6610', n: 3, delay: 0 },
        // ---- the bastion: THE CASTLE GUN, under its tarp until the Apache comes, its crew on the walls either side
        { g: 'K', k: 'cgun', x: 6920, plat: 'c_6840' },
        { g: 'K', k: 'rifle', x: 6780, plat: 'c_6610', look: 'angry' },
        { g: 'K', k: 'rifle', x: 7040, plat: 'c_7000', look: 'youth' },
        { g: 'K2', k: 'sam', x: 6978, plat: 'c_6840', look: 'qat', from: 'hatch', delay: 0 },
        { g: 'K2', k: 'rpg', x: 7062, plat: 'c_7000', look: 'worried', from: 'run:7190', delay: 30 },
        // ---- the keep: THE LAUNCHER, kept inside it (out through its gate into the courtyard when the Apache comes), and
        //      men on the walls about the courtyard, more coming up while it raises its missile
        { g: 'M', k: 'launcher', x: 7542, stop: 7336 },
        { g: 'M', k: 'rifle', x: 7212, plat: 'c_7200', look: 'angry' },
        { g: 'M', k: 'rifle', x: 7240, plat: 'c_7200', look: 'youth', from: 'hatch', delay: 240 },
        { g: 'M', k: 'rpg', x: 7172, plat: 'c_7000', look: 'worried', from: 'run:7196', delay: 600 }
      ]
    }
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL_TAIZ;
