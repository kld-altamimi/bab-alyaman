// unit4.js - build 4: the coast road's sand run, the mines you can see coming, and the art agreeing with the level.
'use strict';
const path = require('path');
const Sim = require(path.join(__dirname, '../src/sim.js'));
require(path.join(__dirname, '../src/drive.js'));
require(path.join(__dirname, '../src/boss.js'));
const LEVEL = require(path.join(__dirname, '../src/level.js'));
LEVEL.ground = require(path.join(__dirname, '../gen/ground.json'));
const ATLAS = require(path.join(__dirname, '../gen/atlas.json'));
const { smartBot } = require('./bot.js');
let fails = 0;
const ok = (c, what) => { console.log((c ? 'ok   ' : 'FAIL ') + what); if (!c) fails++; };
const none = { mx: 0, my: 0, fire: false, jump: false, grenade: false, auto: false };

// ------------------------------------------------------------------ the level and the pictures agree on where the sand is
{
  const Wl = LEVEL.world, Wa = ATLAS.world;
  ok(['XR1', 'XS0', 'XS1', 'XR2'].every(k => Wl[k] === Wa[k]) && Wl.XR1 < Wl.XS0 && Wl.XS0 < Wl.XS1 && Wl.XS1 < Wl.XR2 && Wl.XR2 < Wl.XB,
     'level and art put the sand run in the same place (' + Wl.XS0 + ' to ' + Wl.XS1 + ', joins ' + Wl.XR1 + ' and ' + Wl.XR2 + ')');
  const play = ATLAS.layers.play.strips, fore = ATLAS.layers.fore.strips;
  let gap = 0, x = 0;
  for (const st of play) { if (st.x !== x) gap++; x = st.until != null ? st.until : st.x + st.w; }
  ok(gap === 0 && x === Wl.XB + 900, 'the ground strips run end to end with no gap, to the end of the world (' + x + ')');
  const fs = fore.find(st => st.img === 'fore_sand');
  // the near foreground moves at 1.25: its sand should come on screen with the middle of the first join and go with the middle of the second
  const midIn = (Wl.XR1 + Wl.XS0) / 2, midOut = (Wl.XS1 + Wl.XR2) / 2;
  // (with the camera at cam, the middle of a 468-wide screen shows the ground at cam + 234 and the foreground at 1.25 cam + 234)
  const camIn = (fs.x - 234) / 1.25, camOut = (fs.until - 234) / 1.25;
  ok(Math.abs(camIn + 234 - midIn) < 40 && Math.abs(camOut + 234 - midOut) < 40,
     'the foreground turns to beach within 40 px of the ground doing so (' + Math.round(camIn + 234 - midIn) + ', ' + Math.round(camOut + 234 - midOut) + ')');
  const missing = LEVEL.scenery.filter(sc => !ATLAS.frames['sc_' + sc.k]).map(sc => sc.k);
  ok(missing.length === 0, 'every piece of scenery has a picture' + (missing.length ? ' (missing: ' + missing.join(', ') + ')' : ''));
  const onSand = LEVEL.scenery.filter(sc => sc.x > Wl.XS0 && sc.x < Wl.XS1);
  ok(onSand.some(sc => sc.k === 'boat' || sc.k === 'boat2') && !onSand.some(sc => /^sign_|stone/.test(sc.k)), 'on the sand: boats, and no road signs or kilometre stones');
}

// ------------------------------------------------------------------ the mines: each is called out once, in good time
{
  const s = Sim.create(LEVEL, { viewW: 468, seed: 11, zone: 3 });
  const bot = smartBot({});
  const mines = LEVEL.road.filter(it => it.k === 'rmine').length;
  const spots = [], blown = [];
  let leadMin = 1e9;
  for (let k = 0; k < 60 * 90 && s.mode !== 'foot'; k++) {
    Sim.step(s, Object.assign({ viewW: 468 }, bot(s)));
    if (s.p.plates < 2) s.p.plates = 3;
    for (const e of s.events) {
      if (e.t === 'spot' && e.k === 'rmine') {
        spots.push(e.x);
        const front = s.car.x + Sim.D.FRONT;
        leadMin = Math.min(leadMin, (e.x - front) / Math.max(1, s.car.vx));
      }
      if (e.t === 'explode' && e.kind === 'mine') blown.push(e.x);
    }
  }
  const uniq = new Set(spots).size;
  ok(spots.length === mines && uniq === mines, 'each of the ' + mines + ' road mines is called out once (' + spots.length + ' calls)');
  ok(leadMin > 0.9, 'and at least ' + leadMin.toFixed(2) + ' s before the front of the car reaches it at the speed it is going');
}
{
  // a mine that is shot or set off before it is seen says nothing
  const L = Object.assign({}, LEVEL, { road: [{ x: LEVEL.world.XA + 900, k: 'rmine' }] });
  const s = Sim.create(L, { viewW: 468, seed: 3, zone: 3 });
  let calls = 0, wasThere = false;
  for (let k = 0; k < 600; k++) {
    Sim.step(s, Object.assign({ viewW: 468 }, none));
    const m = s.props.find(o => o.k === 'rmine');
    if (m && !m.seen) { m.gone = true; wasThere = true; }      // put on the road ahead, and gone (shot, say) before it is in view
    for (const e of s.events) if (e.t === 'spot') calls++;
  }
  ok(wasThere && calls === 0, 'a mine gone before it comes into view is not called out');
}

console.log(fails ? '\n' + fails + ' FAILED' : '\nALL BUILD 4 CHECKS OK');
process.exit(fails ? 1 : 0);
