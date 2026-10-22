// test_taiz_music.js - Taiz's own music (0.9.57): the title fetches none of it; Taiz, started, fetches its night theme and
// its bosses' (and not the Strait's); the night theme plays after the jingle; the Castle Gun comes on to the bosses' theme;
// it stops when the gun goes up; the launcher, rolling out of the keep, brings it back; dawn brings the night theme back; nothing goes wrong on the
// page. (The fights are set up by hand: the gates before each one marked done, the camera put at it.)
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [], got = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  page.on('response', r => { const u = r.url(); if (/\/audio\/[^/]+\.mp3$/.test(u)) got.push(u.split('/').pop().replace('.mp3', '')); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.waitForFunction(() => Sound.isReady(), null, { timeout: 20000 });
  await page.waitForTimeout(800);
  note(got.indexOf('music_taiz') < 0 && got.indexOf('music_taizboss') < 0, 'the title fetches none of Taiz\'s music (' + got.join(', ') + ')');
  const man = await page.evaluate(() => [AUDIO.music.taiz, AUDIO.music.taizboss, LEVEL_TAIZ.music, LEVEL_TAIZ.bossMusic]);
  note(man[0] && man[0].file === 'music_taiz' && man[1] && man[1].file === 'music_taizboss' && man[2] === 'taiz' && man[3] === 'taizboss',
    'the page knows Taiz\'s two loops and the mission names them (' + JSON.stringify(man) + ')');
  await page.evaluate(() => window.__m1.begin('taiz', 3));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli && window.__m1.sim().heli.st === 'fly', null, { timeout: 20000 });
  await page.waitForFunction(() => Sound.playing() === 'taiz', null, { timeout: 10000 }).catch(() => {});
  note((await page.evaluate(() => Sound.playing())) === 'taiz', 'Taiz from the castle: its night theme plays');
  note(got.indexOf('music_taiz') >= 0 && got.indexOf('music_taizboss') >= 0 && got.indexOf('music_strait') < 0 && got.indexOf('music_battery') < 0,
    'it fetched its own two loops and not the Strait\'s (' + got.join(', ') + ')');
  await page.waitForFunction(() => Sound.hasTrack('taizboss'), null, { timeout: 8000 }).catch(() => {});
  note(await page.evaluate(() => Sound.hasTrack('taiz') && Sound.hasTrack('taizboss')), 'both are decoded and ready');
  // to the Castle Gun's fight: everything before it done, the camera at it
  const toFight = async (gid, boss) => page.evaluate(([gid, boss]) => {
    const s = window.__m1.sim(), L = s.L;
    let gi = -1;
    for (let i = 0; i < L.gates.length; i++) if (L.gates[i].id === gid) gi = i;
    for (let i = 0; i < gi; i++) { s.gates[i].done = true; for (const k of L.gates[i].groups) { s.groups[k].done = true; s.groups[k].pending.length = 0; s.groups[k].awake = true; } }
    const before = []; for (let i = 0; i < gi; i++) before.push(...L.gates[i].groups);
    for (const e of s.enemies) if (e.alive && e.hostile && e.k !== boss && before.indexOf(e.g) >= 0) { Sim._.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; }
    for (const k of L.gates[gi].groups) s.groups[k].awake = true;
    s.u = Math.max(s.u, L.gates[gi].u);
    const g = L.gates[gi];
    s.heli.x = g.at ? g.at[0] - 160 : s.heli.x; s.heli.y = g.at ? g.at[1] - 60 : s.heli.y;
    s.p.inv = 9999;
    return gi;
  }, [gid, boss]);
  const gk = await toFight('k', 'cgun');
  note(gk >= 0, 'the Castle Gun\'s fight is gate ' + gk);
  const boss1 = await page.waitForFunction(() => { const s = window.__m1.sim(); return s.boss && s.boss.kind === 'cgun' ? Sound.playing() : null; }, null, { timeout: 10000 }).then(h => h.jsonValue()).catch(() => null);
  note(boss1 === 'taizboss', 'the Castle Gun comes up to the bosses\' theme (' + boss1 + ')');
  await page.evaluate(() => { const s = window.__m1.sim(); for (const e of s.enemies) if (e.k === 'cgun') { Sim._.standDown(s, e); e.hp = 0; e.alive = false; } });
  const off = await page.waitForFunction(() => { const s = window.__m1.sim(); return s.enemies.some(e => e.k === 'cgun' && e.dieT >= 70) ? String(Sound.playing()) : null; }, null, { timeout: 10000 }).then(h => h.jsonValue()).catch(() => 'timeout');
  note(off === 'null', 'the music stops as the gun goes up (' + off + ')');
  await toFight('m', 'launcher');
  const boss2 = await page.waitForFunction(() => { const s = window.__m1.sim(); return s.boss && s.boss.kind === 'launcher' ? Sound.playing() : null; }, null, { timeout: 10000 }).then(h => h.jsonValue()).catch(() => null);
  const st2 = await page.evaluate(() => { const s = window.__m1.sim(); return { gate: s.gateNow && s.gateNow.id, u: Math.round(s.u), holdU: s.holdU && Math.round(s.holdU), boss: s.boss && s.boss.kind, gs: s.enemies.filter(e => e.k === 'launcher').map(e => [e.st, e.alive, e.g]), M: [s.groups.M.awake, s.groups.M.done], heli: [Math.round(s.heli.x), Math.round(s.heli.y), s.heli.st], dead: s.p.dead, status: s.status }; });
  note(boss2 === 'taizboss', 'their launcher comes out to it again (' + boss2 + '; ' + JSON.stringify(st2) + ')');
  // (the launcher done, and the men on the walls with it, so the fight is over)
  await page.evaluate(() => { const s = window.__m1.sim(); for (const e of s.enemies) if (e.k === 'launcher') { Sim._.standDown(s, e); e.hp = 0; e.alive = false; } });
  await page.waitForFunction(() => !window.__m1.sim().boss, null, { timeout: 10000 }).catch(() => {});
  await page.evaluate(() => { const s = window.__m1.sim(); for (const e of s.enemies) if (e.alive && e.hostile && e.g === 'M') { Sim._.standDown(s, e); e.alive = false; e.st = 'gone'; e.deadT = 999; } s.groups.M.pending.length = 0; });
  const dawn = await page.waitForFunction(() => { const s = window.__m1.sim(); return s.ending && Sound.playing() === 'taiz' ? [s.ending.st, +(s.dawn || 0).toFixed(2)] : null; }, null, { timeout: 15000 }).then(h => h.jsonValue()).catch(() => null);
  const st3 = await page.evaluate(() => { const s = window.__m1.sim(); return { gate: s.gateNow && s.gateNow.id, u: Math.round(s.u), len: Math.round(s.rt ? s.rt.len : -1), ending: s.ending, boss: s.boss && s.boss.kind, live: s.enemies.filter(e => e.alive && e.hostile).map(e => [e.k, e.g, e.st]), M: [s.groups.M.awake, s.groups.M.done, s.groups.M.pending.length, s.groups.M.hostile], heli: [Math.round(s.heli.x), Math.round(s.heli.y), s.heli.st], playing: Sound.playing(), status: s.status }; });
  note(!!dawn, 'dawn brings the night theme back, quietly (' + JSON.stringify(dawn) + (dawn ? '' : '; ' + JSON.stringify(st3)) + ')');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
