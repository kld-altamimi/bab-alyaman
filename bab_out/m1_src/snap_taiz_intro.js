// snap_taiz_intro.js - Taiz's opening in a real page: the street, the Apache coming in, the men running, the landing,
// Yazeed walking to it (the right arrow held), climbing in, the lift-off and the picture drawing back. Pictures in shots/.
const { chromium } = require('playwright');
const URL = process.argv[2] || 'http://127.0.0.1:8766/index.html?internal=1';
const LANG = process.argv[3] || 'en';
const OUT = __dirname + '/shots/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', msg => { if (msg.type() === 'error' && !/font|ERR_|Failed to load resource|posthog/.test(msg.text())) errors.push(msg.text()); });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  if (LANG !== 'en') await page.evaluate(l => window.__m1.setLang(l), LANG);
  await page.mouse.click(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const st = () => page.evaluate(() => { const s = window.__m1.sim(); return { t: s.intro && s.intro.t, st: s.intro && s.intro.st, heli: s.heli.st, zoom: +s.zoom.toFixed(2), vw: s.viewW, vh: s.viewH, cam: Math.round(s.cam), camY: Math.round(s.camY), canvas: [Render.width(), Render.height(), Render.zoom()] }; });
  const out = [];
  const shot = async name => { await page.screenshot({ path: OUT + 'intro_' + LANG + '_' + name + '.png' }); out.push(name + ' ' + JSON.stringify(await st())); };
  const until = async (cond, ms) => { await page.waitForFunction(cond, null, { timeout: ms || 20000 }); };
  await sleep(600); await shot('a_street');
  await until(() => window.__m1.sim().intro.t > 140); await shot('b_arrive');
  await until(() => window.__m1.sim().intro.t > 200); await shot('c_scream');
  await until(() => window.__m1.sim().intro.t > 235); await shot('d_run');
  await until(() => window.__m1.sim().intro.st === 'wait'); await sleep(300); await shot('e_landed');
  await page.keyboard.down('ArrowRight');
  await sleep(1200); await shot('f_walk');
  await until(() => window.__m1.sim().intro && window.__m1.sim().intro.st === 'board'); await page.keyboard.up('ArrowRight'); await sleep(150); await shot('g_board');
  await until(() => window.__m1.sim().intro && window.__m1.sim().intro.st === 'lift'); await sleep(300); await shot('h_lift');
  await until(() => window.__m1.sim().intro && window.__m1.sim().intro.st === 'zoom' && window.__m1.sim().intro.zoomT > 50); await shot('i_zoom');
  await until(() => !window.__m1.sim().intro); await sleep(400); await shot('j_flying');
  console.log(out.join('\n'));
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
