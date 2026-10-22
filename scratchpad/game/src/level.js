// level.js - the Strait, as build 3 plays it: three zones of beach on foot, the coast road in the back of Salem's pickup,
// and the battery, where the Commander has something to show you.
// Geometry was measured off the painted stage: the ground is the walk line, platforms are the tops of things.
var LEVEL = (function () {
  'use strict';
  var XA = 1500, TILE = 936, NT = 13, XB = XA + NT * TILE;      // where the road's strip starts, its length, how often it repeats, where the battery starts
  function R(r) { return XA + r; }                              // a place along the road
  var L = {
    id: 'm1',                  // the mission it is on the map (campaign.js)
    name: 'The Strait',
    art: 'strait',             // its pictures: ATLAS.stages.strait
    banner: 'THE STRAIT',      // under MISSION START!
    music: 'strait', bossMusic: 'battery',
    sea: true,                 // the sound of the sea under it all
    // who speaks when: [ticks after the start (or the clear), line, priority]
    lines: { start: [[10, 'ann_start', 4], [222, 'yazeed_sand', 1]], clear: [[26, 'ann_complete', 8], [215, 'yazeed_tea', 8]] },
    freedNote: 'the elder is still on the roof',
    bossFact: 'Boat downed in',
    width: XB + 900,
    height: 216,
    par: 240,                  // seconds, for the Ace medal: beach 105 (as build 2), road about 60, the boat about 75
    start: 118,                // where the skiff lets you off
    exitX: XB + 800,           // walk this far, with the battery dealt with, and the mission ends
    restX: XB + 826,
    endRight: XB + 900,        // the right edge of the last screen
    boatLine: [676, 880],      // a blast between these by the wreck of the dhow: Yazeed has a word to say about it
    ground: /*GROUND*/{ step: 4, y: [180] }/*END*/,
    world: { XA: XA, TILE: TILE, NT: NT, XB: XB, XR1: R(3744), XS0: R(4680), XS1: R(7488), XR2: R(8424) },   // XR1..XS0 the tarmac giving out, XS0..XS1 sand, XS1..XR2 tarmac again
    // one-way platforms: land on them from above, drop through with down + jump
    plats: [
      { id: 'deck', pts: [[728, 159], [764, 161], [790, 160], [812, 155], [830, 151]] },
      { id: 'roof', pts: [[684, 122], [727, 122]] },
      { id: 'oxide', pts: [[952, 131], [1074, 141]] },
      { id: 'ochre', pts: [[1008, 115], [1128, 108]] },
      { id: 'blue', pts: [[1086, 131], [1206, 131]] },
      { id: 'green', pts: [[1112, 80], [1176, 80]] },
      { id: 'white', pts: [[1242, 147], [1354, 127]] }
    ],
    zones: [
      { x: 0, name: 'Landfall', spawn: 118 },
      { x: 610, name: 'The fishing camp', spawn: 622 },
      { x: 1004, name: 'Container beach', spawn: 962 },
      { x: 1424, name: 'The coast road', spawn: 1452, drive: true },
      { x: XB + 120, name: 'The battery', spawn: XB + 92, battery: true }
    ],
    // a gate is a line the screen stops at until its groups are dealt with
    gates: [
      { id: 'g0', x: 380, groups: ['A', 'A2', 'B'] },
      { id: 'g1', x: 812, groups: ['W', 'W2'] },
      { id: 'g2', x: 1180, groups: ['C', 'C2', 'C3'], quiet: true },     // (Salem pulls up as it opens: he has the word)
      { id: 'gB', x: XB + 470, groups: ['BOSS'] }
    ],
    // a group wakes when the player passes trig, or when the group named in `after` is dealt with
    groups: {
      A: { zone: 0, trig: 250 },                  // just past the first crate: a breath to find the thumbs before anyone turns up
      A2: { zone: 0, after: 'A', delay: 30 },
      B: { zone: 0, after: 'A2', delay: 40 },
      W: { zone: 1, trig: 610, lastManSurrenders: true },
      W2: { zone: 1, after: 'W', delay: 40 },
      C: { zone: 2, trig: 1004 },
      C2: { zone: 2, after: 'C', delay: 40 },
      C3: { zone: 2, after: 'C2', delay: 50, lastManSurrenders: true },
      ROAD: { zone: 3, hold: true, noSurrender: true },          // whoever is standing on the tarmac
      BOSS: { zone: 4, hold: true, trig: XB + 318, noSurrender: true }
    },
    // k: rifle | bomber | door.  enter: 1 walks in from the right edge, -1 from the left.  dx: how far back in the file.
    // plat: stands his post up there.  behind: keeps in the lee of the man tagged so.  covered: fires from behind cover.
    spawns: [
      { g: 'A', k: 'rifle', enter: 1, delay: 0, look: 'worried' },
      { g: 'A', k: 'rifle', enter: 1, delay: 50, look: 'youth' },
      { g: 'A', k: 'rifle', enter: -1, delay: 150, look: 'angry' },
      { g: 'A2', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 0, dx: 34, behind: 'd', look: 'qat' },
      { g: 'A2', k: 'rifle', enter: 1, delay: 0, dx: 62, behind: 'd', look: 'worried' },
      { g: 'B', k: 'bomber', enter: 1, delay: 0 },
      { g: 'B', k: 'rifle', enter: 1, delay: 40, look: 'angry' },
      { g: 'B', k: 'rifle', enter: 1, delay: 120, look: 'youth' },

      { g: 'W', k: 'rifle', x: 818, plat: 'deck', post: 1, look: 'qat' },
      { g: 'W', k: 'bomber', x: 754, plat: 'deck', post: 1 },
      { g: 'W', k: 'rifle', x: 914, post: 1, covered: 1, look: 'worried' },
      { g: 'W', k: 'door', enter: 1, delay: 30, tag: 'd' },
      { g: 'W', k: 'rifle', enter: 1, delay: 30, dx: 36, behind: 'd', look: 'youth' },
      { g: 'W2', k: 'rifle', enter: -1, delay: 0, look: 'angry' },
      { g: 'W2', k: 'rifle', enter: 1, delay: 60, look: 'youth' },
      { g: 'W2', k: 'bomber', enter: 1, delay: 150 },
      { g: 'W2', k: 'rifle', enter: 1, delay: 260, look: 'qat' },

      { g: 'C', k: 'rifle', x: 1066, plat: 'oxide', post: 1, look: 'angry' },
      { g: 'C', k: 'rifle', x: 1162, plat: 'blue', post: 1, look: 'qat' },
      { g: 'C', k: 'bomber', x: 1278, plat: 'white', post: 1 },
      { g: 'C', k: 'door', enter: 1, delay: 20, tag: 'd' },
      { g: 'C', k: 'rifle', enter: 1, delay: 20, dx: 34, behind: 'd', look: 'youth' },
      { g: 'C', k: 'rifle', enter: 1, delay: 20, dx: 60, behind: 'd', look: 'worried' },
      { g: 'C2', k: 'rifle', enter: -1, delay: 0, look: 'worried' },
      { g: 'C2', k: 'rifle', enter: 1, delay: 40, look: 'angry' },
      { g: 'C2', k: 'rifle', enter: 1, delay: 70, look: 'qat' },
      { g: 'C2', k: 'bomber', enter: 1, delay: 110 },
      { g: 'C2', k: 'rifle', enter: 1, delay: 170, look: 'youth' },
      { g: 'C3', k: 'door', enter: 1, delay: 0, tag: 'd' },
      { g: 'C3', k: 'bomber', enter: 1, delay: 0, dx: 40, behind: 'd' },
      { g: 'C3', k: 'rifle', enter: -1, delay: 60, look: 'angry' },
      { g: 'C3', k: 'rifle', enter: 1, delay: 120, look: 'worried' }
    ],
    // things that stand in the level
    props: [
      { k: 'crate', x: 236, gives: 'hmg', zone: 0 },
      { k: 'mine', x: 447, zone: 0 },
      { k: 'detainee', x: 702, plat: 'roof', zone: 1 },
      { k: 'cover', x: 916, x0: 886, x1: 946, top: 150, zone: 1 },
      { k: 'drum', x: 969, paint: 'oxide', zone: 2 },
      { k: 'crate', x: 1100, plat: 'blue', gives: 'hmg', zone: 2 },
      { k: 'drum', x: 1347, paint: 'blue', zone: 2 },
      { k: 'crate', x: XB + 268, gives: 'hmg', zone: 4 }
    ],
    // ---- the coast road
    pickup: { x: 1452, after: ['g2'] },           // where Salem pulls up, once the beach is clear
    park: { x: XB + 150 },                        // and where he stops, at the battery's barrier
    // what is on the tarmac, in the order the car meets it.
    //   men: n of them from x, gap apart (kinds cycles; march: a file on the move with its back to you)
    //   truck: block (parked across the road), run (driving ahead of you), charge (coming at you, horn going)
    //   rmine, drum, rbags (sandbags, for show), crate (grenades), drones: n little ones with a mortar bomb each
    road: [
      { x: R(520), k: 'men', n: 3, gap: 28 },
      { x: R(1060), k: 'rmine' },
      { x: R(1500), k: 'men', n: 5, gap: 24, kinds: ['rifle', 'rifle', 'bomber', 'rifle', 'rifle'] },
      { x: R(2060), k: 'truck', mode: 'block' },
      { x: R(2600), k: 'rmine' },
      { x: R(2790), k: 'rmine' },
      { x: R(3020), k: 'crate', gives: 'gren' },
      { x: R(3300), k: 'truck', mode: 'run', paint: 'sand' },
      { x: R(3360), k: 'men', n: 2, gap: 30 },
      { x: R(3950), k: 'drones', n: 2 },
      { x: R(4470), k: 'rbags' },
      { x: R(4500), k: 'drum', paint: 'oxide' },
      { x: R(4518), k: 'drum', paint: 'blue' },
      { x: R(4560), k: 'men', n: 3, gap: 22, kinds: ['rifle', 'door', 'rifle'] },
      { x: R(4690), k: 'truck', mode: 'block' },
      { x: R(5300), k: 'truck', mode: 'charge', nogun: true, paint: 'sand' },
      { x: R(5720), k: 'men', n: 3, gap: 26 },
      { x: R(5810), k: 'rmine' },
      { x: R(5840), k: 'men', n: 3, gap: 26, kinds: ['rifle', 'bomber', 'rifle'] },
      { x: R(5960), k: 'rmine' },
      { x: R(6500), k: 'drones', n: 2 },
      { x: R(6760), k: 'truck', mode: 'run' },
      { x: R(7300), k: 'rmine' },
      { x: R(7470), k: 'rmine' },
      { x: R(7640), k: 'rmine' },
      { x: R(7960), k: 'men', n: 5, gap: 30, kinds: ['bomber', 'rifle', 'rifle', 'bomber', 'rifle'] },
      { x: R(8350), k: 'crate', gives: 'gren' },
      { x: R(8560), k: 'rbags' },
      { x: R(8590), k: 'drum', paint: 'blue' },
      { x: R(8608), k: 'drum', paint: 'oxide' },
      { x: R(8626), k: 'drum', paint: 'blue' },
      { x: R(8730), k: 'truck', mode: 'block', paint: 'sand' },
      { x: R(9260), k: 'truck', mode: 'charge', nogun: true },
      { x: R(9560), k: 'truck', mode: 'charge', nogun: true, paint: 'sand' },
      { x: R(9960), k: 'men', n: 9, gap: 20, march: true },
      { x: R(10620), k: 'drones', n: 3 },
      { x: R(11020), k: 'rmine' },
      { x: R(11130), k: 'truck', mode: 'block' },
      { x: R(11200), k: 'men', n: 3, gap: 24, kinds: ['rifle', 'rifle', 'door'] },
      { x: R(11330), k: 'rmine' },
      { x: R(11700), k: 'truck', mode: 'charge', nogun: true }
    ],
    // what stands beside the road, to look at
    scenery: [
      { x: R(140), k: 'sign_end' }, { x: R(330), k: 'palm_a' }, { x: R(760), k: 'rock_a' }, { x: R(930), k: 'sign_camel' }, { x: R(1240), k: 'palm_b' },
      { x: R(1700), k: 'hut' }, { x: R(1790), k: 'camel' }, { x: R(2300), k: 'rock_b' }, { x: R(2480), k: 'palm_a' }, { x: R(3120), k: 'stone' },
      { x: R(3600), k: 'palm_b' }, { x: R(3680), k: 'palm_a' }, { x: R(4200), k: 'sign_stop' }, { x: R(4900), k: 'rock_a' }, { x: R(5100), k: 'camel' },
      // the sand run (from R(3744), the tarmac giving out, to R(8424), where it starts again): boats pulled up at the water's edge, nets drying
      { x: R(4760), k: 'boat2', y: 165 }, { x: R(5500), k: 'palm_a' }, { x: R(5760), k: 'net', y: 165 }, { x: R(6080), k: 'boat', y: 166 }, { x: R(6300), k: 'hut' },
      { x: R(6560), k: 'boat2', y: 164 }, { x: R(6900), k: 'palm_b' }, { x: R(7120), k: 'net', y: 166 }, { x: R(7330), k: 'boat', y: 165 },
      { x: R(7800), k: 'rock_b' }, { x: R(8200), k: 'palm_a' }, { x: R(8440), k: 'sign_stop' }, { x: R(9000), k: 'palm_b' }, { x: R(9100), k: 'stone' },
      { x: R(9700), k: 'camel' }, { x: R(9800), k: 'rock_a' }, { x: R(10300), k: 'palm_a' }, { x: R(10400), k: 'palm_b' }, { x: R(10900), k: 'hut' },
      { x: R(11500), k: 'sign_battery' }, { x: R(11900), k: 'rock_b' }
    ],
    // ---- the battery
    boss: {
      left: XB + 236, right: XB + 704,            // the widest the fight can be
      rise: [XB + 556, 186],                      // where it comes up from: out of the sea, behind the beach
      launcher: [XB + 522, 172],                  // the thing it lands on at the end
      tower: [XB + 640, 121], towerW: 46          // where the Commander stands to watch
    }
  };
  return L;
})();
if (typeof module !== 'undefined') module.exports = LEVEL;
