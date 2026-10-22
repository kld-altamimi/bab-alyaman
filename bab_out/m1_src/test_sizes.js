// test_sizes.js - the layout at the sizes of real phones and tablets, both ways up: is everything on screen, clear of everything else, and big enough to press?
const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sizes = [[568, 320, 2, 'iPhone SE on its side'], [667, 375, 2, 'iPhone 8 on its side'], [812, 375, 3, 'iPhone X on its side'], [844, 390, 3, 'iPhone 14 on its side'], [932, 430, 3, 'iPhone Pro Max on its side'],
  [800, 360, 3, 'Galaxy S on its side'], [915, 412, 2.625, 'Pixel on its side'], [740, 300, 3, 'a phone on its side inside an app with bars'], [1024, 768, 2, 'iPad on its side'], [1180, 820, 2, 'iPad Air on its side'],
  [320, 568, 2, 'iPhone SE upright'], [360, 640, 3, 'small Android upright'], [390, 700, 3, 'iPhone 14 upright in a browser'], [430, 932, 3, 'iPhone Pro Max upright'], [412, 800, 2.625, 'Pixel upright'], [768, 1024, 2, 'iPad upright'],
  [390, 480, 3, 'a short upright frame'], [300, 220, 2, 'a very small frame']];
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  let bad = 0;
  for (const [w, h, dpr, label] of sizes) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, hasTouch: true, isMobile: true });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    const fits = (pid, bid) => page.evaluate(([pid, bid]) => { const pe = document.getElementById(pid), p = pe.getBoundingClientRect(), s = document.getElementById(bid).getBoundingClientRect(), c = document.getElementById('hi').getBoundingClientRect();
      return { top: p.top, bottom: p.bottom, left: p.left, right: p.right, sh: pe.scrollHeight, ch: pe.clientHeight, startVisible: s.top >= 0 && s.bottom <= innerHeight && s.left >= 0 && s.right <= innerWidth, sw: document.documentElement.scrollWidth, shh: document.documentElement.scrollHeight,
               canvas: { left: c.left, right: c.right, top: c.top, bottom: c.bottom } }; }, [pid, bid]);
    const title = await fits('pHome', 'bStart');
    await page.evaluate(() => window.__m1.wake()); await page.tap('#bStart');
    await page.waitForFunction(() => window.__m1.state() === 'map', null, { timeout: 12000 });
    await sleep(500);
    const card = await fits('pMap', 'bPlay');
    const mapv = await page.evaluate(() => window.__m1.menu());
    await page.tap('#bPlay');
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 12000 });
    await sleep(150);
    const g = await page.evaluate(() => {
      const r = id => { const b = document.getElementById(id).getBoundingClientRect(); return { x: b.left, y: b.top, w: b.width, h: b.height, cx: b.left + b.width / 2, cy: b.top + b.height / 2, r: b.width / 2 }; };
      const geo = window.__m1.geo();
      return { hi: r('hi'), fire: r('bFire'), jump: r('bJump'), bomb: r('bBomb'), stick: r('stick'), W: window.__m1.width(), land: geo.land, rot: geo.rot, n: geo.n, scale: geo.scale, fast: geo.fast, iw: innerWidth, ih: innerHeight, pause: geo.G.pause, top: geo.G.top, split: geo.G.split };
    });
    const probs = [];
    const inside = (b, name) => { if (b.x < -0.5 || b.y < -0.5 || b.x + b.w > g.iw + 0.5 || b.y + b.h > g.ih + 0.5) probs.push(name + ' off screen'); };
    ['fire', 'jump', 'bomb', 'stick', 'hi'].forEach(k => inside(g[k], k));
    const gap = (a, b) => Math.hypot(a.cx - b.cx, a.cy - b.cy) - a.r - b.r;
    const gaps = { fj: gap(g.fire, g.jump), fb: gap(g.fire, g.bomb), jb: gap(g.jump, g.bomb), js: gap(g.jump, g.stick) };
    for (const k in gaps) if (gaps[k] < 2) probs.push('buttons touch: ' + k + ' ' + gaps[k].toFixed(1));
    if (g.fire.w < 52) probs.push('fire only ' + g.fire.w.toFixed(0) + ' px');
    if (g.jump.w < 44) probs.push('jump only ' + g.jump.w.toFixed(0) + ' px');
    if (g.bomb.w < 44) probs.push('bomb only ' + g.bomb.w.toFixed(0) + ' px');
    // (held upright the game is turned a quarter: its left and right run down the screen)
    if (g.rot ? (g.hi.y < 15.5 || g.hi.y + g.hi.h > g.ih - 15.5) : (g.hi.x < 15.5 || g.hi.x + g.hi.w > g.iw - 15.5)) probs.push('picture in the gutter');
    if (!g.land) probs.push('laid out upright');
    if ((g.rot ? g.jump.y : g.jump.x) < g.split) probs.push('jump crosses into the stick half');
    if (title.sw > g.iw || title.shh > g.ih) probs.push('page scrolls');
    if (!title.startVisible) probs.push('Start not visible without scrolling');
    if (!card.startVisible) probs.push('Start mission not visible without scrolling');
    if (card.sw > g.iw || card.shh > g.ih) probs.push('the map page scrolls');
    if (g.rot ? (card.top < card.canvas.top - 0.5 || card.bottom > card.canvas.bottom + 0.5) : (card.left < card.canvas.left - 0.5 || card.right > card.canvas.right + 0.5)) probs.push('the mission card hangs off the picture');
    if (mapv.vis < 150) probs.push('the card leaves only ' + Math.round(mapv.vis) + ' of the map in view');
    if (errs.length) probs.push('errors: ' + errs.join('; '));
    const tight = (w < 320 || h < 240);
    if (probs.length && !tight) bad++;
    console.log((probs.length ? (tight ? 'note ' : 'FAIL ') : 'ok   ') + (label + ' ' + w + 'x' + h).padEnd(46) + ' picture ' + g.W + ' wide at ' + g.scale.toFixed(2) + ' (x' + g.n + '), ' + Math.round(g.hi.w) + 'x' + Math.round(g.hi.h) +
      (g.rot ? ' turned' : '') + '; fire ' + Math.round(g.fire.w) + ' jump ' + Math.round(g.jump.w) + ' bomb ' + Math.round(g.bomb.w) + ' stick ' + Math.round(g.stick.w) + '; home ' + (title.sh > title.ch + 1 ? 'scrolls inside its panel' : 'fits') + ', card ' + (card.sh > card.ch + 1 ? 'scrolls inside itself' : 'fits') + ', map in view ' + Math.round(mapv.vis) + (probs.length ? '  <-- ' + probs.join(', ') : ''));
    await ctx.close();
  }
  await browser.close();
  console.log(bad ? bad + ' SIZE(S) WITH PROBLEMS' : 'ALL SIZES GOOD');
})();
