// test_page.js - open the prototype in a real browser at phone and desktop sizes, play it with thumbs and with a bot, and report.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const base = 'http://127.0.0.1:8766/index.html';
const shots = '/home/claude/bab_out/m1_src/shots/';
fs.mkdirSync(shots, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/';
const only = process.argv.slice(2);
const want = name => !only.length || only.includes(name);

// the careful bot from the headless tests, lifted into the page so it plays the real thing
const botSrc = fs.readFileSync(GAME + 'tools/bot.js', 'utf8');
const m = botSrc.match(/function smartBot\(opts\) \{[\s\S]*?\n\}\n/);
if (!m) throw new Error('could not find the bot');
const BOT = 'window.__mkBot = function (opts) { var T = Sim.T; ' + m[0] + ' return smartBot(opts); };';

const problems = [];
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) problems.push(what); };

async function open(browser, name, vp, opts) {
  opts = opts || {};
  const ctx = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: vp[2] || 1, hasTouch: !!opts.touch, isMobile: !!opts.touch, colorScheme: opts.scheme || 'dark',
                                         reducedMotion: opts.calm ? 'reduce' : 'no-preference' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message + '\n' + (e.stack || '').split('\n').slice(0, 4).join('\n')));
  page.on('requestfailed', r => errors.push('request failed: ' + r.url()));
  await page.goto(base, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 15000 });
  const client = await ctx.newCDPSession(page);
  const pts = {};
  const send = async type => client.send('Input.dispatchTouchEvent', { type, touchPoints: Object.keys(pts).map(id => ({ x: pts[id][0], y: pts[id][1], id: +id, radiusX: 12, radiusY: 12, force: 1 })) });
  const touch = {
    down: async (id, x, y) => { pts[id] = [x, y]; await send('touchStart'); },
    move: async (id, x, y) => { pts[id] = [x, y]; await send('touchMove'); },
    // this browser lifts exactly the fingers named in a touchEnd
    up: async id => { const q = pts[id]; delete pts[id]; await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [{ x: q[0], y: q[1], id: +id, radiusX: 12, radiusY: 12, force: 1 }] }); },
  };
  const real = () => errors.filter(e => !/fonts\.(googleapis|gstatic)|ERR_|Failed to load resource|posthog/.test(e));
  return { ctx, page, errors, real, touch, name };
}
const shot = (t, file) => t.page.screenshot({ path: shots + file });
const st = t => t.page.evaluate(() => {
  const s = window.__m1.sim(), g = window.__m1.geo();
  return { state: window.__m1.state(), W: window.__m1.width(), x: s ? s.p.x : null, y: s ? s.p.y : null, cam: s ? s.cam : null, status: s ? s.status : null, zone: s ? s.zone : null,
           plates: s ? s.p.plates : null, lives: s ? s.p.lives : null, time: s ? s.time : null, score: s ? s.score : null, tick: s ? s.tick : null,
           land: g.land, rot: g.rot, n: g.n, fast: g.fast, scale: g.scale, snd: Sound.info(), lock: Input.isLocked() };
});
const boxes = t => t.page.evaluate(() => {
  const r = e => { const b = document.getElementById(e).getBoundingClientRect(); return { x: b.left, y: b.top, w: b.width, h: b.height, cx: b.left + b.width / 2, cy: b.top + b.height / 2 }; };
  const hid = id => { const e = document.getElementById(id); return e.hidden || getComputedStyle(e).display === 'none' || getComputedStyle(e).visibility === 'hidden'; };
  return { app: r('app'), hi: r('hi'), fire: r('bFire'), jump: r('bJump'), bomb: r('bBomb'), stick: r('stick'), ui: r('ui'),
           fireHidden: hid('bFire'), sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight, iw: innerWidth, ih: innerHeight,
           panel: (() => { const p = document.querySelector('.panel:not([hidden])'); if (!p) return null; const b = p.getBoundingClientRect(); return { x: b.left, y: b.top, w: b.width, h: b.height, sh: p.scrollHeight, ch: p.clientHeight, id: p.id }; })() };
});
async function startByTap(t) {
  await t.page.evaluate(() => window.__m1.wake()); await t.page.tap('#bStart');
  await t.page.waitForFunction(() => window.__m1.state() === 'map', null, { timeout: 12000 });
  await t.page.tap('#bPlay');
  await t.page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
}
// where mission i's badge is on the screen, from the map's own numbers
const nodeOnScreen = (t, i) => t.page.evaluate(i => {
  const g = window.__m1.geo(), m = window.__m1.menu(), n = ATLAS.menu.map.nodes[i], W = window.__m1.width(), c = document.getElementById('hi').getBoundingClientRect();
  return [c.left + (n[0] - m.cam) * c.width / W, c.top + (n[1] - m.camY) * c.height / 216];
}, i);
async function tapAt(t, xy) { await t.touch.down(9, xy[0], xy[1]); await sleep(50); await t.touch.up(9); }
async function withBot(t, auto) {
  await t.page.evaluate(BOT);
  await t.page.evaluate(a => { const bot = window.__mkBot({ auto: a }); window.__realSample = window.__realSample || Input.sample; Input.sample = function () { const s = window.__m1.sim(); const i = bot(s); return { mx: i.mx, my: i.my, fire: i.fire, jump: i.jump, grenade: i.grenade, auto: i.auto }; }; }, !!auto);
}

