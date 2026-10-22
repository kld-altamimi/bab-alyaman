// snap_menus.js - pictures of the home screen, the campaign map and the options, at a phone on its side, a phone upright and
// a desktop window; and the first-clear reveal, frame by frame. usage: node snap_menus.js [fresh|cleared|reveal|all]
const { chromium } = require('playwright');
const fs = require('fs');
const out = '/home/claude/bab_out/m1_src/shots/menus/';
fs.mkdirSync(out, { recursive: true });
const which = process.argv[2] || 'all';
const SIZES = [['land', 844, 390, 3, true], ['port', 390, 760, 3, true], ['desk', 1280, 720, 1, false]];
const CLEARED = { scheme: 'hold', prog: { m1: { reached: 4, cleared: true, best: { total: 25300, time: 203 }, ace: true, lib: false, runs: 3, stamped: true } } };
const REVEAL = { scheme: 'hold', prog: { m1: { reached: 4, cleared: true, best: { total: 25300, time: 203 }, ace: false, lib: true, runs: 1, stamped: false } } };
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const errors = [];
  async function open(name, w, h, dpr, touch, saved) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, hasTouch: touch, isMobile: touch });
    const page = await ctx.newPage();
    page.on('pageerror', e => errors.push(name + ': ' + e.message));
    page.on('console', m => { if (m.type() === 'error' && !/font|ERR_/.test(m.text())) errors.push(name + ': ' + m.text()); });
    if (saved) await page.addInitScript(s => { try { localStorage.setItem('strait-m1', s); } catch (e) {} }, JSON.stringify(saved));
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    return { ctx, page };
  }
  async function shoot(page, file) { await page.screenshot({ path: out + file + '.png' }); }
  for (const [nm, w, h, dpr, touch] of SIZES) {
    for (const save of (which === 'all' ? ['fresh', 'cleared'] : (which === 'reveal' ? [] : [which]))) {
      const { ctx, page } = await open(nm, w, h, dpr, touch, save === 'cleared' ? CLEARED : null);
      await page.waitForTimeout(1400);
      await shoot(page, `${nm}_${save}_home`);
      await page.click('#bStart');
      await page.waitForFunction(() => window.__m1.state() === 'map');
      await page.waitForTimeout(700);
      await shoot(page, `${nm}_${save}_map_m1`);
      // along the roads with the keys, the camera sliding after
      await page.keyboard.press('ArrowRight'); await page.keyboard.press('ArrowRight'); await page.keyboard.press('ArrowRight');
      await page.waitForTimeout(900);
      await shoot(page, `${nm}_${save}_keys_hodeidah`);
      // and every mission, the camera put straight on it
      for (const id of ['mocha', 'zabid', 'kawkaban', 'taiz', 'ibb', 'dhamar', 'sanaa', 'marib']) {
        await page.evaluate(i => window.__m1.toMap(i), id);
        await page.waitForTimeout(250);
        await shoot(page, `${nm}_${save}_map_${id}`);
      }
      await page.click('#bBriefs');
      await page.waitForFunction(() => window.__m1.state() === 'brief');
      await page.waitForTimeout(300);
      await shoot(page, `${nm}_${save}_brief`);
      await page.evaluate(() => { const l = document.getElementById('bList'); l.scrollTop = l.scrollHeight; });
      await page.waitForTimeout(200);
      await shoot(page, `${nm}_${save}_brief_end`);
      await page.click('#bBriefBack');
      await page.waitForFunction(() => window.__m1.state() === 'map');
      if (save === 'fresh') {
        await page.click('#bOpts2');
        await page.waitForTimeout(300);
        await shoot(page, `${nm}_${save}_opts`);
      }
      const info = await page.evaluate(() => Object.assign({ state: window.__m1.state() }, window.__m1.menu()));
      console.log(nm, save, JSON.stringify(info));
      await ctx.close();
    }
  }
  if (which === 'all' || which === 'reveal') {
    const { ctx, page } = await open('reveal', 844, 390, 2, true, REVEAL);
    await page.click('#bStart');
    await page.waitForFunction(() => window.__m1.state() === 'map');
    for (const at of [10, 28, 40, 70, 100, 125, 150, 205]) {
      await page.waitForFunction(n => window.__m1.menu().rv >= n || window.__m1.menu().rv < 0, at);
      await shoot(page, 'reveal_' + ('00' + at).slice(-3));
    }
    console.log('after the reveal', JSON.stringify(await page.evaluate(() => [window.__m1.menu(), window.__m1.prog().m1])));
    await ctx.close();
  }
  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no errors');
  await browser.close();
})();
