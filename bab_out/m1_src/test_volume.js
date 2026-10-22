// test_volume.js - the three meters (build 15): in the options and the pause menu, music, effects and voices each
// have a slider; dragging one sets that gain and no other, the two copies agree, arrows on a focused slider move
// it (and leave the menu alone), a level survives a reload, and the levels still fit the panels on a phone.
const { chromium } = require('playwright');
const fs = require('fs');
const shots = '/home/claude/bab_out/m1_src/shots/volume/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
fs.mkdirSync(shots, { recursive: true });
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
const gains = page => page.evaluate(() => { const t = Sound.tap(); return t.music ? { m: +t.music.gain.value.toFixed(3), s: +t.sfx.gain.value.toFixed(3), v: +t.voice.gain.value.toFixed(3) } : null; });
const meters = page => page.evaluate(() => Object.fromEntries(['vMusic', 'vSfx', 'vVoice', 'vMusic2', 'vSfx2', 'vVoice2'].map(id => { const m = document.getElementById(id); return [id, [m.value, m.parentNode.querySelector('output').textContent]]; })));
async function slide(page, id, pc) {
  // a finger on the track: pressed where the value asked for sits, then let go
  const r = await page.evaluate(id => { const b = document.getElementById(id).getBoundingClientRect(); return { x: b.left, y: b.top + b.height / 2, w: b.width }; }, id);
  const x = r.x + 11 + (r.w - 22) * pc / 100;
  await page.mouse.move(x, r.y); await page.mouse.down(); await page.mouse.move(x + 1, r.y); await page.mouse.move(x, r.y); await page.mouse.up();
  await sleep(150);
}
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource/.test(msg.text())) errors.push(msg.text()); });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.evaluate(() => window.__m1.wake());
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(300);
  const m0 = await meters(page);
  note(Object.values(m0).every(v => v[0] === '100' && v[1] === '100%'), 'a fresh save: every meter at 100% (' + JSON.stringify(m0) + ')');
  const fit = await page.evaluate(() => { const p = document.getElementById('pOpts'); const ms = [...p.querySelectorAll('.meter input')].map(i => i.getBoundingClientRect()); const pr = p.getBoundingClientRect(); return { sh: p.scrollHeight, ch: p.clientHeight, inside: ms.every(b => b.top >= pr.top && b.bottom <= pr.bottom && b.height >= 30), n: ms.length }; });
  note(fit.n === 3 && fit.inside && fit.sh <= fit.ch + 1, 'on a phone on its side the three meters sit inside the options, nothing to scroll (' + JSON.stringify(fit) + ')');
  await page.screenshot({ path: shots + 'opts_full.png' });
  // music down to 40
  await slide(page, 'vMusic', 40);
  let g = await gains(page), m = await meters(page);
  note(m.vMusic[0] === '40' && m.vMusic2[0] === '40' && m.vMusic[1] === '40%' && m.vSfx[0] === '100' && m.vVoice[0] === '100', 'music slid to 40: both copies say 40%, the others untouched (' + JSON.stringify(m) + ')');
  note(g && Math.abs(g.m - 0.62 * 0.4) < 0.03 && Math.abs(g.s - 0.62) < 0.01 && Math.abs(g.v - 1.2) < 0.01, 'and the music gain alone went down (' + JSON.stringify(g) + ')');
  // voices to 0 with the keyboard: arrows move the slider, not the menu
  await page.focus('#vVoice');
  for (let i = 0; i < 25; i++) await page.keyboard.press('ArrowLeft');
  await sleep(200);
  g = await gains(page); m = await meters(page);
  const state = await page.evaluate(() => window.__m1.state());
  note(m.vVoice[0] === '0' && m.vVoice2[0] === '0' && state === 'opts', 'arrows on the voices slider take it to 0 and leave the options open (' + m.vVoice[0] + ', ' + state + ')');
  note(g && g.v < 0.02 && Math.abs(g.m - 0.62 * 0.4) < 0.03, 'the voice gain is 0, the music still at 40% (' + JSON.stringify(g) + ')');
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
  await page.screenshot({ path: shots + 'opts_set.png' });
  // effects to 70, then a reload keeps all three
  await slide(page, 'vSfx', 70);
  await sleep(200);
  await page.reload();
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.evaluate(() => window.__m1.wake());
  await page.tap('#bOpts');
  await page.waitForFunction(() => window.__m1.state() === 'opts');
  await sleep(300);
  m = await meters(page);
  note(m.vMusic[0] === '40' && m.vSfx[0] === '70' && m.vVoice[0] === '0' && m.vMusic2[0] === '40', 'after a reload the meters are where they were left: music 40, effects 70, voices 0 (' + JSON.stringify(m) + ')');
  await page.tap('#bBack');
  await page.waitForFunction(() => window.__m1.state() === 'home');
  await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
  await page.waitForFunction(() => window.__m1.state() === 'map');
  await sleep(500);
  g = await gains(page);
  note(g && Math.abs(g.m - 0.62 * 0.4) < 0.03 && Math.abs(g.s - 0.62 * 0.7) < 0.03 && g.v < 0.02, 'and the sound runs at those levels once it starts (' + JSON.stringify(g) + ')');
  // in play: the pause menu's copies, and a change there shows in the options
  await page.tap('#bPlay');
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await sleep(500);
  await page.keyboard.press('p');
  await page.waitForFunction(() => window.__m1.state() === 'pause');
  await sleep(200);
  const fit2 = await page.evaluate(() => { const p = document.getElementById('pPause'); const ms = [...p.querySelectorAll('.meter input')].map(i => i.getBoundingClientRect()); const pr = p.getBoundingClientRect(); return { sh: p.scrollHeight, ch: p.clientHeight, inside: ms.every(b => b.top >= pr.top && b.bottom <= pr.bottom && b.height >= 30), n: ms.length }; });
  note(fit2.n === 3 && fit2.inside && fit2.sh <= fit2.ch + 1, 'the pause menu has the three meters in view too (' + JSON.stringify(fit2) + ')');
  await slide(page, 'vVoice2', 100);
  m = await meters(page); g = await gains(page);
  note(m.vVoice2[0] === '100' && m.vVoice[0] === '100' && g && Math.abs(g.v - 1.2) < 0.03, 'voices back up to 100 from the pause menu: the options copy follows, the gain is back (' + JSON.stringify([m.vVoice, g]) + ')');
  await page.screenshot({ path: shots + 'pause.png' });
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => window.__m1.state() === 'play');
  await sleep(300);
  note(await page.evaluate(() => window.__m1.state() === 'play'), 'and the game goes on');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