(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });

  // ------------------------------------------------------------------ a phone on its side
  if (want('land')) {
    const t = await open(browser, 'land', [844, 390, 3], { touch: true });
    let b = await boxes(t), s = await st(t);
    note(b.sw <= b.iw && b.sh <= b.ih, `phone on its side: nothing scrolls (page ${b.sw} x ${b.sh} in a ${b.iw} x ${b.ih} window)`);
    note(s.W >= 384 && s.W <= 468 && Math.abs(b.hi.h - 390) < 1 && b.hi.x >= 16 && b.hi.x + b.hi.w <= b.iw - 16 + 0.5, `picture ${s.W} wide, drawn ${b.hi.w.toFixed(1)} x ${b.hi.h.toFixed(1)} at x=${b.hi.x.toFixed(1)}; enlarged x${s.n}${s.fast ? ' plain' : ' sharp'}`);
    note(b.panel && b.panel.id === 'pHome' && b.panel.sh <= b.panel.ch + 1 && b.panel.y >= b.hi.y + b.hi.h * 0.7 && b.panel.y + b.panel.h <= b.ih, `home: the buttons sit along the foot of the picture: ${JSON.stringify(b.panel)}`);
    note(b.fireHidden, 'thumb buttons are hidden while a menu is up');
    note(s.snd.state === 'not started', 'no audio context before a tap (' + s.snd.state + ', files ' + s.snd.decoded + ' decoded ' + s.snd.how + ')');
    note(await t.page.evaluate(() => document.querySelector('#pHome .acts').hidden && !window.__m1.woke()), 'fresh: Start and Options are not shown yet, the picture says TAP TO START');
    await shot(t, 'land_home.png');
    await t.page.touchscreen.tap(422, 150);
    await t.page.waitForFunction(() => window.__m1.woke());
    await sleep(600);
    note(await t.page.evaluate(() => window.__m1.state() === 'home' && !document.querySelector('#pHome .acts').hidden && Sound.playing() === 'title'), 'a tap on the picture wakes the sound: the home theme plays, still on the home screen, Start and Options shown');
    await shot(t, 'land_home_awake.png');
    await t.page.tap('#bOpts');
    await t.page.waitForFunction(() => window.__m1.state() === 'opts');
    b = await boxes(t);
    note(b.panel && b.panel.id === 'pOpts' && b.panel.sh <= b.panel.ch + 1 && b.panel.y + b.panel.h <= b.ih, `options panel fits: ${JSON.stringify(b.panel)}`);
    await t.page.tap('#segAuto');
    note(await t.page.evaluate(() => Input.scheme() === 'auto' && document.querySelector('#pOpts .scheme-note').textContent.indexOf('by itself') > 0), 'choosing auto-fire changes the scheme and its note');
    await t.page.tap('#segHold');
    await t.page.tap('#bErase');
    note(await t.page.evaluate(() => document.getElementById('bErase').textContent === 'Tap again to erase'), 'Erase progress asks for a second tap first');
    await t.page.tap('#bBack');
    await t.page.waitForFunction(() => window.__m1.state() === 'home');
    // a tap anywhere on the picture opens the map
    await tapAt(t, [b.hi.cx || 422, 120]);
    await t.page.waitForFunction(() => window.__m1.state() === 'map', null, { timeout: 5000 });
    await sleep(700);
    b = await boxes(t);
    let mv = await t.page.evaluate(() => window.__m1.menu());
    note(b.panel && b.panel.id === 'pMap' && b.panel.x + b.panel.w <= b.hi.x + b.hi.w + 0.5 && b.panel.x > b.hi.x + b.hi.w * 0.5 && b.panel.sh <= b.panel.ch + 1, `map: the mission card stands at the right of the picture: ${JSON.stringify(b.panel)}`);
    const c1 = await t.page.evaluate(() => [document.getElementById('mName').textContent, document.getElementById('mTag').textContent, document.getElementById('mAhead').textContent]);
    note(mv.sel === 'm1' && mv.vis > 220 && c1[0] === 'The Strait' && c1[1] === 'Bab al-Mandab', `map: The Strait (at Bab al-Mandab) is chosen, ${Math.round(mv.vis)} of ${s.W} dots of map in view`);
    note(/Next stop: the Coffee Port\./.test(c1[2]), `the card says where the road goes: "${c1[2]}"`);
    await shot(t, 'land_map.png');
    await tapAt(t, await nodeOnScreen(t, 'mocha'));
    await sleep(500);
    mv = await t.page.evaluate(() => window.__m1.menu());
    const c2 = await t.page.evaluate(() => [document.getElementById('mName').textContent, document.getElementById('bPlay').disabled, document.getElementById('mEye').textContent, document.getElementById('mBrief').textContent, document.getElementById('mBoss').textContent, document.getElementById('mTag').textContent, document.getElementById('mAhead').textContent, document.getElementById('bPlay').textContent]);
    note(mv.sel === 'mocha' && c2[0] === 'The Coffee Port' && c2[5] === 'Mocha' && !c2[1] && c2[7] === 'Skip ahead' && /Locked/.test(c2[2]) && c2[3].length > 40 && c2[4].length > 20, `a tap on Mocha shows the Coffee Port's briefing, locked, offering to skip ahead (${JSON.stringify(c2.slice(0, 3).concat(c2[7]))})`);
    note(/fork in the road/.test(c2[6]) && /coast road to the Souq,/.test(c2[6]) && /mountain road to the Castle\./.test(c2[6]) && /Clear the Strait/.test(c2[6]), `the Coffee Port's card says where the road forks: "${c2[6]}"`);
    await tapAt(t, await nodeOnScreen(t, 'mocha'));
    await sleep(300);
    note((await st(t)).state === 'map', 'a second tap on a locked mission does nothing');
    // every briefing on one list
    await t.page.tap('#bBriefs');
    await t.page.waitForFunction(() => window.__m1.state() === 'brief');
    b = await boxes(t);
    const bl = await t.page.evaluate(() => [...document.querySelectorAll('#bList .brief-item')].map(e => e.querySelector('.bname').textContent));
    const tags = await t.page.evaluate(() => [...document.querySelectorAll('#bList .brief-item .btag')].map(e => e.textContent));
    note(bl.length === 11 && bl[0] === 'The Strait' && bl.indexOf('The Islands') > 0 && bl.indexOf('Bab al-Yemen') > 0 && tags.length === 11 && tags[0] === 'Bab al-Mandab' && tags.indexOf('Hodeidah') > 0 && b.panel && b.panel.id === 'pBrief' && b.panel.y + b.panel.h <= b.ih + 0.5, `Briefings lists all eleven missions (${bl.join(', ')})`);
    await shot(t, 'land_briefs.png');
    await t.page.evaluate(() => [...document.querySelectorAll('#bList .brief-item')].find(e => e.getAttribute('data-id') === 'marib').scrollIntoView());
    await t.page.tap('#bList .brief-item[data-id="marib"]');
    await t.page.waitForFunction(() => window.__m1.state() === 'map');
    note((await t.page.evaluate(() => [window.__m1.menu().sel, document.getElementById('mName').textContent]))[1] === 'The Old Dam', 'a briefing tapped on the list shows that mission on the map');
    await t.page.waitForFunction(() => { const m = window.__m1.menu(); return Math.abs(m.cam - m.target) < 1 && Math.abs(m.camY - m.targetY) < 1; });
    // the Strait is now far off the bottom left of the picture: drag the map across and up to it
    const cam0 = await t.page.evaluate(() => [window.__m1.menu().cam, window.__m1.menu().camY]);
    await t.touch.down(8, 200, 330); for (let k = 1; k <= 8; k++) await t.touch.move(8, 200 + k * 40, 330 - k * 34); await t.touch.up(8);
    await sleep(200);
    await t.touch.down(8, 300, 330); for (let k = 1; k <= 8; k++) await t.touch.move(8, 300, 330 - k * 34); await t.touch.up(8);
    await sleep(300);
    const cam1 = await t.page.evaluate(() => [window.__m1.menu().cam, window.__m1.menu().camY]);
    note(cam1[0] < cam0[0] - 60 && cam1[1] > cam0[1] + 150, `a drag slides the map both ways (${JSON.stringify(cam0.map(Math.round))} to ${JSON.stringify(cam1.map(Math.round))})`);
    await tapAt(t, await nodeOnScreen(t, 'm1'));
    await sleep(600);
    note((await t.page.evaluate(() => window.__m1.menu().sel)) === 'm1', 'a tap on mission 1 chooses it again');
    await tapAt(t, await nodeOnScreen(t, 'm1'));
    await t.page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
    note(true, 'a second tap on mission 1 starts it');
    await sleep(900);
    s = await st(t); b = await boxes(t);
    note(s.snd.state === 'running' && s.snd.ready, `after Start: sound ${s.snd.state} at ${s.snd.rate} Hz, files ${s.snd.decoded}`);
    note(!b.fireHidden && b.fire.w >= 60 && b.jump.w >= 50 && b.bomb.w >= 44, `buttons showing: fire ${b.fire.w.toFixed(0)} px, jump ${b.jump.w.toFixed(0)} px, bomb ${b.bomb.w.toFixed(0)} px across`);
    const inside = k => b[k].x >= 0 && b[k].y >= 0 && b[k].x + b[k].w <= b.iw && b[k].y + b[k].h <= b.ih;
    note(inside('fire') && inside('jump') && inside('bomb') && inside('stick'), 'all four controls are fully on screen');
    await shot(t, 'land_start.png');
    // thumbs: run right, then jump, then fire and lock
    const x0 = s.x;
    await t.touch.down(1, 150, 300);
    await t.touch.move(1, 200, 302);
    await sleep(700);
    let s2 = await st(t);
    note(s2.x > x0 + 50, `left thumb pushed right: Yazeed ran ${(s2.x - x0).toFixed(0)} px in 0.7 s`);
    await t.touch.down(2, b.jump.cx, b.jump.cy);
    await sleep(120);
    const air = await t.page.evaluate(() => window.__m1.sim().p.air);
    await t.touch.up(2);
    note(air, 'right thumb on JUMP: he is in the air');
    await sleep(700);
    const shots0 = await t.page.evaluate(() => window.__m1.sim().stats.shots);
    await t.touch.down(3, b.fire.cx, b.fire.cy);
    await sleep(500);
    const shots1 = await t.page.evaluate(() => window.__m1.sim().stats.shots);
    note(shots1 - shots0 >= 3, `right thumb held on FIRE for half a second: ${shots1 - shots0} shots`);
    await shot(t, 'land_thumbs.png');
    await t.touch.move(3, b.fire.cx, b.fire.cy - 30);
    await t.touch.move(3, b.fire.cx, b.fire.cy - 60);
    await sleep(60);
    await t.touch.up(3);
    await sleep(400);
    s2 = await st(t);
    const shots2 = await t.page.evaluate(() => window.__m1.sim().stats.shots);
    note(s2.lock && shots2 > shots1 + 1, `slid up off FIRE and let go: locked=${s2.lock}, still firing (${shots2 - shots1} more shots)`);
    await t.touch.down(3, b.fire.cx, b.fire.cy); await sleep(50); await t.touch.up(3);
    await sleep(100);
    note(!(await st(t)).lock, 'a tap on FIRE lets the lock go');
    await t.touch.down(4, b.bomb.cx, b.bomb.cy); await sleep(60); await t.touch.up(4);
    await sleep(100);
    note(await t.page.evaluate(() => window.__m1.sim().stats.grenades === 1), 'a tap on BOMB throws one grenade');
    await t.touch.move(1, 150, 345);
    await sleep(200);
    note(await t.page.evaluate(() => window.__m1.sim().p.crouch), 'left thumb pulled down: he crouches');
    await t.touch.up(1);
    // pause from the corner of the picture
    const pz = await t.page.evaluate(() => { const g = window.__m1.geo().G.pause; return [(g.x0 + g.x1) / 2, (g.y0 + g.y1) / 2]; });
    await t.touch.down(5, pz[0], pz[1]); await sleep(40); await t.touch.up(5);
    await sleep(250);
    s2 = await st(t); b = await boxes(t);
    note(s2.state === 'pause' && s2.snd.state === 'suspended', `tapping the pause mark: state ${s2.state}, sound ${s2.snd.state}`);
    note(b.panel && b.panel.sh <= b.panel.ch + 1 && b.panel.y + b.panel.h <= b.ih, `pause panel fits: ${JSON.stringify(b.panel)}`);
    await shot(t, 'land_pause.png');
    // developer mode: off by default, so no phone report, no hit boxes, no FPS; switched on, all three come back
    const devOff = await t.page.evaluate(() => ({ dev: window.__m1.dev(), rep: getComputedStyle(document.querySelector('#pPause .rep')).display, boxes: getComputedStyle(document.getElementById('bBoxes')).display }));
    note(devOff.dev === false && devOff.rep === 'none' && devOff.boxes === 'none', `developer mode off by default: report and hit boxes hidden (${JSON.stringify(devOff)})`);
    await t.page.evaluate(() => window.__m1.setDev(true));
    await sleep(150);
    b = await boxes(t);
    const devOn = await t.page.evaluate(() => ({ dev: window.__m1.dev(), rep: getComputedStyle(document.querySelector('#pPause .rep')).display, boxes: getComputedStyle(document.getElementById('bBoxes')).display, kept: JSON.parse(localStorage.getItem('strait-m1')).dev }));
    note(devOn.dev && devOn.rep !== 'none' && devOn.boxes !== 'none' && devOn.kept === true, `developer mode on: report and hit boxes shown, the setting kept (${JSON.stringify(devOn)})`);
    note(b.panel && b.panel.sh <= b.panel.ch + 1 && b.panel.y + b.panel.h <= b.ih, `pause panel with the developer extras fits: ${JSON.stringify(b.panel)}`);
    await t.page.tap('#pPause .rep summary');
    await sleep(100);
    console.log('     report:\n' + (await t.page.evaluate(() => document.getElementById('report').textContent)).split('\n').map(l => '       ' + l).join('\n'));
    await shot(t, 'land_pause_report.png');
    await t.page.tap('#pPause .rep summary');
    await t.page.tap('#bRestart');
    await t.page.waitForFunction(() => window.__m1.state() === 'play');
    // the bot plays the whole slice in the real page
    await withBot(t, false);
    const seen = {};
    const t0 = Date.now();
    let last = null, lowLives = false;
    while (Date.now() - t0 < 480000) {
      const q = await t.page.evaluate(() => {
        const s = window.__m1.sim(), l = window.__m1.line();
        return { state: window.__m1.state(), status: s.status, zone: s.zone, x: s.p.x, time: s.time, lives: s.p.lives, dead: s.p.dead, clearT: s.clearT, line: l ? l.who + ': ' + l.text : '',
                 foes: s.enemies.filter(e => e.alive && e.hostile && Sim.onScreen(s, e.x, 0)).length, bombs: s.bombs.length, surr: s.enemies.some(e => e.st === 'surr' && !e.captured),
                 det: (s.props.find(o => o.k === 'detainee') || {}).st, weapon: s.p.weapon, mode: s.mode, flip: (s.trucks || []).some(k => k.st === 'flip'),
                 boss: s.boss ? s.boss.st : null, cmdr: s.cmdr ? s.cmdr.st : null, drones: (s.drones || []).length };
      });
      last = q;
      const snap = async (key, cond) => { if (!seen[key] && cond) { seen[key] = q.time.toFixed(1); await shot(t, 'run_' + key + '.png'); } };
      await snap('fight', q.foes >= 3 && q.zone === 0);
      await snap('hmg', q.weapon === 'hmg' && q.foes >= 2);
      await snap('line', !!q.line && q.time > 6);
      await snap('wreck', q.zone === 1 && q.foes >= 2);
      await snap('freed', q.det === 'freed');
      await snap('surrender', q.surr);
      await snap('boxes', q.zone === 2 && q.foes >= 3);
      await snap('road', q.mode === 'drive' && q.foes >= 2);
      await snap('flip', q.flip);
      await snap('drones', q.mode === 'drive' && q.drones >= 2);
      await snap('boss', q.boss === 'idle' || q.boss === 'bomb');
      await snap('boss_down', q.boss === 'dead');
      await snap('commander', q.cmdr === 'surr');
      await snap('clear', q.status === 'clear' && q.clearT > 90);
      if (q.state === 'over') { await shot(t, 'run_over.png'); await t.page.tap('#bContinue'); lowLives = true; }
      if (q.state === 'results') break;
      await sleep(120);
    }
    s = await st(t); b = await boxes(t);
    note(s.state === 'results', `the bot finished the slice in the page: state ${s.state}, game clock ${s.time.toFixed(1)} s, score ${s.score}, plates ${s.plates}, lives ${s.lives}${lowLives ? ' (needed a continue)' : ''}`);
    console.log('     moments photographed at (game seconds): ' + JSON.stringify(seen));
    note(b.panel && b.panel.id === 'pDone' && b.panel.y >= 0 && b.panel.y + b.panel.h <= b.ih, `results panel on screen: ${JSON.stringify(b.panel)}`);
    await shot(t, 'land_results.png');
    const P = await t.page.evaluate(() => { const m = window.__m1.meter(); return { hz: m.M.hz, snap: m.M.snap, frames: m.P.frames, avg: m.P.frames * 1000 / m.P.ms, long: m.P.long, worst: m.P.worst, min: m.P.minFps, slips: m.P.slips }; });
    console.log(`     frames here (software rendering, so only a floor): ${P.avg.toFixed(1)} a second average over ${P.frames}, worst second ${P.min.toFixed(0)}, slowest ${P.worst.toFixed(0)} ms, ${P.long} long, ${P.slips} steps dropped`);
    const pr = await t.page.evaluate(() => window.__m1.prog().m1);
    note(pr.cleared && pr.best && pr.reached === 4 && pr.runs >= 2 && !pr.stamped, `the clear is kept: ${JSON.stringify(pr)}`);
    await t.page.tap('#bToMap');
    await t.page.waitForFunction(() => window.__m1.state() === 'map');
    await t.page.waitForFunction(() => window.__m1.menu().rv > 40);
    await shot(t, 'land_map_stamp.png');
    await t.page.waitForFunction(() => window.__m1.menu().rv < 0, null, { timeout: 8000 });
    await sleep(400);
    const after = await t.page.evaluate(() => { const st = Menu.statuses(window.__m1.prog()); return [window.__m1.prog().m1.stamped, window.__m1.menu().sel, document.getElementById('mName').textContent, document.getElementById('mEye').textContent, Sound.counts().stamp || 0, st.mocha, st.zabid, st.taiz]; });
    note(after[0] && after[1] === 'mocha' && after[2] === 'The Coffee Port' && /Ready/.test(after[3]) && after[4] === 1 && after[5] === 'open' && after[6] === 'locked' && after[7] === 'locked',
         `back on the map: CLEAR stamped, the Coffee Port open and ready to play, both roads beyond it still locked (${JSON.stringify(after)})`);
    note((await t.page.evaluate(() => document.getElementById('bPlay').textContent)) === 'Start mission', 'the Coffee Port offers Start mission');
    await shot(t, 'land_map_after.png');
    await tapAt(t, await nodeOnScreen(t, 'm1'));
    await sleep(400);
    note((await t.page.evaluate(() => document.getElementById('bPlay').textContent)) === 'Play again', 'The Strait now offers Play again');
    await t.page.tap('#bPlay');
    await t.page.waitForFunction(() => window.__m1.state() === 'play');
    note(await t.page.evaluate(() => window.__m1.sim().time < 1 && window.__m1.sim().p.lives === 3), 'Play again starts a fresh run');
    note(t.real().length === 0, 'no errors on the page' + (t.real().length ? ':\n' + t.real().join('\n') : ''));
    await t.ctx.close();
  }

  // ------------------------------------------------------------------ a phone held upright: the game comes turned on its side
  if (want('port')) {
    const t = await open(browser, 'port', [390, 760, 3], { touch: true });
    let b = await boxes(t), s = await st(t);
    const inView = r => r && r.x >= -0.5 && r.y >= -0.5 && r.x + r.w <= b.iw + 0.5 && r.y + r.h <= b.ih + 0.5;
    note(b.sw <= b.iw && b.sh <= b.ih, `phone upright: nothing scrolls (page ${b.sw} x ${b.sh} in ${b.iw} x ${b.ih})`);
    note(s.rot && s.land && s.W >= 384 && b.hi.h > b.hi.w && inView(b.hi), `held upright, the game comes turned a quarter, on its side: picture ${s.W} wide, drawn ${b.hi.h.toFixed(0)} x ${b.hi.w.toFixed(0)} down the screen, enlarged x${s.n}`);
    const gone = await t.page.evaluate(() => ['bSide', 'bSide2', 'bSide3', 'turnTip', 'cap'].filter(id => document.getElementById(id)));
    note(!gone.length, 'no upright layout is left: no Turn sideways buttons, no words under the picture' + (gone.length ? ' (still there: ' + gone.join(', ') + ')' : ''));
    note(b.panel && b.panel.id === 'pHome' && inView(b.panel), `the home buttons are on screen: ${JSON.stringify(b.panel)}`);
    await shot(t, 'port_home.png');
    await t.page.evaluate(() => window.__m1.wake()); await t.page.tap('#bStart');
    await t.page.waitForFunction(() => window.__m1.state() === 'map');
    await sleep(600);
    b = await boxes(t);
    const pb = await t.page.evaluate(() => { const r = document.getElementById('bPlay').getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
    note(b.panel && b.panel.id === 'pMap' && inView(b.panel) && inView(pb) && b.panel.sh <= b.panel.ch + 1, `the mission card is turned with the map, on screen, and fits: ${JSON.stringify(b.panel)}`);
    await shot(t, 'port_map.png');
    await t.page.tap('#bPlay');
    await t.page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
    await sleep(1500);
    b = await boxes(t);
    note(inView(b.fire) && inView(b.jump) && inView(b.bomb) && inView(b.stick), `the thumbs are on screen: fire ${b.fire.w.toFixed(0)} px at (${b.fire.cx.toFixed(0)},${b.fire.cy.toFixed(0)}), jump (${b.jump.cx.toFixed(0)},${b.jump.cy.toFixed(0)}), bomb (${b.bomb.cx.toFixed(0)},${b.bomb.cy.toFixed(0)}), stick (${b.stick.cx.toFixed(0)},${b.stick.cy.toFixed(0)})`);
    await shot(t, 'port_start.png');
    // in the turned game the stick is at the top-left of the upright screen... work it out from the geometry
    const G = await t.page.evaluate(() => { const g = window.__m1.geo(), a = document.getElementById('app').getBoundingClientRect(); const un = (x, y) => [a.left + a.width - y, a.top + x]; return { stick: un(g.G.stick.x, g.G.stick.y), right: un(g.G.stick.x + 50, g.G.stick.y), fire: un(g.G.fire.x, g.G.fire.y) }; });
    const xa = (await st(t)).x;
    await t.touch.down(1, G.stick[0], G.stick[1]); await t.touch.move(1, G.right[0], G.right[1]);
    await sleep(600);
    const xb = (await st(t)).x;
    await t.touch.up(1);
    const sh0 = await t.page.evaluate(() => window.__m1.sim().stats.shots);
    await t.touch.down(2, G.fire[0], G.fire[1]); await sleep(400); await t.touch.up(2);
    const sh1 = await t.page.evaluate(() => window.__m1.sim().stats.shots);
    note(xb > xa + 25 && sh1 > sh0, `turned, the thumbs land where the buttons are drawn: ran ${(xb - xa).toFixed(0)} px on, fired ${sh1 - sh0}`);
    await withBot(t, true);
    await sleep(8000);
    await shot(t, 'port_play.png');
    await t.page.evaluate(() => { Input.sample = window.__realSample; });
    await t.page.evaluate(() => window.__m1.pause());
    await sleep(200);
    b = await boxes(t);
    note(b.panel && b.panel.id === 'pPause' && inView(b.panel), `the pause panel is on screen: ${JSON.stringify(b.panel)}`);
    await shot(t, 'port_pause.png');
    note(t.real().length === 0, 'no errors on the page' + (t.real().length ? ':\n' + t.real().join('\n') : ''));
    await t.ctx.close();
  }

  // ------------------------------------------------------------------ a short wide frame, as inside an app with its own bars
  if (want('short')) {
    const t = await open(browser, 'short', [640, 280, 2.625], { touch: true });
    let b = await boxes(t), s = await st(t);
    note(b.sw <= b.iw && b.sh <= b.ih, `short frame: nothing scrolls (${b.sw} x ${b.sh} in ${b.iw} x ${b.ih})`);
    note(b.panel && b.panel.y >= 0 && b.panel.y + b.panel.h <= b.ih + 0.5, `home buttons in 280 px of height: ${JSON.stringify(b.panel)}; picture ${s.W} wide x${s.n}`);
    await shot(t, 'short_home.png');
    await t.page.evaluate(() => window.__m1.wake()); await t.page.tap('#bStart');
    await t.page.waitForFunction(() => window.__m1.state() === 'map');
    await sleep(600);
    b = await boxes(t);
    const pv = await t.page.evaluate(() => { const r = document.getElementById('bPlay').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; });
    note(b.panel && b.panel.y >= 0 && b.panel.y + b.panel.h <= b.ih + 0.5 && pv, `mission card in 280 px of height, Start mission on screen: ${JSON.stringify(b.panel)}`);
    await shot(t, 'short_map.png');
    await t.page.tap('#bPlay');
    await t.page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
    await withBot(t, false);
    await sleep(7000);
    await shot(t, 'short_play.png');
    await t.page.evaluate(() => window.__m1.pause());
    await sleep(200);
    b = await boxes(t);
    note(b.panel && b.panel.y >= 0 && b.panel.y + b.panel.h <= b.ih + 0.5, `pause panel in 280 px of height: ${JSON.stringify(b.panel)}`);
    await shot(t, 'short_pause.png');
    note(t.real().length === 0, 'no errors on the page' + (t.real().length ? ':\n' + t.real().join('\n') : ''));
    await t.ctx.close();
  }

  // ------------------------------------------------------------------ running out of lives, and turning the phone mid-fight
  if (want('over')) {
    const t = await open(browser, 'over', [844, 390, 2], { touch: true });
    await startByTap(t);
    await sleep(600);
    await t.page.evaluate(() => { const s = window.__m1.sim(); s.p.lives = 1; s.p.plates = 1; s.p.inv = 0; s.bullets.push({ x: s.p.x - 40, y: s.p.y - 20, vx: 172, vy: 0, life: 90, own: false, src: 'test' }); });
    await t.page.waitForFunction(() => window.__m1.state() === 'over', null, { timeout: 8000 });
    await sleep(300);
    let b = await boxes(t);
    note(b.panel && b.panel.id === 'pOver' && b.panel.y >= 0 && b.panel.y + b.panel.h <= b.ih, `last life gone: the out-of-lives panel shows and fits: ${JSON.stringify(b.panel)}`);
    await shot(t, 'over_panel.png');
    await t.page.tap('#bContinue');
    await t.page.waitForFunction(() => window.__m1.state() === 'play');
    let s = await st(t);
    const cont = await t.page.evaluate(() => window.__m1.sim().stats.continues);
    note(s.lives === 3 && s.plates === 3 && cont === 1 && s.snd.state === 'running', `Continue: three lives again, ${cont} continue counted, sound ${s.snd.state}`);
    await sleep(500);
    await shot(t, 'over_continue.png');
    // turn the phone upright in the middle of play
    await t.page.setViewportSize({ width: 390, height: 844 });
    await sleep(500);
    s = await st(t); b = await boxes(t);
    note(s.state === 'pause' && s.rot && s.land && s.W >= 384 && b.sw <= b.iw && b.sh <= b.ih, `turned upright mid-play: it pauses and turns the game a quarter, still on its side (state ${s.state}, picture ${s.W} wide, turned=${s.rot})`);
    await shot(t, 'turn_upright.png');
    await t.page.tap('#bResume');
    await t.page.waitForFunction(() => window.__m1.state() === 'play');
    await sleep(400);
    await t.page.setViewportSize({ width: 844, height: 390 });
    await sleep(500);
    s = await st(t);
    note(s.state === 'pause' && s.land && !s.rot && s.W > 384, `turned back on its side: paused again, the game square to the screen, picture ${s.W} wide`);
    // a browser bar sliding away changes the height a little: that must not stop the game
    await t.page.tap('#bResume');
    await t.page.waitForFunction(() => window.__m1.state() === 'play');
    await t.page.setViewportSize({ width: 844, height: 340 });
    await sleep(400);
    s = await st(t);
    note(s.state === 'play' && s.W === 468, `the window getting 50 px shorter does not pause it (state ${s.state}, picture now ${s.W} wide)`);
    await shot(t, 'shorter.png');
    note(t.real().length === 0, 'no errors on the page' + (t.real().length ? ':\n' + t.real().join('\n') : ''));
    await t.ctx.close();
  }

  // ------------------------------------------------------------------ a desk, a keyboard
  if (want('desk')) {
    const t = await open(browser, 'desk', [1280, 800, 1], { touch: false });
    let b = await boxes(t), s = await st(t);
    note(b.fireHidden && s.W >= 384, `desktop: no thumb buttons; picture ${s.W} wide, drawn ${b.hi.w.toFixed(0)} x ${b.hi.h.toFixed(0)}, enlarged x${s.n}`);
    note(await t.page.evaluate(() => !window.__m1.woke() && document.querySelector('#pHome .acts').hidden), 'desktop, fresh: the home screen asks for a key, Start not shown yet');
    await t.page.keyboard.press(' ');
    await sleep(300);
    note(await t.page.evaluate(() => window.__m1.woke() && !document.querySelector('#pHome .acts').hidden && Sound.playing() === 'title' && document.activeElement && document.activeElement.id === 'bStart'), 'a key wakes it: the theme plays, Start is shown and has the keyboard focus');
    await shot(t, 'desk_home.png');
    await t.page.keyboard.press('Enter');
    await t.page.waitForFunction(() => window.__m1.state() === 'map', null, { timeout: 12000 });
    await sleep(500);
    note(await t.page.evaluate(() => document.activeElement && document.activeElement.id === 'bPlay'), 'on the map, Start mission has the keyboard focus');
    await t.page.keyboard.press('ArrowRight'); await sleep(250);
    const k1 = await t.page.evaluate(() => [window.__m1.menu().sel, document.getElementById('mName').textContent]);
    await t.page.keyboard.press('ArrowRight'); await sleep(250);
    const k2 = await t.page.evaluate(() => window.__m1.menu().sel);
    await t.page.keyboard.press('ArrowDown'); await sleep(250);
    const k3 = await t.page.evaluate(() => window.__m1.menu().sel);
    await t.page.keyboard.press('ArrowLeft'); await sleep(250);
    await t.page.keyboard.press('ArrowLeft'); await sleep(250);
    note(k1[0] === 'mocha' && k2 === 'zabid' && k3 === 'taiz' && (await t.page.evaluate(() => window.__m1.menu().sel)) === 'm1', `arrows move along the roads and across the fork (${JSON.stringify([k1[1], k2, k3])})`);
    await shot(t, 'desk_map.png');
    await t.page.keyboard.press('Escape');
    await t.page.waitForFunction(() => window.__m1.state() === 'home', null, { timeout: 5000 });
    note(true, 'Escape on the map goes back home');
    await t.page.keyboard.press('Enter');
    await t.page.waitForFunction(() => window.__m1.state() === 'map', null, { timeout: 5000 });
    await sleep(400);
    await t.page.keyboard.press('Enter');
    await t.page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
    await sleep(500);
    const x0 = (await st(t)).x;
    await t.page.keyboard.down('ArrowRight'); await sleep(500);
    await t.page.keyboard.down('z'); await sleep(400);
    await t.page.keyboard.press('x'); await sleep(200);
    await t.page.keyboard.press('c'); await sleep(200);
    s = await st(t);
    const k = await t.page.evaluate(() => { const s = window.__m1.sim(); return { shots: s.stats.shots, gren: s.stats.grenades }; });
    note(s.x > x0 + 60 && k.shots >= 2 && k.gren === 1, `keys: ran ${(s.x - x0).toFixed(0)} px, ${k.shots} shots, ${k.gren} grenade`);
    await shot(t, 'desk_play.png');
    await t.page.keyboard.up('ArrowRight'); await t.page.keyboard.up('z');
    await t.page.keyboard.press('p'); await sleep(150);
    note((await st(t)).state === 'pause', 'P pauses');
    await shot(t, 'desk_pause.png');
    await t.page.keyboard.press('Escape'); await sleep(150);
    note((await st(t)).state === 'play', 'Escape resumes');
    await t.page.evaluate(() => window.dispatchEvent(new Event('blur')));
    await sleep(100);
    note((await st(t)).state === 'pause', 'leaving the window pauses');
    note(t.real().length === 0, 'no errors on the page' + (t.real().length ? ':\n' + t.real().join('\n') : ''));
    await t.ctx.close();
  }

  await browser.close();
  console.log(problems.length ? '\n' + problems.length + ' PROBLEM(S)' : '\nALL GOOD');
})().catch(e => { console.error('TEST CRASHED', e); process.exit(1); });
