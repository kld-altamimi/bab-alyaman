// snap_mapfull.js - the whole campaign map in one picture, stitched from the game's own drawing with the card out of the
// way: once as a fresh save sees it, once with every mission cleared. usage: node snap_mapfull.js [out-dir]
const { chromium } = require('playwright');
const fs = require('fs');
const out = (process.argv[2] || '/home/claude/bab_out/m1_src/shots/menus/') ;
fs.mkdirSync(out, { recursive: true });
const ALL = {};
['m1', 'mocha', 'zabid', 'hodeidah', 'haraz', 'kawkaban', 'taiz', 'ibb', 'dhamar', 'sanaa', 'marib'].forEach(id => {
  ALL[id] = { reached: 0, cleared: true, best: { total: 20000, time: 200 }, ace: false, lib: false, runs: 1, stamped: true };
});
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  for (const [name, saved] of [['fresh', null], ['all', { scheme: 'hold', prog: ALL }]]) {
    const ctx = await browser.newContext({ viewport: { width: 936, height: 432 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    page.on('pageerror', e => console.log('ERR', e.message));
    if (saved) await page.addInitScript(s => { try { localStorage.setItem('strait-m1', s); } catch (e) {} }, JSON.stringify(saved));
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    await page.evaluate(() => window.__m1.toMap('m1'));
    await page.waitForTimeout(300);
    await page.addStyleTag({ content: '#ui{visibility:hidden !important}' });
    const geo = await page.evaluate(() => { const c = document.getElementById('hi').getBoundingClientRect(); return { x: c.left, y: c.top, w: c.width, h: c.height, W: document.getElementById('hi').width }; });
    const shots = [];
    for (const cy of [0, 108, 216, 264]) for (const cx of [0, 134, 268]) {
      await page.evaluate(([x, y]) => window.__m1.look(x, y), [cx, cy]);
      await page.waitForTimeout(120);
      const file = out + `full_${name}_${cx}_${cy}.png`;
      await page.screenshot({ path: file, clip: { x: geo.x, y: geo.y, width: geo.w, height: geo.h } });
      shots.push([file, cx, cy]);
    }
    fs.writeFileSync(out + `full_${name}.json`, JSON.stringify({ geo, shots }));
    await ctx.close();
  }
  await browser.close();
})();
